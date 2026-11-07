package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.SessionPhase
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSessionConfig
import com.videokit.testkit.DemoThumbnail
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.RecordingHostCallbacks
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/** 04A P1 (thumbnails), P2 (media info) and L3 (looping in snapshots) on the real session over the fake engines. */
class PlaybackSessionFeaturesTest {
    @Test
    fun mediaInfoAfterBindAndThumbnails() = runTest {
        val kit = PlaybackContractSubject(backgroundScope).create(RecordingHostCallbacks())
        val session = kit.createSession(VideoKitSessionConfig())
        val early = assertIs<ThumbnailResult.Failed>(session.captureThumbnail(0, 160, 90))
        assertEquals(ErrorCode.INVALID_STATE, early.error.code)
        assertEquals(VideoKitCommandResult.Executed, session.bind(FakeMediaSources.video("info"), null, emptyList()))
        session.state.first { it.phase == SessionPhase.READY }
        val info = assertNotNull(session.state.value.mediaInfo)
        assertEquals("video/avc", info.videoCodec)
        assertEquals(1920, info.width)
        val captured = assertIs<ThumbnailResult.Captured>(session.captureThumbnail(5_000_000, 160, 90))
        assertEquals(DemoThumbnail.WIDTH, captured.width)
        assertEquals(0xFF.toByte(), captured.bytes[0])
        assertIs<ThumbnailResult.Failed>(session.captureThumbnail(-1, 160, 90))
        session.release()
        assertEquals(ErrorCode.SESSION_RELEASED, assertIs<ThumbnailResult.Failed>(session.captureThumbnail(0, 1, 1)).error.code)
        kit.close()
    }

    @Test
    fun loopingIsSavedAndRestored() = runTest {
        val kit = PlaybackContractSubject(backgroundScope).create(RecordingHostCallbacks())
        val first = kit.createSession(VideoKitSessionConfig())
        first.bind(FakeMediaSources.video("loop"), null, emptyList())
        first.state.first { it.phase == SessionPhase.READY }
        assertFalse(first.state.value.looping)
        assertEquals(false, first.captureState().looping)
        first.execute(VideoKitCommand.SetLooping(true))
        val snapshot = first.release()
        assertEquals(true, snapshot.looping)
        val second = kit.createSession(VideoKitSessionConfig())
        second.bind(FakeMediaSources.video("loop"), snapshot, emptyList())
        second.state.first { it.phase == SessionPhase.READY }
        assertTrue(second.state.value.looping)
        // null keeps the default of the media kind.
        val third = kit.createSession(VideoKitSessionConfig())
        third.bind(FakeMediaSources.video("loop"), VideoKitPlaybackState(looping = null), emptyList())
        third.state.first { it.phase == SessionPhase.READY }
        assertFalse(third.state.value.looping)
        kit.close()
    }
}
