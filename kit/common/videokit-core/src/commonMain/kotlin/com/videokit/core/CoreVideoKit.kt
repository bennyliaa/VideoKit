package com.videokit.core

import com.videokit.api.CapabilityRequest
import com.videokit.api.EditFeatures
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.FeatureKey
import com.videokit.api.ImageFeatures
import com.videokit.api.MediaProbeResult
import com.videokit.api.ResourceBudget
import com.videokit.api.SerializedEditProject
import com.videokit.api.SupportLevel
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitApiVersion
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitStableError
import com.videokit.core.runtime.AtomicCounter
import com.videokit.core.runtime.AtomicFlag
import com.videokit.core.runtime.AtomicMap
import com.videokit.core.runtime.HostCallbackRunner
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.PlatformEngines
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineName
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout

/** Options of the core runtime. */
public data class CoreOptions(
    /** Hard session limit (07 §3, 04A I18). */
    val maxSessions: Int = 12,
    /** Timeout of opening and preparing a host source (bind) and of a capability probe. */
    val sourceTimeoutMs: Long = 10_000L,
    /** Reported API version. */
    val apiVersion: VideoKitApiVersion = VideoKitApiVersion.CURRENT,
    /** Whether the engines serve demo data (test engines); the UI then shows the demo badge (04A I6). */
    val isDemo: Boolean = false,
    /** Off-screen time after which a session releases its decoder (07 §5.3, [com.videokit.core.runtime.VisibilityPolicy]). */
    val offscreenReleaseMs: Long = com.videokit.core.runtime.VisibilityPolicy.DEFAULT_OFFSCREEN_RELEASE_MS,
    /** Background time after which a session releases its decoder. */
    val backgroundReleaseMs: Long = com.videokit.core.runtime.VisibilityPolicy.DEFAULT_BACKGROUND_RELEASE_MS,
)

/** Creates the media sessions of a [CoreVideoKit] (implemented by `videokit-playback`). */
public fun interface SessionFactory {
    /** Creates the session described by [context]. */
    public fun create(context: SessionContext): VideoKitSession
}

/** Everything a session needs from its [CoreVideoKit]. */
public class SessionContext internal constructor(
    /** Opaque session id. */
    public val sessionId: String,
    /** Configuration. */
    public val config: VideoKitSessionConfig,
    /** Shared runtime. */
    public val runtime: CoreRuntime,
)

/** Runtime shared by all sessions of one [CoreVideoKit]. */
public class CoreRuntime internal constructor(
    /** Parent scope of the sessions; cancelled when the kit is closed. */
    public val scope: CoroutineScope,
    /** Host callbacks with timeouts and isolation. */
    public val callbacks: HostCallbackRunner,
    /** Host-scoped resource budget. */
    public val budget: ResourceBudget,
    /** Platform engines. */
    public val engines: PlatformEngines,
    /** Options. */
    public val options: CoreOptions,
    private val onReleased: (String) -> Unit,
) {
    /** A session reports that it is released (it leaves the session count). */
    public fun sessionReleased(sessionId: String) {
        onReleased(sessionId)
    }
}

/**
 * The real [VideoKit] (02 §4.0 `videokit-core`): sessions, capability negotiation and the resource budget over
 * injected platform engines (02 §4.2). Platforms assemble it (Android: `VideoKitFactory`); tests assemble it with
 * the fake engines of `videokit-testkit`.
 *
 * Editing and export arrive in VK-M4: until then [createEditProject] and [restoreEditProject] throw and the
 * capability report marks the features as not implemented.
 */
public class CoreVideoKit(
    config: VideoKitConfig,
    private val engines: PlatformEngines,
    private val sessionFactory: SessionFactory,
    private val options: CoreOptions = CoreOptions(),
    parentScope: CoroutineScope? = null,
) : VideoKit {
    private val scope: CoroutineScope = run {
        val parent = parentScope?.coroutineContext
        CoroutineScope((parent ?: engines.scheduler.compute) + SupervisorJob(parent?.get(Job)) + CoroutineName("VideoKit"))
    }
    private val callbacks = HostCallbackRunner(scope, config.hostCallbacks, config.callbackTimeouts)
    private val closed = AtomicFlag()
    private val sessionIds = AtomicCounter()
    private val sessions = AtomicMap<String, VideoKitSession>()
    private val runtime = CoreRuntime(scope, callbacks, config.resourceBudget, engines, options) { sessions.remove(it) }

    override val apiVersion: VideoKitApiVersion get() = options.apiVersion

    override val isDemo: Boolean get() = options.isDemo

    /** Live (not released) sessions. */
    public val activeSessions: List<VideoKitSession> get() = sessions.snapshot.values.toList()

    /** Number of failed or timed-out host callbacks so far (diagnostics). */
    public val callbackFailures: Int get() = callbacks.failures

    override suspend fun capabilities(request: CapabilityRequest): VideoKitCapabilities {
        val device = CapabilityNegotiation.effective(engines.capabilities.device(), engines, options.isDemo)
        val probe = request.source?.let { probe(it) }
        return device.copy(mediaProbe = probe)
    }

    override fun createSession(config: VideoKitSessionConfig): VideoKitSession {
        if (closed.value) throw VideoKitException(StableErrors.of(ErrorCode.SESSION_RELEASED, ErrorStage.BIND, "VIDEOKIT_CLOSED"))
        if (sessions.snapshot.size >= options.maxSessions) {
            throw VideoKitException(
                StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "SESSION_LIMIT:${options.maxSessions}"),
            )
        }
        val id = "session-" + sessionIds.incrementAndGet().toString().padStart(4, '0')
        return sessionFactory.create(SessionContext(id, config, runtime)).also { sessions.put(id, it) }
    }

    override fun createEditProject(config: EditProjectConfig): VideoKitEditProject = throw editingUnavailable()

    override suspend fun restoreEditProject(serialized: SerializedEditProject, config: EditProjectConfig): VideoKitEditProject =
        throw editingUnavailable()

    override fun close() {
        if (!closed.setOnce()) return
        scope.launch {
            sessions.snapshot.values.toList().forEach { session -> runCatching { session.release() } }
            callbacks.close()
            scope.cancel()
        }
    }

    private fun editingUnavailable(): VideoKitException {
        val code = if (closed.value) ErrorCode.SESSION_RELEASED else ErrorCode.INVALID_STATE
        return VideoKitException(StableErrors.of(code, ErrorStage.EDIT, "EDITING_NOT_AVAILABLE"))
    }

    private suspend fun probe(source: VideoKitMediaSource): MediaProbeResult = try {
        withTimeout(options.sourceTimeoutMs) { engines.capabilities.media(source) }
    } catch (timeout: TimeoutCancellationException) {
        failedProbe(source, StableErrors.fromSourceFailure(timeout, ErrorStage.PROBE))
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (failure: SpiException) {
        failedProbe(source, failure.error)
    } catch (failure: Exception) {
        failedProbe(source, StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
    }

    private fun failedProbe(source: VideoKitMediaSource, error: VideoKitStableError) = MediaProbeResult(
        mediaToken = source.mediaToken,
        playable = SupportLevel.UNSUPPORTED,
        editable = SupportLevel.UNSUPPORTED,
        error = error,
    )
}

/**
 * Capability negotiation (02 §4.0 `videokit-core`): the device report of the platform probe, reduced to what the
 * assembled engines can actually do in this build, with a reason for every unavailable feature (04 §10).
 */
public object CapabilityNegotiation {
    /** Effective capabilities of [device] given the available [engines]. */
    public fun effective(device: VideoKitCapabilities, engines: PlatformEngines, isDemo: Boolean): VideoKitCapabilities {
        val reasons = device.unavailableReasons.toMutableMap()
        var result = device
        if (engines.images == null) {
            result = result.copy(imageFeatures = ImageFeatures())
            listOf(FeatureKey.IMAGE_STATIC, FeatureKey.IMAGE_ANIMATED, FeatureKey.IMAGE_LARGE_TILING)
                .forEach { reasons.addDefault(it, UnsupportedReason.NOT_IMPLEMENTED) }
        }
        // Editing, export and tracking need the timeline/export runtime of VK-M4–M6.
        result = result.copy(editFeatures = EditFeatures(), outputFormats = emptyList())
        listOf(FeatureKey.EDIT_CLIPS, FeatureKey.EDIT_CONCAT, FeatureKey.MANUAL_MASK, FeatureKey.EXPORT)
            .forEach { reasons.addDefault(it, UnsupportedReason.NOT_IMPLEMENTED) }
        if (engines.tracker == null) {
            listOf(FeatureKey.FACE_TRACKING, FeatureKey.OBJECT_TRACKING)
                .forEach { reasons.addDefault(it, UnsupportedReason.MODULE_NOT_INSTALLED) }
        }
        return result.copy(unavailableReasons = reasons, isDemo = isDemo || device.isDemo)
    }
}

private fun MutableMap<FeatureKey, UnsupportedReason>.addDefault(key: FeatureKey, reason: UnsupportedReason) {
    if (key !in this) this[key] = reason
}
