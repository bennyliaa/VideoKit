package com.videokit.api

/**
 * Session phase (04 §3.1, original requirement §19.1).
 *
 * ```
 * CREATED → BINDING → READY ⇄ PLAYING ⇄ PAUSED
 *                      ↘ BUFFERING ↗      ↘ ENDED
 * any → ERROR_RECOVERABLE (retry back to BINDING/READY)
 * any → ERROR_FATAL
 * any → RELEASING → RELEASED (terminal)
 * ```
 *
 * Image sessions use [READY] while an image is displayed and [PLAYING]/[PAUSED] for animation state.
 * State machine enums have no "unknown" value: a protocol mismatch fails initialisation instead.
 */
public enum class SessionPhase {
    /** Created; nothing bound yet. */
    CREATED,

    /** A source is being bound and probed. */
    BINDING,

    /** Bound and ready; paused at the start or displaying an image. */
    READY,

    /** Playing (video) or animating (animated image). */
    PLAYING,

    /** Paused by command. */
    PAUSED,

    /** Waiting for data while play-when-ready is set. */
    BUFFERING,

    /** Playback reached the end. */
    ENDED,

    /** A recoverable error; [VideoKitSessionState.error] says what happened. Re-binding may recover. */
    ERROR_RECOVERABLE,

    /** A fatal error; only release is possible. */
    ERROR_FATAL,

    /** Release in progress. */
    RELEASING,

    /** Released; terminal. */
    RELEASED,
    ;

    /** Whether the phase is [RELEASING] or [RELEASED]. */
    public val isReleasedOrReleasing: Boolean get() = this == RELEASING || this == RELEASED
}

/** An immutable size in pixels. */
public data class Size(
    /** Width in pixels. */
    val width: Int,
    /** Height in pixels. */
    val height: Int,
)

/** An audio or subtitle track (06 §4). */
public data class TrackInfo(
    /** Opaque track id, stable for the bound source. */
    val id: String,
    /** BCP 47 language tag, if known. */
    val language: String? = null,
    /** Display label, if any. */
    val label: String? = null,
    /** Codec / format name, if known (for example `audio/ac3`, `text/x-ssa`). */
    val codec: String? = null,
    /** Whether the device can decode/render this track. */
    val supported: Boolean = true,
    /** Audio channels (1 mono, 2 stereo, 6 for 5.1, ...); audio tracks only, `null` when unknown (04A C1). */
    val channelCount: Int? = null,
)

/** How content is fitted into the render target. */
public enum class FitMode {
    /** Fit inside the target, keeping aspect ratio (letterbox). */
    FIT,

    /** Fill the target, keeping aspect ratio (crop). */
    FILL,

    /** Original pixel size (1:1), centered; may crop or letterbox (04A N11). */
    ORIGINAL,
}

/**
 * User view transform: zoom, pan, rotation and fit (06 §4). Computed by the UI from gestures and
 * submitted with [VideoKitCommand.SetTransform]; the session keeps it and returns it in snapshots.
 */
public data class MediaTransform(
    /** Zoom factor; 1 = no zoom. */
    val scale: Float = 1f,
    /** Horizontal pan, normalized to the content width (0 = centered). */
    val panX: Float = 0f,
    /** Vertical pan, normalized to the content height (0 = centered). */
    val panY: Float = 0f,
    /** Clockwise rotation in degrees: 0, 90, 180 or 270. */
    val rotationDeg: Int = 0,
    /** Fit mode. */
    val fitMode: FitMode = FitMode.FIT,
)

/** Requested screen orientation (06 §4). The host activity performs the actual rotation. */
public enum class OrientationRequest {
    /** Follow the content (landscape for landscape video). */
    AUTO,

    /** Portrait. */
    PORTRAIT,

    /** Landscape. */
    LANDSCAPE,

    /** Keep the current orientation. */
    LOCKED,
}

/** Orientation of the content after applying rotation metadata. */
public enum class MediaOrientation {
    /** Taller than wide. */
    PORTRAIT,

    /** Wider than tall. */
    LANDSCAPE,

    /** Square. */
    SQUARE,

    /** Unknown (metadata missing or nothing bound). */
    UNKNOWN,
}

/** Orientation and fullscreen state of a session. */
public data class OrientationState(
    /** Last accepted orientation request. */
    val request: OrientationRequest = OrientationRequest.AUTO,
    /** Orientation of the bound content; UNKNOWN before binding or when metadata is missing. */
    val contentOrientation: MediaOrientation = MediaOrientation.UNKNOWN,
    /** Whether the host has the session in fullscreen. */
    val fullscreen: Boolean = false,
)

/** SessionVisibility of a session as reported by the host (07 §3, 06 §4.2). */
public enum class SessionVisibility {
    /** On screen. */
    VISIBLE,

    /** Partly on screen (for example a slot scrolled half out): keeps playing, may lower frame rate or resolution (07 §3). */
    PARTIALLY_VISIBLE,

    /** Not on screen but the host page is in the foreground (for example a scrolled-away slot). */
    OFFSCREEN,

    /** The host is in the background. */
    BACKGROUND,
}

/**
 * State and result of one host action as maintained by the session (14 §3.2). Pending merging of
 * repeated clicks is done by the session.
 */
public data class HostActionState(
    /** The action as last provided by the host. */
    val action: VideoKitHostAction,
    /** Whether a request for this action is in flight or reported pending by the host. */
    val pending: Boolean = action.pending,
    /** Status of the last request, if any. */
    val lastStatus: HostActionStatus? = null,
    /** Error of the last request, if it failed. */
    val lastError: VideoKitStableError? = null,
)

/**
 * Observable session state (04 §3.1). Video-only fields (tracks, speed, volume) keep their defaults
 * for image sessions and are not shown by the UI.
 */
public data class VideoKitSessionState(
    /** Current phase. */
    val phase: SessionPhase = SessionPhase.CREATED,
    /** Kind of the bound media, `null` before binding. */
    val mediaKind: MediaKind? = null,
    /** Current position in microseconds. */
    val positionUs: Long = 0L,
    /** Duration in microseconds, if known. */
    val durationUs: Long? = null,
    /** Buffered position in microseconds, if known. */
    val bufferedUs: Long? = null,
    /** Whether playback continues as soon as possible. */
    val playWhenReady: Boolean = false,
    /** Playback speed. */
    val speed: Float = 1f,
    /** Session volume 0..1. */
    val volume: Float = 1f,
    /** Whether the session is muted by command. */
    val muted: Boolean = false,
    /** Audio tracks. */
    val audioTracks: List<TrackInfo> = emptyList(),
    /** Subtitle tracks. */
    val subtitleTracks: List<TrackInfo> = emptyList(),
    /** Selected audio track id. */
    val selectedAudioTrackId: String? = null,
    /** Selected subtitle track id; `null` = subtitles off. */
    val selectedSubtitleTrackId: String? = null,
    /** View transform. */
    val transform: MediaTransform = MediaTransform(),
    /** Orientation and fullscreen. */
    val orientation: OrientationState = OrientationState(),
    /** SessionVisibility reported by the host. */
    val visibility: SessionVisibility = SessionVisibility.VISIBLE,
    /**
     * Whether this session is the one allowed to play audio (07 §4). `false` by default (04A A1): a bound session is
     * silent until the host grants audio with `SetActiveAudio(true, epoch)`; single-player hosts grant it after bind.
     */
    val activeAudio: Boolean = false,
    /** Whether the playback controls are visible (original requirement §15.2). */
    val controlsVisible: Boolean = true,
    /** Current error, if the phase is an error phase. */
    val error: VideoKitStableError? = null,
    /** Whether the session still holds decoder, source or surface resources (original requirement §19.1). */
    val resourcesHeld: Boolean = false,
    /** Target of the seek that is in progress, if any (14 §3.2). */
    val seekingToUs: Long? = null,
    /** Host actions and their pending/result state (14 §3.2). */
    val hostActions: List<HostActionState> = emptyList(),
    /** Content size after rotation correction, if known (14 §3.2). */
    val videoSize: Size? = null,
    /** Whether the content is hidden because the host is locked (06 §4.2). */
    val hiddenForLock: Boolean = false,
    /** Whether playback loops (04A L1); set from the media kind at bind (animated images true, videos false). */
    val looping: Boolean = false,
    /** Image facts the engine knows (04A L2); always `null` for videos. */
    val imageDetails: ImageDetails? = null,
    /** Media parameters (04A P2), filled once bind completed; `null` before and when unknown. */
    val mediaInfo: MediaInfo? = null,
)

/**
 * Image facts for the details panel (04A L2). Every field is optional: the engine fills what it knows and the UI
 * shows only present values.
 */
public data class ImageDetails(
    /** Number of frames (1 for a static image), if known. */
    val frameCount: Int? = null,
    /** Bytes of the decoded bitmap(s) currently held, if known. */
    val decodedBytes: Long? = null,
    /** Decode subsampling factor (1 = full resolution, 2 = half, ...), if known. */
    val sampleSize: Int? = null,
)

/**
 * Snapshot of per-media playback preferences returned to the host (05 §3, original requirement §15.3).
 * The host persists it per content and scope; VideoKit never stores the scope. Video-only fields are
 * `null` for images.
 */
public data class VideoKitPlaybackState(
    /** Snapshot schema version; see [CURRENT_SCHEMA_VERSION]. */
    val schemaVersion: Int = CURRENT_SCHEMA_VERSION,
    /** Session that produced the snapshot, if any. */
    val sessionId: String? = null,
    /** Media token of the bound source, if any. */
    val mediaToken: String? = null,
    /** Zoom factor. */
    val zoom: Float = 1f,
    /** Horizontal pan. */
    val panX: Float = 0f,
    /** Vertical pan. */
    val panY: Float = 0f,
    /** Rotation in degrees. */
    val rotationDeg: Int = 0,
    /** Fit mode. */
    val fitMode: FitMode = FitMode.FIT,
    /** Preferred orientation. */
    val preferredOrientation: OrientationRequest = OrientationRequest.AUTO,
    /** Fullscreen. */
    val fullscreen: Boolean = false,
    /** Position in microseconds (video only). */
    val positionUs: Long? = null,
    /** Speed (video only). */
    val speed: Float? = null,
    /** Volume (video only). */
    val volume: Float? = null,
    /** Muted (video only). */
    val muted: Boolean? = null,
    /**
     * Selected subtitle track id (video only). Together with [subtitlesEnabled]: enabled + id = that track,
     * `subtitlesEnabled == false` = subtitles switched off, `null` id with `null` flag = nothing chosen (04A I9).
     */
    val subtitleTrackId: String? = null,
    /** Whether subtitles are on (video only); `null` = not chosen, the implementation default applies. */
    val subtitlesEnabled: Boolean? = null,
    /** Selected audio track id (video only). */
    val audioTrackId: String? = null,
    /** Wall clock time of the last view in epoch milliseconds, if known. */
    val lastViewedAtEpochMs: Long? = null,
    /** Looping preference (04A L3); `null` = the default of the media kind. Restored by bind when not `null`. */
    val looping: Boolean? = null,
) {
    public companion object {
        /** Schema version written by this API version. Older versions are read; newer majors are rejected. */
        public const val CURRENT_SCHEMA_VERSION: Int = 1
    }
}

/** Purpose of a session; used for defaults and resource priority. */
public enum class SessionPurpose {
    /** Single media player or viewer. */
    SINGLE,

    /** One slot of a multi-view grid (07). */
    MULTI_SLOT,

    /** Preview of an edit project. */
    EDIT_PREVIEW,
}

/** Configuration of a new session. */
public data class VideoKitSessionConfig(
    /** Purpose of the session. */
    val purpose: SessionPurpose = SessionPurpose.SINGLE,
    /** Resource priority used when reserving decoders (07 §2). */
    val priority: ResourcePriority = ResourcePriority.VISIBLE,
    /** Initial visibility. */
    val initialVisibility: SessionVisibility = SessionVisibility.VISIBLE,
    /** Initial audio activation (04A A1: `false`; the host grants audio with `SetActiveAudio(true, epoch)`, 07 §4). */
    val initialActiveAudio: Boolean = false,
    /** Opaque, host-chosen tag for diagnostics; never shown to the user. */
    val debugTag: String? = null,
)

/**
 * Media parameters for the details panel (04A P2). Every field is optional: the engine fills what the container and
 * the tracks declare, `null` when unknown.
 */
public data class MediaInfo(
    /** Container name, for example `mp4`, `mkv`, `ts`. */
    val container: String? = null,
    /** Video codec MIME type, for example `video/avc`. */
    val videoCodec: String? = null,
    /** Audio codec MIME type of the selected (or first) audio track. */
    val audioCodec: String? = null,
    /** Coded width in pixels (before rotation). */
    val width: Int? = null,
    /** Coded height in pixels (before rotation). */
    val height: Int? = null,
    /** Frame rate, frames per second. */
    val frameRate: Float? = null,
    /** Overall or video bitrate in bits per second. */
    val bitrateBps: Long? = null,
    /** Rotation metadata in degrees (0, 90, 180, 270). */
    val rotationDeg: Int? = null,
    /** Duration. */
    val durationUs: Long? = null,
    /** Source size in bytes, when the host knows it. */
    val fileSizeBytes: Long? = null,
)

/** Result of [VideoKitSession.captureThumbnail] (04A P1). */
public sealed interface ThumbnailResult {
    /** The thumbnail. */
    public class Captured(
        /** Encoded image (JPEG unless [mimeType] says otherwise). */
        public val bytes: ByteArray,
        /** Width in pixels. */
        public val width: Int,
        /** Height in pixels. */
        public val height: Int,
        /** MIME type of [bytes]. */
        public val mimeType: String = "image/jpeg",
    ) : ThumbnailResult {
        override fun equals(other: Any?): Boolean = other is Captured &&
            other.width == width &&
            other.height == height &&
            other.mimeType == mimeType &&
            other.bytes.contentEquals(bytes)

        override fun hashCode(): Int = (bytes.contentHashCode() * 31 + width) * 31 + height

        override fun toString(): String = "Captured(${width}x$height, $mimeType, ${bytes.size} bytes)"
    }

    /** No thumbnail; [error] says why. */
    public data class Failed(
        /** Stable error. */
        val error: VideoKitStableError,
    ) : ThumbnailResult
}
