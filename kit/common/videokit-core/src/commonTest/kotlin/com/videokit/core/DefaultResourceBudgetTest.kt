package com.videokit.core

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceRequest
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.runtime.StableErrors
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertTrue

class DefaultResourceBudgetTest {
    private fun request(session: String, priority: ResourcePriority = ResourcePriority.VISIBLE) =
        ResourceRequest(session, ResourceKind.VIDEO_DECODER, ResourceEstimate(), priority)

    @Test
    fun reserveBeforeCreateWithinTheDeviceLimit() = runTest {
        val budget = DefaultResourceBudget.forDevice(2)
        val first = assertIs<ReservationResult.Granted>(budget.reserve(request("a")))
        assertIs<ReservationResult.Granted>(budget.reserve(request("b")))
        val denied = assertIs<ReservationResult.Denied>(budget.reserve(request("c")))
        assertEquals(DegradeSuggestion.REDUCE_ACTIVE_VIDEOS, denied.suggestion)
        assertEquals(
            DegradeSuggestion.SHOW_STATIC_PLACEHOLDER,
            assertIs<ReservationResult.Denied>(budget.reserve(request("d", ResourcePriority.OFFSCREEN))).suggestion,
        )
        assertEquals(listOf("a", "b"), budget.snapshot().usages.single { it.kind == ResourceKind.VIDEO_DECODER }.consumers)
        // Releasing a lease frees the unit; closing twice is harmless.
        first.lease.close()
        first.lease.close()
        assertIs<ReservationResult.Granted>(budget.reserve(request("c")))
    }

    @Test
    fun deviceSuggestionIsCappedByTheHardLimit() = runTest {
        val budget = DefaultResourceBudget.forDevice(99)
        repeat(DefaultResourceBudget.HARD_VIDEO_LIMIT) { assertIs<ReservationResult.Granted>(budget.reserve(request("s$it"))) }
        assertIs<ReservationResult.Denied>(budget.reserve(request("over")))
        // Kinds without a limit are not counted against it.
        assertIs<ReservationResult.Granted>(
            budget.reserve(ResourceRequest("img", ResourceKind.IMAGE_MEMORY, ResourceEstimate(), ResourcePriority.VISIBLE)),
        )
    }

    @Test
    fun stableErrorsCarryRegistryDefaults() {
        val timeout = StableErrors.of(com.videokit.api.ErrorCode.SOURCE_TIMEOUT, com.videokit.api.ErrorStage.PLAYBACK)
        assertTrue(timeout.retryable)
        assertEquals(com.videokit.api.SuggestedAction.RECONNECT_SOURCE, timeout.suggestedAction)
        val redacted = StableErrors.fromSourceFailure(IllegalStateException("/data/user/0/secret"), com.videokit.api.ErrorStage.BIND)
        assertEquals(com.videokit.api.ErrorCode.INTERNAL_ERROR_REDACTED, redacted.code)
        assertTrue(!redacted.diagnostic.orEmpty().contains("secret"))
    }
}
