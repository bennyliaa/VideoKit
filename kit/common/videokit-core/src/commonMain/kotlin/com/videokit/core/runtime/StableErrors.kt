package com.videokit.core.runtime

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.SuggestedAction
import com.videokit.api.VideoKitSinkException
import com.videokit.api.VideoKitSourceException
import com.videokit.api.VideoKitStableError
import kotlinx.coroutines.TimeoutCancellationException

/**
 * Construction of stable errors (04 §9, `spec/errors.json`) with the registered retry flags and suggestions.
 * Diagnostics are English and redacted: never a message, path or credential, only codes and type names.
 */
public object StableErrors {
    /** An error with the default retry flag and suggestion of [code]. */
    public fun of(code: ErrorCode, stage: ErrorStage, diagnostic: String? = null): VideoKitStableError =
        VideoKitStableError(code, stage, retryable(code), suggestion(code), diagnostic)

    /** Illegal state transition (04A V7). */
    public fun illegalState(stage: ErrorStage, what: String): VideoKitStableError =
        VideoKitStableError(ErrorCode.INVALID_STATE, stage, false, SuggestedAction.NONE, "ILLEGAL_STATE:$what")

    /** Invalid or out-of-range argument (04A V7). */
    public fun invalidArgument(stage: ErrorStage, what: String): VideoKitStableError =
        VideoKitStableError(ErrorCode.INVALID_ARGUMENT, stage, false, SuggestedAction.NONE, "INVALID_ARGUMENT:$what")

    /** A host callback failed or timed out (04 §8). */
    public fun callbackFailed(
        callback: String,
        cause: Throwable?,
        timedOut: Boolean = cause is TimeoutCancellationException,
    ): VideoKitStableError = VideoKitStableError(
        ErrorCode.HOST_CALLBACK_FAILED,
        ErrorStage.CALLBACK,
        retryable = true,
        suggestedAction = SuggestedAction.RETRY,
        diagnostic = "$callback:${if (timedOut) "TIMEOUT" else cause?.typeName() ?: "INVALID"}",
    )

    /** Maps any failure of a host source; only classified exceptions keep their meaning. */
    public fun fromSourceFailure(failure: Throwable, stage: ErrorStage): VideoKitStableError = when (failure) {
        is VideoKitSourceException -> of(failure.code.errorCode, stage, "SOURCE:${failure.code.name}")

        is TimeoutCancellationException -> of(ErrorCode.SOURCE_TIMEOUT, stage, "SOURCE:TIMEOUT")

        // Never copy the message: it may contain a path or a credential.
        else -> of(ErrorCode.INTERNAL_ERROR_REDACTED, stage, "SOURCE:${failure.typeName()}")
    }

    /** Maps any failure of a host sink; a space shortfall the sink reported becomes `requiredBytes` (J8). */
    public fun fromSinkFailure(failure: Throwable): VideoKitStableError = when (failure) {
        is VideoKitSinkException -> withRequiredBytes(
            of(failure.code.errorCode, ErrorStage.SINK, "SINK:${failure.code.name}"),
            failure.requiredBytes,
        )

        else -> of(ErrorCode.EXPORT_FAILED, ErrorStage.SINK, "SINK:${failure.typeName()}")
    }

    /** [ErrorCode.OUTPUT_SPACE_INSUFFICIENT] with the shortfall when known (UI-AUDIT-A1 J8, `spec/errors.json`). */
    public fun spaceInsufficient(stage: ErrorStage, requiredBytes: Long?, diagnostic: String? = null): VideoKitStableError =
        withRequiredBytes(of(ErrorCode.OUTPUT_SPACE_INSUFFICIENT, stage, diagnostic), requiredBytes)

    private fun withRequiredBytes(error: VideoKitStableError, requiredBytes: Long?): VideoKitStableError =
        if (error.code == ErrorCode.OUTPUT_SPACE_INSUFFICIENT && requiredBytes != null && requiredBytes > 0) {
            error.copy(params = error.params + (ErrorParams.REQUIRED_BYTES to requiredBytes.toString()))
        } else {
            error
        }

    /** Whether [code] is retryable by default (`spec/errors.json`). */
    public fun retryable(code: ErrorCode): Boolean = when (code) {
        ErrorCode.SOURCE_DISCONNECTED,
        ErrorCode.SOURCE_TIMEOUT,
        ErrorCode.DECODER_RESOURCE_EXHAUSTED,
        ErrorCode.OUTPUT_SPACE_INSUFFICIENT,
        ErrorCode.EXPORT_FAILED,
        ErrorCode.HOST_CALLBACK_FAILED,
        ErrorCode.TRACKING_LOST,
        ErrorCode.CANCELLED,
        ErrorCode.FEATURE_DENIED,
        -> true

        else -> false
    }

    /** Default suggestion of [code] (`spec/errors.json`). */
    public fun suggestion(code: ErrorCode): SuggestedAction = when (code) {
        ErrorCode.SOURCE_DISCONNECTED, ErrorCode.SOURCE_TIMEOUT -> SuggestedAction.RECONNECT_SOURCE
        ErrorCode.SOURCE_PERMISSION_DENIED, ErrorCode.OUTPUT_PERMISSION_DENIED -> SuggestedAction.CHECK_PERMISSION
        ErrorCode.UNSUPPORTED_AUDIO_CODEC -> SuggestedAction.CHOOSE_OTHER_TRACK
        ErrorCode.DECODER_RESOURCE_EXHAUSTED -> SuggestedAction.CLOSE_OTHER_SESSIONS
        ErrorCode.OUTPUT_SPACE_INSUFFICIENT -> SuggestedAction.FREE_SPACE
        ErrorCode.ENCODER_UNAVAILABLE -> SuggestedAction.REDUCE_QUALITY
        ErrorCode.EXPORT_FAILED, ErrorCode.HOST_CALLBACK_FAILED, ErrorCode.CANCELLED -> SuggestedAction.RETRY
        else -> SuggestedAction.NONE
    }
}
