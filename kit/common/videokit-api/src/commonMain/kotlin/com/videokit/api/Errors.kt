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
    ;

    public companion object {
        /** Maps a stage name to an [ErrorStage]; returns `null` for unknown names. */
        public fun fromWireName(name: String?): ErrorStage? = entries.firstOrNull { it.name == name }
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
) : Exception(message ?: code.name, cause)
