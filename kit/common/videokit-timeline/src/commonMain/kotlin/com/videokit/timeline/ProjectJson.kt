package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.CoverageQuality
import com.videokit.api.CoverageRange
import com.videokit.api.CoverageReport
import com.videokit.api.EditSource
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.ExportPreset
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskKeyframe
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskTrack
import com.videokit.api.MaskType
import com.videokit.api.SerializedEditProject
import com.videokit.api.SourceProbe
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingRun
import com.videokit.api.TrackingRunStatus
import com.videokit.api.VideoKitException
import com.videokit.core.runtime.StableErrors
import com.videokit.timeline.internal.MiniJson

/**
 * JSON codec of [ProjectDocument]: the edit project snapshot schema 1.0 of `spec/schema/edit-project.v1.json`
 * (04A E2, 08 §2.1), the single source for this codec and the Dart one. In short:
 * - writing (W1–W3): every property, `schemaVersion` [SCHEMA_VERSION] and `schemaMinor` [SCHEMA_MINOR]; ranges as
 *   `{startUs, endUs}`; no runtime state (tracking progress, probe mismatch flag); a running tracking run as CANCELLED;
 * - reading (R1–R6): the payload's `schemaVersion` (else the envelope's); a higher major is rejected, a lower one
 *   migrated through [SchemaMigrations]; any minor readable, unknown properties ignored, missing optional properties
 *   read as defaults, unknown enum values read as the schema's `x-unknown` value.
 *
 * Errors (thrown as [VideoKitException], stage EDIT):
 * - `UNSUPPORTED_SNAPSHOT_VERSION`, diagnostic `UNSUPPORTED_SCHEMA_VERSION:<n>`: a higher major or no migration path;
 * - `INVALID_ARGUMENT` (04A V7), diagnostic `SNAPSHOT_MALFORMED:<type>`: not a JSON object, a missing required
 *   property, a wrong type, or a failing migration. The snapshot content is never copied into a diagnostic.
 */
public object ProjectJson {
    /** Major version written by this Kit. */
    public const val SCHEMA_VERSION: Int = SerializedEditProject.CURRENT_SCHEMA_VERSION

    /** Minor version written by this Kit (04A E2 (b)). */
    public const val SCHEMA_MINOR: Int = 0

    /** Serializes [document]. */
    public fun encode(document: ProjectDocument): SerializedEditProject = SerializedEditProject(
        schemaVersion = SCHEMA_VERSION,
        json = MiniJson.write(toTree(document)),
    )

    /** Reads [serialized], migrating older versions with [migrations]. */
    public fun decode(serialized: SerializedEditProject, migrations: SchemaMigrations = SchemaMigrations.DEFAULT): ProjectDocument {
        if (serialized.schemaVersion > migrations.currentVersion) throw unsupported(serialized.schemaVersion)
        val root = malformedOnFailure { MiniJson.parse(serialized.json) as? Map<*, *> ?: error("root is not an object") }
        val payloadVersion = root["schemaVersion"]
        val version = when (payloadVersion) {
            null -> serialized.schemaVersion
            is Long -> payloadVersion.toInt()
            else -> throw malformed("ClassCastException")
        }
        if (!migrations.supports(version)) throw unsupported(version)
        @Suppress("UNCHECKED_CAST")
        val migrated = malformedOnFailure { migrations.migrate(version, root as Map<String, Any?>) }
        return malformedOnFailure { fromTree(migrated) }
    }

    // ------------------------------------------------------------------ errors

    private fun unsupported(version: Int): VideoKitException = VideoKitException(
        StableErrors.of(ErrorCode.UNSUPPORTED_SNAPSHOT_VERSION, ErrorStage.EDIT, "UNSUPPORTED_SCHEMA_VERSION:$version"),
    )

    private fun malformed(type: String): VideoKitException =
        VideoKitException(StableErrors.of(ErrorCode.INVALID_ARGUMENT, ErrorStage.EDIT, "SNAPSHOT_MALFORMED:$type"))

    private inline fun <T> malformedOnFailure(block: () -> T): T = try {
        block()
    } catch (failure: VideoKitException) {
        throw failure
    } catch (failure: Exception) {
        throw malformed(failure::class.simpleName ?: "Unknown")
    }

    // ------------------------------------------------------------------ writing

    internal fun toTree(document: ProjectDocument): Map<String, Any?> = linkedMapOf(
        "schemaVersion" to SCHEMA_VERSION,
        "schemaMinor" to SCHEMA_MINOR,
        "projectId" to document.projectId,
        "revision" to document.revision,
        "createdAt" to document.createdAtMs,
        "updatedAt" to document.updatedAtMs,
        "exportPresetId" to document.exportPreset?.name,
        "sources" to document.sources.map(::sourceToJson),
        "timeline" to mapOf("clips" to document.clips.map(::clipToJson)),
        "masks" to document.masks.map(::maskToJson),
        "tracking" to document.tracking.values.map(::trackingToJson),
    )

    private fun range(range: TimeRangeUs): Map<String, Any?> = linkedMapOf("startUs" to range.startUs, "endUs" to range.endUs)

    private fun sourceToJson(source: EditSource): Map<String, Any?> = linkedMapOf(
        "sourceId" to source.sourceId,
        "mediaToken" to source.mediaToken,
        "displayName" to source.displayName,
        "probe" to source.probe?.let { probe ->
            linkedMapOf(
                "durationUs" to probe.durationUs,
                "width" to probe.width,
                "height" to probe.height,
                "rotation" to probe.rotationDeg,
                "fps" to probe.frameRate,
                "videoCodec" to probe.videoCodec,
                "audioCodec" to probe.audioCodec,
                "hasAudio" to probe.hasAudio,
            )
        },
    )

    private fun clipToJson(clip: Clip): Map<String, Any?> =
        linkedMapOf("clipId" to clip.clipId, "sourceId" to clip.sourceId, "inUs" to clip.inUs, "outUs" to clip.outUs)

    private fun maskToJson(mask: MaskTrack): Map<String, Any?> = linkedMapOf(
        "maskId" to mask.maskId,
        "type" to mask.type.name,
        "style" to mask.style.name,
        "strength" to mask.strength,
        "enabled" to mask.enabled,
        "rangeUs" to range(mask.rangeUs),
        "keyframes" to mask.keyframes.map { keyframe ->
            linkedMapOf(
                "atUs" to keyframe.atUs,
                "region" to regionToJson(keyframe.region),
                "source" to keyframe.source.name,
                "state" to keyframe.quality?.name,
            )
        },
        "acceptedRanges" to mask.acceptedRangesUs.map(::range),
    )

    private fun regionToJson(region: MaskRegion): Map<String, Any?> = linkedMapOf(
        "x" to region.x,
        "y" to region.y,
        "width" to region.width,
        "height" to region.height,
        "rotation" to region.rotationDeg,
    )

    private fun trackingToJson(run: TrackingRun): Map<String, Any?> = linkedMapOf(
        "maskId" to run.maskId,
        // W3: a run in progress restarts after restore (08 §6).
        "status" to (if (run.status == TrackingRunStatus.RUNNING) TrackingRunStatus.CANCELLED else run.status).name,
        "coverage" to run.coverage?.ranges.orEmpty().map { item ->
            linkedMapOf("startUs" to item.rangeUs.startUs, "endUs" to item.rangeUs.endUs, "quality" to item.quality.name)
        },
    )

    // ------------------------------------------------------------------ reading (schema 1)

    internal fun fromTree(root: Map<String, Any?>): ProjectDocument {
        val timeline = root.optObject("timeline")
        return ProjectDocument(
            projectId = root.requiredString("projectId"),
            revision = root.optLong("revision", 0L),
            createdAtMs = root.optLong("createdAt", 0L),
            updatedAtMs = root.optLong("updatedAt", 0L),
            sources = root.optObjects("sources").map(::sourceFromJson),
            clips = timeline?.optObjects("clips").orEmpty().map(::clipFromJson),
            masks = root.optObjects("masks").map(::maskFromJson),
            tracking = root.optObjects("tracking").map(::trackingFromJson).associateBy { it.maskId },
            exportPreset = root.optString("exportPresetId")?.let { name -> ExportPreset.entries.firstOrNull { it.name == name } },
        )
    }

    private fun sourceFromJson(json: Map<*, *>): EditSource = EditSource(
        sourceId = json.requiredString("sourceId"),
        mediaToken = json.requiredString("mediaToken"),
        displayName = json.optString("displayName"),
        probe = json.optObject("probe")?.let { probe ->
            SourceProbe(
                durationUs = probe.optLong("durationUs", 0L),
                width = probe.optLong("width", 0L).toInt(),
                height = probe.optLong("height", 0L).toInt(),
                rotationDeg = probe.optLong("rotation", 0L).toInt(),
                frameRate = probe.optNumber("fps")?.toFloat(),
                videoCodec = probe.optString("videoCodec")?.takeIf { it.isNotEmpty() },
                audioCodec = probe.optString("audioCodec")?.takeIf { it.isNotEmpty() },
                hasAudio = probe.optBoolean("hasAudio", false),
            )
        },
    )

    private fun clipFromJson(json: Map<*, *>): Clip =
        Clip(json.requiredString("clipId"), json.requiredString("sourceId"), json.requiredLong("inUs"), json.requiredLong("outUs"))

    private fun maskFromJson(json: Map<*, *>): MaskTrack = MaskTrack(
        maskId = json.requiredString("maskId"),
        type = json.enumOr("type", MaskType.entries, MaskType.MANUAL, required = true),
        style = json.enumOr("style", MaskStyle.entries, MaskStyle.MOSAIC),
        strength = json.optNumber("strength")?.toFloat() ?: DEFAULT_STRENGTH,
        enabled = json.optBoolean("enabled", true),
        rangeUs = rangeFromJson(json.optObject("rangeUs") ?: error("missing rangeUs")),
        keyframes = json.optObjects("keyframes").map { keyframe ->
            MaskKeyframe(
                atUs = keyframe.requiredLong("atUs"),
                region = regionFromJson(keyframe.optObject("region") ?: error("missing region")),
                source = keyframe.enumOr("source", KeyframeSource.entries, KeyframeSource.USER),
                quality = keyframe.optString("state")?.let { quality(it) },
            )
        },
        acceptedRangesUs = json.optObjects("acceptedRanges").map(::rangeFromJson),
    )

    private fun rangeFromJson(json: Map<*, *>): TimeRangeUs = TimeRangeUs(json.requiredLong("startUs"), json.requiredLong("endUs"))

    private fun regionFromJson(json: Map<*, *>): MaskRegion = MaskRegion(
        x = json.requiredNumber("x").toFloat(),
        y = json.requiredNumber("y").toFloat(),
        width = json.requiredNumber("width").toFloat(),
        height = json.requiredNumber("height").toFloat(),
        rotationDeg = json.optNumber("rotation")?.toFloat() ?: 0f,
    )

    private fun trackingFromJson(json: Map<*, *>): TrackingRun {
        val status = json.enumOr("status", TrackingRunStatus.entries, TrackingRunStatus.FAILED, required = true)
        return TrackingRun(
            maskId = json.requiredString("maskId"),
            // R6: a running run (only in hand-made data) restarts like one written by W3.
            status = if (status == TrackingRunStatus.RUNNING) TrackingRunStatus.CANCELLED else status,
            progress = null,
            // No coverage (written as an empty list) reads as no report.
            coverage = json.optObjects("coverage").map { item ->
                CoverageRange(
                    TimeRangeUs(item.requiredLong("startUs"), item.requiredLong("endUs")),
                    quality(item.requiredString("quality")),
                )
            }.takeIf { it.isNotEmpty() }?.let(::CoverageReport),
        )
    }

    /** R4: unknown qualities read as NOT_ANALYZED (never counts as covered). */
    private fun quality(name: String): CoverageQuality =
        CoverageQuality.entries.firstOrNull { it.name == name } ?: CoverageQuality.NOT_ANALYZED

    private const val DEFAULT_STRENGTH = 0.5f

    // ------------------------------------------------------------------ typed access (R3: wrong types are malformed)

    private fun Map<*, *>.requiredString(key: String): String = optString(key) ?: error("missing $key")

    private fun Map<*, *>.optString(key: String): String? = when (val value = this[key]) {
        null -> null
        is String -> value
        else -> error("$key is not a string")
    }

    private fun Map<*, *>.requiredLong(key: String): Long = optLongOrNull(key) ?: error("missing $key")

    private fun Map<*, *>.optLong(key: String, default: Long): Long = optLongOrNull(key) ?: default

    private fun Map<*, *>.optLongOrNull(key: String): Long? = when (val value = this[key]) {
        null -> null
        is Long -> value
        else -> error("$key is not an integer")
    }

    private fun Map<*, *>.requiredNumber(key: String): Number = optNumber(key) ?: error("missing $key")

    private fun Map<*, *>.optNumber(key: String): Number? = when (val value = this[key]) {
        null -> null
        is Number -> value
        else -> error("$key is not a number")
    }

    private fun Map<*, *>.optBoolean(key: String, default: Boolean): Boolean = when (val value = this[key]) {
        null -> default
        is Boolean -> value
        else -> error("$key is not a boolean")
    }

    private fun Map<*, *>.optObject(key: String): Map<*, *>? = when (val value = this[key]) {
        null -> null
        is Map<*, *> -> value
        else -> error("$key is not an object")
    }

    private fun Map<*, *>.optObjects(key: String): List<Map<*, *>> = when (val value = this[key]) {
        null -> emptyList()
        is List<*> -> value.map { it as? Map<*, *> ?: error("$key item is not an object") }
        else -> error("$key is not an array")
    }

    private fun <E : Enum<E>> Map<*, *>.enumOr(key: String, entries: List<E>, unknown: E, required: Boolean = false): E {
        val name = if (required) requiredString(key) else optString(key) ?: return unknown
        return entries.firstOrNull { it.name == name } ?: unknown
    }
}
