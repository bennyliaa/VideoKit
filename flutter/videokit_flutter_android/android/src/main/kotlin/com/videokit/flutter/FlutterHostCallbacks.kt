package com.videokit.flutter

import com.videokit.api.FeatureAccess
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.VideoKitFeature
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitStableError
import com.videokit.flutter.Mappers.toMsg
import com.videokit.flutter.Mappers.toResult
import com.videokit.flutter.gen.VideoKitCallbacksApi
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.withContext

/**
 * Host callbacks of one engine, forwarded to Dart through the Pigeon `@FlutterApi` (14 §8.1). Timeouts are
 * applied by the Kit runtime (04A I8); a Dart side error, a missing listener or a timeout becomes
 * HOST_CALLBACK_FAILED there. Every call is sent from the platform thread, as required by the Flutter channels.
 */
internal class FlutterHostCallbacks(private val api: VideoKitCallbacksApi, private val main: CoroutineDispatcher) : VideoKitHostCallbacks {
    override suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult =
        withContext(main) { api.onHostActionRequested(request.toMsg()) }.toResult()

    override suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult =
        Mappers.navigationResult(withContext(main) { api.onNavigationRequested(request.toMsg()) })

    override suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState) {
        val msg = snapshot.toMsg()
        withContext(main) { api.onPlaybackSnapshot(msg) }
    }

    override suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent) {
        val msg = event.toMsg()
        withContext(main) { api.onPlaybackEvent(msg) }
    }

    override suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean) =
        withContext(main) { api.onControlsVisibilityChanged(sessionId, visible) }

    override suspend fun onSourceReleased(sessionId: String, mediaToken: String) =
        withContext(main) { api.onSourceReleased(sessionId, mediaToken) }

    override suspend fun onRecoverableError(sessionId: String, error: VideoKitStableError): RecoveryDecision {
        val msg = error.toMsg()
        return Mappers.recoveryDecision(withContext(main) { api.onRecoverableError(sessionId, msg) })
    }

    override suspend fun onFatalSessionError(sessionId: String, error: VideoKitStableError) {
        val msg = error.toMsg()
        withContext(main) { api.onFatalSessionError(sessionId, msg) }
    }

    // REQ-API-10: the Dart host's gate. A Dart error or the Kit timeout counts as denied (Kit runtime).
    override suspend fun checkFeature(feature: VideoKitFeature, sessionId: String?): FeatureAccess =
        Mappers.featureAccess(withContext(main) { api.checkFeature(feature.name, sessionId) })
}
