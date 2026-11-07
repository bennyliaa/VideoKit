package com.videokit.testkit.android

import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.android.AndroidSurface
import com.videokit.testkit.FakeVideoKitOptions
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class AndroidTestPatternTest {
    @Test
    fun factoryAcceptsOnlyAndroidSurfaces() {
        // The mockable android.jar provides stub Surface objects on the JVM; drawing itself needs a device (NOT_RUN).
        val android = AndroidSurface(android.view.Surface(android.graphics.SurfaceTexture(0)), 320, 180)
        assertTrue(AndroidTestPattern.targetFactory(android) is SurfaceTestPatternTarget)
        val foreign = object : VideoKitSurfaceTarget {
            override val width: Int = 1
            override val height: Int = 1
        }
        assertNull(AndroidTestPattern.targetFactory(foreign))
    }

    @Test
    fun installSetsTheFactory() {
        val options = AndroidTestPattern.install(FakeVideoKitOptions())
        val android = AndroidSurface(android.view.Surface(android.graphics.SurfaceTexture(0)), 320, 180)
        assertNotNull(options.patternTargetFactory(android))
        assertNull(FakeVideoKitOptions().patternTargetFactory(android))
    }
}
