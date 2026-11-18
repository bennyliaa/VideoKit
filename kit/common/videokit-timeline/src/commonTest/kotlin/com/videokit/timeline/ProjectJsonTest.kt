package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.CoverageQuality
import com.videokit.api.CoverageRange
import com.videokit.api.CoverageReport
import com.videokit.api.EditSource
import com.videokit.api.ErrorCode
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
import com.videokit.timeline.internal.MiniJson
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class ProjectJsonTest {
    private val document = ProjectDocument(
        projectId = "p-1",
        revision = 12,
        createdAtMs = 1_000,
        updatedAtMs = 2_000,
        sources = listOf(
            EditSource(
                "src-1",
                "media-1",
                "a \"quoted\" name\n",
                SourceProbe(10_000_000, 1920, 1080, 90, 29.97f, "video/avc", "audio/mp4a-latm", hasAudio = true),
            ),
            EditSource("src-2", "media-2", probe = null),
        ),
        clips = listOf(Clip("clip-3", "src-1", 0, 3_000_000), Clip("clip-4", "src-1", 5_000_000, 6_000_000)),
        masks = listOf(
            MaskTrack(
                maskId = "mask-5",
                type = MaskType.FACE,
                style = MaskStyle.BLUR,
                strength = 0.33f,
                enabled = false,
                rangeUs = TimeRangeUs(0, 2_000_000),
                keyframes = listOf(
                    MaskKeyframe(0, MaskRegion(0.1f, 0.2f, 0.3f, 0.4f, 15f)),
                    MaskKeyframe(1_000_000, MaskRegion(0.2f, 0.2f, 0.3f, 0.4f), KeyframeSource.TRACKER, CoverageQuality.LOW_CONFIDENCE),
                ),
                acceptedRangesUs = listOf(TimeRangeUs(1_500_000, 2_000_000)),
            ),
        ),
        tracking = mapOf(
            "mask-5" to TrackingRun(
                "mask-5",
                TrackingRunStatus.COMPLETED,
                coverage = CoverageReport(listOf(CoverageRange(TimeRangeUs(0, 2_000_000), CoverageQuality.TRACKED))),
            ),
        ),
        exportPreset = ExportPreset.P720,
    )

    @Test
    fun roundTripKeepsEveryField() {
        val serialized = ProjectJson.encode(document)
        assertEquals(ProjectJson.SCHEMA_VERSION, serialized.schemaVersion)
        // Progress is runtime state; a completed run is written without it.
        assertEquals(document, ProjectJson.decode(serialized))
    }

    @Test
    fun mismatchFlagIsNotWritten() {
        val flagged = document.copy(sources = document.sources.map { it.copy(mismatch = true) })
        assertFalse(ProjectJson.decode(ProjectJson.encode(flagged)).sources.any { it.mismatch })
    }

    @Test
    fun runningTrackingRestoresCancelled() {
        val running = document.copy(tracking = mapOf("mask-5" to TrackingRun("mask-5", TrackingRunStatus.RUNNING, progress = 0.5f)))
        val restored = ProjectJson.decode(ProjectJson.encode(running)).tracking.getValue("mask-5")
        assertEquals(TrackingRunStatus.CANCELLED, restored.status)
        assertEquals(null, restored.progress)
    }

    @Test
    fun unknownFieldsAreIgnoredAndOptionalFieldsDefault() {
        @Suppress("UNCHECKED_CAST")
        val root = MiniJson.parse(ProjectJson.encode(document).json) as MutableMap<String, Any?>
        root["fromAFutureMinor"] = listOf(1L, 2L)
        root.remove("exportPresetId")
        root.remove("tracking")
        val restored = ProjectJson.decode(SerializedEditProject(1, MiniJson.write(root)))
        assertEquals(document.copy(exportPreset = null, tracking = emptyMap()), restored)
    }

    @Test
    fun unsupportedAndMalformedSnapshotsAreRejected() {
        val json = ProjectJson.encode(document).json
        fun rejection(serialized: SerializedEditProject) = assertFailsWith<VideoKitException> { ProjectJson.decode(serialized) }.error

        val future = rejection(SerializedEditProject(ProjectJson.SCHEMA_VERSION + 1, json))
        assertEquals(ErrorCode.UNSUPPORTED_SNAPSHOT_VERSION, future.code)
        assertEquals("UNSUPPORTED_SCHEMA_VERSION:${ProjectJson.SCHEMA_VERSION + 1}", future.diagnostic)
        // R1: the payload's version wins over the envelope's.
        val futurePayload = json.replace("\"schemaVersion\":1,", "\"schemaVersion\":2,")
        assertEquals("UNSUPPORTED_SCHEMA_VERSION:2", rejection(SerializedEditProject(1, futurePayload)).diagnostic)
        assertEquals(document, ProjectJson.decode(SerializedEditProject(0, json)), "a v1 payload in a v0 envelope reads as v1")
        val malformed = rejection(SerializedEditProject(1, json.dropLast(3)))
        assertEquals(ErrorCode.INVALID_ARGUMENT, malformed.code)
        assertTrue(malformed.diagnostic!!.startsWith("SNAPSHOT_MALFORMED:"))
        // The payload never reaches the diagnostic (it may contain names or tokens).
        assertFalse(malformed.diagnostic!!.contains("media-1"))
        val missingClipField = json.replace("\"inUs\":0,", "")
        assertTrue(rejection(SerializedEditProject(1, missingClipField)).diagnostic!!.startsWith("SNAPSHOT_MALFORMED:"))
        val wrongType = json.replace("\"revision\":12", "\"revision\":\"12\"")
        assertEquals(ErrorCode.INVALID_ARGUMENT, rejection(SerializedEditProject(1, wrongType)).code)
        assertEquals(ErrorCode.INVALID_ARGUMENT, rejection(SerializedEditProject(1, "[1,2]")).code)
    }

    @Test
    fun rangesAreObjectsAndTrackingKeepsNoRuntimeState() {
        val running = document.copy(tracking = mapOf("mask-5" to TrackingRun("mask-5", TrackingRunStatus.RUNNING, progress = 0.5f)))
        val root = MiniJson.parse(ProjectJson.encode(running).json) as Map<*, *>
        assertEquals(ProjectJson.SCHEMA_MINOR.toLong(), root["schemaMinor"])
        val mask = (root["masks"] as List<*>).single() as Map<*, *>
        assertEquals(mapOf("startUs" to 0L, "endUs" to 2_000_000L), mask["rangeUs"])
        assertEquals(listOf(mapOf("startUs" to 1_500_000L, "endUs" to 2_000_000L)), mask["acceptedRanges"])
        val run = (root["tracking"] as List<*>).single() as Map<*, *>
        assertEquals(setOf("maskId", "status", "coverage"), run.keys)
        assertEquals("CANCELLED", run["status"], "W3: a running run is written as cancelled")
    }

    @Test
    fun unknownEnumValuesReadAsTheSchemaDefaults() {
        val json = ProjectJson.encode(document).json
            .replace("\"style\":\"BLUR\"", "\"style\":\"PIXELATE\"")
            .replace("\"state\":\"LOW_CONFIDENCE\"", "\"state\":\"SOMETHING_NEW\"")
            .replace("\"quality\":\"TRACKED\"", "\"quality\":\"SOMETHING_NEW\"")
            .replace("\"status\":\"COMPLETED\"", "\"status\":\"PAUSED\"")
        val restored = ProjectJson.decode(SerializedEditProject(1, json))
        val mask = restored.masks.single()
        assertEquals(MaskStyle.MOSAIC, mask.style)
        assertEquals(CoverageQuality.NOT_ANALYZED, mask.keyframes[1].quality)
        val run = restored.tracking.getValue("mask-5")
        assertEquals(TrackingRunStatus.FAILED, run.status)
        assertEquals(CoverageQuality.NOT_ANALYZED, run.coverage!!.ranges.single().quality)
    }
}
