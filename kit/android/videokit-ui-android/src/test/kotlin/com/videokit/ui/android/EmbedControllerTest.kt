package com.videokit.ui.android

import android.content.ContextWrapper
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.api.VideoKitConfig
import com.videokit.testkit.FakeResourceBudget
import com.videokit.testkit.FakeVideoKit
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.ui.android.gen.EmbedContentMsg
import com.videokit.ui.android.gen.EmbedSurfaceKind
import com.videokit.ui.android.gen.EmbedThemeMsg
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test

/** The native side of the embed channel (14 §9.2), on the JVM without a Flutter engine. */
class EmbedControllerTest {
    private class RecordingApi : EmbedFlutterApi {
        val calls = mutableListOf<String>()

        override suspend fun showContent(content: EmbedContentMsg) {
            calls += "show:${content.kind}:${content.sessionId}"
        }

        override suspend fun setTheme(theme: EmbedThemeMsg?) {
            calls += "theme:${theme?.brightness}"
        }

        override suspend fun navigationResult(requestId: Long, result: String) {
            calls += "nav:$requestId:$result"
        }

        override suspend fun setStrings(strings: Map<String, String>) {
            calls += "strings:${strings.size}"
        }
    }

    private val api = RecordingApi()
    private val controller = EmbedController(
        api,
        CoroutineScope(Dispatchers.Unconfined),
        VideoKitThemeOverrides(EmbedBrightness.DARK, mapOf("color.accent" to 0xFF2563EB.toInt())),
        mapOf("player.play" to "播放"),
    )

    @Test
    fun contentSetBeforeAttachIsPulledNotPushed() {
        controller.show(EmbedController.player("s-1", PlayerEmbedOptions(autoHideControlsMs = 5_000)))
        assertTrue(api.calls.isEmpty())
        val start = controller.attach(1)
        assertEquals(EMBED_PROTOCOL_VERSION, start.protocolVersion)
        assertEquals(EmbedSurfaceKind.PLAYER, start.content?.kind)
        assertEquals("s-1", start.content?.sessionId)
        assertEquals(5_000L, start.content?.playerOptions?.autoHideControlsMs)
        assertEquals("DARK", start.theme?.brightness)
        // ARGB travels as an unsigned 32-bit value.
        assertEquals(0xFF2563EBL, start.theme?.colors?.get("color.accent"))
        assertEquals("播放", start.strings["player.play"])
    }

    @Test
    fun changesAfterAttachArePushed() {
        controller.attach(1)
        controller.show(EmbedController.imageViewer("s-2"))
        controller.setTheme(null)
        controller.setStrings(emptyMap())
        assertEquals(listOf("show:IMAGE_VIEWER:s-2", "theme:null", "strings:0"), api.calls)
    }

    @Test
    fun navigationWithoutListenerOrUnknownDirectionIsUnavailable() {
        controller.requestNavigation(1, "NEXT")
        controller.listener = object : VideoKitEmbedListener {
            override suspend fun onNavigationRequested(direction: NavigationDirection) = NavigationResult.ACCEPTED
        }
        controller.requestNavigation(2, "SIDEWAYS")
        controller.requestNavigation(3, "PREVIOUS")
        assertEquals(listOf("nav:1:UNAVAILABLE", "nav:2:UNAVAILABLE", "nav:3:ACCEPTED"), api.calls)
    }

    @Test
    fun failingNavigationListenerAnswersFailed() {
        controller.listener = object : VideoKitEmbedListener {
            override suspend fun onNavigationRequested(direction: NavigationDirection): NavigationResult = error("host bug")
        }
        controller.requestNavigation(7, "NEXT")
        assertEquals(listOf("nav:7:FAILED"), api.calls)
    }

    @Test
    fun multiViewContentCarriesAllSessions() {
        controller.show(EmbedController.multiView(listOf("a", "b", "c", "d")))
        val start = controller.attach(1)
        assertEquals(EmbedSurfaceKind.MULTI_VIEW, start.content?.kind)
        assertEquals(listOf("a", "b", "c", "d"), start.content?.sessionIds)
    }

    @Test
    fun uiRequestsReachTheListenerAndPanelHook() {
        val events = mutableListOf<String>()
        controller.onControlsChanged = { visible, ms -> events += "panel:$visible:$ms" }
        controller.onDisplayed = { events += "displayed:$it" }
        controller.listener = object : VideoKitEmbedListener {
            override fun onControlsVisibilityChanged(visible: Boolean) {
                events += "controls:$visible"
            }

            override fun onFullscreenRequested(fullscreen: Boolean) {
                events += "fullscreen:$fullscreen"
            }

            override fun onEditRequested(sessionId: String) {
                events += "edit:$sessionId"
            }
        }
        controller.onControlsVisibilityChanged(false, 200)
        controller.onFullscreenRequested(true)
        controller.onEditRequested("s-3")
        controller.onContentDisplayed(EmbedSurfaceKind.EDITOR)
        assertEquals(listOf("panel:false:200", "controls:false", "fullscreen:true", "edit:s-3", "displayed:EDITOR"), events)
    }

    @Test
    fun hostKitBackendSharesTheHostInstance() {
        val kit = FakeVideoKit(RecordingHostCallbacks())
        val backend = HostKitBackend(kit)
        assertFalse(backend.ownsKits)
        assertTrue(backend.isDemo)
        assertSame(kit, backend.create(object : ContextWrapper(null) {}, kitConfig()))
        assertNull(backend.demoSink())
        kit.close()
    }

    private fun kitConfig() = VideoKitConfig(
        hostCallbacks = RecordingHostCallbacks(),
        resourceBudget = FakeResourceBudget(),
    )
}
