package com.videokit.playback

import com.videokit.api.SeekMode
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.CoreOptions
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeResourceBudget
import com.videokit.testkit.FakeScenario
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.ContinuationInterceptor
import kotlin.test.Test
import kotlin.test.assertEquals

/**
 * TEST-R5 R5-01a: with a long GOP a key frame seek lands away from the target. The session reports where the engine
 * landed (so the bar does not jump back on the next engine update), and an EXACT seek (the release of a drag, 14 §5)
 * lands on the target after any number of preview seeks.
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class SeekLandingTest {
    private val callbacks = RecordingHostCallbacks()

    private fun TestScope.kit() = run {
        val dispatcher = coroutineContext[ContinuationInterceptor] as CoroutineDispatcher
        val options = FakeEngineOptions(
            clock = FakeClock(),
            scenarioResolver = { FakeScenario.forSource(it).copy(keyframeIntervalUs = GOP_US) },
        )
        PlaybackVideoKit.create(
            VideoKitConfig(callbacks, FakeResourceBudget()),
            FakeEngines.platform(dispatcher, options),
            CoreOptions(isDemo = true),
            backgroundScope,
        )
    }

    @Test
    fun keyFrameSeeksReportTheLandedPosition() = runTest {
        val kit = kit()
        val session = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("long-gop"), null, emptyList()))
        // 7.4 s with a 4 s GOP: the closest key frame is 8 s; 5.9 s → 4 s.
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(7_400_000, SeekMode.CLOSEST_SYNC)))
        assertEquals(8_000_000L, session.state.value.positionUs)
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(5_900_000, SeekMode.PREVIEW)))
        assertEquals(4_000_000L, session.state.value.positionUs)
        runCurrent()
        val seek = callbacks.playbackEvents.filterIsInstance<VideoKitPlaybackEvent.UserSeek>().last()
        assertEquals(4_000_000L, seek.toUs, "the host is told the landed position")
        kit.close()
    }

    @Test
    fun releaseAfterPreviewSeeksLandsExactly() = runTest {
        val kit = kit()
        val session = kit.createSession(VideoKitSessionConfig())
        session.bind(FakeMediaSources.video("drag"), null, emptyList())
        listOf(1_000_000L, 2_500_000L, 3_700_000L, 5_300_000L).forEach {
            session.execute(VideoKitCommand.SeekTo(it, SeekMode.PREVIEW))
        }
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(5_300_000, SeekMode.EXACT)))
        assertEquals(5_300_000L, session.state.value.positionUs)
        kit.close()
    }

    private companion object {
        const val GOP_US = 4_000_000L
    }
}
