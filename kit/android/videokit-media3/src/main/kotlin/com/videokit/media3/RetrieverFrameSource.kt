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
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer

/**
 * [FrameSource] for thumbnails (04A P1) with the platform `MediaMetadataRetriever` over the host's `readAt`
 * (15 §2.4: the documented alternative to Media3's experimental frame extractor; S1 compares both). Frames stay in
 * memory; nothing is written to disk. m2ts sources are not supported by the retriever and fail with
 * UNSUPPORTED_CONTAINER.
 */
public class RetrieverFrameSource(
    private val readTimeoutMs: Long = Media3EngineConfig().readTimeoutMs,
    private val jpegQuality: Int = DEFAULT_JPEG_QUALITY,
) : FrameSource {
    override suspend fun open(source: VideoKitMediaSource): FrameReader = withContext(Dispatchers.IO) {
        val handle = try {
            source.sourceFactory.open(OpenPurpose.PROBE)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
        val retriever = MediaMetadataRetriever()
        try {
            retriever.setDataSource(HostMediaDataSource(handle, readTimeoutMs))
        } catch (failure: Exception) {
            runCatching { retriever.release() }
            runCatching { handle.close() }
            val error =
                PlaybackErrors.hostFailure(failure) ?: StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "RETRIEVER:OPEN")
            throw SpiException(error)
        }
        RetrieverFrameReader(retriever, handle, jpegQuality)
    }

    public companion object {
        /** JPEG quality of thumbnails. */
        public const val DEFAULT_JPEG_QUALITY: Int = 85
    }
}

/** `MediaDataSource` over a host read handle (blocking bridge with timeout, as [HostReader]). */
internal class HostMediaDataSource(private val handle: VideoKitReadHandle, private val readTimeoutMs: Long) : MediaDataSource() {
    override fun readAt(position: Long, buffer: ByteArray, offset: Int, size: Int): Int {
        if (size == 0) return 0
        return blocking(readTimeoutMs, ErrorStage.PROBE) { handle.readAt(position, buffer, offset, size) }
    }

    override fun getSize(): Long = handle.length ?: -1L

    override fun close() = Unit
}

private class RetrieverFrameReader(
    private val retriever: MediaMetadataRetriever,
    private val handle: VideoKitReadHandle,
    private val jpegQuality: Int,
) : FrameReader {
    override suspend fun frameAt(timeUs: Long, maxSize: Size, format: PixelFormat): FrameData = withContext(Dispatchers.IO) {
        val bitmap = frame(timeUs, maxSize)
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

    override suspend fun thumbnailAt(timeUs: Long, maxSize: Size): ThumbnailResult.Captured = withContext(Dispatchers.IO) {
        val bitmap = frame(timeUs, maxSize)
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

    override fun close() {
        runCatching { retriever.release() }
        runCatching { handle.close() }
    }

    /** The frame nearest to [timeUs] (closest sync frame: fast and good enough for thumbnails), fitting [maxSize]. */
    private fun frame(timeUs: Long, maxSize: Size): Bitmap = try {
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
