package com.videokit.spike.s4

import android.app.Activity
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.media.MediaExtractor
import android.media.MediaFormat
import android.os.Bundle
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Message
import android.os.Messenger
import android.os.ParcelFileDescriptor
import android.os.SystemClock
import android.util.Log
import android.view.SurfaceHolder
import android.view.SurfaceView
import android.view.WindowManager
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.MediaKind
import com.videokit.api.MediaProbeResult
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.OpenPurpose
import com.videokit.api.RecoveryDecision
import com.videokit.api.Seekability
import com.videokit.api.SessionPhase
import com.videokit.api.SupportLevel
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSourceFactory
import com.videokit.api.VideoKitStableError
import com.videokit.api.android.AndroidSurface
import com.videokit.core.CoreOptions
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.spi.CapabilityProbe
import com.videokit.core.spi.Clock
import com.videokit.core.spi.PlatformEngines
import com.videokit.core.spi.Scheduler
import com.videokit.media3.Media3PlaybackEngine
import com.videokit.playback.PlaybackVideoKit
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.util.concurrent.CopyOnWriteArrayList

/**
 * S4 driver (15 §4): plays a video through the Kit in this (main) process and runs one isolated export task per
 * fault. Start with `adb shell am start -n com.videokit.spike.s4/.S4Activity --es input dog.mp4 --es play cat.mp4
 * [--es faults NONE,CANCEL,SIGSEGV,OOM,LOOP,KILL]`; files are in the app's external files directory. Results:
 * `files/s4_results.jsonl` and logcat tag `S4RESULT`; the last line is `{"event":"done"}`.
 */
class S4Activity : Activity() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private lateinit var view: SurfaceView
    private var started = false
    private var loader = S4Protocol.LOADER_JAVA
    private var probe = true
    private val samples = CopyOnWriteArrayList<Triple<Long, Long, SessionPhase>>()
    private lateinit var out: File

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        view = SurfaceView(this)
        setContentView(view)
        view.holder.addCallback(
            object : SurfaceHolder.Callback {
                override fun surfaceCreated(holder: SurfaceHolder) = start()

                override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) = Unit

                override fun surfaceDestroyed(holder: SurfaceHolder) = Unit
            },
        )
    }

    private fun start() {
        if (started) return
        started = true
        val dir = getExternalFilesDir(null) ?: filesDir
        out = File(dir, "s4_results.jsonl").apply { delete() }
        val input = File(dir, intent.getStringExtra("input") ?: "input.mp4")
        val play = File(dir, intent.getStringExtra("play") ?: input.name)
        val faults = intent.getStringExtra("faults")?.split(',')?.map { S4Protocol.Fault.valueOf(it.trim()) } ?: S4Protocol.Fault.entries
        loader = intent.getStringExtra("loader") ?: S4Protocol.LOADER_JAVA
        // Attempt 4: the decode probe runs once, in the first task (before its export).
        probe = intent.getStringExtra("probe") != "false"
        scope.launch {
            val session = startPlayback(play)
            line("""{"event":"start","device":"${android.os.Build.MODEL}","sdk":${android.os.Build.VERSION.SDK_INT},"mainPid":${android.os.Process.myPid()},"input":"${input.name}","inputBytes":${input.length()},"playing":"${play.name}","playPhase":"${session?.state?.value?.phase}"}""")
            faults.forEachIndexed { index, fault -> runCatching { runTask(index, fault, input) }.onFailure { line("""{"event":"error","fault":"$fault","error":"${it::class.java.simpleName}"}""") } }
            val leftovers = cacheDir.listFiles { f -> f.name.startsWith("s4_out") }?.map { it.name }.orEmpty()
            line("""{"event":"done","mainPid":${android.os.Process.myPid()},"mainSessionPhase":"${session?.state?.value?.phase}","residue":${leftovers.size}}""")
        }
    }

    // ------------------------------------------------------------------ main process playback

    private suspend fun startPlayback(file: File): VideoKitSession? {
        val engines = PlatformEngines(Media3PlaybackEngine(this), NoProbe, SystemClocks, SpikeScheduler)
        val kit = PlaybackVideoKit.create(VideoKitConfig(QuietCallbacks, DefaultResourceBudget()), engines, CoreOptions())
        val session = kit.createSession(VideoKitSessionConfig())
        val surface = view.holder.surface
        session.attachSurface(AndroidSurface(surface, view.width, view.height))
        session.bind(localSource(file), VideoKitPlaybackState(looping = true), emptyList())
        session.execute(VideoKitCommand.SetLooping(true))
        session.execute(VideoKitCommand.Play)
        withTimeoutOrNull(30_000) { session.state.first { it.phase == SessionPhase.PLAYING } }
        scope.launch(Dispatchers.Default) {
            while (true) {
                val state = session.state.value
                samples += Triple(SystemClock.elapsedRealtime(), state.positionUs, state.phase)
                delay(SAMPLE_MS)
            }
        }
        return session
    }

    /** Longest time the main playback stood still while it should play, within [from, to]. */
    private fun maxStallMs(from: Long, to: Long): Long {
        var stall = 0L
        var lastMove = from
        var lastPosition = -1L
        for ((at, position, phase) in samples) {
            if (at < from || at > to) continue
            if (position != lastPosition || phase != SessionPhase.PLAYING) {
                lastPosition = position
                lastMove = at
            } else {
                stall = maxOf(stall, at - lastMove)
            }
        }
        return stall
    }

    // ------------------------------------------------------------------ one isolated export task

    private suspend fun runTask(index: Int, fault: S4Protocol.Fault, input: File) {
        val task = "s4_${fault.name.lowercase()}_$index"
        val output = File(cacheDir, "s4_out_$task.mp4").apply { delete() }
        val broker = InputBroker(input)
        val events = CopyOnWriteArrayList<Pair<Long, String>>()
        val terminal = CompletableDeferred<String>()
        val probeSteps = CopyOnWriteArrayList<String>()
        val withProbe = probe && index == 0
        val replyThread = HandlerThread("s4-replies-$task").apply { start() }
        var lastProgress = SystemClock.elapsedRealtime()
        var cancelSentAt = -1L
        var worker: Messenger? = null
        var workerBinder: IBinder? = null
        val replies = Messenger(
            Handler(replyThread.looper) { message ->
                val now = SystemClock.elapsedRealtime()
                lastProgress = now
                when (message.what) {
                    S4Protocol.STARTED -> events += now to "STARTED"

                    S4Protocol.PROBE -> message.data.getString(S4Protocol.KEY_CODE)?.takeIf { it != "probe=START" }?.let { probeSteps += it }

                    S4Protocol.SAMPLE -> if (message.data.getLong(S4Protocol.KEY_SAMPLES) == 1L) {
                        events += now to "FIRST_SAMPLE"
                        if (fault == S4Protocol.Fault.CANCEL) {
                            cancelSentAt = now
                            worker?.send(Message.obtain(null, S4Protocol.CANCEL))
                        }
                    }

                    S4Protocol.DONE -> terminal.complete("DONE")

                    S4Protocol.ERROR -> terminal.complete("ERROR:${message.data.getString(S4Protocol.KEY_CODE)}")

                    S4Protocol.CANCELLED -> terminal.complete("CANCELLED")
                }
                true
            },
        )
        val death = IBinder.DeathRecipient { terminal.complete("WORKER_DIED") }
        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName, service: IBinder) {
                workerBinder = service
                runCatching { service.linkToDeath(death, 0) }
                val messenger = Messenger(service)
                worker = messenger
                val pfd = ParcelFileDescriptor.open(
                    output,
                    ParcelFileDescriptor.MODE_READ_WRITE or ParcelFileDescriptor.MODE_CREATE or ParcelFileDescriptor.MODE_TRUNCATE,
                )
                val start = Message.obtain(null, S4Protocol.START).apply {
                    replyTo = replies
                    data = Bundle().apply {
                        putString(S4Protocol.KEY_TASK, task)
                        putBinder(S4Protocol.KEY_BROKER, broker)
                        putParcelable(S4Protocol.KEY_OUTPUT, pfd)
                        putString(S4Protocol.KEY_FAULT, fault.name)
                        putLong(S4Protocol.KEY_CLIP_MS, CLIP_MS)
                        putString(S4Protocol.KEY_LOADER, loader)
                        putBoolean(S4Protocol.KEY_PROBE, withProbe)
                    }
                }
                runCatching { messenger.send(start) }.onFailure { terminal.complete("SEND_FAILED") }
                // The worker holds its own duplicate of the descriptor now.
                runCatching { pfd.close() }
            }

            override fun onServiceDisconnected(name: ComponentName) {
                terminal.complete("DISCONNECTED")
            }
        }
        val t0 = SystemClock.elapsedRealtime()
        val bound = bindIsolatedService(Intent(this, ExportWorkerService::class.java), Context.BIND_AUTO_CREATE, task, mainExecutor, connection)
        if (!bound) terminal.complete("BIND_FAILED")
        // Watchdog: a worker without progress for HANG_MS is treated as hung (LOOP).
        val watchdog = scope.launch(Dispatchers.Default) {
            while (!terminal.isCompleted) {
                delay(250)
                if (SystemClock.elapsedRealtime() - lastProgress > HANG_MS) terminal.complete("HUNG")
            }
        }
        val outcome = withTimeoutOrNull(TASK_TIMEOUT_MS) { terminal.await() } ?: "TIMEOUT"
        val terminalAt = SystemClock.elapsedRealtime()
        watchdog.cancel()
        // Abort or keep the output (the main process owns it), revoke the input, stop the worker.
        val valid = if (outcome == "DONE") validate(output) else null
        val outputBytes = output.length()
        broker.revoke()
        runCatching { workerBinder?.unlinkToDeath(death, 0) }
        runCatching { unbindService(connection) }
        if (outcome != "DONE") output.delete()
        val aborted = outcome != "DONE" && !output.exists()
        if (outcome == "DONE") output.delete()
        replyThread.quitSafely()
        delay(POST_WINDOW_MS)
        val firstSample = events.firstOrNull { it.second == "FIRST_SAMPLE" }?.first
        val residue = cacheDir.listFiles { f -> f.name.startsWith("s4_out_$task") }?.size ?: 0
        line(
            """{"event":"task","task":"$task","fault":"$fault","loader":"$loader","outcome":"$outcome","totalMs":${terminalAt - t0},""" +
                """"firstSampleMs":${firstSample?.let { it - t0 } ?: -1},""" +
                """"detectMs":${if (firstSample != null && fault != S4Protocol.Fault.NONE) terminalAt - firstSample else -1},""" +
                """"cancelMs":${if (cancelSentAt > 0) terminalAt - cancelSentAt else -1},""" +
                """"outputBytesAtEnd":$outputBytes,"outputValid":${valid ?: "null"},"outputAborted":$aborted,"residue":$residue,""" +
                """"brokerReads":${broker.reads.get()},"brokerCalls":${broker.calls.get()},""" +
                """"probe":${if (withProbe) probeSteps.joinToString(",", "[", "]") { "\"$it\"" } else "null"},""" +
                """"mainPid":${android.os.Process.myPid()},"mainMaxStallMs":${maxStallMs(t0, terminalAt + POST_WINDOW_MS)}}""",
        )
    }

    /** A finished output is a playable MP4 with a video track and a duration. */
    private fun validate(file: File): String = runCatching {
        val extractor = MediaExtractor()
        try {
            extractor.setDataSource(file.absolutePath)
            val formats = (0 until extractor.trackCount).map { extractor.getTrackFormat(it) }
            val video = formats.firstOrNull { it.getString(MediaFormat.KEY_MIME)?.startsWith("video/") == true }
            val durationUs = video?.takeIf { it.containsKey(MediaFormat.KEY_DURATION) }?.getLong(MediaFormat.KEY_DURATION) ?: -1L
            """{"tracks":${formats.size},"video":${video != null},"durationUs":$durationUs}"""
        } finally {
            extractor.release()
        }
    }.getOrElse { "\"INVALID:${it::class.java.simpleName}\"" }

    private fun line(json: String) {
        Log.i(TAG, json)
        out.appendText(json + "\n")
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }

    private companion object {
        const val TAG = "S4RESULT"
        const val SAMPLE_MS = 100L
        const val CLIP_MS = 8_000L
        const val HANG_MS = 5_000L
        const val TASK_TIMEOUT_MS = 120_000L
        const val POST_WINDOW_MS = 2_000L
    }
}

private fun localSource(file: File): VideoKitMediaSource = VideoKitMediaSource(
    mediaToken = "s4-play",
    mediaKind = MediaKind.VIDEO,
    displayName = file.name,
    knownLength = file.length(),
    extension = file.extension,
    seekability = Seekability.RANDOM_ACCESS,
    sourceFactory = object : VideoKitSourceFactory {
        override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle = withContext(Dispatchers.IO) {
            val channel = RandomAccessFile(file, "r").channel
            object : VideoKitReadHandle {
                override val length: Long = file.length()

                override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int =
                    withContext(Dispatchers.IO) { channel.read(ByteBuffer.wrap(target, targetOffset, length), offset) }

                override fun close() {
                    runCatching { channel.close() }
                }
            }
        }
    },
)

private object NoProbe : CapabilityProbe {
    override suspend fun device(): VideoKitCapabilities = VideoKitCapabilities(suggestedHardwareVideoSessions = 4)

    override suspend fun media(source: VideoKitMediaSource): MediaProbeResult =
        MediaProbeResult(source.mediaToken, SupportLevel.SUPPORTED, SupportLevel.UNSUPPORTED)
}

private object SystemClocks : Clock {
    override fun monotonicUs(): Long = SystemClock.elapsedRealtimeNanos() / 1_000L

    override fun epochMs(): Long = System.currentTimeMillis()
}

private object SpikeScheduler : Scheduler {
    override val io: CoroutineDispatcher get() = Dispatchers.IO

    override val compute: CoroutineDispatcher get() = Dispatchers.Default

    @OptIn(ExperimentalCoroutinesApi::class)
    override fun serial(name: String): CoroutineDispatcher = Dispatchers.Default.limitedParallelism(1)
}

private object QuietCallbacks : VideoKitHostCallbacks {
    override suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult = HostActionResult(HostActionStatus.FAILED)

    override suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult = NavigationResult.UNAVAILABLE

    override suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState) = Unit

    override suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent) = Unit

    override suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean) = Unit

    override suspend fun onSourceReleased(sessionId: String, mediaToken: String) = Unit

    override suspend fun onRecoverableError(sessionId: String, error: VideoKitStableError): RecoveryDecision = RecoveryDecision.KEEP_ERROR

    override suspend fun onFatalSessionError(sessionId: String, error: VideoKitStableError) = Unit
}
