package com.videokit.export.android

import android.net.Uri
import android.os.IBinder
import android.os.Looper
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
 * Transformer [AssetLoader] of one clip `[inUs, outUs)` of the broker source (M6-B1 pass-through export). Demuxes
 * with the pure-Java Media3 extractors, so the worker never creates an ExoPlayer and never runs its audio
 * initialization (15 §2.8, S4 attempts 2–4); Transformer decodes and re-encodes the compressed samples.
 *
 * The clip starts at the key frame at or before `inUs` ([startUs]; an exact in point needs the composition engine
 * after S3) and output timestamps start at 0. The first video and the first audio track are kept; samples of other
 * tracks are read and dropped. Each kept track ends before `outUs`.
 */
@UnstableApi
internal class ClipAssetLoader(
    private val broker: IBinder,
    private val inUs: Long,
    private val outUs: Long,
    private val listener: AssetLoader.Listener,
    private val onStart: (Long) -> Unit,
) : AssetLoader {
    @Volatile private var released = false

    @Volatile private var progress = 0
    private var thread: Thread? = null

    override fun start() {
        thread = Thread({ run() }, "videokit-export-demux").apply { start() }
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
            // Read until the container's seek map is known, then go to the key frame at or before the in point.
            while (output.seekMap == null && !output.sawSample) {
                checkActive()
                if (!demuxer.readOnce()) break
            }
            val seekMap = output.seekMap
            output.startUs = if (inUs > 0 && seekMap != null && seekMap.isSeekable) {
                val point = seekMap.getSeekPoints(inUs).first
                demuxer.seekTo(point.position, point.timeUs)
                point.timeUs.coerceAtMost(inUs)
            } else {
                if (inUs > 0) throw IOException("SEEK_UNSUPPORTED")
                0L
            }
            onStart(output.startUs)
            while (!output.allEnded()) {
                checkActive()
                if (!demuxer.readOnce()) break
            }
            output.endAll()
            progress = 100
        } catch (interrupted: InterruptedException) {
            // released
        } catch (failure: Exception) {
            if (!released) listener.onError(ExportException.createForAssetLoader(failure, ExportException.ERROR_CODE_IO_UNSPECIFIED))
        } finally {
            demuxer.close()
        }
    }

    private inner class Output : ExtractorOutput {
        private val tracks = LinkedHashMap<Int, Track>()
        var seekMap: SeekMap? = null
        var sawSample = false
        var startUs = 0L
        private var announced = false

        override fun track(id: Int, type: Int): TrackOutput = tracks.getOrPut(id) { Track(type) }

        override fun endTracks() = Unit

        override fun seekMap(seekMap: SeekMap) {
            this.seekMap = seekMap
        }

        fun allEnded(): Boolean = announced && tracks.values.filter { it.selected }.all { it.ended }

        fun announce() {
            if (announced) return
            announced = true
            val kept = listOf(C.TRACK_TYPE_VIDEO, C.TRACK_TYPE_AUDIO).mapNotNull { type ->
                tracks.values.firstOrNull { it.type == type && it.format != null }
            }
            if (kept.isEmpty()) throw IOException("NO_TRACKS")
            kept.forEach { it.selected = true }
            listener.onDurationUs(outUs - startUs)
            listener.onTrackCount(kept.size)
            kept.forEach { listener.onTrackAdded(checkNotNull(it.format), AssetLoader.SUPPORTED_OUTPUT_TYPE_ENCODED) }
            kept.forEach { it.consumer = awaitConsumer(checkNotNull(it.format)) }
        }

        fun endAll() {
            if (!announced) announce()
            tracks.values.filter { it.selected && !it.ended }.forEach { it.end() }
        }

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
                sawSample = true
                // Samples before the seek (while the seek map was looked for) are dropped; the loader seeks afterwards.
                if (seekMap != null || inUs == 0L) {
                    if (!announced) announce()
                    if (selected && !ended && timeUs >= startUs) {
                        if (timeUs >= outUs) {
                            end()
                        } else {
                            queue(start, size, timeUs - startUs, flags)
                            if (type == C.TRACK_TYPE_VIDEO) {
                                progress = ((timeUs - startUs) * 100 / (outUs - startUs)).toInt().coerceIn(0, 99)
                            }
                        }
                    }
                }
                System.arraycopy(pending, end, pending, 0, offset)
                pendingSize = offset
            }

            private fun queue(start: Int, size: Int, timeUs: Long, flags: Int) {
                val target = checkNotNull(consumer)
                val buffer = awaitBuffer(target)
                buffer.ensureSpaceForWrite(size)
                checkNotNull(buffer.data).put(pending, start, size)
                buffer.timeUs = timeUs
                buffer.setFlags(flags and C.BUFFER_FLAG_KEY_FRAME)
                buffer.flip()
                awaitQueued(target)
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
    class Factory(
        private val broker: IBinder,
        private val inUs: Long,
        private val outUs: Long,
        private val onStart: (Long) -> Unit,
    ) : AssetLoader.Factory {
        override fun createAssetLoader(
            editedMediaItem: EditedMediaItem,
            looper: Looper,
            listener: AssetLoader.Listener,
            compositionSettings: AssetLoader.CompositionSettings,
        ): AssetLoader = ClipAssetLoader(broker, inUs, outUs, listener, onStart)
    }

    private companion object {
        const val RETRY_MS = 2L
        const val INITIAL_PENDING = 256 * 1024
    }
}

/** Pure-Java demuxing over the broker (S4 attempt 4): sniffs the Media3 default extractors, follows their seeks. */
@UnstableApi
internal class JavaDemuxer(broker: IBinder, private val checkActive: () -> Unit = {}) {
    private val source = BrokerDataSource(broker)
    private val position = PositionHolder()
    private var extractor: Extractor? = null
    private var input: ExtractorInput? = null
    private var length = C.LENGTH_UNSET.toLong()

    fun open(output: ExtractorOutput) {
        // Text tracks are not exported; no transcoding of subtitles during extraction.
        @Suppress("DEPRECATION")
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
    fun readOnce(): Boolean = when (checkNotNull(extractor).read(checkNotNull(input), position)) {
        Extractor.RESULT_CONTINUE -> true

        Extractor.RESULT_SEEK -> {
            input = openAt(position.position)
            true
        }

        else -> false
    }

    /** Seeks to the byte [position] of the seek point at [timeUs]. */
    fun seekTo(position: Long, timeUs: Long) {
        checkNotNull(extractor).seek(position, timeUs)
        input = openAt(position)
    }

    fun close() {
        runCatching { extractor?.release() }
        runCatching { source.close() }
    }

    private fun openAt(at: Long): ExtractorInput {
        runCatching { source.close() }
        val remaining = source.open(DataSpec.Builder().setUri(Uri.parse("videokit-export://input")).setPosition(at).build())
        if (length == C.LENGTH_UNSET.toLong() && remaining != C.LENGTH_UNSET.toLong()) length = at + remaining
        return DefaultExtractorInput(source, at, length)
    }
}
