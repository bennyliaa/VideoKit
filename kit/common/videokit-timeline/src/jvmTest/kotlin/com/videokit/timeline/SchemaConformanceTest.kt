package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.CoverageQuality
import com.videokit.api.CoverageRange
import com.videokit.api.CoverageReport
import com.videokit.api.EditSource
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
import com.videokit.timeline.internal.MiniJson
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * [ProjectJson] against the single source `spec/schema/edit-project.v1.json` (04A E2): what the Kotlin writer emits
 * conforms (rule W1: every defined property, nothing else), and the schema's enums and defaults are the Kotlin ones.
 * A small validator for the keywords the schema uses (type, const, enum, required, properties, items, \$ref, oneOf,
 * minimum, maximum); no JSON Schema dependency.
 */
class SchemaConformanceTest {
    private val schema = TimelineVectors.read("schema/edit-project.v1.json")
    private val defs = schema["\$defs"] as Map<*, *>

    private val document = ProjectDocument(
        projectId = "p-1",
        revision = 3,
        createdAtMs = 10,
        updatedAtMs = 20,
        sources = listOf(
            EditSource("src-1", "m-1", "a.mp4", SourceProbe(5_000_000, 1920, 1080, 90, 30f, "video/avc", "audio/mp4a-latm", true)),
            EditSource("src-2", "m-2", null, SourceProbe(5_000_000, 640, 360)),
            EditSource("src-3", "m-3", null, null),
        ),
        clips = listOf(Clip("clip-4", "src-1", 0, 1_000_000)),
        masks = listOf(
            MaskTrack(
                maskId = "mask-5",
                type = MaskType.OBJECT,
                style = MaskStyle.BLUR,
                strength = 0.7f,
                rangeUs = TimeRangeUs(0, 1_000_000),
                keyframes = listOf(
                    MaskKeyframe(0, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f)),
                    MaskKeyframe(500_000, MaskRegion(0.2f, 0.1f, 0.2f, 0.2f, 5f), KeyframeSource.TRACKER, CoverageQuality.AMBIGUOUS),
                ),
                acceptedRangesUs = listOf(TimeRangeUs(500_000, 1_000_000)),
            ),
        ),
        tracking = mapOf(
            "mask-5" to TrackingRun(
                "mask-5",
                TrackingRunStatus.RUNNING,
                progress = 0.4f,
                coverage = CoverageReport(listOf(CoverageRange(TimeRangeUs(0, 500_000), CoverageQuality.NOT_ANALYZED))),
            ),
        ),
        exportPreset = ExportPreset.P1080,
    )

    @Test
    fun writerOutputConformsAndWritesEveryProperty() {
        val tree = MiniJson.parse(ProjectJson.encode(document).json)
        val problems = ArrayList<String>()
        validate(tree, schema, "$", problems)
        assertEquals(emptyList<String>(), problems)
    }

    @Test
    fun emptyDocumentConformsToo() {
        val problems = ArrayList<String>()
        validate(MiniJson.parse(ProjectJson.encode(ProjectDocument("p")).json), schema, "$", problems)
        assertEquals(emptyList<String>(), problems)
    }

    @Test
    fun enumsAreTheKotlinEnums() {
        fun enumOf(vararg path: String): List<*> {
            var node: Any? = defs
            path.forEach { node = (node as Map<*, *>)[it] }
            return (node as Map<*, *>)["enum"] as List<*>
        }
        assertEquals(CoverageQuality.entries.map { it.name }, defs.def("trackingQuality")["enum"])
        assertEquals(MaskType.entries.map { it.name }, enumOf("mask", "properties", "type"))
        assertEquals(MaskStyle.entries.map { it.name }, enumOf("mask", "properties", "style"))
        assertEquals(KeyframeSource.entries.map { it.name }, enumOf("keyframe", "properties", "source"))
        // RUNNING is never written (W3).
        assertEquals(TrackingRunStatus.entries.map { it.name } - "RUNNING", enumOf("trackingRun", "properties", "status"))
        assertEquals(listOf(ProjectJson.SCHEMA_VERSION.toLong(), ProjectJson.SCHEMA_MINOR.toLong()), versionOf(schema))
    }

    @Test
    fun defaultsAreWhatTheReaderFillsIn() {
        val minimal = """{"schemaVersion":1,"projectId":"p","sources":[{"sourceId":"s","mediaToken":"m","probe":{}}],""" +
            """"masks":[{"maskId":"k","type":"MANUAL","rangeUs":{"startUs":0,"endUs":1},""" +
            """"keyframes":[{"atUs":0,"region":{"x":0,"y":0,"width":0.5,"height":0.5}}]}]}"""
        val restored = ProjectJson.decode(SerializedEditProject(1, minimal))
        val root = schema["properties"] as Map<*, *>
        assertEquals(root.default("revision"), restored.revision)
        assertEquals(root.default("createdAt"), restored.createdAtMs)
        assertEquals(root.default("updatedAt"), restored.updatedAtMs)
        assertEquals(root.default("exportPresetId"), restored.exportPreset)
        val probe = defs.def("probe")["properties"] as Map<*, *>
        val readProbe = restored.sources.single().probe!!
        assertEquals(probe.default("rotation"), readProbe.rotationDeg.toLong())
        assertEquals(probe.default("hasAudio"), readProbe.hasAudio)
        assertEquals(probe.default("fps"), readProbe.frameRate)
        val mask = defs.def("mask")["properties"] as Map<*, *>
        val readMask = restored.masks.single()
        assertEquals(mask.default("style"), readMask.style.name)
        assertEquals((mask.default("strength") as Number).toFloat(), readMask.strength)
        assertEquals(mask.default("enabled"), readMask.enabled)
        val keyframe = defs.def("keyframe")["properties"] as Map<*, *>
        assertEquals(keyframe.default("source"), readMask.keyframes.single().source.name)
        assertEquals(keyframe.default("state"), readMask.keyframes.single().quality)
        val region = defs.def("region")["properties"] as Map<*, *>
        assertEquals((region.default("rotation") as Number).toFloat(), readMask.keyframes.single().region.rotationDeg)
    }

    // ------------------------------------------------------------------ validator

    private fun validate(value: Any?, rule: Map<*, *>, at: String, problems: MutableList<String>) {
        (rule["\$ref"] as? String)?.let { ref ->
            validate(value, defs.def(ref.removePrefix("#/\$defs/")), at, problems)
            return
        }
        (rule["oneOf"] as? List<*>)?.let { options ->
            val matching = options.count { option -> ArrayList<String>().also { validate(value, option as Map<*, *>, at, it) }.isEmpty() }
            if (matching != 1) problems += "$at: matches $matching of oneOf"
            return
        }
        rule["type"]?.let { type ->
            val types = (type as? List<*>) ?: listOf(type)
            if (types.none { matchesType(value, it as String) }) {
                problems += "$at: type $types, was ${value?.let { it::class.simpleName }}"
            }
        }
        if (rule.containsKey("const") && rule["const"] != value) problems += "$at: const ${rule["const"]}, was $value"
        (rule["enum"] as? List<*>)?.let { if (value !in it) problems += "$at: $value not in $it" }
        (rule["minimum"] as? Number)?.let { if (value is Number && value.toDouble() < it.toDouble()) problems += "$at: below $it" }
        (rule["maximum"] as? Number)?.let { if (value is Number && value.toDouble() > it.toDouble()) problems += "$at: above $it" }
        if (value is Map<*, *>) {
            val properties = rule["properties"] as? Map<*, *> ?: emptyMap<Any?, Any?>()
            (rule["required"] as? List<*>).orEmpty().forEach { if (!value.containsKey(it)) problems += "$at: missing required $it" }
            // W1: writers write every defined property and nothing else.
            properties.keys.forEach { if (!value.containsKey(it)) problems += "$at: not written: $it" }
            value.keys.forEach { if (it !in properties.keys) problems += "$at: not in the schema: $it" }
            properties.forEach { (key, child) ->
                if (value.containsKey(key)) validate(value[key], child as Map<*, *>, "$at.$key", problems)
            }
        }
        if (value is List<*>) {
            val items = rule["items"] as? Map<*, *> ?: return
            value.forEachIndexed { index, item -> validate(item, items, "$at[$index]", problems) }
        }
    }

    private fun matchesType(value: Any?, type: String): Boolean = when (type) {
        "object" -> value is Map<*, *>
        "array" -> value is List<*>
        "string" -> value is String
        "integer" -> value is Long
        "number" -> value is Number
        "boolean" -> value is Boolean
        "null" -> value == null
        else -> error("unknown type $type")
    }

    private fun Map<*, *>.def(name: String): Map<*, *> = this[name] as? Map<*, *> ?: error("no \$defs/$name")

    private fun Map<*, *>.default(property: String): Any? {
        val rule = this[property] as Map<*, *>
        assertTrue(rule.containsKey("default"), "$property has no default")
        return rule["default"]
    }

    private fun versionOf(schema: Map<*, *>): List<Any?> = (schema["x-version"] as Map<*, *>).let { listOf(it["major"], it["minor"]) }
}
