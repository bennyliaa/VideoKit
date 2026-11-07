package com.videokit.testkit

import com.videokit.api.ThumbnailResult

/**
 * Demo thumbnail of the Fake (04A P1): a real 32×18 JPEG (blue with an orange block) so hosts and UIs can decode and
 * show it. Platform-independent code cannot encode JPEG; Android test code installs a test-pattern encoder instead
 * (`AndroidTestPattern.install`).
 */
public object DemoThumbnail {
    /** Width of [bytes]. */
    public const val WIDTH: Int = 32

    /** Height of [bytes]. */
    public const val HEIGHT: Int = 18

    private const val HEX: String =
        "ffd8ffe000104a46494600010101006000600000ffdb0043000302020302020303030304030304050805050404050a07" +
            "0706080c0a0c0c0b0a0b0b0d0e12100d0e110e0b0b1016101113141515150c0f171816141812141514ffdb0043010304" +
            "0405040509050509140d0b0d141414141414141414141414141414141414141414141414141414141414141414141414" +
            "1414141414141414141414141414ffc00011080012002003012200021101031101ffc4001f0000010501010101010100" +
            "000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d010203000411051221" +
            "31410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a" +
            "434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a9293949596979899" +
            "9aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1" +
            "f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100" +
            "020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f015" +
            "6272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a63646566676869" +
            "6a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4" +
            "c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00f2" +
            "aa28a2bfb40fc3cfa028af0fff00848755ff00a09de7fe043ff8d1ff00090eabff00413bcffc087ff1afe22ff897fccf" +
            "fe83a9ff00e0323fac3fe233603fe8127ff8144cfa28a2bfb74fe4f0a28a2803ffd9"

    /** The JPEG bytes (a fresh copy per call). */
    public val bytes: ByteArray get() = ByteArray(HEX.length / 2) { HEX.substring(it * 2, it * 2 + 2).toInt(16).toByte() }

    /** The demo thumbnail as a capture result, whatever size was requested. */
    public fun captured(): ThumbnailResult.Captured = ThumbnailResult.Captured(bytes, WIDTH, HEIGHT)
}
