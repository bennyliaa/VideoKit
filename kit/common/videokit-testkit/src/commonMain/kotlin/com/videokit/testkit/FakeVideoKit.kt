package com.videokit.testkit

import com.videokit.api.CapabilityRequest
import com.videokit.api.EditFeatures
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.ExportPreset
import com.videokit.api.FeatureKey
import com.videokit.api.FormatSupport
import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.ImageFeatures
import com.videokit.api.MediaKind
import com.videokit.api.MediaProbeResult
import com.videokit.api.OpenPurpose
import com.videokit.api.OutputFormat
import com.videokit.api.PlaybackFeatures
import com.videokit.api.ResourceBudget
import com.videokit.api.SerializedEditProject
import com.videokit.api.SinkRequirements
import com.videokit.api.Size
import com.videokit.api.SupportLevel
import com.videokit.api.TrackingModuleStatus
import com.videokit.api.TrackingStatus
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitApiVersion
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.AtomicFlag
import com.videokit.testkit.internal.AtomicMap
import com.videokit.testkit.internal.CallbackRunner
import com.videokit.testkit.internal.Errors
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout
import kotlin.time.Clock

/** Options of a [FakeVideoKit]. */
public data class FakeVideoKitOptions(
    /** Parent scope; tests pass `TestScope.backgroundScope`. Default: an own scope on [Dispatchers.Default]. */
    val scope: CoroutineScope? = null,
    /** Media clock shared by all sessions. */
    val clock: FakeClock = FakeClock(),
    /** Scenario per bound source; default [FakeScenario.forSource] (`demo:<name>` tokens). */
    val scenarioResolver: (VideoKitMediaSource) -> FakeScenario = FakeScenario::forSource,
    /** Resource budget. */
    val resourceBudget: ResourceBudget = FakeResourceBudget(),
    /** Host callback timeouts. */
    val callbackTimeouts: HostCallbackTimeouts = HostCallbackTimeouts(),
    /** Timeout of opening and reading a host source. */
    val sourceTimeoutMs: Long = 10_000L,
    /** Hard session limit (07 §3). */
    val maxSessions: Int = 12,
    /** Test pattern target per render target; `null` = the target type is not supported (nothing is drawn). Android: `AndroidTestPattern.targetFactory`. */
    val patternTargetFactory: (VideoKitSurfaceTarget) -> TestPatternTarget? = { null },
    /** Wall clock in epoch milliseconds (timestamps of snapshots and export results). */
    val wallClockMs: () -> Long = { Clock.System.now().toEpochMilliseconds() },
    /** Interval between test pattern frames (30 fps). */
    val renderIntervalMs: Long = 33L,
    /** Whether the demo tracking module reports as available. */
    val trackingAvailable: Boolean = true,
    /** Reported API version. */
    val apiVersion: VideoKitApiVersion = VideoKitApiVersion.CURRENT,
)

/**
 * Kotlin Fake of [VideoKit] (14 §2.2, §11): complete session state machine, in-memory edit projects,
 * scenario scripts, a controllable clock and a test pattern renderer. No media is decoded; sources are
 * only opened, probed (a few bytes) and closed so that host source behaviour is exercised.
 *
 * Every Fake reports [isDemo] = `true`.
 */
public class FakeVideoKit(
    hostCallbacks: VideoKitHostCallbacks,
    /** Options. */
    public val options: FakeVideoKitOptions = FakeVideoKitOptions(),
) : VideoKit {
    internal val scope: CoroutineScope = run {
        val parent = options.scope?.coroutineContext
        CoroutineScope((parent ?: Dispatchers.Default) + SupervisorJob(parent?.get(Job)) + CoroutineName("FakeVideoKit"))
    }
    internal val callbacks = CallbackRunner(scope, hostCallbacks, options.callbackTimeouts)
    private val closed = AtomicFlag()
    private val sessionIds = AtomicCounter()
    private val projectIds = AtomicCounter()
    private val sessions = AtomicMap<String, FakeSession>()
    private val projects = AtomicMap<String, FakeEditProject>()

    override val apiVersion: VideoKitApiVersion get() = options.apiVersion

    override val isDemo: Boolean get() = true

    /** The shared media clock. */
    public val clock: FakeClock get() = options.clock

    /** Live (not released) sessions. */
    public val activeSessions: List<FakeSession> get() = sessions.snapshot.values.toList()

    /** Number of failed or timed-out host callbacks so far. */
    public val callbackFailures: Int get() = callbacks.failures

    override suspend fun capabilities(request: CapabilityRequest): VideoKitCapabilities {
        val probe = request.source?.let { probe(it) }
        return demoCapabilities().copy(mediaProbe = probe)
    }

    override fun createSession(config: VideoKitSessionConfig): VideoKitSession {
        if (closed.value) throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.BIND, "VIDEOKIT_CLOSED"))
        if (sessions.snapshot.size >= options.maxSessions) {
            throw VideoKitException(
                Errors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "SESSION_LIMIT:${options.maxSessions}"),
            )
        }
        val id = "fake-session-" + sessionIds.incrementAndGet().toString().padStart(4, '0')
        return FakeSession(id, config, this).also { sessions.put(id, it) }
    }

    override fun createEditProject(config: EditProjectConfig): VideoKitEditProject {
        if (closed.value) throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, "VIDEOKIT_CLOSED"))
        return FakeEditProject(newProjectId(), config, this, restored = null).also { projects.put(it.projectId, it) }
    }

    override suspend fun restoreEditProject(serialized: SerializedEditProject, config: EditProjectConfig): VideoKitEditProject {
        if (closed.value) throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, "VIDEOKIT_CLOSED"))
        val model = ProjectCodec.decode(serialized)
        return FakeEditProject(model.projectId, config, this, restored = model).also { projects.put(it.projectId, it) }
    }

    override fun close() {
        if (!closed.setOnce()) return
        scope.launch {
            sessions.snapshot.values.toList().forEach { it.release() }
            projects.snapshot.values.toList().forEach { it.releaseAndAwait() }
            callbacks.close()
            scope.cancel()
        }
    }

    internal fun onSessionReleased(sessionId: String) {
        sessions.remove(sessionId)
    }

    internal fun onProjectReleased(projectId: String) {
        projects.remove(projectId)
    }

    internal fun newPreviewSession(): FakeSession {
        val id = "fake-session-" + sessionIds.incrementAndGet().toString().padStart(4, '0')
        return FakeSession(id, VideoKitSessionConfig(purpose = com.videokit.api.SessionPurpose.EDIT_PREVIEW), this)
            .also { sessions.put(id, it) }
    }

    private fun newProjectId(): String = "fake-project-" + projectIds.incrementAndGet().toString().padStart(4, '0')

    private suspend fun probe(source: VideoKitMediaSource): MediaProbeResult {
        val scenario = options.scenarioResolver(source)
        return try {
            withTimeout(options.sourceTimeoutMs) {
                val handle = source.sourceFactory.open(OpenPurpose.PROBE)
                try {
                    handle.readAt(0, ByteArray(PROBE_BYTES), 0, PROBE_BYTES)
                } finally {
                    handle.close()
                }
            }
            val playable = if (scenario.unsupportedVideoCodec &&
                source.mediaKind == MediaKind.VIDEO
            ) {
                SupportLevel.UNSUPPORTED
            } else {
                SupportLevel.SUPPORTED
            }
            MediaProbeResult(
                mediaToken = source.mediaToken,
                playable = playable,
                editable = if (source.mediaKind == MediaKind.VIDEO) playable else SupportLevel.UNSUPPORTED,
                fastConcatEligible = null,
                durationUs = if (source.mediaKind == MediaKind.VIDEO) scenario.durationUs else null,
                size = scenario.videoSize,
            )
        } catch (cancelled: CancellationException) {
            if (cancelled !is TimeoutCancellationException) throw cancelled
            failedProbe(source, Errors.fromSourceFailure(cancelled, ErrorStage.PROBE))
        } catch (failure: Exception) {
            failedProbe(source, Errors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
    }

    private fun failedProbe(source: VideoKitMediaSource, error: com.videokit.api.VideoKitStableError) = MediaProbeResult(
        mediaToken = source.mediaToken,
        playable = SupportLevel.UNSUPPORTED,
        editable = SupportLevel.UNSUPPORTED,
        error = error,
    )

    private fun demoCapabilities(): VideoKitCapabilities = VideoKitCapabilities(
        containerCodecSupport = listOf(
            FormatSupport(container = "mp4", videoCodec = "video/avc", level = SupportLevel.SUPPORTED),
            FormatSupport(container = "mkv", videoCodec = "video/hevc", level = SupportLevel.SUPPORTED),
            FormatSupport(
                container = "mkv",
                audioCodec = "audio/ac3",
                level = SupportLevel.PARTIAL,
                reason = UnsupportedReason.DEVICE_CAPABILITY,
            ),
            FormatSupport(
                container = "m2ts",
                videoCodec = "video/mpeg2",
                level = SupportLevel.UNSUPPORTED,
                reason = UnsupportedReason.DEVICE_CAPABILITY,
            ),
        ),
        suggestedHardwareVideoSessions = 4,
        maxSuggestedResolution = Size(3840, 2160),
        maxSuggestedFrameRate = 60,
        playbackFeatures = PlaybackFeatures(
            subtitles = SupportLevel.PARTIAL,
            audioTrackSelection = true,
            speeds = listOf(0.5f, 0.75f, 1f, 1.25f, 1.5f, 2f),
            exactSeek = true,
        ),
        imageFeatures = ImageFeatures(staticImages = true, animatedImages = true, largeImageTiling = true),
        editFeatures = EditFeatures(singleVideoClips = true, multiInputConcat = true, manualMasks = true),
        outputFormats = listOf(OutputFormat("mp4", "video/avc", "audio/mp4a-latm", ExportPreset.entries)),
        tracking = if (options.trackingAvailable) {
            TrackingStatus(TrackingModuleStatus.AVAILABLE, TrackingModuleStatus.AVAILABLE, Size(640, 360), 4)
        } else {
            TrackingStatus()
        },
        sinkRequirements = SinkRequirements(randomWriteOrFileDescriptor = true, sequentialFallbackAvailable = true),
        unavailableReasons = if (options.trackingAvailable) {
            emptyMap()
        } else {
            mapOf(
                FeatureKey.FACE_TRACKING to UnsupportedReason.MODULE_NOT_INSTALLED,
                FeatureKey.OBJECT_TRACKING to UnsupportedReason.MODULE_NOT_INSTALLED,
            )
        },
    )

    public companion object {
        private const val PROBE_BYTES = 64

        /** Creates a Fake from a [VideoKitConfig], taking its callbacks, budget and timeouts. */
        public fun fromConfig(config: VideoKitConfig, options: FakeVideoKitOptions = FakeVideoKitOptions()): FakeVideoKit = FakeVideoKit(
            config.hostCallbacks,
            options.copy(resourceBudget = config.resourceBudget, callbackTimeouts = config.callbackTimeouts),
        )
    }
}
