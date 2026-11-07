package com.videokit.api

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/**
 * Edit project phase (04 §6, original requirement §19.2):
 * `CREATED → PREPARING → READY ⇄ TRACKING → READY → EXPORTING → COMPLETED / FAILED / CANCELLING → CANCELLED`,
 * any → `RELEASING → RELEASED`. After COMPLETED, FAILED or CANCELLED a new edit command returns to READY.
 */
public enum class EditPhase {
    /** Created, no source yet. */
    CREATED,

    /** Sources are being probed. */
    PREPARING,

    /** Ready for editing. */
    READY,

    /** Automatic tracking in progress. */
    TRACKING,

    /** Export in progress. */
    EXPORTING,

    /** The last export completed. */
    COMPLETED,

    /** The last export failed. */
    FAILED,

    /** The export is being cancelled. */
    CANCELLING,

    /** The last export was cancelled. */
    CANCELLED,

    /** Release in progress. */
    RELEASING,

    /** Released; terminal. */
    RELEASED,
}

/** A half-open time range `[startUs, endUs)` in microseconds. */
public data class TimeRangeUs(
    /** Start, inclusive. */
    val startUs: Long,
    /** End, exclusive. */
    val endUs: Long,
) {
    /** Duration in microseconds. */
    public val durationUs: Long get() = endUs - startUs

    /** Whether [startUs] < [endUs]. */
    public val isValid: Boolean get() = startUs in 0 until endUs

    /** Whether [timeUs] is inside the range. */
    public operator fun contains(timeUs: Long): Boolean = timeUs >= startUs && timeUs < endUs
}

/** Opaque handle of a source added to a project. */
public data class SourceToken(
    /** Source id inside the project. */
    val sourceId: String,
)

/** Probe information of a project source (08 §2.1). */
public data class SourceProbe(
    /** Duration in microseconds. */
    val durationUs: Long,
    /** Coded width. */
    val width: Int,
    /** Coded height. */
    val height: Int,
    /** Rotation metadata in degrees. */
    val rotationDeg: Int = 0,
    /** Frame rate, if known. */
    val frameRate: Float? = null,
    /** Video codec MIME type, if known. */
    val videoCodec: String? = null,
    /** Audio codec MIME type, if any. */
    val audioCodec: String? = null,
    /** Whether the source has audio. */
    val hasAudio: Boolean = false,
)

/** A source of the project (08 §2.1). Identity is project id + source id + media token, never a path. */
public data class EditSource(
    /** Source id. */
    val sourceId: String,
    /** Media token. */
    val mediaToken: String,
    /** Display name; display only. */
    val displayName: String? = null,
    /** Probe result; `null` while preparing. */
    val probe: SourceProbe? = null,
    /** Whether a restored project found different probe data than recorded (08 §2.1). */
    val mismatch: Boolean = false,
)

/** A clip of the timeline (08 §2.1). */
public data class Clip(
    /** Clip id. */
    val clipId: String,
    /** Source id. */
    val sourceId: String,
    /** In point in source time (microseconds). */
    val inUs: Long,
    /** Out point in source time (microseconds), exclusive. */
    val outUs: Long,
) {
    /** Clip duration. */
    public val durationUs: Long get() = outUs - inUs
}

/** The timeline: sources and ordered clips (08 §2.1). Clip order is playback order. */
public data class Timeline(
    /** Sources. */
    val sources: List<EditSource> = emptyList(),
    /** Ordered clips. */
    val clips: List<Clip> = emptyList(),
) {
    /** Total output duration: the sum of clip durations (08 §3). */
    public val durationUs: Long get() = clips.sumOf { it.durationUs }
}

/** Mask type (08 §4). */
public enum class MaskType {
    /** Manually placed. */
    MANUAL,

    /** Face tracking. */
    FACE,

    /** Object tracking. */
    OBJECT,
}

/** Mask effect (08 §4). */
public enum class MaskStyle {
    /** Pixelation. */
    MOSAIC,

    /** Blur. */
    BLUR,
}

/**
 * A mask region, normalized 0..1 to the rotation-corrected source frame (04 §1).
 * ([x], [y]) is the top-left corner before rotation around the region center.
 */
public data class MaskRegion(
    /** Left edge. */
    val x: Float,
    /** Top edge. */
    val y: Float,
    /** Width. */
    val width: Float,
    /** Height. */
    val height: Float,
    /** Rotation around the center in degrees. */
    val rotationDeg: Float = 0f,
) {
    /** Whether the region is inside 0..1 and has a positive size. */
    public val isValid: Boolean
        get() = width > 0f && height > 0f && x >= 0f && y >= 0f && x + width <= 1f + EPSILON && y + height <= 1f + EPSILON

    private companion object {
        const val EPSILON = 1e-4f
    }
}

/** Origin of a keyframe. */
public enum class KeyframeSource {
    /** Placed or corrected by the user. */
    USER,

    /** Produced by the tracker. */
    TRACKER,
}

/** Tracking quality of a time range or keyframe (09). */
public enum class CoverageQuality {
    /** Tracked with good confidence. */
    TRACKED,

    /** Low confidence. */
    LOW_CONFIDENCE,

    /** Ambiguous target. */
    AMBIGUOUS,

    /** Target lost. */
    LOST,
}

/** A mask keyframe; regions are linearly interpolated between keyframes (08 §4). */
public data class MaskKeyframe(
    /** Timeline time in microseconds. */
    val atUs: Long,
    /** Region. */
    val region: MaskRegion,
    /** Origin. */
    val source: KeyframeSource = KeyframeSource.USER,
    /** Quality for tracker keyframes; `null` for user keyframes. */
    val quality: CoverageQuality? = null,
)

/** A mask track (08 §4). */
public data class MaskTrack(
    /** Mask id. */
    val maskId: String,
    /** Type. */
    val type: MaskType,
    /** Effect. */
    val style: MaskStyle = MaskStyle.MOSAIC,
    /** Effect strength 0..1. */
    val strength: Float = 0.5f,
    /** Whether the mask is enabled. */
    val enabled: Boolean = true,
    /** Active time range on the timeline. */
    val rangeUs: TimeRangeUs,
    /** Keyframes sorted by time. */
    val keyframes: List<MaskKeyframe> = emptyList(),
)

/** One coverage range of a tracking run (09). */
public data class CoverageRange(
    /** Time range on the timeline. */
    val rangeUs: TimeRangeUs,
    /** Quality. */
    val quality: CoverageQuality,
)

/** Coverage report of a tracking run (09). */
public data class CoverageReport(
    /** Ranges sorted by time. */
    val ranges: List<CoverageRange> = emptyList(),
)

/** State of a tracking run. */
public enum class TrackingRunStatus {
    /** Running. */
    RUNNING,

    /** Completed. */
    COMPLETED,

    /** Cancelled. */
    CANCELLED,

    /** Failed. */
    FAILED,
}

/** Progress and result of tracking one mask. */
public data class TrackingRun(
    /** Mask id. */
    val maskId: String,
    /** Status. */
    val status: TrackingRunStatus,
    /** Progress 0..1, when it can be estimated reliably; otherwise `null`. */
    val progress: Float? = null,
    /** Coverage, when available. */
    val coverage: CoverageReport? = null,
    /** Error when failed. */
    val error: VideoKitStableError? = null,
)

/** Export stage (08 §6). */
public enum class ExportStage {
    /** Preparing the plan and the sink. */
    PREPARING,

    /** Completing missing tracking. */
    TRACKING,

    /** Encoding / muxing. */
    ENCODING,

    /** Verifying the output. */
    VERIFYING,

    /** Output written and verified. */
    WRITING_COMPLETE,
}

/** Export progress (08 §6, original requirement §17.4). Percentages are never faked. */
public data class ExportProgress(
    /** Export id. */
    val exportId: String,
    /** Stage. */
    val stage: ExportStage,
    /** Completed fraction 0..1, only when it can be estimated reliably. */
    val fraction: Float? = null,
    /** Processed output duration in microseconds. */
    val processedUs: Long = 0L,
    /** Processed frames, if known. */
    val processedFrames: Long? = null,
    /** Output bytes written. */
    val outputBytes: Long = 0L,
    /** Remaining time estimate in microseconds, only when reliable. */
    val remainingEstimateUs: Long? = null,
    /** Whether the export can still be cancelled. */
    val cancellable: Boolean = true,
)

/** Estimates of the export output (08 §3). */
public data class EditEstimate(
    /** Estimated output duration. */
    val durationUs: Long = 0L,
    /** Estimated size in bytes; `null` when it cannot be estimated. */
    val sizeBytes: Long? = null,
)

/** Observable edit project state (14 §3.3). */
public data class VideoKitEditState(
    /** Phase. */
    val phase: EditPhase = EditPhase.CREATED,
    /** Incremented by every successful edit command; async results carry it and stale ones are dropped. */
    val revision: Long = 0L,
    /** Sources and clips. */
    val timeline: Timeline = Timeline(),
    /** Masks. */
    val masks: List<MaskTrack> = emptyList(),
    /** Tracking runs by mask id. */
    val tracking: Map<String, TrackingRun> = emptyMap(),
    /** Current or last export progress. */
    val export: ExportProgress? = null,
    /** Whether undo is possible. */
    val canUndo: Boolean = false,
    /** Whether redo is possible. */
    val canRedo: Boolean = false,
    /** Output estimates. */
    val estimate: EditEstimate = EditEstimate(),
    /** Current error. */
    val error: VideoKitStableError? = null,
)

/** Edit command (08 §2.2, 14 §3.3). All commands are undoable. */
public sealed interface VideoKitEditCommand {
    /** Adds a clip of [sourceId] at [index] (end when `null`). */
    public data class AddClip(
        /** Source id. */
        val sourceId: String,
        /** In point (source time). */
        val inUs: Long,
        /** Out point (source time), exclusive. */
        val outUs: Long,
        /** Insert position; `null` appends. */
        val index: Int? = null,
    ) : VideoKitEditCommand

    /** Splits [clipId] at source time [atUs]. */
    public data class SplitAt(
        /** Clip id. */
        val clipId: String,
        /** Split point in source time, strictly inside the clip. */
        val atUs: Long,
    ) : VideoKitEditCommand

    /** Changes the in/out points of [clipId]. */
    public data class TrimClip(
        /** Clip id. */
        val clipId: String,
        /** New in point. */
        val inUs: Long,
        /** New out point. */
        val outUs: Long,
    ) : VideoKitEditCommand

    /** Removes [clipId]. */
    public data class RemoveClip(
        /** Clip id. */
        val clipId: String,
    ) : VideoKitEditCommand

    /** Moves [clipId] to [toIndex]. */
    public data class MoveClip(
        /** Clip id. */
        val clipId: String,
        /** Target index. */
        val toIndex: Int,
    ) : VideoKitEditCommand

    /** Adds a mask with an initial keyframe at the range start. */
    public data class AddMask(
        /** Type. */
        val type: MaskType,
        /** Initial region. */
        val region: MaskRegion,
        /** Active range on the timeline. */
        val rangeUs: TimeRangeUs,
        /** Effect. */
        val style: MaskStyle = MaskStyle.MOSAIC,
        /** Strength 0..1. */
        val strength: Float = 0.5f,
    ) : VideoKitEditCommand

    /** Adds or replaces the keyframe of [maskId] at [atUs]. */
    public data class UpdateMaskKeyframe(
        /** Mask id. */
        val maskId: String,
        /** Timeline time inside the mask range. */
        val atUs: Long,
        /** Region. */
        val region: MaskRegion,
    ) : VideoKitEditCommand

    /** Removes the keyframe of [maskId] at [atUs]. */
    public data class RemoveMaskKeyframe(
        /** Mask id. */
        val maskId: String,
        /** Keyframe time. */
        val atUs: Long,
    ) : VideoKitEditCommand

    /** Changes the effect of [maskId]. */
    public data class SetMaskStyle(
        /** Mask id. */
        val maskId: String,
        /** Effect. */
        val style: MaskStyle,
        /** Strength 0..1. */
        val strength: Float,
    ) : VideoKitEditCommand

    /** Enables or pauses [maskId]. */
    public data class SetMaskEnabled(
        /** Mask id. */
        val maskId: String,
        /** Whether enabled. */
        val enabled: Boolean,
    ) : VideoKitEditCommand

    /** Removes [maskId]. */
    public data class RemoveMask(
        /** Mask id. */
        val maskId: String,
    ) : VideoKitEditCommand

    /** Starts tracking [maskId] (FACE or OBJECT masks) over its range. */
    public data class StartTracking(
        /** Mask id. */
        val maskId: String,
    ) : VideoKitEditCommand

    /** Adds a user correction keyframe to a tracked mask (09). */
    public data class CorrectTracking(
        /** Mask id. */
        val maskId: String,
        /** Timeline time. */
        val atUs: Long,
        /** Corrected region. */
        val region: MaskRegion,
    ) : VideoKitEditCommand

    /** Cancels tracking of [maskId]. */
    public data class CancelTracking(
        /** Mask id. */
        val maskId: String,
    ) : VideoKitEditCommand
}

/** Result of an edit command, undo or redo. */
public sealed interface EditCommandResult {
    /** Applied; the project is now at [revision]. */
    public data class Applied(
        /** New revision. */
        val revision: Long,
    ) : EditCommandResult

    /** Rejected (out of range, conflict, illegal phase). */
    public data class Rejected(
        /** Reason. */
        val error: VideoKitStableError,
    ) : EditCommandResult

    /** Not supported by this build or device. */
    public data class Unsupported(
        /** Reason. */
        val reason: UnsupportedReason,
    ) : EditCommandResult

    /** The project has been released. */
    public data object ProjectReleased : EditCommandResult
}

/** One-off edit project events (original requirement §17.4). */
public sealed interface VideoKitEditEvent {
    /** A source was probed. */
    public data class SourceProbed(
        /** Source id. */
        val sourceId: String,
    ) : VideoKitEditEvent

    /** A restored source does not match its recorded probe data; user confirmation is needed. */
    public data class SourceMismatch(
        /** Source id. */
        val sourceId: String,
    ) : VideoKitEditEvent

    /** Tracking lost the target in [rangeUs]. */
    public data class TrackingLost(
        /** Mask id. */
        val maskId: String,
        /** Lost range. */
        val rangeUs: TimeRangeUs,
    ) : VideoKitEditEvent

    /** The export entered [stage]. */
    public data class ExportStageChanged(
        /** Export id. */
        val exportId: String,
        /** Stage. */
        val stage: ExportStage,
    ) : VideoKitEditEvent

    /** The export completed. */
    public data class ExportCompleted(
        /** Result. */
        val result: VideoKitExportResult,
    ) : VideoKitEditEvent

    /** The export failed; the sink was aborted. */
    public data class ExportFailed(
        /** Export id. */
        val exportId: String,
        /** Error. */
        val error: VideoKitStableError,
    ) : VideoKitEditEvent

    /** Cancellation was confirmed; the sink was aborted. */
    public data class ExportCancelled(
        /** Export id. */
        val exportId: String,
    ) : VideoKitEditEvent

    /** A warning, for example `BOUNDARY_ALIGNED_TO_KEYFRAME`. */
    public data class Warning(
        /** Warning code. */
        val code: String,
    ) : VideoKitEditEvent

    /** All input and output resources were released. */
    public data object ResourcesReleased : VideoKitEditEvent
}

/** Configuration of an edit project. */
public data class EditProjectConfig(
    /** Export presets the host allows; empty = all. */
    val allowedPresets: Set<ExportPreset> = emptySet(),
    /** Whether automatic tracking may be used. */
    val trackingAllowed: Boolean = true,
    /** Initial playhead position (for example the playback position when entering the editor). */
    val initialPositionUs: Long? = null,
)

/**
 * Serialized edit project (04 §10, 08 §2.1): versioned JSON produced by [VideoKitEditProject.snapshot].
 * The payload is opaque to hosts.
 */
public data class SerializedEditProject(
    /** Schema major version; older versions are migrated, unknown future versions are rejected. */
    val schemaVersion: Int,
    /** Versioned JSON payload. */
    val json: String,
) {
    public companion object {
        /** Schema version written by this API version. */
        public const val CURRENT_SCHEMA_VERSION: Int = 1
    }
}

/**
 * An edit project (04 §6). Sources are read only; output only goes through the host sink.
 */
public interface VideoKitEditProject : AutoCloseable {
    /** Opaque project id. */
    public val projectId: String

    /** State. */
    public val state: StateFlow<VideoKitEditState>

    /** Bounded events. */
    public val events: Flow<VideoKitEditEvent>

    /** Adds and probes a source. Throws [VideoKitException] when probing fails. */
    public suspend fun addSource(source: VideoKitMediaSource): SourceToken

    /** Applies an edit command. */
    public suspend fun apply(command: VideoKitEditCommand): EditCommandResult

    /** Undoes the last command. */
    public suspend fun undo(): EditCommandResult

    /** Redoes the last undone command. */
    public suspend fun redo(): EditCommandResult

    /** Serializes the project. */
    public suspend fun snapshot(): SerializedEditProject

    /** Preview session sharing the export plan. The same instance is returned until the project is released. */
    public fun previewSession(): VideoKitSession

    /** Checks whether [request] can be exported to [sink] (capabilities, sink, space, tracking coverage). */
    public suspend fun checkExport(request: VideoKitExportRequest, sink: VideoKitOutputSink): ExportPrecheck

    /**
     * Exports. On failure or cancellation the sink is aborted and a [VideoKitException] is thrown
     * ([ErrorCode.CANCELLED] after [cancelExport]); partial output is never marked ready.
     */
    public suspend fun export(request: VideoKitExportRequest, sink: VideoKitOutputSink): VideoKitExportResult

    /** Cancels the export [exportId] within a bounded time; unknown ids are ignored. */
    public suspend fun cancelExport(exportId: String)

    /** Releases the project, its preview session and all handles. Idempotent. */
    override fun close()
}
