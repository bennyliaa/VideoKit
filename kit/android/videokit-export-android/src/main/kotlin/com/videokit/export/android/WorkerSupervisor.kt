package com.videokit.export.android

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.ExportFailureReasons
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitStableError
import com.videokit.core.runtime.StableErrors

/**
 * Decisions of the main process about one export task in the `:export` worker (15 §1.5 / §2.8 option c1, S4):
 *
 * - **watchdog**: before the first written sample the worker gets [startupGraceMs] (cold start of the process plus
 *   the Transformer set-up: about 12 s on the emulator in S4 attempt 5); afterwards [hangMs] without any message is a
 *   hang (`EXPORT_FAILED`, reason `WORKER_TIMEOUT`);
 * - **errors win** (15 §2.8 constraint 4): once the worker reported an error, a later DONE is never trusted (S4
 *   attempt 5: a crashing worker still delivered DONE 15 s before it died);
 * - **death** without a terminal message is `WORKER_CRASHED` or `WORKER_KILLED`, from the system's exit reason;
 * - **bounded cancel**: a worker that does not confirm the cancellation within [cancelGraceMs] is killed and the
 *   task ends cancelled.
 *
 * Pure: no Android types; time comes from [nowMs]. Not thread safe (the client serializes calls).
 */
internal class WorkerSupervisor(
    private val nowMs: () -> Long,
    val startupGraceMs: Long = WorkerProtocol.STARTUP_GRACE_MS,
    val hangMs: Long = WorkerProtocol.HANG_MS,
    val cancelGraceMs: Long = WorkerProtocol.CANCEL_GRACE_MS,
) {
    /** How the worker process ended, from the system (ApplicationExitInfo) when known. */
    enum class Exit { CRASHED, KILLED, UNKNOWN }

    sealed interface Event {
        data class Started(val pid: Int) : Event

        data class Progress(val samples: Long, val processedUs: Long, val bytes: Long) : Event

        data class Done(val metadata: VideoKitOutputMetadata) : Event

        data class Error(val error: VideoKitStableError) : Event

        data object Cancelled : Event

        data class Died(val exit: Exit) : Event
    }

    sealed interface Verdict {
        /** Still running. */
        data object Running : Verdict

        /** The worker finished; the output still has to pass the main process checks. */
        data class Succeeded(val metadata: VideoKitOutputMetadata) : Verdict

        data class Failed(val error: VideoKitStableError) : Verdict

        data object Cancelled : Verdict
    }

    private val startedAt = nowMs()
    private var lastProgressAt = startedAt
    private var firstSample = false
    private var reportedError: VideoKitStableError? = null
    private var cancelRequestedAt: Long? = null
    private var verdict: Verdict = Verdict.Running

    /** Worker process id from STARTED, -1 before. */
    var pid: Int = -1
        private set

    /** Whether the client must kill the worker now (hang, cancel timeout); cleared by [killed]. */
    var killRequested: Boolean = false
        private set

    val isFinished: Boolean get() = verdict != Verdict.Running

    /** Whether the worker has written its first sample (watchdog switched from startup grace to [hangMs]). */
    val pastFirstSample: Boolean get() = firstSample

    fun onEvent(event: Event): Verdict {
        when (event) {
            is Event.Started -> {
                pid = event.pid
                lastProgressAt = nowMs()
            }

            is Event.Progress -> {
                lastProgressAt = nowMs()
                if (event.samples > 0) firstSample = true
            }

            is Event.Done -> if (!isFinished) {
                // Constraint 4: an error reported before means the output is not trusted, whatever the worker says now.
                verdict = reportedError?.let { Verdict.Failed(it) } ?: Verdict.Succeeded(event.metadata)
            }

            is Event.Error -> {
                if (reportedError == null) reportedError = event.error
                if (!isFinished || verdict is Verdict.Succeeded) verdict = Verdict.Failed(reportedError!!)
            }

            Event.Cancelled -> if (!isFinished) verdict = Verdict.Cancelled

            is Event.Died -> if (!isFinished) {
                verdict = when {
                    cancelRequestedAt != null -> Verdict.Cancelled
                    reportedError != null -> Verdict.Failed(reportedError!!)
                    event.exit == Exit.CRASHED -> Verdict.Failed(failure(ExportFailureReasons.WORKER_CRASHED))
                    else -> Verdict.Failed(failure(ExportFailureReasons.WORKER_KILLED))
                }
            }
        }
        return verdict
    }

    /** Asks for a cancellation; the client sends CANCEL to the worker. */
    fun requestCancel() {
        if (cancelRequestedAt == null && !isFinished) cancelRequestedAt = nowMs()
    }

    /** Watchdog tick: applies the time limits. */
    fun tick(): Verdict {
        if (isFinished) return verdict
        val now = nowMs()
        val cancelAt = cancelRequestedAt
        if (cancelAt != null && now - cancelAt > cancelGraceMs) {
            killRequested = true
            verdict = Verdict.Cancelled
            return verdict
        }
        val limit = if (firstSample) hangMs else startupGraceMs
        if (now - lastProgressAt > limit) {
            killRequested = true
            verdict = Verdict.Failed(failure(ExportFailureReasons.WORKER_TIMEOUT))
        }
        return verdict
    }

    /** The client killed the worker. */
    fun killed() {
        killRequested = false
    }

    /** A late success that the main process output checks rejected (stage VERIFYING). */
    fun rejectOutput(diagnostic: String): Verdict {
        verdict = Verdict.Failed(StableErrors.of(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, "VERIFY:$diagnostic"))
        return verdict
    }

    companion object {
        /** `EXPORT_FAILED` with `params.reason` (04A X1). */
        fun failure(reason: String): VideoKitStableError =
            StableErrors.of(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, "WORKER:$reason").let {
                it.copy(params = it.params + (ErrorParams.REASON to reason))
            }
    }
}
