package com.videokit.api

/**
 * Top-level VideoKit entry (04 §2). Create one per host scope with [VideoKitFactory.create].
 * Closing it releases every session and edit project it created.
 */
public interface VideoKit : AutoCloseable {
    /** API version implemented by this instance. */
    public val apiVersion: VideoKitApiVersion

    /** Whether this instance is a demo/fake backend (14 §8.2 `demoBackend`). */
    public val isDemo: Boolean get() = false

    /** Capability report, optionally for one media source (04 §9.2). */
    public suspend fun capabilities(request: CapabilityRequest): VideoKitCapabilities

    /**
     * Creates a session. Throws [VideoKitException] with [ErrorCode.DECODER_RESOURCE_EXHAUSTED] when the
     * hard session limit (07 §3) is reached and with [ErrorCode.SESSION_RELEASED] after [close].
     */
    public fun createSession(config: VideoKitSessionConfig): VideoKitSession

    /** Creates an empty edit project. Throws [VideoKitException] after [close]. */
    public fun createEditProject(config: EditProjectConfig): VideoKitEditProject

    /**
     * Restores an edit project from a snapshot. Older schema versions are migrated; an unknown future
     * major version is rejected with [VideoKitException] (04 §10).
     */
    public suspend fun restoreEditProject(serialized: SerializedEditProject, config: EditProjectConfig): VideoKitEditProject

    /** Releases everything this instance created. Idempotent. */
    override fun close()
}

/**
 * Platform independent configuration of a [VideoKit] instance (04 §2). Platform entry points add their
 * own inputs (Android: `VideoKitFactory.create(context, config)` in `videokit-api-android`).
 */
public data class VideoKitConfig(
    /** Host callbacks. */
    val hostCallbacks: VideoKitHostCallbacks,
    /** Host-scoped resource budget (07). */
    val resourceBudget: ResourceBudget,
    /** Logging policy. */
    val logging: LoggingPolicy = LoggingPolicy.ReleaseDefault,
    /** Host callback timeouts (04 §8, 14 §12). */
    val callbackTimeouts: HostCallbackTimeouts = HostCallbackTimeouts(),
)
