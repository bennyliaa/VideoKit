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

/**
 * Basic resource budget (07 §2): reserve before create, per-kind limits, a degradation suggestion instead of
 * retries when a limit is reached. The full estimation (codec performance points, failure history, thermal state)
 * is VK-M3; this version counts leases against limits derived from the capability report.
 *
 * Byte limited kinds (image memory, 06 §6.2) count the `estimate.bytes` of their leases instead of units (a request
 * without a byte estimate counts 0 bytes); their [ResourceUsage] reports KiB.
 *
 * Host scoped, not a process singleton: each host (window) passes its own instance in `VideoKitConfig`.
 */
public class DefaultResourceBudget(
    /** Units per kind; kinds not listed are unlimited. Video decoders default to the 07 §3 hard limit 12. */
    private val limits: Map<ResourceKind, Int> = mapOf(ResourceKind.VIDEO_DECODER to HARD_VIDEO_LIMIT),
    /** Bytes per kind; image memory defaults to [DEFAULT_IMAGE_MEMORY_BYTES]. */
    private val byteLimits: Map<ResourceKind, Long> = mapOf(ResourceKind.IMAGE_MEMORY to DEFAULT_IMAGE_MEMORY_BYTES),
) : ResourceBudget {
    private val leases = MutableStateFlow<Map<String, Held>>(emptyMap())
    private val ids = AtomicCounter()

    override suspend fun reserve(request: ResourceRequest): ReservationResult {
        val limit = limits[request.kind]
        val byteLimit = byteLimits[request.kind]
        val bytes = request.estimate.bytes?.coerceAtLeast(0L) ?: 0L
        val id = "lease-${ids.incrementAndGet()}"
        var granted = false
        leases.update { current ->
            val held = current.values.filter { it.kind == request.kind }
            granted = (limit == null || held.size < limit) && (byteLimit == null || held.sumOf { it.bytes } + bytes <= byteLimit)
            if (granted) current + (id to Held(request.kind, request.sessionId, bytes)) else current
        }
        if (!granted) {
            val what = if (byteLimit != null) "$byteLimit bytes" else "$limit"
            return ReservationResult.Denied("${request.kind} limit $what reached", suggestionFor(request))
        }
        return ReservationResult.Granted(Lease(id, request.kind))
    }

    /** Bytes still free for [kind], or `null` when the kind is not byte limited. */
    public fun freeBytes(kind: ResourceKind): Long? {
        val limit = byteLimits[kind] ?: return null
        return (limit - leases.value.values.filter { it.kind == kind }.sumOf { it.bytes }).coerceAtLeast(0L)
    }

    override fun snapshot(): ResourceReport {
        val current = leases.value
        return ResourceReport(
            ResourceKind.entries.map { kind ->
                val held = current.values.filter { it.kind == kind }
                val consumers = held.map { it.sessionId }
                val units = if (kind in byteLimits) (held.sumOf { it.bytes } / KIB).toInt() else held.size
                ResourceUsage(kind, units, units, consumers.distinct(), emptyList())
            },
        )
    }

    private fun suggestionFor(request: ResourceRequest): DegradeSuggestion = when (request.priority) {
        // Off-screen and optional consumers should step back first (07 §3).
        ResourcePriority.OPTIONAL, ResourcePriority.OFFSCREEN -> DegradeSuggestion.SHOW_STATIC_PLACEHOLDER

        else -> if (request.kind ==
            ResourceKind.IMAGE_MEMORY
        ) {
            DegradeSuggestion.REDUCE_RESOLUTION
        } else {
            DegradeSuggestion.REDUCE_ACTIVE_VIDEOS
        }
    }

    private class Held(val kind: ResourceKind, val sessionId: String, val bytes: Long)

    private inner class Lease(override val leaseId: String, override val kind: ResourceKind) : ResourceLease {
        private val closed = AtomicFlag()

        override fun close() {
            if (closed.setOnce()) leases.update { it - leaseId }
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
