package com.videokit.api

import kotlin.random.Random

/** First-release export presets (08 §8): MP4 / H.264 / AAC / SDR. */
public enum class ExportPreset {
    /** Resolution of the first source (within encoder limits). Default. */
    ORIGINAL,

    /** Long edge 1920. */
    P1080,

    /** Long edge 1280; recommended for low-end devices. */
    P720,
}

/** Export request. */
public data class VideoKitExportRequest(
    /** Preset. */
    val preset: ExportPreset = ExportPreset.ORIGINAL,
    /** Caller chosen export id, used by [VideoKitEditProject.cancelExport]. */
    val exportId: String = newExportId(),
    /** Optional file name hint passed to the sink; never a path. */
    val fileNameHint: String? = null,
)

/** A random opaque export id (`export-` + 16 hex digits). */
private fun newExportId(): String = "export-" + Random.nextLong().toULong().toString(16).padStart(16, '0')

/** How the export writes to the sink (08 §5). */
public enum class SinkWriteMode {
    /** Through a file descriptor. */
    FILE_DESCRIPTOR,

    /** Random access writes. */
    RANDOM_WRITE,

    /** Sequential writes only (fragmented output or private staging copy). */
    SEQUENTIAL,
}

/** Result of [VideoKitEditProject.checkExport]. */
public data class ExportPrecheck(
    /** Whether the export can start. */
    val ok: Boolean,
    /** Write mode that will be used, when [ok]. */
    val writeMode: SinkWriteMode? = null,
    /** Output estimates. */
    val estimate: EditEstimate = EditEstimate(),
    /** Blocking problems. */
    val problems: List<VideoKitStableError> = emptyList(),
    /** Non-blocking warnings, for example incomplete tracking coverage. */
    val warnings: List<String> = emptyList(),
    /**
     * Tracked-mask ranges without usable tracking (not TRACKED and not accepted by the user), each with its
     * [CoverageRange.maskId], for the coverage check page (UI-07/08, 04A T2).
     */
    val uncoveredRanges: List<CoverageRange> = emptyList(),
)

/** Output token returned by the host sink; VideoKit cannot derive a directory or path from it. */
public data class VideoKitOutputToken(
    /** Opaque value. */
    val value: String,
)

/**
 * Metadata of a written output, passed to [VideoKitOutputSink.markReady] (08 §5, §7). It describes the bytes
 * VideoKit wrote and verified; the host returns the [VideoKitOutputToken] for it.
 */
public data class VideoKitOutputMetadata(
    /** Container, for example `mp4`. */
    val container: String,
    /** File extension without dot. */
    val extension: String,
    /** Video codec MIME type. */
    val videoCodec: String?,
    /** Audio codec MIME type. */
    val audioCodec: String?,
    /** Width. */
    val width: Int,
    /** Height. */
    val height: Int,
    /** Rotation in degrees. */
    val rotationDeg: Int,
    /** Duration. */
    val durationUs: Long,
    /** Size in bytes. */
    val sizeBytes: Long,
    /** Frame rate, if constant. */
    val frameRate: Float?,
    /** Whether audio is present. */
    val audioPresent: Boolean,
    /** Whether the output is demo data, not real media (04A I6). */
    val isDemo: Boolean = false,
)

/** Exported media (08 §7, original requirement §11.2), carried by [VideoKitExportResult.Succeeded]. */
public data class VideoKitExportedMedia(
    /** Token from the sink. */
    val outputToken: VideoKitOutputToken,
    /** Container. */
    val container: String,
    /** Extension without dot. */
    val extension: String,
    /** Video codec MIME type. */
    val videoCodec: String?,
    /** Audio codec MIME type. */
    val audioCodec: String?,
    /** Width. */
    val width: Int,
    /** Height. */
    val height: Int,
    /** Rotation in degrees. */
    val rotationDeg: Int,
    /** Duration. */
    val durationUs: Long,
    /** Size in bytes. */
    val sizeBytes: Long,
    /** Frame rate, if constant. */
    val frameRate: Float?,
    /** Whether audio is present. */
    val audioPresent: Boolean,
    /** Creation time in epoch milliseconds. */
    val createdAtEpochMs: Long,
    /** Media tokens of the inputs. */
    val sourceTokens: List<String>,
    /** Project id. */
    val editProjectId: String,
    /** Preset. */
    val exportPreset: ExportPreset,
    /** Warnings, for example `BOUNDARY_ALIGNED_TO_KEYFRAME`, `SILENCE_INSERTED`, `DEMO_OUTPUT_NOT_REAL_MEDIA`. */
    val warnings: List<String> = emptyList(),
    /** Whether the output is demo data, not real media (04A I6). */
    val isDemo: Boolean = false,
)

/**
 * Result of [VideoKitEditProject.export] (04A I5). Normal failures and cancellation are results, not exceptions.
 */
public sealed interface VideoKitExportResult {
    /** Export id. */
    public val exportId: String

    /** The output was written, verified and marked ready. */
    public data class Succeeded(
        override val exportId: String,
        /** The exported media. */
        val media: VideoKitExportedMedia,
    ) : VideoKitExportResult

    /** The export failed; the sink was aborted. */
    public data class Failed(
        override val exportId: String,
        /** Error. */
        val error: VideoKitStableError,
        /** Stage in which it failed, if known. */
        val stage: ExportStage? = null,
    ) : VideoKitExportResult

    /** The export was cancelled; the sink was aborted. */
    public data class Cancelled(
        override val exportId: String,
        /** Whether the partial output was removed (aborted at the sink). */
        val partialOutputRemoved: Boolean = true,
    ) : VideoKitExportResult
}

/** Write capabilities of a sink (08 §5, original requirement §17.2). */
public data class SinkCapabilities(
    /** Sequential writes. */
    val sequentialWrite: Boolean = true,
    /** Random access writes ([VideoKitWriteHandle.writeAt]). */
    val randomWrite: Boolean = false,
    /**
     * File descriptor mode: the handles returned by the sink additionally implement the platform's
     * descriptor handle type (Android: `com.videokit.api.android.FileDescriptorWriteHandle`).
     */
    val fileDescriptor: Boolean = false,
    /** Whether [VideoKitWriteHandle.flush] is meaningful. */
    val flush: Boolean = true,
    /** Known free space in bytes; `null` when unknown. */
    val knownFreeSpaceBytes: Long? = null,
)

/** Request to open a temporary output. */
public data class OutputOpenRequest(
    /** Export id. */
    val exportId: String,
    /** MIME type, for example `video/mp4`. */
    val mimeType: String,
    /** Extension without dot. */
    val extension: String,
    /** Write mode the export will use. */
    val writeMode: SinkWriteMode,
    /** Estimated size, if known. */
    val estimatedBytes: Long? = null,
    /** File name hint; never a path. */
    val fileNameHint: String? = null,
)

/** Why an output is aborted. */
public enum class VideoKitAbortReason {
    /** The export was cancelled. */
    CANCELLED,

    /** The export failed. */
    EXPORT_FAILED,

    /** Output verification failed. */
    VERIFICATION_FAILED,

    /** The project was released during export. */
    RELEASED,
}

/** A temporary output handle (08 §5). Closing is idempotent. */
public interface VideoKitWriteHandle : AutoCloseable {
    /** Opaque handle id. */
    public val handleId: String

    /** Appends bytes. May throw [VideoKitSinkException]. */
    public suspend fun write(data: ByteArray, offset: Int, length: Int)

    /** Writes at [position]; only when [SinkCapabilities.randomWrite]. May throw [VideoKitSinkException]. */
    public suspend fun writeAt(position: Long, data: ByteArray, offset: Int, length: Int)

    /** Flushes written data. */
    public suspend fun flush()
}

/**
 * Host output sink (08 §5, original requirement §17.2). `markReady` only means VideoKit finished
 * writing and self-checks passed, not that the host committed the file.
 */
public interface VideoKitOutputSink {
    /** Write capabilities. */
    public val capabilities: SinkCapabilities

    /** Opens a temporary output. May throw [VideoKitSinkException]. */
    public suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle

    /** Marks the output of [handleId] ready and returns the host token. */
    public suspend fun markReady(handleId: String, metadata: VideoKitOutputMetadata): VideoKitOutputToken

    /** Aborts the output of [handleId]; the host deletes the temporary data. */
    public suspend fun abort(handleId: String, reason: VideoKitAbortReason)
}
