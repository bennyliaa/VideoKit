package com.videokit.api.android

import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Seekability
import com.videokit.api.SourceErrorCode
import com.videokit.api.VideoKitSourceException
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class MediaSourcesTest {
    @get:Rule
    val temp = TemporaryFolder()

    @Test
    fun fromFileReadsAtArbitraryOffsets() = runTest {
        val bytes = ByteArray(4096) { (it % 251).toByte() }
        val file = temp.newFile("clip.MP4").apply { writeBytes(bytes) }
        val source = MediaSources.fromFile(file, "token-1", MediaKind.VIDEO)
        assertEquals("mp4", source.extension)
        assertEquals(4096L, source.knownLength)
        assertEquals(Seekability.RANDOM_ACCESS, source.seekability)
        assertNull(source.displayName)

        source.sourceFactory.open(OpenPurpose.PLAYBACK).use { handle ->
            assertEquals(4096L, handle.length)
            val target = ByteArray(16)
            assertEquals(10, handle.readAt(1000, target, 3, 10))
            assertArrayEquals(bytes.copyOfRange(1000, 1010), target.copyOfRange(3, 13))
            // Short read at the end, then EOF.
            assertEquals(6, handle.readAt(4090, target, 0, 16))
            assertEquals(-1, handle.readAt(4096, target, 0, 16))
        }
    }

    @Test
    fun missingFileMapsToNotFound() = runTest {
        val source = MediaSources.fromFile(File(temp.root, "missing.mp4"), "token-2", MediaKind.VIDEO)
        try {
            source.sourceFactory.open(OpenPurpose.PROBE)
            fail("expected VideoKitSourceException")
        } catch (expected: VideoKitSourceException) {
            assertEquals(SourceErrorCode.NOT_FOUND, expected.code)
        }
    }

    @Test
    fun closedHandleRejectsReadsAndCloseIsIdempotent() = runTest {
        val file = temp.newFile("a.bin").apply { writeBytes(ByteArray(8)) }
        val handle = MediaSources.fromFile(file, "t", MediaKind.VIDEO).sourceFactory.open(OpenPurpose.PROBE)
        handle.close()
        handle.close()
        assertNull(handle.length)
        try {
            handle.readAt(0, ByteArray(4), 0, 4)
            fail("expected IllegalStateException")
        } catch (expected: IllegalStateException) {
            assertEquals("read handle is closed", expected.message)
        }
    }
}
