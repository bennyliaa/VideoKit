package com.videokit.testkit

import com.videokit.api.SessionVisibility
import com.videokit.core.runtime.VisibilityPolicy
import com.videokit.testkit.internal.MiniJson
import org.junit.Assert.assertEquals
import org.junit.Test

/** Verifies [VisibilityPolicy] and [SessionVisibility] against `spec/vectors/multi-instance/visibility.json` (04A V1). */
class VisibilityPolicyVectorsTest {
    private val file = MiniJson.parse(SpecFiles.read("vectors/multi-instance/visibility.json")) as Map<*, *>
    private val defaults = file["defaults"] as Map<*, *>
    private val rows = (file["visibilities"] as List<*>).map { it as Map<*, *> }

    @Test
    fun everyVisibilityIsListedInOrder() {
        assertEquals("visibility-policy", file["kind"])
        assertEquals(SessionVisibility.entries.map { it.name }, rows.map { it["visibility"] })
    }

    @Test
    fun policyMatches() {
        val offscreen = (defaults["offscreenReleaseMs"] as Number).toLong()
        val background = (defaults["backgroundReleaseMs"] as Number).toLong()
        assertEquals(VisibilityPolicy.DEFAULT_OFFSCREEN_RELEASE_MS, offscreen)
        assertEquals(VisibilityPolicy.DEFAULT_BACKGROUND_RELEASE_MS, background)
        rows.forEach { row ->
            val visibility = SessionVisibility.valueOf(row["visibility"] as String)
            assertEquals("pauses $visibility", row["pauses"], VisibilityPolicy.pauses(visibility))
            assertEquals("mayReduceQuality $visibility", row["mayReduceQuality"], VisibilityPolicy.mayReduceQuality(visibility))
            val expected = (row["releaseAfter"] as String?)?.let { (defaults[it] as Number).toLong() }
            assertEquals("releaseAfter $visibility", expected, VisibilityPolicy.releaseDelayMs(visibility, offscreen, background))
        }
    }
}
