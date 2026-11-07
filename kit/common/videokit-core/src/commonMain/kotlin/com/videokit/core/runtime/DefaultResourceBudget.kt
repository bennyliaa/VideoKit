package com.videokit.core.runtime

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceBudget
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceReport
import com.videokit.api.ResourceRequest
import com.videokit.api.ResourceUsage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update

/** System resource pressure (07 §2: thermal state and available memory), reported by the platform. */
public enum class ResourcePressure {
    /** Normal. */
    NORMAL,

    /** Elevated (thermal "moderate", memory trim while running): one decoder less, optional work stops. */
    ELEVATED,

    /** Critical (thermal "severe" or worse, low memory): one decoder, half the image memory, no optional work. */
    CRITICAL,
}

/**
 * A [ResourceBudget] that learns from the runtime (07 §2): failed creations lower later limits, system pressure
 * lowers them for as long as it lasts, and releases the engine could not confirm are reported. The runtime finds it
 * by type; hosts may still inject any [ResourceBudget].
 */
public interface AdaptiveResourceBudget : ResourceBudget {
    /** Current pressure. */
    public val pressure: ResourcePressure

    /** Sets the pressure (Android: thermal status and memory trim callbacks, `AndroidResourcePressure`). */
    public fun setPressure(pressure: ResourcePressure)

    /**
     * A resource of [kind] could not be created although the reservation was granted (for example the codec reported
     * insufficient resources): later limits stay at the number held without it (07 §2 "实际创建失败会更新历史").
     */
    public fun onCreationFailed(kind: ResourceKind)

    /** The release of [lease] could not be confirmed (engine close failed); it stays listed in the report. */
    public fun onReleaseUnconfirmed(lease: ResourceLease, sessionId: String)
}

/**
 * Default resource budget (07 §2–§3): reserve before create, per-kind limits, a degradation suggestion instead of
 * retries when a limit is reached.
 *
 * - Unit limited kinds (video decoders) start from the device suggestion of the capability probe; a failed creation
 *   lowers the effective limit to what was held when it failed (never below 1); pressure lowers it further while it
 *   lasts (ELEVATED: −1, CRITICAL: 1).
 * - Byte limited kinds (image memory, 06 §6.2) count the `estimate.bytes` of their leases (a request without a byte
 *   estimate counts 0 bytes); CRITICAL pressure halves them. Their [ResourceUsage] reports KiB.
 * - Lowering a limit never takes back granted leases (07 §3: no forced cancellation of other slots); it applies to
 *   the next reservations.
 *
 * Host scoped, not a process singleton: each host (window) passes its own instance in `VideoKitConfig`.
 */
public class DefaultResourceBudget(
    /** Units per kind; kinds not listed are unlimited. Video decoders default to the 07 §3 hard limit 12. */
    private val limits: Map<ResourceKind, Int> = mapOf(ResourceKind.VIDEO_DECODER to HARD_VIDEO_LIMIT),
    /** Bytes per kind; image memory defaults to [DEFAULT_IMAGE_MEMORY_BYTES]. */
    private val byteLimits: Map<ResourceKind, Long> = mapOf(ResourceKind.IMAGE_MEMORY to DEFAULT_IMAGE_MEMORY_BYTES),
) : AdaptiveResourceBudget {
    private val state = MutableStateFlow(State())
    private val ids = AtomicCounter()

    override val pressure: ResourcePressure get() = state.value.pressure

    override suspend fun reserve(request: ResourceRequest): ReservationResult {
        val bytes = request.estimate.bytes?.coerceAtLeast(0L) ?: 0L
        val id = "lease-${ids.incrementAndGet()}"
        var granted = false
        var reason = ""
        state.update { current ->
            val held = current.leases.values.filter { it.kind == request.kind }
            val limit = current.unitLimit(request.kind)
            val byteLimit = current.byteLimit(request.kind)
            granted = (limit == null || held.size < limit) && (byteLimit == null || held.sumOf { it.bytes } + bytes <= byteLimit)
            reason = if (byteLimit != null) "${request.kind} limit $byteLimit bytes reached" else "${request.kind} limit $limit reached"
            if (granted) current.copy(leases = current.leases + (id to Held(request.kind, request.sessionId, bytes))) else current
        }
        if (!granted) return ReservationResult.Denied(reason, suggestionFor(request))
        return ReservationResult.Granted(Lease(id, request.kind))
    }

    override fun setPressure(pressure: ResourcePressure) {
        state.update { it.copy(pressure = pressure) }
    }

    override fun onCreationFailed(kind: ResourceKind) {
        state.update { current ->
            val base = limits[kind] ?: return@update current
            // The failing consumer still holds its lease: the device managed the others.
            val managed = (current.leases.values.count { it.kind == kind } - 1).coerceAtLeast(1)
            val learned = minOf(current.learned[kind] ?: base, managed)
            current.copy(learned = current.learned + (kind to learned))
        }
    }

    override fun onReleaseUnconfirmed(lease: ResourceLease, sessionId: String) {
        state.update { it.copy(unconfirmed = it.unconfirmed + (lease.leaseId to (lease.kind to sessionId))) }
    }

    /** Effective unit limit of [kind] now (calibration and pressure applied), or `null` when unlimited. */
    public fun effectiveLimit(kind: ResourceKind): Int? = state.value.unitLimit(kind)

    /** Bytes still free for [kind], or `null` when the kind is not byte limited. */
    public fun freeBytes(kind: ResourceKind): Long? {
        val current = state.value
        val limit = current.byteLimit(kind) ?: return null
        return (limit - current.leases.values.filter { it.kind == kind }.sumOf { it.bytes }).coerceAtLeast(0L)
    }

    override fun snapshot(): ResourceReport {
        val current = state.value
        return ResourceReport(
            ResourceKind.entries.map { kind ->
                val held = current.leases.values.filter { it.kind == kind }
                val consumers = held.map { it.sessionId }
                val units = if (kind in byteLimits) (held.sumOf { it.bytes } / KIB).toInt() else held.size
                val unconfirmed = current.unconfirmed.filterValues { it.first == kind }.keys.toList()
                ResourceUsage(kind, units, units, consumers.distinct(), unconfirmed)
            },
        )
    }

    private fun suggestionFor(request: ResourceRequest): DegradeSuggestion = when {
        // Off-screen and optional consumers should step back first (07 §3).
        request.priority == ResourcePriority.OPTIONAL || request.priority == ResourcePriority.OFFSCREEN ->
            DegradeSuggestion.SHOW_STATIC_PLACEHOLDER

        request.kind == ResourceKind.IMAGE_MEMORY -> DegradeSuggestion.REDUCE_RESOLUTION

        else -> DegradeSuggestion.REDUCE_ACTIVE_VIDEOS
    }

    private data class State(
        val leases: Map<String, Held> = emptyMap(),
        val learned: Map<ResourceKind, Int> = emptyMap(),
        val pressure: ResourcePressure = ResourcePressure.NORMAL,
        val unconfirmed: Map<String, Pair<ResourceKind, String>> = emptyMap(),
    )

    private fun State.unitLimit(kind: ResourceKind): Int? {
        val base = limits[kind] ?: return null
        val calibrated = minOf(base, learned[kind] ?: base)
        return when (pressure) {
            ResourcePressure.NORMAL -> calibrated
            ResourcePressure.ELEVATED -> (calibrated - 1).coerceAtLeast(1)
            ResourcePressure.CRITICAL -> 1
        }
    }

    private fun State.byteLimit(kind: ResourceKind): Long? {
        val base = byteLimits[kind] ?: return null
        return if (pressure == ResourcePressure.CRITICAL) base / 2 else base
    }

    private class Held(val kind: ResourceKind, val sessionId: String, val bytes: Long)

    private inner class Lease(override val leaseId: String, override val kind: ResourceKind) : ResourceLease {
        private val closed = AtomicFlag()

        override fun close() {
            if (closed.setOnce()) state.update { it.copy(leases = it.leases - leaseId) }
        }
    }

    public companion object {
        /** Hard limit of video sessions (07 §3). */
        public const val HARD_VIDEO_LIMIT: Int = 12

        /** Default image memory of one host (06 §6.2): 192 MiB of decoded bitmaps over all image sessions. */
        public const val DEFAULT_IMAGE_MEMORY_BYTES: Long = 192L * 1024 * 1024

        private const val KIB = 1024L

        /**
         * A budget whose video decoder limit is the device suggestion ([suggestedHardwareVideoSessions], from the
         * capability probe), capped by the hard limit; at least one. [imageMemoryBytes] bounds decoded images.
         */
        public fun forDevice(
            suggestedHardwareVideoSessions: Int,
            imageMemoryBytes: Long = DEFAULT_IMAGE_MEMORY_BYTES,
        ): DefaultResourceBudget = DefaultResourceBudget(
            mapOf(ResourceKind.VIDEO_DECODER to suggestedHardwareVideoSessions.coerceIn(1, HARD_VIDEO_LIMIT)),
            mapOf(ResourceKind.IMAGE_MEMORY to imageMemoryBytes.coerceAtLeast(0L)),
        )
    }
}
