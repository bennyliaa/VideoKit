package com.videokit.playback

import com.videokit.api.FitMode
import com.videokit.api.MediaKind
import com.videokit.api.MediaOrientation
import com.videokit.api.MediaTransform
import com.videokit.api.Size
import com.videokit.api.TrackInfo
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSessionState
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

class PlaybackRulesTest {
    private val audio = listOf(TrackInfo("a1", "zh", null, "audio/ac3", false), TrackInfo("a2", "en", null, "audio/aac", true))
    private val subtitles = listOf(TrackInfo("s1", "zh", null, "text/vtt", true))
    private val prepared = VideoKitSessionState(
        mediaKind = MediaKind.VIDEO,
        durationUs = 10_000_000,
        audioTracks = audio,
        subtitleTracks = subtitles,
        selectedAudioTrackId = "a2",
    )

    @Test
    fun validation() {
        assertTrue(PlaybackRules.isValidSpeed(0.25f))
        assertTrue(PlaybackRules.isValidSpeed(4f))
        assertFalse(PlaybackRules.isValidSpeed(4.5f))
        assertFalse(PlaybackRules.isValidSpeed(Float.NaN))
        assertFalse(PlaybackRules.isValidVolume(1.1f))
        assertTrue(PlaybackRules.isValidTransform(MediaTransform(2f, 0.1f, -0.1f, 90, FitMode.FILL)))
        assertFalse(PlaybackRules.isValidTransform(MediaTransform(2f, 0f, 0f, 45)))
        assertFalse(PlaybackRules.isValidTransform(MediaTransform(0f)))
    }

    @Test
    fun orientation() {
        assertEquals(MediaOrientation.LANDSCAPE, PlaybackRules.orientationOf(Size(1920, 1080)))
        assertEquals(MediaOrientation.PORTRAIT, PlaybackRules.orientationOf(Size(1080, 1920)))
        assertEquals(MediaOrientation.SQUARE, PlaybackRules.orientationOf(Size(1, 1)))
        assertEquals(MediaOrientation.UNKNOWN, PlaybackRules.orientationOf(null))
    }

    @Test
    fun initialStateRestoresValidValuesOnly() {
        val restored = PlaybackRules.applyInitial(
            prepared,
            VideoKitPlaybackState(
                positionUs = 99_000_000,
                speed = 9f,
                volume = 0.5f,
                muted = true,
                audioTrackId = "a1",
                subtitleTrackId = "s1",
                subtitlesEnabled = true,
            ),
        )
        assertEquals(10_000_000, restored.positionUs)
        assertEquals(1f, restored.speed)
        assertEquals(0.5f, restored.volume)
        assertTrue(restored.muted)
        // Unsupported track is not restored.
        assertEquals("a2", restored.selectedAudioTrackId)
        assertEquals("s1", restored.selectedSubtitleTrackId)
    }

    @Test
    fun subtitlesOffWinsOverRememberedTrack() {
        val restored = PlaybackRules.applyInitial(
            prepared.copy(selectedSubtitleTrackId = "s1"),
            VideoKitPlaybackState(subtitleTrackId = "s1", subtitlesEnabled = false),
        )
        assertNull(restored.selectedSubtitleTrackId)
        val snapshot = PlaybackRules.snapshotOf("s", "t", restored, 7L)
        assertEquals(false, snapshot.subtitlesEnabled)
        assertEquals(7L, snapshot.lastViewedAtEpochMs)
    }

    @Test
    fun audioPolicyFollowsActiveAudioMuteAndLock() {
        // 04A A1: silent until the host grants audio.
        assertFalse(PlaybackRules.audioEnabled(prepared))
        val granted = prepared.copy(activeAudio = true)
        assertTrue(PlaybackRules.audioEnabled(granted))
        assertFalse(PlaybackRules.audioEnabled(granted.copy(hiddenForLock = true)))
        assertEquals(0f, PlaybackRules.outputVolume(prepared.copy(muted = true)))
        assertEquals(0.3f, PlaybackRules.outputVolume(prepared.copy(volume = 0.3f)))
    }

    @Test
    fun imageSnapshotHasNoVideoFields() {
        val snapshot = PlaybackRules.snapshotOf("s", "t", VideoKitSessionState(mediaKind = MediaKind.IMAGE_STATIC), null)
        assertNull(snapshot.positionUs)
        assertNull(snapshot.subtitlesEnabled)
    }

    @Test
    fun statisticsTickAndWatchTime() {
        val stats = PlaybackStatistics(tickUs = 250_000, reportUs = 1_000_000)
        assertEquals(PlaybackStatistics.Step(null, null), stats.onPlayed(100_000, 100_000, visible = true))
        assertEquals(PlaybackStatistics.Step(300_000, null), stats.onPlayed(300_000, 200_000, visible = true))
        // Invisible playback ticks but is not watch time.
        assertEquals(PlaybackStatistics.Step(600_000, null), stats.onPlayed(600_000, 300_000, visible = false))
        assertEquals(PlaybackStatistics.Step(1_400_000, 1_100_000), stats.onPlayed(1_400_000, 800_000, visible = true))
        assertEquals(PlaybackStatistics.Step(null, null), stats.onPlayed(1_400_000, 0, visible = true))
    }
}
