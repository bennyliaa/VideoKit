package com.videokit.testkit.internal

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.SuggestedAction
import com.videokit.api.VideoKitSinkException
import com.videokit.api.VideoKitSourceException
import com.videokit.api.VideoKitStableError
import kotlinx.coroutines.TimeoutCancellationException

/** Construction of stable errors with default retry flags and suggestions; diagnostics are redacted. */
internal object Errors {
    fun of(code: ErrorCode, stage: ErrorStage, diagnostic: String? = null): VideoKitStableError =
        VideoKitStableError(code, stage, retryable(code), suggestion(code), diagnostic)

    /** Illegal state transition. The contract has no dedicated code yet; see the M0-B1-B report. */
    fun illegalState(stage: ErrorStage, what: String): VideoKitStableError =
        VideoKitStableError(ErrorCode.INTERNAL_ERROR_REDACTED, stage, false, SuggestedAction.NONE, "ILLEGAL_STATE:$what")

    fun invalidArgument(stage: ErrorStage, what: String): VideoKitStableError =
        VideoKitStableError(ErrorCode.INTERNAL_ERROR_REDACTED, stage, false, SuggestedAction.NONE, "INVALID_ARGUMENT:$what")

    fun callbackFailed(
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
    fun fromSourceFailure(failure: Throwable, stage: ErrorStage): VideoKitStableError = when (failure) {
        is VideoKitSourceException -> of(failure.code.errorCode, stage, "SOURCE:${failure.code.name}")

        is TimeoutCancellationException -> of(ErrorCode.SOURCE_TIMEOUT, stage, "SOURCE:TIMEOUT")

        // Never copy the message: it may contain a path or a credential.
        else -> of(ErrorCode.INTERNAL_ERROR_REDACTED, stage, "SOURCE:${failure.typeName()}")
    }

    /** Maps any failure of a host sink. */
    fun fromSinkFailure(failure: Throwable): VideoKitStableError = when (failure) {
        is VideoKitSinkException -> of(failure.code.errorCode, ErrorStage.SINK, "SINK:${failure.code.name}")
        else -> of(ErrorCode.EXPORT_FAILED, ErrorStage.SINK, "SINK:${failure.typeName()}")
    }

    private fun retryable(code: ErrorCode): Boolean = when (code) {
        ErrorCode.SOURCE_DISCONNECTED,
        ErrorCode.SOURCE_TIMEOUT,
        ErrorCode.DECODER_RESOURCE_EXHAUSTED,
        ErrorCode.OUTPUT_SPACE_INSUFFICIENT,
        ErrorCode.EXPORT_FAILED,
        ErrorCode.HOST_CALLBACK_FAILED,
        ErrorCode.TRACKING_LOST,
        ErrorCode.CANCELLED,
        -> true

        else -> false
    }

    private fun suggestion(code: ErrorCode): SuggestedAction = when (code) {
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
