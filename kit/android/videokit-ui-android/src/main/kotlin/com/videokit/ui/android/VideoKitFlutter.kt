package com.videokit.ui.android

import android.app.Application
import android.content.Context
import android.os.Looper
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitSession
import com.videokit.flutter.VideoKitBackend
import com.videokit.flutter.VideoKitFlutter as PluginConfig

/**
 * Entry point of the add-to-app bridge for native hosts (14 §9.1).
 *
 * ```kotlin
 * // Application.onCreate
 * VideoKitFlutter.initialize(this, VideoKitFlutterConfig(videoKit = myVideoKit))
 * // Screen
 * val session = myVideoKit.createSession(VideoKitSessionConfig())
 * session.bind(source)
 * supportFragmentManager.beginTransaction()
 *     .replace(R.id.player, VideoKitPlayerFragment.newInstance(session, PlayerEmbedOptions()))
 *     .commit()
 * ```
 *
 * Sessions stay owned by the host: embedded UIs observe them (the plugin's `adoptSession`) and never release them,
 * so rotation and fullscreen changes do not interrupt playback; the host releases them when it is done.
 * Media callbacks (host actions, errors, snapshots) stay on the host's native `VideoKitHostCallbacks`.
 * Main thread only.
 */
public object VideoKitFlutter {
    private var engines: EmbedEngines? = null
    private var currentConfig: VideoKitFlutterConfig? = null

    /** Whether [initialize] was called. */
    public val isInitialized: Boolean get() = engines != null

    /**
     * Initializes the bridge, typically in `Application.onCreate`. The host's [VideoKitFlutterConfig.videoKit]
     * becomes the backend of the VideoKit Flutter plugin in every embedded engine. Prewarms the first engine when
     * [VideoKitFlutterConfig.prewarmOnInit] is set. Calling it again replaces the configuration for new engines.
     */
    public fun initialize(app: Application, config: VideoKitFlutterConfig) {
        checkMainThread()
        PluginConfig.setBackend(HostKitBackend(config.videoKit))
        currentConfig = config
        engines = EmbedEngines(app.applicationContext, config)
        if (config.prewarmOnInit) prewarm()
    }

    /** Creates and caches the first engine ahead of the first embed (14 §9.2). No-op if one is waiting. */
    public fun prewarm() {
        checkMainThread()
        requireEngines().prewarm()
    }

    /**
     * Makes [session] available to embedded UIs by its id; [VideoKitPlayerFragment.newInstance] with a session
     * does this for you. The host keeps ownership.
     */
    public fun share(session: VideoKitSession) {
        PluginConfig.shareSession(session)
    }

    /** Stops sharing a session id (embeds already showing it keep their proxy until the session is released). */
    public fun unshare(sessionId: String) {
        PluginConfig.unshareSession(sessionId)
    }

    /** Number of embed engines in use (diagnostics and 14 §9.3 multi-instance measurements). */
    public val activeEngineCount: Int get() = engines?.activeCount ?: 0

    internal fun requireEngines(): EmbedEngines =
        engines ?: throw IllegalStateException("VideoKitFlutter.initialize() must be called before embedding VideoKit UI")

    internal val config: VideoKitFlutterConfig? get() = currentConfig

    private fun checkMainThread() {
        check(Looper.myLooper() == Looper.getMainLooper()) { "VideoKitFlutter must be used on the main thread" }
    }
}

/**
 * Plugin backend over the host's VideoKit (add-to-app): every engine uses the same host-owned instance, which an
 * engine never closes; the plugin's own per-engine host callbacks are not used.
 */
internal class HostKitBackend(private val videoKit: VideoKit) : VideoKitBackend {
    override val isDemo: Boolean get() = videoKit.isDemo

    override val ownsKits: Boolean get() = false

    override fun create(context: Context, config: VideoKitConfig): VideoKit = videoKit
}
