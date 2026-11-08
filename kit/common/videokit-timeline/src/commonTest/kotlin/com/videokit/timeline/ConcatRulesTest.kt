package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ExportPreset
import com.videokit.api.ExportWarnings
import com.videokit.api.SourceProbe
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/** Unit checks of [ConcatRules]; the full table is `spec/vectors/timeline/concat-path.json`. */
class ConcatRulesTest {
    private val probe = SourceProbe(10_000_000, 1920, 1080, 0, 30f, "video/avc", "audio/mp4a-latm", hasAudio = true)
    private val sources = listOf(EditSource("a", "media-a", probe = probe), EditSource("b", "media-b", probe = probe))

    @Test
    fun fastPathKeepsClipsAndHasNoReasons() {
        val clips = listOf(Clip("c1", "a", 0, 1_000_000), Clip("c2", "b", 0, 2_000_000))
        val decision = ConcatRules.decide(ConcatRequest(clips, sources))
        assertEquals(ConcatPath.FAST, decision.path)
        assertTrue(decision.reasons.isEmpty())
        assertEquals(clips, decision.effectiveClips)
        assertTrue(decision.warnings.isEmpty())
    }

    @Test
    fun snappedCutsAreReportedOnce() {
        val clips = listOf(Clip("c1", "a", 1_500_000, 2_000_000), Clip("c2", "a", 2_500_000, 3_000_000))
        val decision = ConcatRules.decide(ConcatRequest(clips, sources, keyframesUs = mapOf("a" to listOf(0L, 1_000_000L, 2_000_000L))))
        assertEquals(ConcatPath.FAST, decision.path)
        assertEquals(listOf(1_000_000L, 2_000_000L), decision.effectiveClips.map { it.inUs })
        assertEquals(listOf(ExportWarnings.BOUNDARY_ALIGNED_TO_KEYFRAME), decision.warnings)
    }

    @Test
    fun transcodeKeepsTheClipsAsSet() {
        val clips = listOf(Clip("c1", "a", 1_500_000, 2_000_000))
        val decision = ConcatRules.decide(
            ConcatRequest(clips, sources, keyframesUs = mapOf("a" to listOf(0L, 1_000_000L)), preset = ExportPreset.P720),
        )
        assertEquals(ConcatPath.TRANSCODE, decision.path)
        assertEquals(listOf(ConcatReason.OUTPUT_RESIZE), decision.reasons)
        assertEquals(clips, decision.effectiveClips, "a transcode cuts exactly")
        assertTrue(decision.warnings.isEmpty())
    }

    @Test
    fun presetLongEdges() {
        assertEquals(null, ConcatRules.longEdgeLimit(ExportPreset.ORIGINAL))
        assertEquals(1920, ConcatRules.longEdgeLimit(ExportPreset.P1080))
        assertEquals(1280, ConcatRules.longEdgeLimit(ExportPreset.P720))
    }
}
