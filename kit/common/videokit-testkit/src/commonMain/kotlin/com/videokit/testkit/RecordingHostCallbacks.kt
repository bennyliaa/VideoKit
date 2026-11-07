package com.videokit.testkit

import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitStableError
import com.videokit.testkit.internal.AtomicMap
import com.videokit.testkit.internal.RecordList
import kotlinx.coroutines.awaitCancellation
import kotlin.concurrent.Volatile

/** How a [RecordingHostCallbacks] callback misbehaves. */
public enum class CallbackMode {
    /** Answers normally. */
    NORMAL,

    /** Throws an exception. */
    THROW,

    /** Never returns until cancelled (VideoKit's timeout must fire). */
    HANG,
}

/**
 * [VideoKitHostCallbacks] that records every call and can be switched to throw or hang, for the
 * contract suite's callback isolation cases. All lists are thread-safe immutable snapshots.
 */
public class RecordingHostCallbacks(
    /** Mode of all callbacks unless [overrideMode] says otherwise; may be changed at any time. */
    @Volatile public var mode: CallbackMode = CallbackMode.NORMAL,
    /** Answer to host action requests. */
    @Volatile public var hostActionAnswer: (HostActionRequest) -> HostActionResult = { HostActionResult(HostActionStatus.COMPLETED) },
    /** Answer to navigation requests. */
    @Volatile public var navigationAnswer: (NavigationRequest) -> NavigationResult = { NavigationResult.UNAVAILABLE },
    /** Answer to recoverable errors. */
    @Volatile public var recoveryAnswer: (VideoKitStableError) -> RecoveryDecision = { RecoveryDecision.KEEP_ERROR },
) : VideoKitHostCallbacks {
    private val overrides = AtomicMap<String, CallbackMode>()

    /** Sets the mode of one callback, by name (for example `onHostActionRequested`); `null` removes the override. */
    public fun overrideMode(callbackName: String, mode: CallbackMode?) {
        if (mode == null) overrides.remove(callbackName) else overrides.put(callbackName, mode)
    }

    private val hostActionRequestsRecord = RecordList<HostActionRequest>()

    /** Recorded host action requests. */
    public val hostActionRequests: List<HostActionRequest> get() = hostActionRequestsRecord.snapshot

    private val navigationRequestsRecord = RecordList<NavigationRequest>()

    /** Recorded navigation requests. */
    public val navigationRequests: List<NavigationRequest> get() = navigationRequestsRecord.snapshot

    private val snapshotsRecord = RecordList<VideoKitPlaybackState>()

    /** Recorded snapshots. */
    public val snapshots: List<VideoKitPlaybackState> get() = snapshotsRecord.snapshot

    private val playbackEventsRecord = RecordList<VideoKitPlaybackEvent>()

    /** Recorded playback events. */
    public val playbackEvents: List<VideoKitPlaybackEvent> get() = playbackEventsRecord.snapshot

    private val controlsVisibilityRecord = RecordList<Pair<String, Boolean>>()

    /** Recorded controls visibility changes (session id, visible). */
    public val controlsVisibility: List<Pair<String, Boolean>> get() = controlsVisibilityRecord.snapshot

    private val sourceReleasesRecord = RecordList<Pair<String, String>>()

    /** Recorded source releases (session id, media token). */
    public val sourceReleases: List<Pair<String, String>> get() = sourceReleasesRecord.snapshot

    private val recoverableErrorsRecord = RecordList<VideoKitStableError>()

    /** Recorded recoverable errors. */
    public val recoverableErrors: List<VideoKitStableError> get() = recoverableErrorsRecord.snapshot

    private val fatalErrorsRecord = RecordList<VideoKitStableError>()

    /** Recorded fatal errors. */
    public val fatalErrors: List<VideoKitStableError> get() = fatalErrorsRecord.snapshot

    override suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult {
        hostActionRequestsRecord.add(request)
        misbehave("onHostActionRequested")
        return hostActionAnswer(request)
    }

    override suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult {
        navigationRequestsRecord.add(request)
        misbehave("onNavigationRequested")
        return navigationAnswer(request)
    }

    override suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState) {
        snapshotsRecord.add(snapshot)
        misbehave("onPlaybackSnapshot")
    }

    override suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent) {
        playbackEventsRecord.add(event)
        misbehave("onPlaybackEvent")
    }

    override suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean) {
        controlsVisibilityRecord.add(sessionId to visible)
        misbehave("onControlsVisibilityChanged")
    }

    override suspend fun onSourceReleased(sessionId: String, mediaToken: String) {
        sourceReleasesRecord.add(sessionId to mediaToken)
        misbehave("onSourceReleased")
    }

    override suspend fun onRecoverableError(error: VideoKitStableError): RecoveryDecision {
        recoverableErrorsRecord.add(error)
        misbehave("onRecoverableError")
        return recoveryAnswer(error)
    }

    override suspend fun onFatalSessionError(error: VideoKitStableError) {
        fatalErrorsRecord.add(error)
        misbehave("onFatalSessionError")
    }

    private suspend fun misbehave(name: String) {
        when (overrides[name] ?: mode) {
            CallbackMode.NORMAL -> Unit
            CallbackMode.THROW -> throw IllegalStateException("host callback $name failed (injected)")
            CallbackMode.HANG -> awaitCancellation()
        }
    }
}
