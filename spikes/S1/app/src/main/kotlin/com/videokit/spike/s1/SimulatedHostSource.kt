package com.videokit.spike.s1

import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Seekability
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

/**
 * One network condition of S1 (15 §4): every host `readAt` waits [latencyMs] before it returns, and the delivered
 * bytes are paced to [bytesPerSecond] (0 = unlimited). Models an SMB/WebDAV host behind the Browser's readAt.
 */
data class Condition(val name: String, val latencyMs: Long, val bytesPerSecond: Long) {
    companion object {
        val ALL = listOf(
            Condition("local", 0, 0),
            Condition("lat20", 20, 0),
            Condition("lat50", 50, 0),
            Condition("lat100", 100, 0),
            // Throttled: 4 MB/s (≈ 32 Mbit/s Wi-Fi to a NAS) with 20 ms latency.
            Condition("throttle4MBps", 20, 4L * 1024 * 1024),
        )
    }
}

/** Host source over a local file with the latency and pacing of a [Condition]; counts reads and bytes. */
class SimulatedHostSource(private val file: File, private val condition: Condition) : VideoKitSourceFactory {
    val reads = AtomicLong()
    val bytes = AtomicLong()
    val openHandles = AtomicInteger()
    val maxReadMs = AtomicLong()

    fun mediaSource(token: String): VideoKitMediaSource = VideoKitMediaSource(
        mediaToken = token,
        mediaKind = MediaKind.VIDEO,
        displayName = file.name,
        knownLength = file.length(),
        extension = file.extension,
        seekability = Seekability.RANDOM_ACCESS,
        sourceFactory = this,
    )

    override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle = withContext(Dispatchers.IO) {
        delay(condition.latencyMs)
        openHandles.incrementAndGet()
        val channel = RandomAccessFile(file, "r").channel
        object : VideoKitReadHandle {
            @Volatile private var closed = false

            override val length: Long = file.length()

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
                val started = System.nanoTime()
                delay(condition.latencyMs)
                val read = withContext(Dispatchers.IO) {
                    check(!closed) { "read after close" }
                    channel.read(ByteBuffer.wrap(target, targetOffset, length), offset)
                }
                if (read > 0 && condition.bytesPerSecond > 0) delay(read * 1_000L / condition.bytesPerSecond)
                reads.incrementAndGet()
                if (read > 0) bytes.addAndGet(read.toLong())
                val ms = (System.nanoTime() - started) / 1_000_000
                maxReadMs.accumulateAndGet(ms) { a, b -> maxOf(a, b) }
                return read
            }

            override fun close() {
                if (closed) return
                closed = true
                runCatching { channel.close() }
                openHandles.decrementAndGet()
            }
        }
    }
}
