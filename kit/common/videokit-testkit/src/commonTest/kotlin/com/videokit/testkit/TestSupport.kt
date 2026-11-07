package com.videokit.testkit

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent

/**
 * Lets the Fake settle. The Fake runs in `backgroundScope`, whose tasks `advanceUntilIdle()` ignores,
 * so virtual time is advanced explicitly (longer than every Fake latency and callback timeout).
 */
@OptIn(ExperimentalCoroutinesApi::class)
internal fun TestScope.settle(virtualMs: Long = 30_000L) {
    testScheduler.advanceTimeBy(virtualMs)
    runCurrent()
}
