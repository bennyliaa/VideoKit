package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.NoticeCodes
import com.videokit.api.ResourceKind
import com.videokit.api.SessionPhase
import com.videokit.api.SessionVisibility
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.CoreOptions
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.runtime.ResourcePressure
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import com.videokit.testkit.spi.FakePlaybackEngine
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.ContinuationInterceptor
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue

/** Audio focus, budget calibration and pressure on the real session (07 §2–§4, 04A K1). */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class MultiInstanceSessionTest {
    private fun TestScope.rig(budget: DefaultResourceBudget, engines: com.videokit.core.spi.PlatformEngines? = null) = run {
        val dispatcher = coroutineContext[ContinuationInterceptor] as CoroutineDispatcher
        val platform = engines ?: FakeEngines.platform(dispatcher, FakeEngineOptions(clock = FakeClock()))
        platform to
            PlaybackVideoKit.create(VideoKitConfig(RecordingHostCallbacks(), budget), platform, CoreOptions(isDemo = true), backgroundScope)
    }

    private fun TestScope.settle() {
        advanceTimeBy(1_000L)
        runCurrent()
    }

    @Test
    fun audioFocusLossPausesAndNotifies() = runTest {
        val (engines, kit) = rig(DefaultResourceBudget())
        val session = kit.createSession(VideoKitSessionConfig())
        session.bind(FakeMediaSources.video("focus"), null, emptyList())
        session.state.first { it.phase == SessionPhase.READY }
        session.execute(VideoKitCommand.Play)
        val notice = async(start = CoroutineStart.UNDISPATCHED) { session.events.first { it is VideoKitEvent.TransientNotice } }
        (engines.playback as FakePlaybackEngine).lastOpened!!.loseAudioFocus()
        assertEquals(VideoKitEvent.TransientNotice(NoticeCodes.AUDIO_FOCUS_LOST), notice.await())
        val paused = session.state.first { it.phase == SessionPhase.PAUSED }
        assertTrue(!paused.playWhenReady)
        // Playing again is the user's decision.
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play))
        kit.close()
    }

    @Test
    fun failedDecoderCreationCalibratesTheBudget() = runTest {
        val budget = DefaultResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to 6))
        val dispatcher = coroutineContext[ContinuationInterceptor] as CoroutineDispatcher
        val base = FakeEngines.platform(dispatcher, FakeEngineOptions(clock = FakeClock()))
        val (_, kit) = rig(budget, base)
        repeat(2) { index ->
            val session = kit.createSession(VideoKitSessionConfig())
            assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("ok-$index"), null, emptyList()))
        }
        // The device cannot create the third decoder (scenario resourceExhausted throws DECODER_RESOURCE_EXHAUSTED).
        val third = kit.createSession(VideoKitSessionConfig())
        val failed =
            assertIs<VideoKitCommandResult.Rejected>(third.bind(FakeMediaSources.video("demo:resourceExhausted"), null, emptyList()))
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, failed.error.code)
        assertEquals(2, budget.effectiveLimit(ResourceKind.VIDEO_DECODER))
        assertEquals(2, budget.snapshot().usages.single { it.kind == ResourceKind.VIDEO_DECODER }.held)
        kit.close()
    }

    @Test
    fun deniedResumeIsDegradedNotRetried() = runTest {
        val budget = DefaultResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to 1))
        val (_, kit) = rig(budget)
        val hidden = kit.createSession(VideoKitSessionConfig())
        hidden.bind(FakeMediaSources.video("hidden"), null, emptyList())
        hidden.state.first { it.phase == SessionPhase.READY }
        hidden.execute(VideoKitCommand.SetVisibility(SessionVisibility.OFFSCREEN))
        advanceTimeBy(CoreOptions().offscreenReleaseMs + 1_000L)
        runCurrent()
        assertTrue(!hidden.state.value.resourcesHeld)
        val other = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, other.bind(FakeMediaSources.video("other"), null, emptyList()))
        val notice = async(start = CoroutineStart.UNDISPATCHED) { hidden.events.first { it is VideoKitEvent.TransientNotice } }
        hidden.execute(VideoKitCommand.SetVisibility(SessionVisibility.VISIBLE))
        assertEquals(VideoKitEvent.TransientNotice(NoticeCodes.RESOURCE_DEGRADED), notice.await())
        settle()
        assertTrue(!hidden.state.value.resourcesHeld, "no retry loop took the decoder")
        assertEquals(1, budget.snapshot().usages.single { it.kind == ResourceKind.VIDEO_DECODER }.held)
        kit.close()
    }

    @Test
    fun criticalPressureStopsThumbnails() = runTest {
        val budget = DefaultResourceBudget()
        val (_, kit) = rig(budget)
        val session = kit.createSession(VideoKitSessionConfig())
        session.bind(FakeMediaSources.video("thumbs"), null, emptyList())
        session.state.first { it.phase == SessionPhase.READY }
        assertIs<ThumbnailResult.Captured>(session.captureThumbnail(0, 160, 90))
        budget.setPressure(ResourcePressure.CRITICAL)
        val refused = assertIs<ThumbnailResult.Failed>(session.captureThumbnail(0, 160, 90))
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, refused.error.code)
        budget.setPressure(ResourcePressure.NORMAL)
        assertIs<ThumbnailResult.Captured>(session.captureThumbnail(0, 160, 90))
        kit.close()
    }
}
