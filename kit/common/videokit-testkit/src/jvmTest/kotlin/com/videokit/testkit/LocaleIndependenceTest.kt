package com.videokit.testkit

import com.videokit.api.EditProjectConfig
import com.videokit.api.ExportPreset
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.TimeRangeUs
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.Visibility
import com.videokit.testkit.internal.MiniJson
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Locale

/**
 * 13 §3.1: diagnostics, codes, numbers, time codes and snapshots are machine formatted (English, ASCII
 * digits, `Locale.ROOT` semantics) and do not change with the device language. Every check runs under
 * Turkish (dotted/dotless i), Arabic (Arabic-Indic digits, comma decimal) and Simplified Chinese defaults
 * and must give the same result as under `Locale.ROOT`.
 */
class LocaleIndependenceTest {
    private val original = Locale.getDefault()

    @After
    fun restore() {
        Locale.setDefault(original)
    }

    private fun <T> underEveryLocale(block: () -> T): T {
        Locale.setDefault(Locale.ROOT)
        val expected = block()
        listOf(Locale.forLanguageTag("tr-TR"), Locale.forLanguageTag("ar-EG"), Locale.SIMPLIFIED_CHINESE).forEach { locale ->
            Locale.setDefault(locale)
            assertEquals("result under $locale", expected, block())
        }
        return expected
    }

    @Test
    fun timecodeAndTagsUseAsciiDigits() {
        val timecode = underEveryLocale { TestPattern.formatTimecode(3_723_456_000) }
        assertEquals("01:02:03.456", timecode)
        underEveryLocale { TestPattern.frame("fake-session-0042", 1_500_000, 1920, 1080).copy(blocks = emptyList()) }
    }

    @Test
    fun jsonNumbersAreLocaleIndependent() {
        val text = underEveryLocale { MiniJson.write(mapOf("f" to 0.25f, "d" to 1234.5, "l" to 1_000_000L)) }
        assertEquals("""{"f":0.25,"d":1234.5,"l":1000000}""", text)
    }

    @Test
    fun diagnosticsAreUpperCaseAsciiUnderTurkish() = runTest {
        val kit = FakeVideoKit(RecordingHostCallbacks(), FakeVideoKitOptions(scope = backgroundScope))
        val session = kit.createSession(VideoKitSessionConfig())
        val diagnostics = underEveryLocale {
            kotlinx.coroutines.runBlocking {
                listOf(VideoKitCommand.Play, VideoKitCommand.SetVisibility(Visibility.VISIBLE), VideoKitCommand.SeekTo(1))
                    .map { (session.execute(it) as? VideoKitCommandResult.Rejected)?.error?.diagnostic }
            }
        }
        // PLAY / SEEKTO are rejected before bind; the diagnostic keeps a plain ASCII "I" in Turkish too.
        assertEquals(listOf("ILLEGAL_STATE:PLAY_IN_CREATED", null, "ILLEGAL_STATE:SEEK_IN_CREATED"), diagnostics)
        diagnostics.filterNotNull().forEach { text -> assertTrue(text, text.all { it.code < 128 }) }
    }

    @Test
    fun editSnapshotIsLocaleIndependent() = runTest {
        val kit = FakeVideoKit(RecordingHostCallbacks(), FakeVideoKitOptions(scope = backgroundScope, wallClockMs = { 1_700_000_000_000L }))
        val project = kit.createEditProject(EditProjectConfig())
        val source = project.addSource(FakeMediaSources.video("locale"))
        project.apply(VideoKitEditCommand.AddClip(source.sourceId, 0, 2_000_000))
        project.apply(
            VideoKitEditCommand.AddMask(
                MaskType.MANUAL,
                MaskRegion(0.125f, 0.5f, 0.25f, 0.2f),
                TimeRangeUs(0, 1_000_000),
                strength = 0.75f,
            ),
        )
        val json = underEveryLocale { kotlinx.coroutines.runBlocking { project.snapshot().json } }
        assertTrue(json, json.contains("\"x\":0.125") && json.contains("\"strength\":0.75") && json.all { it.code < 128 })
        val precheck = underEveryLocale {
            kotlinx.coroutines.runBlocking {
                project.checkExport(VideoKitExportRequest(ExportPreset.P720, exportId = "e"), RecordingOutputSink()).estimate
            }
        }
        assertEquals(2_000_000L, precheck.durationUs)
    }

    @Test
    fun commandNamesUseRootCaseMapping() {
        // Kotlin's uppercase()/lowercase() are locale independent; this guards against String.toUpperCase(Locale) regressions.
        assertEquals("SETVISIBILITY", underEveryLocale { "SetVisibility".uppercase() })
        assertEquals("avi", underEveryLocale { "AVI".lowercase() })
    }
}
