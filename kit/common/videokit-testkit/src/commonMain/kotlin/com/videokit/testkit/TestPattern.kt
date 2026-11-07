package com.videokit.testkit

/** One colored block of a test pattern; coordinates normalized 0..1. */
public data class PatternBlock(
    /** Left edge. */
    val left: Float,
    /** Top edge. */
    val top: Float,
    /** Right edge. */
    val right: Float,
    /** Bottom edge. */
    val bottom: Float,
    /** ARGB color. */
    val argb: Int,
)

/**
 * A frame of the Fake test pattern (14 §8.4): color blocks + time code + last 4 characters of the
 * session id + demo label. Pure data, so the drawing logic can be tested on the JVM.
 */
public data class TestPatternFrame(
    /** Target width in pixels. */
    val width: Int,
    /** Target height in pixels. */
    val height: Int,
    /** Background ARGB color, derived from the session id. */
    val backgroundArgb: Int,
    /** Blocks in drawing order: fixed color bars, then the moving block. */
    val blocks: List<PatternBlock>,
    /** Time code `HH:MM:SS.mmm`. */
    val timecode: String,
    /** Last 4 characters of the session id. */
    val sessionTag: String,
    /** Demo label; never omitted (demo data must not pass as real media). */
    val label: String = TestPattern.DEMO_LABEL,
)

/** Builds [TestPatternFrame]s. */
public object TestPattern {
    /** Label drawn on every frame. */
    public const val DEMO_LABEL: String = "DEMO"

    /** Period of the moving block. */
    public const val MOTION_PERIOD_US: Long = 4_000_000L

    /** Fixed bar colors (opaque white, yellow, cyan, green, magenta, red, blue, black). */
    public val BAR_COLORS: List<Int> = listOf(
        0xFFFFFFFF.toInt(),
        0xFFFFFF00.toInt(),
        0xFF00FFFF.toInt(),
        0xFF00FF00.toInt(),
        0xFFFF00FF.toInt(),
        0xFFFF0000.toInt(),
        0xFF0000FF.toInt(),
        0xFF000000.toInt(),
    )

    private const val BAR_TOP = 0.1f
    private const val BAR_BOTTOM = 0.35f
    private const val MOVER_SIZE = 0.2f
    private const val MOVER_TOP = 0.45f

    /** The frame for [sessionId] at [positionUs] on a [width]×[height] target. */
    public fun frame(sessionId: String, positionUs: Long, width: Int, height: Int): TestPatternFrame {
        val bars = BAR_COLORS.mapIndexed { index, color ->
            val left = index / BAR_COLORS.size.toFloat()
            PatternBlock(left, BAR_TOP, left + 1f / BAR_COLORS.size, BAR_BOTTOM, color)
        }
        val phase = (positionUs.coerceAtLeast(0L) % MOTION_PERIOD_US) / MOTION_PERIOD_US.toFloat()
        val moverLeft = phase * (1f - MOVER_SIZE)
        val mover = PatternBlock(moverLeft, MOVER_TOP, moverLeft + MOVER_SIZE, MOVER_TOP + MOVER_SIZE, 0xFFFFFFFF.toInt())
        return TestPatternFrame(
            width = width,
            height = height,
            backgroundArgb = backgroundFor(sessionId),
            blocks = bars + mover,
            timecode = formatTimecode(positionUs),
            sessionTag = sessionTag(sessionId),
        )
    }

    /** `HH:MM:SS.mmm`; negative positions are clamped to zero. */
    public fun formatTimecode(positionUs: Long): String {
        val totalMs = positionUs.coerceAtLeast(0L) / 1_000L
        val ms = totalMs % 1_000L
        val totalSeconds = totalMs / 1_000L
        val seconds = totalSeconds % 60L
        val minutes = (totalSeconds / 60L) % 60L
        val hours = totalSeconds / 3_600L
        return "${pad(hours, 2)}:${pad(minutes, 2)}:${pad(seconds, 2)}.${pad(ms, 3)}"
    }

    /** Last 4 characters of [sessionId], left padded with `_` when shorter. */
    public fun sessionTag(sessionId: String): String = sessionId.takeLast(4).padStart(4, '_')

    /** Opaque dark background color derived from [sessionId], so slots are distinguishable. */
    public fun backgroundFor(sessionId: String): Int {
        val hash = sessionId.hashCode()
        val r = 0x20 + (hash and 0x3F)
        val g = 0x20 + ((hash shr 6) and 0x3F)
        val b = 0x20 + ((hash shr 12) and 0x3F)
        return (0xFF shl 24) or (r shl 16) or (g shl 8) or b
    }

    private fun pad(value: Long, width: Int): String = value.toString().padStart(width, '0')
}

/** A render target of the Fake test pattern. */
public interface TestPatternTarget {
    /** Draws [frame]; returns `false` when the target cannot draw (for example the surface is gone). */
    public fun draw(frame: TestPatternFrame): Boolean

    /** Stops using the target. The underlying surface belongs to its owner and is not released. */
    public fun release()
}
