package com.videokit.spike.s7

import kotlin.math.abs
import kotlin.math.sqrt

/**
 * Alpha matte quality against ground truth (S7 brief: edge, hair, background residue). Mattes are 0..1 per pixel,
 * row-major, same size. Regions come from the ground truth:
 * - **edge band**: pixels whose ground truth is partial (0 < a < 1) or within [band] pixels of the 0.5 contour;
 * - **hair**: an optional hair mask (synthetic set: the generated strands);
 * - **background**: ground truth a = 0, outside the edge band.
 */
data class MatteScores(
    /** Sum of absolute differences / 1000 (the usual matting SAD unit). */
    val sad: Double,
    /** Mean squared error over the image. */
    val mse: Double,
    /** Mean absolute error in the edge band. */
    val edgeMae: Double,
    /** Mean absolute error on hair pixels; null without a hair mask. */
    val hairMae: Double?,
    /** Background residue: mean predicted alpha on true background (visible leftovers). */
    val backgroundResidue: Double,
    /** Share of true background pixels with predicted alpha > 0.1 (speckles, halos). */
    val backgroundLeak: Double,
    /** Foreground loss: share of true solid foreground (a = 1) with predicted alpha < 0.9 (holes). */
    val foregroundLoss: Double,
)

object MattingMetrics {
    fun score(predicted: FloatArray, truth: FloatArray, width: Int, height: Int, hair: BooleanArray? = null, band: Int = 3): MatteScores {
        require(predicted.size == truth.size && truth.size == width * height)
        val edge = edgeBand(truth, width, height, band)
        var sad = 0.0
        var se = 0.0
        var edgeErr = 0.0
        var edgeN = 0
        var hairErr = 0.0
        var hairN = 0
        var bgSum = 0.0
        var bgLeak = 0
        var bgN = 0
        var fgLoss = 0
        var fgN = 0
        for (i in truth.indices) {
            val d = abs(predicted[i] - truth[i]).toDouble()
            sad += d
            se += d * d
            if (edge[i]) {
                edgeErr += d
                edgeN++
            }
            if (hair != null && hair[i]) {
                hairErr += d
                hairN++
            }
            if (truth[i] == 0f && !edge[i]) {
                bgSum += predicted[i]
                bgN++
                if (predicted[i] > 0.1f) bgLeak++
            }
            if (truth[i] == 1f && !edge[i]) {
                fgN++
                if (predicted[i] < 0.9f) fgLoss++
            }
        }
        return MatteScores(
            sad = sad / 1000.0,
            mse = se / truth.size,
            edgeMae = if (edgeN == 0) 0.0 else edgeErr / edgeN,
            hairMae = if (hair == null || hairN == 0) null else hairErr / hairN,
            backgroundResidue = if (bgN == 0) 0.0 else bgSum / bgN,
            backgroundLeak = if (bgN == 0) 0.0 else bgLeak.toDouble() / bgN,
            foregroundLoss = if (fgN == 0) 0.0 else fgLoss.toDouble() / fgN,
        )
    }

    /** Partial-alpha pixels plus a band of [band] pixels around the 0.5 contour of [truth]. */
    fun edgeBand(truth: FloatArray, width: Int, height: Int, band: Int): BooleanArray {
        val contour = BooleanArray(truth.size)
        for (y in 0 until height) {
            for (x in 0 until width) {
                val i = y * width + x
                val a = truth[i]
                if (a > 0f && a < 1f) contour[i] = true
                val inside = a >= 0.5f
                if (x + 1 < width && (truth[i + 1] >= 0.5f) != inside) contour[i] = true
                if (y + 1 < height && (truth[i + width] >= 0.5f) != inside) contour[i] = true
            }
        }
        val out = BooleanArray(truth.size)
        for (y in 0 until height) {
            for (x in 0 until width) {
                if (!contour[y * width + x]) continue
                for (dy in -band..band) {
                    for (dx in -band..band) {
                        val nx = x + dx
                        val ny = y + dy
                        if (nx in 0 until width && ny in 0 until height && sqrt((dx * dx + dy * dy).toDouble()) <= band) out[ny * width + nx] = true
                    }
                }
            }
        }
        return out
    }
}
