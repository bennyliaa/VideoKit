package com.videokit.api

/**
 * A feature the host can switch off or gate (REQ-API-10, VK-A2; list confirmed by the user 2026-11-08). Playback and
 * image viewing are not features in this sense: they can never be turned off and are never gated. Same as the Dart
 * `VideoKitFeature`, in the same order.
 *
 * [MASK_TRACKING] and [AVATAR] depend on [EDIT] ([parent]): hiding [EDIT] hides them too. [EXPORT] is independent (a
 * host may lock export and leave editing open). The dynamic gate ([VideoKitHostCallbacks.checkFeature]) is asked only
 * for the feature named; a denied [EDIT] keeps the user out of the editor, so its sub-features are unreachable as well.
 * No quotas or parameter limits.
 */
public enum class VideoKitFeature(
    /** The feature this one depends on, or `null`. */
    public val parent: VideoKitFeature?,
) {
    /** Multi-view grids (sessions with [SessionPurpose.MULTI_SLOT]). */
    MULTI_VIEW(null),

    /** Editing and concatenation, including saving and restoring projects. */
    EDIT(null),

    /** Manual masks and automatic tracking (face and object). */
    MASK_TRACKING(EDIT),

    /** Avatar replacement (REQ-ED-07), including the avatar tools (cut-out). */
    AVATAR(EDIT),

    /** Export of edit projects. */
    EXPORT(null),

    /** A feature this version does not know (wire fallback); never hidden and never gated. */
    UNKNOWN(null),
    ;

    /** Capability keys that this feature hides when it is [FeatureMode.HIDDEN]. */
    public val capabilityKeys: List<FeatureKey>
        get() = when (this) {
            MULTI_VIEW -> listOf(FeatureKey.MULTI_VIEW)
            EDIT -> listOf(FeatureKey.EDIT_CLIPS, FeatureKey.EDIT_CONCAT)
            MASK_TRACKING -> listOf(FeatureKey.MANUAL_MASK, FeatureKey.FACE_TRACKING, FeatureKey.OBJECT_TRACKING)
            EXPORT -> listOf(FeatureKey.EXPORT)
            AVATAR, UNKNOWN -> emptyList()
        }

    public companion object {
        /** The features a host can configure, in registry order (without [UNKNOWN]). */
        public val CONFIGURABLE: List<VideoKitFeature> = entries.filter { it != UNKNOWN }

        /** Maps a name to a feature; unknown or future names map to [UNKNOWN]. */
        public fun fromWireName(name: String?): VideoKitFeature = entries.firstOrNull { it.name == name } ?: UNKNOWN
    }
}

/** Static switch of a [VideoKitFeature] in [VideoKitConfig.features] (REQ-API-10 ①). */
public enum class FeatureMode {
    /** The feature is available (default for every feature not in the map). */
    ENABLED,

    /**
     * The feature is hidden: the UI shows no entry for it, every API call of it returns
     * [UnsupportedReason.FEATURE_DISABLED] or throws [ErrorCode.FEATURE_DISABLED], and the capability report lists it in
     * [VideoKitCapabilities.hiddenFeatures].
     */
    HIDDEN,
    ;

    public companion object {
        /** Maps a name to a mode; unknown names map to [ENABLED] (an unknown switch never hides a feature). */
        public fun fromWireName(name: String?): FeatureMode = entries.firstOrNull { it.name == name } ?: ENABLED
    }
}

/**
 * Marker the host wants on the entry of a feature (REQ-API-10 ②), for example a lock or "trial". The Kit shows no
 * text of its own: `videokit_ui` draws the marker and its localized label.
 */
public enum class FeatureBadge {
    /** Locked: the host will ask the user to subscribe or buy. */
    LOCK,

    /** Available during a trial. */
    TRIAL,

    /** Unknown marker (wire fallback); drawn as no marker. */
    UNKNOWN,
    ;

    public companion object {
        /** Maps a name to a badge; `null` stays `null`, unknown names map to [UNKNOWN]. */
        public fun fromWireName(name: String?): FeatureBadge? = name?.let { n -> entries.firstOrNull { it.name == n } ?: UNKNOWN }
    }
}

/** Answer of the dynamic feature gate [VideoKitHostCallbacks.checkFeature] (REQ-API-10 ②). */
public sealed interface FeatureAccess {
    /** Marker for the entry, or `null`. */
    public val badge: FeatureBadge?

    /** The feature may be used, optionally with a marker (for example [FeatureBadge.TRIAL]). */
    public data class Allowed(override val badge: FeatureBadge? = null) : FeatureAccess

    /**
     * The feature may not be used now. The host handles the user side itself (for example shows its paywall); the
     * Kit does not enter the feature and reports [UnsupportedReason.FEATURE_DENIED] or [ErrorCode.FEATURE_DENIED].
     */
    public data class Denied(override val badge: FeatureBadge? = FeatureBadge.LOCK) : FeatureAccess

    public companion object {
        /** Allowed without a marker: the answer of a host that does not implement the gate. */
        public val ALLOWED: FeatureAccess = Allowed()
    }
}
