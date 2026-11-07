package com.videokit.ui.android

import android.content.Context
import com.videokit.ui.android.gen.VideoKitEmbedFlutterApi
import com.videokit.ui.android.gen.VideoKitEmbedHostApi
import io.flutter.FlutterInjector
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.FlutterEngineCache
import io.flutter.embedding.engine.FlutterEngineGroup
import io.flutter.embedding.engine.dart.DartExecutor
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel

/** One embed engine with its channel; cached in [FlutterEngineCache] under [engineId]. */
internal class EmbedEngine(
    val engineId: String,
    val engine: FlutterEngine,
    val controller: EmbedController,
    val prewarmed: Boolean,
    private val scope: CoroutineScope,
) {
    fun destroy() {
        VideoKitEmbedHostApi.setUp(engine.dartExecutor.binaryMessenger, null)
        FlutterEngineCache.getInstance().remove(engineId)
        scope.cancel()
        engine.destroy()
    }
}

/**
 * Engine management of the bridge (14 §9.2): one [FlutterEngineGroup] per process, so embedded instances share
 * the Dart VM; an optional prewarmed engine handed to the first embed; every engine runs the embed entry point
 * and gets its own embed channel. Main thread only.
 */
internal class EmbedEngines(private val appContext: Context, private val config: VideoKitFlutterConfig) {
    private val group by lazy { FlutterEngineGroup(appContext) }
    private val engines = HashMap<String, EmbedEngine>()
    private var prewarmed: EmbedEngine? = null
    private var counter = 0

    /** Creates the prewarmed engine if there is none (14 §9.2). */
    fun prewarm() {
        if (prewarmed == null) prewarmed = create(nextId(), prewarmed = true)
    }

    /** An engine for a new embed: the prewarmed one first, otherwise a new engine from the group. */
    fun acquire(): EmbedEngine {
        val engine = prewarmed?.also { prewarmed = null } ?: create(nextId(), prewarmed = false)
        engines[engine.engineId] = engine
        return engine
    }

    /**
     * The engine of a restored embed. After a configuration change it is still alive; after process death the
     * cache is empty and a new engine is created under the saved id, so a restored FlutterFragment finds it.
     */
    fun restore(engineId: String): EmbedEngine = engines[engineId] ?: create(engineId, prewarmed = false).also { engines[engineId] = it }

    fun destroy(engineId: String) {
        engines.remove(engineId)?.destroy()
    }

    /** Engines in use (diagnostics, multi-instance measurements). */
    val activeCount: Int get() = engines.size

    private fun nextId(): String = "videokit.embed.${++counter}"

    private fun create(engineId: String, prewarmed: Boolean): EmbedEngine {
        val loader = FlutterInjector.instance().flutterLoader()
        val entrypoint = config.dartLibraryUri
            ?.let { DartExecutor.DartEntrypoint(loader.findAppBundlePath(), it, config.dartEntrypoint) }
            ?: DartExecutor.DartEntrypoint(loader.findAppBundlePath(), config.dartEntrypoint)
        val engine = group.createAndRunEngine(appContext, entrypoint)
        val scope = CoroutineScope(SupervisorJob() + MainDispatcher)
        val messenger = engine.dartExecutor.binaryMessenger
        val controller = EmbedController(PigeonEmbedFlutterApi(VideoKitEmbedFlutterApi(messenger)), scope, config.theme, config.strings)
        VideoKitEmbedHostApi.setUp(messenger, controller)
        FlutterEngineCache.getInstance().put(engineId, engine)
        return EmbedEngine(engineId, engine, controller, prewarmed, scope)
    }
}
