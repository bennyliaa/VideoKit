package com.videokit.core.spi

import com.videokit.api.SeekMode
import com.videokit.api.Size
import com.videokit.api.TrackInfo
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitSurfaceTarget
import kotlinx.coroutines.flow.StateFlow

/**
 * Playback engine (02 §4.2): opens a source, controls playback, exposes tracks and renders to a target.
 * Android: ExoPlayer in `videokit-media3`. The session state machine, command serialization, host callbacks and
 * event sampling are not part of the engine; they live in `videokit-core` / `videokit-playback`.
 *
 * Contract (checked by the playback contract tests):
 * - [open] returns once the media is prepared (duration, tracks and size known) or throws [SpiException] with a
 *   stable error; cancelling the caller cancels the open and closes every read handle it opened.
 * - All read handles of a playback are closed when [PlaybackHandle.close] returns (06 §7: SourceReleased is only
 *   reported after that).
 * - Errors during playback are reported through [EngineState.status] = FAILED with a stable error; the engine
 *   never throws from state collection.
 */
public interface PlaybackEngine {
    /** Opens [source] for playback. Throws [SpiException] when the source cannot be opened or prepared. */
    public suspend fun open(source: VideoKitMediaSource, options: PlaybackOpenOptions): PlaybackHandle

    /** Whether [target] is a render target type this engine can draw into (04A I13). */
    public fun supports(target: VideoKitSurfaceTarget): Boolean
}

/** Options of [PlaybackEngine.open]. */
public data class PlaybackOpenOptions(
    /** Whether audio output is enabled (silent multi-view slots disable the audio track, 15 §2.1). */
    val audioEnabled: Boolean = true,
    /** Whether the engine may request system audio focus (only the audible session, 15 §2.1). */
    val handleAudioFocus: Boolean = false,
    /** Initial position. */
    val startPositionUs: Long = 0L,
    /** Initial looping (04A L1). */
    val looping: Boolean = false,
)

/** Playback state reported by the engine. */
public enum class EngineStatus {
    /** Preparing. */
    PREPARING,

    /** Ready to play. */
    READY,

    /** Waiting for data. */
    BUFFERING,

    /** Reached the end (never reported while looping). */
    ENDED,

    /** Failed; see [EngineState.error]. */
    FAILED,
}

/** Snapshot of the engine state. Position updates at least every 250 ms while playing. */
public data class EngineState(
    /** Status. */
    val status: EngineStatus,
    /** Whether playing when ready. */
    val playing: Boolean,
    /** Position. */
    val positionUs: Long,
    /** Duration, when known. */
    val durationUs: Long?,
    /** Buffered position, when known. */
    val bufferedUs: Long?,
    /** Content size after rotation, when known. */
    val videoSize: Size?,
    /** Audio tracks. */
    val audioTracks: List<TrackInfo>,
    /** Subtitle tracks. */
    val subtitleTracks: List<TrackInfo>,
    /** Error when [status] is [EngineStatus.FAILED]. */
    val error: VideoKitStableError? = null,
    /** Selected audio track, when any. */
    val selectedAudioTrackId: String? = null,
    /** Media parameters from the container and the track formats (04A P2), once known. */
    val mediaInfo: com.videokit.api.MediaInfo? = null,
    /** Selected subtitle track, `null` when subtitles are off. */
    val selectedSubtitleTrackId: String? = null,
)

/** An opened playback. Closing releases decoders, the render target and all read handles. */
public interface PlaybackHandle : AutoCloseable {
    /** Engine state. */
    public val state: StateFlow<EngineState>

    /** Starts or resumes. */
    public suspend fun play()

    /** Pauses. */
    public suspend fun pause()

    /**
     * Seeks and suspends until the engine has the new position (the frame at the target can be rendered).
     * [SeekMode.PREVIEW] / [SeekMode.CLOSEST_SYNC] may land on a nearby key frame; [SeekMode.EXACT] is frame exact.
     */
    public suspend fun seekTo(positionUs: Long, mode: SeekMode)

    /** Sets the speed (pitch preserved). */
    public suspend fun setSpeed(speed: Float)

    /** Sets the volume 0..1; 0 for muted. */
    public suspend fun setVolume(volume: Float)

    /**
     * Enables or disables audio output. Disabled deselects the audio track (releasing the audio decoder) and
     * abandons audio focus; enabled re-selects it and requests focus when [PlaybackOpenOptions.handleAudioFocus].
     */
    public suspend fun setAudioEnabled(enabled: Boolean)

    /** Selects an audio track; `null` for the default. */
    public suspend fun selectAudioTrack(trackId: String?)

    /** Selects a subtitle track; `null` turns subtitles off. */
    public suspend fun selectSubtitleTrack(trackId: String?)

    /** Loops at the end instead of ending (04A L1). */
    public suspend fun setLooping(looping: Boolean)

    /** Renders to [target] (a type [PlaybackEngine.supports]); replaces the previous target. */
    public fun attach(target: VideoKitSurfaceTarget)

    /** Stops rendering. */
    public fun detach()
}
