package com.videokit.core.spi

import com.videokit.api.Clip
import com.videokit.api.ExportPreset
import com.videokit.api.ExportStage
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskTrack
import com.videokit.api.MediaProbeResult
import com.videokit.api.SinkWriteMode
import com.videokit.api.Size
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.VideoKitWriteHandle
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/** Pixel layout of a [FrameData]. */
public enum class PixelFormat {
    /** 8-bit RGBA, row-major, no padding. */
    RGBA_8888,

    /** 8-bit luminance only (analysis frames). */
    GRAY_8,
}

/** A decoded frame in CPU memory (thumbnails, tracking analysis, CPU effect reference). */
public class FrameData(
    /** Width in pixels. */
    public val width: Int,
    /** Height in pixels. */
    public val height: Int,
    /** Presentation time. */
    public val timeUs: Long,
    /** Pixel layout. */
    public val format: PixelFormat,
    /** Pixels in [format]. */
    public val pixels: ByteArray,
)

/**
 * Frame extraction (02 §4.2 `FrameSource`).
 *
 * Cancellation contract (04A P5): [open], [FrameReader.frameAt] and [FrameReader.thumbnailAt] must return promptly
 * when their coroutine is cancelled, even while a platform extractor is blocked in a host read. Implementations run
 * the blocking work on their own worker thread with their own read handle, close that handle on cancellation so the
 * blocked read fails, and discard the late result. [FrameReader.close] must not block on work still in progress.
 */
public interface FrameSource {
    /** Opens [source] for frame extraction. */
    public suspend fun open(source: VideoKitMediaSource): FrameReader
}

/** An opened frame reader. */
public interface FrameReader : AutoCloseable {
    /** The frame nearest to [timeUs], scaled to fit [maxSize]. */
    public suspend fun frameAt(timeUs: Long, maxSize: Size, format: PixelFormat): FrameData

    /**
     * A JPEG thumbnail of the frame nearest to [timeUs], fitting [maxSize] (04A P1); the platform encodes it.
     * Throws [SpiException] with a stable error when the frame cannot be extracted.
     */
    public suspend fun thumbnailAt(timeUs: Long, maxSize: Size): com.videokit.api.ThumbnailResult.Captured
}

/** One input of an export plan. */
public data class PlanInput(
    /** Source id in the project. */
    val sourceId: String,
    /** Source descriptor. */
    val source: VideoKitMediaSource,
)

/**
 * Immutable export plan computed by `videokit-export` from the edit project (08 §1: preview and export share
 * the plan). The exporter executes it; it does not make editing decisions.
 */
public data class ExportPlan(
    /** Export id. */
    val exportId: String,
    /** Inputs. */
    val inputs: List<PlanInput>,
    /** Ordered clips. */
    val clips: List<Clip>,
    /** Enabled masks with resolved keyframes. */
    val masks: List<MaskTrack>,
    /** Preset. */
    val preset: ExportPreset,
    /** Output size. */
    val outputSize: Size,
    /** Whether the plan qualifies for fast concatenation without re-encoding. */
    val fastConcat: Boolean,
    /** How to write to the sink. */
    val writeMode: SinkWriteMode,
)

/** Progress of a [CompositionExporter]; fractions only when reliable (08 §6). */
public data class ExporterProgress(
    /** Stage. */
    val stage: ExportStage,
    /** Fraction 0..1, if reliable. */
    val fraction: Float?,
    /** Processed output duration. */
    val processedUs: Long,
    /** Bytes written. */
    val outputBytes: Long,
)

/** Export pipeline (02 §4.2 `CompositionExporter`). Cancellation = cancelling the coroutine. */
public interface CompositionExporter {
    /**
     * Executes [plan], writing to [output], reporting [progress]. Returns the metadata of the written media;
     * throws [SpiException] on failure. Never marks the output ready; the export runtime does that.
     */
    public suspend fun export(plan: ExportPlan, output: VideoKitWriteHandle, progress: (ExporterProgress) -> Unit): VideoKitOutputMetadata
}

/** One region of an effect pass. */
public data class EffectRegion(
    /** Region, normalized to the frame. */
    val region: MaskRegion,
    /** Effect. */
    val style: MaskStyle,
    /** Strength 0..1. */
    val strength: Float,
)

/**
 * Mosaic/blur rendering (02 §4.2 `EffectRenderer`). GPU implementations must match the CPU reference
 * implementation of `videokit-effects` within the tolerance of the golden-image tests.
 */
public interface EffectRenderer {
    /** Styles the renderer supports. */
    public val supportedStyles: Set<MaskStyle>

    /** Applies [regions] to [frame] (reference/test path; the real-time path is wired inside the exporter). */
    public suspend fun render(frame: FrameData, regions: List<EffectRegion>): FrameData
}

/** A detection or tracking result. */
public data class TrackedRegion(
    /** Region, normalized. */
    val region: MaskRegion,
    /** Confidence 0..1. */
    val confidence: Float,
)

/** Tracking inference (02 §4.2 `TrackerBackend`). Orchestration lives in `videokit-tracking`. */
public interface TrackerBackend {
    /** Detects faces in [frame]. */
    public suspend fun detectFaces(frame: FrameData): List<TrackedRegion>

    /** Starts tracking the object at [initial] in [frame]. */
    public suspend fun startObject(frame: FrameData, initial: MaskRegion): ObjectTracker
}

/** A single object track. */
public interface ObjectTracker : AutoCloseable {
    /** Tracks into [frame]; `null` when the target is lost. */
    public suspend fun track(frame: FrameData): TrackedRegion?
}

/** Capability probing (02 §4.2 `CapabilityProbe`). */
public interface CapabilityProbe {
    /** Device capabilities (decoders, encoders, limits, thermal state). */
    public suspend fun device(): VideoKitCapabilities

    /** Probe of one media source (playable / editable / fast-concat eligibility). */
    public suspend fun media(source: VideoKitMediaSource): MediaProbeResult
}

/** Kind of an isolated task. */
public enum class IsolatedTaskKind {
    /** Export encoding. */
    EXPORT,

    /** Tracking inference. */
    TRACKING,

    /** Probing of unknown formats. */
    PROBE,
}

/** Lifecycle event of an isolated task. */
public sealed interface IsolationEvent {
    /** The isolated environment started. */
    public data object Started : IsolationEvent

    /** The environment terminated abnormally (crash, OOM, killed); the host process is unaffected. */
    public data class Crashed(
        /** English, redacted reason for diagnostics. */
        val reason: String,
    ) : IsolationEvent

    /** The task finished. */
    public data object Finished : IsolationEvent
}

/**
 * Runs high-risk work in an isolated environment (02 §4.2 `IsolationHost`; Android: `isolatedProcess`
 * service). Platforms without process isolation run in-process and report it in the capabilities.
 */
public interface IsolationHost {
    /** Whether tasks really run outside the host process. */
    public val isolated: Boolean

    /** Starts an isolated environment for [kind]. */
    public suspend fun start(kind: IsolatedTaskKind): IsolatedTask
}

/** A running isolated environment. Closing stops it. */
public interface IsolatedTask : AutoCloseable {
    /** Lifecycle events. */
    public val events: Flow<IsolationEvent>

    /** Whether the environment is alive. */
    public val alive: StateFlow<Boolean>

    /** Generation of the worker (07 §5.2): replies of other generations are refused. */
    public val generation: Int

    /**
     * Runs [operation] in the worker with [payload] and returns its reply. Reads of [source] are served from this
     * process through the bounded read channel of the protocol (the worker has no file access, 07 §5.2). Throws
     * [SpiException]: the worker's stable error, or INTERNAL_ERROR_REDACTED when the worker died, stopped answering
     * or sent an invalid message; the task is then failed for good (no replay).
     */
    public suspend fun call(operation: String, payload: ByteArray = ByteArray(0), source: VideoKitMediaSource? = null): ByteArray

    /** Injects [fault] into the worker (fault injection of 07 §5.2; diagnostics and device verification only). */
    public suspend fun injectFault(fault: IsolationFault)
}

/** Faults that can be injected into an isolated worker (07 §5.2: crash, out of memory, hang, bad message). */
public enum class IsolationFault {
    /** The worker process crashes. */
    CRASH,

    /** The worker runs out of memory. */
    OUT_OF_MEMORY,

    /** The worker stops answering. */
    HANG,

    /** The worker sends a malformed reply (wrong version, stale generation, oversize). */
    BAD_MESSAGE,
}
