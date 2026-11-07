package com.videokit.ui.android

import android.os.Bundle
import android.os.SystemClock
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentContainerView
import com.videokit.api.NavigationDirection
import com.videokit.api.VideoKitSession
import com.videokit.ui.android.gen.EmbedContentMsg
import io.flutter.embedding.android.FlutterFragment
import io.flutter.embedding.android.RenderMode
import io.flutter.embedding.android.TransparencyMode
import io.flutter.embedding.engine.renderer.FlutterUiDisplayListener

/**
 * Common base of the embed fragments (14 §9.1, §9.2). The root is a [FrameLayout] with the Flutter UI (a child
 * [FlutterFragment] on a cached engine, opaque surface) and [hostPanelContainer] for native host panels, which the
 * bridge shows and hides together with the VideoKit controls.
 *
 * Engine lifetime: one engine per fragment, kept across configuration changes (the Dart UI state and the
 * host-owned session survive rotation) and destroyed when the fragment is finally removed. The session is never
 * released here.
 */
public abstract class VideoKitEmbedFragment : Fragment() {
    /** UI-level callbacks; falls back to a parent fragment or the activity implementing [VideoKitEmbedListener]. */
    public var listener: VideoKitEmbedListener? = null

    /** Container for native host panels (e.g. a neighbour strip), laid out at the bottom over the Flutter UI. */
    public var hostPanelContainer: FrameLayout? = null
        private set

    private var embed: EmbedEngine? = null
    private var engineId: String? = null
    private var firstFrameReported = false
    private val displayListener = object : FlutterUiDisplayListener {
        override fun onFlutterUiDisplayed() = reportFirstFrame()

        override fun onFlutterUiNoLongerDisplayed() = Unit
    }

    /** Content of this embed. */
    internal abstract fun content(): EmbedContentMsg

    /** Kind of this embed. */
    internal abstract val kind: EmbedContentKind

    override fun onCreate(savedInstanceState: Bundle?) {
        // Resolve the engine before super.onCreate restores the child FlutterFragment, which looks it up by id.
        val engines = VideoKitFlutter.requireEngines()
        val saved = savedInstanceState?.getString(STATE_ENGINE_ID)
        val resolved = if (saved != null) engines.restore(saved) else engines.acquire()
        embed = resolved
        engineId = resolved.engineId
        firstFrameReported = savedInstanceState?.getBoolean(STATE_FIRST_FRAME) ?: false
        super.onCreate(savedInstanceState)
        bindController(resolved)
        resolved.controller.show(content())
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val context = requireContext()
        val root = FrameLayout(context)
        val flutterContainer = FragmentContainerView(context).apply { id = R.id.videokit_flutter_container }
        root.addView(flutterContainer, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        val panels = FrameLayout(context)
        root.addView(
            panels,
            FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.BOTTOM),
        )
        hostPanelContainer = panels
        // A restored child FlutterFragment re-attaches to the same container id by itself.
        if (childFragmentManager.findFragmentByTag(FLUTTER_TAG) == null) {
            val flutter = FlutterFragment.withCachedEngine(requireNotNull(engineId))
                .renderMode(RenderMode.surface)
                .transparencyMode(TransparencyMode.opaque)
                .shouldAttachEngineToActivity(true)
                .destroyEngineWithFragment(false)
                .build<FlutterFragment>()
            childFragmentManager.beginTransaction().add(R.id.videokit_flutter_container, flutter, FLUTTER_TAG).commit()
        }
        return root
    }

    override fun onDestroyView() {
        hostPanelContainer = null
        super.onDestroyView()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        engineId?.let { outState.putString(STATE_ENGINE_ID, it) }
        outState.putBoolean(STATE_FIRST_FRAME, firstFrameReported)
    }

    override fun onDestroy() {
        val current = embed
        embed = null
        current?.engine?.renderer?.removeIsDisplayingFlutterUiListener(displayListener)
        current?.controller?.apply {
            listener = null
            onControlsChanged = null
            onDisplayed = null
        }
        super.onDestroy()
        // Keep the engine for the re-created fragment after a configuration change; destroy it otherwise.
        val changingConfigurations = activity?.isChangingConfigurations == true
        if (current != null && !changingConfigurations) VideoKitFlutter.requireEngines().destroy(current.engineId)
    }

    private fun bindController(engine: EmbedEngine) {
        engine.controller.listener = object : VideoKitEmbedListener {
            override fun onControlsVisibilityChanged(visible: Boolean) {
                effectiveListener()?.onControlsVisibilityChanged(visible)
            }

            override suspend fun onNavigationRequested(direction: NavigationDirection) =
                effectiveListener()?.onNavigationRequested(direction) ?: super.onNavigationRequested(direction)

            override fun onFullscreenRequested(fullscreen: Boolean) {
                effectiveListener()?.onFullscreenRequested(fullscreen)
            }

            override fun onEditRequested(sessionId: String) {
                effectiveListener()?.onEditRequested(sessionId)
            }
        }
        engine.controller.onControlsChanged = { visible, animationMs ->
            hostPanelContainer?.let { HostPanels.animate(it, visible, animationMs) }
        }
        engine.controller.onDisplayed = { reportFirstFrame() }
        engine.engine.renderer.addIsDisplayingFlutterUiListener(displayListener)
    }

    private fun reportFirstFrame() {
        if (firstFrameReported) return
        firstFrameReported = true
        val requestedAt = arguments?.getLong(ARG_REQUESTED_AT, 0L) ?: 0L
        val elapsed = if (requestedAt > 0L) SystemClock.elapsedRealtime() - requestedAt else -1L
        effectiveListener()?.onFirstFrame(kind, elapsed, embed?.prewarmed == true)
    }

    private fun effectiveListener(): VideoKitEmbedListener? =
        listener ?: parentFragment as? VideoKitEmbedListener ?: activity as? VideoKitEmbedListener

    internal companion object {
        const val ARG_SESSION_ID = "videokit.sessionId"
        const val ARG_PROJECT_ID = "videokit.projectId"
        const val ARG_OPTIONS = "videokit.options"
        const val ARG_REQUESTED_AT = "videokit.requestedAt"
        private const val STATE_ENGINE_ID = "videokit.engineId"
        private const val STATE_FIRST_FRAME = "videokit.firstFrameReported"
        private const val FLUTTER_TAG = "videokit.flutter"

        fun baseArgs(): Bundle = Bundle().apply { putLong(ARG_REQUESTED_AT, SystemClock.elapsedRealtime()) }
    }
}

/** Embedded player (UI-01) for a host-owned session (14 §9.1). */
public class VideoKitPlayerFragment : VideoKitEmbedFragment() {
    override val kind: EmbedContentKind get() = EmbedContentKind.PLAYER

    override fun content(): EmbedContentMsg = EmbedController.player(
        requireNotNull(requireArguments().getString(ARG_SESSION_ID)) { "sessionId missing" },
        PlayerEmbedOptions.fromBundle(requireArguments().getBundle(ARG_OPTIONS)),
    )

    public companion object {
        /** Player for a session already shared with [VideoKitFlutter.share]. */
        @JvmStatic
        public fun newInstance(sessionId: String, options: PlayerEmbedOptions = PlayerEmbedOptions()): VideoKitPlayerFragment =
            VideoKitPlayerFragment().apply {
                arguments = baseArgs().apply {
                    putString(ARG_SESSION_ID, sessionId)
                    putBundle(ARG_OPTIONS, options.toBundle())
                }
            }

        /** Shares [session] and returns a player for it. */
        @JvmStatic
        public fun newInstance(session: VideoKitSession, options: PlayerEmbedOptions = PlayerEmbedOptions()): VideoKitPlayerFragment {
            VideoKitFlutter.share(session)
            return newInstance(session.sessionId, options)
        }
    }
}

/** Embedded image viewer (UI-03) for a host-owned session bound to an image. */
public class VideoKitImageViewerFragment : VideoKitEmbedFragment() {
    override val kind: EmbedContentKind get() = EmbedContentKind.IMAGE_VIEWER

    override fun content(): EmbedContentMsg =
        EmbedController.imageViewer(requireNotNull(requireArguments().getString(ARG_SESSION_ID)) { "sessionId missing" })

    public companion object {
        /** Image viewer for a session already shared with [VideoKitFlutter.share]. */
        @JvmStatic
        public fun newInstance(sessionId: String): VideoKitImageViewerFragment = VideoKitImageViewerFragment().apply {
            arguments = baseArgs().apply { putString(ARG_SESSION_ID, sessionId) }
        }
    }
}

/**
 * Embedded editor (UI-06). Skeleton in M0: the edit project is created by the embedded UI from its own
 * VideoKit proxy, [projectId] is passed through for the Dart side (sharing native edit projects is not part of
 * protocol 1).
 */
public class VideoKitEditorFragment : VideoKitEmbedFragment() {
    override val kind: EmbedContentKind get() = EmbedContentKind.EDITOR

    override fun content(): EmbedContentMsg =
        EmbedController.editor(requireNotNull(requireArguments().getString(ARG_PROJECT_ID)) { "projectId missing" })

    public companion object {
        @JvmStatic
        public fun newInstance(projectId: String): VideoKitEditorFragment = VideoKitEditorFragment().apply {
            arguments = baseArgs().apply { putString(ARG_PROJECT_ID, projectId) }
        }
    }
}
