package com.videokit.testkit.internal

import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.VideoKitHostCallbacks
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout

/**
 * Calls host callbacks with timeouts and failure isolation (04 §8, 02 §5).
 *
 * Notifications are delivered in order by one worker coroutine through a bounded queue (oldest
 * notifications are dropped under pressure), each with [HostCallbackTimeouts.notificationMs].
 * A failing or hanging callback never blocks a session; failures are counted as HOST_CALLBACK_FAILED.
 */
internal class CallbackRunner(scope: CoroutineScope, private val callbacks: VideoKitHostCallbacks, val timeouts: HostCallbackTimeouts) {
    private val queue = Channel<Notification>(capacity = QUEUE_CAPACITY, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val failureCount = AtomicCounter()

    /** Number of failed or timed-out callbacks (diagnostics). */
    val failures: Int get() = failureCount.value.toInt()

    init {
        scope.launch {
            for (notification in queue) {
                request(notification.name, timeouts.notificationMs) { notification.block(this) }
            }
        }
    }

    /** Queues a notification callback. Never suspends. */
    fun notify(name: String, block: suspend VideoKitHostCallbacks.() -> Unit) {
        queue.trySend(Notification(name, block))
    }

    /**
     * Calls a request/response callback in the caller's coroutine with [timeoutMs].
     * Returns a failure for exceptions and timeouts; propagates cancellation of the caller.
     */
    suspend fun <T> request(name: String, timeoutMs: Long, block: suspend VideoKitHostCallbacks.() -> T): CallbackOutcome<T> = try {
        CallbackOutcome.Success(withTimeout(timeoutMs) { callbacks.block() })
    } catch (timeout: TimeoutCancellationException) {
        failureCount.incrementAndGet()
        CallbackOutcome.Failure(Errors.callbackFailed(name, timeout))
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (failure: Exception) {
        failureCount.incrementAndGet()
        CallbackOutcome.Failure(Errors.callbackFailed(name, failure))
    }

    fun close() {
        queue.close()
    }

    private class Notification(val name: String, val block: suspend VideoKitHostCallbacks.() -> Unit)

    private companion object {
        const val QUEUE_CAPACITY = 256
    }
}

/** Outcome of a host callback request. */
internal sealed interface CallbackOutcome<out T> {
    data class Success<T>(val value: T) : CallbackOutcome<T>

    data class Failure(val error: com.videokit.api.VideoKitStableError) : CallbackOutcome<Nothing>
}
