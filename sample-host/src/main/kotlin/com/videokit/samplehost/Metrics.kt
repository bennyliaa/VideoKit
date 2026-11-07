package com.videokit.samplehost

import android.util.Log

/**
 * One logcat line per measurement event (tag `VideoKitMetrics`), parsed by the 14 §9.3 scripts in
 * `sample-host/measure/`. Format: `<event> key=value key=value`.
 */
internal object Metrics {
    const val TAG: String = "VideoKitMetrics"

    fun log(event: String, vararg fields: Pair<String, Any>) {
        Log.i(
            TAG,
            buildString {
                append(event)
                fields.forEach { (key, value) -> append(' ').append(key).append('=').append(value) }
            },
        )
    }
}

/** Launch extras of [MainActivity] used by the measurement scripts (`adb shell am start ... --ez/--es/--el`). */
internal object LaunchExtras {
    /** Boolean, default true: prewarm the first embed engine when the main screen starts. */
    const val PREWARM: String = "prewarm"

    /** String: open a page automatically — `engine`, `embed`, `multiview4` (four engines), `multiview1` (one engine). */
    const val OPEN: String = "open"

    /** Long, default 0: delay before [OPEN], so a prewarm can finish first. */
    const val OPEN_DELAY_MS: String = "openDelayMs"
}
