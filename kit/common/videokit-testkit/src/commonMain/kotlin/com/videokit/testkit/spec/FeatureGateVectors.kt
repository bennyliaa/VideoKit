package com.videokit.testkit.spec

import com.videokit.api.CapabilityRequest
import com.videokit.api.EditCommandResult
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorParams
import com.videokit.api.FeatureAccess
import com.videokit.api.FeatureBadge
import com.videokit.api.FeatureMode
import com.videokit.api.MaskAvatar
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskType
import com.videokit.api.SessionPurpose
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingKind
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
import com.videokit.api.VideoKitStableError
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.RecordingOutputSink
import com.videokit.testkit.contract.ContractFeature
import com.videokit.testkit.contract.VideoKitContractSubject
import com.videokit.testkit.internal.MiniJson

/** One case of `spec/vectors/features/feature-gate.json` (REQ-API-10). */
public class FeatureGateVector internal constructor(
    /** Case id. */
    public val id: String,
    internal val features: Map<VideoKitFeature, FeatureMode>,
    internal val gate: Map<String, String>?,
    internal val requires: Set<ContractFeature>,
    internal val steps: List<Map<*, *>>,
) {
    override fun toString(): String = id
}

/**
 * Runner of the feature switch and feature gate vectors (REQ-API-10, VK-A2) against a [VideoKitContractSubject]: the
 * Kotlin Fake runs every case, the core runtime the cases without editing. Dart runs the same file. A failed
 * expectation throws [IllegalStateException] naming the case and step.
 */
public object FeatureGateVectors {
    /** Expected `kind` of the file. */
    public const val KIND: String = "feature-gate"

    /** Parses a vector file. Unknown feature names are dropped and unknown modes read as ENABLED, as in a host config. */
    public fun parse(json: String): List<FeatureGateVector> {
        val root = MiniJson.parse(json) as? Map<*, *> ?: throw IllegalArgumentException("vector file is not an object")
        require(root["kind"] == KIND) { "unexpected kind ${root["kind"]}" }
        return (root["cases"] as List<*>).map { raw ->
            val case = raw as Map<*, *>
            val features = (case["features"] as Map<*, *>?).orEmpty()
                .map { (name, mode) -> VideoKitFeature.fromWireName(name as String) to FeatureMode.fromWireName(mode as String?) }
                .filter { it.first != VideoKitFeature.UNKNOWN }
                .toMap()
            FeatureGateVector(
                id = case["id"] as String,
                features = features,
                gate = (case["gate"] as Map<*, *>?)?.map { (k, v) -> k as String to v as String }?.toMap(),
                requires = (case["requires"] as List<*>?).orEmpty().map { ContractFeature.valueOf(it as String) }.toSet(),
                steps = (case["steps"] as List<*>).map { it as Map<*, *> },
            )
        }
    }

    /**
     * Runs [vector] on an instance of [subject]. Returns [VectorOutcome.SKIPPED] when the subject lacks a required
     * feature or cannot take the switches.
     */
    public suspend fun run(vector: FeatureGateVector, subject: VideoKitContractSubject): VectorOutcome {
        if (!subject.features.containsAll(vector.requires)) return VectorOutcome.SKIPPED
        val callbacks = RecordingHostCallbacks()
        vector.gate?.let { gate -> callbacks.featureAnswer = { feature, _ -> answer(gate[feature.name] ?: gate["*"] ?: "ALLOWED") } }
        val kit = if (vector.features.isEmpty()) {
            subject.create(callbacks)
        } else {
            if (ContractFeature.FEATURE_SWITCHES !in subject.features) return VectorOutcome.SKIPPED
            subject.create(callbacks, vector.features) ?: return VectorOutcome.SKIPPED
        }
        try {
            Run(vector, subject, kit, callbacks).steps()
        } finally {
            kit.close()
        }
        return VectorOutcome.PASSED
    }

    private fun answer(text: String): FeatureAccess {
        val (kind, badge) = text.split(':', limit = 2).let { it[0] to it.getOrNull(1)?.let(FeatureBadge::fromWireName) }
        return when (kind) {
            "ALLOWED" -> FeatureAccess.Allowed(badge)
            "DENIED" -> FeatureAccess.Denied(badge)
            "THROW" -> throw IllegalStateException("feature gate failed (vector)")
            else -> throw IllegalArgumentException("unknown gate answer $text")
        }
    }

    private class Run(
        val vector: FeatureGateVector,
        val subject: VideoKitContractSubject,
        val kit: VideoKit,
        val callbacks: RecordingHostCallbacks,
    ) {
        var project: VideoKitEditProject? = null
        var sourceId: String? = null
        var lastMaskId: String? = null

        suspend fun steps() {
            vector.steps.forEachIndexed { index, step ->
                val where = "${vector.id} step $index (${step["op"]})"
                val expected = step["expect"]
                val actual: Any? = when (val op = step["op"]) {
                    "featureMode" -> kit.featureMode(feature(step)).name
                    "checkFeature" -> outcome { access(kit.checkFeature(feature(step))) }
                    "hiddenFeatures" -> hidden(where)
                    "createEditProject" -> outcome {
                        project = kit.createEditProject(EditProjectConfig())
                        "OK"
                    }
                    "addSource" -> outcome {
                        sourceId = project(where).addSource(subject.playableVideo("gate-${vector.id}")).sourceId
                        "OK"
                    }
                    "edit" -> edit(step["command"] as String, where)
                    "detectCandidates" -> project(where).detectCandidates(0L).error?.let { "ERROR:${it.code.name}" } ?: "OK"
                    "checkExport" -> project(where).checkExport(VideoKitExportRequest(), RecordingOutputSink()).let { precheck ->
                        if (precheck.ok) "OK" else "PROBLEM:${precheck.problems.firstOrNull()?.code?.name}"
                    }
                    "export" -> export(where)
                    "singleBind" -> bind(SessionPurpose.SINGLE)
                    "multiSlotBind" -> bind(SessionPurpose.MULTI_SLOT)
                    "gateCalls" -> callbacks.featureChecks.count { it.first == feature(step) }
                    else -> throw IllegalArgumentException("$where: unknown op $op")
                }
                val want = when (expected) {
                    is Number -> expected.toInt()
                    is List<*> -> expected.toSet()
                    else -> expected
                }
                check(want == actual) { "$where: expected <$want> but was <$actual>" }
            }
        }

        fun feature(step: Map<*, *>): VideoKitFeature = VideoKitFeature.valueOf(step["feature"] as String)

        fun project(where: String): VideoKitEditProject = project ?: throw IllegalStateException("$where: no project")

        fun access(access: FeatureAccess): String {
            val kind = if (access is FeatureAccess.Allowed) "ALLOWED" else "DENIED"
            return access.badge?.let { "$kind:${it.name}" } ?: kind
        }

        suspend fun hidden(where: String): Set<String> {
            val caps = kit.capabilities(CapabilityRequest())
            for (feature in caps.hiddenFeatures) {
                for (key in feature.capabilityKeys) {
                    check(caps.unavailableReasons[key] == UnsupportedReason.FEATURE_DISABLED) { "$where: $key not FEATURE_DISABLED" }
                }
            }
            return caps.hiddenFeatures.map { it.name }.toSet()
        }

        suspend fun edit(command: String, where: String): String {
            val p = project(where)
            val mask = lastMaskId ?: "none"
            val cmd = when (command) {
                "ADD_CLIP" -> {
                    val source = sourceId ?: throw IllegalStateException("$where: no source")
                    val duration = p.state.value.timeline.sources.first { it.sourceId == source }.probe?.durationUs ?: 1_000_000L
                    VideoKitEditCommand.AddClip(source, 0L, minOf(duration, 3_000_000L))
                }
                "SPLIT" -> p.state.value.timeline.clips.first().let { VideoKitEditCommand.SplitAt(it.clipId, it.inUs + it.durationUs / 2) }
                "ADD_MASK" -> VideoKitEditCommand.AddMask(MaskType.MANUAL, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f), TimeRangeUs(0L, 1_000_000L))
                "SET_STYLE_BLUR" -> VideoKitEditCommand.SetMaskStyle(mask, MaskStyle.BLUR, 0.5f)
                "SET_STYLE_IMAGE" -> VideoKitEditCommand.SetMaskStyle(mask, MaskStyle.IMAGE, 0.5f)
                "SET_MASK_AVATAR" -> VideoKitEditCommand.SetMaskAvatar(mask, MaskAvatar("builtin:1"))
                "START_TRACKING" -> VideoKitEditCommand.StartTracking(mask, TrackingKind.FACE)
                else -> throw IllegalArgumentException("$where: unknown command $command")
            }
            return when (val result = p.apply(cmd)) {
                is EditCommandResult.Applied -> {
                    if (cmd is VideoKitEditCommand.AddMask) lastMaskId = result.createdId
                    "APPLIED"
                }
                is EditCommandResult.Unsupported -> "UNSUPPORTED:${result.reason.name}"
                is EditCommandResult.Rejected -> "REJECTED:${result.error.code.name}"
                EditCommandResult.ProjectReleased -> "PROJECT_RELEASED"
            }
        }

        suspend fun export(where: String): String {
            val sink = RecordingOutputSink()
            return when (val result = project(where).export(VideoKitExportRequest(), sink)) {
                is VideoKitExportResult.Succeeded -> "SUCCEEDED"
                is VideoKitExportResult.Failed -> {
                    check(sink.openRequests.isEmpty() || result.error.code.name !in FEATURE_CODES) { "$where: sink opened" }
                    "FAILED:${result.error.code.name}"
                }
                is VideoKitExportResult.Cancelled -> "CANCELLED"
            }
        }

        suspend fun bind(purpose: SessionPurpose): String = outcome {
            val session = kit.createSession(VideoKitSessionConfig(purpose = purpose))
            try {
                when (val result = session.bind(subject.playableVideo("gate-bind"), null, emptyList())) {
                    VideoKitCommandResult.Executed -> "EXECUTED"
                    is VideoKitCommandResult.Unsupported -> "UNSUPPORTED:${result.reason.name}"
                    else -> result.toString()
                }
            } finally {
                session.release()
            }
        }

        /** [block]'s value, or the code (and badge) of a thrown [VideoKitException]. */
        suspend fun outcome(block: suspend () -> String): String = try {
            block()
        } catch (failure: VideoKitException) {
            errorText(failure.error)
        }

        fun errorText(error: VideoKitStableError): String =
            error.params[ErrorParams.BADGE]?.let { "${error.code.name}:$it" } ?: error.code.name
    }

    private val FEATURE_CODES = setOf("FEATURE_DISABLED", "FEATURE_DENIED")
}
