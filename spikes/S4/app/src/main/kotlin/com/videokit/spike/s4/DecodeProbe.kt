package com.videokit.spike.s4

import android.graphics.ImageFormat
import android.media.ImageReader
import android.media.MediaCodec
import android.media.MediaCodecList
import android.os.IBinder
import android.os.SystemClock
import android.util.Log
import androidx.media3.common.C
import androidx.media3.common.DataReader
import androidx.media3.common.Format
import androidx.media3.common.util.MediaFormatUtil
import androidx.media3.common.util.ParsableByteArray
import androidx.media3.common.util.UnstableApi
import androidx.media3.extractor.ExtractorOutput
import androidx.media3.extractor.SeekMap
import androidx.media3.extractor.TrackOutput
import java.io.EOFException
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/**
 * S4 attempt 4: does MediaCodec *decode* in the isolated process (D1 only proved encoding)? Three bounded steps, each
 * on its own thread so a blocking call shows as `HUNG` instead of stalling the worker (the main process watchdog
 * allows [STEP_TIMEOUT_MS] < 5 s between messages; every step reports):
 * 1. `demux`: the first [SAMPLES] video samples through [JavaDemuxer] (pure Java, via the broker);
 * 2. `buffer`: decode them with `MediaCodec` to ByteBuffers (codec lookup via `MediaCodecList`);
 * 3. `surface`: decode them to an `ImageReader` surface (`PRIVATE`), as Transformer decodes to a surface.
 * Results are `step=OK:...` or `step=FAIL:<type>` / `step=HUNG` / `step=SKIPPED`.
 */
@UnstableApi
class DecodeProbe(private val broker: IBinder, private val report: (String) -> Unit) {
    private class Sample(val data: ByteArray, val timeUs: Long, val key: Boolean)

    private var format: Format? = null
    private val samples = ArrayList<Sample>()

    fun run() {
        val demux = step("demux") { demux() }
        report(demux)
        if (!demux.startsWith("demux=OK")) {
            report("buffer=SKIPPED")
            report("surface=SKIPPED")
            return
        }
        report(step("buffer") { decode(toSurface = false) })
        report(step("surface") { decode(toSurface = true) })
    }

    private fun step(name: String, body: () -> String): String {
        var result = "$name=HUNG"
        val done = CountDownLatch(1)
        val started = SystemClock.elapsedRealtime()
        Thread({
            result = runCatching { "$name=OK:${body()}" }.getOrElse { "$name=FAIL:${it::class.java.simpleName}" }
            done.countDown()
        }, "s4-probe-$name").apply { isDaemon = true }.start()
        done.await(STEP_TIMEOUT_MS, TimeUnit.MILLISECONDS)
        val line = "$result:ms=${SystemClock.elapsedRealtime() - started}"
        Log.i(TAG, line)
        return line
    }

    private fun demux(): String {
        val demuxer = JavaDemuxer(broker)
        try {
            val output = CollectOutput()
            demuxer.open(output)
            while (samples.size < SAMPLES && demuxer.readOnce()) Unit
            val video = format ?: throw IllegalStateException("NO_VIDEO")
            return "${demuxer.extractorName}:${video.sampleMimeType}:${video.width}x${video.height}:samples=${samples.size}"
        } finally {
            demuxer.close()
        }
    }

    private fun decode(toSurface: Boolean): String {
        val video = checkNotNull(format)
        val mediaFormat = MediaFormatUtil.createMediaFormatFromFormat(video)
        val name = MediaCodecList(MediaCodecList.REGULAR_CODECS).findDecoderForFormat(mediaFormat)
            ?: throw IllegalStateException("NO_DECODER")
        val reader = if (toSurface) ImageReader.newInstance(video.width, video.height, ImageFormat.PRIVATE, IMAGES) else null
        val codec = MediaCodec.createByCodecName(name)
        var rendered = 0
        var outputs = 0
        try {
            codec.configure(mediaFormat, reader?.surface, null, 0)
            codec.start()
            val info = MediaCodec.BufferInfo()
            var next = 0
            var inputEnded = false
            val deadline = SystemClock.elapsedRealtime() + DECODE_BUDGET_MS
            while (SystemClock.elapsedRealtime() < deadline) {
                if (!inputEnded) {
                    val index = codec.dequeueInputBuffer(DEQUEUE_US)
                    if (index >= 0) {
                        if (next < samples.size) {
                            val sample = samples[next++]
                            checkNotNull(codec.getInputBuffer(index)).put(sample.data)
                            val flags = if (sample.key) MediaCodec.BUFFER_FLAG_KEY_FRAME else 0
                            codec.queueInputBuffer(index, 0, sample.data.size, sample.timeUs, flags)
                        } else {
                            codec.queueInputBuffer(index, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM)
                            inputEnded = true
                        }
                    }
                }
                val out = codec.dequeueOutputBuffer(info, DEQUEUE_US)
                if (out >= 0) {
                    if (info.size > 0) outputs++
                    codec.releaseOutputBuffer(out, toSurface)
                    if (info.flags and MediaCodec.BUFFER_FLAG_END_OF_STREAM != 0) break
                }
                reader?.acquireLatestImage()?.let {
                    rendered++
                    it.close()
                }
            }
        } finally {
            runCatching { codec.stop() }
            runCatching { codec.release() }
            runCatching { reader?.close() }
        }
        if (outputs == 0) throw IllegalStateException("NO_OUTPUT")
        return "$name:frames=$outputs${if (toSurface) ":images=$rendered" else ""}"
    }

    /** Keeps the first video track's format and its first [SAMPLES] samples; discards everything else. */
    private inner class CollectOutput : ExtractorOutput {
        private val tracks = HashMap<Int, Track>()

        override fun track(id: Int, type: Int): TrackOutput = tracks.getOrPut(id) { Track(type) }

        override fun endTracks() = Unit

        override fun seekMap(seekMap: SeekMap) = Unit

        private inner class Track(val type: Int) : TrackOutput {
            private var pending = ByteArray(256 * 1024)
            private var size = 0
            private var kept = false

            override fun format(format: Format) {
                if (type == C.TRACK_TYPE_VIDEO && this@DecodeProbe.format == null) {
                    this@DecodeProbe.format = format
                    kept = true
                }
            }

            override fun sampleData(input: DataReader, length: Int, allowEndOfInput: Boolean, sampleDataPart: Int): Int {
                grow(length)
                val read = input.read(pending, size, length)
                if (read == C.RESULT_END_OF_INPUT) {
                    if (allowEndOfInput) return C.RESULT_END_OF_INPUT
                    throw EOFException()
                }
                size += read
                return read
            }

            override fun sampleData(data: ParsableByteArray, length: Int, sampleDataPart: Int) {
                grow(length)
                data.readBytes(pending, size, length)
                size += length
            }

            override fun sampleMetadata(timeUs: Long, flags: Int, sampleSize: Int, offset: Int, cryptoData: TrackOutput.CryptoData?) {
                val end = size - offset
                if (kept && samples.size < SAMPLES) {
                    samples += Sample(pending.copyOfRange(end - sampleSize, end), timeUs, flags and C.BUFFER_FLAG_KEY_FRAME != 0)
                }
                System.arraycopy(pending, end, pending, 0, offset)
                size = offset
            }

            private fun grow(extra: Int) {
                if (size + extra > pending.size) pending = pending.copyOf(maxOf(pending.size * 2, size + extra))
            }
        }
    }

    private companion object {
        const val TAG = "S4Probe"
        const val SAMPLES = 30
        const val IMAGES = 4
        const val STEP_TIMEOUT_MS = 4_000L
        const val DECODE_BUDGET_MS = 3_000L
        const val DEQUEUE_US = 10_000L
    }
}
