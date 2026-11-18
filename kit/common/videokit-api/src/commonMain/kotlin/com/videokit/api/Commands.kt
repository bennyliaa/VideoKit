package com.videokit.api

/** Seek precision (04 §4.3). */
public enum class SeekMode {
    /** Cheap preview while the user drags; may land on a nearby frame. */
    PREVIEW,

    /** Closest sync (key) frame. */
    CLOSEST_SYNC,

    /** Exact position. */
    EXACT,
}

/** Session command (04 §4.1, original requirement §15.5). Every command returns a [VideoKitCommandResult]. */
public sealed interface VideoKitCommand {
    /** Start or resume playback (video) or animation (animated image). */
    public data object Play : VideoKitCommand

    /** Pause playback or animation. */
    public data object Pause : VideoKitCommand

    /** Seek to [positionUs]. Rapid seeks only execute the latest target; earlier ones return [VideoKitCommandResult.Superseded]. */
    public data class SeekTo(
        /** Target position in microseconds. */
        val positionUs: Long,
        /** Precision. */
        val mode: SeekMode = SeekMode.CLOSEST_SYNC,
    ) : VideoKitCommand

    /** Set the playback speed. */
    public data class SetSpeed(
        /** Speed factor, for example 0.5, 1, 2. */
        val speed: Float,
    ) : VideoKitCommand

    /**
     * Loop or stop at the end (04A L1). Default per media kind: animated images loop, videos do not. Without
     * looping playback stops on the last frame, enters ENDED and emits PlaybackEnded; with looping it never ends.
     * Static images answer `Unsupported(MEDIA_KIND)`.
     */
    public data class SetLooping(
        /** Whether to loop. */
        val looping: Boolean,
    ) : VideoKitCommand

    /** Mute or unmute the session. */
    public data class SetMuted(
        /** Whether to mute. */
        val muted: Boolean,
    ) : VideoKitCommand

    /** Set the session volume. */
    public data class SetVolume(
        /** Volume 0..1. */
        val volume: Float,
    ) : VideoKitCommand

    /** Select an audio track. */
    public data class SelectAudioTrack(
        /** Track id from [VideoKitSessionState.audioTracks], or `null` for the default. */
        val trackId: String?,
    ) : VideoKitCommand

    /** Select a subtitle track. */
    public data class SelectSubtitleTrack(
        /** Track id from [VideoKitSessionState.subtitleTracks]; `null` turns subtitles off. */
        val trackId: String?,
    ) : VideoKitCommand

    /** Store the view transform computed by the UI. */
    public data class SetTransform(
        /** New transform. */
        val transform: MediaTransform,
    ) : VideoKitCommand

    /** Request a screen orientation; the host executes it. */
    public data class SetOrientation(
        /** Requested orientation. */
        val request: OrientationRequest,
    ) : VideoKitCommand

    /** Record the fullscreen state. */
    public data class SetFullscreen(
        /** Whether fullscreen. */
        val fullscreen: Boolean,
    ) : VideoKitCommand

    /** Report visibility (07 §3). */
    public data class SetVisibility(
        /** New visibility. */
        val visibility: SessionVisibility,
    ) : VideoKitCommand

    /**
     * Make this session the single audible one, or silence it (07 §4). Commands with an [audioEpoch]
     * lower than the highest accepted one are rejected so that late commands cannot win.
     */
    public data class SetActiveAudio(
        /** Whether this session may play audio. */
        val active: Boolean,
        /** Monotonic epoch maintained by the host. */
        val audioEpoch: Long,
    ) : VideoKitCommand

    /** Hide (or show) the content because the host is locked (06 §4.2). Lock wins over audio commands. */
    public data class HideContentForLock(
        /** Whether to hide. */
        val hidden: Boolean,
    ) : VideoKitCommand

    /** Release the session; equivalent to [VideoKitSession.release] without the snapshot. */
    public data object Release : VideoKitCommand
}

/** Why a command or feature is unsupported. Unknown wire values map to [UNKNOWN]. */
public enum class UnsupportedReason {
    /** Not implemented in this VideoKit build or backend. */
    NOT_IMPLEMENTED,

    /** The device lacks the capability (decoder, encoder, display). */
    DEVICE_CAPABILITY,

    /** The media format does not support it. */
    FORMAT,

    /** Not applicable to the bound media kind (for example speed on an image). */
    MEDIA_KIND,

    /** The source is sequential only. */
    SOURCE_SEQUENTIAL_ONLY,

    /** Disabled by the host configuration. */
    HOST_DISABLED,

    /** The optional module (tracking, export) is not installed. */
    MODULE_NOT_INSTALLED,

    /** A requested value is outside the supported range (04A V1). */
    VALUE_OUT_OF_RANGE,

    /** The requested track does not exist (04A V1). */
    TRACK_NOT_FOUND,

    /** The content is hidden because the host is locked (04A V1). */
    CONTENT_LOCKED,

    /** The feature is hidden by the host configuration ([FeatureMode.HIDDEN], REQ-API-10 ①). */
    FEATURE_DISABLED,

    /** The host's feature gate did not allow the feature ([FeatureAccess.Denied], REQ-API-10 ②). */
    FEATURE_DENIED,

    /** Unknown reason (also used for unknown wire values). */
    UNKNOWN,
    ;

    public companion object {
        /** Maps a name to a reason; unknown names map to [UNKNOWN]. */
        public fun fromWireName(name: String?): UnsupportedReason = entries.firstOrNull { it.name == name } ?: UNKNOWN
    }
}

/** Stable result of a session command (04 §4.2). */
public sealed interface VideoKitCommandResult {
    /** The command was executed. */
    public data object Executed : VideoKitCommandResult

    /** The command was rejected, for example an illegal state transition or invalid argument. */
    public data class Rejected(
        /** Reason. */
        val error: VideoKitStableError,
    ) : VideoKitCommandResult

    /** A later command of the same kind replaced this one (for example rapid seeks). */
    public data object Superseded : VideoKitCommandResult

    /** The capability is not supported. */
    public data class Unsupported(
        /** Reason. */
        val reason: UnsupportedReason,
    ) : VideoKitCommandResult

    /** The session has been released. */
    public data object SessionReleased : VideoKitCommandResult
}

/**
 * One-off session events for the UI (14 §3.2). The UI only uses events for transient notices and
 * never rebuilds state from them; state is in [VideoKitSession.state].
 */
public sealed interface VideoKitEvent {
    /** Playback reached the end. */
    public data object PlaybackEnded : VideoKitEvent

    /** All read handles of [mediaToken] are closed (original requirement §14.4). */
    public data class SourceReleased(
        /** Released media token. */
        val mediaToken: String,
    ) : VideoKitEvent

    /** A host action request failed or timed out. */
    public data class HostActionFailed(
        /** Action id. */
        val actionId: String,
        /** Error, usually [ErrorCode.HOST_CALLBACK_FAILED]. */
        val error: VideoKitStableError,
    ) : VideoKitEvent

    /** A transient notice the UI may show briefly. */
    public data class TransientNotice(
        /** Notice code, for example `AUDIO_UNSUPPORTED_PLAYING_SILENT`. */
        val code: String,
    ) : VideoKitEvent

    /** An error was raised; the state carries the same error. */
    public data class ErrorRaised(
        /** The error. */
        val error: VideoKitStableError,
    ) : VideoKitEvent
}

/**
 * Playback events for host statistics (06 §4.1, original requirement §15.4). Delivered through
 * [VideoKitHostCallbacks.onPlaybackEvent]; high-frequency events are sampled.
 */
public sealed interface VideoKitPlaybackEvent {
    /** Session the event belongs to. */
    public val sessionId: String

    /** Sampled position update. */
    public data class PositionTick(
        override val sessionId: String,
        /** Position in microseconds. */
        val positionUs: Long,
    ) : VideoKitPlaybackEvent

    /** Phase or play-when-ready changed. */
    public data class PlayStateChanged(
        override val sessionId: String,
        /** New phase. */
        val phase: SessionPhase,
        /** Play-when-ready. */
        val playWhenReady: Boolean,
    ) : VideoKitPlaybackEvent

    /** Buffering started. */
    public data class BufferingStarted(
        override val sessionId: String,
        /** Position in microseconds. */
        val positionUs: Long,
    ) : VideoKitPlaybackEvent

    /** Buffering ended. */
    public data class BufferingEnded(
        override val sessionId: String,
        /** Buffering duration in microseconds (media clock). */
        val durationUs: Long,
    ) : VideoKitPlaybackEvent

    /** The user (or host) seeked. */
    public data class UserSeek(
        override val sessionId: String,
        /** Position before the seek. */
        val fromUs: Long,
        /** Position after the seek. */
        val toUs: Long,
    ) : VideoKitPlaybackEvent

    /** SessionVisibility changed. */
    public data class VisibilityChanged(
        override val sessionId: String,
        /** New visibility. */
        val visibility: SessionVisibility,
    ) : VideoKitPlaybackEvent

    /** Foreground state changed. */
    public data class ForegroundChanged(
        override val sessionId: String,
        /** Whether the host is in the foreground. */
        val foreground: Boolean,
    ) : VideoKitPlaybackEvent

    /** Watch time accumulated while playing, visible and not buffering; seeks are not counted. */
    public data class WatchTimeAccumulated(
        override val sessionId: String,
        /** Accumulated media time in microseconds since the previous event. */
        val deltaUs: Long,
    ) : VideoKitPlaybackEvent

    /** The session ended (released or source replaced). */
    public data class SessionEnded(
        override val sessionId: String,
        /** Media token that was bound, if any. */
        val mediaToken: String?,
    ) : VideoKitPlaybackEvent
}
