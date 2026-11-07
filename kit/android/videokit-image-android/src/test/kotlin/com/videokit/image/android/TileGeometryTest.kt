package com.videokit.image.android

import com.videokit.api.Size
import com.videokit.core.spi.PixelRect
import org.junit.Assert.assertEquals
import org.junit.Test

/** Oriented tile regions map back to the stored (un-rotated) image of BitmapRegionDecoder (15 §2.3). */
class TileGeometryTest {
    // Stored 400 × 300, so the image oriented by 90° / 270° is 300 × 400.
    private val stored = Size(400, 300)

    @Test
    fun noRotationIsIdentity() {
        val rect = PixelRect(10, 20, 110, 220)
        assertEquals(rect, TileGeometry.toStored(rect, stored, 0))
    }

    @Test
    fun rotated90() {
        // The top-left oriented corner (0..100 × 0..50) comes from the bottom-left of the stored image.
        assertEquals(PixelRect(0, 200, 50, 300), TileGeometry.toStored(PixelRect(0, 0, 100, 50), stored, 90))
    }

    @Test
    fun rotated180() {
        assertEquals(PixelRect(300, 250, 400, 300), TileGeometry.toStored(PixelRect(0, 0, 100, 50), stored, 180))
    }

    @Test
    fun rotated270() {
        // The top-left oriented corner comes from the top-right of the stored image.
        assertEquals(PixelRect(350, 0, 400, 100), TileGeometry.toStored(PixelRect(0, 0, 100, 50), stored, 270))
    }

    @Test
    fun wholeImageMapsToWholeImage() {
        listOf(90, 270).forEach { rotation ->
            assertEquals(PixelRect(0, 0, 400, 300), TileGeometry.toStored(PixelRect(0, 0, 300, 400), stored, rotation))
        }
        assertEquals(PixelRect(0, 0, 400, 300), TileGeometry.toStored(PixelRect(0, 0, 400, 300), stored, 180))
    }
}
