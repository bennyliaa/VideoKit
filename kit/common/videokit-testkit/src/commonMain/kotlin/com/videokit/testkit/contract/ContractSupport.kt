package com.videokit.testkit.contract

import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.testkit.CountingSourceFactory
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.SourceBehavior
import com.videokit.testkit.internal.RecordList
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull

/**
 * The implementation under test of [VideoKitContractSuite] (04 §11). The Kotlin Fake and the real
 * implementation (instrumented, from VK-M1) provide one each.
 */
public interface VideoKitContractSubject {
    /** Callback timeouts the created instances use. */
    public val callbackTimeouts: HostCallbackTimeouts

    /** Source open/read timeout of the created instances. */
    public val sourceTimeoutMs: Long

    /** Creates a new instance with [callbacks]. */
    public fun create(callbacks: VideoKitHostCallbacks): VideoKit

    /** A playable video of at least 3 seconds with two or more audio tracks. */
    public fun playableVideo(token: String): VideoKitMediaSource

    /** A displayable static image. */
    public fun playableImage(token: String): VideoKitMediaSource

    /** Lets [us] microseconds of media time pass (Fake: advance the clock; real: wait). */
    public suspend fun advanceMediaTime(us: Long)

    /**
     * Drives [session] (state CREATED) into ERROR_FATAL, for example with a corrupt test file. Returns `false`
     * when the subject has no way to do so; vectors starting in ERROR_FATAL are then reported as skipped.
     */
    public suspend fun driveToFatalError(session: com.videokit.api.VideoKitSession): Boolean = false
}

/** Requirement group of a contract case (04 §11). */
public enum class ContractGroup {
    /** Version and capability negotiation. */
    VERSION_AND_CAPABILITIES,

    /** Legal and illegal state machine transitions. */
    STATE_MACHINE,

    /** Command results. */
    COMMAND_RESULTS,

    /** Cancellation and timeouts. */
    CANCELLATION_AND_TIMEOUT,

    /** Idempotent release. */
    RELEASE,

    /** Host callback failure isolation. */
    CALLBACK_ISOLATION,

    /** Input and sink fault mapping. */
    FAULT_MAPPING,

    /** Snapshot compatibility. */
    SNAPSHOT_COMPATIBILITY,
}

/** One contract case. */
public class ContractCase internal constructor(
    /** Stable id, for example `release.idempotent`. */
    public val id: String,
    /** Group. */
    public val group: ContractGroup,
    /** One-line description. */
    public val description: String,
    internal val body: suspend ContractScope.() -> Unit,
) {
    override fun toString(): String = id
}

/** A violated contract expectation. */
public class ContractViolation(message: String) : AssertionError(message)

/** Records the values of a flow from the moment it is created. */
public class EventRecorder<T> internal constructor(flow: Flow<T>, scope: CoroutineScope) {
    private val record = RecordList<T>()

    /** Values received so far (snapshot). */
    public val values: List<T> get() = record.snapshot

    private val job = scope.launch(Dispatchers.Unconfined, start = CoroutineStart.UNDISPATCHED) {
        flow.collect { record.add(it) }
    }

    /** Stops recording. */
    public fun stop() {
        job.cancel()
    }
}

/** Environment of a running contract case. */
public class ContractScope internal constructor(
    /** Subject. */
    public val subject: VideoKitContractSubject,
    /** Instance under test, created for this case. */
    public val kit: VideoKit,
    /** Host callbacks given to [kit]. */
    public val callbacks: RecordingHostCallbacks,
    private val background: CoroutineScope,
) {
    /** Default wait for state changes. */
    public val defaultWaitMs: Long = DEFAULT_WAIT_MS

    /** Starts recording [flow]. */
    public fun <T> record(flow: Flow<T>): EventRecorder<T> = EventRecorder(flow, background)

    /** Waits until [state] satisfies [predicate]. */
    public suspend fun <T> awaitState(
        state: StateFlow<T>,
        timeoutMs: Long = DEFAULT_WAIT_MS,
        what: String = "state",
        predicate: (T) -> Boolean,
    ): T = withTimeoutOrNull(timeoutMs) { state.first(predicate) }
        ?: throw ContractViolation("timed out waiting for $what; last value: ${state.value}")

    /** Waits until [condition] holds, polling every 10 ms. */
    public suspend fun eventually(what: String, timeoutMs: Long = DEFAULT_WAIT_MS, condition: () -> Boolean) {
        val ok = withTimeoutOrNull(timeoutMs) {
            while (!condition()) delay(POLL_MS)
            true
        }
        if (ok != true) throw ContractViolation("timed out waiting for $what")
    }

    /** Runs [block] with a timeout; a timeout is a violation. */
    public suspend fun <T> within(what: String, timeoutMs: Long = DEFAULT_WAIT_MS, block: suspend () -> T): T = try {
        withTimeout(timeoutMs) { block() }
    } catch (timeout: kotlinx.coroutines.TimeoutCancellationException) {
        throw ContractViolation("$what did not finish within $timeoutMs ms")
    }

    /** Launches [block] in the background scope. */
    public fun launchInBackground(block: suspend CoroutineScope.() -> Unit): kotlinx.coroutines.Job = background.launch(block = block)

    /** Wraps the subject's video so handle usage can be counted. */
    public fun countedVideo(token: String): Pair<VideoKitMediaSource, CountingSourceFactory> {
        val base = subject.playableVideo(token)
        val factory = CountingSourceFactory(SourceBehavior.Delegate(base.sourceFactory))
        return base.copy(sourceFactory = factory) to factory
    }

    /** The subject's video with a failing or hanging source. */
    public fun faultyVideo(token: String, behavior: SourceBehavior): Pair<VideoKitMediaSource, CountingSourceFactory> {
        val factory = CountingSourceFactory(behavior)
        return subject.playableVideo(token).copy(sourceFactory = factory) to factory
    }

    private companion object {
        const val DEFAULT_WAIT_MS = 15_000L
        const val POLL_MS = 10L
    }
}

internal fun expect(condition: Boolean, message: () -> String) {
    if (!condition) throw ContractViolation(message())
}

internal fun <T> expectEquals(expected: T, actual: T, what: String) {
    if (expected != actual) throw ContractViolation("$what: expected <$expected> but was <$actual>")
}
