package com.videokit.api

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/**
 * Render target for a session (04 §4.4). Platform independent and open: every platform module provides
 * its concrete type (Android: `com.videokit.api.android.AndroidSurface`). A platform implementation only
 * accepts its own target types. VideoKit never releases the underlying surface; its owner does.
 */
public interface VideoKitSurfaceTarget {
    /** Target width in pixels. */
    public val width: Int

    /** Target height in pixels. */
    public val height: Int
}

/**
 * A playback or image session (04 §3). One session binds one media at a time. All suspend functions
 * are cancellable; commands execute in order on the session's serial executor.
 */
public interface VideoKitSession : AutoCloseable {
    /** Opaque session id. */
    public val sessionId: String

    /** Current state; replaced as a whole on every change. */
    public val state: StateFlow<VideoKitSessionState>

    /** Bounded, sampled one-off events. */
    public val events: Flow<VideoKitEvent>

    /** Whether this session is backed by demo/fake data (14 §3.2); the UI then shows a permanent demo badge. */
    public val isDemo: Boolean get() = false

    /**
     * Binds [source]. Re-binding first releases the old source and emits [VideoKitEvent.SourceReleased].
     *
     * @param initialState host-stored playback preferences to restore, if any.
     * @param hostActions host actions to show for this media.
     */
    public suspend fun bind(
        source: VideoKitMediaSource,
        initialState: VideoKitPlaybackState?,
        hostActions: List<VideoKitHostAction>,
    ): VideoKitCommandResult

    /** Executes [command] and returns its stable result. */
    public suspend fun execute(command: VideoKitCommand): VideoKitCommandResult

    /** Replaces the host actions. */
    public suspend fun updateHostActions(actions: List<VideoKitHostAction>)

    /**
     * Called by the UI when the user activates the host action [actionId] (04 §7). The session calls
     * [VideoKitHostCallbacks.onHostActionRequested] with a timeout. While a request for the same action
     * is pending, repeated requests are merged and return [VideoKitCommandResult.Superseded].
     */
    public suspend fun requestHostAction(actionId: String): VideoKitCommandResult

    /**
     * Called by the UI when the user asks for the previous/next media (06 §5). The session forwards it
     * to [VideoKitHostCallbacks.onNavigationRequested]; callback failures and timeouts map to
     * [NavigationResult.FAILED] (04A V4).
     */
    public suspend fun requestNavigation(direction: NavigationDirection): NavigationResult

    /**
     * Called by the UI when the controls are shown or hidden (14 §4.4). Updates
     * [VideoKitSessionState.controlsVisible] and notifies [VideoKitHostCallbacks.onControlsVisibilityChanged].
     */
    public fun setControlsVisible(visible: Boolean)

    /**
     * A thumbnail of the bound media (04A P1): the frame nearest to [atUs] for videos, the scaled picture for images,
     * as JPEG fitting [maxWidth] x [maxHeight]. Failures are returned as [ThumbnailResult.Failed], never thrown.
     */
    public suspend fun captureThumbnail(atUs: Long, maxWidth: Int, maxHeight: Int): ThumbnailResult

    /** Captures the current playback preferences. */
    public suspend fun captureState(): VideoKitPlaybackState

    /**
     * Releases the session and all its resources. Idempotent: repeated calls return the same final
     * snapshot. After release every command returns [VideoKitCommandResult.SessionReleased].
     */
    public suspend fun release(): VideoKitPlaybackState

    /**
     * Attaches a render target, replacing the previous one (04A I13). Returns [VideoKitCommandResult.Executed],
     * [VideoKitCommandResult.Unsupported] with [UnsupportedReason.DEVICE_CAPABILITY] for target types this
     * platform does not know, or [VideoKitCommandResult.SessionReleased].
     */
    public fun attachSurface(target: VideoKitSurfaceTarget): VideoKitCommandResult

    /** Detaches the current render target, for example when the surface is destroyed. */
    public fun detachSurface()

    /** Equivalent to [release] without waiting for the result. */
    override fun close()
}
