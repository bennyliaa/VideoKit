package com.videokit.core.spi

import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitSurfaceTarget
import kotlinx.coroutines.flow.StateFlow

/** Information about an opened image, read from its header (06 §6.1). */
public data class ImageInfo(
    /** Size after EXIF orientation, in pixels. */
    val size: Size,
    /** Whether animated (GIF, animated WebP/AVIF). */
    val animated: Boolean,
    /** Duration of one animation loop, when animated and known. */
    val loopDurationUs: Long? = null,
    /** Number of frames (1 for static images), if known. */
    val frameCount: Int? = null,
    /** Format name in lower case (`jpeg`, `png`, `webp`, `gif`, `heif`, `avif`, `bmp`), if known. */
    val format: String? = null,
    /** Clockwise EXIF rotation already applied to [size]: 0, 90, 180 or 270. */
    val orientationDeg: Int = 0,
    /** Whether the image has an alpha channel, if known. */
    val hasAlpha: Boolean? = null,
    /** Whether the engine can decode regions of this image (tiles, 06 §6.2). */
    val regionDecodable: Boolean = false,
    /** Size of the encoded file in bytes, as read from the host source (04A P2 fileSizeBytes), if known. */
    val fileSizeBytes: Long? = null,
)

/** A rectangle in pixels of the oriented image; [right] and [bottom] are exclusive. */
public data class PixelRect(
    /** Left edge. */
    val left: Int,
    /** Top edge. */
    val top: Int,
    /** Right edge (exclusive). */
    val right: Int,
    /** Bottom edge (exclusive). */
    val bottom: Int,
) {
    /** Width. */
    val width: Int get() = right - left

    /** Height. */
    val height: Int get() = bottom - top
}

/** One high-resolution tile of an [ImageRenderPlan]: [region] of the oriented image decoded at [sampleSize]. */
public data class ImageTile(
    /** Region of the oriented image. */
    val region: PixelRect,
    /** Subsampling factor (power of two, 1 = full resolution). */
    val sampleSize: Int,
)

/**
 * What the engine decodes and draws (06 §6.2), computed by the platform independent image rules (`videokit-image`)
 * from the image size, the render target, the transform and the memory quota. The engine draws the whole image
 * into the target from the [decodeSize] decode and the [tiles] on top of it; it makes no decisions itself.
 */
public data class ImageRenderPlan(
    /** Size the whole image is decoded at (ImageDecoder target size), at most the oriented size. */
    val decodeSize: Size,
    /** Subsampling of [decodeSize] relative to the oriented size, rounded up to a power of two (diagnostics). */
    val baseSampleSize: Int,
    /** Tiles of the visible region at a finer sampling; empty when the base decode is sharp enough. */
    val tiles: List<ImageTile> = emptyList(),
)

/** Options of [ImageEngine.open]. */
public data class ImageOpenOptions(
    /** Initial looping of animated images (04A L1: on by default). */
    val looping: Boolean = true,
)

/** State of an opened image. */
public enum class ImageStatus {
    /** Header read; nothing decoded yet. */
    OPENED,

    /** The current plan is decoded (static) or the animation is ready. */
    READY,

    /** Animation reached its last frame without looping. */
    ENDED,

    /** Failed; see [ImageEngineState.error]. */
    FAILED,
}

/** Snapshot of an opened image. Animated images update [positionUs] at least every 250 ms while animating. */
public data class ImageEngineState(
    /** Status. */
    val status: ImageStatus,
    /** Whether the animation runs. */
    val animating: Boolean = false,
    /** Position within the animation loop. */
    val positionUs: Long = 0L,
    /** Bytes of decoded bitmaps currently held (base, tiles and animation frames). */
    val decodedBytes: Long = 0L,
    /** Plan in effect, once one was rendered. */
    val plan: ImageRenderPlan? = null,
    /** Error when [status] is [ImageStatus.FAILED]. */
    val error: VideoKitStableError? = null,
)

/**
 * Image decoding and display (02 §4.2 `ImageEngine`; Android: ImageDecoder, BitmapRegionDecoder and
 * AnimatedImageDrawable in `videokit-image-android`).
 *
 * Contract:
 * - [open] reads the header (format, oriented size, animation) through the host source and throws [SpiException]
 *   with `UNSUPPORTED_CONTAINER` / `CORRUPT_MEDIA` / a source error when it cannot; it decodes nothing yet.
 * - All read handles are closed when [ImageHandle.close] returns (06 §7).
 * - Decode failures after open are reported through [ImageEngineState.status] = FAILED.
 */
public interface ImageEngine {
    /** Opens [source]. */
    public suspend fun open(source: VideoKitMediaSource, options: ImageOpenOptions = ImageOpenOptions()): ImageHandle

    /** Whether [target] is a render target type this engine can draw into (04A I13). */
    public fun supports(target: VideoKitSurfaceTarget): Boolean
}

/** An opened image. Closing releases bitmaps, the animation, the render target and all read handles. */
public interface ImageHandle : AutoCloseable {
    /** Image information. */
    public val info: ImageInfo

    /** State. */
    public val state: StateFlow<ImageEngineState>

    /**
     * Decodes what [plan] says and draws it when attached; suspends until decoded. Throws [SpiException] when the
     * image cannot be decoded (the state then reports FAILED).
     */
    public suspend fun render(plan: ImageRenderPlan)

    /** Renders to [target]; replaces the previous target and redraws the current plan. */
    public fun attach(target: VideoKitSurfaceTarget)

    /** Stops rendering. */
    public fun detach()

    /** Starts or resumes the animation (no effect for static images). */
    public suspend fun play()

    /** Pauses the animation on the current frame. */
    public suspend fun pause()

    /** Restarts the animation from its first frame (replay after ENDED). */
    public suspend fun restart()

    /** Loops the animation instead of stopping on the last frame (04A L1). */
    public suspend fun setLooping(looping: Boolean)

    /** A JPEG thumbnail of the (first frame of the) image fitting [maxSize] (04A P1); throws [SpiException]. */
    public suspend fun thumbnail(maxSize: Size): ThumbnailResult.Captured
}
