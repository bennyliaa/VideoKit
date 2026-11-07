package com.videokit.core.runtime

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.getAndUpdate
import kotlinx.coroutines.flow.update

/*
 * Lock-free building blocks of the session runtime for platform independent code (13 §3.2: no `java.*` in
 * commonMain). Backed by MutableStateFlow, whose update/compareAndSet are atomic on every platform. Public because
 * the runtime modules (videokit-playback, later image/export) use them; not intended for hosts.
 */

/** A flag that can be set once. */
public class AtomicFlag(initial: Boolean = false) {
    private val state = MutableStateFlow(initial)

    /** Current value. */
    public val value: Boolean get() = state.value

    /** Sets the flag; returns `true` only for the call that changed it from `false`. */
    public fun setOnce(): Boolean = state.compareAndSet(expect = false, update = true)
}

/** A counter. */
public class AtomicCounter(initial: Long = 0L) {
    private val state = MutableStateFlow(initial)

    /** Current value. */
    public val value: Long get() = state.value

    /** Increments and returns the new value. */
    public fun incrementAndGet(): Long = state.getAndUpdate { it + 1 } + 1
}

/** A reference with identity compare-and-set. */
public class AtomicValue<T>(initial: T) {
    private val state = MutableStateFlow(Box(initial))

    /** Current value. */
    public val value: T get() = state.value.item

    /** Sets [item]; returns the previous value. */
    public fun getAndSet(item: T): T = state.getAndUpdate { Box(item) }.item

    /** Sets [item] only when the current value is [expect] (identity); returns whether it was set. */
    public fun compareAndSet(expect: T, item: T): Boolean {
        val current = state.value
        return current.item === expect && state.compareAndSet(current, Box(item))
    }

    // Boxing gives identity semantics to compareAndSet, independent of the item's equals().
    private class Box<T>(val item: T)
}

/** Thread-safe map with copy-on-write updates. */
public class AtomicMap<K, V> {
    private val state = MutableStateFlow<Map<K, V>>(emptyMap())

    /** Immutable snapshot. */
    public val snapshot: Map<K, V> get() = state.value

    /** Value for [key]. */
    public operator fun get(key: K): V? = state.value[key]

    /** Puts [value] for [key]. */
    public fun put(key: K, value: V) {
        state.update { it + (key to value) }
    }

    /** Removes [key]. */
    public fun remove(key: K) {
        state.update { it - key }
    }
}

/** Simple class name for redacted diagnostics (never the message, which may contain paths or credentials). */
public fun Any.typeName(): String = this::class.simpleName ?: "Unknown"
