package com.videokit.ui.android

import android.content.Context
import android.os.SystemClock
import android.util.AttributeSet
import android.view.Gravity
import android.view.ViewGroup
import android.widget.FrameLayout
import com.videokit.api.NavigationDirection
import com.videokit.api.VideoKitSession
import com.videokit.ui.android.gen.EmbedContentMsg
import io.flutter.embedding.android.FlutterSurfaceView
import io.flutter.embedding.android.FlutterView
import io.flutter.embedding.engine.renderer.FlutterUiDisplayListener

/**
 * VideoKit UI as a plain View (14 §9.1), for hosts that do not use Fragments (list items, custom layouts).
 *
 * The view owns one embed engine from the moment content is requested until [destroy]; attaching to / detaching
 * from the window only resumes / pauses it. Unlike the Fragments it is not re-created by the system: the host keeps
 * the view (and calls [destroy]) itself. The shown session stays owned by the host.
 */
public class VideoKitFlutterView @JvmOverloads constructor(context: Context, attrs: AttributeSet? = null) : FrameLayout(context, attrs) {
    /** UI-level callbacks. */
    public var listener: VideoKitEmbedListener? = null

    /** Container for native host panels, at the bottom over the Flutter UI. */
    public val hostPanelContainer: FrameLayout = FrameLayout(context)

    private var embed: EmbedEngine? = null
    private var flutterView: FlutterView? = null
    private var requestedAt = 0L
    private var kind = EmbedContentKind.PLAYER
    private var firstFrameReported = false
    private val displayListener = object : FlutterUiDisplayListener {
        override fun onFlutterUiDisplayed() = reportFirstFrame()

        override fun onFlutterUiNoLongerDisplayed() = Unit
    }

    /** Shows the player for [session] (shared automatically). */
    public fun showPlayer(session: VideoKitSession, options: PlayerEmbedOptions = PlayerEmbedOptions()) {
        VideoKitFlutter.share(session)
        show(EmbedContentKind.PLAYER) { EmbedController.player(session.sessionId, options) }
    }

    /** Shows the image viewer for a shared session. */
    public fun showImageViewer(sessionId: String) {
        show(EmbedContentKind.IMAGE_VIEWER) { EmbedController.imageViewer(sessionId) }
    }

    /**
     * Shows [sessions] in one engine as a multi-view grid (`VideoKitSlotGrid`); the single-engine side of the
     * 14 §9.3 multi-instance memory comparison.
     */
    public fun showMultiView(sessions: List<VideoKitSession>) {
        sessions.forEach(VideoKitFlutter::share)
        show(EmbedContentKind.MULTI_VIEW) { EmbedController.multiView(sessions.map { it.sessionId }) }
    }

    /** Releases the engine of this view. The view can show content again afterwards (with a new engine). */
    public fun destroy() {
        detachFlutterView()
        embed?.let { engine ->
            engine.engine.renderer.removeIsDisplayingFlutterUiListener(displayListener)
            VideoKitFlutter.requireEngines().destroy(engine.engineId)
        }
        embed = null
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        embed?.let { attachFlutterView(it) }
    }

    override fun onDetachedFromWindow() {
        embed?.engine?.lifecycleChannel?.appIsPaused()
        detachFlutterView()
        super.onDetachedFromWindow()
    }

    private inline fun show(next: EmbedContentKind, content: () -> EmbedContentMsg) {
        kind = next
        firstFrameReported = false
        requestedAt = SystemClock.elapsedRealtime()
        val engine = embed ?: VideoKitFlutter.requireEngines().acquire().also { acquired ->
            embed = acquired
            bindController(acquired)
            if (isAttachedToWindow) attachFlutterView(acquired)
        }
        engine.controller.show(content())
    }

    private fun bindController(engine: EmbedEngine) {
        engine.controller.listener = object : VideoKitEmbedListener {
            override fun onControlsVisibilityChanged(visible: Boolean) {
                listener?.onControlsVisibilityChanged(visible)
            }

            override suspend fun onNavigationRequested(direction: NavigationDirection) =
                listener?.onNavigationRequested(direction) ?: super.onNavigationRequested(direction)

            override fun onFullscreenRequested(fullscreen: Boolean) {
                listener?.onFullscreenRequested(fullscreen)
            }

            override fun onEditRequested(sessionId: String) {
                listener?.onEditRequested(sessionId)
            }
        }
        engine.controller.onControlsChanged = { visible, animationMs -> HostPanels.animate(hostPanelContainer, visible, animationMs) }
        engine.controller.onDisplayed = { reportFirstFrame() }
        engine.engine.renderer.addIsDisplayingFlutterUiListener(displayListener)
    }

    private fun attachFlutterView(engine: EmbedEngine) {
        if (flutterView != null) return
        // Opaque surface: the player background is black, no transparent composition (14 §9.2).
        val view = FlutterView(context, FlutterSurfaceView(context, false))
        addView(view, 0, LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        if (hostPanelContainer.parent == null) {
            addView(
                hostPanelContainer,
                LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM),
            )
        }
        view.attachToFlutterEngine(engine.engine)
        flutterView = view
        engine.engine.lifecycleChannel.appIsResumed()
    }

    private fun detachFlutterView() {
        val view = flutterView ?: return
        view.detachFromFlutterEngine()
        removeView(view)
        flutterView = null
    }

    private fun reportFirstFrame() {
        if (firstFrameReported) return
        firstFrameReported = true
        listener?.onFirstFrame(kind, SystemClock.elapsedRealtime() - requestedAt, embed?.prewarmed == true)
    }
}
