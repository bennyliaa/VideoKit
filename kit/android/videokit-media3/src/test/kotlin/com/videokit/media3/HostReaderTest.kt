package com.videokit.media3

import com.videokit.api.ErrorCode
import com.videokit.api.OpenPurpose
import com.videokit.api.SourceErrorCode
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceException
import com.videokit.api.VideoKitSourceFactory
import kotlinx.coroutines.awaitCancellation
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import java.io.InterruptedIOException
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

/** The host read bridge of HostDataSource (06 §3), on the JVM without Media3 or a device. */
class HostReaderTest {
    private class MemoryHandle(
        private val bytes: ByteArray,
        private val maxRead: Int = Int.MAX_VALUE,
        override val length: Long? = bytes.size.toLong(),
    ) : VideoKitReadHandle {
        var reads = 0
        var closed = false

        override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
            reads++
            if (offset >= bytes.size) return -1
            val count = minOf(length, maxRead, bytes.size - offset.toInt())
            System.arraycopy(bytes, offset.toInt(), target, targetOffset, count)
            return count
        }

        override fun close() {
            closed = true
        }
    }

    private class Factory(private val handle: VideoKitReadHandle) : VideoKitSourceFactory {
        var opens = 0
        val purposes = mutableListOf<OpenPurpose>()

        override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle {
            opens++
            purposes += purpose
            return handle
        }
    }

    private val data = ByteArray(100_000) { (it % 251).toByte() }

    private fun readAll(reader: HostReader, chunk: Int = 1_000): ByteArray {
        val out = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(chunk)
        while (true) {
            val read = reader.read(buffer, 0, buffer.size)
            if (read == HostReader.END) return out.toByteArray()
            out.write(buffer, 0, read)
        }
    }

    @Test
    fun readsWholeSourceThroughBoundedPrefetch() {
        val handle = MemoryHandle(data)
        val pool = HostHandlePool(Factory(handle), 1_000)
        val reader = HostReader(pool, 1_000, 16 * 1024)
        assertEquals(data.size.toLong(), reader.open(0, HostReader.UNKNOWN))
        assertArrayEquals(data, readAll(reader))
        // 100 000 bytes in 16 KiB read-ahead blocks: 7 host reads, not one per 1 000-byte Media3 read.
        assertEquals(7, handle.reads)
    }

    @Test
    fun rangeOpenReadsOnlyTheRangeAndSeeksReuseTheHostHandle() {
        val handle = MemoryHandle(data)
        val factory = Factory(handle)
        val pool = HostHandlePool(factory, 1_000)
        val reader = HostReader(pool, 1_000, 8 * 1024)
        assertEquals(500L, reader.open(70_000, 500))
        assertArrayEquals(data.copyOfRange(70_000, 70_500), readAll(reader, 64))
        reader.close()
        // A seek re-opens the data source, not the host handle (06 §3.3).
        assertEquals(1_000L, reader.open(99_000, HostReader.UNKNOWN))
        reader.close()
        assertEquals(1, factory.opens)
        assertEquals(listOf(OpenPurpose.PLAYBACK), factory.purposes)
        assertFalse(handle.closed)
        pool.close()
        assertTrue(handle.closed)
    }

    @Test
    fun shortReadsAndUnknownLengthEndAtMinusOne() {
        val handle = MemoryHandle(data.copyOf(10_000), maxRead = 333, length = null)
        val reader = HostReader(HostHandlePool(Factory(handle), 1_000), 1_000, 4 * 1024)
        assertEquals(HostReader.UNKNOWN, reader.open(0, HostReader.UNKNOWN))
        assertArrayEquals(data.copyOf(10_000), readAll(reader))
    }

    @Test
    fun positionsBeyondTwoGibAreLongs() {
        val big = object : VideoKitReadHandle {
            var lastOffset = -1L
            override val length: Long = 3L * 1024 * 1024 * 1024

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
                lastOffset = offset
                target.fill(7, targetOffset, targetOffset + length)
                return length
            }

            override fun close() = Unit
        }
        val reader = HostReader(HostHandlePool(Factory(big), 1_000), 1_000, 4 * 1024)
        val start = 2_500_000_000L
        assertEquals(big.length - start, reader.open(start, HostReader.UNKNOWN))
        assertEquals(100, reader.read(ByteArray(100), 0, 100))
        assertEquals(start, big.lastOffset)
    }

    @Test
    fun classifiedHostFailuresKeepTheirCodeAndOthersAreRedacted() {
        val classified = object : VideoKitReadHandle {
            override val length: Long = 10

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int =
                throw VideoKitSourceException(SourceErrorCode.DISCONNECTED, "smb://user:secret@nas/path")

            override fun close() = Unit
        }
        val failure = readFailure(classified)
        assertEquals(ErrorCode.SOURCE_DISCONNECTED, failure.error.code)
        val plain = object : VideoKitReadHandle {
            override val length: Long = 10

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int =
                throw java.io.IOException("/storage/emulated/0/private/file.mp4")

            override fun close() = Unit
        }
        val redacted = readFailure(plain)
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, redacted.error.code)
        assertFalse("no path in diagnostics", redacted.error.diagnostic.orEmpty().contains("storage"))
        assertFalse(redacted.message.orEmpty().contains("storage"))
    }

    @Test
    fun hangingReadTimesOutAsSourceTimeout() {
        val hanging = object : VideoKitReadHandle {
            override val length: Long = 10

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int = awaitCancellation()

            override fun close() = Unit
        }
        val reader = HostReader(HostHandlePool(Factory(hanging), 1_000), 50, 4 * 1024)
        reader.open(0, HostReader.UNKNOWN)
        try {
            reader.read(ByteArray(10), 0, 10)
            fail("expected timeout")
        } catch (expected: HostReadException) {
            assertEquals(ErrorCode.SOURCE_TIMEOUT, expected.error.code)
        }
    }

    @Test
    fun interruptingTheLoaderThreadCancelsTheRead() {
        val started = CountDownLatch(1)
        val hanging = object : VideoKitReadHandle {
            override val length: Long = 10

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
                started.countDown()
                awaitCancellation()
            }

            override fun close() = Unit
        }
        val reader = HostReader(HostHandlePool(Factory(hanging), 1_000), 60_000, 4 * 1024)
        reader.open(0, HostReader.UNKNOWN)
        val outcome = AtomicReference<Throwable?>()
        val loader = Thread {
            try {
                reader.read(ByteArray(10), 0, 10)
            } catch (failure: Throwable) {
                outcome.set(failure)
            }
        }
        loader.start()
        assertTrue(started.await(5, TimeUnit.SECONDS))
        loader.interrupt()
        loader.join(5_000)
        assertFalse("loader thread finished", loader.isAlive)
        assertTrue("cancelled as InterruptedIOException, was ${outcome.get()}", outcome.get() is InterruptedIOException)
    }

    @Test
    fun releasedPoolRefusesNewLoads() {
        val pool = HostHandlePool(Factory(MemoryHandle(data)), 1_000)
        pool.close()
        try {
            HostReader(pool, 1_000, 4 * 1024).open(0, HostReader.UNKNOWN)
            fail("expected refusal")
        } catch (expected: InterruptedIOException) {
            // A released playback never re-opens the host source.
        }
    }

    private fun readFailure(handle: VideoKitReadHandle): HostReadException {
        val reader = HostReader(HostHandlePool(Factory(handle), 1_000), 1_000, 4 * 1024)
        reader.open(0, HostReader.UNKNOWN)
        try {
            reader.read(ByteArray(10), 0, 10)
        } catch (failure: HostReadException) {
            return failure
        }
        throw AssertionError("expected HostReadException")
    }
}
