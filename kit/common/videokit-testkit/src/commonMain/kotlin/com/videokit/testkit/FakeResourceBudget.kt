package com.videokit.testkit

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceBudget
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourceReport
import com.videokit.api.ResourceRequest
import com.videokit.api.ResourceUsage
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.AtomicFlag
import com.videokit.testkit.internal.AtomicMap

/**
 * In-memory [ResourceBudget] for tests and demos: a fixed number of units per [ResourceKind].
 * Kinds without a limit are always granted. Releasing a lease twice is harmless.
 */
public class FakeResourceBudget(
    /** Units per kind; defaults to 12 video decoders (07 §3 hard limit). */
    private val limits: Map<ResourceKind, Int> = mapOf(ResourceKind.VIDEO_DECODER to 12),
) : ResourceBudget {
    private val leases = AtomicMap<String, Pair<ResourceKind, String>>()
    private val ids = AtomicCounter()

    override suspend fun reserve(request: ResourceRequest): ReservationResult {
        val id = "lease-${ids.incrementAndGet()}"
        val limit = limits[request.kind]
        val granted = leases.modify { current ->
            val used = current.values.count { it.first == request.kind }
            if (limit != null && used >= limit) current to false else (current + (id to (request.kind to request.sessionId))) to true
        }
        return if (granted) {
            ReservationResult.Granted(Lease(id, request.kind))
        } else {
            ReservationResult.Denied("${request.kind} limit $limit reached", DegradeSuggestion.REDUCE_ACTIVE_VIDEOS)
        }
    }

    override fun snapshot(): ResourceReport {
        val current = leases.snapshot
        return ResourceReport(
            ResourceKind.entries.map { kind ->
                val consumers = current.values.filter { it.first == kind }.map { it.second }
                ResourceUsage(kind, consumers.size, consumers.size, consumers.distinct(), emptyList())
            },
        )
    }

    /** Number of currently held leases of [kind]. */
    public fun held(kind: ResourceKind): Int = leases.snapshot.values.count { it.first == kind }

    private inner class Lease(override val leaseId: String, override val kind: ResourceKind) : ResourceLease {
        private val closed = AtomicFlag()

        override fun close() {
            if (closed.setOnce()) leases.remove(leaseId)
        }
    }
}
