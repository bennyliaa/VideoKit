package com.videokit.media3

import com.videokit.api.ErrorStage
import com.videokit.api.VideoKitReadHandle
import kotlinx.coroutines.awaitCancellation
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

/** 04A P5: a frame extraction blocked in a host read is aborted from another thread (S1 hang at lat100). */
class AbortableReadsTest {
    private class HangingHandle : VideoKitReadHandle {
        val started = CountDownLatch(1)
        val closes = AtomicInteger()
        override val length: Long = 1_000

        override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
            started.countDown()
            awaitCancellation()
        }

        override fun close() {
            closes.incrementAndGet()
        }
    }

    @Test
    fun abortCancelsTheBlockedReadClosesTheHandleOnceAndFailsLaterReads() {
        val handle = HangingHandle()
        val reads = AbortableReads(handle)
        val outcome = AtomicReference<Throwable?>()
        // The retriever's worker thread: one host read with a long timeout, as HostMediaDataSource.readAt.
        val worker = Thread {
            try {
                blocking(60_000, ErrorStage.PROBE) { reads.read { handle.readAt(0, ByteArray(10), 0, 10) } }
            } catch (failure: Throwable) {
                outcome.set(failure)
            }
        }
        worker.start()
        assertTrue(handle.started.await(5, TimeUnit.SECONDS))
        val abortedAt = System.nanoTime()
        reads.abort()
        worker.join(5_000)
        val joinMs = (System.nanoTime() - abortedAt) / 1_000_000
        assertFalse("worker finished", worker.isAlive)
        assertTrue("aborted read returned in ${joinMs}ms", joinMs < 1_000)
        assertTrue("fails as a host read error, was ${outcome.get()}", outcome.get() is HostReadException)
        assertTrue(reads.isAborted)
        assertEquals(1, handle.closes.get())

        // Later reads fail at once and never reach the host; closing again does not close twice.
        try {
            blocking(60_000, ErrorStage.PROBE) { reads.read { handle.readAt(0, ByteArray(10), 0, 10) } }
            fail("expected failure")
        } catch (expected: HostReadException) {
            // aborted
        }
        reads.abort()
        reads.closeHandle()
        assertEquals(1, handle.closes.get())
    }

    @Test
    fun closeWithoutAbortClosesTheHandleOnce() {
        val handle = HangingHandle()
        val reads = AbortableReads(handle)
        reads.closeHandle()
        reads.closeHandle()
        assertEquals(1, handle.closes.get())
        assertFalse(reads.isAborted)
    }
}
