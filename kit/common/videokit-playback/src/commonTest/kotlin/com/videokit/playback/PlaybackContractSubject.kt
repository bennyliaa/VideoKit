package com.videokit.playback

import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.MediaKind
import com.videokit.api.SessionPhase
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.core.CoreOptions
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeResourceBudget
import com.videokit.testkit.FakeScenario
import com.videokit.testkit.contract.ContractFeature
import com.videokit.testkit.contract.VideoKitContractSubject
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.coroutines.yield
import kotlin.coroutines.ContinuationInterceptor

/**
 * The real runtime (CoreVideoKit + [PlaybackSession]) over the fake platform engines of the testkit, as a
 * [VideoKitContractSubject]: the same contract suite and `spec` vectors as the Kotlin Fake (12 §1.1 #2). Pass a
 * scope on the test dispatcher so that latencies and timeouts run on virtual time.
 *
 * Images run on the fake image engine; editing (VK-M4) is not implemented yet and its cases are reported as skipped.
 */
class PlaybackContractSubject(private val scope: CoroutineScope, val clock: FakeClock = FakeClock()) : VideoKitContractSubject {
    override val features: Set<ContractFeature> get() = setOf(ContractFeature.IMAGES)

    override val callbackTimeouts: HostCallbackTimeouts get() = HostCallbackTimeouts()

    override val sourceTimeoutMs: Long get() = CoreOptions().sourceTimeoutMs

    override fun create(callbacks: VideoKitHostCallbacks): VideoKit {
        val dispatcher = scope.coroutineContext[ContinuationInterceptor] as? CoroutineDispatcher ?: error("scope without dispatcher")
        val engines = FakeEngines.platform(dispatcher, FakeEngineOptions(clock = clock))
        val config = VideoKitConfig(hostCallbacks = callbacks, resourceBudget = FakeResourceBudget(), callbackTimeouts = callbackTimeouts)
        return PlaybackVideoKit.create(config, engines, CoreOptions(isDemo = true), parentScope = scope)
    }

    override fun playableVideo(token: String): VideoKitMediaSource = FakeMediaSources.video(token)

    override fun playableImage(token: String): VideoKitMediaSource = FakeMediaSources.image(token, MediaKind.IMAGE_STATIC)

    override fun playableAnimatedImage(token: String): VideoKitMediaSource = FakeMediaSources.image(token, MediaKind.IMAGE_ANIMATED)

    override suspend fun advanceMediaTime(us: Long) {
        clock.advanceUs(us)
        yield()
    }

    /** Binds the `demo:corrupt` scenario and plays across its corrupt position. */
    override suspend fun driveToFatalError(session: VideoKitSession): Boolean {
        val corruptAt = FakeScenario.named("corrupt")?.corruptAtUs ?: return false
        if (session.bind(FakeMediaSources.video("demo:corrupt"), null, emptyList()) != VideoKitCommandResult.Executed) return false
        session.execute(VideoKitCommand.SeekTo(corruptAt - 100_000L))
        session.execute(VideoKitCommand.Play)
        advanceMediaTime(500_000L)
        return withTimeoutOrNull(15_000L) { session.state.first { it.phase == SessionPhase.ERROR_FATAL } } != null
    }
}
