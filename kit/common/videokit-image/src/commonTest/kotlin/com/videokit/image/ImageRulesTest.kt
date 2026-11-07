package com.videokit.image

import com.videokit.api.MediaKind
import com.videokit.api.MediaTransform
import com.videokit.api.Size
import com.videokit.core.spi.ImageEngineState
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageRenderPlan
import com.videokit.core.spi.ImageStatus
import com.videokit.core.spi.PixelRect
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ImageRulesTest {
    private val photo = ImageInfo(Size(4000, 3000), animated = false, format = "jpeg", regionDecodable = true)
    private val panorama = ImageInfo(Size(20000, 5000), animated = false, format = "jpeg", regionDecodable = true)
    private val gif = ImageInfo(Size(480, 270), animated = true, loopDurationUs = 2_000_000L, frameCount = 20, format = "gif")

    @Test
    fun fitNeverUpscales() {
        assertEquals(Size(480, 270), ImageRules.fitWithin(Size(480, 270), Size(1920, 1080)))
        assertEquals(Size(1440, 1080), ImageRules.fitWithin(Size(4000, 3000), Size(1920, 1080)))
        assertEquals(Size(4096, 1024), ImageRules.textureSizeFor(Size(20000, 5000)))
    }

    @Test
    fun wholeImageIsDecodedAtTheTargetNotTheOriginalSize() {
        val plan = ImageRules.plan(photo, Size(1920, 1080), MediaTransform(), ImageRules.MAX_SESSION_BYTES)
        assertEquals(Size(1440, 1080), plan.decodeSize)
        assertEquals(4, plan.baseSampleSize)
        assertTrue(plan.tiles.isEmpty(), "no tiles without zoom")
        // Small images are decoded at their own size.
        assertEquals(Size(480, 270), ImageRules.plan(gif, Size(1920, 1080), MediaTransform(), ImageRules.MAX_SESSION_BYTES).decodeSize)
    }

    @Test
    fun regionDecodableImagesKeepTheBaseNearDisplaySize() {
        val plan = ImageRules.plan(panorama, ImageRules.textureSizeFor(panorama.size), MediaTransform(), ImageRules.MAX_SESSION_BYTES)
        assertEquals(Size(2048, 512), plan.decodeSize)
    }

    @Test
    fun quotaDegradesTheSampling() {
        val target = Size(1920, 1080)
        val full = ImageRules.plan(photo, target, MediaTransform(), ImageRules.MAX_SESSION_BYTES)
        val small = ImageRules.plan(photo, target, MediaTransform(), quotaBytes = 1_000_000L)
        assertTrue(ImageRules.baseBytes(photo, small.decodeSize) <= 1_000_000L, "degraded decode fits: ${small.decodeSize}")
        assertTrue(small.baseSampleSize > full.baseSampleSize, "degraded sample ${small.baseSampleSize}")
        // Never below the minimum side.
        val tiny = ImageRules.plan(photo, target, MediaTransform(), quotaBytes = 1L)
        assertTrue(maxOf(tiny.decodeSize.width, tiny.decodeSize.height) >= ImageRules.MIN_DECODE_SIDE / 2)
    }

    @Test
    fun zoomAddsTilesOfTheVisibleRegionWithinTheQuota() {
        val target = ImageRules.textureSizeFor(panorama.size)
        val plan = ImageRules.plan(panorama, target, MediaTransform(scale = 4f), ImageRules.MAX_SESSION_BYTES)
        assertTrue(plan.tiles.isNotEmpty(), "tiles when zoomed")
        val sample = plan.tiles.first().sampleSize
        assertTrue(sample < plan.baseSampleSize, "tiles $sample finer than base ${plan.baseSampleSize}")
        // Not finer than the texture can show.
        assertTrue(sample >= ImageRules.ceilPowerOfTwo(20000.0 / 4096))
        val visible = ImageRules.visibleRegion(panorama.size, MediaTransform(scale = 4f))
        plan.tiles.forEach { tile ->
            assertTrue(tile.region.right > visible.left && tile.region.left < visible.right, "tile $tile outside $visible")
        }
        assertTrue(ImageRules.planBytes(panorama, plan) <= ImageRules.MAX_SESSION_BYTES)
        // A quota that only fits the base: no tiles.
        val baseOnly = ImageRules.baseBytes(panorama, plan.decodeSize)
        assertTrue(ImageRules.plan(panorama, target, MediaTransform(scale = 4f), baseOnly).tiles.isEmpty())
        // Animated and not region decodable images never tile.
        assertTrue(ImageRules.plan(gif, Size(1920, 1080), MediaTransform(scale = 4f), ImageRules.MAX_SESSION_BYTES).tiles.isEmpty())
    }

    @Test
    fun visibleRegionFollowsPanAndRotation() {
        val size = Size(1000, 1000)
        assertEquals(PixelRect(0, 0, 1000, 1000), ImageRules.visibleRegion(size, MediaTransform()))
        assertEquals(PixelRect(250, 250, 750, 750), ImageRules.visibleRegion(size, MediaTransform(scale = 2f)))
        // Pan right by half the content: the left part becomes visible (mini map: centre = 0.5 - pan / scale).
        assertEquals(PixelRect(0, 250, 500, 750), ImageRules.visibleRegion(size, MediaTransform(scale = 2f, panX = 0.5f)))
        // Rotated by 180°, the same pan shows the right part of the image.
        assertEquals(
            PixelRect(500, 250, 1000, 750),
            ImageRules.visibleRegion(size, MediaTransform(scale = 2f, panX = 0.5f, rotationDeg = 180)),
        )
    }

    @Test
    fun tileGridIsAlignedAndClipped() {
        val tiles = ImageRules.tilesFor(Size(1200, 700), PixelRect(100, 100, 1100, 600), sampleSize = 1)
        assertEquals(6, tiles.size)
        assertEquals(PixelRect(1024, 512, 1200, 700), tiles.last().region)
    }

    @Test
    fun reservationAndDegradation() {
        val wanted = ImageRules.reservationFor(photo)
        assertTrue(wanted <= ImageRules.MAX_SESSION_BYTES)
        var bytes: Long? = wanted
        var steps = 0
        while (bytes != null) {
            bytes = ImageRules.degradedReservation(photo, bytes)
            steps++
        }
        assertTrue(steps in 2..10, "degradation ends: $steps steps")
    }

    @Test
    fun kindDetailsAndMediaInfo() {
        assertEquals(MediaKind.IMAGE_ANIMATED, ImageRules.kindOf(MediaKind.IMAGE_UNKNOWN, gif))
        assertEquals(MediaKind.IMAGE_STATIC, ImageRules.kindOf(MediaKind.IMAGE_UNKNOWN, photo))
        val plan = ImageRenderPlan(Size(1440, 1080), 4)
        val details = ImageRules.detailsOf(photo, ImageEngineState(ImageStatus.READY, decodedBytes = 42L, plan = plan))
        assertEquals(1, details.frameCount)
        assertEquals(42L, details.decodedBytes)
        assertEquals(4, details.sampleSize)
        assertEquals(20, ImageRules.detailsOf(gif, ImageEngineState(ImageStatus.OPENED)).frameCount)
        val info = ImageRules.mediaInfoOf(gif)
        assertEquals("gif", info.container)
        assertEquals(2_000_000L, info.durationUs)
        assertEquals(480, info.width)
    }

    @Test
    fun powersOfTwo() {
        assertEquals(1, ImageRules.ceilPowerOfTwo(0.5))
        assertEquals(4, ImageRules.ceilPowerOfTwo(2.8))
        assertEquals(2, ImageRules.floorPowerOfTwo(2.8))
        assertEquals(1, ImageRules.floorPowerOfTwo(0.3))
    }
}
