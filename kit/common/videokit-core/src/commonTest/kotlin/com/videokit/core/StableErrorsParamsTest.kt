package com.videokit.core

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.SinkErrorCode
import com.videokit.api.SuggestedAction
import com.videokit.api.VideoKitSinkException
import com.videokit.core.runtime.StableErrors
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** UI-AUDIT-A1 J8: OUTPUT_SPACE_INSUFFICIENT carries the shortfall as `requiredBytes` when known (`spec/errors.json`). */
class StableErrorsParamsTest {
    @Test
    fun spaceInsufficientCarriesRequiredBytesOnlyWhenKnown() {
        val error = StableErrors.spaceInsufficient(ErrorStage.SINK, 120_000_000L, "FREE_SPACE")
        assertEquals(ErrorCode.OUTPUT_SPACE_INSUFFICIENT, error.code)
        assertEquals(SuggestedAction.FREE_SPACE, error.suggestedAction)
        assertTrue(error.retryable)
        assertEquals(mapOf(ErrorParams.REQUIRED_BYTES to "120000000"), error.params)
        assertTrue(StableErrors.spaceInsufficient(ErrorStage.SINK, null).params.isEmpty())
        assertTrue(StableErrors.spaceInsufficient(ErrorStage.SINK, -1L).params.isEmpty())
    }

    @Test
    fun sinkFailureKeepsTheReportedShortfall() {
        val reported = StableErrors.fromSinkFailure(VideoKitSinkException(SinkErrorCode.SPACE_INSUFFICIENT, requiredBytes = 3_000_000_000L))
        assertEquals("3000000000", reported.params[ErrorParams.REQUIRED_BYTES])
        assertTrue(StableErrors.fromSinkFailure(VideoKitSinkException(SinkErrorCode.SPACE_INSUFFICIENT)).params.isEmpty())
        assertTrue(
            StableErrors.fromSinkFailure(VideoKitSinkException(SinkErrorCode.PERMISSION_DENIED, requiredBytes = 1L)).params.isEmpty(),
        )
    }
}
