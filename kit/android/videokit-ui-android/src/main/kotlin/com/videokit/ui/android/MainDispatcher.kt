package com.videokit.ui.android

import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.CoroutineDispatcher
import kotlin.coroutines.CoroutineContext

/**
 * Main-looper dispatcher of the bridge. The bridge depends only on api-android and the Flutter embedding (M0-B3
 * dependency rule), so it does not pull in kotlinx-coroutines-android for `Dispatchers.Main`.
 */
internal object MainDispatcher : CoroutineDispatcher() {
    private val handler by lazy { Handler(Looper.getMainLooper()) }

    override fun isDispatchNeeded(context: CoroutineContext): Boolean = Looper.myLooper() != Looper.getMainLooper()

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        handler.post(block)
    }
}
