package com.videokit.image

import com.videokit.api.ErrorCode
import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Seekability
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceFactory
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull

class ImageHeadersTest {
    private fun bytes(vararg values: Int) = ByteArray(values.size) { values[it].toByte() }

    private fun ascii(text: String) = text.encodeToByteArray()

    private fun le16(value: Int) = bytes(value and 0xFF, value shr 8 and 0xFF)

    private fun le24(value: Int) = bytes(value and 0xFF, value shr 8 and 0xFF, value shr 16 and 0xFF)

    private fun le32(value: Int) = le16(value and 0xFFFF) + le16(value ushr 16)

    private fun gifFrame(delayCs: Int) = bytes(0x21, 0xF9, 0x04, 0x00) + le16(delayCs) + bytes(0x00, 0x00) +
        bytes(0x2C, 0, 0, 0, 0, 1, 0, 1, 0, 0x00) + bytes(0x02, 0x02, 0x4C, 0x01, 0x00)

    private val gif = ascii("GIF89a") + le16(1) + le16(1) + bytes(0x00, 0, 0) +
        bytes(0x21, 0xFF, 0x0B) + ascii("NETSCAPE2.0") + bytes(0x03, 0x01, 0x00, 0x00, 0x00) +
        gifFrame(5) + gifFrame(0) + bytes(0x3B)

    private fun chunk(name: String, payload: ByteArray) = ascii(name) + le32(payload.size) + payload

    private fun anmf(durationMs: Int) = chunk("ANMF", ByteArray(12) + le24(durationMs) + bytes(0))

    private val webp = run {
        val body = ascii("WEBP") + chunk("VP8X", ByteArray(10).also { it[0] = 0x02 }) +
            chunk("ANIM", ByteArray(4) + le16(3)) + anmf(120) + anmf(0)
        ascii("RIFF") + le32(body.size) + body
    }

    @Test
    fun gifTiming() {
        val timing = AnimationHeaders.parse(gif)
        assertEquals(AnimationTiming(frameCount = 2, loopDurationUs = 150_000L, storedLoopCount = 0), timing)
    }

    @Test
    fun webpTiming() {
        assertEquals(AnimationTiming(frameCount = 2, loopDurationUs = 220_000L, storedLoopCount = 3), AnimationHeaders.parse(webp))
    }

    @Test
    fun brokenOrOtherDataHasNoTiming() {
        assertNull(AnimationHeaders.parse(gif.copyOf(30)))
        assertNull(AnimationHeaders.parse(ascii("not an image")))
        assertNull(AnimationHeaders.parse(ByteArray(0)))
    }

    @Test
    fun formatSniffing() {
        assertEquals(ImageFormats.JPEG, ImageFormats.sniff(bytes(0xFF, 0xD8, 0xFF, 0xE0)))
        assertEquals(ImageFormats.PNG, ImageFormats.sniff(bytes(0x89) + ascii("PNG\r\n") + bytes(0x1A, 0x0A)))
        assertEquals(ImageFormats.GIF, ImageFormats.sniff(gif))
        assertEquals(ImageFormats.WEBP, ImageFormats.sniff(webp))
        assertEquals(ImageFormats.BMP, ImageFormats.sniff(ascii("BM") + ByteArray(20)))
        assertEquals(ImageFormats.HEIF, ImageFormats.sniff(le32(24) + ascii("ftypheic") + ByteArray(4) + ascii("mif1heic")))
        assertEquals(ImageFormats.AVIF, ImageFormats.sniff(le32(24) + ascii("ftypmif1") + ByteArray(4) + ascii("avifmiaf")))
        assertNull(ImageFormats.sniff(ascii("hello world, not an image")))
    }

    private class MemorySource(private val data: ByteArray, private val reportLength: Boolean = true, private val fail: Boolean = false) :
        VideoKitSourceFactory {
        var opened = 0
        var closed = 0

        override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle {
            opened++
            return object : VideoKitReadHandle {
                override val length: Long? get() = if (reportLength) data.size.toLong() else null

                override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
                    if (fail) throw IllegalStateException("/secret/path")
                    if (offset >= data.size) return -1
                    val count = minOf(length, data.size - offset.toInt(), 1000)
                    data.copyInto(target, targetOffset, offset.toInt(), offset.toInt() + count)
                    return count
                }

                override fun close() {
                    closed++
                }
            }
        }
    }

    private fun source(factory: VideoKitSourceFactory) =
        VideoKitMediaSource("img", MediaKind.IMAGE_STATIC, seekability = Seekability.RANDOM_ACCESS, sourceFactory = factory)

    @Test
    fun encodedImageIsReadOnceAndTheHandleClosed() = runTest {
        val data = ByteArray(5_000) { it.toByte() }
        for (known in listOf(true, false)) {
            val factory = MemorySource(data, reportLength = known)
            assertContentEquals(data, EncodedImage.read(source(factory), readTimeoutMs = 1_000L))
            assertEquals(1, factory.opened)
            assertEquals(1, factory.closed)
        }
    }

    @Test
    fun encodedImageFailures() = runTest {
        val tooLarge =
            assertFailsWith<SpiException> { EncodedImage.read(source(MemorySource(ByteArray(2_000))), 1_000L, maxBytes = 1_000L) }
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, tooLarge.error.code)
        val unknownTooLarge = assertFailsWith<SpiException> {
            EncodedImage.read(source(MemorySource(ByteArray(2_000_000), reportLength = false)), 1_000L, maxBytes = 1_000_000L)
        }
        assertEquals(ErrorCode.DECODER_RESOURCE_EXHAUSTED, unknownTooLarge.error.code)
        val empty = assertFailsWith<SpiException> { EncodedImage.read(source(MemorySource(ByteArray(0), reportLength = false)), 1_000L) }
        assertEquals(ErrorCode.CORRUPT_MEDIA, empty.error.code)
        val factory = MemorySource(ByteArray(10), fail = true)
        val failed = assertFailsWith<SpiException> { EncodedImage.read(source(factory), 1_000L) }
        assertEquals(false, failed.error.diagnostic.orEmpty().contains("secret"))
        assertEquals(1, factory.closed)
    }
}
