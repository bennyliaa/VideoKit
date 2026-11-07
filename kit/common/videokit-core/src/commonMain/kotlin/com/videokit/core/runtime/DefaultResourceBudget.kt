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
 * Host scoped, not a process singleton: each host (window) passes its own instance in `VideoKitConfig`.
 */
public class DefaultResourceBudget(
    /** Units per kind; kinds not listed are unlimited. Video decoders default to the 07 §3 hard limit 12. */
    private val limits: Map<ResourceKind, Int> = mapOf(ResourceKind.VIDEO_DECODER to HARD_VIDEO_LIMIT),
) : ResourceBudget {
    private val leases = MutableStateFlow<Map<String, Held>>(emptyMap())
    private val ids = AtomicCounter()

    override suspend fun reserve(request: ResourceRequest): ReservationResult {
        val limit = limits[request.kind]
        val id = "lease-${ids.incrementAndGet()}"
        var granted = false
        leases.update { current ->
            val used = current.values.count { it.kind == request.kind }
            granted = limit == null || used < limit
            if (granted) current + (id to Held(request.kind, request.sessionId)) else current
        }
        if (!granted) {
            return ReservationResult.Denied("${request.kind} limit $limit reached", suggestionFor(request))
        }
        return ReservationResult.Granted(Lease(id, request.kind))
    }

    override fun snapshot(): ResourceReport {
        val current = leases.value
        return ResourceReport(
            ResourceKind.entries.map { kind ->
                val consumers = current.values.filter { it.kind == kind }.map { it.sessionId }
                ResourceUsage(kind, consumers.size, consumers.size, consumers.distinct(), emptyList())
            },
        )
    }

    private fun suggestionFor(request: ResourceRequest): DegradeSuggestion = when (request.priority) {
        // Off-screen and optional consumers should step back first (07 §3).
        ResourcePriority.OPTIONAL, ResourcePriority.OFFSCREEN -> DegradeSuggestion.SHOW_STATIC_PLACEHOLDER

        else -> DegradeSuggestion.REDUCE_ACTIVE_VIDEOS
    }

    private class Held(val kind: ResourceKind, val sessionId: String)

    private inner class Lease(override val leaseId: String, override val kind: ResourceKind) : ResourceLease {
        private val closed = AtomicFlag()

        override fun close() {
            if (closed.setOnce()) leases.update { it - leaseId }
        }
    }

    public companion object {
        /** Hard limit of video sessions (07 §3). */
        public const val HARD_VIDEO_LIMIT: Int = 12

        /**
         * A budget whose video decoder limit is the device suggestion ([suggestedHardwareVideoSessions], from the
         * capability probe), capped by the hard limit; at least one.
         */
        public fun forDevice(suggestedHardwareVideoSessions: Int): DefaultResourceBudget =
            DefaultResourceBudget(mapOf(ResourceKind.VIDEO_DECODER to suggestedHardwareVideoSessions.coerceIn(1, HARD_VIDEO_LIMIT)))
    }
}
