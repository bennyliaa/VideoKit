package com.videokit.media3

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.OpenPurpose
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceFactory
import com.videokit.api.VideoKitStableError
import com.videokit.core.runtime.StableErrors
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import java.io.IOException
import java.io.InterruptedIOException

/** A host source failure inside Media3's loading path, carrying the stable error for the session (06 §3.5). */
internal class HostReadException(val error: VideoKitStableError) : IOException("host read failed: ${error.code}")

/**
 * The read handle of one playback (06 §3.1): opened once with [OpenPurpose.PLAYBACK] on first use and reused by
 * every load (seeks re-open the data source, not the host handle); closed when the playback is released, after
 * which [acquire] fails. Thread safe: Media3 loads run on loader threads.
 */
internal class HostHandlePool(private val factory: VideoKitSourceFactory, private val openTimeoutMs: Long) : AutoCloseable {
    private val lock = Any()
    private var handle: VideoKitReadHandle? = null
    private var closed = false

    /** Length the host reported for the open handle (04A P2 fileSizeBytes), when known. */
    val length: Long? get() = synchronized(lock) { handle?.length }

    /** Whether the host handle is currently open (diagnostics, release checks). */
    val isOpen: Boolean get() = synchronized(lock) { handle != null }

    fun acquire(): VideoKitReadHandle = synchronized(lock) {
        if (closed) throw InterruptedIOException("playback released")
        handle ?: blocking(openTimeoutMs, ErrorStage.BIND) { factory.open(OpenPurpose.PLAYBACK) }.also { handle = it }
    }

    override fun close() {
        val current = synchronized(lock) {
            closed = true
            handle.also { handle = null }
        }
        runCatching { current?.close() }
    }
}

/**
 * Reads a byte range of the host handle for Media3 (06 §3.2–3.4): blocking bridge to the suspending `readAt` on the
 * calling loader thread with a timeout, interruptible (thread interrupt = cancellation), and a bounded in-memory
 * read-ahead buffer of [prefetchBytes] (no disk cache, 15 §2.1). Short reads are normal; -1 means end of input.
 *
 * Not thread safe: one reader per data source instance, which Media3 uses from one loader thread at a time.
 */
internal class HostReader(private val pool: HostHandlePool, private val readTimeoutMs: Long, prefetchBytes: Int) {
    private val buffer = ByteArray(prefetchBytes.coerceAtLeast(MIN_PREFETCH))
    private var bufferStart = -1L
    private var bufferLength = 0
    private var position = 0L
    private var remaining = UNKNOWN
    private var handle: VideoKitReadHandle? = null

    /**
     * Opens the range starting at [position] with [length] bytes ([UNKNOWN] = to the end). Returns the number of
     * bytes that can be read, or [UNKNOWN] when the host does not know the total length.
     */
    fun open(position: Long, length: Long): Long {
        require(position >= 0) { "negative position" }
        val opened = pool.acquire()
        handle = opened
        this.position = position
        val total = opened.length
        if (total != null && position > total) {
            throw HostReadException(StableErrors.invalidArgument(ErrorStage.PLAYBACK, "READ_POSITION"))
        }
        val available = total?.let { it - position }
        remaining = when {
            length != UNKNOWN && available != null -> minOf(length, available)
            length != UNKNOWN -> length
            available != null -> available
            else -> UNKNOWN
        }
        return remaining
    }

    /** Reads up to [length] bytes into [target]; -1 at the end of the range or of the source. */
    fun read(target: ByteArray, offset: Int, length: Int): Int {
        if (length == 0) return 0
        if (remaining == 0L) return END
        val wanted = if (remaining == UNKNOWN) length else minOf(length.toLong(), remaining).toInt()
        if (!buffered(position)) {
            val fill = if (remaining == UNKNOWN) buffer.size else minOf(buffer.size.toLong(), remaining).toInt()
            val opened = handle ?: throw IllegalStateException("read before open")
            val read = blocking(readTimeoutMs, ErrorStage.PLAYBACK) { opened.readAt(position, buffer, 0, fill) }
            if (read <= 0) {
                remaining = 0L
                return END
            }
            bufferStart = position
            bufferLength = read
        }
        val inBuffer = (position - bufferStart).toInt()
        val count = minOf(wanted, bufferLength - inBuffer)
        System.arraycopy(buffer, inBuffer, target, offset, count)
        position += count
        if (remaining != UNKNOWN) remaining -= count
        return count
    }

    /** Skips [count] bytes of the range without copying (m2ts packet prefixes); returns the bytes skipped. */
    fun skip(count: Int): Int {
        val skipped = if (remaining == UNKNOWN) count.toLong() else minOf(count.toLong(), remaining)
        position += skipped
        if (remaining != UNKNOWN) remaining -= skipped
        return skipped.toInt()
    }

    /** Ends the range; the host handle stays open for the next load (closed by the [HostHandlePool]). */
    fun close() {
        handle = null
        remaining = UNKNOWN
    }

    /** Current read position (diagnostics and the m2ts adapter). */
    val currentPosition: Long get() = position

    private fun buffered(at: Long): Boolean = bufferStart >= 0 && at >= bufferStart && at < bufferStart + bufferLength

    companion object {
        /** Unknown length (Media3 `C.LENGTH_UNSET`). */
        const val UNKNOWN = -1L

        /** End of input (Media3 `C.RESULT_END_OF_INPUT`). */
        const val END = -1

        /** Default read-ahead per host read (S1 tunes it; 15 §2.1). */
        const val DEFAULT_PREFETCH_BYTES = 256 * 1024

        private const val MIN_PREFETCH = 4 * 1024
    }
}

/**
 * Runs a suspending host call on the calling (loader) thread. Thread interrupt → [InterruptedIOException] (Media3
 * cancels loads this way); timeout → SOURCE_TIMEOUT; classified failures keep their code; anything else is
 * redacted (13 §3.1: never the message).
 */
internal fun <T> blocking(timeoutMs: Long, stage: ErrorStage, block: suspend () -> T): T = try {
    runBlocking { withTimeout(timeoutMs) { block() } }
} catch (interrupted: InterruptedException) {
    Thread.currentThread().interrupt()
    throw InterruptedIOException("host read interrupted")
} catch (failure: HostReadException) {
    throw failure
} catch (timeout: TimeoutCancellationException) {
    throw HostReadException(StableErrors.of(ErrorCode.SOURCE_TIMEOUT, stage, "SOURCE:TIMEOUT"))
} catch (interrupted: InterruptedIOException) {
    throw interrupted
} catch (failure: Exception) {
    // Includes host IOExceptions: their messages may contain paths and ExoPlayer logs errors, so they are redacted.
    throw HostReadException(StableErrors.fromSourceFailure(failure, stage))
}
