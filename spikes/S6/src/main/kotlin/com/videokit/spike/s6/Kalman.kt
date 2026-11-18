package com.videokit.spike.s6

import kotlin.math.sqrt

/**
 * Constant-velocity Kalman filter of the box centre, one independent (position, velocity) filter per axis, plus a
 * smoothed size. Predicts where the target should be while it is occluded or undetected; the innovation gives a
 * normalized distance used for gating.
 */
class Kalman(initial: Box, private val processNoise: Double = 4.0, private val measurementNoise: Double = 25.0) {
    private class Axis(var p: Double, var v: Double) {
        // Covariance [[a, b], [b, c]].
        var a = 100.0
        var b = 0.0
        var c = 100.0
    }

    private val ax = Axis(initial.cx, 0.0)
    private val ay = Axis(initial.cy, 0.0)
    private var w = initial.w
    private var h = initial.h

    /** Frames since the last update (prediction only). */
    var coasting = 0
        private set

    fun predict(): Box {
        listOf(ax, ay).forEach { axis ->
            axis.p += axis.v
            val a = axis.a + 2 * axis.b + axis.c + processNoise
            val b = axis.b + axis.c + processNoise
            val c = axis.c + processNoise
            axis.a = a
            axis.b = b
            axis.c = c
        }
        coasting++
        return predicted()
    }

    fun predicted(): Box = Box.centered(ax.p, ay.p, w, h)

    /** Normalized distance (in standard deviations) of [box] from the prediction; scaled by the box size. */
    fun distance(box: Box): Double {
        val sx = sqrt(ax.a + measurementNoise)
        val sy = sqrt(ay.a + measurementNoise)
        val dx = (box.cx - ax.p) / sx
        val dy = (box.cy - ay.p) / sy
        return sqrt(dx * dx + dy * dy)
    }

    fun update(box: Box) {
        update(ax, box.cx)
        update(ay, box.cy)
        w = 0.7 * w + 0.3 * box.w
        h = 0.7 * h + 0.3 * box.h
        coasting = 0
    }

    private fun update(axis: Axis, z: Double) {
        val s = axis.a + measurementNoise
        val kp = axis.a / s
        val kv = axis.b / s
        val y = z - axis.p
        axis.p += kp * y
        axis.v += kv * y
        val a = (1 - kp) * axis.a
        val b = (1 - kp) * axis.b
        val c = axis.c - kv * axis.b
        axis.a = a
        axis.b = b
        axis.c = c
    }
}
