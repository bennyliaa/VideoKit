package com.videokit.core

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceRequest
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.runtime.SourceUses
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.yield
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue

class ImageBudgetAndSourceUsesTest {
    private fun image(session: String, bytes: Long) =
        ResourceRequest(session, ResourceKind.IMAGE_MEMORY, ResourceEstimate(bytes = bytes), ResourcePriority.VISIBLE)

    @Test
    fun imageMemoryIsCountedInBytes() = runTest {
        val budget = DefaultResourceBudget.forDevice(4, imageMemoryBytes = 10_000L)
        val first = assertIs<ReservationResult.Granted>(budget.reserve(image("a", 6_000L)))
        assertEquals(4_000L, budget.freeBytes(ResourceKind.IMAGE_MEMORY))
        val denied = assertIs<ReservationResult.Denied>(budget.reserve(image("b", 6_000L)))
        assertEquals(DegradeSuggestion.REDUCE_RESOLUTION, denied.suggestion)
        assertIs<ReservationResult.Granted>(budget.reserve(image("b", 4_000L)))
        assertEquals(0L, budget.freeBytes(ResourceKind.IMAGE_MEMORY))
        first.lease.close()
        assertEquals(6_000L, budget.freeBytes(ResourceKind.IMAGE_MEMORY))
        // Video decoders stay unit counted, and are not byte limited.
        assertNull(budget.freeBytes(ResourceKind.VIDEO_DECODER))
        val usage = budget.snapshot().usages.single { it.kind == ResourceKind.IMAGE_MEMORY }
        assertEquals(listOf("b"), usage.consumers)
    }

    @Test
    fun sourceUsesAreClosedWithoutCancellingTheirCallers() = runTest {
        val uses = SourceUses(this)
        val started = CompletableDeferred<Unit>()
        var closedHandle = false
        val caller = async {
            uses.use {
                try {
                    started.complete(Unit)
                    awaitCancellation()
                } finally {
                    closedHandle = true
                }
            }
        }
        started.await()
        assertEquals(1, uses.active)
        uses.closeAll()
        assertTrue(closedHandle, "the use finished before closeAll returned")
        assertNull(caller.await(), "a closed use answers null; its caller continues")
        assertEquals(0, uses.active)
        // A normal use returns its value.
        assertEquals(42, uses.use { 42 })
        // The caller's own cancellation is not swallowed.
        val cancelled = launch { uses.use { awaitCancellation() } }
        yield()
        cancelled.cancel()
        cancelled.join()
        assertTrue(cancelled.isCancelled)
        assertEquals(0, uses.active)
    }
}
