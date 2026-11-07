package com.videokit.platform.android

import android.content.ComponentCallbacks2
import android.content.Context
import android.content.res.Configuration
import android.media.MediaCodecInfo
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.os.SystemClock
import com.videokit.core.runtime.AdaptiveResourceBudget
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.runtime.ResourcePressure

/** Concurrent decode capacity from codec performance points (07 §2). */
internal object DecoderCapacity {
    /** Highest stream count tried (the 07 §3 hard limit). */
    private const val MAX_STREAMS = 12

    /**
     * How many 1080p30 streams [points] cover together (a point covering 1080p at `30 × n` fps runs `n` streams),
     * capped by [maxInstances]; `null` when the codec publishes no performance points (then [maxInstances] alone).
     */
    fun streams1080p30(points: List<MediaCodecInfo.VideoCapabilities.PerformancePoint>?, maxInstances: Int): Int? {
        val cap = if (maxInstances > 0) maxInstances else MAX_STREAMS
        if (points.isNullOrEmpty()) return maxInstances.takeIf { it > 0 }?.coerceAtMost(MAX_STREAMS)
        val streams = (MAX_STREAMS downTo 1).firstOrNull { n ->
            val wanted = MediaCodecInfo.VideoCapabilities.PerformancePoint(1920, 1080, 30 * n)
            points.any { it.covers(wanted) }
        } ?: return 0
        return minOf(streams, cap)
    }
}

/** Resource budgets for Android hosts (07 §2: host scoped, initial value from the decoder capabilities). */
public object AndroidResourceBudgets {
    /**
     * A [DefaultResourceBudget] whose video decoder limit is the device estimate of the capability probe; pass it in
     * `VideoKitConfig.resourceBudget` of one host (window) and attach [AndroidResourcePressure] to it.
     */
    public fun forDevice(
        context: Context,
        imageMemoryBytes: Long = DefaultResourceBudget.DEFAULT_IMAGE_MEMORY_BYTES,
    ): DefaultResourceBudget =
        DefaultResourceBudget.forDevice(AndroidCapabilityProbe(context.applicationContext).suggestedVideoSessions(), imageMemoryBytes)
}

/**
 * Feeds the thermal status and memory trim signals of the system into an [AdaptiveResourceBudget] (07 §2–§3: limits
 * drop while the device is hot or short of memory; optional work stops first). The pressure is the higher of the two
 * signals; a memory signal decays after [memoryHoldMs] without a new one. Close it with the host.
 */
public class AndroidResourcePressure private constructor(
    private val context: Context,
    private val budget: AdaptiveResourceBudget,
    private val memoryHoldMs: Long,
) : AutoCloseable {
    private val handler = Handler(Looper.getMainLooper())
    private val power = context.getSystemService(PowerManager::class.java)

    @Volatile
    private var thermal = ResourcePressure.NORMAL

    @Volatile
    private var memory = ResourcePressure.NORMAL

    @Volatile
    private var memoryAtMs = 0L

    @Volatile
    private var closed = false

    private val thermalListener = PowerManager.OnThermalStatusChangedListener { status ->
        thermal = thermalPressure(status)
        publish()
    }

    private val trimCallbacks = object : ComponentCallbacks2 {
        override fun onTrimMemory(level: Int) {
            memoryPressure(level)?.let(::onMemory)
        }

        override fun onConfigurationChanged(newConfig: Configuration) = Unit

        @Deprecated("Deprecated in the platform; still delivered on low memory.")
        override fun onLowMemory() {
            onMemory(ResourcePressure.CRITICAL)
        }
    }

    private val decay = Runnable {
        if (SystemClock.uptimeMillis() - memoryAtMs >= memoryHoldMs) {
            memory = ResourcePressure.NORMAL
            publish()
        }
    }

    private fun start() {
        power?.let {
            thermal = thermalPressure(it.currentThermalStatus)
            it.addThermalStatusListener(context.mainExecutor, thermalListener)
        }
        context.registerComponentCallbacks(trimCallbacks)
        publish()
    }

    private fun onMemory(pressure: ResourcePressure) {
        if (closed) return
        memory = maxOf(memory, pressure)
        memoryAtMs = SystemClock.uptimeMillis()
        handler.removeCallbacks(decay)
        handler.postDelayed(decay, memoryHoldMs)
        publish()
    }

    private fun publish() {
        if (!closed) budget.setPressure(maxOf(thermal, memory))
    }

    override fun close() {
        if (closed) return
        closed = true
        power?.removeThermalStatusListener(thermalListener)
        context.unregisterComponentCallbacks(trimCallbacks)
        handler.removeCallbacks(decay)
        budget.setPressure(ResourcePressure.NORMAL)
    }

    public companion object {
        /** Default time a memory signal is held. */
        public const val DEFAULT_MEMORY_HOLD_MS: Long = 30_000L

        /** Starts feeding [budget]; keeps only the application context. */
        public fun attach(
            context: Context,
            budget: AdaptiveResourceBudget,
            memoryHoldMs: Long = DEFAULT_MEMORY_HOLD_MS,
        ): AndroidResourcePressure = AndroidResourcePressure(context.applicationContext, budget, memoryHoldMs).also { it.start() }

        /** Pressure of a `PowerManager` thermal status. */
        internal fun thermalPressure(status: Int): ResourcePressure = when {
            status >= PowerManager.THERMAL_STATUS_SEVERE -> ResourcePressure.CRITICAL
            status >= PowerManager.THERMAL_STATUS_MODERATE -> ResourcePressure.ELEVATED
            else -> ResourcePressure.NORMAL
        }

        /**
         * Pressure of an `onTrimMemory` level while the app runs (levels 10 RUNNING_LOW and 15 RUNNING_CRITICAL; the
         * constants are deprecated since API 34 but still delivered on API 31–33), `null` for other levels.
         */
        internal fun memoryPressure(level: Int): ResourcePressure? = when (level) {
            TRIM_RUNNING_CRITICAL -> ResourcePressure.CRITICAL
            TRIM_RUNNING_LOW -> ResourcePressure.ELEVATED
            else -> null
        }

        private const val TRIM_RUNNING_LOW = 10
        private const val TRIM_RUNNING_CRITICAL = 15
    }
}
