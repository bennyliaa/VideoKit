package com.videokit.export.android

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.ExportFailureReasons
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.core.runtime.StableErrors
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** M6-B1: the main process rules for one export task (15 §2.8, 04A X1, S4 attempt 5 findings). */
class WorkerSupervisorTest {
    private var now = 1_000L
    private val supervisor = WorkerSupervisor(nowMs = { now })
    private val meta = VideoKitOutputMetadata("mp4", "mp4", "video/avc", null, 640, 360, 0, 8_000_000, 1_000, 30f, false)

    private fun reasonOf(verdict: WorkerSupervisor.Verdict): String? =
        (verdict as WorkerSupervisor.Verdict.Failed).error.params[ErrorParams.REASON]

    @Test
    fun startupGraceBeforeTheFirstSampleThenHangLimit() {
        supervisor.onEvent(WorkerSupervisor.Event.Started(4242))
        now += WorkerProtocol.STARTUP_GRACE_MS
        assertEquals(WorkerSupervisor.Verdict.Running, supervisor.tick())
        supervisor.onEvent(WorkerSupervisor.Event.Progress(samples = 1, processedUs = 33_000, bytes = 900))
        assertTrue(supervisor.pastFirstSample)
        now += WorkerProtocol.HANG_MS
        assertEquals(WorkerSupervisor.Verdict.Running, supervisor.tick())
        now += 1
        val verdict = supervisor.tick()
        assertEquals(ExportFailureReasons.WORKER_TIMEOUT, reasonOf(verdict))
        assertEquals(ErrorCode.EXPORT_FAILED, (verdict as WorkerSupervisor.Verdict.Failed).error.code)
        assertTrue("a hang is killed", supervisor.killRequested)
        supervisor.killed()
        assertFalse(supervisor.killRequested)
        assertEquals(4242, supervisor.pid)
    }

    @Test
    fun startupThatNeverWritesTimesOutAfterTheGrace() {
        now += WorkerProtocol.STARTUP_GRACE_MS + 1
        assertEquals(ExportFailureReasons.WORKER_TIMEOUT, reasonOf(supervisor.tick()))
    }

    @Test
    fun anErrorIsNeverOverriddenByALaterDone() {
        // S4 attempt 5: the OOM worker still sent DONE 15 s after its fatal exception.
        val crash = WorkerSupervisor.failure(ExportFailureReasons.WORKER_CRASHED)
        supervisor.onEvent(WorkerSupervisor.Event.Error(crash))
        val verdict = supervisor.onEvent(WorkerSupervisor.Event.Done(meta))
        assertEquals(ExportFailureReasons.WORKER_CRASHED, reasonOf(verdict))
    }

    @Test
    fun anErrorAfterDoneStillWins() {
        supervisor.onEvent(WorkerSupervisor.Event.Done(meta))
        val late = StableErrors.of(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, "TRANSFORMER:7000")
        assertEquals(late, (supervisor.onEvent(WorkerSupervisor.Event.Error(late)) as WorkerSupervisor.Verdict.Failed).error)
    }

    @Test
    fun deathWithoutAnswerIsCrashedOrKilled() {
        assertEquals(
            ExportFailureReasons.WORKER_CRASHED,
            reasonOf(WorkerSupervisor(nowMs = { now }).onEvent(WorkerSupervisor.Event.Died(WorkerSupervisor.Exit.CRASHED))),
        )
        assertEquals(
            ExportFailureReasons.WORKER_KILLED,
            reasonOf(WorkerSupervisor(nowMs = { now }).onEvent(WorkerSupervisor.Event.Died(WorkerSupervisor.Exit.KILLED))),
        )
        assertEquals(
            ExportFailureReasons.WORKER_KILLED,
            reasonOf(WorkerSupervisor(nowMs = { now }).onEvent(WorkerSupervisor.Event.Died(WorkerSupervisor.Exit.UNKNOWN))),
        )
        // A death after a reported error keeps the error.
        val failed = WorkerSupervisor.failure(ExportFailureReasons.WORKER_CRASHED)
        supervisor.onEvent(WorkerSupervisor.Event.Error(failed))
        val afterDeath = supervisor.onEvent(WorkerSupervisor.Event.Died(WorkerSupervisor.Exit.KILLED))
        assertEquals(failed, (afterDeath as WorkerSupervisor.Verdict.Failed).error)
    }

    @Test
    fun cancelIsBounded() {
        supervisor.onEvent(WorkerSupervisor.Event.Progress(1, 0, 0))
        supervisor.requestCancel()
        now += WorkerProtocol.CANCEL_GRACE_MS
        assertEquals(WorkerSupervisor.Verdict.Running, supervisor.tick())
        now += 1
        assertEquals(WorkerSupervisor.Verdict.Cancelled, supervisor.tick())
        assertTrue("an unanswered cancel is killed", supervisor.killRequested)
    }

    @Test
    fun confirmedCancelAndDeathDuringCancelEndCancelled() {
        supervisor.requestCancel()
        assertEquals(WorkerSupervisor.Verdict.Cancelled, supervisor.onEvent(WorkerSupervisor.Event.Cancelled))
        val other = WorkerSupervisor(nowMs = { now })
        other.requestCancel()
        assertEquals(WorkerSupervisor.Verdict.Cancelled, other.onEvent(WorkerSupervisor.Event.Died(WorkerSupervisor.Exit.KILLED)))
    }

    @Test
    fun rejectedOutputIsAVerifyFailure() {
        supervisor.onEvent(WorkerSupervisor.Event.Done(meta))
        val verdict = supervisor.rejectOutput("PTS_GAP") as WorkerSupervisor.Verdict.Failed
        assertEquals(ErrorCode.EXPORT_FAILED, verdict.error.code)
        assertEquals("VERIFY:PTS_GAP", verdict.error.diagnostic)
        assertEquals(null, verdict.error.params[ErrorParams.REASON])
    }
}
