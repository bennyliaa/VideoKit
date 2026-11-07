package com.videokit.platform.android

/**
 * Container detection from the first bytes of a file (06 §1 probe, 15 §2.2): the containers Media3's extractors
 * read, plus m2ts (through the adapter of `videokit-media3`). Pure, so it is unit tested on the JVM.
 */
internal object ContainerSniffer {
    /** Bytes [detect] looks at. */
    const val HEADER_BYTES = 4096

    /** Detected container name (`mp4`, `mov`, `mkv`, `webm`, `avi`, `ts`, `m2ts`), or `null` when unknown. */
    fun detect(header: ByteArray, length: Int): String? {
        if (length < 12) return null
        return when {
            isFtyp(header) -> if (brand(header) == "qt  ") "mov" else "mp4"
            startsWith(header, EBML) -> if (contains(header, length, "webm")) "webm" else "mkv"
            startsWith(header, "RIFF".toByteArray()) && ascii(header, 8, 4) == "AVI " -> "avi"
            tsSync(header, length, offset = 0, stride = 188) -> "ts"
            tsSync(header, length, offset = 4, stride = 192) -> "m2ts"
            else -> null
        }
    }

    private val EBML = byteArrayOf(0x1A, 0x45, 0xDF.toByte(), 0xA3.toByte())

    private fun isFtyp(header: ByteArray): Boolean = ascii(header, 4, 4) == "ftyp"

    private fun brand(header: ByteArray): String = ascii(header, 8, 4)

    private fun ascii(header: ByteArray, offset: Int, count: Int): String = String(header, offset, count, Charsets.US_ASCII)

    private fun startsWith(header: ByteArray, prefix: ByteArray): Boolean = prefix.indices.all { header[it] == prefix[it] }

    private fun contains(header: ByteArray, length: Int, text: String): Boolean =
        String(header, 0, length, Charsets.ISO_8859_1).contains(text)

    /** Three consecutive 0x47 sync bytes at [offset] + n·[stride]. */
    private fun tsSync(header: ByteArray, length: Int, offset: Int, stride: Int): Boolean =
        (0 until 3).all { packet -> offset + packet * stride < length && header[offset + packet * stride] == SYNC } &&
            // Plain TS also has a sync byte at 4 + n·192 rarely; m2ts must not have it at 0 + n·188.
            !(offset == 4 && header[0] == SYNC && 188 < length && header[188] == SYNC)

    private const val SYNC: Byte = 0x47
}
