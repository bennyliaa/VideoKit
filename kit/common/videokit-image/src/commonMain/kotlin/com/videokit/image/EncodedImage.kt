package com.videokit.image

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.OpenPurpose
import com.videokit.api.VideoKitMediaSource
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout

/**
 * The encoded bytes of an image, read once through the host `readAt` (06 §6.2: the decoder source reads from a
 * bounded session buffer; region decoding of large images reads its tiles from the same buffer). The read handle is
 * closed before this returns, so an opened image holds no host handle; nothing is written to disk.
 */
public object EncodedImage {
    /** Largest encoded image read into memory (larger files fail with DECODER_RESOURCE_EXHAUSTED). */
    public const val MAX_ENCODED_BYTES: Long = 96L * 1024 * 1024

    /** Bytes per host read. */
    public const val CHUNK_BYTES: Int = 512 * 1024

    /**
     * Reads all of [source]. Throws [SpiException]: a stable source error for host failures and timeouts (each read
     * is bounded by [readTimeoutMs]), CORRUPT_MEDIA for an empty file, DECODER_RESOURCE_EXHAUSTED above [maxBytes].
     */
    public suspend fun read(source: VideoKitMediaSource, readTimeoutMs: Long, maxBytes: Long = MAX_ENCODED_BYTES): ByteArray {
        val handle = try {
            source.sourceFactory.open(OpenPurpose.PLAYBACK)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.BIND))
        }
        try {
            val known = handle.length
            if (known != null && known > maxBytes) throw tooLarge()
            var buffer = ByteArray((known ?: CHUNK_BYTES.toLong()).coerceAtLeast(1L).toInt())
            var filled = 0
            while (true) {
                if (filled == buffer.size) {
                    if (known != null && filled.toLong() >= known) break
                    if (buffer.size.toLong() >= maxBytes) throw tooLarge()
                    buffer = buffer.copyOf(minOf(maxBytes, buffer.size.toLong() * 2).toInt())
                }
                val wanted = minOf(CHUNK_BYTES, buffer.size - filled)
                val read = withTimeout(readTimeoutMs) { handle.readAt(filled.toLong(), buffer, filled, wanted) }
                // -1 is the end; a read of 0 bytes is treated as the end too (no busy loop on a stalled host).
                if (read <= 0) break
                filled += read
            }
            if (filled == 0) throw SpiException(StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.PROBE, "IMAGE_EMPTY"))
            return if (filled == buffer.size) buffer else buffer.copyOf(filled)
        } catch (timeout: TimeoutCancellationException) {
            throw SpiException(StableErrors.fromSourceFailure(timeout, ErrorStage.BIND))
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: SpiException) {
            throw failure
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.BIND))
        } finally {
            withContext(NonCancellable) { runCatching { handle.close() } }
        }
    }

    private fun tooLarge() = SpiException(StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "IMAGE_ENCODED_TOO_LARGE"))
}
