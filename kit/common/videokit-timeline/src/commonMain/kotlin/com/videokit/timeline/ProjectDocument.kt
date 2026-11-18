package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ExportPreset
import com.videokit.api.MaskTrack
import com.videokit.api.Timeline
import com.videokit.api.TrackingRun

/**
 * The serializable content of an edit project (08 §2.1): what [ProjectJson] writes into a snapshot and reads back.
 * Immutable; [TimelineEditor] produces new documents. Identity is project id + source id + media token, never a path;
 * times are microseconds; mask regions are normalized to the rotation-corrected source frame.
 *
 * Not part of the document: the phase, the undo/redo history and live tracking or export work. A restored project
 * starts with an empty history, and tracking runs that were in progress restart (08 §6).
 */
public data class ProjectDocument(
    /** Opaque project id. */
    val projectId: String,
    /** Incremented by every successful change (commands, undo, redo, source changes). */
    val revision: Long = 0L,
    /** Creation time, epoch milliseconds. */
    val createdAtMs: Long = 0L,
    /** Time of the last change, epoch milliseconds. */
    val updatedAtMs: Long = 0L,
    /** Sources in insertion order. */
    val sources: List<EditSource> = emptyList(),
    /** Ordered clips; order is playback order. */
    val clips: List<Clip> = emptyList(),
    /** Mask tracks (08 §4). */
    val masks: List<MaskTrack> = emptyList(),
    /** Tracking results by mask id (09). */
    val tracking: Map<String, TrackingRun> = emptyMap(),
    /** Last used export preset, if any. */
    val exportPreset: ExportPreset? = null,
    /**
     * The `schemaMinor` the document was read from (runtime only, not written; new documents: this Kit's
     * [ProjectJson.SCHEMA_MINOR]). Above this Kit's minor the reader may have dropped unknown data, so the original
     * must not be overwritten (schema R8, [ProjectJson.saveMode]).
     */
    val sourceSchemaMinor: Int = ProjectJson.SCHEMA_MINOR,
) {
    /** Sources and clips as the API timeline. */
    public val timeline: Timeline get() = Timeline(sources, clips)

    /** Output duration: the sum of the clip durations (08 §3). */
    public val durationUs: Long get() = clips.sumOf { it.durationUs }

    /** The source with [sourceId], if any. */
    public fun source(sourceId: String): EditSource? = sources.firstOrNull { it.sourceId == sourceId }

    /** The clip with [clipId], if any. */
    public fun clip(clipId: String): Clip? = clips.firstOrNull { it.clipId == clipId }

    /** The mask with [maskId], if any. */
    public fun mask(maskId: String): MaskTrack? = masks.firstOrNull { it.maskId == maskId }

    /**
     * Highest numeric suffix of the ids in this document (`src-3`, `clip-12` → 12); id generators of a restored
     * project continue after it so ids are never reused.
     */
    public fun maxIdNumber(): Long {
        val ids = sources.map { it.sourceId } + clips.map { it.clipId } + masks.map { it.maskId }
        return ids.mapNotNull { it.substringAfterLast('-').toLongOrNull() }.maxOrNull() ?: 0L
    }
}
