package com.videokit.api

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue
import kotlin.test.fail

class ApiTypesTest {
    @Test
    fun apiVersionIsOneZeroZero() {
        assertEquals(VideoKitApiVersion(1, 0, 0), VideoKitApiVersion.CURRENT)
        assertEquals("1.0.0", VideoKitApiVersion.CURRENT.toString())
    }

    @Test
    fun apiVersionParseAndCompare() {
        assertEquals(VideoKitApiVersion(1, 2, 3), VideoKitApiVersion.parse("1.2.3"))
        assertNull(VideoKitApiVersion.parse("1.2"))
        assertNull(VideoKitApiVersion.parse("1.x.3"))
        assertNull(VideoKitApiVersion.parse("-1.0.0"))
        assertTrue(VideoKitApiVersion(1, 2, 0) > VideoKitApiVersion(1, 1, 9))
        assertTrue(VideoKitApiVersion(1, 2, 0).isCompatibleWith(VideoKitApiVersion(1, 1, 0)))
        assertFalse(VideoKitApiVersion(1, 0, 0).isCompatibleWith(VideoKitApiVersion(1, 1, 0)))
        assertFalse(VideoKitApiVersion(2, 0, 0).isCompatibleWith(VideoKitApiVersion(1, 0, 0)))
    }

    @Test
    fun unknownErrorCodeMapsToInternalRedacted() {
        assertEquals(ErrorCode.SOURCE_TIMEOUT, ErrorCode.fromWireName("SOURCE_TIMEOUT"))
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorCode.fromWireName("SOME_FUTURE_CODE"))
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorCode.fromWireName(null))
        assertEquals(22, ErrorCode.entries.size)
    }

    @Test
    fun otherWireNameFallbacks() {
        assertEquals(SuggestedAction.NONE, SuggestedAction.fromWireName("FUTURE"))
        assertEquals(UnsupportedReason.UNKNOWN, UnsupportedReason.fromWireName("FUTURE"))
        assertNull(ErrorStage.fromWireName("FUTURE"))
        assertEquals(ErrorStage.SINK, ErrorStage.fromWireName("SINK"))
    }

    @Test
    fun sourceAndSinkErrorCodesMapToStableCodes() {
        assertEquals(ErrorCode.SOURCE_NOT_FOUND, SourceErrorCode.NOT_FOUND.errorCode)
        assertEquals(ErrorCode.SOURCE_PERMISSION_DENIED, SourceErrorCode.PERMISSION_DENIED.errorCode)
        assertEquals(ErrorCode.SOURCE_DISCONNECTED, SourceErrorCode.DISCONNECTED.errorCode)
        assertEquals(ErrorCode.SOURCE_TIMEOUT, SourceErrorCode.TIMEOUT.errorCode)
        assertEquals(ErrorCode.OUTPUT_PERMISSION_DENIED, SinkErrorCode.PERMISSION_DENIED.errorCode)
        assertEquals(ErrorCode.OUTPUT_SPACE_INSUFFICIENT, SinkErrorCode.SPACE_INSUFFICIENT.errorCode)
        assertEquals(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED, SinkErrorCode.CAPABILITY_UNSUPPORTED.errorCode)
        assertEquals(ErrorCode.EXPORT_FAILED, SinkErrorCode.IO_FAILED.errorCode)
    }

    @Test
    fun sessionPhasesMatchContract() {
        assertEquals(
            listOf(
                "CREATED", "BINDING", "READY", "PLAYING", "PAUSED", "BUFFERING", "ENDED",
                "ERROR_RECOVERABLE", "ERROR_FATAL", "RELEASING", "RELEASED",
            ),
            SessionPhase.entries.map { it.name },
        )
        assertEquals(
            listOf(
                "CREATED", "PREPARING", "READY", "TRACKING", "EXPORTING", "COMPLETED", "FAILED",
                "CANCELLING", "CANCELLED", "RELEASING", "RELEASED",
            ),
            EditPhase.entries.map { it.name },
        )
    }

    @Test
    fun defaultsOfStateAndSnapshot() {
        val state = VideoKitSessionState()
        assertEquals(SessionPhase.CREATED, state.phase)
        assertFalse(state.resourcesHeld)
        assertEquals(1f, state.speed)
        val snapshot = VideoKitPlaybackState()
        assertEquals(VideoKitPlaybackState.CURRENT_SCHEMA_VERSION, snapshot.schemaVersion)
        assertNull(snapshot.positionUs)
        assertEquals(1, VideoKitCapabilities().schemaVersion)
    }

    @Test
    fun timeRangeAndMaskRegion() {
        val range = TimeRangeUs(10, 20)
        assertTrue(range.isValid)
        assertEquals(10, range.durationUs)
        assertTrue(15L in range)
        assertFalse(20L in range)
        assertFalse(TimeRangeUs(20, 20).isValid)
        assertFalse(TimeRangeUs(-1, 20).isValid)
        assertTrue(MaskRegion(0.1f, 0.1f, 0.5f, 0.5f).isValid)
        assertFalse(MaskRegion(0.6f, 0.1f, 0.5f, 0.5f).isValid)
        assertFalse(MaskRegion(0.1f, 0.1f, 0f, 0.5f).isValid)
    }

    @Test
    fun timelineDurationIsSumOfClips() {
        val timeline = Timeline(clips = listOf(Clip("a", "s", 0, 1_000), Clip("b", "s", 5_000, 7_000)))
        assertEquals(3_000, timeline.durationUs)
    }

    @Test
    fun callbackTimeoutDefaultsFollowM0Defaults() {
        val timeouts = HostCallbackTimeouts()
        assertEquals(10_000L, timeouts.hostActionMs)
        assertEquals(3_000L, timeouts.navigationMs)
        assertEquals(2_000L, timeouts.notificationMs)
        try {
            HostCallbackTimeouts(hostActionMs = 0)
            fail("expected IllegalArgumentException")
        } catch (expected: IllegalArgumentException) {
            assertTrue(expected.message!!.contains("positive"))
        }
    }
}
