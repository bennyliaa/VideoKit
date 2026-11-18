package com.videokit.export.android

import android.os.IBinder

/**
 * Messages between the main process and the export worker (Messenger `what` codes and Bundle keys), and the
 * timings verified in S4 (reports\S4 §0.7). Internal to this module: both ends ship together.
 */
internal object WorkerProtocol {
    // main -> worker
    const val START = 1
    const val CANCEL = 2

    // worker -> main
    const val STARTED = 10
    const val PROGRESS = 11
    const val DONE = 12
    const val ERROR = 13
    const val CANCELLED = 14

    const val KEY_BROKER = "broker"
    const val KEY_OUTPUT = "output"
    const val KEY_IN_US = "inUs"
    const val KEY_OUT_US = "outUs"
    const val KEY_TARGET_HEIGHT = "targetHeight"
    const val KEY_PID = "pid"
    const val KEY_SAMPLES = "samples"
    const val KEY_BYTES = "bytes"
    const val KEY_PROCESSED_US = "processedUs"
    const val KEY_CODE = "code"
    const val KEY_REASON = "reason"
    const val KEY_DIAGNOSTIC = "diagnostic"
    const val KEY_METADATA = "metadata"

    /** Before the first written sample: process cold start and Transformer set-up (S4 attempt 5: about 12 s). */
    const val STARTUP_GRACE_MS = 60_000L

    /** After the first sample: no message for this long is a hang (S4 LOOP: detected in 5.0 s). */
    const val HANG_MS = 5_000L

    /** A worker that does not confirm CANCEL within this time is killed (S4: confirmed in 138 ms). */
    const val CANCEL_GRACE_MS = 3_000L

    /** Waiting for the binder death after `killProcess` (S4: 20–95 ms). */
    const val KILL_WAIT_MS = 5_000L

    /** Watchdog period. */
    const val TICK_MS = 250L

    /** Progress messages at most this often. */
    const val PROGRESS_INTERVAL_MS = 200L

    const val BROKER_DESCRIPTOR = "com.videokit.export.android.SourceBroker"
    const val BROKER_READ = IBinder.FIRST_CALL_TRANSACTION
    const val BROKER_LENGTH = IBinder.FIRST_CALL_TRANSACTION + 1

    /** Bytes per broker call (S4). */
    const val MAX_READ = 64 * 1024
}
