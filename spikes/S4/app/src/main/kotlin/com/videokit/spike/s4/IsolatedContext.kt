package com.videokit.spike.s4

import android.content.BroadcastReceiver
import android.content.Context
import android.content.ContextWrapper
import android.content.Intent
import android.content.IntentFilter
import android.os.Handler

/**
 * S4 attempt 1 finding: Media3's `NetworkTypeObserver` (behind the default bandwidth meter of the ExoPlayer inside
 * Transformer's asset loader) calls `registerReceiver`, which Android forbids in an isolated process
 * (`SecurityException: Isolated process not allowed to call registerReceiver`), killing the worker at start.
 * An export worker has no use for network or broadcast state: registering is a no-op here (returns no sticky intent).
 * `getApplicationContext()` returns this wrapper so that singletons created from it see the same behaviour.
 */
class IsolatedContext(base: Context) : ContextWrapper(base) {
    override fun getApplicationContext(): Context = this

    override fun registerReceiver(receiver: BroadcastReceiver?, filter: IntentFilter?): Intent? = null

    override fun registerReceiver(receiver: BroadcastReceiver?, filter: IntentFilter?, flags: Int): Intent? = null

    override fun registerReceiver(
        receiver: BroadcastReceiver?,
        filter: IntentFilter?,
        broadcastPermission: String?,
        scheduler: Handler?,
    ): Intent? = null

    override fun registerReceiver(
        receiver: BroadcastReceiver?,
        filter: IntentFilter?,
        broadcastPermission: String?,
        scheduler: Handler?,
        flags: Int,
    ): Intent? = null

    override fun unregisterReceiver(receiver: BroadcastReceiver?) = Unit
}
