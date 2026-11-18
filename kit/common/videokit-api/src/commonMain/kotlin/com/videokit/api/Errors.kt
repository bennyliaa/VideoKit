package com.videokit.api

/**
 * Stable error code (04 §9.1, original requirement §19.3).
 *
 * New codes are a minor version change. Hosts and adapters must treat any code they do not know as
 * [INTERNAL_ERROR_REDACTED]; use [fromWireName] when reading a code from a wire format or storage.
 */
public enum class ErrorCode {
    /** The source no longer exists. */
    SOURCE_NOT_FOUND,

    /** The host denied access to the source. */
    SOURCE_PERMISSION_DENIED,

    /** The source connection was lost (for example an SMB disconnect). */
    SOURCE_DISCONNECTED,

    /** Reading the source did not finish within the read timeout. */
    SOURCE_TIMEOUT,

    /** The container format is not supported. */
    UNSUPPORTED_CONTAINER,

    /** The video codec is not supported on this device. */
    UNSUPPORTED_VIDEO_CODEC,

    /** The audio codec is not supported on this device. */
    UNSUPPORTED_AUDIO_CODEC,

    /** No decoder could be created. */
    DECODER_UNAVAILABLE,

    /** Decoder resources (instances, memory) are exhausted. */
    DECODER_RESOURCE_EXHAUSTED,

    /** The media is damaged or truncated. */
    CORRUPT_MEDIA,

    /** The source or format does not allow seeking. */
    SEEK_UNSUPPORTED,

    /** The output sink denied writing. */
    OUTPUT_PERMISSION_DENIED,

    /** The output location does not have enough free space. */
    OUTPUT_SPACE_INSUFFICIENT,

    /** The output sink lacks a capability the export needs (random write, file descriptor, ...). */
    OUTPUT_CAPABILITY_UNSUPPORTED,

    /** No suitable encoder is available. */
    ENCODER_UNAVAILABLE,

    /** The export failed for another reason. */
    EXPORT_FAILED,

    /** The tracking model is not installed or cannot be loaded. */
    TRACKING_MODEL_UNAVAILABLE,

    /** The tracked target was lost. */
    TRACKING_LOST,

    /** The operation was cancelled. */
    CANCELLED,

    /** A host callback threw, timed out or returned an invalid result. */
    HOST_CALLBACK_FAILED,

    /** The session or project has been released. */
    SESSION_RELEASED,

    /** An internal error; details are redacted. Also used for every unknown code. */
    INTERNAL_ERROR_REDACTED,

    /** A command is not allowed in the current state (illegal state transition, 04A V7). */
    INVALID_STATE,

    /** An argument is out of range or malformed (04A V7). */
    INVALID_ARGUMENT,

    /** A snapshot or project schema version is not supported, for example a future major version (04A V7). */
    UNSUPPORTED_SNAPSHOT_VERSION,

    /** No usable face in an avatar image (REQ-ED-07, 04A E6): the user picks another photo. */
    AVATAR_NO_FACE,

    /** An avatar image cannot be decoded or exceeds the size limit, including a host-supplied PNG (04A E6). */
    AVATAR_IMAGE_UNSUPPORTED,

    /** The feature is hidden by the host configuration (REQ-API-10 ①, [FeatureMode.HIDDEN]); params `feature`. */
    FEATURE_DISABLED,

    /** The host's feature gate did not allow the feature (REQ-API-10 ②); params `feature`, `badge`. */
    FEATURE_DENIED,
    ;

    public companion object {
        /** Maps a code name to an [ErrorCode]; unknown or future names map to [INTERNAL_ERROR_REDACTED]. */
        public fun fromWireName(name: String?): ErrorCode = entries.firstOrNull { it.name == name } ?: INTERNAL_ERROR_REDACTED
    }
}

/** Stage in which an error happened (04 §9.1). */
public enum class ErrorStage {
    /** Probing the media. */
    PROBE,

    /** Binding a source to a session. */
    BIND,

    /** Playback control. */
    PLAYBACK,

    /** Decoding. */
    DECODE,

    /** Editing a project. */
    EDIT,

    /** Automatic tracking. */
    TRACKING,

    /** Exporting. */
    EXPORT,

    /** Writing to the output sink. */
    SINK,

    /** Calling a host callback. */
    CALLBACK,

    /** Unknown stage (fallback for unknown wire values). */
    UNKNOWN,
    ;

    public companion object {
        /** Maps a stage name to an [ErrorStage]; unknown names map to [UNKNOWN] (04A V6). */
        public fun fromWireName(name: String?): ErrorStage = entries.firstOrNull { it.name == name } ?: UNKNOWN
    }
}

/** Action the UI or host may suggest to the user (04 §9.1). */
public enum class SuggestedAction {
    /** Nothing useful can be suggested. */
    NONE,

    /** Retry the same operation. */
    RETRY,

    /** Choose another audio or subtitle track. */
    CHOOSE_OTHER_TRACK,

    /** Lower the quality or resolution. */
    REDUCE_QUALITY,

    /** Free storage space. */
    FREE_SPACE,

    /** Check the access permission of the source or output. */
    CHECK_PERMISSION,

    /** Reconnect to the source (network share). */
    RECONNECT_SOURCE,

    /** Close or pause other sessions to free resources. */
    CLOSE_OTHER_SESSIONS,

    /** Correct the tracked region (09). */
    CORRECT_TRACKING,

    /** Choose another media source. */
    CHOOSE_OTHER_SOURCE,
    ;

    public companion object {
        /** Maps a name to a [SuggestedAction]; unknown names map to [NONE]. */
        public fun fromWireName(name: String?): SuggestedAction = entries.firstOrNull { it.name == name } ?: NONE
    }
}

/**
 * A stable, host-facing error (04 §9.1). Third-party exceptions and stack traces never cross the
 * public API; they are converted to this type at the boundary (13 §3).
 */
public data class VideoKitStableError(
    /** Stable code. */
    val code: ErrorCode,
    /** Stage in which the error happened. */
    val stage: ErrorStage,
    /** Whether retrying the same operation may succeed. */
    val retryable: Boolean,
    /** Suggested user action. */
    val suggestedAction: SuggestedAction = SuggestedAction.NONE,
    /**
     * Redacted diagnostic summary for logs and debugging: English, machine-oriented, never shown to users
     * and never containing paths, credentials or media names (13 §3.1, §4).
     */
    val diagnostic: String? = null,
    /**
     * Message parameters for the UI (13 §3.1): the Kit outputs no user-visible text; `videokit_ui` resolves
     * [code] with these parameters in the current Locale. Keys are lowerCamelCase English identifiers; values
     * are machine formatted with `Locale.ROOT` (for example `"limit" to "12"`).
     */
    val params: Map<String, String> = emptyMap(),
)

/**
 * Thrown by suspending API calls that cannot return a result value, for example
 * [VideoKit.restoreEditProject] with an unsupported schema or [VideoKitEditProject.export] after a failure.
 */
public class VideoKitException(
    /** The stable error. */
    public val error: VideoKitStableError,
) : Exception("VideoKit error ${error.code} at ${error.stage}")

/** Error codes a host [VideoKitSourceFactory] or [VideoKitReadHandle] may report (04 §5). */
public enum class SourceErrorCode(
    /** The stable error code VideoKit maps this source error to. */
    public val errorCode: ErrorCode,
) {
    /** The source does not exist any more. */
    NOT_FOUND(ErrorCode.SOURCE_NOT_FOUND),

    /** Access to the source was denied. */
    PERMISSION_DENIED(ErrorCode.SOURCE_PERMISSION_DENIED),

    /** The connection to the source was lost. */
    DISCONNECTED(ErrorCode.SOURCE_DISCONNECTED),

    /** The source did not answer in time. */
    TIMEOUT(ErrorCode.SOURCE_TIMEOUT),
}

/**
 * Thrown by host source implementations to report a classified failure (04 §5). VideoKit maps it to
 * the matching [ErrorCode]; any other exception from a source is mapped to [ErrorCode.INTERNAL_ERROR_REDACTED].
 */
public class VideoKitSourceException(
    /** Classified source error. */
    public val code: SourceErrorCode,
    message: String? = null,
    cause: Throwable? = null,
) : Exception(message ?: code.name, cause)

/** Error codes a host [VideoKitOutputSink] may report. */
public enum class SinkErrorCode(
    /** The stable error code VideoKit maps this sink error to. */
    public val errorCode: ErrorCode,
) {
    /** Writing was denied. */
    PERMISSION_DENIED(ErrorCode.OUTPUT_PERMISSION_DENIED),

    /** Not enough free space. */
    SPACE_INSUFFICIENT(ErrorCode.OUTPUT_SPACE_INSUFFICIENT),

    /** The requested write mode is not supported. */
    CAPABILITY_UNSUPPORTED(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED),

    /** Another I/O failure. */
    IO_FAILED(ErrorCode.EXPORT_FAILED),
}

/**
 * Thrown by host [VideoKitOutputSink] / [VideoKitWriteHandle] implementations to report a classified
 * failure. Any other exception from a sink is mapped to [ErrorCode.EXPORT_FAILED].
 */
public class VideoKitSinkException(
    /** Classified sink error. */
    public val code: SinkErrorCode,
    message: String? = null,
    cause: Throwable? = null,
    /**
     * For [SinkErrorCode.SPACE_INSUFFICIENT]: the additional bytes the sink would need, when known. Reported as the
     * [ErrorParams.REQUIRED_BYTES] parameter (UI-AUDIT-A1 J8).
     */
    public val requiredBytes: Long? = null,
) : Exception(message ?: code.name, cause)

/** Registered message parameter keys of [VideoKitStableError.params] (`spec/errors.json` "params"). */
public object ErrorParams {
    /**
     * [ErrorCode.OUTPUT_SPACE_INSUFFICIENT]: additional bytes that must be freed, a decimal integer > 0; absent when
     * not known (UI-AUDIT-A1 J8).
     */
    public const val REQUIRED_BYTES: String = "requiredBytes"

    /** [ErrorCode.EXPORT_FAILED]: why the export worker failed, one of [ExportFailureReasons]; absent otherwise (04A X1). */
    public const val REASON: String = "reason"

    /** `UNSUPPORTED_*` media codes: codec MIME type, for example `video/hevc` (04A X2). */
    public const val CODEC: String = "codec"

    /** `UNSUPPORTED_*` media codes: codec profile as the media declares it (04A X2). */
    public const val PROFILE: String = "profile"

    /** `UNSUPPORTED_*` media codes: luma bit depth, a decimal integer (04A X2). */
    public const val BIT_DEPTH: String = "bitDepth"

    /** `UNSUPPORTED_*` media codes: container MIME type (04A X2). */
    public const val CONTAINER: String = "container"

    /** `UNSUPPORTED_*` media codes: one of [UnsupportedDetails] (04A X2). */
    public const val REASON_DETAIL: String = "reasonDetail"

    /** [ErrorCode.FEATURE_DISABLED], [ErrorCode.FEATURE_DENIED]: the [VideoKitFeature] wire name (REQ-API-10). */
    public const val FEATURE: String = "feature"

    /** [ErrorCode.FEATURE_DENIED]: the [FeatureBadge] wire name the host gave; absent without a marker (REQ-API-10). */
    public const val BADGE: String = "badge"
}

/** Values of [ErrorParams.REASON_DETAIL] on the `UNSUPPORTED_*` media codes (04A X2, `spec/errors.json`). */
public object UnsupportedDetails {
    /** No decoder for this format. */
    public const val FORMAT_UNSUPPORTED: String = "FORMAT_UNSUPPORTED"

    /** A decoder exists, but not for this profile, level, size or bit depth. */
    public const val EXCEEDS_CAPABILITIES: String = "EXCEEDS_CAPABILITIES"

    /** The container cannot be read. */
    public const val CONTAINER_UNSUPPORTED: String = "CONTAINER_UNSUPPORTED"

    /** All values in registry order. */
    public val ALL: List<String> = listOf(FORMAT_UNSUPPORTED, EXCEEDS_CAPABILITIES, CONTAINER_UNSUPPORTED)
}

/** Values of [ErrorParams.REASON] on [ErrorCode.EXPORT_FAILED] (04A X1, `spec/errors.json`). */
public object ExportFailureReasons {
    /** The system or the main process killed the worker (for example low memory). */
    public const val WORKER_KILLED: String = "WORKER_KILLED"

    /** The worker crashed: native signal, uncaught exception, out of memory. */
    public const val WORKER_CRASHED: String = "WORKER_CRASHED"

    /** No progress within the watchdog time. */
    public const val WORKER_TIMEOUT: String = "WORKER_TIMEOUT"

    /** All values in registry order. */
    public val ALL: List<String> = listOf(WORKER_KILLED, WORKER_CRASHED, WORKER_TIMEOUT)
}
