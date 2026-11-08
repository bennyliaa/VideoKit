package com.videokit.timeline

import com.videokit.api.SerializedEditProject
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class SchemaMigrationTest {
    private class Step(override val fromVersion: Int, private val log: MutableList<Int>) : SchemaMigration {
        override fun migrate(root: Map<String, Any?>): Map<String, Any?> {
            log += fromVersion
            return root + ("v${fromVersion + 1}" to true)
        }
    }

    @Test
    fun defaultChainMigratesFromZero() {
        assertEquals(0, SchemaMigrations.DEFAULT.oldestSupportedVersion)
        assertEquals(ProjectJson.SCHEMA_VERSION, SchemaMigrations.DEFAULT.currentVersion)
        assertTrue(SchemaMigrations.DEFAULT.supports(0))
        assertFalse(SchemaMigrations.DEFAULT.supports(-1))
        assertFalse(SchemaMigrations.DEFAULT.supports(ProjectJson.SCHEMA_VERSION + 1))
    }

    @Test
    fun stepsRunInOrderFromTheSnapshotVersion() {
        val log = mutableListOf<Int>()
        val chain = SchemaMigrations(listOf(Step(2, log), Step(0, log), Step(1, log)), currentVersion = 3)
        val migrated = chain.migrate(1, mapOf("projectId" to "p"))
        assertEquals(listOf(1, 2), log)
        assertEquals(mapOf("projectId" to "p", "v2" to true, "v3" to true), migrated)
        assertEquals(mapOf("x" to 1L), chain.migrate(3, mapOf("x" to 1L)), "current version is not migrated")
    }

    @Test
    fun chainsMustBeContiguousAndEndAtTheCurrentVersion() {
        assertFailsWith<IllegalArgumentException> { SchemaMigrations(listOf(Step(0, mutableListOf()), Step(2, mutableListOf())), 3) }
        assertFailsWith<IllegalArgumentException> { SchemaMigrations(listOf(Step(0, mutableListOf())), 3) }
        assertFailsWith<IllegalArgumentException> { SchemaMigrations(listOf(Step(0, mutableListOf()), Step(0, mutableListOf())), 1) }
        assertEquals(3, SchemaMigrations(emptyList(), 3).oldestSupportedVersion)
    }

    @Test
    fun v0BecomesSchemaOne() {
        val v0 = mapOf(
            "projectId" to "p",
            "revision" to 4L,
            "sources" to listOf(mapOf("sourceId" to "src-1", "mediaToken" to "m")),
            "timeline" to mapOf("clips" to listOf(mapOf("clipId" to "clip-2", "sourceId" to "src-1", "inUs" to 0L, "outUs" to 5L))),
            "masks" to listOf(
                mapOf("maskId" to "mask-3", "type" to "FACE", "rangeUs" to listOf(0L, 5L), "acceptedRanges" to listOf(listOf(0L, 1L))),
            ),
            "tracking" to listOf(
                mapOf(
                    "maskId" to "mask-3",
                    "status" to "COMPLETED",
                    "requestId" to "r-1",
                    "coverage" to listOf(
                        mapOf("startUs" to 0L, "endUs" to 2L, "state" to "TRACKED"),
                        mapOf("startUs" to 2L, "endUs" to 5L, "state" to "LOST", "accepted" to true),
                    ),
                ),
            ),
        )
        val v1 = V0ToV1.migrate(v0)
        assertEquals(1L, v1["schemaVersion"])
        assertEquals(0L, v1["schemaMinor"])
        assertEquals(0L, v1["createdAt"])
        assertEquals(v0["timeline"], v1["timeline"], "other properties are kept")
        val mask = (v1["masks"] as List<*>).single() as Map<*, *>
        assertEquals(mapOf("startUs" to 0L, "endUs" to 5L), mask["rangeUs"])
        assertEquals(listOf(mapOf("startUs" to 0L, "endUs" to 1L), mapOf("startUs" to 2L, "endUs" to 5L)), mask["acceptedRanges"])
        val run = (v1["tracking"] as List<*>).single() as Map<*, *>
        assertEquals(setOf("maskId", "status", "coverage"), run.keys)
        assertEquals(
            listOf(
                mapOf("startUs" to 0L, "endUs" to 2L, "quality" to "TRACKED"),
                mapOf("startUs" to 2L, "endUs" to 5L, "quality" to "LOST"),
            ),
            run["coverage"],
        )
        // The v0 input is not modified.
        assertEquals(listOf(0L, 5L), ((v0["masks"] as List<*>).single() as Map<*, *>)["rangeUs"])
    }

    @Test
    fun restoredV0IsWrittenAsTheCurrentSchema() {
        val restored = ProjectJson.decode(SerializedEditProject(0, """{"projectId":"p","revision":2}"""))
        assertEquals(2L, restored.revision)
        assertEquals(ProjectJson.SCHEMA_VERSION, ProjectJson.encode(restored).schemaVersion)
    }
}
