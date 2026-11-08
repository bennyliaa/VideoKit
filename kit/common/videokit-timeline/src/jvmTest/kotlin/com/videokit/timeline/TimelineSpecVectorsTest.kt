package com.videokit.timeline

import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import kotlin.test.assertTrue

/** Runs `spec/vectors/timeline/schema-migration.json` against [ProjectJson] (M4-B1). */
@RunWith(Parameterized::class)
class SchemaMigrationVectorsTest(private val id: String, private val case: Map<*, *>) {
    @Test
    fun vector() = TimelineVectors.runMigration(case)

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = TimelineVectors.cases("vectors/timeline/schema-migration.json", "timeline-schema-migration")
            .map { arrayOf(it["id"] as Any, it) }
    }
}

/** Runs `spec/vectors/timeline/concat-path.json` against [ConcatRules] (M4-B1). */
@RunWith(Parameterized::class)
class ConcatPathVectorsTest(private val id: String, private val case: Map<*, *>) {
    @Test
    fun vector() = TimelineVectors.runConcat(probes, case)

    companion object {
        private const val FILE = "vectors/timeline/concat-path.json"
        private val probes: Map<*, *> by lazy { TimelineVectors.read(FILE)["probes"] as Map<*, *> }

        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = TimelineVectors.cases(FILE, "timeline-concat-path").map { arrayOf(it["id"] as Any, it) }
    }
}

/** Runs `spec/vectors/timeline/edit-model.json` against [TimelineEditor] (M4-B1). */
@RunWith(Parameterized::class)
class EditModelVectorsTest(private val id: String, private val case: Map<*, *>) {
    @Test
    fun vector() = TimelineVectors.runEditModel(case)

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> =
            TimelineVectors.cases("vectors/timeline/edit-model.json", "timeline-edit-model").map { arrayOf(it["id"] as Any, it) }
    }
}

/**
 * Runs the edit model part of `spec/vectors/state-machine/edit-project.json` against [TimelineEditor]: the cases
 * that only use edit commands, undo and redo (phases, tracking runs, export and release are the project's, not the
 * model's). The same cases run against the Kotlin and Dart Fakes, so the editor and the Fakes agree.
 */
@RunWith(Parameterized::class)
class EditProjectModelVectorsTest(private val id: String, private val case: Map<*, *>) {
    @Test
    fun vector() = TimelineVectors.runEditProjectCase(case)

    companion object {
        private const val FILE = "vectors/state-machine/edit-project.json"

        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = TimelineVectors.cases(FILE, "edit-state-machine")
            .filter(TimelineVectors::isModelCase)
            .map { arrayOf(it["id"] as Any, it) }
    }
}

/** Guards against the model filter of [EditProjectModelVectorsTest] silently selecting nothing (25 cases at M4-B1). */
class EditProjectModelCoverageTest {
    @Test
    fun selectsModelCases() {
        val selected = EditProjectModelVectorsTest.cases().size
        assertTrue(selected >= MIN_MODEL_CASES, "only $selected model cases selected")
    }

    private companion object {
        const val MIN_MODEL_CASES = 20
    }
}
