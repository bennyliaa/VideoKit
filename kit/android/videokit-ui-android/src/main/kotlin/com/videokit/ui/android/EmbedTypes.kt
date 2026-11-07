package com.videokit.ui.android

import android.os.Bundle
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationResult
import com.videokit.api.VideoKit

/**
 * Configuration of the add-to-app bridge (14 §9.1).
 *
 * @property videoKit the host's native VideoKit (the Kotlin Fake in M0). It stays owned by the host: the bridge
 *   never closes it, and its host callbacks stay the host's native callbacks.
 * @property prewarmOnInit create and cache the first engine in [VideoKitFlutter.initialize] (14 §9.2).
 * @property theme token overrides from the native side.
 * @property strings text overrides, keys as in the ARB file.
 * @property dartEntrypoint Dart entry point of the embed engines.
 * @property dartLibraryUri library of [dartEntrypoint]; `null` = the module's main library.
 */
public class VideoKitFlutterConfig(
    public val videoKit: VideoKit,
    public val prewarmOnInit: Boolean = true,
    public val theme: VideoKitThemeOverrides? = null,
    public val strings: Map<String, String> = emptyMap(),
    public val dartEntrypoint: String = DEFAULT_DART_ENTRYPOINT,
    public val dartLibraryUri: String? = null,
) {
    public companion object {
        /** `@pragma('vm:entry-point') void videokitEmbedMain(List<String> args)` (14 §9.2). */
        public const val DEFAULT_DART_ENTRYPOINT: String = "videokitEmbedMain"
    }
}

/** Brightness of the embedded UI; `null` in [VideoKitThemeOverrides] follows the system. */
public enum class EmbedBrightness { LIGHT, DARK }

/**
 * Token overrides passed from the native host (14 §9.1).
 *
 * @property colors ARGB colors keyed by the Dart token key (`VkTokenKeys`, e.g. `color.accent`).
 */
public class VideoKitThemeOverrides(public val brightness: EmbedBrightness? = null, public val colors: Map<String, Int> = emptyMap())

/** Options of an embedded player (14 §9.1, defaults 14 §12). */
public data class PlayerEmbedOptions(
    /** Controls auto-hide delay. */
    val autoHideControlsMs: Long = 3_000L,
    /** Whether the UI offers fullscreen (the host performs it on [VideoKitEmbedListener.onFullscreenRequested]). */
    val allowFullscreen: Boolean = true,
    /** Whether previous / next navigation is shown. */
    val showNavigation: Boolean = true,
    /** Start in the fullscreen layout. */
    val startFullscreen: Boolean = false,
) {
    internal fun toBundle(): Bundle = Bundle().apply {
        putLong(KEY_AUTO_HIDE, autoHideControlsMs)
        putBoolean(KEY_FULLSCREEN, allowFullscreen)
        putBoolean(KEY_NAVIGATION, showNavigation)
        putBoolean(KEY_START_FULLSCREEN, startFullscreen)
    }

    internal companion object {
        private const val KEY_AUTO_HIDE = "autoHideControlsMs"
        private const val KEY_FULLSCREEN = "allowFullscreen"
        private const val KEY_NAVIGATION = "showNavigation"
        private const val KEY_START_FULLSCREEN = "startFullscreen"

        fun fromBundle(bundle: Bundle?): PlayerEmbedOptions {
            val defaults = PlayerEmbedOptions()
            if (bundle == null) return defaults
            return PlayerEmbedOptions(
                autoHideControlsMs = bundle.getLong(KEY_AUTO_HIDE, defaults.autoHideControlsMs),
                allowFullscreen = bundle.getBoolean(KEY_FULLSCREEN, defaults.allowFullscreen),
                showNavigation = bundle.getBoolean(KEY_NAVIGATION, defaults.showNavigation),
                startFullscreen = bundle.getBoolean(KEY_START_FULLSCREEN, defaults.startFullscreen),
            )
        }
    }
}

/** What an embed shows (mirrors the embed protocol). */
public enum class EmbedContentKind { PLAYER, IMAGE_VIEWER, EDITOR, MULTI_VIEW }

/**
 * UI-level requests of an embedded VideoKit UI (14 §9.1). Media callbacks (host actions, errors, snapshots) stay on
 * the host's native `VideoKitHostCallbacks`. Every method has a no-op default; all are called on the main thread.
 */
public interface VideoKitEmbedListener {
    /** Controls were shown or hidden; the bridge has already started animating the host panel container. */
    public fun onControlsVisibilityChanged(visible: Boolean) {}

    /** Previous / next requested from the embedded UI. */
    public suspend fun onNavigationRequested(direction: NavigationDirection): NavigationResult = NavigationResult.UNAVAILABLE

    /** The UI asks to enter or leave fullscreen; the host changes orientation and system bars. */
    public fun onFullscreenRequested(fullscreen: Boolean) {}

    /** The UI asks to open the editor for [sessionId]'s media. */
    public fun onEditRequested(sessionId: String) {}

    /**
     * First Flutter frame of the embed (14 §9.3 first-frame metric).
     *
     * @param elapsedMs from `newInstance` (or [VideoKitFlutterView] content request) to the first frame.
     * @param prewarmed whether the engine was the prewarmed one.
     */
    public fun onFirstFrame(kind: EmbedContentKind, elapsedMs: Long, prewarmed: Boolean) {}
}
