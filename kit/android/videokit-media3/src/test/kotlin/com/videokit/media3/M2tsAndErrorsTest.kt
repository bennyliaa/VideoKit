package com.videokit.media3

import androidx.media3.common.C
import androidx.media3.common.ColorInfo
import androidx.media3.common.Format
import androidx.media3.common.MimeTypes
import androidx.media3.common.PlaybackException
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.OpenPurpose
import com.videokit.api.UnsupportedDetails
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceFactory
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.InterruptedIOException

/** m2ts adapter (15 §2.2) and Media3 error mapping (06 §1). */
class M2tsAndErrorsTest {
    /** A synthetic m2ts file: [packets] packets of a 4-byte prefix (0xAA..) and a 188-byte TS packet (0x47, n...). */
    private fun m2ts(packets: Int): Pair<ByteArray, ByteArray> {
        val physical = java.io.ByteArrayOutputStream()
        val logical = java.io.ByteArrayOutputStream()
        repeat(packets) { p ->
            physical.write(byteArrayOf(0xAA.toByte(), 0xBB.toByte(), 0xCC.toByte(), p.toByte()))
            val ts = ByteArray(M2ts.TS_PACKET_SIZE) { i -> if (i == 0) 0x47 else ((p * 7 + i) % 256).toByte() }
            physical.write(ts)
            logical.write(ts)
        }
        return physical.toByteArray() to logical.toByteArray()
    }

    private fun reader(bytes: ByteArray, prefetch: Int = 4 * 1024): M2tsReader {
        val handle = object : VideoKitReadHandle {
            override val length: Long = bytes.size.toLong()

            override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
                if (offset >= bytes.size) return -1
                val count = minOf(length, bytes.size - offset.toInt())
                System.arraycopy(bytes, offset.toInt(), target, targetOffset, count)
                return count
            }

            override fun close() = Unit
        }
        val factory = VideoKitSourceFactory { _: OpenPurpose -> handle }
        return M2tsReader(HostReader(HostHandlePool(factory, 1_000), 1_000, prefetch))
    }

    private fun readAll(reader: M2tsReader, chunk: Int): ByteArray {
        val out = java.io.ByteArrayOutputStream()
        val buffer = ByteArray(chunk)
        while (true) {
            val read = reader.read(buffer, 0, buffer.size)
            if (read == HostReader.END) return out.toByteArray()
            out.write(buffer, 0, read)
        }
    }

    @Test
    fun offsetMapping() {
        assertEquals(4L, M2ts.physicalOffset(0))
        assertEquals(4L + 187, M2ts.physicalOffset(187))
        assertEquals(192L + 4, M2ts.physicalOffset(188))
        assertEquals(10L * 192 + 4 + 5, M2ts.physicalOffset(10L * 188 + 5))
        assertEquals(188L * 3, M2ts.logicalLength(192L * 3))
        // A truncated last packet keeps the TS bytes it has.
        assertEquals(188L * 3 + 10, M2ts.logicalLength(192L * 3 + 14))
        assertEquals(188L * 3, M2ts.logicalLength(192L * 3 + 3))
    }

    @Test
    fun logicalStreamHasNoPrefixes() {
        val (physical, logical) = m2ts(40)
        val view = reader(physical)
        assertEquals(logical.size.toLong(), view.open(0, HostReader.UNKNOWN))
        assertArrayEquals(logical, readAll(view, 1_000))
    }

    @Test
    fun seekIntoTheMiddleOfAPacket() {
        val (physical, logical) = m2ts(40)
        val view = reader(physical, prefetch = 4 * 1024)
        val start = 188L * 17 + 99
        assertEquals(logical.size - start, view.open(start, HostReader.UNKNOWN))
        assertArrayEquals(logical.copyOfRange(start.toInt(), logical.size), readAll(view, 333))
        view.close()
        assertEquals(500L, view.open(188L * 2, 500))
        assertArrayEquals(logical.copyOfRange(376, 876), readAll(view, 64))
    }

    @Test
    fun sniffing() {
        val (physical, logical) = m2ts(3)
        assertTrue(M2ts.isM2ts(physical, physical.size))
        assertFalse("plain TS is not m2ts", M2ts.isM2ts(logical, logical.size))
        assertFalse("too short", M2ts.isM2ts(physical, 100))
    }

    @Test
    fun errorMapping() {
        fun code(errorCode: Int, trackType: Int? = null, cause: Throwable? = null) = PlaybackErrors.map(errorCode, cause, trackType).code
        assertEquals(ErrorCode.SOURCE_NOT_FOUND, code(PlaybackException.ERROR_CODE_IO_FILE_NOT_FOUND))
        assertEquals(ErrorCode.SOURCE_PERMISSION_DENIED, code(PlaybackException.ERROR_CODE_IO_NO_PERMISSION))
        assertEquals(ErrorCode.SOURCE_DISCONNECTED, code(PlaybackException.ERROR_CODE_IO_UNSPECIFIED))
        assertEquals(ErrorCode.UNSUPPORTED_CONTAINER, code(PlaybackException.ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED))
        assertEquals(ErrorCode.CORRUPT_MEDIA, code(PlaybackException.ERROR_CODE_PARSING_CONTAINER_MALFORMED))
        assertEquals(ErrorCode.UNSUPPORTED_VIDEO_CODEC, code(PlaybackException.ERROR_CODE_DECODING_FORMAT_UNSUPPORTED, C.TRACK_TYPE_VIDEO))
        assertEquals(
            ErrorCode.UNSUPPORTED_AUDIO_CODEC,
            code(PlaybackException.ERROR_CODE_DECODING_FORMAT_EXCEEDS_CAPABILITIES, C.TRACK_TYPE_AUDIO),
        )
        assertEquals(ErrorCode.DECODER_UNAVAILABLE, code(PlaybackException.ERROR_CODE_DECODER_INIT_FAILED))
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, code(PlaybackException.ERROR_CODE_UNSPECIFIED))
        // Host failures win over the Media3 code; interrupted loads are cancellations.
        val host =
            HostReadException(com.videokit.core.runtime.StableErrors.of(ErrorCode.SOURCE_TIMEOUT, com.videokit.api.ErrorStage.PLAYBACK))
        assertEquals(ErrorCode.SOURCE_TIMEOUT, code(PlaybackException.ERROR_CODE_IO_UNSPECIFIED, cause = RuntimeException(host)))
        assertEquals(ErrorCode.CANCELLED, code(PlaybackException.ERROR_CODE_IO_UNSPECIFIED, cause = InterruptedIOException()))
        assertFalse(
            PlaybackErrors.map(
                PlaybackException.ERROR_CODE_UNSPECIFIED,
                RuntimeException("/secret/path"),
                null,
            ).diagnostic.orEmpty().contains("secret"),
        )
    }

    @Test
    fun unsupportedFormatsCarryTheirDetails() {
        // 04A X2: the UI shows "HEVC 10-bit" from these parameters.
        val hevc10 = Format.Builder()
            .setSampleMimeType(MimeTypes.VIDEO_H265)
            .setCodecs("hvc1.2.4.L120")
            .setContainerMimeType(MimeTypes.VIDEO_MATROSKA)
            .setColorInfo(ColorInfo.Builder().setLumaBitdepth(10).setChromaBitdepth(10).build())
            .build()
        val exceedsCode = PlaybackException.ERROR_CODE_DECODING_FORMAT_EXCEEDS_CAPABILITIES
        val exceeds = PlaybackErrors.map(exceedsCode, null, C.TRACK_TYPE_VIDEO, hevc10)
        assertEquals(ErrorCode.UNSUPPORTED_VIDEO_CODEC, exceeds.code)
        assertEquals(
            mapOf(
                ErrorParams.REASON_DETAIL to UnsupportedDetails.EXCEEDS_CAPABILITIES,
                ErrorParams.CODEC to MimeTypes.VIDEO_H265,
                ErrorParams.PROFILE to "hvc1.2.4.L120",
                ErrorParams.BIT_DEPTH to "10",
                ErrorParams.CONTAINER to MimeTypes.VIDEO_MATROSKA,
            ),
            exceeds.params,
        )
        // Without a format only the detail is known; other errors get no details.
        val noFormat = PlaybackErrors.map(PlaybackException.ERROR_CODE_DECODING_FORMAT_UNSUPPORTED, null, C.TRACK_TYPE_AUDIO)
        assertEquals(mapOf(ErrorParams.REASON_DETAIL to UnsupportedDetails.FORMAT_UNSUPPORTED), noFormat.params)
        assertTrue(PlaybackErrors.map(PlaybackException.ERROR_CODE_DECODING_FAILED, null, C.TRACK_TYPE_VIDEO, hevc10).params.isEmpty())
    }
}
