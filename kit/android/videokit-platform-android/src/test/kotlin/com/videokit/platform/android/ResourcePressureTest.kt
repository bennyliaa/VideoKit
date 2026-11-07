package com.videokit.platform.android

import android.os.PowerManager
import com.videokit.core.runtime.ResourcePressure
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** System signals → budget pressure (07 §2–§3). */
class ResourcePressureTest {
    @Test
    fun thermalStatus() {
        assertEquals(ResourcePressure.NORMAL, AndroidResourcePressure.thermalPressure(PowerManager.THERMAL_STATUS_NONE))
        assertEquals(ResourcePressure.NORMAL, AndroidResourcePressure.thermalPressure(PowerManager.THERMAL_STATUS_LIGHT))
        assertEquals(ResourcePressure.ELEVATED, AndroidResourcePressure.thermalPressure(PowerManager.THERMAL_STATUS_MODERATE))
        assertEquals(ResourcePressure.CRITICAL, AndroidResourcePressure.thermalPressure(PowerManager.THERMAL_STATUS_SEVERE))
        assertEquals(ResourcePressure.CRITICAL, AndroidResourcePressure.thermalPressure(PowerManager.THERMAL_STATUS_SHUTDOWN))
    }

    @Test
    fun memoryTrimLevels() {
        assertEquals(ResourcePressure.ELEVATED, AndroidResourcePressure.memoryPressure(10))
        assertEquals(ResourcePressure.CRITICAL, AndroidResourcePressure.memoryPressure(15))
        // UI hidden and background levels are not pressure on the running playback.
        assertNull(AndroidResourcePressure.memoryPressure(20))
        assertNull(AndroidResourcePressure.memoryPressure(40))
    }
}
