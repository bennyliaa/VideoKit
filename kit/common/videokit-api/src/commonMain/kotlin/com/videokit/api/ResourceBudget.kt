package com.videokit.api

/** Kind of a budgeted resource (07 §2). */
public enum class ResourceKind {
    /** A video decoder instance. */
    VIDEO_DECODER,

    /** Image decoding memory. */
    IMAGE_MEMORY,

    /** A tracking worker. */
    TRACKING_WORKER,

    /** An export worker. */
    EXPORT_WORKER,

    /** An encoder instance. */
    ENCODER,
}

/** Resource priority; higher priorities are served first (07 §2). */
public enum class ResourcePriority {
    /** Optional work (prefetch, thumbnails). */
    OPTIONAL,

    /** Off-screen slot. */
    OFFSCREEN,

    /** Visible but silent. */
    VISIBLE,

    /** Visible and audible. */
    VISIBLE_AUDIBLE,
}

/** Estimate of the resources a request needs. All fields are optional hints. */
public data class ResourceEstimate(
    /** Width in pixels. */
    val width: Int? = null,
    /** Height in pixels. */
    val height: Int? = null,
    /** Frame rate. */
    val frameRate: Float? = null,
    /** Codec MIME type. */
    val codec: String? = null,
    /** Whether a hardware codec is requested. */
    val hardware: Boolean? = null,
    /** Memory in bytes. */
    val bytes: Long? = null,
)

/** A resource reservation request (07 §2). */
public data class ResourceRequest(
    /** Requesting session or project id. */
    val sessionId: String,
    /** Kind of resource. */
    val kind: ResourceKind,
    /** Estimate. */
    val estimate: ResourceEstimate,
    /** ResourcePriority. */
    val priority: ResourcePriority,
)

/** Degradation the host may apply when a reservation is denied (07 §3). */
public enum class DegradeSuggestion {
    /** Reduce the number of active videos. */
    REDUCE_ACTIVE_VIDEOS,

    /** Pause off-screen slots. */
    PAUSE_OFFSCREEN,

    /** Show a static placeholder instead of video. */
    SHOW_STATIC_PLACEHOLDER,

    /** Lower the resolution. */
    REDUCE_RESOLUTION,

    /** No suggestion. */
    NONE,
}

/** A granted reservation; closing it returns the resource. Closing is idempotent. */
public interface ResourceLease : AutoCloseable {
    /** Opaque lease id. */
    public val leaseId: String

    /** Kind of the reserved resource. */
    public val kind: ResourceKind

    /** Returns the resource. */
    override fun close()
}

/** Result of [ResourceBudget.reserve]. */
public sealed interface ReservationResult {
    /** The reservation was granted. */
    public data class Granted(
        /** The lease; close it when the resource is released. */
        val lease: ResourceLease,
    ) : ReservationResult

    /** The reservation was denied. */
    public data class Denied(
        /** Redacted reason. */
        val reason: String,
        /** Suggested degradation. */
        val suggestion: DegradeSuggestion,
    ) : ReservationResult
}

/** Usage of one resource kind. */
public data class ResourceUsage(
    /** Resource kind. */
    val kind: ResourceKind,
    /** Number of reserved units. */
    val reserved: Int,
    /** Number of units actually held. */
    val held: Int,
    /** Consumer ids. */
    val consumers: List<String>,
    /** Leases whose release was not confirmed. */
    val unconfirmedReleases: List<String>,
)

/** Snapshot of the budget for hosts and debugging (07 §2). */
public data class ResourceReport(
    /** Usage per kind. */
    val usages: List<ResourceUsage>,
)

/**
 * Host-scoped resource budget (07 §2): resources are reserved before they are created and failures
 * degrade in a bounded way. VideoKit provides a default implementation in the core module (M3).
 */
public interface ResourceBudget {
    /** Reserves a resource. Never retries in a loop. */
    public suspend fun reserve(request: ResourceRequest): ReservationResult

    /** Current usage. */
    public fun snapshot(): ResourceReport
}

/** Log level of [VideoKitLogger]. */
public enum class LogLevel {
    /** Debug details. */
    DEBUG,

    /** Information. */
    INFO,

    /** Warning. */
    WARN,

    /** Error. */
    ERROR,
}

/**
 * Replaceable logger (13 §4). Messages never contain credentials, full paths, full media names,
 * media content or face data; media are identified by a hash prefix of the media token.
 */
public fun interface VideoKitLogger {
    /** Logs one redacted message. */
    public fun log(level: LogLevel, tag: String, message: String)
}

/** Logging policy (13 §4). */
public sealed interface LoggingPolicy {
    /** Release default: no logs are written. */
    public data object ReleaseDefault : LoggingPolicy

    /** Debug diagnostics (off by default), written to [logger]. */
    public data class Diagnostics(
        /** Logger receiving redacted diagnostics. */
        val logger: VideoKitLogger,
        /** Minimum level. */
        val minLevel: LogLevel = LogLevel.DEBUG,
    ) : LoggingPolicy
}
