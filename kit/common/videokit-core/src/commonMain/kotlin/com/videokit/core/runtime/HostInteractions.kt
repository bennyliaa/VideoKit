package com.videokit.core.runtime

import com.videokit.api.ErrorStage
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionState
import com.videokit.api.HostActionStatus
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitSessionState
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

/**
 * Host interaction rules of one session (05 §5–§6, 04A I1–I3), shared by every media kind:
 *
 * - **Host actions**: the host's callback runs with the `hostActionMs` timeout; a request for an action that is
 *   pending (host answered PENDING, or a callback is in flight) is merged and answered `Superseded` without
 *   reaching the host again; a failure or timeout only marks the action (lightweight error, playback unaffected).
 *   [updateHostActions] keeps the local pending flag of in-flight requests and the last status.
 * - **Navigation**: one request-answer at a time; a repeated request in the same direction while one is in flight
 *   shares its answer (a double swipe does not skip two media); failure and timeout answer FAILED (04A V4).
 * - **Controls visibility**: written back into the state and reported to the host only on change (14 §4.4).
 *
 * All state changes go through [state] while holding [lock] (the session's serial executor); callbacks run outside
 * of it.
 */
public class HostInteractions(
    private val sessionId: String,
    private val callbacks: HostCallbackRunner,
    private val lock: Mutex,
    private val state: MutableStateFlow<VideoKitSessionState>,
    private val events: MutableSharedFlow<VideoKitEvent>,
    /** Media token of the bound media (read under [lock]); `null` when nothing is bound. */
    private val boundToken: () -> String?,
    /** Media token for navigation: the bound media or the last one (after a failed bind). */
    private val navigationToken: () -> String?,
    /** Whether the session is released or releasing. */
    private val released: () -> Boolean,
) {
    private val inFlightActions = mutableSetOf<String>()
    private val navigationLock = Mutex()
    private val inFlightLock = Mutex()
    private var inFlightNavigation: Pair<NavigationDirection, CompletableDeferred<NavigationResult>>? = null

    /** Host action states of [actions] for a new bind (called under [lock]). */
    public fun statesForBind(actions: List<VideoKitHostAction>): List<HostActionState> = actions.map { HostActionState(it) }

    /** Replaces the action list (04 §5), keeping local pending flags and the last results. */
    public suspend fun updateHostActions(actions: List<VideoKitHostAction>) {
        lock.withLock {
            if (released()) return
            state.update { current ->
                val previous = current.hostActions.associateBy { it.action.actionId }
                current.copy(
                    hostActions = actions.map { action ->
                        val old = previous[action.actionId]
                        HostActionState(
                            action = action,
                            pending = action.pending || action.actionId in inFlightActions,
                            lastStatus = old?.lastStatus,
                            lastError = old?.lastError,
                        )
                    },
                )
            }
        }
    }

    /** Asks the host to perform [actionId] (05 §5). */
    public suspend fun requestHostAction(actionId: String): VideoKitCommandResult {
        val request: HostActionRequest
        lock.withLock {
            if (released()) return VideoKitCommandResult.SessionReleased
            val token = boundToken() ?: return rejected("HOST_ACTION_WITHOUT_MEDIA")
            val entry = state.value.hostActions.firstOrNull { it.action.actionId == actionId }
                ?: return VideoKitCommandResult.Rejected(StableErrors.invalidArgument(ErrorStage.CALLBACK, "HOST_ACTION_ID"))
            if (!entry.action.enabled) return rejected("HOST_ACTION_DISABLED")
            // 04A I1: repeated requests while pending are merged and never reach the host again.
            if (entry.pending || actionId in inFlightActions) return VideoKitCommandResult.Superseded
            inFlightActions += actionId
            updateAction(actionId) { it.copy(pending = true, lastError = null) }
            request = HostActionRequest(actionId, sessionId, token)
        }
        var outcome: CallbackOutcome<HostActionResult>? = null
        try {
            outcome = callbacks.request("onHostActionRequested", callbacks.timeouts.hostActionMs) { onHostActionRequested(request) }
        } finally {
            withContext(NonCancellable) {
                lock.withLock {
                    inFlightActions -= actionId
                    if (outcome == null) updateAction(actionId) { it.copy(pending = false) }
                }
            }
        }
        return lock.withLock {
            if (released()) return@withLock VideoKitCommandResult.SessionReleased
            when (val result = outcome) {
                is CallbackOutcome.Success -> {
                    val answer = result.value
                    val stillPending = answer.status == HostActionStatus.PENDING
                    updateAction(actionId) {
                        val action = (answer.updatedAction ?: it.action).copy(pending = stillPending)
                        HostActionState(action, pending = stillPending, lastStatus = answer.status, lastError = null)
                    }
                    answer.messageKey?.let { events.tryEmit(VideoKitEvent.TransientNotice(it)) }
                    VideoKitCommandResult.Executed
                }

                is CallbackOutcome.Failure -> {
                    updateAction(actionId) { it.copy(pending = false, lastStatus = HostActionStatus.FAILED, lastError = result.error) }
                    events.tryEmit(VideoKitEvent.HostActionFailed(actionId, result.error))
                    VideoKitCommandResult.Rejected(result.error)
                }
            }
        }
    }

    /** Asks the host for the previous/next media (05 §6); the host binds it. */
    public suspend fun requestNavigation(direction: NavigationDirection): NavigationResult {
        if (released()) return NavigationResult.UNAVAILABLE
        // A repeated request in the same direction shares the pending answer; other requests queue behind it.
        val answer = CompletableDeferred<NavigationResult>()
        val pending = inFlightLock.withLock {
            inFlightNavigation?.takeIf { it.first == direction }?.second.also { if (it == null) inFlightNavigation = direction to answer }
        }
        if (pending != null) return pending.await()
        return try {
            navigationLock.withLock {
                if (released()) return@withLock NavigationResult.UNAVAILABLE
                val token = lock.withLock { navigationToken() }
                val request = NavigationRequest(sessionId, token, direction)
                val outcome = callbacks.request("onNavigationRequested", callbacks.timeouts.navigationMs) { onNavigationRequested(request) }
                (outcome as? CallbackOutcome.Success)?.value ?: NavigationResult.FAILED
            }.also(answer::complete)
        } catch (cancelled: CancellationException) {
            answer.complete(NavigationResult.FAILED)
            throw cancelled
        } finally {
            withContext(NonCancellable) {
                inFlightLock.withLock { if (inFlightNavigation?.second === answer) inFlightNavigation = null }
            }
        }
    }

    /** Writes back the visibility of the controls (04A I3) and reports a change to the host. */
    public fun setControlsVisible(visible: Boolean) {
        if (released()) return
        var changed = false
        state.update { current ->
            changed = current.controlsVisible != visible
            current.copy(controlsVisible = visible)
        }
        if (changed) callbacks.notify("onControlsVisibilityChanged") { onControlsVisibilityChanged(sessionId, visible) }
    }

    private fun updateAction(actionId: String, transform: (HostActionState) -> HostActionState) {
        state.update { current ->
            current.copy(hostActions = current.hostActions.map { if (it.action.actionId == actionId) transform(it) else it })
        }
    }

    private fun rejected(what: String): VideoKitCommandResult =
        VideoKitCommandResult.Rejected(StableErrors.illegalState(ErrorStage.CALLBACK, what))
}

/**
 * Work that holds extra read handles of the bound media besides the engine (thumbnails, probes). 05 §4:
 * SourceReleased may only be reported once every handle the session opened for the media is closed, so the
 * session [closeAll]s these uses before it reports it. Each use runs as a child of [scope] (the session scope), so
 * closing a use never cancels its caller.
 */
public class SourceUses(private val scope: CoroutineScope) {
    private val jobs = AtomicMap<Long, Job>()
    private val ids = AtomicCounter()

    /**
     * Runs [block] as a use of the bound media. Returns `null` when [closeAll] stopped it (the media was released);
     * the caller's own cancellation is rethrown after the use finished.
     */
    public suspend fun <T : Any> use(block: suspend CoroutineScope.() -> T): T? {
        val id = ids.incrementAndGet()
        val work = scope.async(start = CoroutineStart.LAZY, block = block)
        jobs.put(id, work)
        return try {
            work.start()
            work.await()
        } catch (cancelled: CancellationException) {
            if (!currentCoroutineContext().isActive) {
                withContext(NonCancellable) { work.cancelAndJoin() }
                throw cancelled
            }
            null
        } finally {
            jobs.remove(id)
        }
    }

    /** Number of uses in progress (diagnostics). */
    public val active: Int get() = jobs.snapshot.size

    /** Cancels every use in progress and waits until each finished (its `finally` blocks closed the handles). */
    public suspend fun closeAll() {
        jobs.snapshot.values.toList().forEach { runCatching { it.cancelAndJoin() } }
    }
}
