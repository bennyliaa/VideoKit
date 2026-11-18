package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ErrorCode
import com.videokit.api.MaskAvatar
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskType
import com.videokit.api.SourceProbe
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingRun
import com.videokit.api.TrackingRunStatus
import com.videokit.api.VideoKitEditCommand
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue

class TimelineEditorTest {
    private val source = EditSource("src-1", "media-1", probe = SourceProbe(10_000_000, 1280, 720))
    private var now = 100L

    private fun editor(document: ProjectDocument = ProjectDocument("p", sources = listOf(source)), undoLimit: Int = 100) =
        TimelineEditor(document, undoLimit = undoLimit, clockMs = { now })

    private fun TimelineEditor.add(inUs: Long, outUs: Long): String =
        assertIs<EditOutcome.Applied>(apply(VideoKitEditCommand.AddClip("src-1", inUs, outUs))).createdId!!

    @Test
    fun commandsIncrementRevisionAndStampTheChange() {
        val editor = editor()
        now = 500L
        val id = editor.add(0, 1_000_000)
        assertEquals("clip-2", id, "ids continue after the document's highest id (src-1)")
        assertEquals(1L, editor.document.revision)
        assertEquals(500L, editor.document.updatedAtMs)
        val rejected = assertIs<EditOutcome.Rejected>(editor.apply(VideoKitEditCommand.RemoveClip("missing")))
        assertEquals(ErrorCode.INVALID_ARGUMENT, rejected.error.code)
        assertEquals("INVALID_ARGUMENT:UNKNOWN_CLIP", rejected.error.diagnostic)
        assertEquals(1L, editor.document.revision, "a rejection changes nothing")
        assertIs<EditOutcome.Applied>(editor.undo())
        assertEquals(2L, editor.document.revision, "undo is a change")
    }

    @Test
    fun restoredProjectsNeverReuseIds() {
        val restored = ProjectDocument("p", sources = listOf(source), clips = listOf(Clip("clip-41", "src-1", 0, 1_000)))
        val editor = editor(restored)
        assertFalse(editor.canUndo, "a restored project has no history")
        assertEquals("clip-42", editor.add(0, 2_000))
        assertEquals("src-43", editor.newSourceId())
    }

    @Test
    fun splitNamesTheSecondClipAndKeepsTheDuration() {
        val editor = editor()
        val first = editor.add(0, 4_000_000)
        val split = assertIs<EditOutcome.Applied>(editor.apply(VideoKitEditCommand.SplitAt(first, 1_500_000)))
        assertEquals(listOf(first, split.createdId), editor.document.clips.map { it.clipId })
        assertEquals(listOf(0L to 1_500_000L, 1_500_000L to 4_000_000L), editor.document.clips.map { it.inUs to it.outUs })
        assertEquals(4_000_000L, editor.document.durationUs)
    }

    @Test
    fun historyIsBoundedByTheUndoLimit() {
        val editor = editor(undoLimit = 3)
        repeat(5) { editor.add(it * 1_000L, it * 1_000L + 500L) }
        repeat(3) { assertIs<EditOutcome.Applied>(editor.undo()) }
        assertEquals(2, editor.document.clips.size, "only the last 3 steps are undoable")
        val rejected = assertIs<EditOutcome.Rejected>(editor.undo())
        assertEquals("ILLEGAL_STATE:NOTHING_TO_UNDO", rejected.error.diagnostic)
        assertTrue(editor.canRedo)
    }

    @Test
    fun sourcesAndTrackingAreNotUndoable() {
        val editor = editor()
        editor.add(0, 1_000)
        val revision = editor.document.revision
        editor.putSource(EditSource("src-9", "media-9", probe = SourceProbe(1_000, 10, 10)))
        assertEquals(revision + 1, editor.document.revision)
        editor.setTracking(TrackingRun("mask-1", TrackingRunStatus.COMPLETED))
        assertEquals(revision + 1, editor.document.revision, "tracking results do not change the revision")
        assertIs<EditOutcome.Applied>(editor.undo())
        assertEquals(2, editor.document.sources.size, "undo does not remove a probed source")
        assertTrue(editor.document.clips.isEmpty())
        assertEquals(setOf("mask-1"), editor.document.tracking.keys)
        // Re-probing replaces the source in place.
        editor.putSource(source.copy(mismatch = true))
        assertEquals(listOf("src-1", "src-9"), editor.document.sources.map { it.sourceId })
        assertTrue(editor.document.source("src-1")!!.mismatch)
    }

    @Test
    fun replaceMaskIsOneUndoableStep() {
        val editor = editor()
        editor.add(0, 2_000_000)
        val maskId = assertIs<EditOutcome.Applied>(
            editor.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f), TimeRangeUs(0, 1_000_000))),
        ).createdId!!
        val mask = editor.document.mask(maskId)!!
        assertNull(editor.replaceMask(mask.copy(maskId = "unknown")))
        editor.replaceMask(mask.copy(enabled = false))
        assertFalse(editor.document.mask(maskId)!!.enabled)
        assertIs<EditOutcome.Applied>(editor.undo())
        assertTrue(editor.document.mask(maskId)!!.enabled)
    }

    @Test
    fun avatarsAreSetBeforeTheImageStyle() {
        val editor = editor()
        editor.add(0, 2_000_000)
        val maskId = assertIs<EditOutcome.Applied>(
            editor.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f), TimeRangeUs(0, 1_000_000))),
        ).createdId!!
        val noAvatar = assertIs<EditOutcome.Rejected>(editor.apply(VideoKitEditCommand.SetMaskStyle(maskId, MaskStyle.IMAGE, 0.5f)))
        assertEquals("INVALID_ARGUMENT:MASK_AVATAR", noAvatar.error.diagnostic)
        val badScale = editor.apply(VideoKitEditCommand.SetMaskAvatar(maskId, MaskAvatar("host:a", scale = 0f)))
        assertIs<EditOutcome.Rejected>(badScale)
        assertIs<EditOutcome.Rejected>(editor.apply(VideoKitEditCommand.SetMaskAvatar(maskId, MaskAvatar(" "))))
        val avatar = MaskAvatar("host:a", scale = 1.5f, offsetY = -0.1f)
        assertIs<EditOutcome.Applied>(editor.apply(VideoKitEditCommand.SetMaskAvatar(maskId, avatar)))
        assertIs<EditOutcome.Applied>(editor.apply(VideoKitEditCommand.SetMaskStyle(maskId, MaskStyle.IMAGE, 0.5f)))
        assertEquals(MaskStyle.IMAGE, editor.document.mask(maskId)!!.style)
        assertEquals(avatar, editor.document.mask(maskId)!!.avatar)
        // Snapshot 1.1 keeps both.
        assertEquals(editor.document, ProjectJson.decode(ProjectJson.encode(editor.document)))
    }

    @Test
    fun projectsFromANewerMinorAreOnlySavedAsCopies() {
        // Schema R8 (04A E7 Q3): the reader dropped what it does not know, so the original must stay.
        val newer = editor(ProjectDocument("p", sources = listOf(source), sourceSchemaMinor = ProjectJson.SCHEMA_MINOR + 1))
        assertEquals(SaveMode.SAVE_AS_COPY, newer.saveMode)
        val rejected = assertIs<SaveResult.Rejected>(newer.save(SaveMode.OVERWRITE))
        assertEquals("ILLEGAL_STATE:OVERWRITE_NEWER_MINOR", rejected.error.diagnostic)
        assertTrue(assertIs<SaveResult.Saved>(newer.save(SaveMode.SAVE_AS_COPY)).copyRequired)
        // Edits keep the origin; a project of this or an older minor overwrites normally.
        newer.add(0, 1_000)
        assertEquals(SaveMode.SAVE_AS_COPY, newer.saveMode)
        val current = editor()
        assertEquals(SaveMode.OVERWRITE, current.saveMode)
        assertIs<SaveResult.Saved>(current.save(SaveMode.OVERWRITE))
    }

    @Test
    fun trackingCommandsAreNotEdits() {
        val editor = editor()
        assertEquals(EditOutcome.NotAnEdit, editor.apply(VideoKitEditCommand.CancelTracking("mask-1")))
        assertEquals(0L, editor.document.revision)
    }
}
