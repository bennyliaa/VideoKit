package com.videokit.testkit

import com.videokit.api.ActionPlacement
import com.videokit.api.ErrorCode
import com.videokit.api.HostIcon
import com.videokit.api.MediaKind
import com.videokit.api.RecoveryDecision
import com.videokit.api.ResourceKind
import com.videokit.api.SessionPhase
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSurfaceTarget
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import kotlin.test.fail

@OptIn(ExperimentalCoroutinesApi::class)
class FakeSessionScenarioTest {
    private val callbacks = RecordingHostCallbacks()

    private fun TestScope.kit(scenario: FakeScenario, options: FakeVideoKitOptions = FakeVideoKitOptions()): FakeVideoKit =
        FakeVideoKit(callbacks, options.copy(scope = backgroundScope, scenarioResolver = { scenario }))

    private suspend fun TestScope.ready(kit: FakeVideoKit, token: String = "v"): VideoKitSession {
        val session = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video(token), null, emptyList()))
        return session
    }

    private fun TestScope.advanceClock(kit: FakeVideoKit, us: Long) {
        kit.clock.advanceUs(us)
        runCurrent()
    }

    @Test
    fun slowLoadTakesTheConfiguredTime() = runTest {
        val kit = kit(FakeScenario.normal().slowLoad(3_000))
        val session = kit.createSession(VideoKitSessionConfig())
        val bind = backgroundScope.launch { session.bind(FakeMediaSources.video("slow"), null, emptyList()) }
        advanceTimeBy(2_900)
        runCurrent()
        assertEquals(SessionPhase.BINDING, session.state.value.phase)
        advanceTimeBy(200)
        runCurrent()
        assertEquals(SessionPhase.READY, session.state.value.phase)
        bind.join()
    }

    @Test
    fun bufferingEpisodeReturnsToPlaying() = runTest {
        val kit = kit(FakeScenario.normal().buffering(atUs = 2_000_000, forUs = 1_000_000))
        val session = ready(kit)
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 2_500_000)
        assertEquals(SessionPhase.BUFFERING, session.state.value.phase)
        assertEquals(2_000_000L, session.state.value.positionUs)
        advanceClock(kit, 1_000_000)
        assertEquals(SessionPhase.PLAYING, session.state.value.phase)
        advanceClock(kit, 500_000)
        assertEquals(2_500_000L, session.state.value.positionUs)
        settle()
        assertTrue(callbacks.playbackEvents.any { it is VideoKitPlaybackEvent.BufferingStarted })
        assertTrue(callbacks.playbackEvents.any { it is VideoKitPlaybackEvent.BufferingEnded })
    }

    @Test
    fun corruptMediaIsFatalAndReleasesTheSource() = runTest {
        val kit = kit(FakeScenario.normal().corrupt(atUs = 1_000_000))
        val factory = CountingSourceFactory()
        val session = kit.createSession(VideoKitSessionConfig())
        session.bind(FakeMediaSources.video("c", factory), null, emptyList())
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 2_000_000)
        assertEquals(SessionPhase.ERROR_FATAL, session.state.value.phase)
        assertEquals(ErrorCode.CORRUPT_MEDIA, session.state.value.error?.code)
        assertEquals(1_000_000L, session.state.value.positionUs)
        assertEquals(0, factory.openHandles)
        assertTrue(session.execute(VideoKitCommand.Play) is VideoKitCommandResult.Rejected)
        assertTrue(session.bind(FakeMediaSources.video("again"), null, emptyList()) is VideoKitCommandResult.Rejected)
        settle()
        assertEquals(ErrorCode.CORRUPT_MEDIA, callbacks.fatalErrors.single().code)
    }

    @Test
    fun disconnectIsRecoverableAndRetryRebindsOnce() = runTest {
        callbacks.recoveryAnswer = { RecoveryDecision.RETRY }
        val kit = kit(FakeScenario.normal().disconnect(atUs = 1_000_000))
        val session = ready(kit, "d")
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 1_500_000)
        settle()
        // RETRY re-binds the same source: the session is READY again at position 0.
        assertEquals(SessionPhase.READY, session.state.value.phase)
        assertEquals(1, callbacks.recoverableErrors.size)
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 1_500_000)
        settle()
        // Second failure: no further automatic retry (no retry loops, 07 §1).
        assertEquals(SessionPhase.ERROR_RECOVERABLE, session.state.value.phase)
        assertEquals(2, callbacks.recoverableErrors.size)
    }

    @Test
    fun unsupportedVideoCodecRejectsBind() = runTest {
        val kit = kit(FakeScenario.normal().unsupportedVideoCodec())
        val session = kit.createSession(VideoKitSessionConfig())
        val result = session.bind(FakeMediaSources.video("u"), null, emptyList())
        assertEquals(ErrorCode.UNSUPPORTED_VIDEO_CODEC, (result as VideoKitCommandResult.Rejected).error.code)
        assertFalse(session.state.value.resourcesHeld)
    }

    @Test
    fun unsupportedAudioPlaysSilentlyWithNotice() = runTest {
        val kit = kit(FakeScenario.normal().unsupportedAudioCodec())
        val session = kit.createSession(VideoKitSessionConfig())
        val events = mutableListOf<VideoKitEvent>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { session.events.toList(events) }
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("a"), null, emptyList()))
        assertTrue(session.state.value.audioTracks.none { it.supported })
        assertEquals(null, session.state.value.selectedAudioTrackId)
        assertTrue(events.contains(VideoKitEvent.TransientNotice("AUDIO_UNSUPPORTED_PLAYING_SILENT")))
        assertEquals(
            VideoKitCommandResult.Unsupported(UnsupportedReason.FORMAT),
            session.execute(VideoKitCommand.SelectAudioTrack(session.state.value.audioTracks.first().id)),
        )
    }

    @Test
    fun resourceBudgetDenialIsRecoverable() = runTest {
        val budget = FakeResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to 1))
        val kit = kit(FakeScenario.normal(), FakeVideoKitOptions(resourceBudget = budget))
        val first = ready(kit, "one")
        val second = kit.createSession(VideoKitSessionConfig())
        val denied = second.bind(FakeMediaSources.video("two"), null, emptyList())
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, (denied as VideoKitCommandResult.Rejected).error.code)
        assertEquals(SessionPhase.ERROR_RECOVERABLE, second.state.value.phase)
        first.release()
        assertEquals(0, budget.held(ResourceKind.VIDEO_DECODER))
        assertEquals(VideoKitCommandResult.Executed, second.bind(FakeMediaSources.video("two"), null, emptyList()))
        assertEquals(1, budget.held(ResourceKind.VIDEO_DECODER))
    }

    @Test
    fun imageSessionsDoNotUseDecoderBudget() = runTest {
        val budget = FakeResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to 0))
        val kit = kit(FakeScenario.normal(), FakeVideoKitOptions(resourceBudget = budget))
        val session = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.image("img"), null, emptyList()))
        assertEquals(VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND), session.execute(VideoKitCommand.Play))
    }

    @Test
    fun animatedImageLoops() = runTest {
        val kit = kit(FakeScenario.normal())
        val session = kit.createSession(VideoKitSessionConfig())
        session.bind(FakeMediaSources.image("gif", MediaKind.IMAGE_ANIMATED), null, emptyList())
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Play))
        advanceClock(kit, 2_500_000)
        assertEquals(SessionPhase.PLAYING, session.state.value.phase)
        assertEquals(500_000L, session.state.value.positionUs)
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.Pause))
        assertEquals(SessionPhase.PAUSED, session.state.value.phase)
    }

    @Test
    fun hostActionTimeoutScenario() = runTest {
        val kit = kit(FakeScenario.normal().hostActionTimeout("delete"))
        val session = kit.createSession(VideoKitSessionConfig())
        val delete = VideoKitHostAction("delete", "delete", "delete", HostIcon.BuiltIn("delete"), placement = ActionPlacement.OVERFLOW)
        session.bind(FakeMediaSources.video("h"), null, listOf(delete))
        val started = testScheduler.currentTime
        val result = session.requestHostAction("delete")
        assertEquals(ErrorCode.HOST_CALLBACK_FAILED, (result as VideoKitCommandResult.Rejected).error.code)
        assertEquals(10_000L, testScheduler.currentTime - started)
        assertTrue(callbacks.hostActionRequests.isEmpty())
    }

    @Test
    fun speedScalesPositionAdvance() = runTest {
        val kit = kit(FakeScenario.normal())
        val session = ready(kit)
        session.execute(VideoKitCommand.SetSpeed(2f))
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 1_000_000)
        assertEquals(2_000_000L, session.state.value.positionUs)
    }

    @Test
    fun watchTimeOnlyAccumulatesWhileVisible() = runTest {
        val kit = kit(FakeScenario.normal())
        val session = ready(kit)
        session.execute(VideoKitCommand.Play)
        advanceClock(kit, 1_000_000)
        session.execute(VideoKitCommand.SetVisibility(com.videokit.api.Visibility.OFFSCREEN))
        advanceClock(kit, 3_000_000)
        settle()
        val watched = callbacks.playbackEvents.filterIsInstance<VideoKitPlaybackEvent.WatchTimeAccumulated>().sumOf { it.deltaUs }
        assertEquals(1_000_000L, watched)
    }

    @Test
    fun sessionLimitIsEnforced() = runTest {
        val kit = kit(FakeScenario.normal(), FakeVideoKitOptions(maxSessions = 2))
        val a = kit.createSession(VideoKitSessionConfig())
        kit.createSession(VideoKitSessionConfig())
        try {
            kit.createSession(VideoKitSessionConfig())
            fail("expected VideoKitException")
        } catch (expected: VideoKitException) {
            assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, expected.error.code)
        }
        a.release()
        kit.createSession(VideoKitSessionConfig())
    }

    @Test
    fun surfaceRendersTestPatternUntilDetached() = runTest {
        val frames = mutableListOf<TestPatternFrame>()
        var released = 0
        val target = object : TestPatternTarget {
            override fun draw(frame: TestPatternFrame): Boolean = frames.add(frame)

            override fun release() {
                released++
            }
        }
        val kit = kit(FakeScenario.normal(), FakeVideoKitOptions(patternTargetFactory = { target }))
        val session = ready(kit) as FakeSession
        // A platform independent render target; the injected pattern target does the drawing.
        session.attachSurface(TestTarget(640, 360))
        assertTrue(session.hasSurface)
        advanceTimeBy(100)
        runCurrent()
        assertTrue(frames.size >= 3)
        assertEquals(640, frames.first().width)
        assertEquals(TestPattern.sessionTag(session.sessionId), frames.first().sessionTag)
        session.execute(VideoKitCommand.HideContentForLock(true))
        val whileHidden = frames.size
        advanceTimeBy(100)
        runCurrent()
        assertEquals(whileHidden, frames.size)
        session.detachSurface()
        assertEquals(1, released)
        session.release()
        assertFalse(session.hasSurface)
        assertTrue(session.renderedFrames >= 3)
    }

    @Test
    fun closeReleasesAsynchronously() = runTest {
        val kit = kit(FakeScenario.normal())
        val session = ready(kit)
        session.close()
        settle()
        assertEquals(SessionPhase.RELEASED, session.state.value.phase)
        assertEquals(VideoKitCommandResult.SessionReleased, session.execute(VideoKitCommand.Play))
    }

    @Test
    fun demoTokensSelectNamedScenarios() {
        FakeScenario.NAMES.forEach { name -> assertEquals(true, FakeScenario.named(name) != null) }
        val source = FakeMediaSources.video("demo:corrupt:clip-7")
        assertEquals(45_000_000L, FakeScenario.forSource(source).corruptAtUs)
        assertEquals("normal", FakeScenario.forSource(FakeMediaSources.video("plain")).name)
        assertEquals("normal", FakeScenario.forSource(FakeMediaSources.video("demo:unknown")).name)
    }

    @Test
    fun releasedSessionKeepsFinalSnapshot() = runTest {
        val kit = kit(FakeScenario.normal())
        val session = ready(kit, "final")
        session.execute(VideoKitCommand.SeekTo(5_000_000))
        val snapshot = session.release()
        assertEquals(5_000_000L, snapshot.positionUs)
        assertEquals(snapshot, session.captureState())
        assertTrue(kit.isDemo && session.isDemo)
    }
}

private class TestTarget(override val width: Int, override val height: Int) : VideoKitSurfaceTarget
