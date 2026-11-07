package com.videokit.image

import com.videokit.api.ImageDetails
import com.videokit.api.MediaInfo
import com.videokit.api.MediaKind
import com.videokit.api.MediaTransform
import com.videokit.api.Size
import com.videokit.core.spi.ImageEngineState
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageRenderPlan
import com.videokit.core.spi.ImageTile
import com.videokit.core.spi.PixelRect
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/**
 * Platform independent image rules (06 §6.2, 15 §2.3 / §2.10): what to decode for a render target, how much memory
 * that takes, which tiles of a large image to decode for the visible region, and the image facts of the session
 * state. Engines only execute the resulting [ImageRenderPlan].
 *
 * Coordinates: the texture shows the whole oriented image fitted into the target; zoom, pan and rotation are applied
 * by the UI on the texture (06 §5). The visible region of a [MediaTransform] (scale `s`, pan `p` normalized to the
 * content) is centred at `0.5 - p / s` with an extent of `1 / s` of the image in each axis.
 */
public object ImageRules {
    /** Longest texture side the plugins create for an image (GPU texture limit of the device classes, 15 §2.6). */
    public const val MAX_TEXTURE_SIDE: Int = 4096

    /** Bytes per decoded pixel (ARGB_8888). */
    public const val BYTES_PER_PIXEL: Int = 4

    /** Decoded frame buffers an animation holds at a time (current and next frame). */
    public const val ANIMATION_FRAME_BUFFERS: Int = 2

    /** Side of a decoded tile in pixels (BitmapRegionDecoder region at its sample size). */
    public const val TILE_SIDE: Int = 512

    /** Smallest longest side the base decode is degraded to before the quota is reported as exhausted. */
    public const val MIN_DECODE_SIDE: Int = 256

    /** Memory a session asks for at most (06 §6.2), base decode and tiles together. */
    public const val MAX_SESSION_BYTES: Long = 64L * 1024 * 1024

    /** Memory reserved for tiles on top of the base decode of a region decodable image. */
    public const val TILE_ALLOWANCE_BYTES: Long = 16L * 1024 * 1024

    /** Decoded bytes of an image of [size]. */
    public fun bytesOf(size: Size): Long = size.width.toLong() * size.height * BYTES_PER_PIXEL

    /** [size] fitted into [bounds] keeping the aspect ratio, never larger than [size] (no upscaling), at least 1×1. */
    public fun fitWithin(size: Size, bounds: Size): Size {
        if (size.width <= 0 || size.height <= 0) return Size(1, 1)
        val factor = min(1.0, min(bounds.width.toDouble() / size.width, bounds.height.toDouble() / size.height))
        return Size(max(1, (size.width * factor).roundToInt()), max(1, (size.height * factor).roundToInt()))
    }

    /** Texture size for an image of [size]: the image itself, at most [MAX_TEXTURE_SIDE] on its longest side. */
    public fun textureSizeFor(size: Size): Size = fitWithin(size, Size(MAX_TEXTURE_SIDE, MAX_TEXTURE_SIDE))

    /** Smallest power of two `>= value` (at least 1). */
    public fun ceilPowerOfTwo(value: Double): Int {
        var result = 1
        while (result < value && result < MAX_SAMPLE) result *= 2
        return result
    }

    /** Largest power of two `<= value` (at least 1). */
    public fun floorPowerOfTwo(value: Double): Int {
        var result = 1
        while (result * 2 <= value && result < MAX_SAMPLE) result *= 2
        return result
    }

    /** Memory of the base decode of [plan]'s [ImageRenderPlan.decodeSize] for [info]. */
    public fun baseBytes(info: ImageInfo, decodeSize: Size): Long = bytesOf(decodeSize) * if (info.animated) ANIMATION_FRAME_BUFFERS else 1

    /** Memory of [plan] (base decode and tiles). */
    public fun planBytes(info: ImageInfo, plan: ImageRenderPlan): Long =
        baseBytes(info, plan.decodeSize) + plan.tiles.sumOf { tileBytes(it) }

    /** Longest side of the base decode of a region decodable image; tiles add the detail of zoomed regions. */
    public const val BASE_DECODE_SIDE: Int = 2048

    /** Size the whole image is decoded at for a [target] before quota degradation. */
    public fun baseDecodeSize(info: ImageInfo, target: Size): Size {
        val fitted = fitWithin(info.size, target)
        return if (tiles(info)) fitWithin(fitted, Size(BASE_DECODE_SIDE, BASE_DECODE_SIDE)) else fitted
    }

    /**
     * Memory a session reserves for [info] (base decode on the texture the plugins create for it, plus the tile
     * allowance of region decodable images), capped at [MAX_SESSION_BYTES].
     */
    public fun reservationFor(info: ImageInfo): Long {
        val base = baseBytes(info, baseDecodeSize(info, textureSizeFor(info.size)))
        val tiles = if (tiles(info)) TILE_ALLOWANCE_BYTES else 0L
        return min(MAX_SESSION_BYTES, base + tiles)
    }

    /** The reservation to try after [bytes] was denied, or `null` when nothing smaller is useful. */
    public fun degradedReservation(info: ImageInfo, bytes: Long): Long? {
        val minimum = baseBytes(info, fitWithin(info.size, Size(MIN_DECODE_SIDE, MIN_DECODE_SIDE)))
        if (bytes <= minimum) return null
        return max(minimum, bytes / 4)
    }

    /**
     * The plan for [info] on a [target] with [transform] within [quotaBytes] (06 §6.2):
     * - the whole image is decoded fitted to the target ([baseDecodeSize]: ImageDecoder target size, never the full
     *   original size);
     * - when that exceeds the quota the decode size is halved until it fits (degraded: [ImageRenderPlan.baseSampleSize]
     *   grows and the session reports it);
     * - a zoomed, region decodable static image additionally gets tiles of the visible region at the sampling the
     *   zoom needs (never finer than the target resolution), as many as the rest of the quota allows (coarser
     *   sampling first, then none).
     */
    public fun plan(info: ImageInfo, target: Size, transform: MediaTransform, quotaBytes: Long): ImageRenderPlan {
        var decode = baseDecodeSize(info, target)
        while (baseBytes(info, decode) > quotaBytes && max(decode.width, decode.height) > MIN_DECODE_SIDE) {
            decode = Size(max(1, decode.width / 2), max(1, decode.height / 2))
        }
        val baseSample = ceilPowerOfTwo(longSide(info.size).toDouble() / longSide(decode))
        val base = ImageRenderPlan(decode, baseSample)
        if (!tiles(info) || transform.scale <= 1f || baseSample <= 1) return base
        val allowance = quotaBytes - baseBytes(info, decode)
        val finest = ceilPowerOfTwo(longSide(info.size).toDouble() / longSide(fitWithin(info.size, target)))
        var sample = max(finest, floorPowerOfTwo(longSide(info.size).toDouble() / (longSide(decode) * transform.scale)))
        while (sample < baseSample) {
            val tiles = tilesFor(info.size, visibleRegion(info.size, transform), sample)
            if (tiles.sumOf { tileBytes(it) } <= allowance) return base.copy(tiles = tiles)
            sample *= 2
        }
        return base
    }

    /** The visible region of the oriented image of [size] under [transform], in pixels, clamped to the image. */
    public fun visibleRegion(size: Size, transform: MediaTransform): PixelRect {
        val scale = max(1f, transform.scale)
        // Pan offsets are in screen axes; undo the clockwise rotation of the UI to get image axes.
        val (dx, dy) = when (((transform.rotationDeg % 360) + 360) % 360) {
            90 -> transform.panY to -transform.panX
            180 -> -transform.panX to -transform.panY
            270 -> -transform.panY to transform.panX
            else -> transform.panX to transform.panY
        }
        val extent = 1f / scale
        val centerX = (0.5f - dx / scale).coerceIn(extent / 2, 1f - extent / 2)
        val centerY = (0.5f - dy / scale).coerceIn(extent / 2, 1f - extent / 2)
        fun edge(value: Float, total: Int) = (value * total).roundToInt().coerceIn(0, total)
        return PixelRect(
            left = edge(centerX - extent / 2, size.width),
            top = edge(centerY - extent / 2, size.height),
            right = edge(centerX + extent / 2, size.width),
            bottom = edge(centerY + extent / 2, size.height),
        )
    }

    /** Grid aligned tiles at [sampleSize] covering [region] of an image of [size]. */
    public fun tilesFor(size: Size, region: PixelRect, sampleSize: Int): List<ImageTile> {
        val step = TILE_SIDE * sampleSize
        if (region.width <= 0 || region.height <= 0) return emptyList()
        val result = mutableListOf<ImageTile>()
        var top = (region.top / step) * step
        while (top < region.bottom) {
            var left = (region.left / step) * step
            while (left < region.right) {
                result += ImageTile(PixelRect(left, top, min(left + step, size.width), min(top + step, size.height)), sampleSize)
                left += step
            }
            top += step
        }
        return result
    }

    /** Decoded bytes of [tile]. */
    public fun tileBytes(tile: ImageTile): Long {
        val width = (tile.region.width + tile.sampleSize - 1) / tile.sampleSize
        val height = (tile.region.height + tile.sampleSize - 1) / tile.sampleSize
        return width.toLong() * height * BYTES_PER_PIXEL
    }

    /** Media kind of an opened image; an `IMAGE_UNKNOWN` source becomes static or animated from its header. */
    public fun kindOf(requested: MediaKind, info: ImageInfo): MediaKind = when (requested) {
        MediaKind.IMAGE_UNKNOWN -> if (info.animated) MediaKind.IMAGE_ANIMATED else MediaKind.IMAGE_STATIC
        else -> requested
    }

    /** Image facts of the details panel (04A L2). */
    public fun detailsOf(info: ImageInfo, state: ImageEngineState): ImageDetails = ImageDetails(
        frameCount = info.frameCount ?: if (info.animated) null else 1,
        decodedBytes = state.decodedBytes.takeIf { state.plan != null },
        sampleSize = state.plan?.let { plan -> plan.tiles.minOfOrNull { it.sampleSize } ?: plan.baseSampleSize },
    )

    /** Media parameters of an image (04A P2); the session adds the host's file size. */
    public fun mediaInfoOf(info: ImageInfo): MediaInfo = MediaInfo(
        container = info.format,
        width = info.size.width,
        height = info.size.height,
        rotationDeg = info.orientationDeg,
        durationUs = info.loopDurationUs,
    )

    private fun tiles(info: ImageInfo): Boolean = info.regionDecodable && !info.animated

    private fun longSide(size: Size): Int = max(1, max(size.width, size.height))

    private const val MAX_SAMPLE = 1 shl 16
}
