package com.videokit.api.android

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ErrorCode
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.MediaKind
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceBudget
import com.videokit.api.ResourceReport
import com.videokit.api.ResourceRequest
import com.videokit.api.VideoKitApiVersion
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitStableError
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.util.Locale

class AndroidTypesTest {
    @get:Rule
    val temp = TemporaryFolder()

    @Test
    fun factoryReportsMissingImplementation() {
        val callbacks = object : VideoKitHostCallbacks {
            override suspend fun onHostActionRequested(request: HostActionRequest) = HostActionResult(HostActionStatus.COMPLETED)

            override suspend fun onNavigationRequested(request: NavigationRequest) = NavigationResult.UNAVAILABLE

            override suspend fun onPlaybackSnapshot(snapshot: VideoKitPlaybackState) = Unit

            override suspend fun onPlaybackEvent(event: VideoKitPlaybackEvent) = Unit

            override suspend fun onControlsVisibilityChanged(sessionId: String, visible: Boolean) = Unit

            override suspend fun onSourceReleased(sessionId: String, mediaToken: String) = Unit

            override suspend fun onRecoverableError(error: VideoKitStableError) = RecoveryDecision.KEEP_ERROR

            override suspend fun onFatalSessionError(error: VideoKitStableError) = Unit
        }
        val budget = object : ResourceBudget {
            override suspend fun reserve(request: ResourceRequest): ReservationResult =
                ReservationResult.Denied("none", DegradeSuggestion.NONE)

            override fun snapshot() = ResourceReport(emptyList())
        }
        // android.content.Context is abstract; the mockable android.jar allows an anonymous subclass on the JVM.
        val context = object : android.content.ContextWrapper(null) {}
        try {
            VideoKitFactory.create(context, VideoKitConfig(callbacks, budget))
            fail("expected IllegalStateException")
        } catch (expected: IllegalStateException) {
            assertTrue(expected.message!!.startsWith("VIDEOKIT_IMPLEMENTATION_UNAVAILABLE"))
        }
    }

    @Test
    fun androidSurfaceIsARenderTarget() {
        val target = AndroidSurface(android.view.Surface(android.graphics.SurfaceTexture(0)), 640, 360)
        assertEquals(640, target.width)
        assertEquals("AndroidSurface(640x360)", target.toString())
    }

    /** 13 §3.1: machine formatting does not depend on the device language. */
    @Test
    fun formattingIsIndependentOfTheDefaultLocale() {
        val original = Locale.getDefault()
        try {
            listOf(Locale.forLanguageTag("tr-TR"), Locale.forLanguageTag("ar-EG"), Locale.SIMPLIFIED_CHINESE).forEach { locale ->
                Locale.setDefault(locale)
                // Turkish lowercases "I" to a dotless i when a locale-sensitive API is used.
                val source = MediaSources.fromFile(temp.newFile("clip-$locale.AVI"), "t", MediaKind.VIDEO)
                assertEquals("avi", source.extension)
                assertEquals("1.0.0", VideoKitApiVersion.CURRENT.toString())
                assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorCode.fromWireName("SOURCE_IDLE"))
                assertEquals(ErrorCode.SOURCE_DISCONNECTED, ErrorCode.fromWireName("SOURCE_DISCONNECTED"))
            }
        } finally {
            Locale.setDefault(original)
        }
    }
}
