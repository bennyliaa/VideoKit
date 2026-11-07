package com.videokit.testkit

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertTrue

class TestPatternTest {
    @Test
    fun timecodeFormat() {
        assertEquals("00:00:00.000", TestPattern.formatTimecode(0))
        assertEquals("00:00:00.000", TestPattern.formatTimecode(-5))
        assertEquals("00:01:23.456", TestPattern.formatTimecode(83_456_789))
        assertEquals("02:00:00.001", TestPattern.formatTimecode(7_200_001_000))
    }

    @Test
    fun sessionTagIsLastFourCharacters() {
        assertEquals("0042", TestPattern.sessionTag("fake-session-0042"))
        assertEquals("__ab", TestPattern.sessionTag("ab"))
    }

    @Test
    fun frameHasBarsMovingBlockAndDemoLabel() {
        val frame = TestPattern.frame("fake-session-0001", 1_000_000, 1280, 720)
        assertEquals(TestPattern.BAR_COLORS.size + 1, frame.blocks.size)
        assertEquals(TestPattern.BAR_COLORS, frame.blocks.dropLast(1).map { it.argb })
        assertEquals("00:00:01.000", frame.timecode)
        assertEquals("0001", frame.sessionTag)
        assertEquals("DEMO", frame.label)
        frame.blocks.forEach { block ->
            assertTrue(block.left >= 0f && block.right <= 1f && block.left < block.right)
            assertTrue(block.top >= 0f && block.bottom <= 1f && block.top < block.bottom)
        }
    }

    @Test
    fun movingBlockFollowsPositionAndWraps() {
        fun moverLeft(positionUs: Long) = TestPattern.frame("s", positionUs, 100, 100).blocks.last().left
        assertEquals(0f, moverLeft(0), absoluteTolerance = 1e-6f)
        assertTrue(moverLeft(1_000_000) > moverLeft(0))
        assertTrue(moverLeft(2_000_000) > moverLeft(1_000_000))
        assertEquals(moverLeft(0), moverLeft(TestPattern.MOTION_PERIOD_US), absoluteTolerance = 1e-6f)
    }

    @Test
    fun backgroundIsStablePerSessionAndOpaque() {
        val a = TestPattern.backgroundFor("fake-session-0001")
        assertEquals(a, TestPattern.backgroundFor("fake-session-0001"))
        assertNotEquals(a, TestPattern.backgroundFor("fake-session-0002"))
        assertEquals(0xFF, a ushr 24)
    }
}
