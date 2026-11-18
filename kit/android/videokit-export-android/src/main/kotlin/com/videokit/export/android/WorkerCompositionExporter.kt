package com.videokit.export.android

import android.app.ActivityManager
import android.app.ApplicationExitInfo
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Message
import android.os.Messenger
import android.os.Process
import androidx.media3.common.util.UnstableApi
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.ExportFailureReasons
import com.videokit.api.ExportStage
import com.videokit.api.OpenPurpose
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitWriteHandle
import com.videokit.api.android.FileDescriptorWriteHandle
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.CompositionExporter
import com.videokit.core.spi.ExportPlan
import com.videokit.core.spi.ExporterProgress
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull

/**
 * [CompositionExporter] that runs each export in the `:videokit_export` worker process (15 §1.5 / §2.8 option c1,
 * M6-B1; protocol verified in S4). This batch is the framework with a pass-through export: one clip, no masks,
 * re-encoded to H.264/AAC MP4 at the plan's output height; concatenation and the composition engine come after S3.
 *
 * Per task: the host source is served by a [SourceBroker] (pid pinned), the output descriptor of the host sink goes to
 * the worker, [WorkerSupervisor] applies the watchdog, the error rule and the bounded cancel, the worker is killed when
 * the task ends (always: a same-uid process is not reclaimed on unbind), and a DONE is only accepted after
 * [OutputCheck] in this process. Failures are [SpiException]s with `EXPORT_FAILED` (`params.reason` for worker
 * faults, 04A X1); cancelling the calling coroutine cancels the task within [WorkerProtocol.CANCEL_GRACE_MS] plus the
 * kill and rethrows.
 */
@UnstableApi
public class WorkerCompositionExporter(
    context: Context,
    /** Bound of one host `readAt` served to the worker. */
    private val readTimeoutMs: Long = DEFAULT_READ_TIMEOUT_MS,
) : CompositionExporter {
    private val app = context.applicationContext

    override suspend fun export(
        plan: ExportPlan,
        output: VideoKitWriteHandle,
        progress: (ExporterProgress) -> Unit,
    ): VideoKitOutputMetadata {
        val clip = plan.clips.singleOrNull() ?: throw unsupported("PASSTHROUGH_NEEDS_ONE_CLIP")
        if (plan.masks.isNotEmpty()) throw unsupported("PASSTHROUGH_WITHOUT_MASKS")
        val fdOutput = output as? FileDescriptorWriteHandle
            ?: throw SpiException(
                StableErrors.of(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED, ErrorStage.EXPORT, "WORKER_NEEDS_FILE_DESCRIPTOR"),
            )
        val input = plan.inputs.firstOrNull { it.sourceId == clip.sourceId } ?: throw unsupported("UNKNOWN_SOURCE")
        val handle = withContext(Dispatchers.IO) { input.source.sourceFactory.open(OpenPurpose.EXPORT) }
        val task = Task(handle, fdOutput)
        try {
            return task.run(clip.inUs, clip.outUs, plan.outputSize.height, progress)
        } finally {
            withContext(NonCancellable) { task.close() }
        }
    }

    private fun unsupported(what: String) = SpiException(StableErrors.of(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, "PLAN:$what"))

    /** One export task: broker, worker connection, supervisor. */
    private inner class Task(private val handle: VideoKitReadHandle, private val output: FileDescriptorWriteHandle) {
        private val broker = SourceBroker(handle, readTimeoutMs)
        private val events = Channel<WorkerSupervisor.Event>(Channel.UNLIMITED)
        private val supervisor = WorkerSupervisor(nowMs = { android.os.SystemClock.elapsedRealtime() })
        private val replies = HandlerThread("videokit-export-replies").apply { start() }
        private var worker: Messenger? = null
        private var workerBinder: IBinder? = null
        private var bound = false
        private var workerDied = false
        private var done: Bundle? = null

        private val death = IBinder.DeathRecipient {
            workerDied = true
            events.trySend(WorkerSupervisor.Event.Died(exitOf(supervisor.pid)))
        }

        private val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName, service: IBinder) {
                workerBinder = service
                runCatching { service.linkToDeath(death, 0) }
                worker = Messenger(service)
            }

            override fun onServiceDisconnected(name: ComponentName) = Unit
        }

        private val replyMessenger = Messenger(
            Handler(replies.looper) { message ->
                val data = message.data
                val event = when (message.what) {
                    WorkerProtocol.STARTED -> WorkerSupervisor.Event.Started(data.getInt(WorkerProtocol.KEY_PID, -1))

                    WorkerProtocol.PROGRESS -> WorkerSupervisor.Event.Progress(
                        data.getLong(WorkerProtocol.KEY_SAMPLES),
                        data.getLong(WorkerProtocol.KEY_PROCESSED_US),
                        data.getLong(WorkerProtocol.KEY_BYTES),
                    )

                    WorkerProtocol.DONE -> {
                        done = data.getBundle(WorkerProtocol.KEY_METADATA)
                        WorkerSupervisor.Event.Done(placeholderMetadata())
                    }

                    WorkerProtocol.ERROR -> WorkerSupervisor.Event.Error(errorOf(data))

                    WorkerProtocol.CANCELLED -> WorkerSupervisor.Event.Cancelled

                    else -> null
                }
                event?.let { events.trySend(it) }
                true
            },
        )

        suspend fun run(inUs: Long, outUs: Long, targetHeight: Int, progress: (ExporterProgress) -> Unit): VideoKitOutputMetadata {
            progress(ExporterProgress(ExportStage.PREPARING, null, 0L, 0L))
            connect()
            val start = Message.obtain(null, WorkerProtocol.START).apply {
                replyTo = replyMessenger
                data = Bundle().apply {
                    putBinder(WorkerProtocol.KEY_BROKER, broker)
                    putParcelable(WorkerProtocol.KEY_OUTPUT, output.fileDescriptor())
                    putLong(WorkerProtocol.KEY_IN_US, inUs)
                    putLong(WorkerProtocol.KEY_OUT_US, outUs)
                    putInt(WorkerProtocol.KEY_TARGET_HEIGHT, targetHeight)
                }
            }
            checkNotNull(worker).send(start)
            try {
                supervise(outUs - inUs, progress)
            } catch (cancelled: CancellationException) {
                withContext(NonCancellable) { cancelBounded() }
                throw cancelled
            }
            return when (val verdict = lastVerdict) {
                is WorkerSupervisor.Verdict.Succeeded -> accept(outUs, progress)
                is WorkerSupervisor.Verdict.Failed -> throw SpiException(verdict.error)
                WorkerSupervisor.Verdict.Cancelled ->
                    throw SpiException(StableErrors.of(ErrorCode.CANCELLED, ErrorStage.EXPORT, "WORKER:CANCELLED"))
                WorkerSupervisor.Verdict.Running -> error("supervision ended while running")
            }
        }

        private var lastVerdict: WorkerSupervisor.Verdict = WorkerSupervisor.Verdict.Running

        private suspend fun supervise(clipUs: Long, progress: (ExporterProgress) -> Unit) {
            while (!supervisor.isFinished) {
                val event = withTimeoutOrNull(WorkerProtocol.TICK_MS) { events.receive() }
                if (event != null) {
                    lastVerdict = supervisor.onEvent(event)
                    if (event is WorkerSupervisor.Event.Progress && event.samples > 0) {
                        val fraction = if (clipUs > 0) (event.processedUs.toFloat() / clipUs).coerceIn(0f, 1f) else null
                        progress(ExporterProgress(ExportStage.ENCODING, fraction, event.processedUs, event.bytes))
                    }
                }
                lastVerdict = supervisor.tick()
                if (supervisor.killRequested) {
                    kill()
                    supervisor.killed()
                }
            }
        }

        /** Coroutine cancelled: CANCEL, wait at most the grace, then kill (bounded). */
        private suspend fun cancelBounded() {
            supervisor.requestCancel()
            runCatching { worker?.send(Message.obtain(null, WorkerProtocol.CANCEL)) }
            while (!supervisor.isFinished) {
                val event = withTimeoutOrNull(WorkerProtocol.TICK_MS) { events.receive() }
                if (event != null) lastVerdict = supervisor.onEvent(event)
                lastVerdict = supervisor.tick()
            }
            kill()
        }

        /** Worker said DONE and nothing reported an error: check the output here before accepting it. */
        private fun accept(outUs: Long, progress: (ExporterProgress) -> Unit): VideoKitOutputMetadata {
            progress(ExporterProgress(ExportStage.VERIFYING, null, 0L, 0L))
            val meta = done ?: throw SpiException(supervisorFailure("NO_METADATA"))
            val effectiveInUs = meta.getLong("effectiveInUs")
            val check = OutputCheck.check(output.fileDescriptor().fileDescriptor, outUs - effectiveInUs)
            if (!check.ok) throw SpiException(supervisorFailure(check.failure ?: "UNKNOWN"))
            return VideoKitOutputMetadata(
                container = "mp4",
                extension = "mp4",
                videoCodec = meta.getString("videoCodec"),
                audioCodec = meta.getString("audioCodec"),
                width = check.width.takeIf { it > 0 } ?: meta.getInt("width"),
                height = check.height.takeIf { it > 0 } ?: meta.getInt("height"),
                rotationDeg = 0,
                durationUs = check.videoDurationUs,
                sizeBytes = meta.getLong("sizeBytes"),
                frameRate = check.frameRate,
                audioPresent = check.audioDurationUs != null,
            )
        }

        private fun supervisorFailure(diagnostic: String): VideoKitStableError =
            (supervisor.rejectOutput(diagnostic) as WorkerSupervisor.Verdict.Failed).error

        private suspend fun connect() {
            val intent = Intent(app, ExportWorkerService::class.java)
            bound = app.bindService(intent, Context.BIND_AUTO_CREATE, app.mainExecutor, connection)
            if (!bound) throw SpiException(WorkerSupervisor.failure(ExportFailureReasons.WORKER_KILLED))
            // Connected callbacks arrive on the main executor; the startup grace bounds the wait.
            withTimeoutOrNull(WorkerProtocol.STARTUP_GRACE_MS) { while (worker == null) delay(WorkerProtocol.TICK_MS / 5) }
                ?: throw SpiException(WorkerSupervisor.failure(ExportFailureReasons.WORKER_TIMEOUT))
        }

        /** Kills the worker (same uid) and waits for its binder to die. */
        private suspend fun kill() {
            val pid = supervisor.pid
            if (pid > 0 && pid != Process.myPid() && !workerDied) {
                Process.killProcess(pid)
                withTimeoutOrNull(WorkerProtocol.KILL_WAIT_MS) { while (!workerDied) delay(WorkerProtocol.TICK_MS / 5) }
            }
        }

        suspend fun close() {
            broker.revoke()
            kill()
            runCatching { workerBinder?.unlinkToDeath(death, 0) }
            if (bound) runCatching { app.unbindService(connection) }
            replies.quitSafely()
            runCatching { handle.close() }
        }

        private fun errorOf(data: Bundle): VideoKitStableError {
            val code = ErrorCode.fromWireName(data.getString(WorkerProtocol.KEY_CODE))
            val base = StableErrors.of(code, ErrorStage.EXPORT, data.getString(WorkerProtocol.KEY_DIAGNOSTIC))
            val reason = data.getString(WorkerProtocol.KEY_REASON) ?: return base
            return base.copy(params = base.params + (ErrorParams.REASON to reason))
        }

        /** The supervisor only needs to know that a DONE arrived; the real metadata comes from [accept]. */
        private fun placeholderMetadata() = VideoKitOutputMetadata("mp4", "mp4", null, null, 0, 0, 0, 0L, 0L, null, false)
    }

    /** How the worker process ended, from the system's exit records (API 30+). */
    private fun exitOf(pid: Int): WorkerSupervisor.Exit {
        if (pid <= 0) return WorkerSupervisor.Exit.UNKNOWN
        val manager = app.getSystemService(ActivityManager::class.java) ?: return WorkerSupervisor.Exit.UNKNOWN
        // The exit record can lag the binder death by a moment.
        var info: ApplicationExitInfo? = null
        var attempts = 0
        while (info == null && attempts++ < EXIT_INFO_ATTEMPTS) {
            info = runCatching { manager.getHistoricalProcessExitReasons(app.packageName, pid, 1).firstOrNull() }.getOrNull()
            if (info == null) Thread.sleep(EXIT_INFO_RETRY_MS)
        }
        if (info == null) return WorkerSupervisor.Exit.UNKNOWN
        return when (info.reason) {
            ApplicationExitInfo.REASON_CRASH,
            ApplicationExitInfo.REASON_CRASH_NATIVE,
            ApplicationExitInfo.REASON_ANR,
            -> WorkerSupervisor.Exit.CRASHED
            else -> WorkerSupervisor.Exit.KILLED
        }
    }

    public companion object {
        /** Default bound of one host read served to the worker (the source timeout of 14 §12). */
        public const val DEFAULT_READ_TIMEOUT_MS: Long = 10_000L

        private const val EXIT_INFO_ATTEMPTS = 3
        private const val EXIT_INFO_RETRY_MS = 100L
    }
}
