package com.videokit.platform.android

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ContainerSnifferTest {
    private fun header(vararg parts: ByteArray, size: Int = 1024): ByteArray {
        val out = ByteArray(size)
        var at = 0
        parts.forEach { part ->
            part.copyInto(out, at)
            at += part.size
        }
        return out
    }

    private fun box(type: String, brand: String) = byteArrayOf(0, 0, 0, 0x18) + type.toByteArray() + brand.toByteArray()

    @Test
    fun isoFamily() {
        assertEquals("mp4", ContainerSniffer.detect(header(box("ftyp", "isom")), 1024))
        assertEquals("mov", ContainerSniffer.detect(header(box("ftyp", "qt  ")), 1024))
    }

    @Test
    fun matroskaAndWebm() {
        val ebml = byteArrayOf(0x1A, 0x45, 0xDF.toByte(), 0xA3.toByte(), 0, 0, 0, 0, 0, 0, 0, 0)
        assertEquals("mkv", ContainerSniffer.detect(header(ebml, "matroska".toByteArray()), 1024))
        assertEquals("webm", ContainerSniffer.detect(header(ebml, "webm".toByteArray()), 1024))
    }

    @Test
    fun avi() {
        assertEquals("avi", ContainerSniffer.detect(header("RIFF".toByteArray(), byteArrayOf(0, 0, 0, 0), "AVI LIST".toByteArray()), 1024))
    }

    @Test
    fun transportStreams() {
        val ts = ByteArray(1024).also { bytes -> listOf(0, 188, 376, 564).forEach { bytes[it] = 0x47 } }
        assertEquals("ts", ContainerSniffer.detect(ts, ts.size))
        val m2ts = ByteArray(1024).also { bytes -> listOf(4, 196, 388, 580).forEach { bytes[it] = 0x47 } }
        assertEquals("m2ts", ContainerSniffer.detect(m2ts, m2ts.size))
    }

    @Test
    fun unknownAndShort() {
        assertNull(ContainerSniffer.detect(ByteArray(1024) { 1 }, 1024))
        assertNull(ContainerSniffer.detect(header(box("ftyp", "isom")), 8))
    }
}
