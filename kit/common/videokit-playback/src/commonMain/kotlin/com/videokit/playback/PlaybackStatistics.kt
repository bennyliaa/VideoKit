package com.videokit.playback

/**
 * Playback events and watch-time statistics (06 §4.1): position ticks are sampled every [tickUs] of played media;
 * watch time accumulates only while playing, visible and not buffering, excluding user seeks, and is reported in
 * chunks of [reportUs]. VideoKit never counts plays itself; the host decides (06 §4.1).
 */
public class PlaybackStatistics(private val tickUs: Long = DEFAULT_TICK_US, private val reportUs: Long = DEFAULT_REPORT_US) {
    private var tickAccumUs = 0L
    private var watchAccumUs = 0L

    /** Result of one [onPlayed] step. */
    public data class Step(
        /** Position to report as a PositionTick, when a tick is due. */
        val tickAtUs: Long?,
        /** Watch time to report, when a chunk is complete. */
        val watchTimeUs: Long?,
    )

    /**
     * Media advanced by [advancedUs] to [positionUs] during normal playback. [visible] is whether the session
     * counts as watched (VISIBLE).
     */
    public fun onPlayed(positionUs: Long, advancedUs: Long, visible: Boolean): Step {
        if (advancedUs <= 0) return Step(null, null)
        tickAccumUs += advancedUs
        val tick = if (tickAccumUs >= tickUs) {
            tickAccumUs = 0L
            positionUs
        } else {
            null
        }
        if (!visible) return Step(tick, null)
        watchAccumUs += advancedUs
        val watch = if (watchAccumUs >= reportUs) {
            val delta = watchAccumUs
            watchAccumUs = 0L
            delta
        } else {
            null
        }
        return Step(tick, watch)
    }

    /** A new source is bound: counters restart. */
    public fun reset() {
        tickAccumUs = 0L
        watchAccumUs = 0L
    }

    public companion object {
        /** Position tick interval (14 §12: 4 Hz). */
        public const val DEFAULT_TICK_US: Long = 250_000L

        /** Watch time report chunk. */
        public const val DEFAULT_REPORT_US: Long = 1_000_000L
    }
}
