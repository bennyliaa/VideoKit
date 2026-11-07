package com.videokit.image

/** Frame count and loop length of an animated image, from its container (04A L2; the platform decoders hide them). */
public data class AnimationTiming(
    /** Number of frames. */
    val frameCount: Int,
    /** Duration of one loop. */
    val loopDurationUs: Long,
    /** Loop count stored in the file (0 = forever), if present. */
    val storedLoopCount: Int? = null,
)

/**
 * Reads [AnimationTiming] from GIF and animated WebP data without decoding pixels. Frame delays of 0 or 10 ms are
 * shown as 100 ms, like the common decoders do; other formats (animated AVIF/HEIF) answer `null`.
 */
public object AnimationHeaders {
    /** Delay used for frames that declare 0 or 10 ms. */
    public const val MIN_DELAY_FALLBACK_US: Long = 100_000L

    /** Timing of [data], or `null` when it is not a parsable GIF / animated WebP or has no frames. */
    public fun parse(data: ByteArray): AnimationTiming? = try {
        when {
            data.startsWith("GIF8") -> gif(data)
            data.size >= 12 && data.startsWith("RIFF") && data.matches(8, "WEBP") -> webp(data)
            else -> null
        }
    } catch (_: IndexOutOfBoundsException) {
        null
    }

    private fun gif(data: ByteArray): AnimationTiming? {
        var pos = 6
        val flags = data.u8(pos + 4)
        pos += 7
        if (flags and 0x80 != 0) pos += 3 * (1 shl ((flags and 0x07) + 1))
        var frames = 0
        var totalUs = 0L
        var delayUs = 0L
        var loops: Int? = null
        while (pos < data.size) {
            when (data.u8(pos)) {
                0x21 -> {
                    val label = data.u8(pos + 1)
                    pos += 2
                    if (label == 0xF9 && data.u8(pos) >= 4) delayUs = data.u16le(pos + 2) * 10_000L
                    if (label == 0xFF && data.u8(pos) == 11 && data.matches(pos + 1, "NETSCAPE2.0")) {
                        val sub = pos + 12
                        if (data.u8(sub) >= 3 && data.u8(sub + 1) == 1) loops = data.u16le(sub + 2)
                    }
                    pos = skipSubBlocks(data, pos)
                }

                0x2C -> {
                    frames++
                    totalUs += if (delayUs <= 10_000L) MIN_DELAY_FALLBACK_US else delayUs
                    delayUs = 0L
                    val packed = data.u8(pos + 9)
                    pos += 10
                    if (packed and 0x80 != 0) pos += 3 * (1 shl ((packed and 0x07) + 1))
                    pos += 1 // LZW minimum code size
                    pos = skipSubBlocks(data, pos)
                }

                0x3B -> break

                else -> return null
            }
        }
        return if (frames > 0) AnimationTiming(frames, totalUs, loops) else null
    }

    private fun skipSubBlocks(data: ByteArray, start: Int): Int {
        var pos = start
        while (true) {
            val size = data.u8(pos)
            pos += 1 + size
            if (size == 0) return pos
        }
    }

    private fun webp(data: ByteArray): AnimationTiming? {
        var pos = 12
        var frames = 0
        var totalUs = 0L
        var loops: Int? = null
        while (pos + 8 <= data.size) {
            val size = data.u32le(pos + 4)
            val payload = pos + 8
            when {
                data.matches(pos, "ANIM") -> loops = data.u16le(payload + 4)

                data.matches(pos, "ANMF") -> {
                    frames++
                    val ms = data.u8(payload + 12) or (data.u8(payload + 13) shl 8) or (data.u8(payload + 14) shl 16)
                    val us = ms * 1_000L
                    totalUs += if (us <= 10_000L) MIN_DELAY_FALLBACK_US else us
                }
            }
            if (size < 0) return null
            pos = payload + size + (size and 1)
        }
        return if (frames > 0) AnimationTiming(frames, totalUs, loops) else null
    }

    private fun ByteArray.u8(at: Int): Int = this[at].toInt() and 0xFF

    private fun ByteArray.u16le(at: Int): Int = u8(at) or (u8(at + 1) shl 8)

    private fun ByteArray.u32le(at: Int): Int = u16le(at) or (u16le(at + 2) shl 16)

    private fun ByteArray.matches(at: Int, text: String): Boolean =
        at + text.length <= size && text.indices.all { this[at + it] == text[it].code.toByte() }

    private fun ByteArray.startsWith(text: String): Boolean = matches(0, text)
}
