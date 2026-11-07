package com.videokit.spike.s1

import com.videokit.api.OpenPurpose
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/** The simulated host source delivers the right bytes with the latency and pacing of its condition. */
class SimulatedHostSourceTest {
    private fun sample(size: Int): File = File.createTempFile("s1-sample", ".bin").apply {
        deleteOnExit()
        writeBytes(ByteArray(size) { (it % 251).toByte() })
    }

    @Test
    fun readsTheRightBytesAndCountsThem() = runBlocking {
        val file = sample(100_000)
        val host = SimulatedHostSource(file, Condition("local", 0, 0))
        val handle = host.open(OpenPurpose.PLAYBACK)
        assertEquals(100_000L, handle.length)
        val target = ByteArray(1_000)
        assertEquals(1_000, handle.readAt(50_000, target, 0, 1_000))
        assertArrayEquals(file.readBytes().copyOfRange(50_000, 51_000), target)
        assertEquals(-1, handle.readAt(100_000, target, 0, 10))
        assertEquals(1L, host.bytes.get() / 1_000)
        assertEquals(1, host.openHandles.get())
        handle.close()
        handle.close()
        assertEquals(0, host.openHandles.get())
    }

    @Test
    fun latencyAndThroughputAreApplied() = runBlocking {
        val file = sample(400_000)
        val slow = SimulatedHostSource(file, Condition("lat50", 50, 0))
        val handle = slow.open(OpenPurpose.PLAYBACK)
        val t = System.nanoTime()
        repeat(4) { handle.readAt(it * 1_000L, ByteArray(1_000), 0, 1_000) }
        val ms = (System.nanoTime() - t) / 1_000_000
        assertTrue("4 reads with 50 ms latency took $ms ms", ms >= 200)
        handle.close()
        // 256 KiB at 1 MiB/s takes about 250 ms.
        val paced = SimulatedHostSource(file, Condition("throttle", 0, 1024L * 1024))
        val pacedHandle = paced.open(OpenPurpose.PLAYBACK)
        val t2 = System.nanoTime()
        pacedHandle.readAt(0, ByteArray(256 * 1024), 0, 256 * 1024)
        val pacedMs = (System.nanoTime() - t2) / 1_000_000
        assertTrue("256 KiB at 1 MiB/s took $pacedMs ms", pacedMs in 240..1_000)
        pacedHandle.close()
    }
}
