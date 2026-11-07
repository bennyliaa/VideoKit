package com.videokit.testkit.internal

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.getAndUpdate
import kotlinx.coroutines.flow.update

/**
 * Lock-free building blocks for the platform independent testkit (13 §3.2: no `java.*` in commonMain).
 * They are backed by [MutableStateFlow], whose `update`/`compareAndSet` are atomic on every platform.
 */
internal class AtomicFlag(initial: Boolean = false) {
    private val state = MutableStateFlow(initial)

    val value: Boolean get() = state.value

    /** Sets the flag; returns `true` only for the call that changed it from `false`. */
    fun setOnce(): Boolean = state.compareAndSet(expect = false, update = true)
}

internal class AtomicCounter(initial: Long = 0L) {
    private val state = MutableStateFlow(initial)

    val value: Long get() = state.value

    fun incrementAndGet(): Long = state.getAndUpdate { it + 1 } + 1
}

internal class AtomicValue<T>(initial: T) {
    private val state = MutableStateFlow(Box(initial))

    val value: T get() = state.value.item

    fun getAndSet(item: T): T = state.getAndUpdate { Box(item) }.item

    /** Sets [item] only when the current value is [expect] (identity); returns whether it was set. */
    fun compareAndSet(expect: T, item: T): Boolean {
        val current = state.value
        return current.item === expect && state.compareAndSet(current, Box(item))
    }

    // Boxing gives identity semantics to compareAndSet, independent of the item's equals().
    private class Box<T>(val item: T)
}

/** Append-only, thread-safe record list; reads return immutable snapshots. */
internal class RecordList<T> {
    private val state = MutableStateFlow<List<T>>(emptyList())

    val snapshot: List<T> get() = state.value

    fun add(item: T) {
        state.update { it + item }
    }
}

/** Thread-safe map with copy-on-write updates. */
internal class AtomicMap<K, V> {
    private val state = MutableStateFlow<Map<K, V>>(emptyMap())

    val snapshot: Map<K, V> get() = state.value

    operator fun get(key: K): V? = state.value[key]

    fun put(key: K, value: V) {
        state.update { it + (key to value) }
    }

    fun remove(key: K) {
        state.update { it - key }
    }

    /** Atomically applies [transform]; returns its result. Retried on contention, so it must be pure. */
    fun <R> modify(transform: (Map<K, V>) -> Pair<Map<K, V>, R>): R {
        while (true) {
            val current = state.value
            val (next, result) = transform(current)
            if (state.compareAndSet(current, next)) return result
        }
    }
}

/** Simple class name for redacted diagnostics (never the message, which may contain paths). */
internal fun Any.typeName(): String = this::class.simpleName ?: "Unknown"
