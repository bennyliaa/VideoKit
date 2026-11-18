package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ErrorStage
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskKeyframe
import com.videokit.api.MaskTrack
import com.videokit.api.MaskStyle
import com.videokit.api.MaskType
import com.videokit.api.TrackingRun
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitStableError
import com.videokit.core.runtime.StableErrors

/** Generator of project-unique ids (`src-1`, `clip-2`, `mask-3`); one sequence for all kinds. */
public fun interface IdSource {
    /** A new id with [prefix] (`src`, `clip`, `mask`). */
    public fun next(prefix: String): String
}

/** Sequential [IdSource] starting after [after] (use [ProjectDocument.maxIdNumber] for restored projects). */
public class SequentialIds(after: Long = 0L) : IdSource {
    private var last = after

    override fun next(prefix: String): String = "$prefix-${++last}"
}

/** Outcome of a [TimelineEditor] operation. */
public sealed interface EditOutcome {
    /** Applied; [document] is the new state ([ProjectDocument.revision] incremented). */
    public data class Applied(
        /** The new document. */
        val document: ProjectDocument,
        /** Id of the clip or mask created by AddClip, SplitAt (the new second clip) or AddMask (04A N12). */
        val createdId: String? = null,
    ) : EditOutcome

    /** Rejected: invalid argument or nothing to undo/redo. The document is unchanged. */
    public data class Rejected(
        /** Stable error (INVALID_ARGUMENT or INVALID_STATE, stage EDIT). */
        val error: VideoKitStableError,
    ) : EditOutcome

    /** Not an edit of the document (StartTracking, CancelTracking): handled by the project's tracking runner. */
    public data object NotAnEdit : EditOutcome
}

/**
 * The edit model of a project (08 §2.2, M4-B1): validates and applies [VideoKitEditCommand]s to a
 * [ProjectDocument], with undo/redo. Pure and synchronous; not thread safe (the owning project serializes calls).
 * Phase rules (no edits while tracking or exporting, released projects) are the project's job, not the editor's.
 *
 * Undo/redo covers clips and masks. Sources are not undoable: a probed source stays in the project
 * ([putSource]); tracking runs are runtime results ([setTracking]). Every successful change, including undo and
 * redo, increments the revision. History holds at most [undoLimit] steps; the oldest step is dropped beyond that.
 * A restored project starts with an empty history.
 *
 * Rejections use stable diagnostics shared with the Fake (`INVALID_ARGUMENT:<what>`): `UNKNOWN_SOURCE`,
 * `CLIP_RANGE`, `CLIP_INDEX`, `UNKNOWN_CLIP`, `SPLIT_POINT`, `MASK_REGION`, `MASK_RANGE`, `MASK_STRENGTH`,
 * `UNKNOWN_MASK`, `KEYFRAME_TIME`, `UNKNOWN_KEYFRAME`, `LAST_KEYFRAME`, `MASK_NOT_TRACKED`, `ACCEPT_RANGE`, `MASK_AVATAR`; and
 * `ILLEGAL_STATE:NOTHING_TO_UNDO` / `NOTHING_TO_REDO`.
 */
public class TimelineEditor(
    initial: ProjectDocument,
    private val ids: IdSource = SequentialIds(initial.maxIdNumber()),
    /** Maximum number of undo steps. */
    public val undoLimit: Int = DEFAULT_UNDO_LIMIT,
    private val clockMs: () -> Long = { initial.updatedAtMs },
) {
    init {
        require(undoLimit > 0) { "undoLimit must be positive" }
    }

    private data class Content(val clips: List<Clip>, val masks: List<MaskTrack>)

    private val undoStack = ArrayDeque<Content>()
    private val redoStack = ArrayDeque<Content>()

    /** The current document. */
    public var document: ProjectDocument = initial
        private set

    /** Whether [undo] can apply. */
    public val canUndo: Boolean get() = undoStack.isNotEmpty()

    /** Whether [redo] can apply. */
    public val canRedo: Boolean get() = redoStack.isNotEmpty()

    /** How the project may be saved: a copy only when it was read from a newer minor (schema R8, 04A E7 Q3). */
    public val saveMode: SaveMode get() = ProjectJson.saveMode(document)

    /** Serializes the current document for [target]; overwriting a newer-minor original is rejected (R8). */
    public fun save(target: SaveMode): SaveResult = ProjectJson.save(document, target)

    // ------------------------------------------------------------------ non-undoable changes

    /** Adds [source] or replaces the source with the same id (for example after re-probing). Not undoable. */
    public fun putSource(source: EditSource): ProjectDocument {
        val sources = if (document.source(source.sourceId) != null) {
            document.sources.map { if (it.sourceId == source.sourceId) source else it }
        } else {
            document.sources + source
        }
        return change(document.copy(sources = sources))
    }

    /** A new source id from the shared id sequence. */
    public fun newSourceId(): String = ids.next("src")

    /** Replaces the tracking result of [run]'s mask. Not undoable; does not change the revision. */
    public fun setTracking(run: TrackingRun): ProjectDocument {
        document = document.copy(tracking = document.tracking + (run.maskId to run))
        return document
    }

    /** Increments the revision without other changes (for example when tracking starts or is cancelled). */
    public fun bumpRevision(): ProjectDocument = change(document)

    /**
     * Replaces [mask] (same id) as one undoable step, for results that are not commands, such as tracker keyframes
     * (09). Returns `null` when the mask does not exist.
     */
    public fun replaceMask(mask: MaskTrack): ProjectDocument? {
        if (document.mask(mask.maskId) == null) return null
        commit(Content(document.clips, document.masks.map { if (it.maskId == mask.maskId) mask else it }))
        return document
    }

    // ------------------------------------------------------------------ commands

    /** Validates and applies [command]. */
    public fun apply(command: VideoKitEditCommand): EditOutcome = when (val draft = edit(command)) {
        is Draft.Done -> draft.outcome

        is Draft.Step -> {
            commit(draft.content)
            EditOutcome.Applied(document, draft.createdId)
        }
    }

    /** Undoes the last step. */
    public fun undo(): EditOutcome {
        val previous = undoStack.removeLastOrNull() ?: return rejectedState("NOTHING_TO_UNDO")
        redoStack.addLast(content())
        change(previous)
        return EditOutcome.Applied(document)
    }

    /** Redoes the last undone step. */
    public fun redo(): EditOutcome {
        val next = redoStack.removeLastOrNull() ?: return rejectedState("NOTHING_TO_REDO")
        undoStack.addLast(content())
        change(next)
        return EditOutcome.Applied(document)
    }

    private sealed interface Draft {
        class Step(val content: Content, val createdId: String? = null) : Draft

        class Done(val outcome: EditOutcome) : Draft
    }

    private fun rejectedState(what: String) = EditOutcome.Rejected(StableErrors.illegalState(ErrorStage.EDIT, what))

    private fun content() = Content(document.clips, document.masks)

    private fun commit(next: Content) {
        undoStack.addLast(content())
        while (undoStack.size > undoLimit) undoStack.removeFirst()
        redoStack.clear()
        change(next)
    }

    private fun change(next: Content): ProjectDocument = change(document.copy(clips = next.clips, masks = next.masks))

    private fun change(next: ProjectDocument): ProjectDocument {
        document = next.copy(revision = document.revision + 1, updatedAtMs = clockMs())
        return document
    }

    private fun edit(command: VideoKitEditCommand): Draft {
        val clips = document.clips
        val masks = document.masks

        fun fail(what: String) = Draft.Done(EditOutcome.Rejected(StableErrors.invalidArgument(ErrorStage.EDIT, what)))

        fun withClips(next: List<Clip>, createdId: String? = null) = Draft.Step(Content(next, masks), createdId)

        fun withMask(mask: MaskTrack) = Draft.Step(Content(clips, masks.map { if (it.maskId == mask.maskId) mask else it }))

        fun sourceDuration(sourceId: String): Long? = document.source(sourceId)?.probe?.durationUs

        return when (command) {
            is VideoKitEditCommand.AddClip -> {
                val duration = sourceDuration(command.sourceId) ?: return fail("UNKNOWN_SOURCE")
                if (!validRange(command.inUs, command.outUs, duration)) return fail("CLIP_RANGE")
                val index = command.index ?: clips.size
                if (index !in 0..clips.size) return fail("CLIP_INDEX")
                val clip = Clip(ids.next("clip"), command.sourceId, command.inUs, command.outUs)
                withClips(clips.toMutableList().apply { add(index, clip) }, clip.clipId)
            }

            is VideoKitEditCommand.SplitAt -> {
                val index = clips.indexOfFirst { it.clipId == command.clipId }.takeIf { it >= 0 } ?: return fail("UNKNOWN_CLIP")
                val clip = clips[index]
                if (command.atUs <= clip.inUs || command.atUs >= clip.outUs) return fail("SPLIT_POINT")
                val second = Clip(ids.next("clip"), clip.sourceId, command.atUs, clip.outUs)
                withClips(
                    clips.toMutableList().apply {
                        set(index, clip.copy(outUs = command.atUs))
                        add(index + 1, second)
                    },
                    second.clipId,
                )
            }

            is VideoKitEditCommand.TrimClip -> {
                val clip = document.clip(command.clipId) ?: return fail("UNKNOWN_CLIP")
                val duration = sourceDuration(clip.sourceId) ?: return fail("UNKNOWN_SOURCE")
                if (!validRange(command.inUs, command.outUs, duration)) return fail("CLIP_RANGE")
                withClips(clips.map { if (it.clipId == clip.clipId) it.copy(inUs = command.inUs, outUs = command.outUs) else it })
            }

            is VideoKitEditCommand.RemoveClip -> {
                if (document.clip(command.clipId) == null) return fail("UNKNOWN_CLIP")
                withClips(clips.filterNot { it.clipId == command.clipId })
            }

            is VideoKitEditCommand.MoveClip -> {
                val index = clips.indexOfFirst { it.clipId == command.clipId }.takeIf { it >= 0 } ?: return fail("UNKNOWN_CLIP")
                if (command.toIndex !in clips.indices) return fail("CLIP_INDEX")
                withClips(clips.toMutableList().apply { add(command.toIndex, removeAt(index)) })
            }

            is VideoKitEditCommand.AddMask -> {
                if (!command.region.isValid) return fail("MASK_REGION")
                if (!command.rangeUs.isValid || command.rangeUs.endUs > document.durationUs) return fail("MASK_RANGE")
                if (!validStrength(command.strength)) return fail("MASK_STRENGTH")
                val mask = MaskTrack(
                    maskId = ids.next("mask"),
                    type = command.type,
                    style = command.style,
                    strength = command.strength,
                    rangeUs = command.rangeUs,
                    keyframes = listOf(MaskKeyframe(command.rangeUs.startUs, command.region, KeyframeSource.USER)),
                )
                Draft.Step(Content(clips, masks + mask), mask.maskId)
            }

            is VideoKitEditCommand.UpdateMaskKeyframe -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (!command.region.isValid) return fail("MASK_REGION")
                if (command.atUs < mask.rangeUs.startUs || command.atUs > mask.rangeUs.endUs) return fail("KEYFRAME_TIME")
                withMask(mask.withKeyframe(MaskKeyframe(command.atUs, command.region, KeyframeSource.USER)))
            }

            is VideoKitEditCommand.CorrectTracking -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.type == MaskType.MANUAL) return fail("MASK_NOT_TRACKED")
                if (!command.region.isValid) return fail("MASK_REGION")
                if (command.atUs < mask.rangeUs.startUs || command.atUs > mask.rangeUs.endUs) return fail("KEYFRAME_TIME")
                withMask(mask.withKeyframe(MaskKeyframe(command.atUs, command.region, KeyframeSource.USER)))
            }

            is VideoKitEditCommand.RemoveMaskKeyframe -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.keyframes.none { it.atUs == command.atUs }) return fail("UNKNOWN_KEYFRAME")
                if (mask.keyframes.size <= 1) return fail("LAST_KEYFRAME")
                withMask(mask.copy(keyframes = mask.keyframes.filterNot { it.atUs == command.atUs }))
            }

            is VideoKitEditCommand.SetMaskStyle -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (!validStrength(command.strength)) return fail("MASK_STRENGTH")
                // IMAGE needs an avatar first (SetMaskAvatar; schema R7 reads IMAGE without avatar as MOSAIC).
                if (command.style == MaskStyle.IMAGE && mask.avatar == null) return fail("MASK_AVATAR")
                withMask(mask.copy(style = command.style, strength = command.strength))
            }

            is VideoKitEditCommand.SetMaskAvatar -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                val avatar = command.avatar
                val valid = avatar.avatarToken.isNotBlank() && avatar.scale.isFinite() && avatar.scale > 0f &&
                    avatar.offsetX.isFinite() && avatar.offsetY.isFinite()
                if (!valid) return fail("MASK_AVATAR")
                withMask(mask.copy(avatar = avatar))
            }

            is VideoKitEditCommand.SetMaskEnabled -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                withMask(mask.copy(enabled = command.enabled))
            }

            is VideoKitEditCommand.RemoveMask -> {
                if (document.mask(command.maskId) == null) return fail("UNKNOWN_MASK")
                Draft.Step(Content(clips, masks.filterNot { it.maskId == command.maskId }))
            }

            is VideoKitEditCommand.AcceptTrackingRange -> {
                val mask = document.mask(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.type == MaskType.MANUAL) return fail("MASK_NOT_TRACKED")
                val range = command.rangeUs
                if (!range.isValid || range.startUs < mask.rangeUs.startUs || range.endUs > mask.rangeUs.endUs) return fail("ACCEPT_RANGE")
                withMask(mask.copy(acceptedRangesUs = (mask.acceptedRangesUs + range).sortedBy { it.startUs }))
            }

            is VideoKitEditCommand.StartTracking, is VideoKitEditCommand.CancelTracking -> Draft.Done(EditOutcome.NotAnEdit)
        }
    }

    private fun validRange(inUs: Long, outUs: Long, durationUs: Long): Boolean = inUs >= 0 && inUs < outUs && outUs <= durationUs

    private fun validStrength(strength: Float): Boolean = strength.isFinite() && strength in 0f..1f

    private fun MaskTrack.withKeyframe(keyframe: MaskKeyframe): MaskTrack =
        copy(keyframes = (keyframes.filterNot { it.atUs == keyframe.atUs } + keyframe).sortedBy { it.atUs })

    public companion object {
        /** Undo history limit (08 §2.2: frozen in M4; same as the Fake). */
        public const val DEFAULT_UNDO_LIMIT: Int = 100
    }
}
