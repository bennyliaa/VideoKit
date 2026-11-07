package com.videokit.ui.android

import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.ui.android.gen.EmbedContentMsg
import com.videokit.ui.android.gen.EmbedStartMsg
import com.videokit.ui.android.gen.EmbedSurfaceKind
import com.videokit.ui.android.gen.EmbedThemeMsg
import com.videokit.ui.android.gen.PlayerEmbedOptionsMsg
import com.videokit.ui.android.gen.VideoKitEmbedFlutterApi
import com.videokit.ui.android.gen.VideoKitEmbedHostApi
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch

/** Embed protocol version of the native side (embed_messages.dart). */
internal const val EMBED_PROTOCOL_VERSION: Long = 1L

/**
 * Native side of the embed channel of one engine (14 §9.2). All methods run on the main thread (channel handlers
 * and the Fragment / View that owns the engine). The Dart side pulls the current configuration with `attach`, so
 * content set before the Dart entry point listens is not lost; later changes are pushed.
 */
internal class EmbedController(
    private val flutterApi: EmbedFlutterApi,
    private val scope: CoroutineScope,
    initialTheme: VideoKitThemeOverrides?,
    initialStrings: Map<String, String>,
) : VideoKitEmbedHostApi {
    /** What the Fragment / View currently wants to show. */
    var content: EmbedContentMsg? = null
        private set

    private var theme: EmbedThemeMsg? = initialTheme?.toMsg()
    private var strings: Map<String, String> = initialStrings
    private var attached = false

    /** Forwarding target; set by the owning Fragment / View. */
    var listener: VideoKitEmbedListener? = null

    /** Called before [listener] with the panel animation duration (host panel container sync, 14 §9.2). */
    var onControlsChanged: ((visible: Boolean, animationMs: Long) -> Unit)? = null

    /** Called once per content when Dart reports its first frame. */
    var onDisplayed: ((EmbedContentKind) -> Unit)? = null

    fun show(next: EmbedContentMsg) {
        content = next
        if (attached) scope.launch { runCatching { flutterApi.showContent(next) } }
    }

    fun setTheme(overrides: VideoKitThemeOverrides?) {
        val msg = overrides?.toMsg()
        theme = msg
        if (attached) scope.launch { runCatching { flutterApi.setTheme(msg) } }
    }

    fun setStrings(overrides: Map<String, String>) {
        strings = overrides
        if (attached) scope.launch { runCatching { flutterApi.setStrings(overrides) } }
    }

    // ------------------------------------------------------------------ Dart → native

    override fun attach(dartProtocolVersion: Long): EmbedStartMsg {
        attached = true
        return EmbedStartMsg(EMBED_PROTOCOL_VERSION, content, theme, strings)
    }

    override fun onControlsVisibilityChanged(visible: Boolean, animationMs: Long) {
        onControlsChanged?.invoke(visible, animationMs)
        listener?.onControlsVisibilityChanged(visible)
    }

    override fun requestNavigation(requestId: Long, direction: String) {
        scope.launch {
            val result = navigate(direction)
            runCatching { flutterApi.navigationResult(requestId, result.name) }
        }
    }

    private suspend fun navigate(direction: String): NavigationResult {
        val value = enumValues<NavigationDirection>().firstOrNull { it.name == direction } ?: return NavigationResult.UNAVAILABLE
        val target = listener ?: return NavigationResult.UNAVAILABLE
        return runCatching { target.onNavigationRequested(value) }.getOrDefault(NavigationResult.FAILED)
    }

    override fun onFullscreenRequested(fullscreen: Boolean) {
        listener?.onFullscreenRequested(fullscreen)
    }

    override fun onEditRequested(sessionId: String) {
        listener?.onEditRequested(sessionId)
    }

    override fun onContentDisplayed(kind: EmbedSurfaceKind) {
        onDisplayed?.invoke(kind.toKind())
    }

    internal companion object {
        fun player(sessionId: String, options: PlayerEmbedOptions) = EmbedContentMsg(
            EmbedSurfaceKind.PLAYER,
            sessionId = sessionId,
            sessionIds = emptyList(),
            playerOptions = PlayerEmbedOptionsMsg(
                options.autoHideControlsMs,
                options.allowFullscreen,
                options.showNavigation,
                options.startFullscreen,
            ),
        )

        fun imageViewer(sessionId: String) = EmbedContentMsg(EmbedSurfaceKind.IMAGE_VIEWER, sessionId = sessionId, sessionIds = emptyList())

        fun editor(projectId: String) = EmbedContentMsg(EmbedSurfaceKind.EDITOR, sessionIds = emptyList(), projectId = projectId)

        fun multiView(sessionIds: List<String>) = EmbedContentMsg(EmbedSurfaceKind.MULTI_VIEW, sessionIds = sessionIds)
    }
}

/** The Dart-bound calls of the embed channel; an interface so the controller is testable without an engine. */
internal interface EmbedFlutterApi {
    suspend fun showContent(content: EmbedContentMsg)

    suspend fun setTheme(theme: EmbedThemeMsg?)

    suspend fun setStrings(strings: Map<String, String>)

    suspend fun navigationResult(requestId: Long, result: String)
}

/** [EmbedFlutterApi] over the generated Pigeon class. */
internal class PigeonEmbedFlutterApi(private val api: VideoKitEmbedFlutterApi) : EmbedFlutterApi {
    override suspend fun showContent(content: EmbedContentMsg) = api.showContent(content)

    override suspend fun setTheme(theme: EmbedThemeMsg?) = api.setTheme(theme)

    override suspend fun setStrings(strings: Map<String, String>) = api.setStrings(strings)

    override suspend fun navigationResult(requestId: Long, result: String) = api.navigationResult(requestId, result)
}

internal fun VideoKitThemeOverrides.toMsg(): EmbedThemeMsg =
    // ARGB as an unsigned 32-bit value, so Dart reads it as Color(value) without sign handling.
    EmbedThemeMsg(brightness?.name, colors.mapValues { (_, argb) -> argb.toLong() and 0xFFFFFFFFL })

internal fun EmbedSurfaceKind.toKind(): EmbedContentKind = when (this) {
    EmbedSurfaceKind.PLAYER -> EmbedContentKind.PLAYER
    EmbedSurfaceKind.IMAGE_VIEWER -> EmbedContentKind.IMAGE_VIEWER
    EmbedSurfaceKind.EDITOR -> EmbedContentKind.EDITOR
    EmbedSurfaceKind.MULTI_VIEW -> EmbedContentKind.MULTI_VIEW
}
