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
 * Android: ExoPlayer in `videokit-media3`. The session state machine, command serialization and event
 * sampling are not part of the engine; they live in `videokit-core` / `videokit-playback`.
 */
public interface PlaybackEngine {
    /** Opens [source] for playback. Throws [SpiException] when the source cannot be opened or probed. */
    public suspend fun open(source: VideoKitMediaSource, options: PlaybackOpenOptions): PlaybackHandle
}

/** Options of [PlaybackEngine.open]. */
public data class PlaybackOpenOptions(
    /** Whether audio output is enabled (silent multi-view slots disable the audio track, 15 §2.1). */
    val audioEnabled: Boolean = true,
    /** Whether the engine may request system audio focus. */
    val handleAudioFocus: Boolean = false,
    /** Initial position. */
    val startPositionUs: Long = 0L,
)

/** Playback state reported by the engine. */
public enum class EngineStatus {
    /** Preparing. */
    PREPARING,

    /** Ready to play. */
    READY,

    /** Waiting for data. */
    BUFFERING,

    /** Reached the end. */
    ENDED,

    /** Failed; see [EngineState.error]. */
    FAILED,
}

/** Snapshot of the engine state. */
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
)

/** An opened playback. Closing releases decoders and read handles. */
public interface PlaybackHandle : AutoCloseable {
    /** Engine state. */
    public val state: StateFlow<EngineState>

    /** Starts or resumes. */
    public suspend fun play()

    /** Pauses. */
    public suspend fun pause()

    /** Seeks. */
    public suspend fun seekTo(positionUs: Long, mode: SeekMode)

    /** Sets the speed (pitch preserved). */
    public suspend fun setSpeed(speed: Float)

    /** Sets the volume 0..1; 0 for muted. */
    public suspend fun setVolume(volume: Float)

    /** Enables or disables audio output (disabled releases the audio decoder). */
    public suspend fun setAudioEnabled(enabled: Boolean)

    /** Selects an audio track; `null` for the default. */
    public suspend fun selectAudioTrack(trackId: String?)

    /** Selects a subtitle track; `null` turns subtitles off. */
    public suspend fun selectSubtitleTrack(trackId: String?)

    /** Renders to [target]; throws [SpiException] (`Unsupported` semantics) for foreign target types. */
    public fun attach(target: VideoKitSurfaceTarget)

    /** Stops rendering. */
    public fun detach()
}
