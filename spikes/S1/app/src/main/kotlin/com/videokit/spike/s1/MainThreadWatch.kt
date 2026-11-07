package com.videokit.spike.s1

import android.os.Looper
import android.os.SystemClock
import android.util.Printer

/**
 * Main thread blocking (15 §4 item 7: a single main thread block ≤ 16 ms): the main looper's message logging marks the
 * start and end of every dispatched message; the longest dispatch since [reset] is the longest single block.
 */
object MainThreadWatch {
    @Volatile private var startedAt = 0L

    @Volatile private var maxMs = 0L

    @Volatile private var over16 = 0

    fun install() {
        Looper.getMainLooper().setMessageLogging(
            Printer { line ->
                val now = SystemClock.uptimeMillis()
                if (line.startsWith(">>>>> Dispatching")) {
                    startedAt = now
                } else if (line.startsWith("<<<<< Finished") && startedAt > 0) {
                    val ms = now - startedAt
                    if (ms > maxMs) maxMs = ms
                    if (ms > BLOCK_LIMIT_MS) over16++
                    startedAt = 0
                }
            },
        )
    }

    /** Longest single dispatch and the number of dispatches over 16 ms since the last call; resets. */
    fun takeAndReset(): Pair<Long, Int> {
        val result = maxMs to over16
        maxMs = 0
        over16 = 0
        return result
    }

    private const val BLOCK_LIMIT_MS = 16L
}
