package com.videokit.spike.s6

import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

/** Axis-aligned box in pixels (top-left x, y). */
data class Box(val x: Double, val y: Double, val w: Double, val h: Double) {
    val cx: Double get() = x + w / 2
    val cy: Double get() = y + h / 2

    fun iou(other: Box): Double {
        val ix = max(0.0, min(x + w, other.x + other.w) - max(x, other.x))
        val iy = max(0.0, min(y + h, other.y + other.h) - max(y, other.y))
        val inter = ix * iy
        val union = w * h + other.w * other.h - inter
        return if (union <= 0) 0.0 else inter / union
    }

    /** Torso region below a face box (09 / S6 brief: clothing colour as an auxiliary feature). */
    fun torsoBelow(): Box = Box(x - w * 0.25, y + h * 1.1, w * 1.5, h * 2.0)

    companion object {
        fun centered(cx: Double, cy: Double, w: Double, h: Double) = Box(cx - w / 2, cy - h / 2, w, h)
    }
}

/**
 * One detection of a person in a frame: the face box when a face detector (YuNet) sees one, else a body/tracker box;
 * the face embedding (SFace, 128-d) only when the face is visible; the torso HSV histogram (normalized) when the torso
 * is in frame. [truthId] is ground truth for metrics only; the association never reads it.
 */
data class Detection(
    val box: Box,
    val face: FloatArray?,
    val torso: FloatArray?,
    val truthId: Int,
)

/** Per-frame state of the selected target, the 09 §1 states (TRACKED, LOW_CONFIDENCE, AMBIGUOUS, LOST). */
enum class TargetState { TRACKED, LOW_CONFIDENCE, AMBIGUOUS, LOST }

/** Association output of one frame. */
data class FrameDecision(val state: TargetState, val chosen: Detection?)

internal fun cosine(a: FloatArray, b: FloatArray): Double {
    var dot = 0.0
    var na = 0.0
    var nb = 0.0
    for (i in a.indices) {
        dot += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    }
    return if (na == 0.0 || nb == 0.0) 0.0 else dot / (sqrt(na) * sqrt(nb))
}

/** Bhattacharyya coefficient of two normalized histograms (1 = identical). */
internal fun bhattacharyya(a: FloatArray, b: FloatArray): Double {
    var sum = 0.0
    for (i in a.indices) sum += sqrt((a[i] * b[i]).toDouble().coerceAtLeast(0.0))
    return sum
}
