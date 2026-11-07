package com.videokit.flutter

import android.content.Context
import com.videokit.api.MediaKind
import com.videokit.api.SessionPhase
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSourceFactory
import com.videokit.api.android.VideoKitFactory
import java.util.concurrent.ConcurrentHashMap

/**
 * The native VideoKit implementation the plugin talks to (14 §8.4 `VideoKitBackendProvider`).
 * M0 debug builds default to the Kotlin Fake; from M1 the real implementation is the default.
 */
interface VideoKitBackend {
    /** Whether the backend serves demo data (handshake `demoBackend`, UI demo badge). */
    val isDemo: Boolean

    /**
     * Whether [create] returns an instance owned by the engine (closed when the engine detaches). `false` for a
     * host-owned instance shared by all engines (add-to-app, 14 §9): the engine then releases only the sessions
     * and projects it created, and never closes the instance.
     */
    val ownsKits: Boolean get() = true

    /** Creates one VideoKit instance per Flutter engine (or returns the shared one, see [ownsKits]). */
    fun create(context: Context, config: VideoKitConfig): VideoKit

    /** Source for `demo:<scenarioId>` references, or `null` when the backend has no demo sources. */
    fun demoSource(scenarioId: String, token: String, kind: MediaKind): VideoKitMediaSource? = null

    /** Sink for the `demo:memory` sink reference, or `null`. */
    fun demoSink(): VideoKitOutputSink? = null
}

/**
 * The real implementation through [VideoKitFactory] (VK-M1: core runtime + Media3 playback engine). Release builds
 * must select it (or another backend) explicitly; debug builds default to the Kotlin Fake and opt in with
 * [VideoKitFlutter.useRealBackend].
 */
object RealVideoKitBackend : VideoKitBackend {
    override val isDemo: Boolean = false

    override fun create(context: Context, config: VideoKitConfig): VideoKit = VideoKitFactory.create(context, config)
}

/**
 * Host-facing configuration of the plugin (14 §8.4). Call from `Application.onCreate` before the first
 * Flutter engine attaches.
 */
object VideoKitFlutter {
    /** Error code of the handshake when no backend is available (release build without [setBackend]). */
    const val NO_BACKEND: String = "VIDEOKIT_NO_BACKEND"

    private const val DEBUG_BACKEND_CLASS = "com.videokit.flutter.debug.DebugFakeBackend"

    @Volatile
    private var explicitBackend: VideoKitBackend? = null

    private val sources = ConcurrentHashMap<String, VideoKitSourceFactory>()
    private val sinks = ConcurrentHashMap<String, VideoKitOutputSink>()
    private val sharedSessions = ConcurrentHashMap<String, VideoKitSession>()

    /** Uses the real implementation ([RealVideoKitBackend]), also in debug builds. */
    fun useRealBackend() {
        explicitBackend = RealVideoKitBackend
    }

    /** Selects the backend; `null` restores the default. */
    fun setBackend(backend: VideoKitBackend?) {
        explicitBackend = backend
    }

    /** Registers a host source factory for `registered:<id>` references (04 §12.3). */
    fun registerSource(id: String, factory: VideoKitSourceFactory) {
        sources[id] = factory
    }

    /** Removes a registered source factory. */
    fun unregisterSource(id: String) {
        sources.remove(id)
    }

    /** Registers a host sink for `registered:<id>` sink references (04A I16). */
    fun registerSink(id: String, sink: VideoKitOutputSink) {
        sinks[id] = sink
    }

    /** Removes a registered sink. */
    fun unregisterSink(id: String) {
        sinks.remove(id)
    }

    /**
     * Makes a host-owned session visible to Flutter engines (add-to-app, 14 §9.1): Dart adopts it by id with
     * `FlutterVideoKit.adoptSession`. The host keeps ownership: Dart `release()` and engine detach only stop
     * observing it; the host decides when to release it. Released sessions are dropped automatically.
     */
    fun shareSession(session: VideoKitSession) {
        sharedSessions.entries.removeAll { it.value.state.value.phase == SessionPhase.RELEASED }
        sharedSessions[session.sessionId] = session
    }

    /** Stops sharing [sessionId]; engines already observing it keep their proxy until it is released. */
    fun unshareSession(sessionId: String) {
        sharedSessions.remove(sessionId)
    }

    internal fun sharedSession(sessionId: String): VideoKitSession? =
        sharedSessions[sessionId]?.takeUnless { it.state.value.phase == SessionPhase.RELEASED }

    internal fun registeredSource(id: String): VideoKitSourceFactory? = sources[id]

    internal fun registeredSink(id: String): VideoKitOutputSink? = sinks[id]

    /**
     * Resolves the backend: an explicit one, otherwise the debug-only Fake (present only in debug builds,
     * 14 §11.4). Release builds without an explicit backend return `null` and the handshake fails clearly;
     * they never fall back to the Fake silently.
     */
    internal fun resolveBackend(): VideoKitBackend? = explicitBackend ?: debugBackend()

    private fun debugBackend(): VideoKitBackend? = runCatching {
        Class.forName(DEBUG_BACKEND_CLASS).getField("INSTANCE").get(null) as VideoKitBackend
    }.getOrNull()
}
