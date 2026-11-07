package com.videokit.flutter

import com.videokit.api.SessionPhase
import com.videokit.api.VideoKitSessionState
import org.junit.Assert.assertEquals
import org.junit.Test

/** Snapshot sampling of 14 §8.3: phase changes now, seeking ≤15 Hz, playing ≤4 Hz, other changes now. */
class UpdateSamplerTest {
    private val playing = VideoKitSessionState(phase = SessionPhase.PLAYING, positionUs = 1)

    @Test
    fun firstStateAndPhaseChangesAreImmediate() {
        assertEquals(0L, UpdateSampler.waitMs(null, playing, nowMs = 10, lastSentAtMs = 0))
        assertEquals(0L, UpdateSampler.waitMs(playing, playing.copy(phase = SessionPhase.PAUSED), nowMs = 10, lastSentAtMs = 5))
    }

    @Test
    fun playingIsLimitedToFourHertz() {
        assertEquals(240L, UpdateSampler.waitMs(playing, playing.copy(positionUs = 2), nowMs = 10, lastSentAtMs = 0))
        assertEquals(0L, UpdateSampler.waitMs(playing, playing.copy(positionUs = 2), nowMs = 300, lastSentAtMs = 0))
    }

    @Test
    fun seekingIsLimitedToFifteenHertz() {
        val seeking = playing.copy(seekingToUs = 5_000_000)
        assertEquals(UpdateSampler.SEEKING_INTERVAL_MS - 6, UpdateSampler.waitMs(playing, seeking, nowMs = 106, lastSentAtMs = 100))
    }

    @Test
    fun pausedChangesAreImmediate() {
        val paused = VideoKitSessionState(phase = SessionPhase.PAUSED)
        assertEquals(0L, UpdateSampler.waitMs(paused, paused.copy(volume = 0.5f), nowMs = 1, lastSentAtMs = 0))
    }
}
