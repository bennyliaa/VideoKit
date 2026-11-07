package com.videokit.core.runtime

import com.videokit.api.SessionVisibility

/**
 * Visibility policy of a session (07 §3 / §5.3, 15 §2.7 "不可见槽暂停并释放解码器", 04A V1), shared by the real
 * session and the Kotlin Fake so that both follow the same contract (`spec/vectors/multi-instance/visibility.json`):
 *
 * - VISIBLE plays normally; PARTIALLY_VISIBLE keeps playing and may lower frame rate or resolution
 *   ([mayReduceQuality]; engines with a single local track have nothing to lower);
 * - leaving the visible states (OFFSCREEN, BACKGROUND) pauses a playing session and remembers to resume it;
 * - after [releaseDelayMs] still hidden, the session releases its decoder (engine and resource lease) but stays
 *   bound: phase, position, tracks, speed, looping and transform are kept and `resourcesHeld` becomes false. No
 *   SourceReleased is reported: the media is still bound and the host's lease stays valid (05 §4);
 * - returning to a visible state reserves and reopens the decoder at the kept state (a denied reservation leaves the
 *   session released with a recoverable `DECODER_RESOURCE_EXHAUSTED` error event and the RESOURCE_DEGRADED notice;
 *   nothing retries on its own, 07 §1), then resumes playback if the policy paused it. A Play command while released
 *   reopens the same way.
 * - Content lock (`HideContentForLock`, 06 §4.2) is not a visibility: it wins over every visibility (the picture
 *   stays hidden and silent whatever the visibility is).
 */
public object VisibilityPolicy {
    /** Default delay before an off-screen slot releases its decoder. */
    public const val DEFAULT_OFFSCREEN_RELEASE_MS: Long = 10_000L

    /** Default delay before a session of a background host releases its decoder. */
    public const val DEFAULT_BACKGROUND_RELEASE_MS: Long = 5_000L

    /** Whether a session with [visibility] is paused by the policy. */
    public fun pauses(visibility: SessionVisibility): Boolean = when (visibility) {
        SessionVisibility.VISIBLE, SessionVisibility.PARTIALLY_VISIBLE -> false
        SessionVisibility.OFFSCREEN, SessionVisibility.BACKGROUND -> true
    }

    /** Whether the engine may lower frame rate or resolution for [visibility] (07 §3). */
    public fun mayReduceQuality(visibility: SessionVisibility): Boolean = visibility == SessionVisibility.PARTIALLY_VISIBLE

    /** Delay before a session with [visibility] releases its decoder, or `null` when it keeps it. */
    public fun releaseDelayMs(visibility: SessionVisibility, offscreenMs: Long, backgroundMs: Long): Long? = when (visibility) {
        SessionVisibility.VISIBLE, SessionVisibility.PARTIALLY_VISIBLE -> null
        SessionVisibility.OFFSCREEN -> offscreenMs.coerceAtLeast(0L)
        SessionVisibility.BACKGROUND -> backgroundMs.coerceAtLeast(0L)
    }
}
