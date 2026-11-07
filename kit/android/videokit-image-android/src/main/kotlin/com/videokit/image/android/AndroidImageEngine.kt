// minSdk 31: the platform ExifInterface has the fixes the androidx copy backports (lint ExifInterface is about old
// releases); the engine stays on platform APIs without an extra dependency (15 §2.3).
@file:android.annotation.SuppressLint("ExifInterface")

package com.videokit.image.android

import android.graphics.ImageDecoder
import android.media.ExifInterface
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.Size
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.android.AndroidSurface
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.ImageEngine
import com.videokit.core.spi.ImageHandle
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageOpenOptions
import com.videokit.core.spi.SpiException
import com.videokit.image.AnimationHeaders
import com.videokit.image.EncodedImage
import com.videokit.image.ImageFormats
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayInputStream
import java.nio.ByteBuffer

/** Configuration of [AndroidImageEngine]. */
public data class AndroidImageConfig(
    /** Timeout of one host read (the whole file is read once, 06 §6.2). */
    val readTimeoutMs: Long = 10_000L,
    /** Largest encoded file read into memory. */
    val maxEncodedBytes: Long = EncodedImage.MAX_ENCODED_BYTES,
    /** JPEG quality of thumbnails. */
    val jpegQuality: Int = 85,
)

/**
 * [ImageEngine] with the platform decoders (15 §2.3): `ImageDecoder` for whole images (JPG, PNG, WebP, HEIF, AVIF,
 * BMP; decoded at the plan's target size, EXIF orientation applied by the decoder), `BitmapRegionDecoder` for tiles
 * of large images (EXIF orientation read with `ExifInterface` and applied to the tiles) and `AnimatedImageDrawable`
 * drawn frame by frame into the target surface (GIF, animated WebP/AVIF).
 *
 * The encoded file is read once through the host `readAt` into memory ([EncodedImage]); the host handle is closed
 * before [open] returns. Unknown formats fail with UNSUPPORTED_CONTAINER, undecodable data with CORRUPT_MEDIA.
 */
public class AndroidImageEngine(private val config: AndroidImageConfig = AndroidImageConfig()) : ImageEngine {
    override fun supports(target: VideoKitSurfaceTarget): Boolean = target is AndroidSurface

    override suspend fun open(source: VideoKitMediaSource, options: ImageOpenOptions): ImageHandle = withContext(Dispatchers.IO) {
        val bytes = EncodedImage.read(source, config.readTimeoutMs, config.maxEncodedBytes)
        val probed = ImageProbe.probe(bytes)
        AndroidImageHandle(bytes, probed, options, config)
    }
}

/** Header facts of an encoded image. */
internal class ProbedImage(
    val info: ImageInfo,
    /** Size as stored (before EXIF rotation): the coordinates of BitmapRegionDecoder. */
    val storedSize: Size,
)

/** Reads the header of an encoded image without decoding its pixels. */
internal object ImageProbe {
    fun probe(bytes: ByteArray): ProbedImage {
        val format = ImageFormats.sniff(bytes.copyOf(minOf(bytes.size, ImageFormats.HEADER_BYTES)))
            ?: throw SpiException(StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "IMAGE_FORMAT"))
        var size: Size? = null
        var animated = false
        try {
            ImageDecoder.decodeBitmap(ImageDecoder.createSource(ByteBuffer.wrap(bytes))) { _, info, _ ->
                size = Size(info.size.width, info.size.height)
                animated = info.isAnimated
                throw HeaderRead()
            }
        } catch (_: HeaderRead) {
            // Header only.
        } catch (failure: Exception) {
            throw SpiException(ImageErrors.decodeFailure(failure, ErrorStage.PROBE))
        }
        val oriented = size ?: throw SpiException(StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.PROBE, "IMAGE_HEADER"))
        val exif = if (animated) Exif(0, false) else exif(bytes)
        val stored = if (exif.rotationDeg % 180 != 0) Size(oriented.height, oriented.width) else oriented
        val timing = if (animated) AnimationHeaders.parse(bytes) else null
        val info = ImageInfo(
            size = oriented,
            animated = animated,
            loopDurationUs = timing?.loopDurationUs,
            frameCount = if (animated) timing?.frameCount else 1,
            format = format,
            orientationDeg = exif.rotationDeg,
            hasAlpha = null,
            // Mirrored EXIF orientations are drawn from the whole-image decode only.
            regionDecodable = !animated && !exif.flipped && format in ImageFormats.REGION_DECODABLE,
        )
        return ProbedImage(info, stored)
    }

    private class Exif(val rotationDeg: Int, val flipped: Boolean)

    private fun exif(bytes: ByteArray): Exif = try {
        when (ExifInterface(ByteArrayInputStream(bytes)).getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL)) {
            ExifInterface.ORIENTATION_ROTATE_90 -> Exif(90, false)
            ExifInterface.ORIENTATION_ROTATE_180 -> Exif(180, false)
            ExifInterface.ORIENTATION_ROTATE_270 -> Exif(270, false)
            ExifInterface.ORIENTATION_TRANSPOSE -> Exif(90, true)
            ExifInterface.ORIENTATION_TRANSVERSE -> Exif(270, true)
            ExifInterface.ORIENTATION_FLIP_HORIZONTAL, ExifInterface.ORIENTATION_FLIP_VERTICAL -> Exif(0, true)
            else -> Exif(0, false)
        }
    } catch (_: Exception) {
        Exif(0, false)
    }

    /** Stops ImageDecoder after the header (thrown from the header listener, rethrown by the decoder). */
    private class HeaderRead : RuntimeException() {
        override fun fillInStackTrace(): Throwable = this
    }
}

/** Stable errors of the platform image decoders (no messages: they may contain data). */
internal object ImageErrors {
    fun decodeFailure(failure: Throwable, stage: ErrorStage) = when (failure) {
        is OutOfMemoryError -> StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, stage, "IMAGE_OOM")
        is ImageDecoder.DecodeException -> StableErrors.of(ErrorCode.CORRUPT_MEDIA, stage, "IMAGE_DECODE:${failure.error}")
        is SpiException -> failure.error
        else -> StableErrors.of(ErrorCode.CORRUPT_MEDIA, stage, "IMAGE_DECODE:${failure::class.java.simpleName}")
    }
}
