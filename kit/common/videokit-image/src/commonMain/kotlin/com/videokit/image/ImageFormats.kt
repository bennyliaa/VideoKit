package com.videokit.image

/**
 * Image format detection from the first bytes (06 §6.1 "读文件头识别格式"). Engines refuse unknown formats with
 * UNSUPPORTED_CONTAINER before decoding, so that a decode failure of a known format means CORRUPT_MEDIA.
 */
public object ImageFormats {
    /** JPEG. */
    public const val JPEG: String = "jpeg"

    /** PNG (and APNG). */
    public const val PNG: String = "png"

    /** GIF. */
    public const val GIF: String = "gif"

    /** WebP (static or animated). */
    public const val WEBP: String = "webp"

    /** HEIF/HEIC. */
    public const val HEIF: String = "heif"

    /** AVIF. */
    public const val AVIF: String = "avif"

    /** BMP. */
    public const val BMP: String = "bmp"

    /** Formats whose regions the platform can decode (tiles, 15 §2.3: BitmapRegionDecoder). */
    public val REGION_DECODABLE: Set<String> = setOf(JPEG, PNG, WEBP, HEIF)

    /** Bytes [sniff] needs at most. */
    public const val HEADER_BYTES: Int = 32

    /** The format of [header], or `null` when unknown. */
    public fun sniff(header: ByteArray): String? {
        fun at(index: Int) = if (index < header.size) header[index].toInt() and 0xFF else -1
        fun text(index: Int, value: String) = value.indices.all { at(index + it) == value[it].code }
        return when {
            at(0) == 0xFF && at(1) == 0xD8 && at(2) == 0xFF -> JPEG

            at(0) == 0x89 && text(1, "PNG\r\n") -> PNG

            text(0, "GIF87a") || text(0, "GIF89a") -> GIF

            text(0, "RIFF") && text(8, "WEBP") -> WEBP

            text(0, "BM") && header.size >= 14 -> BMP

            text(4, "ftyp") -> {
                // Major brand, then the compatible brands (an AVIF may declare mif1 first and avif later).
                val brands = (8 until minOf(header.size, HEADER_BYTES) - 3 step 4).filter { it != 12 }.map { index ->
                    String(CharArray(4) { at(index + it).coerceAtLeast(0).toChar() })
                }
                when {
                    brands.any { it == "avif" || it == "avis" } -> AVIF
                    brands.any { it in HEIF_BRANDS } -> HEIF
                    else -> null
                }
            }

            else -> null
        }
    }

    private val HEIF_BRANDS = setOf("heic", "heix", "hevc", "hevx", "heim", "heis", "mif1", "msf1")
}
