package com.videokit.flutter

import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.CoroutineDispatcher
import kotlin.coroutines.CoroutineContext

/** Runs code on the platform (main) thread; Flutter channel replies and events must be sent there (14 §8.3). */
internal fun interface MainThreadRunner {
    fun post(block: () -> Unit)
}

/** [MainThreadRunner] on the Android main looper; runs inline when already on it. */
internal object AndroidMainThread : MainThreadRunner {
    private val handler by lazy { Handler(Looper.getMainLooper()) }

    override fun post(block: () -> Unit) {
        if (Looper.myLooper() == Looper.getMainLooper()) block() else handler.post(block)
    }
}

/**
 * Coroutine dispatcher on the Android main looper, for the suspend Pigeon FlutterApi calls (channel sends
 * must happen on the platform thread). Always enqueues, as the dispatcher contract requires.
 */
internal object AndroidMainDispatcher : CoroutineDispatcher() {
    private val handler by lazy { Handler(Looper.getMainLooper()) }

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        handler.post(block)
    }
}
