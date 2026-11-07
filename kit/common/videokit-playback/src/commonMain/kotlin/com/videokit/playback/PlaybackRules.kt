package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.MediaKind
import com.videokit.api.MediaOrientation
import com.videokit.api.MediaTransform
import com.videokit.api.Size
import com.videokit.api.TrackInfo
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSessionState

/**
 * Playback control rules (02 §4.0 `videokit-playback`, 06 §4): argument validation, the initial-state restore of
 * 04 §6 and the snapshot of a session. Pure functions; the session applies them and pushes the result to the engine.
 */
public object PlaybackRules {
    /** Speed range (06 §4: 0.25–4.0). */
    public val SPEED_RANGE: ClosedFloatingPointRange<Float> = 0.25f..4f

    /** Largest zoom factor. */
    public const val MAX_SCALE: Float = 10f

    private val validRotations = setOf(0, 90, 180, 270)

    /** Codes that end a session (ERROR_FATAL); all others are recoverable. */
    public val FATAL_CODES: Set<ErrorCode> = setOf(ErrorCode.CORRUPT_MEDIA)

    /** Whether [speed] is a valid playback speed. */
    public fun isValidSpeed(speed: Float): Boolean = speed.isFinite() && speed in SPEED_RANGE

    /** Whether [volume] is a valid volume. */
    public fun isValidVolume(volume: Float): Boolean = volume.isFinite() && volume in 0f..1f

    /** Whether [transform] is a valid transform (06 §4: bounded zoom, finite pan, quarter rotations). */
    public fun isValidTransform(transform: MediaTransform): Boolean = transform.scale.isFinite() &&
        transform.scale > 0f &&
        transform.scale <= MAX_SCALE &&
        transform.panX.isFinite() &&
        transform.panY.isFinite() &&
        transform.rotationDeg in validRotations

    /** Default orientation of content of [size] (after rotation metadata). */
    public fun orientationOf(size: Size?): MediaOrientation = when {
        size == null || size.width <= 0 || size.height <= 0 -> MediaOrientation.UNKNOWN
        size.width > size.height -> MediaOrientation.LANDSCAPE
        size.width < size.height -> MediaOrientation.PORTRAIT
        else -> MediaOrientation.SQUARE
    }

    /** The audio track a selection of [trackId] resolves to (`null` = the first supported). */
    public fun resolveAudioTrack(tracks: List<TrackInfo>, trackId: String?): TrackInfo? =
        if (trackId == null) tracks.firstOrNull { it.supported } else tracks.firstOrNull { it.id == trackId }

    /**
     * Applies a host snapshot to a freshly prepared [state] (04 §6): transform and orientation always; position,
     * speed, volume, mute and tracks for videos only. Invalid or unknown values are ignored, never fatal.
     */
    public fun applyInitial(state: VideoKitSessionState, initial: VideoKitPlaybackState): VideoKitSessionState {
        val transform = MediaTransform(initial.zoom, initial.panX, initial.panY, initial.rotationDeg, initial.fitMode)
        var result = state.copy(
            transform = if (isValidTransform(transform)) transform else state.transform,
            orientation = state.orientation.copy(request = initial.preferredOrientation, fullscreen = initial.fullscreen),
        )
        // 04A L3: a saved looping preference overrides the default of the media kind (static images never loop).
        initial.looping?.let { if (loops(state.mediaKind)) result = result.copy(looping = it) }
        if (state.mediaKind != MediaKind.VIDEO) return result
        val duration = state.durationUs ?: 0L
        initial.positionUs?.let { result = result.copy(positionUs = it.coerceIn(0L, duration)) }
        initial.speed?.takeIf(::isValidSpeed)?.let { result = result.copy(speed = it) }
        initial.volume?.takeIf(::isValidVolume)?.let { result = result.copy(volume = it) }
        initial.muted?.let { result = result.copy(muted = it) }
        initial.audioTrackId?.let { id ->
            if (state.audioTracks.any { it.id == id && it.supported }) result = result.copy(selectedAudioTrackId = id)
        }
        when (initial.subtitlesEnabled) {
            // 04A I9: explicitly off wins over a remembered track.
            false -> result = result.copy(selectedSubtitleTrackId = null)

            else -> initial.subtitleTrackId?.let { id ->
                if (state.subtitleTracks.any { it.id == id }) result = result.copy(selectedSubtitleTrackId = id)
            }
        }
        return result
    }

    /** Snapshot of [state] for the host (04 §6); video-only fields are `null` for images. */
    public fun snapshotOf(
        sessionId: String,
        mediaToken: String?,
        state: VideoKitSessionState,
        lastViewedAtEpochMs: Long?,
    ): VideoKitPlaybackState {
        val isVideo = state.mediaKind == MediaKind.VIDEO
        return VideoKitPlaybackState(
            sessionId = sessionId,
            mediaToken = mediaToken,
            zoom = state.transform.scale,
            panX = state.transform.panX,
            panY = state.transform.panY,
            rotationDeg = state.transform.rotationDeg,
            fitMode = state.transform.fitMode,
            preferredOrientation = state.orientation.request,
            fullscreen = state.orientation.fullscreen,
            positionUs = if (isVideo) state.seekingToUs ?: state.positionUs else null,
            speed = if (isVideo) state.speed else null,
            volume = if (isVideo) state.volume else null,
            muted = if (isVideo) state.muted else null,
            subtitleTrackId = if (isVideo) state.selectedSubtitleTrackId else null,
            subtitlesEnabled = if (isVideo) state.selectedSubtitleTrackId != null else null,
            audioTrackId = if (isVideo) state.selectedAudioTrackId else null,
            lastViewedAtEpochMs = lastViewedAtEpochMs,
            looping = if (loops(state.mediaKind)) state.looping else null,
        )
    }

    /** Whether media of [kind] can loop (videos and animated images, 04A L1). */
    public fun loops(kind: MediaKind?): Boolean = kind == MediaKind.VIDEO || kind == MediaKind.IMAGE_ANIMATED

    /** Default looping of [kind] (04A L1): animated images loop, videos do not. */
    public fun defaultLooping(kind: MediaKind?): Boolean = kind == MediaKind.IMAGE_ANIMATED

    /** Output volume sent to the engine: silent when muted or hidden for the lock (06 §4, §4.2). */
    public fun outputVolume(state: VideoKitSessionState): Float = if (state.muted || state.hiddenForLock) 0f else state.volume

    /** Whether the engine's audio output (track and focus) is enabled: only the audible, unlocked session (07 §4). */
    public fun audioEnabled(state: VideoKitSessionState): Boolean = state.activeAudio && !state.hiddenForLock
}
