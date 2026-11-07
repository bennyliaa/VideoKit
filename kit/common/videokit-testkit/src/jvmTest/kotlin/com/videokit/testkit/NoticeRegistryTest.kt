package com.videokit.testkit

import com.videokit.api.ExportWarnings
import com.videokit.api.NoticeCodes
import com.videokit.testkit.internal.MiniJson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/** Verifies Kotlin [NoticeCodes] and the codes the Kit emits against `spec/notices.json` (04A K1). */
class NoticeRegistryTest {
    private val registry = MiniJson.parse(SpecFiles.read("notices.json")) as Map<*, *>
    private val notices = (registry["notices"] as List<*>).map { it as Map<*, *> }

    @Test
    fun codesMatchRegistryInOrder() {
        assertEquals(1L, registry["schemaVersion"])
        assertEquals(notices.map { it["code"] }, NoticeCodes.ALL)
    }

    @Test
    fun codesAreUpperSnakeCaseAndUnique() {
        val pattern = Regex(registry["codePattern"] as String)
        NoticeCodes.ALL.forEach { assertTrue("code $it", pattern.matches(it)) }
        assertEquals(NoticeCodes.ALL.size, NoticeCodes.ALL.toSet().size)
        notices.forEach { assertTrue("emittedBy of ${it["code"]}", it["emittedBy"] in setOf("KIT", "DART", "BOTH")) }
    }

    /** 04A K3: export warning codes, upper snake case, with an optional argument. */
    @Test
    fun exportWarningsMatchRegistryInOrder() {
        val warnings = (registry["exportWarnings"] as List<*>).map { it as Map<*, *> }
        assertEquals(warnings.map { it["code"] }, ExportWarnings.ALL)
        val pattern = Regex(registry["codePattern"] as String)
        ExportWarnings.ALL.forEach { assertTrue("code $it", pattern.matches(it)) }
        warnings.forEach { entry ->
            assertTrue("emittedBy of ${entry["code"]}", entry["emittedBy"] in setOf("KIT", "DART", "BOTH"))
            assertTrue("argument of ${entry["code"]}", entry["argument"] == null || entry["argument"] is String)
        }
        // Codes and their arguments travel as CODE:argument.
        val wire = ExportWarnings.withArgument(ExportWarnings.TRACKING_LOST_RANGES, "mask-1")
        assertEquals("TRACKING_LOST_RANGES:mask-1", wire)
        assertEquals(ExportWarnings.TRACKING_LOST_RANGES, ExportWarnings.codeOf(wire))
        assertEquals(ExportWarnings.FAST_CONCAT_REJECTED, ExportWarnings.codeOf(ExportWarnings.FAST_CONCAT_REJECTED))
    }

    /** Kit sources add export warnings only through registered constants (no literal warning codes). */
    @Test
    fun kitSourcesUseRegisteredWarnings() {
        val kitDir = SpecFiles.dir.resolve("../kit").canonicalFile
        val literal = Regex("""warnings\s*\+?=\s*(?:listOf\()?"([A-Za-z_]+)""")
        val found = kitDir.walkTopDown()
            .filter { it.isFile && it.extension == "kt" && "${File.separator}build${File.separator}" !in it.path && "Test" !in it.name }
            .flatMap { file -> literal.findAll(file.readText()).map { it.groupValues[1] } }
            .toSet()
        val unregistered = found - ExportWarnings.ALL.toSet()
        assertTrue("unregistered export warning literals in Kit sources: $unregistered", unregistered.isEmpty())
    }

    /** Every string literal the Kit sources pass to TransientNotice is a registered code (no unregistered notices). */
    @Test
    fun kitSourcesEmitOnlyRegisteredCodes() {
        val kitDir = SpecFiles.dir.resolve("../kit").canonicalFile
        val literal = Regex("""TransientNotice\(\s*"([^"]+)"""")
        val found = kitDir.walkTopDown()
            .filter { it.isFile && it.extension == "kt" && "${File.separator}build${File.separator}" !in it.path && "Test" !in it.name }
            .flatMap { file -> literal.findAll(file.readText()).map { it.groupValues[1] } }
            .toSet()
        val unregistered = found - NoticeCodes.ALL.toSet()
        assertTrue("unregistered notice codes in Kit sources: $unregistered", unregistered.isEmpty())
        // Codes the registry says the Kit emits must exist as constants.
        notices.filter { it["emittedBy"] != "DART" }.forEach { assertTrue("${it["code"]}", it["code"] in NoticeCodes.ALL) }
    }
}
