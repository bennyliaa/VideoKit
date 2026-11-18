package com.videokit.api

/** Where a host action is placed (04 §7). */
public enum class ActionPlacement {
    /** Primary action bar. */
    PRIMARY_BAR,

    /** Secondary action bar. */
    SECONDARY_BAR,

    /** Overflow menu. */
    OVERFLOW,
}

/** Icon of a host action (04 §7). */
public sealed interface HostIcon {
    /** A built-in VideoKit icon, identified by key (for example `tag`, `favorite`, `delete`). */
    public data class BuiltIn(
        /** Icon key. */
        val iconKey: String,
    ) : HostIcon

    /**
     * An icon resource of the host app (04A N9, T4), identified by a platform independent resource name, never a
     * numeric resource id. Android: a `drawable` resource name such as `ic_tag`, resolved by api-android `HostIcons`.
     */
    public data class Resource(
        /** Resource name (Android: drawable name, optionally prefixed with `drawable/`). */
        val resourceRef: String,
    ) : HostIcon
}

/**
 * A host-defined action shown by VideoKit (04 §7, original requirement §9). VideoKit only knows the
 * opaque [actionId]; the host executes the action.
 */
public data class VideoKitHostAction(
    /** Opaque action id. */
    val actionId: String,
    /**
     * Label key (04 §7). The Kit treats it as an opaque key and never resolves it to text (13 §3.1); the UI
     * resolves it through the host string resolver in the current Locale.
     */
    val labelKey: String,
    /** Content description key; opaque to the Kit, resolved by the UI / host like [labelKey]. */
    val contentDescriptionKey: String,
    /** Icon. */
    val icon: HostIcon,
    /** Whether the action can be activated. */
    val enabled: Boolean = true,
    /** Whether the action is shown as selected (toggle state). */
    val selected: Boolean = false,
    /** Whether the host reports the action as pending. */
    val pending: Boolean = false,
    /** Optional badge text. */
    val badgeText: String? = null,
    /** Higher values are placed first. */
    val displayPriority: Int = 0,
    /** Placement. */
    val placement: ActionPlacement,
)

/** Request sent to the host when a host action is activated (04 §7). */
public data class HostActionRequest(
    /** Action id. */
    val actionId: String,
    /** Session id. */
    val sessionId: String,
    /** Media token of the bound media. */
    val mediaToken: String,
)

/** Outcome of a host action request. */
public enum class HostActionStatus {
    /** The host completed the action. */
    COMPLETED,

    /** The host accepted the action and will finish it later; it updates the actions when done. */
    PENDING,

    /** The host could not perform the action. */
    FAILED,

    /** The user or host cancelled the action. */
    CANCELLED,
}

/** Host answer to [VideoKitHostCallbacks.onHostActionRequested]. */
public data class HostActionResult(
    /** Outcome. */
    val status: HostActionStatus,
    /** Updated action (for example new selected state), if the host wants to replace it. */
    val updatedAction: VideoKitHostAction? = null,
    /** Optional message key for a transient notice. */
    val messageKey: String? = null,
)

/** Direction of a navigation request (06 §5). */
public enum class NavigationDirection {
    /** Previous media. */
    PREVIOUS,

    /** Next media. */
    NEXT,
}

/** Request for the previous/next media; the host decides and re-binds (05, original requirement §15.2). */
public data class NavigationRequest(
    /** Session id. */
    val sessionId: String,
    /** Media token of the bound media, if any. */
    val mediaToken: String?,
    /** Direction. */
    val direction: NavigationDirection,
)

/** Host answer to a navigation request. */
public enum class NavigationResult {
    /** The host will bind the requested media. */
    ACCEPTED,

    /** There is no media in that direction; the UI bounces back. */
    UNAVAILABLE,

    /** The host callback failed or timed out (04A V4). */
    FAILED,
}

/** Host decision for a recoverable error. */
public enum class RecoveryDecision {
    /** Retry (re-bind the same source). */
    RETRY,

    /** Keep the error state; the UI shows the error. */
    KEEP_ERROR,

    /** Release the session. */
    RELEASE,
}

/**
 * Callbacks implemented by the host (04 §8, original requirement §18).
 *
 * VideoKit calls them in coroutines it manages, never on the main thread for blocking work, and with
 * a timeout ([HostCallbackTimeouts]). A callback that throws or times out is recorded as
 * [ErrorCode.HOST_CALLBACK_FAILED] and never blocks the session.
 */
public interface VideoKitHostCallbacks {
    /** A host action was activated. */
    public suspend fun onHostActionRequested(request: HostActionRequest): HostActionResult

    /** The user asked for the previous/next media. */
    public suspend fun onNavigationRequested(request: NavigationRequest): NavigationResult

    /** A stable playback snapshot, sent after changes settle and on release. Failing to store it never blocks release. */
    public suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState)

    /** A sampled playback event for statistics. */
    public suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent)

    /** The controls of [sessionId] were shown or hidden (host side panels follow them). */
    public suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean)

    /** All read handles of [mediaToken] used by [sessionId] are closed; queued file operations may run. */
    public suspend fun onSourceReleased(sessionId: String, mediaToken: String)

    /** A recoverable error happened in [sessionId] (04A I7); the host decides what to do. */
    public suspend fun onRecoverableError(sessionId: String, error: VideoKitStableError): RecoveryDecision

    /** A fatal error happened in [sessionId] (04A I7). */
    public suspend fun onFatalSessionError(sessionId: String, error: VideoKitStableError)

    /**
     * Opens the avatar PNG of [avatarToken] for preview and export (REQ-ED-07, 04A E6): the host keeps the PNG and gives
     * a readable source like a media source; `builtin:N` tokens never reach the host. `null` (the default) when the host
     * has no such avatar: the mask then falls back to mosaic with a warning. Same as the Dart `openAvatar`.
     */
    public suspend fun openAvatar(avatarToken: String): VideoKitSourceFactory? = null

    /**
     * Dynamic feature gate (REQ-API-10 ②): may the user use [feature] now? Called before the user enters the feature
     * ([VideoKit.checkFeature]) and again by the API entry points of the feature (edit project, tracking, export,
     * multi-view bind). The host may show its own page (for example a paywall) before it answers, within
     * [HostCallbackTimeouts.featureGateMs]; the Kit never asks while holding a project or session lock. [sessionId]
     * is the session or edit project the feature is used in, `null` before one exists. Within one edit project or
     * session an [FeatureAccess.Allowed] answer is remembered, so a feature that was entered is not taken away mid-work
     * and the host is not asked again for every command; a [FeatureAccess.Denied] answer is not remembered.
     *
     * The default allows everything without a marker: a host without the gate behaves as before REQ-API-10. A callback
     * that throws or exceeds [HostCallbackTimeouts.featureGateMs] counts as denied. Same as the Dart `checkFeature`.
     */
    public suspend fun checkFeature(feature: VideoKitFeature, sessionId: String?): FeatureAccess = FeatureAccess.ALLOWED
}

/**
 * Timeouts of host callbacks in milliseconds (04 §8; defaults from 14 §12).
 */
public data class HostCallbackTimeouts(
    /** [VideoKitHostCallbacks.onHostActionRequested]; the action is pending meanwhile. */
    val hostActionMs: Long = 10_000L,
    /** [VideoKitHostCallbacks.onNavigationRequested]. */
    val navigationMs: Long = 3_000L,
    /** [VideoKitHostCallbacks.onRecoverableError]. */
    val recoveryDecisionMs: Long = 3_000L,
    /** All notification callbacks (snapshot, events, visibility, source released, fatal error). */
    val notificationMs: Long = 2_000L,
    /**
     * [VideoKitHostCallbacks.checkFeature] (REQ-API-10): long enough for a host page (paywall) shown before it answers;
     * on timeout the feature counts as denied. Same default as the Dart `featureGate`.
     */
    val featureGateMs: Long = 30_000L,
) {
    init {
        require(hostActionMs > 0 && navigationMs > 0 && recoveryDecisionMs > 0 && notificationMs > 0 && featureGateMs > 0) {
            "Callback timeouts must be positive"
        }
    }
}
