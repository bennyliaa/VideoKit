package com.videokit.media3

import android.graphics.Bitmap
import android.media.MediaDataSource
import android.media.MediaMetadataRetriever
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.OpenPurpose
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.FrameData
import com.videokit.core.spi.FrameReader
import com.videokit.core.spi.FrameSource
import com.videokit.core.spi.PixelFormat
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference

/**
 * [FrameSource] for thumbnails (04A P1) with the platform `MediaMetadataRetriever` over the host's `readAt`
 * (15 §2.4: the documented alternative to Media3's experimental frame extractor; S1 compares both). Frames stay in
 * memory; nothing is written to disk. m2ts sources are not supported by the retriever and fail with
 * UNSUPPORTED_CONTAINER.
 *
 * Cancellable (04A P5, S1 finding): the retriever blocks in native code while it reads, so every retriever call
 * runs on a dedicated worker thread with this reader's own host read handle. On cancellation (the session's 3 s hard
 * timeout, or the caller) the read handle is closed and reads in flight are cancelled, so the retriever fails fast;
 * the caller returns at once and the late result is discarded. The retriever is released by whichever finishes last:
 * [FrameReader.close] or the worker thread.
 */
public class RetrieverFrameSource(
    private val readTimeoutMs: Long = Media3EngineConfig().readTimeoutMs,
    private val jpegQuality: Int = DEFAULT_JPEG_QUALITY,
) : FrameSource {
    override suspend fun open(source: VideoKitMediaSource): FrameReader {
        val handle = withContext(Dispatchers.IO) {
            try {
                source.sourceFactory.open(OpenPurpose.PROBE)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: Exception) {
                throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
            }
        }
        val extraction = Extraction(handle, readTimeoutMs)
        try {
            extraction.run { retriever ->
                try {
                    retriever.setDataSource(extraction.dataSource)
                } catch (failure: Exception) {
                    val error =
                        PlaybackErrors.hostFailure(failure)
                            ?: StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "RETRIEVER:OPEN")
                    throw SpiException(error)
                }
            }
        } catch (failure: Throwable) {
            // Includes cancellation: the worker releases the retriever when it returns.
            extraction.close()
            throw failure
        }
        return RetrieverFrameReader(extraction, jpegQuality)
    }

    public companion object {
        /** JPEG quality of thumbnails. */
        public const val DEFAULT_JPEG_QUALITY: Int = 85
    }
}

/**
 * Host reads of one extraction that can be aborted from another thread (04A P5): [abort] cancels the read in flight,
 * makes later reads fail at once and closes the host handle.
 */
internal class AbortableReads(private val handle: VideoKitReadHandle) {
    private val aborted = AtomicBoolean(false)
    private val closed = AtomicBoolean(false)
    private val inFlight = AtomicReference<Job?>(null)

    val isAborted: Boolean get() = aborted.get()

    suspend fun <T> read(block: suspend () -> T): T {
        val job = currentCoroutineContext()[Job]
        inFlight.set(job)
        try {
            if (aborted.get()) throw CancellationException("frame extraction aborted")
            return block()
        } finally {
            inFlight.compareAndSet(job, null)
        }
    }

    fun abort() {
        if (!aborted.compareAndSet(false, true)) return
        inFlight.get()?.cancel()
        closeHandle()
    }

    fun closeHandle() {
        if (closed.compareAndSet(false, true)) runCatching { handle.close() }
    }
}

/** `MediaDataSource` over a host read handle (blocking bridge with timeout, as [HostReader]); fails fast once aborted. */
internal class HostMediaDataSource(
    private val handle: VideoKitReadHandle,
    private val readTimeoutMs: Long,
    private val reads: AbortableReads = AbortableReads(handle),
) : MediaDataSource() {
    override fun readAt(position: Long, buffer: ByteArray, offset: Int, size: Int): Int {
        if (size == 0) return 0
        if (reads.isAborted) throw IOException("frame extraction aborted")
        return blocking(readTimeoutMs, ErrorStage.PROBE) { reads.read { handle.readAt(position, buffer, offset, size) } }
    }

    override fun getSize(): Long = handle.length ?: -1L

    override fun close() = Unit
}

/** One retriever with its own host read handle and worker threads (04A P5). */
private class Extraction(handle: VideoKitReadHandle, readTimeoutMs: Long) {
    val retriever = MediaMetadataRetriever()
    private val reads = AbortableReads(handle)
    val dataSource = HostMediaDataSource(handle, readTimeoutMs, reads)
    private val lock = Any()
    private var busy = false
    private var closed = false
    private val released = AtomicBoolean(false)

    /**
     * Runs [work] on a dedicated worker thread. Cancellation aborts the reads and returns at once; the worker's late
     * result is discarded. One call at a time.
     */
    suspend fun <T> run(work: (MediaMetadataRetriever) -> T): T {
        synchronized(lock) {
            if (closed ||
                reads.isAborted
            ) {
                throw SpiException(StableErrors.of(ErrorCode.SESSION_RELEASED, ErrorStage.DECODE, "THUMBNAIL:CLOSED"))
            }
            if (busy) throw SpiException(StableErrors.illegalState(ErrorStage.DECODE, "THUMBNAIL:BUSY"))
            busy = true
        }
        return suspendCancellableCoroutine { continuation ->
            continuation.invokeOnCancellation { reads.abort() }
            val worker = Thread({
                val result = runCatching { work(retriever) }
                val releaseNow = synchronized(lock) {
                    busy = false
                    closed
                }
                if (releaseNow) release()
                // Ignored when the caller was cancelled: the result is discarded (results own no resources).
                continuation.resumeWith(result)
            }, WORKER_NAME)
            worker.isDaemon = true
            worker.start()
        }
    }

    /** Aborts reads and closes the handle; releases the retriever now, or when the worker in progress returns. */
    fun close() {
        val releaseNow = synchronized(lock) {
            closed = true
            !busy
        }
        reads.abort()
        if (releaseNow) release()
    }

    private fun release() {
        if (released.compareAndSet(false, true)) runCatching { retriever.release() }
    }

    companion object {
        const val WORKER_NAME = "videokit-frames"
    }
}

private class RetrieverFrameReader(private val extraction: Extraction, private val jpegQuality: Int) : FrameReader {
    override suspend fun frameAt(timeUs: Long, maxSize: Size, format: PixelFormat): FrameData = extraction.run { retriever ->
        val bitmap = frame(retriever, timeUs, maxSize)
        try {
            val rgba = ByteBuffer.allocate(bitmap.width * bitmap.height * 4)
            bitmap.copyPixelsToBuffer(rgba)
            val pixels = when (format) {
                PixelFormat.RGBA_8888 -> rgba.array()
                PixelFormat.GRAY_8 -> gray(rgba.array())
            }
            FrameData(bitmap.width, bitmap.height, timeUs, format, pixels)
        } finally {
            bitmap.recycle()
        }
    }

    override suspend fun thumbnailAt(timeUs: Long, maxSize: Size): ThumbnailResult.Captured = extraction.run { retriever ->
        val bitmap = frame(retriever, timeUs, maxSize)
        try {
            val out = ByteArrayOutputStream()
            if (!bitmap.compress(Bitmap.CompressFormat.JPEG, jpegQuality, out)) {
                throw SpiException(StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.DECODE, "THUMBNAIL:ENCODE"))
            }
            ThumbnailResult.Captured(out.toByteArray(), bitmap.width, bitmap.height)
        } finally {
            bitmap.recycle()
        }
    }

    /** Never blocks: a worker still in progress releases the retriever when it returns (04A P5). */
    override fun close() = extraction.close()

    /** The frame nearest to [timeUs] (closest sync frame: fast and good enough for thumbnails), fitting [maxSize]. */
    private fun frame(retriever: MediaMetadataRetriever, timeUs: Long, maxSize: Size): Bitmap = try {
        retriever.getScaledFrameAtTime(timeUs, MediaMetadataRetriever.OPTION_CLOSEST_SYNC, maxSize.width, maxSize.height)
    } catch (failure: Exception) {
        throw SpiException(
            PlaybackErrors.hostFailure(failure) ?: StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "THUMBNAIL:FRAME"),
        )
    } ?: throw SpiException(StableErrors.of(ErrorCode.DECODER_UNAVAILABLE, ErrorStage.DECODE, "THUMBNAIL:NO_FRAME"))

    private fun gray(rgba: ByteArray): ByteArray = ByteArray(rgba.size / 4) { i ->
        val r = rgba[i * 4].toInt() and 0xFF
        val g = rgba[i * 4 + 1].toInt() and 0xFF
        val b = rgba[i * 4 + 2].toInt() and 0xFF
        ((r * 299 + g * 587 + b * 114) / 1000).toByte()
    }
}
