package com.videokit.flutter

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceBudget
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourceReport
import com.videokit.api.ResourceRequest
import com.videokit.api.ResourceUsage
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Budget used for Flutter hosts until the core's DefaultResourceBudget exists (07 §2, VK-M3): one process-wide
 * limit of [maxVideoDecoders] video decoders shared by all engines (07 §3 hard limit 12).
 */
internal class PluginResourceBudget(private val maxVideoDecoders: Int = 12) : ResourceBudget {
    private val lock = Any()
    private val leases = LinkedHashMap<String, Pair<ResourceKind, String>>()
    private val ids = AtomicLong()

    override suspend fun reserve(request: ResourceRequest): ReservationResult = synchronized(lock) {
        val used = leases.values.count { it.first == ResourceKind.VIDEO_DECODER }
        if (request.kind == ResourceKind.VIDEO_DECODER && used >= maxVideoDecoders) {
            return ReservationResult.Denied("VIDEO_DECODER limit $maxVideoDecoders reached", DegradeSuggestion.REDUCE_ACTIVE_VIDEOS)
        }
        val id = "plugin-lease-${ids.incrementAndGet()}"
        leases[id] = request.kind to request.sessionId
        ReservationResult.Granted(Lease(id, request.kind))
    }

    override fun snapshot(): ResourceReport = synchronized(lock) {
        ResourceReport(
            ResourceKind.entries.map { kind ->
                val consumers = leases.values.filter { it.first == kind }.map { it.second }
                ResourceUsage(kind, consumers.size, consumers.size, consumers.distinct(), emptyList())
            },
        )
    }

    private inner class Lease(override val leaseId: String, override val kind: ResourceKind) : ResourceLease {
        private val closed = AtomicBoolean(false)

        override fun close() {
            if (closed.compareAndSet(false, true)) synchronized(lock) { leases.remove(leaseId) }
        }
    }

    companion object {
        /** Shared by every engine of the process. */
        val shared: PluginResourceBudget by lazy { PluginResourceBudget() }
    }
}
