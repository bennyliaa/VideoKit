package com.videokit.spike.s1

import android.content.Context
import android.os.Debug
import android.os.SystemClock
import android.util.Log
import android.view.Surface
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.MediaProbeResult
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.SeekMode
import com.videokit.api.SessionPhase
import com.videokit.api.Size
import com.videokit.api.SupportLevel
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitStableError
import com.videokit.api.android.AndroidSurface
import com.videokit.core.CoreOptions
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.spi.CapabilityProbe
import com.videokit.core.spi.Clock
import com.videokit.core.spi.PlatformEngines
import com.videokit.core.spi.Scheduler
import com.videokit.media3.Media3EngineConfig
import com.videokit.media3.Media3PlaybackEngine
import com.videokit.media3.RetrieverFrameSource
import com.videokit.playback.PlaybackVideoKit
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import java.io.File

/** S1 measurement over the real Kit (CoreVideoKit + PlaybackSession + Media3PlaybackEngine + HostDataSource). */
class S1Bench(private val context: Context, private val surface: () -> Pair<Surface, Size>?, private val out: File) {
    suspend fun run(files: List<File>, conditions: List<Condition>, prefetchSizes: List<Int> = S1BenchDefaults.PREFETCH, reps: Int = 1) {
        line("""{"event":"start","device":"${android.os.Build.MODEL}","sdk":${android.os.Build.VERSION.SDK_INT},"files":${files.size}}""")
        for (file in files) {
            for (condition in conditions) {
                for (prefetch in prefetchSizes) for (rep in 1..reps) {
                    runCatching { playback(file, condition, prefetch, rep) }.onFailure {
                        line("""{"event":"error","file":"${file.name}","condition":"${condition.name}","prefetch":$prefetch,"error":"${it::class.java.simpleName}"}""")
                    }
                }
                runCatching { thumbnail(file, condition) }
            }
        }
        line("""{"event":"done"}""")
    }

    private fun kit(prefetch: Int): VideoKit {
        val engines = PlatformEngines(
            playback = Media3PlaybackEngine(context, Media3EngineConfig(prefetchBytes = prefetch)),
            capabilities = NoProbe,
            clock = SystemClocks,
            scheduler = SpikeScheduler,
            frames = RetrieverFrameSource(),
        )
        return PlaybackVideoKit.create(VideoKitConfig(QuietCallbacks, DefaultResourceBudget()), engines, CoreOptions())
    }

    private suspend fun playback(file: File, condition: Condition, prefetch: Int, rep: Int) {
        val kit = kit(prefetch)
        val host = SimulatedHostSource(file, condition)
        val source = host.mediaSource("s1-${file.name}")
        val session = kit.createSession(VideoKitSessionConfig())
        surface()?.let { (s, size) -> session.attachSurface(AndroidSurface(s, size.width, size.height)) }
        val pssBefore = Debug.getPss()
        var pssPeak = pssBefore
        val sampler = CoroutineScope(Dispatchers.Default).launch {
            while (true) {
                pssPeak = maxOf(pssPeak, Debug.getPss())
                delay(250)
            }
        }
        MainThreadWatch.takeAndReset()
        val t0 = SystemClock.elapsedRealtime()
        val bind = withTimeoutOrNull(STEP_MS) { session.bind(source, null, emptyList()) }
        val bindMs = SystemClock.elapsedRealtime() - t0
        val duration = session.state.value.durationUs ?: 0L
        var firstFrameMs = -1L
        var bindToFirstFrameMs = -1L
        var rebuffers = 0
        var rebufferMs = 0L
        val seeks = mutableListOf<String>()
        if (bind == VideoKitCommandResult.Executed) {
            val tPlay = SystemClock.elapsedRealtime()
            session.execute(VideoKitCommand.Play)
            // First frame: playing and the position advanced (15 §4 item 7: bind → first frame).
            withTimeoutOrNull(STEP_MS) { session.state.first { it.phase == SessionPhase.PLAYING && it.positionUs > 0L } }
                ?.let {
                    val now = SystemClock.elapsedRealtime()
                    firstFrameMs = now - tPlay
                    bindToFirstFrameMs = now - t0
                }
            val (count, ms) = watchBuffering(session, PLAY_WINDOW_MS)
            rebuffers += count
            rebufferMs += ms
            for ((label, fraction) in listOf("p25" to 0.25, "p50" to 0.5, "p90" to 0.9, "end" to -1.0)) for (mode in listOf(SeekMode.CLOSEST_SYNC, SeekMode.EXACT)) {
                val target = if (fraction < 0) (duration - 1_000_000L).coerceAtLeast(0L) else (duration * fraction).toLong()
                val ts = SystemClock.elapsedRealtime()
                val result = withTimeoutOrNull(STEP_MS) { session.execute(VideoKitCommand.SeekTo(target, mode)) }
                val seekMs = SystemClock.elapsedRealtime() - ts
                val resumed = withTimeoutOrNull(STEP_MS) {
                    session.state.first { it.phase == SessionPhase.PLAYING || it.phase == SessionPhase.ENDED || it.phase == SessionPhase.PAUSED }
                }
                val resumeMs = SystemClock.elapsedRealtime() - ts
                seeks += """{"at":"$label","mode":"$mode","result":"${result?.let { it::class.simpleName }}","seekMs":$seekMs,"resumeMs":$resumeMs,"phase":"${resumed?.phase}"}"""
                if (fraction < 0) continue
                val (c, m) = watchBuffering(session, SEEK_WATCH_MS)
                rebuffers += c
                rebufferMs += m
            }
            // Rapid seeks: five in a row, the older ones are superseded (04 §4.3).
            val rapid = (1..5).map { i -> CoroutineScope(Dispatchers.Default).async { session.execute(VideoKitCommand.SeekTo(duration * i / 10, SeekMode.PREVIEW)) } }
            val tr = SystemClock.elapsedRealtime()
            val results = withTimeoutOrNull(STEP_MS) { rapid.map { it.await() } }
            seeks += """{"at":"rapid5","superseded":${results?.count { it == VideoKitCommandResult.Superseded }},"settleMs":${SystemClock.elapsedRealtime() - tr}}"""
        }
        val tr = SystemClock.elapsedRealtime()
        session.release()
        val releaseMs = SystemClock.elapsedRealtime() - tr
        sampler.cancel()
        val (mainMaxBlockMs, mainBlocksOver16) = MainThreadWatch.takeAndReset()
        val cancel = cancelDuringOpen(kit, file, condition)
        kit.close()
        line(
            """{"event":"playback","file":"${file.name}","bytes":${file.length()},"condition":"${condition.name}","prefetch":$prefetch,"rep":$rep,""" +
                """"bind":"${bind?.let { it::class.simpleName } ?: "TIMEOUT"}","bindMs":$bindMs,"firstFrameMs":$firstFrameMs,"bindToFirstFrameMs":$bindToFirstFrameMs,""" +
                """"rebuffers":$rebuffers,"rebufferMs":$rebufferMs,"seeks":[${seeks.joinToString(",")}],"releaseMs":$releaseMs,""" +
                """"handlesAfterRelease":${host.openHandles.get()},"reads":${host.reads.get()},"readBytes":${host.bytes.get()},""" +
                """"maxReadMs":${host.maxReadMs.get()},"pssKbBefore":$pssBefore,"pssKbPeak":$pssPeak,"mainMaxBlockMs":$mainMaxBlockMs,"mainBlocksOver16ms":$mainBlocksOver16,"cancel":$cancel}""",
        )
    }

    /** Releases a session 300 ms into its open: how fast the open stops and whether every handle is closed. */
    private suspend fun cancelDuringOpen(kit: VideoKit, file: File, condition: Condition): String {
        val host = SimulatedHostSource(file, condition)
        val session = kit.createSession(VideoKitSessionConfig())
        val bind = CoroutineScope(Dispatchers.Default).async { session.bind(host.mediaSource("s1-cancel"), null, emptyList()) }
        delay(300)
        val t = SystemClock.elapsedRealtime()
        session.release()
        val result = withTimeoutOrNull(STEP_MS) { bind.await() }
        val ms = SystemClock.elapsedRealtime() - t
        delay(200)
        return """{"releaseMs":$ms,"bind":"${result?.let { it::class.simpleName } ?: "TIMEOUT"}","openHandles":${host.openHandles.get()}}"""
    }

    private suspend fun watchBuffering(session: VideoKitSession, windowMs: Long): Pair<Int, Long> {
        var count = 0
        var total = 0L
        var since = -1L
        val end = SystemClock.elapsedRealtime() + windowMs
        while (SystemClock.elapsedRealtime() < end) {
            val buffering = session.state.value.phase == SessionPhase.BUFFERING
            if (buffering && since < 0) {
                count++
                since = SystemClock.elapsedRealtime()
            } else if (!buffering && since >= 0) {
                total += SystemClock.elapsedRealtime() - since
                since = -1
            }
            delay(20)
        }
        if (since >= 0) total += SystemClock.elapsedRealtime() - since
        return count to total
    }

    /** Thumbnail at 50 % through MediaMetadataRetriever over the same host readAt (04A P1; 15 §2.4). */
    private suspend fun thumbnail(file: File, condition: Condition) {
        val host = SimulatedHostSource(file, condition)
        val source = host.mediaSource("s1-thumb")
        val t = SystemClock.elapsedRealtime()
        val result = withTimeoutOrNull(STEP_MS) {
            val reader = RetrieverFrameSource().open(source)
            try {
                // 30 s in (the retriever takes the nearest sync frame; shorter media clamp to their end).
                reader.thumbnailAt(30_000_000L, Size(320, 180))
            } finally {
                reader.close()
            }
        }
        val ms = SystemClock.elapsedRealtime() - t
        line(
            """{"event":"thumbnail","file":"${file.name}","condition":"${condition.name}","ms":$ms,""" +
                """"ok":${result is ThumbnailResult.Captured},"jpegBytes":${result?.bytes?.size ?: 0},"reads":${host.reads.get()},"openHandles":${host.openHandles.get()}}""",
        )
    }

    private fun line(json: String) {
        Log.i(TAG, json)
        out.appendText(json + "\n")
    }

    private companion object {
        const val TAG = "S1RESULT"
        const val STEP_MS = 60_000L
        const val PLAY_WINDOW_MS = 8_000L
        const val SEEK_WATCH_MS = 3_000L
    }
}

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
