package com.videokit.flutter

import com.videokit.api.SessionPhase
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionState
import com.videokit.flutter.Mappers.toMsg
import com.videokit.flutter.gen.EditUpdateMessage
import com.videokit.flutter.gen.SessionUpdateMessage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.takeWhile
import kotlinx.coroutines.launch
import java.util.concurrent.atomic.AtomicLong

/**
 * Snapshot sampling rule (14 §8.3, §12): phase changes are sent immediately; while seeking at most 15 Hz;
 * while playing at most 4 Hz; any other change immediately. Pure, so it is unit tested on the JVM.
 */
internal object UpdateSampler {
    const val PLAYING_INTERVAL_MS: Long = 250L
    const val SEEKING_INTERVAL_MS: Long = 66L

    /** Milliseconds to wait before sending [next], given the [last] sent state and its time. */
    fun waitMs(last: VideoKitSessionState?, next: VideoKitSessionState, nowMs: Long, lastSentAtMs: Long): Long {
        if (last == null || last.phase != next.phase) return 0L
        val interval = when {
            next.seekingToUs != null -> SEEKING_INTERVAL_MS
            next.phase == SessionPhase.PLAYING || next.phase == SessionPhase.BUFFERING -> PLAYING_INTERVAL_MS
            else -> return 0L
        }
        return (lastSentAtMs + interval - nowMs).coerceAtLeast(0L)
    }
}

/**
 * Wraps one session for the channel (14 §8.4): collects state and events, samples snapshots and sends
 * [SessionUpdateMessage]s with a monotonic `seq`. After the RELEASED snapshot it stops (14 §8.3).
 */
internal class SessionHolder(
    val sessionId: String,
    val session: VideoKitSession,
    private val scope: CoroutineScope,
    private val nowMs: () -> Long,
    private val send: (SessionUpdateMessage) -> Unit,
    /** Texture producers are released on the platform thread only. */
    private val main: MainThreadRunner = MainThreadRunner { it() },
    /** Adopted host session (add-to-app): Dart release and engine detach stop observing, never release it. */
    val hostOwned: Boolean = false,
) {
    private val seq = AtomicLong()
    private var jobs: List<Job> = emptyList()

    @Volatile
    var texture: TextureBinding? = null

    /** Last message sent with a state, replayed to a late stream listener. */
    @Volatile
    var lastStateMessage: SessionUpdateMessage? = null
        private set

    fun start(onReleased: () -> Unit) {
        val stateJob = scope.launch {
            var lastSent: VideoKitSessionState? = null
            var lastSentAt = 0L
            session.state.takeWhile { lastSent?.phase != SessionPhase.RELEASED }.collect { candidate ->
                val wait = UpdateSampler.waitMs(lastSent, candidate, nowMs(), lastSentAt)
                if (wait > 0) delay(wait)
                val current = session.state.value
                if (current != lastSent) {
                    lastSent = current
                    lastSentAt = nowMs()
                    val message = SessionUpdateMessage(sessionId, seq.incrementAndGet(), state = current.toMsg())
                    lastStateMessage = message
                    send(message)
                }
                if (current.phase == SessionPhase.RELEASED) onReleased()
            }
        }
        val eventJob = scope.launch {
            session.events.collect { event -> send(SessionUpdateMessage(sessionId, seq.incrementAndGet(), event = event.toMsg())) }
        }
        jobs = listOf(stateJob, eventJob)
    }

    fun stop() {
        jobs.forEach { it.cancel() }
        texture?.let { binding -> main.post { binding.dispose() } }
        texture = null
    }
}

/** Wraps one edit project for the channel; edit updates are not sampled (they are not high frequency). */
internal class ProjectHolder(
    val projectId: String,
    val project: VideoKitEditProject,
    private val scope: CoroutineScope,
    private val send: (EditUpdateMessage) -> Unit,
) {
    private val seq = AtomicLong()
    private var jobs: List<Job> = emptyList()

    fun start() {
        jobs = listOf(
            scope.launch { project.state.collect { send(EditUpdateMessage(projectId, seq.incrementAndGet(), state = it.toMsg())) } },
            scope.launch { project.events.collect { send(EditUpdateMessage(projectId, seq.incrementAndGet(), event = it.toMsg())) } },
        )
    }

    fun stop() {
        jobs.forEach { it.cancel() }
    }
}
