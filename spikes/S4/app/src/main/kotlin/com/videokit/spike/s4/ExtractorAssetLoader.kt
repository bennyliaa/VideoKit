package com.videokit.spike.s4

import android.media.MediaDataSource
import android.media.MediaExtractor
import android.media.MediaFormat
import android.os.IBinder
import android.os.Looper
import android.os.Parcel
import android.os.RemoteException
import android.util.Log
import androidx.media3.common.C
import androidx.media3.common.Format
import androidx.media3.common.util.MediaFormatUtil
import androidx.media3.common.util.UnstableApi
import androidx.media3.decoder.DecoderInputBuffer
import androidx.media3.transformer.AssetLoader
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.ExportException
import androidx.media3.transformer.ProgressHolder
import androidx.media3.transformer.SampleConsumer
import androidx.media3.transformer.Transformer
import com.google.common.collect.ImmutableMap
import java.io.IOException

/**
 * S4 attempt 3: an [AssetLoader] that demuxes with the platform `MediaExtractor` and hands the compressed samples to
 * Transformer (which decodes them with MediaCodec). It never creates an ExoPlayer, so the worker avoids
 * `ExoPlayerImpl` generating an audio session id (`Util.generateAudioSessionId` -> `media.audio_flinger`), which an
 * isolated process cannot reach and which blocked attempt 2 forever (`ExoPlayerImpl.lambda$new$3`, Media3 1.11.1).
 *
 * One thread per load; [release] stops it and releases the extractor. Input: [BrokerMediaDataSource] over the main
 * process binder; nothing is opened by path. Clipped at [clipUs].
 */
@UnstableApi
class ExtractorAssetLoader(
    private val source: MediaDataSource,
    private val clipUs: Long,
    private val listener: AssetLoader.Listener,
) : AssetLoader {
    @Volatile private var released = false

    @Volatile private var progress = 0
    private var thread: Thread? = null

    override fun start() {
        thread = Thread({ run() }, "s4-extractor").apply { start() }
    }

    override fun getProgress(progressHolder: ProgressHolder): Int {
        progressHolder.progress = progress
        return Transformer.PROGRESS_STATE_AVAILABLE
    }

    override fun getDecoderNames(): ImmutableMap<Int, String> = ImmutableMap.of()

    override fun release() {
        released = true
        thread?.interrupt()
    }

    private class Track(val index: Int, val format: Format) {
        var consumer: SampleConsumer? = null
        var ended = false
    }

    private fun run() {
        val extractor = MediaExtractor()
        try {
            extractor.setDataSource(source)
            val tracks = (0 until extractor.trackCount).mapNotNull { index ->
                val media = extractor.getTrackFormat(index)
                val mime = media.getString(MediaFormat.KEY_MIME) ?: return@mapNotNull null
                if (!mime.startsWith("video/") && !mime.startsWith("audio/")) return@mapNotNull null
                Track(index, MediaFormatUtil.createFormatFromMediaFormat(media))
            }
                // First video and first audio track only.
                .groupBy { it.format.sampleMimeType?.substringBefore('/') }
                .values.map { it.first() }
            if (tracks.isEmpty()) throw IOException("NO_TRACKS")
            val durationUs = tracks.maxOf { extractor.getTrackFormat(it.index).durationOrZero() }
            listener.onDurationUs(if (durationUs > 0) minOf(durationUs, clipUs) else clipUs)
            listener.onTrackCount(tracks.size)
            tracks.forEach { track ->
                extractor.selectTrack(track.index)
                // Encoded output; Transformer decodes (and re-encodes) itself.
                listener.onTrackAdded(track.format, AssetLoader.SUPPORTED_OUTPUT_TYPE_ENCODED)
            }
            tracks.forEach { track -> track.consumer = awaitConsumer(track.format) }
            Log.i(TAG, "tracks ${tracks.map { it.format.sampleMimeType }}, duration ${durationUs}us")
            pump(extractor, tracks)
        } catch (interrupted: InterruptedException) {
            // released
        } catch (failure: Exception) {
            if (!released) {
                Log.w(TAG, "extractor failed: ${failure::class.java.simpleName}")
                listener.onError(ExportException.createForAssetLoader(failure, ExportException.ERROR_CODE_IO_UNSPECIFIED))
            }
        } finally {
            runCatching { extractor.release() }
        }
    }

    private fun awaitConsumer(format: Format): SampleConsumer {
        while (true) {
            checkActive()
            listener.onOutputFormat(format)?.let { return it }
            Thread.sleep(RETRY_MS)
        }
    }

    private fun pump(extractor: MediaExtractor, tracks: List<Track>) {
        val byIndex = tracks.associateBy { it.index }
        while (true) {
            checkActive()
            val index = extractor.sampleTrackIndex
            val timeUs = extractor.sampleTime
            if (index < 0 || timeUs > clipUs) break
            val track = byIndex[index]
            if (track == null || track.ended) {
                extractor.advance()
                continue
            }
            val consumer = checkNotNull(track.consumer)
            val buffer = awaitBuffer(consumer)
            val size = extractor.sampleSize.toInt().coerceAtLeast(0)
            buffer.ensureSpaceForWrite(size)
            val data = checkNotNull(buffer.data)
            val read = extractor.readSampleData(data, data.position())
            if (read < 0) break
            data.position(data.position() + read)
            buffer.timeUs = timeUs
            buffer.setFlags(if (extractor.sampleFlags and MediaExtractor.SAMPLE_FLAG_SYNC != 0) C.BUFFER_FLAG_KEY_FRAME else 0)
            buffer.flip()
            awaitQueued(consumer)
            if (clipUs > 0) progress = (timeUs * 100 / clipUs).toInt().coerceIn(0, 99)
            extractor.advance()
        }
        tracks.forEach { track ->
            if (track.ended) return@forEach
            val consumer = checkNotNull(track.consumer)
            val buffer = awaitBuffer(consumer)
            buffer.addFlag(C.BUFFER_FLAG_END_OF_STREAM)
            awaitQueued(consumer)
            track.ended = true
        }
        progress = 100
        Log.i(TAG, "input ended")
    }

    private fun awaitBuffer(consumer: SampleConsumer): DecoderInputBuffer {
        while (true) {
            checkActive()
            consumer.inputBuffer?.let { return it }
            Thread.sleep(RETRY_MS)
        }
    }

    private fun awaitQueued(consumer: SampleConsumer) {
        while (!consumer.queueInputBuffer()) {
            checkActive()
            Thread.sleep(RETRY_MS)
        }
    }

    private fun checkActive() {
        if (released || Thread.currentThread().isInterrupted) throw InterruptedException("released")
    }

    private fun MediaFormat.durationOrZero(): Long = if (containsKey(MediaFormat.KEY_DURATION)) getLong(MediaFormat.KEY_DURATION) else 0L

    /** Factory for [androidx.media3.transformer.Transformer.Builder.setAssetLoaderFactory]. */
    class Factory(private val broker: IBinder, private val clipUs: Long) : AssetLoader.Factory {
        override fun createAssetLoader(
            editedMediaItem: EditedMediaItem,
            looper: Looper,
            listener: AssetLoader.Listener,
            compositionSettings: AssetLoader.CompositionSettings,
        ): AssetLoader = ExtractorAssetLoader(BrokerMediaDataSource(broker), clipUs, listener)
    }

    private companion object {
        const val TAG = "S4Extractor"
        const val RETRY_MS = 2L
    }
}

/** `MediaDataSource` over the [InputBroker] binder (same protocol as [BrokerDataSource]; at most 64 KiB per call). */
class BrokerMediaDataSource(private val broker: IBinder) : MediaDataSource() {
    private val length: Long by lazy { call(S4Protocol.BROKER_LENGTH) { }.let { reply -> reply.readLong().also { reply.recycle() } } }

    override fun readAt(position: Long, buffer: ByteArray, offset: Int, size: Int): Int {
        if (size == 0) return 0
        if (position >= length) return -1
        var done = 0
        while (done < size) {
            val wanted = minOf(size - done, S4Protocol.MAX_READ)
            val reply = call(S4Protocol.BROKER_READ) {
                writeLong(position + done)
                writeInt(wanted)
            }
            val read = reply.readInt()
            val data = reply.createByteArray() ?: ByteArray(0)
            reply.recycle()
            if (read <= 0) break
            if (read > wanted || data.size != read) throw IOException("INVALID_READ")
            System.arraycopy(data, 0, buffer, offset + done, read)
            done += read
            if (read < wanted) break
        }
        return if (done == 0) -1 else done
    }

    override fun getSize(): Long = length

    override fun close() = Unit

    private inline fun call(code: Int, write: Parcel.() -> Unit): Parcel {
        val data = Parcel.obtain()
        val reply = Parcel.obtain()
        try {
            data.writeInterfaceToken(S4Protocol.BROKER_DESCRIPTOR)
            data.write()
            if (!broker.transact(code, data, reply, 0)) throw IOException("BROKER_PROTOCOL")
            reply.readException()
            return reply
        } catch (gone: RemoteException) {
            reply.recycle()
            throw IOException("SOURCE_DISCONNECTED")
        } catch (failure: RuntimeException) {
            reply.recycle()
            throw IOException("SOURCE_IO_FAILED")
        } finally {
            data.recycle()
        }
    }
}
