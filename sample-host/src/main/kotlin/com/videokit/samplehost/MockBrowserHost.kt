package com.videokit.samplehost

import com.videokit.api.ActionPlacement
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.HostIcon
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitStableError
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.delay
import java.util.concurrent.ConcurrentHashMap

/**
 * Native host callbacks that imitate LocalVideoBrowser (05, 14 §10 mock host): a favourite toggle, a tag action that
 * is pending for 1.5 s and then succeeds, and a delete action that never answers (the Kit times it out, 04A I8). In
 * add-to-app mode these stay the host's callbacks; the embedded UI does not replace them.
 */
class MockBrowserHost : VideoKitHostCallbacks {
    private val favourites = ConcurrentHashMap.newKeySet<String>()

    /** Last snapshot per session (what the host would persist for "continue watching"). */
    val lastSnapshots: MutableMap<String, VideoKitPlaybackState> = ConcurrentHashMap()

    /** Host actions shown in the VideoKit action bar. */
    fun actionsFor(mediaToken: String): List<VideoKitHostAction> = listOf(
        favouriteAction(selected = mediaToken in favourites),
        VideoKitHostAction(
            actionId = ACTION_TAG,
            labelKey = "host.tag",
            contentDescriptionKey = "host.tag.description",
            icon = HostIcon.BuiltIn("tag"),
            placement = ActionPlacement.PRIMARY_BAR,
        ),
        VideoKitHostAction(
            actionId = ACTION_DELETE,
            labelKey = "host.delete",
            contentDescriptionKey = "host.delete.description",
            icon = HostIcon.BuiltIn("delete"),
            placement = ActionPlacement.OVERFLOW,
        ),
    )

    override suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult = when (request.actionId) {
        ACTION_FAVOURITE -> {
            val selected = if (favourites.remove(request.mediaToken)) false else favourites.add(request.mediaToken)
            HostActionResult(HostActionStatus.COMPLETED, updatedAction = favouriteAction(selected))
        }

        ACTION_DELETE -> awaitCancellation()

        ACTION_TAG -> {
            delay(TAG_DELAY_MS)
            HostActionResult(HostActionStatus.COMPLETED)
        }

        else -> HostActionResult(HostActionStatus.FAILED)
    }

    override suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult = NavigationResult.UNAVAILABLE

    override suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState) {
        snapshot.sessionId?.let { lastSnapshots[it] = snapshot }
    }

    override suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent) = Unit

    override suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean) = Unit

    override suspend fun onSourceReleased(sessionId: String, mediaToken: String) = Unit

    override suspend fun onRecoverableError(sessionId: String, error: VideoKitStableError): RecoveryDecision = RecoveryDecision.RETRY

    override suspend fun onFatalSessionError(sessionId: String, error: VideoKitStableError) = Unit

    private fun favouriteAction(selected: Boolean) = VideoKitHostAction(
        actionId = ACTION_FAVOURITE,
        labelKey = "host.favourite",
        contentDescriptionKey = "host.favourite.description",
        icon = HostIcon.BuiltIn("favourite"),
        selected = selected,
        placement = ActionPlacement.PRIMARY_BAR,
    )

    private companion object {
        const val ACTION_FAVOURITE = "favourite"
        const val ACTION_TAG = "tag"
        const val ACTION_DELETE = "delete"
        const val TAG_DELAY_MS = 1_500L
    }
}
