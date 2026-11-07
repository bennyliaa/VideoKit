package com.videokit.flutter

import com.videokit.flutter.gen.EditUpdateMessage
import com.videokit.flutter.gen.EditUpdatesStreamHandler
import com.videokit.flutter.gen.PigeonEventSink
import com.videokit.flutter.gen.SessionUpdateMessage
import com.videokit.flutter.gen.SessionUpdatesStreamHandler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob

/** Coroutine scope of the plugin work (14 §8.3: `SupervisorJob() + Dispatchers.Default`, never the main thread). */
internal object EngineScope {
    fun create(): CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
}

/**
 * Sending side of one update stream. Messages are delivered on the platform thread; a new listener first
 * receives [replay] (the latest state of every live object), so a late Dart subscriber is never empty.
 */
internal class StreamFanout<T>(private val main: MainThreadRunner, private val replay: () -> List<T>) {
    @Volatile
    private var sink: PigeonEventSink<T>? = null

    fun listen(sink: PigeonEventSink<T>) {
        this.sink = sink
        replay().forEach { sink.success(it) }
    }

    fun cancel() {
        sink = null
    }

    fun send(message: T) {
        main.post { sink?.success(message) }
    }
}

/** Pigeon handler of the session update stream. */
internal class SessionStream(private val fanout: StreamFanout<SessionUpdateMessage>) : SessionUpdatesStreamHandler() {
    override fun onListen(p0: Any?, sink: PigeonEventSink<SessionUpdateMessage>) = fanout.listen(sink)

    override fun onCancel(p0: Any?) = fanout.cancel()
}

/** Pigeon handler of the edit update stream. */
internal class EditStream(private val fanout: StreamFanout<EditUpdateMessage>) : EditUpdatesStreamHandler() {
    override fun onListen(p0: Any?, sink: PigeonEventSink<EditUpdateMessage>) = fanout.listen(sink)

    override fun onCancel(p0: Any?) = fanout.cancel()
}

/**
 * Process-wide scope for releases that must outlive a detached engine (sessions an engine created on a shared,
 * host-owned VideoKit).
 */
internal object ReleaseScope : CoroutineScope by CoroutineScope(SupervisorJob() + Dispatchers.Default)
