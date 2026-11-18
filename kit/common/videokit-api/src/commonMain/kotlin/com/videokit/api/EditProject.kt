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

    /**
     * An avatar image drawn over the tracked head (REQ-ED-07, 04A E5/E6); requires [MaskTrack.avatar]. Not rendered
     * before VK-M5A: commands that set it return Unsupported.
     */
    IMAGE,
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

    /** Frames not analysed yet; never counts as covered (09 §3, 04A E2: the snapshot quality enum). */
    NOT_ANALYZED,
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
    /** Head roll in degrees (from the eye line) for [MaskAvatar.followRotation]; `null` when unknown (04A E5, schema 1.1). */
    val rollDeg: Float? = null,
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
    /** Ranges the user explicitly accepted although tracking did not cover them (09 §4). */
    val acceptedRangesUs: List<TimeRangeUs> = emptyList(),
    /** Avatar of style [MaskStyle.IMAGE] (04A E6, schema 1.1); `null` for the other styles. */
    val avatar: MaskAvatar? = null,
)

/**
 * Avatar of a mask (REQ-ED-07, 04A E5/E6). The PNG is not part of the project: the host keeps it and opens it by
 * [avatarToken] ([VideoKitHostCallbacks.openAvatar]); `builtin:N` names a Kit avatar. Scale and offsets are relative to
 * the tracked box and hold for the whole mask.
 */
public data class MaskAvatar(
    /** Opaque host token of the PNG, or `builtin:N`. */
    val avatarToken: String,
    /** Size relative to the tracked box. */
    val scale: Float = 1f,
    /** Horizontal offset relative to the tracked box width. */
    val offsetX: Float = 0f,
    /** Vertical offset relative to the tracked box height. */
    val offsetY: Float = 0f,
    /** Turn with the head ([MaskKeyframe.rollDeg]). */
    val followRotation: Boolean = true,
)

/** One coverage range of a tracking run (09). */
public data class CoverageRange(
    /** Time range on the timeline. */
    val rangeUs: TimeRangeUs,
    /** Quality. */
    val quality: CoverageQuality,
    /** Mask the range belongs to; set where ranges of several masks are listed together (04A T2 precheck). */
    val maskId: String? = null,
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

    /** Writing the verified output to the sink; completion is `EditPhase.COMPLETED` (04A S3). */
    WRITING,
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

    /**
     * Sets the avatar of [maskId] (REQ-ED-07, 04A E6). Before VK-M5A the native Kit returns
     * [EditCommandResult.Unsupported] (avatars are not rendered yet).
     */
    public data class SetMaskAvatar(
        /** Mask id. */
        val maskId: String,
        /** Avatar settings. */
        val avatar: MaskAvatar,
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

    /**
     * Starts tracking [maskId] (FACE or OBJECT masks) over its range (04A S4). [seedRegion] is the object
     * point/box selection (14 §5.7); [targetId] a picked `TrackingCandidate.candidateId`.
     */
    public data class StartTracking(
        /** Mask id. */
        val maskId: String,
        /** What is tracked. */
        val kind: TrackingKind,
        /** Seed region of an object selection, normalized like [MaskRegion]. */
        val seedRegion: MaskRegion? = null,
        /** Picked candidate id. */
        val targetId: String? = null,
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

    /**
     * Explicitly accepts an uncovered or lost interval of a tracked mask (04A I11, 09 §4); the export reports it as
     * the warning `TRACKING_COVERAGE_ACCEPTED` instead of blocking.
     */
    public data class AcceptTrackingRange(
        /** Mask id. */
        val maskId: String,
        /** Accepted range on the timeline, inside the mask range. */
        val rangeUs: TimeRangeUs,
    ) : VideoKitEditCommand
}

/** Result of an edit command, undo or redo. */
public sealed interface EditCommandResult {
    /** Applied; the project is now at [revision]. */
    public data class Applied(
        /** New revision. */
        val revision: Long,
        /** Id of the clip or mask the command created (AddClip, SplitAt: the new second clip, AddMask), if any (04A N12). */
        val createdId: String? = null,
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
     * Exports (04A I5). Normal failures and cancellation are returned as [VideoKitExportResult.Failed] and
     * [VideoKitExportResult.Cancelled], not thrown; the sink is then aborted and partial output is never marked
     * ready. Only programming errors (for example a released project) throw [VideoKitException]. Cancelling the
     * calling coroutine also aborts the sink and rethrows the cancellation.
     */
    public suspend fun export(request: VideoKitExportRequest, sink: VideoKitOutputSink): VideoKitExportResult

    /** Cancels the export [exportId] within a bounded time; unknown ids are ignored. */
    public suspend fun cancelExport(exportId: String)

    /**
     * Detects tracking candidates (for example faces) on the timeline at [atUs] (04A I10, 09 §1). Failures are
     * reported in [CandidateDetectionResult.error] (for example [ErrorCode.TRACKING_MODEL_UNAVAILABLE]).
     */
    public suspend fun detectCandidates(atUs: Long): CandidateDetectionResult

    /** Releases the project, its preview session and all handles. Idempotent. */
    override fun close()
}

/** Kind of a tracking target (09). */
public enum class TrackingKind {
    /** A face. */
    FACE,

    /** A generic object. */
    OBJECT,
}

/** A detected tracking candidate the user can pick (04A I10, 09 §1). */
public data class TrackingCandidate(
    /** Candidate id, valid within the project only. */
    val candidateId: String,
    /** Kind. */
    val kind: TrackingKind,
    /** Region at the detection time, normalized. */
    val region: MaskRegion,
    /** Confidence 0..1, if the detector reports one. */
    val confidence: Float? = null,
)

/** Result of [VideoKitEditProject.detectCandidates]. */
public data class CandidateDetectionResult(
    /** Candidates, possibly empty. */
    val candidates: List<TrackingCandidate> = emptyList(),
    /** Error, for example [ErrorCode.TRACKING_MODEL_UNAVAILABLE] or [ErrorCode.INVALID_ARGUMENT]. */
    val error: VideoKitStableError? = null,
)

/**
 * Optional timeline media of an edit project (04A X2, UI-AUDIT-A4, design pages 15/16: thumbnail film and audio
 * waveform on the clip blocks). A separate interface like the avatar tools: [VideoKitEditProject] is unchanged, and
 * the editor checks `project is VideoKitEditMediaPreview` and otherwise draws plain blocks. Same as the Dart
 * `VideoKitEditMediaPreview`; the native implementation comes with the M4/M6 native batches.
 *
 * Implementations follow 04A P5: every frame read has the hard thumbnail timeout and is cancellable (the editor drops
 * late answers by cancelling). For [SourceLatency.SLOW] sources they serve only a low density of thumbnails: requests
 * closer than [SLOW_SOURCE_THUMBNAIL_SPACING_US] to an already served time may return `null`.
 */
public interface VideoKitEditMediaPreview {
    /**
     * An encoded picture (PNG or JPEG) of source [sourceId] at source time [atUs], at most [maxWidth] × [maxHeight] px;
     * `null` when the frame cannot be read in time (the block keeps its plain look there).
     */
    public suspend fun sourceThumbnail(
        sourceId: String,
        atUs: Long,
        maxWidth: Int = DEFAULT_THUMBNAIL_WIDTH,
        maxHeight: Int = DEFAULT_THUMBNAIL_HEIGHT,
    ): ByteArray?

    /**
     * [buckets] audio peaks (0–1) of source [sourceId] over source time [inUs]–[outUs]; all zero for silence, empty
     * when the source has no audio track.
     */
    public suspend fun sourceWaveform(sourceId: String, inUs: Long, outUs: Long, buckets: Int): List<Float>

    public companion object {
        /** Default thumbnail width (same as Dart). */
        public const val DEFAULT_THUMBNAIL_WIDTH: Int = 160

        /** Default thumbnail height (same as Dart). */
        public const val DEFAULT_THUMBNAIL_HEIGHT: Int = 90

        /** Thumbnail spacing of local sources on the timeline (04A X2, frozen 2026-11-08). */
        public const val LOCAL_SOURCE_THUMBNAIL_SPACING_US: Long = 500_000L

        /** Low thumbnail density of slow sources: at most one per this source time (04A X2, frozen 2026-11-08). */
        public const val SLOW_SOURCE_THUMBNAIL_SPACING_US: Long = 2_000_000L
    }
}
