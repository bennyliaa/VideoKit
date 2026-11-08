package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.SessionPhase
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSessionConfig
import com.videokit.core.CoreOptions
import com.videokit.core.spi.FrameData
import com.videokit.core.spi.FrameReader
import com.videokit.core.spi.FrameSource
import com.videokit.core.spi.PixelFormat
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeResourceBudget
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.spi.FakeEngineOptions
import com.videokit.testkit.spi.FakeEngines
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.currentTime
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.coroutines.ContinuationInterceptor
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue

/**
 * 04A P5 (S1 finding): a thumbnail or seek preview frame whose extraction hangs (slow network source) ends after the
 * 3 s hard timeout with `Failed(SOURCE_TIMEOUT)`; the reader is closed, the session keeps playing and the next
 * thumbnail works. The platform extractor's own abort is covered by `AbortableReadsTest` (videokit-media3).
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class ThumbnailTimeoutTest {
    /** Frame source whose extraction hangs while [hang] is true (cooperatively, as the P5 contract requires). */
    private class HangingFrames : FrameSource {
        var hang = true
        var opened = 0
        var closed = 0

        override suspend fun open(source: VideoKitMediaSource): FrameReader {
            opened++
            return object : FrameReader {
                override suspend fun frameAt(timeUs: Long, maxSize: Size, format: PixelFormat): FrameData =
                    if (hang) awaitCancellation() else FrameData(1, 1, timeUs, format, ByteArray(4))

                override suspend fun thumbnailAt(timeUs: Long, maxSize: Size): ThumbnailResult.Captured =
                    if (hang) awaitCancellation() else ThumbnailResult.Captured(byteArrayOf(1, 2, 3), 16, 9)

                override fun close() {
                    closed++
                }
            }
        }
    }

    private fun TestScope.kit(frames: FrameSource) = run {
        val dispatcher = coroutineContext[ContinuationInterceptor] as CoroutineDispatcher
        val engines = FakeEngines.platform(dispatcher, FakeEngineOptions(clock = FakeClock())).copy(frames = frames)
        PlaybackVideoKit.create(
            VideoKitConfig(RecordingHostCallbacks(), FakeResourceBudget()),
            engines,
            CoreOptions(isDemo = true),
            backgroundScope,
        )
    }

    @Test
    fun hangingExtractionEndsAtTheHardTimeoutAndTheSessionKeepsPlaying() = runTest {
        val frames = HangingFrames()
        val kit = kit(frames)
        val session = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("slow-thumb"), null, emptyList()))
        session.execute(VideoKitCommand.Play)
        session.state.first { it.phase == SessionPhase.PLAYING }

        val startedAt = currentTime
        val pending = async { session.captureThumbnail(5_000_000, 160, 90) }
        advanceTimeBy(CoreOptions.DEFAULT_THUMBNAIL_TIMEOUT_MS - 1)
        runCurrent()
        assertTrue(!pending.isCompleted, "still waiting before the hard timeout")
        val failed = assertIs<ThumbnailResult.Failed>(pending.await())
        assertEquals(ErrorCode.SOURCE_TIMEOUT, failed.error.code)
        assertEquals(CoreOptions.DEFAULT_THUMBNAIL_TIMEOUT_MS, currentTime - startedAt)
        assertEquals(1, frames.closed, "the abandoned reader is closed")
        // The session is not blocked: commands still run and it keeps playing.
        assertEquals(VideoKitCommandResult.Executed, session.execute(VideoKitCommand.SeekTo(1_000_000)))
        assertEquals(SessionPhase.PLAYING, session.state.value.phase)

        // The next request (for example after the network recovered) works.
        frames.hang = false
        val captured = assertIs<ThumbnailResult.Captured>(session.captureThumbnail(6_000_000, 160, 90))
        assertEquals(16, captured.width)
        assertEquals(2, frames.opened)
        assertEquals(2, frames.closed)
        kit.close()
    }

    @Test
    fun releaseDuringAHangingThumbnailReturnsPromptly() = runTest {
        val frames = HangingFrames()
        val kit = kit(frames)
        val session = kit.createSession(VideoKitSessionConfig())
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("release-thumb"), null, emptyList()))
        val pending = async { session.captureThumbnail(0, 160, 90) }
        advanceTimeBy(500)
        runCurrent()
        val releasedAt = currentTime
        session.release()
        val result = assertIs<ThumbnailResult.Failed>(pending.await())
        assertEquals(ErrorCode.SESSION_RELEASED, result.error.code)
        assertTrue(currentTime - releasedAt < CoreOptions.DEFAULT_THUMBNAIL_TIMEOUT_MS, "release did not wait for the timeout")
        assertEquals(1, frames.closed)
        kit.close()
    }
}
