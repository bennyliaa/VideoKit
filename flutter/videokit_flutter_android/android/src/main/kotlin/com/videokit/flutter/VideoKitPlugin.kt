package com.videokit.flutter

import android.content.Context
import com.videokit.api.FeatureMode
import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitFeature
import com.videokit.flutter.gen.EditUpdateMessage
import com.videokit.flutter.gen.EditUpdatesStreamHandler
import com.videokit.flutter.gen.SessionUpdateMessage
import com.videokit.flutter.gen.SessionUpdatesStreamHandler
import com.videokit.flutter.gen.VideoKitCallbacksApi
import com.videokit.flutter.gen.VideoKitHostApi
import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.view.TextureRegistry
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

/**
 * Flutter plugin entry (14 §8.4): one instance per Flutter engine. It registers the Pigeon HostApi, the
 * update streams and the callbacks API on the engine's messenger, and releases everything the engine
 * created when the engine detaches (add-to-app multi-engine, 14 §8.4).
 */
class VideoKitPlugin : FlutterPlugin {
    private var engine: EngineRuntime? = null

    override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        val runtime = EngineRuntime(
            engineKey = UUID.randomUUID().toString(),
            context = binding.applicationContext,
            messenger = binding.binaryMessenger,
            textures = binding.textureRegistry,
            main = AndroidMainThread,
        )
        engine = runtime
        VideoKitRegistry.attach(runtime)
        VideoKitHostApi.setUp(binding.binaryMessenger, HostApiImpl(runtime))
        SessionUpdatesStreamHandler.register(binding.binaryMessenger, runtime.sessionStream)
        EditUpdatesStreamHandler.register(binding.binaryMessenger, runtime.editStream)
    }

    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        VideoKitHostApi.setUp(binding.binaryMessenger, null)
        engine?.let { runtime ->
            VideoKitRegistry.detach(runtime)
            runtime.close()
        }
        engine = null
    }
}

/** Process-wide registry of engines (14 §8.4 VideoKitRegistry); sessions and projects are kept per engine. */
internal object VideoKitRegistry {
    private val engines = ConcurrentHashMap<String, EngineRuntime>()

    fun attach(engine: EngineRuntime) {
        engines[engine.engineKey] = engine
    }

    fun detach(engine: EngineRuntime) {
        engines.remove(engine.engineKey)
    }

    /** Number of attached engines (diagnostics). */
    val engineCount: Int get() = engines.size
}

/**
 * State of one engine: its VideoKit instance, sessions, projects, textures and update streams.
 * Channel methods enter on the main thread; work runs on [EngineScope]; replies go back to the main thread.
 */
internal class EngineRuntime(
    val engineKey: String,
    val context: Context,
    val messenger: BinaryMessenger,
    val textures: TextureRegistry?,
    val main: MainThreadRunner,
    val nowMs: () -> Long = { android.os.SystemClock.uptimeMillis() },
    /** Dispatcher of the platform thread for FlutterApi calls (tests pass `Dispatchers.Unconfined`). */
    val mainDispatcher: CoroutineDispatcher = AndroidMainDispatcher,
    /** Dispatcher of the channel work (never the main thread, 14 §8.3). */
    val workDispatcher: CoroutineDispatcher = Dispatchers.Default,
) {
    val scope = EngineScope.create()
    val sessions = ConcurrentHashMap<String, SessionHolder>()
    val projects = ConcurrentHashMap<String, ProjectHolder>()
    val callbacksApi = VideoKitCallbacksApi(messenger)

    @Volatile
    var kit: VideoKit? = null
        private set

    @Volatile
    var backend: VideoKitBackend? = null
        private set

    val sessionFanout = StreamFanout<SessionUpdateMessage>(main) { sessions.values.mapNotNull { it.lastStateMessage } }
    val sessionStream = SessionStream(sessionFanout)
    val editFanout = StreamFanout<EditUpdateMessage>(main) { emptyList() }
    val editStream = EditStream(editFanout)

    /** Creates the engine's VideoKit at the first handshake (later handshakes reuse it). */
    @Synchronized
    fun ensureKit(
        backend: VideoKitBackend,
        timeouts: HostCallbackTimeouts,
        features: Map<VideoKitFeature, FeatureMode> = emptyMap(),
    ): VideoKit = kit ?: backend.create(
        context,
        VideoKitConfig(
            hostCallbacks = FlutterHostCallbacks(callbacksApi, mainDispatcher),
            resourceBudget = PluginResourceBudget.shared,
            callbackTimeouts = timeouts,
            features = features,
        ),
    ).also {
        this.backend = backend
        kit = it
    }

    /** Tells Dart that the texture of [sessionId] changed (fire-and-forget; a missing listener is ignored). */
    fun notifyTextureChanged(sessionId: String, textureId: Long?) {
        scope.launch(mainDispatcher) { runCatching { callbacksApi.onTextureChanged(sessionId, textureId) } }
    }

    /**
     * Engine detached (14 §8.4): releases everything this engine created. A shared host-owned VideoKit
     * ([VideoKitBackend.ownsKits] `false`) is not closed; adopted host sessions are only no longer observed.
     */
    fun close() {
        val owned = sessions.values.filterNot { it.hostOwned }.map { it.session }
        val ownedProjects = projects.values.map { it.project }
        sessions.values.forEach { it.stop() }
        projects.values.forEach { it.stop() }
        sessions.clear()
        projects.clear()
        val instance = kit
        if (backend?.ownsKits == false) {
            ownedProjects.forEach { project -> runCatching { project.close() } }
            if (owned.isNotEmpty()) ReleaseScope.launch { owned.forEach { session -> runCatching { session.release() } } }
        } else {
            instance?.close()
        }
        kit = null
        scope.cancel()
    }
}
