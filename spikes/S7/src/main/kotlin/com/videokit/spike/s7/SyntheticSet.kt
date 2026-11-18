package com.videokit.spike.s7

import java.awt.image.BufferedImage
import kotlin.math.cos
import kotlin.math.exp
import kotlin.math.hypot
import kotlin.math.sin
import kotlin.random.Random

/**
 * Synthetic test images with exact ground truth (S7: 24 images, 6 backgrounds × 4 hair styles; lighting varies with the
 * background). A drawn head (skin ellipse, hair mass, fine semi-transparent strands) composited over a background.
 * Exact alpha, hair mask and face box let the pipeline pieces and the metrics be checked; they do not replace real
 * photos for judging model quality (reports/S7: real photo set is a gap).
 */
object SyntheticSet {
    const val W = 256
    const val H = 320

    enum class Background { FLAT, GRADIENT, TEXTURE, BUSY_STRIPES, LOW_LIGHT, BACKLIT }

    enum class Hair { SHORT, LONG, CURLY, FLYAWAY }

    class Sample(
        val name: String,
        val image: BufferedImage,
        val alpha: FloatArray,
        val hair: BooleanArray,
        /** Face box as a face detector would report it (forehead to chin). */
        val face: Rect,
        /** Ground-truth head range: bounding box of alpha > 0.03. */
        val head: Rect,
    )

    fun all(seed: Int = 7): List<Sample> = Background.entries.flatMap { bg -> Hair.entries.map { hair -> sample(bg, hair, seed) } }

    fun sample(background: Background, hairStyle: Hair, seed: Int): Sample {
        val random = Random(seed * 31 + background.ordinal * 7 + hairStyle.ordinal)
        val cx = W / 2.0 + random.nextDouble(-12.0, 12.0)
        val cy = H * 0.48
        val rx = 46.0
        val ry = 60.0
        val alpha = FloatArray(W * H)
        val hairMask = BooleanArray(W * H)
        val fg = IntArray(W * H)
        val hairRgb = when (hairStyle) {
            Hair.SHORT -> rgb(40, 28, 20)
            Hair.LONG -> rgb(90, 60, 30)
            Hair.CURLY -> rgb(20, 20, 20)
            Hair.FLYAWAY -> rgb(200, 170, 110)
        }
        val skin = rgb(224, 182, 150)
        val strands = strands(hairStyle, cx, cy, rx, ry, random)
        for (y in 0 until H) {
            for (x in 0 until W) {
                val i = y * W + x
                val face = ((x - cx) / rx).let { it * it } + ((y - cy) / ry).let { it * it }
                // Hair mass: a larger ellipse above and around the face; LONG reaches the shoulders.
                val hairBottom = if (hairStyle == Hair.LONG) cy + ry * 1.6 else cy + ry * 0.2
                val hx = (x - cx) / (rx * (if (hairStyle == Hair.CURLY) 1.45 else 1.25))
                val hy = (y - (cy - ry * 0.25)) / (ry * 1.2)
                val inHairMass = hx * hx + hy * hy <= 1.0 && y <= hairBottom
                val neck = x in (cx - 16).toInt()..(cx + 16).toInt() && y > cy + ry * 0.8 && y < cy + ry * 1.35
                var a = 0f
                var color = 0
                if (inHairMass) {
                    a = 1f
                    color = hairRgb
                    hairMask[i] = true
                }
                if (face <= 1.0 || neck) {
                    a = 1f
                    color = skin
                    hairMask[i] = false
                }
                if (a < 1f) {
                    val s = strands.coverage(x, y)
                    if (s > 0f) {
                        a = s
                        color = hairRgb
                        hairMask[i] = true
                    }
                }
                // Anti-aliased outline of the solid parts.
                if (a == 1f && (face in 0.96..1.0) && !inHairMass) a = 0.6f
                alpha[i] = a
                fg[i] = color
            }
        }
        val image = BufferedImage(W, H, BufferedImage.TYPE_INT_RGB)
        for (y in 0 until H) {
            for (x in 0 until W) {
                val i = y * W + x
                image.setRGB(x, y, mix(fg[i], backgroundAt(background, x, y, random), alpha[i]))
            }
        }
        val face = Rect((cx - rx * 0.9).toInt(), (cy - ry * 0.75).toInt(), (rx * 1.8).toInt(), (ry * 1.75).toInt())
        return Sample("${background.name.lowercase()}_${hairStyle.name.lowercase()}", image, alpha, hairMask, face, bounds(alpha))
    }

    /** Fine strands: arcs of 1–2 px with partial alpha, sticking out of the hair mass. */
    private class Strands(val segments: List<DoubleArray>) {
        fun coverage(x: Int, y: Int): Float {
            var best = 0.0
            for (s in segments) {
                val d = distanceToSegment(x + 0.5, y + 0.5, s[0], s[1], s[2], s[3])
                val a = s[4] * exp(-d * d / 0.8)
                if (a > best) best = a
            }
            return if (best < 0.04) 0f else best.toFloat()
        }
    }

    private fun strands(style: Hair, cx: Double, cy: Double, rx: Double, ry: Double, random: Random): Strands {
        val count = when (style) {
            Hair.SHORT -> 15
            Hair.LONG -> 40
            Hair.CURLY -> 60
            Hair.FLYAWAY -> 90
        }
        val segments = ArrayList<DoubleArray>()
        repeat(count) {
            val angle = random.nextDouble(-Math.PI * 0.95, -Math.PI * 0.05)
            val r = 1.0
            val sx = cx + cos(angle) * rx * 1.25 * r
            val sy = cy - ry * 0.25 + sin(angle) * ry * 1.2 * r
            val length = when (style) {
                Hair.SHORT -> 4.0
                Hair.CURLY -> 10.0
                else -> 18.0
            } * random.nextDouble(0.5, 1.5)
            val dir = angle + random.nextDouble(-0.6, 0.6)
            segments += doubleArrayOf(sx, sy, sx + cos(dir) * length, sy + sin(dir) * length, random.nextDouble(0.35, 0.9))
        }
        return Strands(segments)
    }

    private fun distanceToSegment(px: Double, py: Double, ax: Double, ay: Double, bx: Double, by: Double): Double {
        val dx = bx - ax
        val dy = by - ay
        val t = (((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)).coerceIn(0.0, 1.0)
        return hypot(px - (ax + t * dx), py - (ay + t * dy))
    }

    private fun backgroundAt(kind: Background, x: Int, y: Int, random: Random): Int = when (kind) {
        Background.FLAT -> rgb(120, 170, 210)
        Background.GRADIENT -> rgb(60 + x * 150 / W, 100, 220 - y * 150 / H)
        Background.TEXTURE -> (100 + random.nextInt(60)).let { rgb(it, it - 10, it - 30) }
        Background.BUSY_STRIPES -> if ((x / 9 + y / 13) % 2 == 0) rgb(30, 30, 30) else rgb(230, 200, 60)
        Background.LOW_LIGHT -> (15 + random.nextInt(20)).let { rgb(it, it, it + 5) }
        Background.BACKLIT -> (235 + random.nextInt(20)).let { rgb(it, it, it) }
    }

    private fun bounds(alpha: FloatArray): Rect {
        var l = W
        var t = H
        var r = -1
        var b = -1
        for (y in 0 until H) {
            for (x in 0 until W) {
                if (alpha[y * W + x] > 0.03f) {
                    if (x < l) l = x
                    if (x > r) r = x
                    if (y < t) t = y
                    if (y > b) b = y
                }
            }
        }
        return Rect(l, t, r - l + 1, b - t + 1)
    }

    /** The ground truth as a host-supplied RGBA PNG would carry it (04A E6 path). */
    fun asRgba(sample: Sample): BufferedImage {
        val out = BufferedImage(W, H, BufferedImage.TYPE_INT_ARGB)
        for (y in 0 until H) {
            for (x in 0 until W) {
                val a = (sample.alpha[y * W + x] * 255).toInt().coerceIn(0, 255)
                out.setRGB(x, y, (a shl 24) or (sample.image.getRGB(x, y) and 0xFFFFFF))
            }
        }
        return out
    }

    fun rgb(r: Int, g: Int, b: Int): Int = (r.coerceIn(0, 255) shl 16) or (g.coerceIn(0, 255) shl 8) or b.coerceIn(0, 255)

    private fun mix(fg: Int, bg: Int, a: Float): Int {
        fun ch(c: Int, shift: Int) = (c shr shift) and 0xFF
        fun m(shift: Int) = (ch(fg, shift) * a + ch(bg, shift) * (1 - a)).toInt()
        return rgb(m(16), m(8), m(0))
    }
}
