package com.videokit.spike.s4

import android.net.Uri
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.media3.common.C
import androidx.media3.common.DataReader
import androidx.media3.common.Format
import androidx.media3.common.util.ParsableByteArray
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.DataSpec
import androidx.media3.decoder.DecoderInputBuffer
import androidx.media3.extractor.DefaultExtractorInput
import androidx.media3.extractor.DefaultExtractorsFactory
import androidx.media3.extractor.Extractor
import androidx.media3.extractor.ExtractorInput
import androidx.media3.extractor.ExtractorOutput
import androidx.media3.extractor.PositionHolder
import androidx.media3.extractor.SeekMap
import androidx.media3.extractor.TrackOutput
import androidx.media3.transformer.AssetLoader
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.ExportException
import androidx.media3.transformer.ProgressHolder
import androidx.media3.transformer.SampleConsumer
import androidx.media3.transformer.Transformer
import com.google.common.collect.ImmutableMap
import java.io.EOFException
import java.io.IOException

/**
 * S4 attempt 4 (option a′, lead ruling 2026-11-07): demuxing with the pure-Java Media3 extractors (`media3-extractor`,
 * already in the graph through Transformer/ExoPlayer) inside the isolated worker. Unlike the platform `MediaExtractor`
 * (attempt 3, blocked on the `media.extractor` service) and ExoPlayer (attempt 2, blocked on `media.audio_flinger`),
 * nothing here looks up a system service: the bytes come from the main process through [BrokerDataSource], parsing is
 * plain Java, and the compressed samples go to Transformer (which decodes them with MediaCodec; [DecodeProbe] checks
 * that separately in the same run).
 *
 * One thread per load. Samples are handed over synchronously from [TrackOutput.sampleMetadata], in file order; the
 * first video and the first audio track are kept, every other track is read and discarded. Each kept track ends at
 * [clipUs]. [release] interrupts the thread and releases the extractor; a blocked broker read fails when the main
 * process revokes the broker.
 */
@UnstableApi
class JavaExtractorAssetLoader(
    private val broker: IBinder,
    private val clipUs: Long,
    private val listener: AssetLoader.Listener,
) : AssetLoader {
    @Volatile private var released = false

    @Volatile private var progress = 0
    private var thread: Thread? = null

    override fun start() {
        thread = Thread({ run() }, "s4-java-extractor").apply { start() }
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

    private fun run() {
        val demuxer = JavaDemuxer(broker) { checkActive() }
        try {
            val output = Output()
            demuxer.open(output)
            Log.i(TAG, "extractor ${demuxer.extractorName}")
            while (!output.allEnded()) {
                checkActive()
                if (!demuxer.readOnce()) break
            }
            output.endAll()
            progress = 100
            Log.i(TAG, "input ended, samples ${output.queued}")
        } catch (interrupted: InterruptedException) {
            // released
        } catch (failure: Exception) {
            if (!released) {
                Log.w(TAG, "java extractor failed: ${failure::class.java.simpleName}")
                listener.onError(ExportException.createForAssetLoader(failure, ExportException.ERROR_CODE_IO_UNSPECIFIED))
            }
        } finally {
            demuxer.close()
        }
    }

    /** Extractor output: selects tracks, then announces them to Transformer before the first sample. */
    private inner class Output : ExtractorOutput {
        private val tracks = LinkedHashMap<Int, Track>()
        private var seekMap: SeekMap? = null
        private var announced = false
        var queued = 0L
            private set

        override fun track(id: Int, type: Int): TrackOutput = tracks.getOrPut(id) { Track(type) }

        override fun endTracks() = Unit

        override fun seekMap(seekMap: SeekMap) {
            this.seekMap = seekMap
        }

        fun allEnded(): Boolean = announced && tracks.values.filter { it.selected }.all { it.ended }

        /** Selects the first video and the first audio track with a format and hands them to Transformer. */
        fun announce() {
            if (announced) return
            announced = true
            val kept = listOf(C.TRACK_TYPE_VIDEO, C.TRACK_TYPE_AUDIO).mapNotNull { type ->
                tracks.values.firstOrNull { it.type == type && it.format != null }
            }
            if (kept.isEmpty()) throw IOException("NO_TRACKS")
            kept.forEach { it.selected = true }
            val durationUs = seekMap?.durationUs?.takeIf { it != C.TIME_UNSET && it > 0 }
            listener.onDurationUs(durationUs?.let { minOf(it, clipUs) } ?: clipUs)
            listener.onTrackCount(kept.size)
            // Encoded output; Transformer decodes (and re-encodes) itself.
            kept.forEach { listener.onTrackAdded(checkNotNull(it.format), AssetLoader.SUPPORTED_OUTPUT_TYPE_ENCODED) }
            kept.forEach { it.consumer = awaitConsumer(checkNotNull(it.format)) }
            Log.i(TAG, "tracks ${kept.map { it.format?.sampleMimeType }}, duration ${durationUs}us")
        }

        fun endAll() {
            if (!announced) announce()
            tracks.values.filter { it.selected && !it.ended }.forEach { it.end() }
        }

        /**
         * One track. Bytes arrive through [sampleData] ahead of [sampleMetadata], which then names the last sample as
         * `size` bytes ending `offset` bytes before the end of the pending data (the [TrackOutput] contract).
         */
        private inner class Track(val type: Int) : TrackOutput {
            var format: Format? = null
            var selected = false
            var ended = false
            var consumer: SampleConsumer? = null
            private var pending = ByteArray(INITIAL_PENDING)
            private var pendingSize = 0

            override fun format(format: Format) {
                this.format = format
            }

            override fun sampleData(input: DataReader, length: Int, allowEndOfInput: Boolean, sampleDataPart: Int): Int {
                ensurePending(length)
                val read = input.read(pending, pendingSize, length)
                if (read == C.RESULT_END_OF_INPUT) {
                    if (allowEndOfInput) return C.RESULT_END_OF_INPUT
                    throw EOFException()
                }
                pendingSize += read
                return read
            }

            override fun sampleData(data: ParsableByteArray, length: Int, sampleDataPart: Int) {
                ensurePending(length)
                data.readBytes(pending, pendingSize, length)
                pendingSize += length
            }

            override fun sampleMetadata(timeUs: Long, flags: Int, size: Int, offset: Int, cryptoData: TrackOutput.CryptoData?) {
                val end = pendingSize - offset
                val start = end - size
                if (start < 0 || end > pendingSize) throw IOException("INVALID_SAMPLE")
                if (!announced) announce()
                if (selected && !ended) {
                    if (timeUs > clipUs) {
                        end()
                    } else {
                        queue(start, size, timeUs, flags)
                        if (clipUs > 0 && type == C.TRACK_TYPE_VIDEO) progress = (timeUs * 100 / clipUs).toInt().coerceIn(0, 99)
                    }
                }
                // Drop the sample (and anything before it); keep the `offset` bytes of the next one.
                System.arraycopy(pending, end, pending, 0, offset)
                pendingSize = offset
            }

            private fun queue(start: Int, size: Int, timeUs: Long, flags: Int) {
                val target = checkNotNull(consumer)
                val buffer = awaitBuffer(target)
                buffer.ensureSpaceForWrite(size)
                val data = checkNotNull(buffer.data)
                data.put(pending, start, size)
                buffer.timeUs = timeUs
                buffer.setFlags(flags and C.BUFFER_FLAG_KEY_FRAME)
                buffer.flip()
                awaitQueued(target)
                queued++
            }

            fun end() {
                val target = checkNotNull(consumer)
                val buffer = awaitBuffer(target)
                buffer.addFlag(C.BUFFER_FLAG_END_OF_STREAM)
                awaitQueued(target)
                ended = true
            }

            private fun ensurePending(extra: Int) {
                if (pendingSize + extra <= pending.size) return
                pending = pending.copyOf(maxOf(pending.size * 2, pendingSize + extra))
            }
        }
    }

    private fun awaitConsumer(format: Format): SampleConsumer {
        while (true) {
            checkActive()
            listener.onOutputFormat(format)?.let { return it }
            Thread.sleep(RETRY_MS)
        }
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

    /** Factory for [Transformer.Builder.setAssetLoaderFactory]. */
    class Factory(private val broker: IBinder, private val clipUs: Long) : AssetLoader.Factory {
        override fun createAssetLoader(
            editedMediaItem: EditedMediaItem,
            looper: Looper,
            listener: AssetLoader.Listener,
            compositionSettings: AssetLoader.CompositionSettings,
        ): AssetLoader = JavaExtractorAssetLoader(broker, clipUs, listener)
    }

    private companion object {
        const val TAG = "S4JavaExtractor"
        const val RETRY_MS = 2L
        const val INITIAL_PENDING = 256 * 1024
    }
}

/**
 * Pure-Java demuxing over the broker: sniffs the Media3 default extractors, then reads one step at a time and follows
 * the extractor's seeks by reopening [BrokerDataSource] at the requested position. Shared by the asset loader and the
 * [DecodeProbe].
 */
@UnstableApi
class JavaDemuxer(private val broker: IBinder, private val checkActive: () -> Unit = {}) {
    private val source = BrokerDataSource(broker)
    private val position = PositionHolder()
    private var extractor: Extractor? = null
    private var input: ExtractorInput? = null
    private var length = C.LENGTH_UNSET.toLong()

    val extractorName: String? get() = extractor?.underlyingImplementation?.javaClass?.simpleName

    fun open(output: ExtractorOutput) {
        val candidates = DefaultExtractorsFactory().setTextTrackTranscodingEnabled(false).createExtractors()
        var chosen: Extractor? = null
        for (candidate in candidates) {
            checkActive()
            val probe = openAt(0L)
            val matched = try {
                candidate.sniff(probe)
            } catch (eof: EOFException) {
                false
            } finally {
                probe.resetPeekPosition()
            }
            if (matched) {
                chosen = candidate
                break
            }
        }
        candidates.filter { it !== chosen }.forEach { runCatching { it.release() } }
        val selected = chosen ?: throw IOException("UNRECOGNIZED_CONTAINER")
        extractor = selected
        input = openAt(0L)
        selected.init(output)
    }

    /** One extractor step; false at the end of the input. */
    fun readOnce(): Boolean {
        val current = checkNotNull(extractor)
        when (current.read(checkNotNull(input), position)) {
            Extractor.RESULT_CONTINUE -> return true

            Extractor.RESULT_SEEK -> {
                input = openAt(position.position)
                return true
            }

            else -> return false
        }
    }

    fun close() {
        runCatching { extractor?.release() }
        runCatching { source.close() }
    }

    private fun openAt(at: Long): ExtractorInput {
        runCatching { source.close() }
        val remaining = source.open(DataSpec.Builder().setUri(Uri.parse("s4://input")).setPosition(at).build())
        if (length == C.LENGTH_UNSET.toLong()) length = at + remaining
        return DefaultExtractorInput(source, at, length)
    }
}
