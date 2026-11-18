package com.videokit.spike.s7

import java.awt.image.BufferedImage
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/** Integer rectangle in image pixels. */
data class Rect(val x: Int, val y: Int, val w: Int, val h: Int) {
    val right: Int get() = x + w
    val bottom: Int get() = y + h

    fun clampTo(width: Int, height: Int): Rect {
        val l = x.coerceIn(0, width)
        val t = y.coerceIn(0, height)
        val r = right.coerceIn(0, width)
        val b = bottom.coerceIn(0, height)
        return Rect(l, t, max(0, r - l), max(0, b - t))
    }

    fun iou(o: Rect): Double {
        val iw = max(0, min(right, o.right) - max(x, o.x))
        val ih = max(0, min(bottom, o.bottom) - max(y, o.y))
        val inter = iw.toLong() * ih
        val union = w.toLong() * h + o.w.toLong() * o.h - inter
        return if (union <= 0) 0.0 else inter.toDouble() / union
    }
}

/**
 * Head range from a detected face (S7 step 2, REQ-ED-07): the face box (YuNet covers forehead to chin) widened and
 * extended upwards to include the hair, and a little downwards for the chin and neck line. The factors are the
 * candidates S7 tunes against the test set (§ criteria in reports/S7).
 */
data class HeadExpansion(val widen: Double = 1.9, val up: Double = 0.75, val down: Double = 0.25) {
    fun headOf(face: Rect, imageWidth: Int, imageHeight: Int): Rect {
        val w = face.w * widen
        val cx = face.x + face.w / 2.0
        val top = face.y - face.h * up
        val bottom = face.bottom + face.h * down
        return Rect((cx - w / 2).roundToInt(), top.roundToInt(), w.roundToInt(), (bottom - top).roundToInt()).clampTo(imageWidth, imageHeight)
    }
}

/**
 * Host-supplied avatar PNG (04A E6: the App may bring its own transparent PNG instead of the Kit cutout): the head
 * range is the bounding box of the pixels with alpha above [threshold] (default: anything not fully transparent after
 * ignoring faint fringe). Returns null for a fully transparent or opaque-everywhere image (no usable head range).
 */
object HostPng {
    const val DEFAULT_ALPHA_THRESHOLD = 8

    fun opaqueBounds(image: BufferedImage, threshold: Int = DEFAULT_ALPHA_THRESHOLD): Rect? {
        if (!image.colorModel.hasAlpha()) return null
        var l = image.width
        var t = image.height
        var r = -1
        var b = -1
        var transparent = 0L
        for (y in 0 until image.height) {
            for (x in 0 until image.width) {
                val alpha = image.getRGB(x, y) ushr 24
                if (alpha > threshold) {
                    if (x < l) l = x
                    if (x > r) r = x
                    if (y < t) t = y
                    if (y > b) b = y
                } else {
                    transparent++
                }
            }
        }
        if (r < 0 || transparent == 0L) return null
        return Rect(l, t, r - l + 1, b - t + 1)
    }

    /**
     * Width (pixels, median over rows crossing the subject) of the partially transparent edge: the soft edge the
     * composite needs; 0 means a hard cut.
     */
    fun edgeWidth(image: BufferedImage, low: Int = 8, high: Int = 247): Double {
        val widths = ArrayList<Int>()
        for (y in 0 until image.height) {
            var soft = 0
            var crossed = false
            for (x in 0 until image.width) {
                val a = image.getRGB(x, y) ushr 24
                if (a in (low + 1) until high) soft++
                if (a >= high) crossed = true
            }
            if (crossed) widths += soft / 2
        }
        if (widths.isEmpty()) return 0.0
        widths.sort()
        return widths[widths.size / 2].toDouble()
    }
}
