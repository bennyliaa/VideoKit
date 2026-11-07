package com.videokit.testkit

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * Controllable media clock of the Kotlin Fake (14 §11.1).
 *
 * Fake sessions advance their playback position only when this clock advances, multiplied by the
 * session speed. Tests call [advanceUs]/[advanceMs] for deterministic time; demos call [drive] to
 * follow coroutine time. Latencies (load, seek, export stages, callback timeouts) use coroutine time
 * (`delay`), which is virtual under `kotlinx-coroutines-test`.
 */
public class FakeClock(startUs: Long = 0L) {
    private val elapsed = MutableStateFlow(startUs)

    /** Elapsed media clock time in microseconds. */
    public val elapsedUs: StateFlow<Long> = elapsed.asStateFlow()

    /** Advances the clock by [deltaUs] microseconds. */
    public fun advanceUs(deltaUs: Long) {
        require(deltaUs >= 0) { "deltaUs must not be negative" }
        elapsed.update { it + deltaUs }
    }

    /** Advances the clock by [deltaMs] milliseconds. */
    public fun advanceMs(deltaMs: Long): Unit = advanceUs(deltaMs * 1_000L)

    /** Advances the clock every [tickMs] of coroutine time until the returned job is cancelled. */
    public fun drive(scope: CoroutineScope, tickMs: Long = 16L): Job {
        require(tickMs > 0) { "tickMs must be positive" }
        return scope.launch {
            while (isActive) {
                delay(tickMs)
                advanceMs(tickMs)
            }
        }
    }
}
