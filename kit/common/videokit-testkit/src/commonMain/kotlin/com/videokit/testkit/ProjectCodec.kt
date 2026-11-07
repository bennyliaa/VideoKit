package com.videokit.testkit

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
import com.videokit.testkit.internal.Errors
import com.videokit.testkit.internal.MiniJson
import com.videokit.testkit.internal.typeName

/** Serializable content of a Fake edit project (08 §2.1). */
internal data class ProjectModel(
    val projectId: String,
    val revision: Long,
    val createdAtMs: Long,
    val updatedAtMs: Long,
    val sources: List<EditSource>,
    val clips: List<Clip>,
    val masks: List<MaskTrack>,
    val tracking: Map<String, TrackingRun>,
    val exportPreset: ExportPreset?,
)

/**
 * Versioned JSON codec of [ProjectModel]. Reading ignores unknown fields (minor additions), fills
 * defaults for missing optional fields and rejects unknown future major versions (04 §10).
 */
internal object ProjectCodec {
    const val SCHEMA_VERSION: Int = SerializedEditProject.CURRENT_SCHEMA_VERSION

    fun encode(model: ProjectModel): SerializedEditProject = SerializedEditProject(
        schemaVersion = SCHEMA_VERSION,
        json = MiniJson.write(
            linkedMapOf(
                "schemaVersion" to SCHEMA_VERSION,
                "projectId" to model.projectId,
                "revision" to model.revision,
                "createdAt" to model.createdAtMs,
                "updatedAt" to model.updatedAtMs,
                "sources" to model.sources.map(::sourceToJson),
                "timeline" to mapOf("clips" to model.clips.map(::clipToJson)),
                "masks" to model.masks.map(::maskToJson),
                "tracking" to model.tracking.values.map(::trackingToJson),
                "exportPresetId" to model.exportPreset?.name,
            ),
        ),
    )

    fun decode(serialized: SerializedEditProject): ProjectModel {
        if (serialized.schemaVersion < 1 || serialized.schemaVersion > SCHEMA_VERSION) {
            throw VideoKitException(
                Errors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.EDIT, "UNSUPPORTED_SCHEMA_VERSION:${serialized.schemaVersion}"),
            )
        }
        val root = try {
            MiniJson.parse(serialized.json) as? Map<*, *> ?: error("root is not an object")
        } catch (failure: Exception) {
            throw VideoKitException(
                Errors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.EDIT, "SNAPSHOT_CORRUPT:${failure.typeName()}"),
            )
        }
        val payloadVersion = (root["schemaVersion"] as? Long)?.toInt() ?: serialized.schemaVersion
        if (payloadVersion != serialized.schemaVersion) {
            throw VideoKitException(Errors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.EDIT, "SCHEMA_VERSION_MISMATCH"))
        }
        return try {
            ProjectModel(
                projectId = root.string("projectId"),
                revision = root.long("revision", 0L),
                createdAtMs = root.long("createdAt", 0L),
                updatedAtMs = root.long("updatedAt", 0L),
                sources = root.list("sources").map { sourceFromJson(it as Map<*, *>) },
                clips = (root["timeline"] as? Map<*, *>)?.list("clips").orEmpty().map { clipFromJson(it as Map<*, *>) },
                masks = root.list("masks").map { maskFromJson(it as Map<*, *>) },
                tracking = root.list("tracking").map { trackingFromJson(it as Map<*, *>) }.associateBy { it.maskId },
                exportPreset = (root["exportPresetId"] as? String)?.let { name -> ExportPreset.entries.firstOrNull { it.name == name } },
            )
        } catch (failure: VideoKitException) {
            throw failure
        } catch (failure: Exception) {
            throw VideoKitException(
                Errors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.EDIT, "SNAPSHOT_CORRUPT:${failure.typeName()}"),
            )
        }
    }

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

    private fun sourceFromJson(json: Map<*, *>): EditSource = EditSource(
        sourceId = json.string("sourceId"),
        mediaToken = json.string("mediaToken"),
        displayName = json["displayName"] as? String,
        probe = (json["probe"] as? Map<*, *>)?.let { probe ->
            SourceProbe(
                durationUs = probe.long("durationUs", 0L),
                width = probe.long("width", 0L).toInt(),
                height = probe.long("height", 0L).toInt(),
                rotationDeg = probe.long("rotation", 0L).toInt(),
                frameRate = (probe["fps"] as? Number)?.toFloat(),
                videoCodec = probe["videoCodec"] as? String,
                audioCodec = probe["audioCodec"] as? String,
                hasAudio = probe["hasAudio"] as? Boolean ?: false,
            )
        },
    )

    private fun clipToJson(clip: Clip): Map<String, Any?> =
        linkedMapOf("clipId" to clip.clipId, "sourceId" to clip.sourceId, "inUs" to clip.inUs, "outUs" to clip.outUs)

    private fun clipFromJson(json: Map<*, *>): Clip =
        Clip(json.string("clipId"), json.string("sourceId"), json.long("inUs"), json.long("outUs"))

    private fun maskToJson(mask: MaskTrack): Map<String, Any?> = linkedMapOf(
        "maskId" to mask.maskId,
        "type" to mask.type.name,
        "style" to mask.style.name,
        "strength" to mask.strength,
        "enabled" to mask.enabled,
        "rangeUs" to listOf(mask.rangeUs.startUs, mask.rangeUs.endUs),
        "keyframes" to mask.keyframes.map { keyframe ->
            linkedMapOf(
                "atUs" to keyframe.atUs,
                "region" to regionToJson(keyframe.region),
                "source" to keyframe.source.name,
                "state" to keyframe.quality?.name,
            )
        },
    )

    private fun maskFromJson(json: Map<*, *>): MaskTrack {
        val range = json.list("rangeUs").map { (it as Number).toLong() }
        return MaskTrack(
            maskId = json.string("maskId"),
            type = MaskType.valueOf(json.string("type")),
            style = (json["style"] as? String)?.let { name -> MaskStyle.entries.firstOrNull { it.name == name } } ?: MaskStyle.MOSAIC,
            strength = (json["strength"] as? Number)?.toFloat() ?: 0.5f,
            enabled = json["enabled"] as? Boolean ?: true,
            rangeUs = TimeRangeUs(range[0], range[1]),
            keyframes = json.list("keyframes").map { item ->
                val keyframe = item as Map<*, *>
                MaskKeyframe(
                    atUs = keyframe.long("atUs"),
                    region = regionFromJson(keyframe["region"] as Map<*, *>),
                    source =
                    (keyframe["source"] as? String)?.let { name -> KeyframeSource.entries.firstOrNull { it.name == name } }
                        ?: KeyframeSource.USER,
                    quality = (keyframe["state"] as? String)?.let { name -> CoverageQuality.entries.firstOrNull { it.name == name } },
                )
            },
        )
    }

    private fun regionToJson(region: MaskRegion): Map<String, Any?> = linkedMapOf(
        "x" to region.x,
        "y" to region.y,
        "width" to region.width,
        "height" to region.height,
        "rotation" to region.rotationDeg,
    )

    private fun regionFromJson(json: Map<*, *>): MaskRegion = MaskRegion(
        x = (json["x"] as Number).toFloat(),
        y = (json["y"] as Number).toFloat(),
        width = (json["width"] as Number).toFloat(),
        height = (json["height"] as Number).toFloat(),
        rotationDeg = (json["rotation"] as? Number)?.toFloat() ?: 0f,
    )

    private fun trackingToJson(run: TrackingRun): Map<String, Any?> = linkedMapOf(
        "maskId" to run.maskId,
        "status" to run.status.name,
        "coverage" to run.coverage?.ranges?.map { range ->
            linkedMapOf("rangeUs" to listOf(range.rangeUs.startUs, range.rangeUs.endUs), "quality" to range.quality.name)
        },
    )

    private fun trackingFromJson(json: Map<*, *>): TrackingRun {
        val status = TrackingRunStatus.valueOf(json.string("status"))
        return TrackingRun(
            maskId = json.string("maskId"),
            // A run that was in progress when the snapshot was taken restarts from scratch (08 §6).
            status = if (status == TrackingRunStatus.RUNNING) TrackingRunStatus.CANCELLED else status,
            progress = null,
            coverage = (json["coverage"] as? List<*>)?.let { ranges ->
                CoverageReport(
                    ranges.map { item ->
                        val range = item as Map<*, *>
                        val bounds = range.list("rangeUs").map { (it as Number).toLong() }
                        CoverageRange(TimeRangeUs(bounds[0], bounds[1]), CoverageQuality.valueOf(range.string("quality")))
                    },
                )
            },
        )
    }

    private fun Map<*, *>.string(key: String): String = this[key] as? String ?: error("missing $key")

    private fun Map<*, *>.long(key: String, default: Long? = null): Long =
        (this[key] as? Number)?.toLong() ?: default ?: error("missing $key")

    private fun Map<*, *>.list(key: String): List<*> = this[key] as? List<*> ?: emptyList<Any?>()
}
