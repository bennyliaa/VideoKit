package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ExportPreset
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskType
import com.videokit.api.SerializedEditProject
import com.videokit.api.SourceProbe
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingKind
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitException
import com.videokit.timeline.internal.MiniJson
import java.io.File
import kotlin.math.abs
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.fail

/** Loading and running of `spec/vectors/timeline` and the edit model part of `state-machine/edit-project.json`. */
internal object TimelineVectors {
    fun read(relative: String): Map<*, *> {
        val dir = System.getProperty("videokit.specDir") ?: error("system property videokit.specDir is not set")
        return MiniJson.parse(File(dir, relative).readText()) as Map<*, *>
    }

    fun cases(relative: String, kind: String): List<Map<*, *>> {
        val root = read(relative)
        assertEquals(kind, root["kind"], "$relative kind")
        return (root["cases"] as List<*>).map { it as Map<*, *> }
    }

    // ------------------------------------------------------------------ schema migration

    fun runMigration(case: Map<*, *>) {
        val id = case["id"]
        val version = (case["envelopeVersion"] as Number).toInt()
        val json = case["json"] as? String ?: MiniJson.write(case["payload"])
        val expect = case["expect"] as Map<*, *>
        val outcome = runCatching { ProjectJson.decode(SerializedEditProject(version, json)) }
        when (expect["result"]) {
            "REJECTED" -> {
                val error = (outcome.exceptionOrNull() as? VideoKitException)?.error ?: fail("$id: expected a rejection, got $outcome")
                assertEquals(expect["code"], error.code.name, "$id code")
                (expect["diagnostic"] as? String)?.let { prefix ->
                    assertTrue(error.diagnostic.orEmpty().startsWith(prefix), "$id diagnostic ${error.diagnostic}")
                }
            }

            "RESTORED" -> {
                val document = outcome.getOrElse { fail("$id: restore failed: $it") }
                checkDocument("$id", document, expect)
                // A restored document written again reads back identically (schema 1 round trip).
                assertEquals(document, ProjectJson.decode(ProjectJson.encode(document)), "$id round trip")
            }

            else -> fail("$id: unknown result ${expect["result"]}")
        }
    }

    private fun checkDocument(id: String, document: ProjectDocument, expect: Map<*, *>) {
        expect["projectId"]?.let { assertEquals(it, document.projectId, "$id projectId") }
        expect.long("revision")?.let { assertEquals(it, document.revision, "$id revision") }
        expect.long("createdAt")?.let { assertEquals(it, document.createdAtMs, "$id createdAt") }
        expect.long("updatedAt")?.let { assertEquals(it, document.updatedAtMs, "$id updatedAt") }
        if (expect.containsKey("exportPresetId")) assertEquals(expect["exportPresetId"], document.exportPreset?.name, "$id exportPresetId")
        (expect["sources"] as? List<*>)?.let { sources ->
            assertEquals(sources.size, document.sources.size, "$id sources")
            sources.zip(document.sources).forEach { (want, source) ->
                want as Map<*, *>
                assertEquals(want["sourceId"], source.sourceId, "$id sourceId")
                assertEquals(want["mediaToken"], source.mediaToken, "$id mediaToken")
                want.long("rotation")?.let { assertEquals(it.toInt(), source.probe?.rotationDeg, "$id rotation") }
                if (want.containsKey("fps")) {
                    val fps = want["fps"] as? Number
                    val actual = source.probe?.frameRate?.toDouble()
                    if (fps == null) assertEquals(null, actual, "$id fps") else assertClose(fps.toDouble(), actual, "$id fps")
                }
                if (want.containsKey("videoCodec")) assertEquals(want["videoCodec"], source.probe?.videoCodec, "$id videoCodec")
            }
        }
        (expect["clips"] as? List<*>)?.let { clips ->
            assertEquals(
                clips.map { (it as Map<*, *>).let { c -> Triple(c["clipId"], c.long("inUs"), c.long("outUs")) } },
                document.clips.map { Triple(it.clipId, it.inUs, it.outUs) },
                "$id clips",
            )
        }
        (expect["masks"] as? List<*>)?.let { masks ->
            assertEquals(masks.size, document.masks.size, "$id masks")
            masks.zip(document.masks).forEach { (want, mask) ->
                want as Map<*, *>
                assertEquals(want["maskId"], mask.maskId, "$id maskId")
                want["style"]?.let { assertEquals(it, mask.style.name, "$id style") }
                (want["strength"] as? Number)?.let { assertClose(it.toDouble(), mask.strength.toDouble(), "$id strength") }
                (want["enabled"] as? Boolean)?.let { assertEquals(it, mask.enabled, "$id enabled") }
                (want["rangeUs"] as? Map<*, *>)?.let {
                    assertEquals(range(it), listOf(mask.rangeUs.startUs, mask.rangeUs.endUs), "$id rangeUs")
                }
                (want["keyframes"] as? List<*>)?.let { assertEquals(it.longs(), mask.keyframes.map { k -> k.atUs }, "$id keyframes") }
                (want["keyframeStates"] as? List<*>)?.let {
                    assertEquals(it, mask.keyframes.map { k -> k.quality?.name }, "$id keyframe states")
                }
                (want["acceptedRanges"] as? List<*>)?.let { ranges ->
                    val actual = mask.acceptedRangesUs.map { listOf(it.startUs, it.endUs) }
                    assertEquals(ranges.map { range(it as Map<*, *>) }, actual, "$id accepted")
                }
            }
        }
        (expect["tracking"] as? List<*>)?.let { runs ->
            val actual = document.tracking.values.map { it.maskId to it.status.name }
            assertEquals(runs.map { (it as Map<*, *>)["maskId"] to it["status"] }, actual, "$id tracking")
            runs.zip(document.tracking.values.toList()).forEach { (want, run) ->
                ((want as Map<*, *>)["qualities"] as? List<*>)?.let {
                    assertEquals(it, run.coverage?.ranges.orEmpty().map { r -> r.quality.name }, "$id qualities")
                }
            }
        }
    }

    private fun range(json: Map<*, *>): List<Long> = listOf((json["startUs"] as Number).toLong(), (json["endUs"] as Number).toLong())

    // ------------------------------------------------------------------ concat path

    fun runConcat(probes: Map<*, *>, case: Map<*, *>) {
        val id = case["id"]
        val sources = probes.map { (name, probe) -> EditSource(name as String, "media-$name", probe = probe(probe as Map<*, *>)) }
        val clips = (case["clips"] as List<*>).mapIndexed { index, item ->
            val clip = item as List<*>
            Clip("clip-$index", clip[0] as String, (clip[1] as Number).toLong(), (clip[2] as Number).toLong())
        }
        val keyframes = (case["keyframesUs"] as? Map<*, *>).orEmpty()
            .map { (source, times) -> source as String to (times as List<*>).longs() }
            .toMap()
        val decision = ConcatRules.decide(
            ConcatRequest(
                clips = clips,
                sources = sources,
                keyframesUs = keyframes,
                preset = (case["preset"] as? String)?.let { ExportPreset.valueOf(it) } ?: ExportPreset.ORIGINAL,
                masksEnabled = case["masksEnabled"] as? Boolean ?: false,
                preciseCuts = case["preciseCuts"] as? Boolean ?: false,
            ),
        )
        val expect = case["expect"] as Map<*, *>
        assertEquals(expect["path"], decision.path.name, "$id path (${decision.reasons})")
        assertEquals(expect["reasons"], decision.reasons.map { it.name }, "$id reasons")
        (expect["effectiveInUs"] as? List<*>)?.let {
            assertEquals(it.longs(), decision.effectiveClips.map { c -> c.inUs }, "$id effective")
        }
        assertEquals((expect["warnings"] as? List<*>).orEmpty(), decision.warnings, "$id warnings")
    }

    private fun probe(json: Map<*, *>): SourceProbe = SourceProbe(
        durationUs = json.long("durationUs") ?: 0L,
        width = json.long("width")?.toInt() ?: 0,
        height = json.long("height")?.toInt() ?: 0,
        rotationDeg = json.long("rotation")?.toInt() ?: 0,
        frameRate = (json["fps"] as? Number)?.toFloat(),
        videoCodec = json["videoCodec"] as? String,
        audioCodec = json["audioCodec"] as? String,
        hasAudio = json["hasAudio"] as? Boolean ?: false,
    )

    // ------------------------------------------------------------------ edit model (timeline/edit-model.json)

    private const val SOURCE_US = 10_000_000L

    private fun start(from: String): TimelineEditor {
        val source = EditSource("src", "media-src", probe = SourceProbe(SOURCE_US, 1920, 1080, frameRate = 30f, videoCodec = "video/avc"))
        val clips = when (from) {
            "EMPTY", "SOURCE" -> emptyList()
            "CLIP" -> listOf(Clip("clip-1", "src", 0L, 3_000_000L))
            "TWO_CLIPS" -> listOf(Clip("clip-1", "src", 0L, 3_000_000L), Clip("clip-2", "src", 5_000_000L, 6_000_000L))
            else -> error("unknown start state $from")
        }
        val sources = if (from == "EMPTY") emptyList() else listOf(source)
        return TimelineEditor(ProjectDocument("vector", sources = sources, clips = clips))
    }

    fun runEditModel(case: Map<*, *>) {
        val id = case["id"]
        val editor = start(case["from"] as String)
        val baseRevision = editor.document.revision
        (case["steps"] as List<*>).forEachIndexed { index, item ->
            val step = item as Map<*, *>
            val where = "$id step ${index + 1} ${step["command"]}"
            val outcome = modelStep(editor, step)
            val expect = step["expect"] as Map<*, *>
            when (expect["result"]) {
                "APPLIED" -> assertTrue(outcome is EditOutcome.Applied, "$where: $outcome")

                "NOT_AN_EDIT" -> assertEquals(EditOutcome.NotAnEdit, outcome, where)

                "REJECTED" -> {
                    val rejected = outcome as? EditOutcome.Rejected ?: fail("$where: expected rejection, got $outcome")
                    expect["diagnostic"]?.let { assertEquals<Any?>(it, rejected.error.diagnostic, where) }
                }

                else -> fail("$where: unknown result ${expect["result"]}")
            }
            checkModel(where, editor, baseRevision, expect)
        }
    }

    private fun checkModel(where: String, editor: TimelineEditor, baseRevision: Long, expect: Map<*, *>) {
        val document = editor.document
        (expect["clips"] as? List<*>)?.let { clips ->
            assertEquals(clips.map { (it as List<*>).longs() }, document.clips.map { listOf(it.inUs, it.outUs) }, "$where clips")
        }
        expect.long("durationUs")?.let { assertEquals(it, document.durationUs, "$where durationUs") }
        expect.long("revision")?.let { assertEquals(it, document.revision - baseRevision, "$where revision") }
        expect.long("masks")?.let { assertEquals(it.toInt(), document.masks.size, "$where masks") }
        (expect["canUndo"] as? Boolean)?.let { assertEquals(it, editor.canUndo, "$where canUndo") }
        (expect["canRedo"] as? Boolean)?.let { assertEquals(it, editor.canRedo, "$where canRedo") }
        val mask = document.masks.firstOrNull()
        (expect["keyframes"] as? List<*>)?.let { assertEquals(it.longs(), mask?.keyframes?.map { k -> k.atUs }, "$where keyframes") }
        expect["style"]?.let { assertEquals<Any?>(it, mask?.style?.name, "$where style") }
        (expect["strength"] as? Number)?.let { assertClose(it.toDouble(), mask?.strength?.toDouble(), "$where strength") }
        (expect["enabled"] as? Boolean)?.let { assertEquals(it, mask?.enabled, "$where enabled") }
    }

    private fun modelStep(editor: TimelineEditor, step: Map<*, *>): EditOutcome {
        val document = editor.document
        fun clip(): String = document.clips[step.int("clip")].clipId
        fun mask(): String = document.masks[step.int("mask")].maskId
        fun region() = MaskRegion(step.float("x"), step.float("y"), step.float("width"), step.float("height"))
        val command: VideoKitEditCommand = when (val name = step["command"] as String) {
            "UNDO" -> return editor.undo()

            "REDO" -> return editor.redo()

            "ADD_CLIP" -> VideoKitEditCommand.AddClip(
                step["source"] as? String ?: "src",
                step.long("inUs")!!,
                step.long("outUs")!!,
                step.long("index")?.toInt(),
            )

            "SPLIT" -> VideoKitEditCommand.SplitAt(clip(), step.long("atUs")!!)

            "TRIM" -> VideoKitEditCommand.TrimClip(clip(), step.long("inUs")!!, step.long("outUs")!!)

            "MOVE" -> VideoKitEditCommand.MoveClip(clip(), step.int("toIndex"))

            "REMOVE" -> VideoKitEditCommand.RemoveClip(clip())

            "ADD_MASK" -> VideoKitEditCommand.AddMask(
                type = MaskType.valueOf(step["type"] as String),
                region = region(),
                rangeUs = TimeRangeUs(step.long("startUs")!!, step.long("endUs")!!),
                style = (step["style"] as? String)?.let { MaskStyle.valueOf(it) } ?: MaskStyle.MOSAIC,
                strength = (step["strength"] as? Number)?.toFloat() ?: 0.5f,
            )

            "UPDATE_KEYFRAME" -> VideoKitEditCommand.UpdateMaskKeyframe(mask(), step.long("atUs")!!, region())

            "REMOVE_KEYFRAME" -> VideoKitEditCommand.RemoveMaskKeyframe(mask(), step.long("atUs")!!)

            "SET_STYLE" -> VideoKitEditCommand.SetMaskStyle(mask(), MaskStyle.valueOf(step["style"] as String), step.float("strength"))

            "SET_ENABLED" -> VideoKitEditCommand.SetMaskEnabled(mask(), step["enabled"] as Boolean)

            "REMOVE_MASK" -> VideoKitEditCommand.RemoveMask(mask())

            "CORRECT_TRACKING" -> VideoKitEditCommand.CorrectTracking(mask(), step.long("atUs")!!, region())

            "ACCEPT_RANGE" -> VideoKitEditCommand.AcceptTrackingRange(mask(), TimeRangeUs(step.long("startUs")!!, step.long("endUs")!!))

            "START_TRACKING" -> VideoKitEditCommand.StartTracking(mask(), TrackingKind.FACE)

            else -> error("unknown edit model command $name")
        }
        return editor.apply(command)
    }

    // ------------------------------------------------------------------ state-machine/edit-project.json (model subset)

    /** Commands of edit-project.json that are pure edit model operations; cases with any other command are skipped. */
    private val MODEL_COMMANDS = setOf(
        "ADD_CLIP", "SPLIT_FIRST", "TRIM_FIRST", "REMOVE_FIRST", "MOVE_FIRST", "ADD_MASK",
        "UNDO", "REDO", "ACCEPT_TRACKING_RANGE_FIRST_MASK",
    )

    /** Fake source duration of the state machine vectors (the Kotlin and Dart Fakes probe 120 s). */
    private const val FAKE_SOURCE_US = 120_000_000L

    /** Whether the edit model can run [case] (only model commands, from a start state without phase). */
    fun isModelCase(case: Map<*, *>): Boolean = case["from"] in setOf("EMPTY", "READY_WITH_SOURCE", "READY_WITH_CLIP") &&
        (case["steps"] as List<*>).all { (it as Map<*, *>)["command"] in MODEL_COMMANDS }

    fun runEditProjectCase(case: Map<*, *>) {
        val id = case["id"]
        val editor = TimelineEditor(ProjectDocument("vector"))
        val from = case["from"] as String
        if (from != "EMPTY") {
            editor.putSource(EditSource(editor.newSourceId(), "vector-edit", probe = SourceProbe(FAKE_SOURCE_US, 1280, 720)))
        }
        if (from == "READY_WITH_CLIP") {
            // Same setup as the runner of the Fakes: the clip is added by a command, so it is on the undo stack.
            val added = editor.apply(VideoKitEditCommand.AddClip(editor.document.sources.single().sourceId, 0L, 3_000_000L))
            assertTrue(added is EditOutcome.Applied, "$id setup: $added")
        }
        (case["steps"] as List<*>).forEachIndexed { index, item ->
            val step = item as Map<*, *>
            val where = "$id step ${index + 1} ${step["command"]}"
            val document = editor.document
            val firstClip = document.clips.firstOrNull()?.clipId ?: "no-clip"
            val firstMask = document.masks.firstOrNull()?.maskId ?: "no-mask"
            val outcome = when (step["command"]) {
                "UNDO" -> editor.undo()

                "REDO" -> editor.redo()

                "ADD_CLIP" -> editor.apply(
                    VideoKitEditCommand.AddClip(
                        if (step["source"] == "first") document.sources.firstOrNull()?.sourceId ?: "no-source" else "unknown-source",
                        step.long("inUs")!!,
                        step.long("outUs")!!,
                        step.long("index")?.toInt(),
                    ),
                )

                "SPLIT_FIRST" -> editor.apply(VideoKitEditCommand.SplitAt(firstClip, step.long("atUs")!!))

                "TRIM_FIRST" -> editor.apply(VideoKitEditCommand.TrimClip(firstClip, step.long("inUs")!!, step.long("outUs")!!))

                "REMOVE_FIRST" -> editor.apply(VideoKitEditCommand.RemoveClip(firstClip))

                "MOVE_FIRST" -> editor.apply(VideoKitEditCommand.MoveClip(firstClip, step.int("toIndex")))

                "ADD_MASK" -> editor.apply(
                    VideoKitEditCommand.AddMask(
                        MaskType.valueOf(step["type"] as String),
                        MaskRegion(step.float("x"), step.float("y"), step.float("width"), step.float("height")),
                        TimeRangeUs(step.long("startUs")!!, step.long("endUs")!!),
                    ),
                )

                "ACCEPT_TRACKING_RANGE_FIRST_MASK" ->
                    editor.apply(
                        VideoKitEditCommand.AcceptTrackingRange(firstMask, TimeRangeUs(step.long("startUs")!!, step.long("endUs")!!)),
                    )

                else -> error("$where: not a model command")
            }
            val expect = step["expect"] as Map<*, *>
            val (result, code) = when (outcome) {
                is EditOutcome.Applied -> "APPLIED" to null
                is EditOutcome.Rejected -> "REJECTED" to outcome.error.code.name
                EditOutcome.NotAnEdit -> "NOT_AN_EDIT" to null
            }
            assertEquals(expect["result"], result, "$where result ($outcome)")
            expect["code"]?.let { assertEquals<Any?>(it, code, "$where code") }
            // The model has no phase; CREATED and READY follow from the sources.
            when (expect["phase"]) {
                "CREATED" -> assertTrue(editor.document.sources.isEmpty(), "$where phase CREATED")
                "READY" -> assertTrue(editor.document.sources.isNotEmpty(), "$where phase READY")
            }
        }
    }

    // ------------------------------------------------------------------ helpers

    private fun Map<*, *>.long(key: String): Long? = (this[key] as? Number)?.toLong()

    private fun Map<*, *>.int(key: String): Int = (this[key] as Number).toInt()

    private fun Map<*, *>.float(key: String): Float = (this[key] as Number).toFloat()

    private fun List<*>.longs(): List<Long> = map { (it as Number).toLong() }

    private fun assertClose(expected: Double, actual: Double?, what: String) {
        assertTrue(actual != null && abs(expected - actual) < 1e-4, "$what: expected $expected, was $actual")
    }
}
