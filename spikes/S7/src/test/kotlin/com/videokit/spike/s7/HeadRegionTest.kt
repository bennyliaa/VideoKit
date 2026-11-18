package com.videokit.spike.s7

import java.awt.image.BufferedImage
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

class HeadRegionTest {
    @Test
    fun hostPngBoundsAreTheOpaquePixels() {
        val image = BufferedImage(20, 10, BufferedImage.TYPE_INT_ARGB)
        image.setRGB(3, 2, 0xFF000000.toInt())
        image.setRGB(15, 7, 0x80FFFFFF.toInt())
        image.setRGB(18, 9, 0x05FFFFFF) // below the threshold: fringe, ignored
        assertEquals(Rect(3, 2, 13, 6), HostPng.opaqueBounds(image))
        assertNull(HostPng.opaqueBounds(BufferedImage(4, 4, BufferedImage.TYPE_INT_ARGB)), "fully transparent")
        assertNull(HostPng.opaqueBounds(BufferedImage(4, 4, BufferedImage.TYPE_INT_RGB)), "no alpha channel")
    }

    @Test
    fun syntheticGroundTruthRoundTripsThroughTheHostPath() {
        val sample = SyntheticSet.sample(SyntheticSet.Background.BUSY_STRIPES, SyntheticSet.Hair.FLYAWAY, 1)
        val bounds = HostPng.opaqueBounds(SyntheticSet.asRgba(sample))!!
        assertTrue(bounds.iou(sample.head) > 0.95, "$bounds vs ${sample.head}")
    }

    @Test
    fun headExpansionCoversTheFaceAndStaysInTheImage() {
        val face = Rect(100, 100, 40, 50)
        val head = HeadExpansion().headOf(face, 256, 320)
        assertTrue(head.x <= face.x && head.right >= face.right && head.y < face.y && head.bottom >= face.bottom)
        val clipped = HeadExpansion().headOf(Rect(0, 0, 40, 50), 256, 320)
        assertEquals(0, clipped.x)
        assertEquals(0, clipped.y)
    }

    @Test
    fun perfectMatteScoresZero() {
        val sample = SyntheticSet.sample(SyntheticSet.Background.FLAT, SyntheticSet.Hair.SHORT, 1)
        val scores = MattingMetrics.score(sample.alpha.copyOf(), sample.alpha, SyntheticSet.W, SyntheticSet.H, sample.hair)
        assertEquals(0.0, scores.sad)
        assertEquals(0.0, scores.backgroundResidue)
        assertEquals(0.0, scores.foregroundLoss)
    }
}
