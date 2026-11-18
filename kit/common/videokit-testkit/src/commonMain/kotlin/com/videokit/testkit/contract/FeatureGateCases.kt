package com.videokit.testkit.contract

import com.videokit.api.CapabilityRequest
import com.videokit.api.EditCommandResult
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.FeatureAccess
import com.videokit.api.FeatureBadge
import com.videokit.api.FeatureKey
import com.videokit.api.FeatureMode
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.SessionPurpose
import com.videokit.api.TimeRangeUs
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitFeature
import com.videokit.api.VideoKitSessionConfig
import com.videokit.testkit.CallbackMode
import com.videokit.testkit.RecordingOutputSink

/**
 * Feature switch and feature gate cases (REQ-API-10, VK-A2; FT01B-01..03): a hidden feature is rejected without asking
 * the host, a denied feature is rejected, a host without the gate behaves as before, and other features are unaffected.
 */
internal fun featureGateCases(): List<ContractCase> = listOf(
    gateCase("features.no_gate_allows", "a host without checkFeature allows every feature without a marker") {
        for (feature in VideoKitFeature.CONFIGURABLE) {
            expectEquals(FeatureMode.ENABLED, kit.featureMode(feature), "featureMode $feature")
            expectEquals(FeatureAccess.ALLOWED, kit.checkFeature(feature), "checkFeature $feature")
        }
        expect(kit.capabilities(CapabilityRequest()).hiddenFeatures.isEmpty()) { "hiddenFeatures without switches" }
        val slot = kit.createSession(VideoKitSessionConfig(purpose = SessionPurpose.MULTI_SLOT))
        expectEquals(VideoKitCommandResult.Executed, slot.bind(subject.playableVideo("gate-open"), null, emptyList()), "multi-slot bind")
        slot.release()
    },
    gateCase(
        "features.hidden_multi_view",
        "a hidden multi-view rejects multi-slot sessions without asking the host; single sessions are unaffected",
        ContractFeature.FEATURE_SWITCHES,
    ) {
        withFeatures(mapOf(VideoKitFeature.MULTI_VIEW to FeatureMode.HIDDEN)) { hidden ->
            expectEquals(FeatureMode.HIDDEN, hidden.featureMode(VideoKitFeature.MULTI_VIEW), "featureMode")
            expectEquals(FeatureMode.ENABLED, hidden.featureMode(VideoKitFeature.EDIT), "featureMode EDIT")
            expectFeatureError(ErrorCode.FEATURE_DISABLED, VideoKitFeature.MULTI_VIEW, "createSession MULTI_SLOT") {
                hidden.createSession(VideoKitSessionConfig(purpose = SessionPurpose.MULTI_SLOT))
            }
            expectFeatureError(ErrorCode.FEATURE_DISABLED, VideoKitFeature.MULTI_VIEW, "checkFeature") {
                hidden.checkFeature(VideoKitFeature.MULTI_VIEW)
            }
            val caps = hidden.capabilities(CapabilityRequest())
            expectEquals(setOf(VideoKitFeature.MULTI_VIEW), caps.hiddenFeatures, "hiddenFeatures")
            expectEquals(UnsupportedReason.FEATURE_DISABLED, caps.unavailableReasons[FeatureKey.MULTI_VIEW], "unavailable MULTI_VIEW")
            val single = hidden.createSession(VideoKitSessionConfig())
            val bound = single.bind(subject.playableVideo("gate-single"), null, emptyList())
            expectEquals(VideoKitCommandResult.Executed, bound, "single bind")
            single.release()
            expect(callbacks.featureChecks.none { it.first == VideoKitFeature.MULTI_VIEW }) { "host asked for a hidden feature" }
        }
    },
    gateCase("features.denied_multi_view", "a denied multi-view slot is not bound; a later allow is not blocked") {
        callbacks.featureAnswer = { feature, _ ->
            if (feature == VideoKitFeature.MULTI_VIEW) FeatureAccess.Denied(FeatureBadge.LOCK) else FeatureAccess.ALLOWED
        }
        expectEquals(FeatureAccess.Denied(FeatureBadge.LOCK), kit.checkFeature(VideoKitFeature.MULTI_VIEW), "checkFeature")
        val slot = kit.createSession(VideoKitSessionConfig(purpose = SessionPurpose.MULTI_SLOT))
        expectEquals(
            VideoKitCommandResult.Unsupported(UnsupportedReason.FEATURE_DENIED),
            slot.bind(subject.playableVideo("gate-denied"), null, emptyList()),
            "denied bind",
        )
        val single = kit.createSession(VideoKitSessionConfig())
        expectEquals(VideoKitCommandResult.Executed, single.bind(subject.playableVideo("gate-single"), null, emptyList()), "single bind")
        // The host allows after its paywall: denied answers are not remembered.
        callbacks.featureAnswer = { _, _ -> FeatureAccess.Allowed(FeatureBadge.TRIAL) }
        expectEquals(VideoKitCommandResult.Executed, slot.bind(subject.playableVideo("gate-denied"), null, emptyList()), "bind after allow")
        expect(callbacks.featureChecks.contains(VideoKitFeature.MULTI_VIEW to slot.sessionId)) { "gate asked without the session id" }
        slot.release()
        single.release()
    },
    gateCase("features.gate_failure_denies", "a gate callback that throws counts as denied without a marker") {
        callbacks.overrideMode("checkFeature", CallbackMode.THROW)
        expectEquals(FeatureAccess.Denied(badge = null), kit.checkFeature(VideoKitFeature.MULTI_VIEW), "checkFeature")
        val slot = kit.createSession(VideoKitSessionConfig(purpose = SessionPurpose.MULTI_SLOT))
        expectEquals(
            VideoKitCommandResult.Unsupported(UnsupportedReason.FEATURE_DENIED),
            slot.bind(subject.playableVideo("gate-throws"), null, emptyList()),
            "bind",
        )
        slot.release()
    },
    gateCase(
        "features.hidden_edit",
        "a hidden edit hides masks and avatars and rejects creating and restoring projects; export and multi-view stay",
        ContractFeature.FEATURE_SWITCHES,
        ContractFeature.EDITING,
    ) {
        val snapshot = kit.createEditProject(EditProjectConfig()).let { project ->
            project.addSource(subject.playableVideo("gate-edit"))
            project.snapshot().also { project.close() }
        }
        withFeatures(mapOf(VideoKitFeature.EDIT to FeatureMode.HIDDEN)) { hidden ->
            val all = setOf(VideoKitFeature.EDIT, VideoKitFeature.MASK_TRACKING, VideoKitFeature.AVATAR)
            for (feature in VideoKitFeature.CONFIGURABLE) {
                val want = if (feature in all) FeatureMode.HIDDEN else FeatureMode.ENABLED
                expectEquals(want, hidden.featureMode(feature), "featureMode $feature")
            }
            expectEquals(all, hidden.capabilities(CapabilityRequest()).hiddenFeatures, "hiddenFeatures")
            expectFeatureError(ErrorCode.FEATURE_DISABLED, VideoKitFeature.EDIT, "createEditProject") {
                hidden.createEditProject(EditProjectConfig())
            }
            expectFeatureError(ErrorCode.FEATURE_DISABLED, VideoKitFeature.EDIT, "restoreEditProject") {
                hidden.restoreEditProject(snapshot, EditProjectConfig())
            }
        }
    },
    gateCase(
        "features.hidden_export",
        "a hidden export fails the precheck and the export before the sink is opened; editing still works",
        ContractFeature.FEATURE_SWITCHES,
        ContractFeature.EDITING,
    ) {
        withFeatures(mapOf(VideoKitFeature.EXPORT to FeatureMode.HIDDEN)) { hidden ->
            val project = clipProject(hidden, "gate-export")
            val sink = RecordingOutputSink()
            val precheck = project.checkExport(VideoKitExportRequest(), sink)
            expect(!precheck.ok && precheck.problems.any { it.code == ErrorCode.FEATURE_DISABLED }) { "precheck $precheck" }
            val failed = project.export(VideoKitExportRequest(), sink) as? VideoKitExportResult.Failed
            expectEquals(ErrorCode.FEATURE_DISABLED, failed?.error?.code, "export")
            expectEquals(VideoKitFeature.EXPORT.name, failed?.error?.params?.get(ErrorParams.FEATURE), "export feature param")
            expect(sink.openRequests.isEmpty()) { "sink opened for a hidden export" }
            project.close()
        }
    },
    gateCase(
        "features.denied_mask",
        "denied masks return Unsupported(FEATURE_DENIED); clip commands still apply; an allowed answer is asked once",
        ContractFeature.EDITING,
    ) {
        callbacks.featureAnswer = { feature, _ ->
            if (feature == VideoKitFeature.MASK_TRACKING) FeatureAccess.Denied(FeatureBadge.LOCK) else FeatureAccess.ALLOWED
        }
        val project = clipProject(kit, "gate-mask")
        val addMask = VideoKitEditCommand.AddMask(MaskType.MANUAL, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f), TimeRangeUs(0L, 1_000_000L))
        expectEquals(EditCommandResult.Unsupported(UnsupportedReason.FEATURE_DENIED), project.apply(addMask), "denied AddMask")
        expect(project.state.value.masks.isEmpty()) { "mask added while denied" }
        val clip = project.state.value.timeline.clips.single()
        val split = project.apply(VideoKitEditCommand.SplitAt(clip.clipId, clip.inUs + clip.durationUs / 2))
        expect(split is EditCommandResult.Applied) { "clip command while masks are denied returned $split" }
        callbacks.featureAnswer = null
        expect(project.apply(addMask) is EditCommandResult.Applied) { "AddMask after allow" }
        expect(project.apply(addMask) is EditCommandResult.Applied) { "second AddMask" }
        val maskChecks = callbacks.featureChecks.count { it == (VideoKitFeature.MASK_TRACKING to project.projectId) }
        // One denied and one allowed answer; the allowed one is remembered for the project.
        expectEquals(2, maskChecks, "MASK_TRACKING gate calls")
        project.close()
    },
    gateCase(
        "features.denied_edit",
        "a denied edit rejects adding sources with FEATURE_DENIED and the host's badge",
        ContractFeature.EDITING,
    ) {
        callbacks.featureAnswer = { feature, _ ->
            if (feature == VideoKitFeature.EDIT) FeatureAccess.Denied(FeatureBadge.LOCK) else FeatureAccess.ALLOWED
        }
        val project = kit.createEditProject(EditProjectConfig())
        val error = expectFeatureError(ErrorCode.FEATURE_DENIED, VideoKitFeature.EDIT, "addSource") {
            project.addSource(subject.playableVideo("gate-edit-denied"))
        }
        expectEquals(FeatureBadge.LOCK.name, error.params[ErrorParams.BADGE], "badge param")
        expect(error.retryable) { "FEATURE_DENIED must be retryable" }
        expect(project.state.value.timeline.sources.isEmpty()) { "source added while denied" }
        project.close()
    },
)

private fun gateCase(id: String, description: String, vararg requires: ContractFeature, body: suspend ContractScope.() -> Unit) =
    ContractCase(id, ContractGroup.FEATURE_GATE, description, requires.toSet(), body)

/** Runs [block] on an extra instance with [features] (sharing the scope's recording callbacks), then closes it. */
private suspend fun ContractScope.withFeatures(features: Map<VideoKitFeature, FeatureMode>, block: suspend (VideoKit) -> Unit) {
    val other = subject.create(callbacks, features) ?: throw ContractViolation("subject declares FEATURE_SWITCHES but cannot create")
    try {
        block(other)
    } finally {
        other.close()
    }
}

private suspend fun ContractScope.clipProject(on: VideoKit, token: String): VideoKitEditProject {
    val project = on.createEditProject(EditProjectConfig())
    val source = project.addSource(subject.playableVideo(token))
    val duration = project.state.value.timeline.sources.first { it.sourceId == source.sourceId }.probe?.durationUs
        ?: throw ContractViolation("no probe for $token")
    val added = project.apply(VideoKitEditCommand.AddClip(source.sourceId, 0L, minOf(duration, 3_000_000L)))
    expect(added is EditCommandResult.Applied) { "AddClip returned $added" }
    return project
}

/** Runs [block], which must throw [VideoKitException] with [code] and the `feature` param of [feature]; returns the error. */
private suspend fun expectFeatureError(
    code: ErrorCode,
    feature: VideoKitFeature,
    what: String,
    block: suspend () -> Any?,
): com.videokit.api.VideoKitStableError {
    val error = try {
        block()
        throw ContractViolation("$what did not throw $code")
    } catch (failure: VideoKitException) {
        failure.error
    }
    expectEquals(code, error.code, "$what code")
    expectEquals(feature.name, error.params[ErrorParams.FEATURE], "$what feature param")
    return error
}
