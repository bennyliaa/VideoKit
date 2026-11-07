package com.videokit.media3

import androidx.media3.common.C
import androidx.media3.common.PlaybackException
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.VideoKitStableError
import com.videokit.core.runtime.StableErrors
import java.io.InterruptedIOException

/**
 * Maps Media3 playback failures to stable errors (06 §1, 04 §9): no underlying exception, message or path reaches
 * the host; the diagnostic only names the Media3 error code. Host source failures keep their classified code.
 */
internal object PlaybackErrors {
    /**
     * Stable error of a Media3 failure with [errorCode] (`PlaybackException.errorCode`), [cause] and the type of the
     * failing renderer ([trackType] = `C.TRACK_TYPE_*`, `null` when not a renderer failure).
     */
    fun map(errorCode: Int, cause: Throwable?, trackType: Int?): VideoKitStableError {
        hostFailure(cause)?.let { return it }
        if (causes(cause).any {
                it is InterruptedIOException
            }
        ) {
            return StableErrors.of(ErrorCode.CANCELLED, ErrorStage.PLAYBACK, "MEDIA3:INTERRUPTED")
        }
        val diagnostic = "MEDIA3:$errorCode"
        val audio = trackType == C.TRACK_TYPE_AUDIO
        return when (errorCode) {
            PlaybackException.ERROR_CODE_IO_FILE_NOT_FOUND -> StableErrors.of(ErrorCode.SOURCE_NOT_FOUND, ErrorStage.PLAYBACK, diagnostic)

            PlaybackException.ERROR_CODE_IO_NO_PERMISSION -> StableErrors.of(
                ErrorCode.SOURCE_PERMISSION_DENIED,
                ErrorStage.PLAYBACK,
                diagnostic,
            )

            PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_TIMEOUT,
            PlaybackException.ERROR_CODE_TIMEOUT,
            -> StableErrors.of(ErrorCode.SOURCE_TIMEOUT, ErrorStage.PLAYBACK, diagnostic)

            PlaybackException.ERROR_CODE_IO_UNSPECIFIED,
            PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_FAILED,
            PlaybackException.ERROR_CODE_IO_READ_POSITION_OUT_OF_RANGE,
            -> StableErrors.of(ErrorCode.SOURCE_DISCONNECTED, ErrorStage.PLAYBACK, diagnostic)

            PlaybackException.ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED ->
                StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, diagnostic)

            PlaybackException.ERROR_CODE_PARSING_CONTAINER_MALFORMED,
            PlaybackException.ERROR_CODE_PARSING_MANIFEST_MALFORMED,
            PlaybackException.ERROR_CODE_DECODING_FAILED,
            -> StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, diagnostic)

            PlaybackException.ERROR_CODE_DECODING_FORMAT_UNSUPPORTED,
            PlaybackException.ERROR_CODE_DECODING_FORMAT_EXCEEDS_CAPABILITIES,
            -> StableErrors.of(
                if (audio) ErrorCode.UNSUPPORTED_AUDIO_CODEC else ErrorCode.UNSUPPORTED_VIDEO_CODEC,
                ErrorStage.DECODE,
                diagnostic,
            )

            PlaybackException.ERROR_CODE_DECODER_INIT_FAILED,
            PlaybackException.ERROR_CODE_DECODER_QUERY_FAILED,
            PlaybackException.ERROR_CODE_AUDIO_TRACK_INIT_FAILED,
            -> StableErrors.of(ErrorCode.DECODER_UNAVAILABLE, ErrorStage.DECODE, diagnostic)

            PlaybackException.ERROR_CODE_DECODING_RESOURCES_RECLAIMED ->
                StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.DECODE, diagnostic)

            else -> StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.PLAYBACK, diagnostic)
        }
    }

    /** The stable error of a host source failure in [cause]'s chain, if any. */
    fun hostFailure(cause: Throwable?): VideoKitStableError? = causes(cause).filterIsInstance<HostReadException>().firstOrNull()?.error

    private fun causes(start: Throwable?): Sequence<Throwable> = generateSequence(start) { current ->
        current.cause?.takeIf { it !== current }
    }
}
