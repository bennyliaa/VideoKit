package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.SessionPhase
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.CoreOptions
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeResourceBudget
import com.videokit.testkit.FakeScenario
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import com.videokit.testkit.spi.FakePlaybackEngine
import com.videokit.testkit.spi.FakeRenderTarget
import kotlinx.coroutines.CoroutineDispatcher
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
import kotlin.test.assertSame
import kotlin.test.assertTrue

/**
 * TEST-R2 R2-03: a configuration change (rotation) while a media is opening. The surface is destroyed and recreated,
 * the session is not released and the open continues; an open that is released or that cannot finish always ends in
 * a terminal state (never stays BINDING).
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class OpenLifecycleTest {
    private fun TestScope.kit(loadDelayMs: Long) = run {
        val dispatcher = coroutineContext[ContinuationInterceptor] as CoroutineDispatcher
        val engines = FakeEngines.platform(
            dispatcher,
            FakeEngineOptions(clock = FakeClock(), scenarioResolver = { FakeScenario.normal().slowLoad(loadDelayMs) }),
        )
        engines to
            PlaybackVideoKit.create(
                VideoKitConfig(RecordingHostCallbacks(), FakeResourceBudget()),
                engines,
                CoreOptions(isDemo = true),
                backgroundScope,
            )
    }

    @Test
    fun surfaceRecreatedDuringOpenKeepsTheSession() = runTest {
        val (engines, kit) = kit(loadDelayMs = 3_000L)
        val session = kit.createSession(VideoKitSessionConfig())
        session.attachSurface(FakeRenderTarget(1080, 1920))
        val bind = async { session.bind(FakeMediaSources.video("rotate"), null, emptyList()) }
        advanceTimeBy(1_000L)
        runCurrent()
        assertEquals(SessionPhase.BINDING, session.state.value.phase)
        // Rotation: Flutter destroys the surface, then provides a new one with the new size.
        session.detachSurface()
        val landscape = FakeRenderTarget(1920, 1080)
        assertEquals(VideoKitCommandResult.Executed, session.attachSurface(landscape))
        assertEquals(VideoKitCommandResult.Executed, bind.await())
        val ready = session.state.first { it.phase == SessionPhase.READY }
        assertTrue(ready.resourcesHeld)
        // The opened engine draws into the new surface.
        assertSame(landscape, (engines.playback as FakePlaybackEngine).lastOpened?.target)
        kit.close()
    }

    @Test
    fun releasedDuringOpenEndsReleased() = runTest {
        val (engines, kit) = kit(loadDelayMs = 3_000L)
        val session = kit.createSession(VideoKitSessionConfig())
        val bind = async { session.bind(FakeMediaSources.video("released"), null, emptyList()) }
        advanceTimeBy(1_000L)
        runCurrent()
        session.release()
        assertEquals(VideoKitCommandResult.SessionReleased, bind.await())
        assertEquals(SessionPhase.RELEASED, session.state.value.phase)
        assertEquals(0, (engines.playback as FakePlaybackEngine).openHandles)
        kit.close()
    }

    @Test
    fun openSlowerThanTheTimeoutEndsWithAStableError() = runTest {
        val (engines, kit) = kit(loadDelayMs = CoreOptions().sourceTimeoutMs + 5_000L)
        val session = kit.createSession(VideoKitSessionConfig())
        val result = assertIs<VideoKitCommandResult.Rejected>(session.bind(FakeMediaSources.video("slow"), null, emptyList()))
        assertEquals(ErrorCode.SOURCE_TIMEOUT, result.error.code)
        assertEquals(SessionPhase.ERROR_RECOVERABLE, session.state.value.phase)
        assertTrue(!session.state.value.resourcesHeld)
        assertEquals(0, (engines.playback as FakePlaybackEngine).openHandles)
        kit.close()
    }
}
