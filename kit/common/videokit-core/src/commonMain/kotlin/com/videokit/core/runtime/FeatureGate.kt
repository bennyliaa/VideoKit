package com.videokit.core.runtime

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.FeatureAccess
import com.videokit.api.FeatureMode
import com.videokit.api.MaskStyle
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitFeature
import com.videokit.api.VideoKitStableError

/**
 * Static feature switches and the dynamic feature gate of one VideoKit instance (REQ-API-10, VK-A2). Every API entry
 * point of a feature goes through here, so hidden and denied features behave the same in the core Kit, the Fake and
 * the Flutter channel.
 *
 * - Static: [mode] is [FeatureMode.HIDDEN] when the feature or one of its parents is hidden; hidden features never ask
 *   the host.
 * - Dynamic: [check] asks the host through [ask] (which applies the callback timeout and returns `null` when the
 *   callback threw or timed out: denied without a marker). An [FeatureAccess.Allowed] answer is remembered per scope
 *   (edit project or session id) until [forget]; denied answers are not remembered, so the host can allow after a
 *   purchase.
 */
public class FeatureGate(
    modes: Map<VideoKitFeature, FeatureMode>,
    private val ask: suspend (VideoKitFeature, String?) -> FeatureAccess?,
) {
    private val hidden: Set<VideoKitFeature> = VideoKitFeature.CONFIGURABLE.filter { feature ->
        generateSequence(feature) { it.parent }.any { modes[it] == FeatureMode.HIDDEN }
    }.toSet()
    private val allowed = AtomicMap<String, Set<VideoKitFeature>>()

    /** Hidden features, parents included. */
    public val hiddenFeatures: Set<VideoKitFeature> get() = hidden

    /** Effective static mode of [feature]. */
    public fun mode(feature: VideoKitFeature): FeatureMode = if (feature in hidden) FeatureMode.HIDDEN else FeatureMode.ENABLED

    /** Throws [ErrorCode.FEATURE_DISABLED] at [stage] when [feature] is hidden. */
    public fun requireEnabled(feature: VideoKitFeature, stage: ErrorStage) {
        if (feature in hidden) throw VideoKitException(disabledError(feature, stage))
    }

    /**
     * The gate's answer for [feature] in [scopeId] (`null` = no project or session yet, never remembered). Throws
     * [ErrorCode.FEATURE_DISABLED] when the feature is hidden.
     */
    public suspend fun check(feature: VideoKitFeature, scopeId: String?, stage: ErrorStage = ErrorStage.CALLBACK): FeatureAccess {
        requireEnabled(feature, stage)
        if (feature == VideoKitFeature.UNKNOWN) return FeatureAccess.ALLOWED
        if (scopeId != null && allowed[scopeId].orEmpty().contains(feature)) return FeatureAccess.ALLOWED
        val access = ask(feature, scopeId) ?: FeatureAccess.Denied(badge = null)
        if (access is FeatureAccess.Allowed && scopeId != null) allowed.put(scopeId, allowed[scopeId].orEmpty() + feature)
        return access
    }

    /** Throws [ErrorCode.FEATURE_DISABLED] or [ErrorCode.FEATURE_DENIED] at [stage] unless [feature] may be used. */
    public suspend fun require(feature: VideoKitFeature, scopeId: String?, stage: ErrorStage) {
        val access = check(feature, scopeId, stage)
        if (access is FeatureAccess.Denied) throw VideoKitException(deniedError(feature, access, stage))
    }

    /**
     * For command results: `null` when [feature] may be used, otherwise [UnsupportedReason.FEATURE_DISABLED] or
     * [UnsupportedReason.FEATURE_DENIED].
     */
    public suspend fun unsupportedReason(feature: VideoKitFeature, scopeId: String?): UnsupportedReason? = when {
        feature in hidden -> UnsupportedReason.FEATURE_DISABLED
        check(feature, scopeId) is FeatureAccess.Denied -> UnsupportedReason.FEATURE_DENIED
        else -> null
    }

    /** The first of [features] that is hidden or denied, with its reason; `null` when all may be used. */
    public suspend fun firstUnsupported(features: Collection<VideoKitFeature>, scopeId: String?): UnsupportedReason? {
        features.firstOrNull { it in hidden }?.let { return UnsupportedReason.FEATURE_DISABLED }
        return features.firstNotNullOfOrNull { unsupportedReason(it, scopeId) }
    }

    /** Drops the remembered answers of [scopeId] (the project or session was released). */
    public fun forget(scopeId: String) {
        allowed.remove(scopeId)
    }

    /** [capabilities] with the hidden features and their keys marked [UnsupportedReason.FEATURE_DISABLED]. */
    public fun applyTo(capabilities: VideoKitCapabilities): VideoKitCapabilities {
        if (hidden.isEmpty()) return capabilities
        val keys = hidden.flatMap { it.capabilityKeys }.associateWith { UnsupportedReason.FEATURE_DISABLED }
        val edit = capabilities.editFeatures
        return capabilities.copy(
            hiddenFeatures = hidden,
            unavailableReasons = capabilities.unavailableReasons + keys,
            editFeatures = edit.copy(
                singleVideoClips = edit.singleVideoClips && VideoKitFeature.EDIT !in hidden,
                multiInputConcat = edit.multiInputConcat && VideoKitFeature.EDIT !in hidden,
                manualMasks = edit.manualMasks && VideoKitFeature.MASK_TRACKING !in hidden,
            ),
        )
    }

    public companion object {
        /** A gate without switches that allows everything (tests, hosts without REQ-API-10). */
        public val OPEN: FeatureGate = FeatureGate(emptyMap()) { _, _ -> FeatureAccess.ALLOWED }

        /**
         * Features an edit command uses, outermost first. [VideoKitEditCommand.CancelTracking] uses none: stopping work
         * is never gated. Undo, redo, snapshots and preview are not commands and are never gated either.
         */
        public fun featuresOf(command: VideoKitEditCommand): List<VideoKitFeature> = when (command) {
            is VideoKitEditCommand.AddClip,
            is VideoKitEditCommand.SplitAt,
            is VideoKitEditCommand.TrimClip,
            is VideoKitEditCommand.RemoveClip,
            is VideoKitEditCommand.MoveClip,
            -> listOf(VideoKitFeature.EDIT)

            is VideoKitEditCommand.AddMask,
            is VideoKitEditCommand.UpdateMaskKeyframe,
            is VideoKitEditCommand.RemoveMaskKeyframe,
            is VideoKitEditCommand.SetMaskEnabled,
            is VideoKitEditCommand.RemoveMask,
            -> listOf(VideoKitFeature.EDIT, VideoKitFeature.MASK_TRACKING)

            is VideoKitEditCommand.SetMaskStyle -> if (command.style == MaskStyle.IMAGE) {
                listOf(VideoKitFeature.EDIT, VideoKitFeature.AVATAR)
            } else {
                listOf(VideoKitFeature.EDIT, VideoKitFeature.MASK_TRACKING)
            }

            is VideoKitEditCommand.SetMaskAvatar -> listOf(VideoKitFeature.EDIT, VideoKitFeature.AVATAR)

            is VideoKitEditCommand.StartTracking,
            is VideoKitEditCommand.CorrectTracking,
            is VideoKitEditCommand.AcceptTrackingRange,
            -> listOf(VideoKitFeature.EDIT, VideoKitFeature.MASK_TRACKING)

            is VideoKitEditCommand.CancelTracking -> emptyList()
        }

        /** The [ErrorCode.FEATURE_DISABLED] error of [feature]. */
        public fun disabledError(feature: VideoKitFeature, stage: ErrorStage): VideoKitStableError = VideoKitStableError(
            code = ErrorCode.FEATURE_DISABLED,
            stage = stage,
            retryable = false,
            diagnostic = "FEATURE_HIDDEN:${feature.name}",
            params = mapOf(ErrorParams.FEATURE to feature.name),
        )

        /** The [ErrorCode.FEATURE_DENIED] error of [feature]; retryable, the host may allow later (after a purchase). */
        public fun deniedError(feature: VideoKitFeature, access: FeatureAccess.Denied, stage: ErrorStage): VideoKitStableError =
            VideoKitStableError(
                code = ErrorCode.FEATURE_DENIED,
                stage = stage,
                retryable = true,
                diagnostic = "FEATURE_DENIED:${feature.name}",
                params = buildMap {
                    put(ErrorParams.FEATURE, feature.name)
                    access.badge?.let { put(ErrorParams.BADGE, it.name) }
                },
            )
    }
}
