package com.videokit.core.runtime

import com.videokit.api.HostCallbackTimeouts
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitStableError
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout

/**
 * Calls host callbacks with timeouts and failure isolation (04 §8, 02 §5, 04A I8).
 *
 * Notifications are delivered in order by one worker coroutine through a bounded queue (the oldest are dropped
 * under pressure), each with [HostCallbackTimeouts.notificationMs]. A failing or hanging callback never blocks a
 * session; failures count as HOST_CALLBACK_FAILED.
 */
public class HostCallbackRunner(
    scope: CoroutineScope,
    private val callbacks: VideoKitHostCallbacks,
    /** Timeouts. */
    public val timeouts: HostCallbackTimeouts,
) {
    private val queue = Channel<Notification>(capacity = QUEUE_CAPACITY, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val failureCount = AtomicCounter()

    /** Number of failed or timed-out callbacks (diagnostics). */
    public val failures: Int get() = failureCount.value.toInt()

    init {
        scope.launch {
            for (notification in queue) {
                request(notification.name, timeouts.notificationMs) { notification.block(this) }
            }
        }
    }

    /** Queues a notification callback. Never suspends. */
    public fun notify(name: String, block: suspend VideoKitHostCallbacks.() -> Unit) {
        queue.trySend(Notification(name, block))
    }

    /**
     * Calls a request/response callback in the caller's coroutine with [timeoutMs]. Returns a failure for
     * exceptions and timeouts; propagates cancellation of the caller.
     */
    public suspend fun <T> request(name: String, timeoutMs: Long, block: suspend VideoKitHostCallbacks.() -> T): CallbackOutcome<T> = try {
        CallbackOutcome.Success(withTimeout(timeoutMs) { callbacks.block() })
    } catch (timeout: TimeoutCancellationException) {
        failureCount.incrementAndGet()
        CallbackOutcome.Failure(StableErrors.callbackFailed(name, timeout))
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (failure: Exception) {
        failureCount.incrementAndGet()
        CallbackOutcome.Failure(StableErrors.callbackFailed(name, failure))
    }

    /** Stops delivering queued notifications. */
    public fun close() {
        queue.close()
    }

    private class Notification(val name: String, val block: suspend VideoKitHostCallbacks.() -> Unit)

    private companion object {
        const val QUEUE_CAPACITY = 256
    }
}

/** Outcome of a host callback request. */
public sealed interface CallbackOutcome<out T> {
    /** The host answered. */
    public data class Success<T>(val value: T) : CallbackOutcome<T>

    /** The callback failed or timed out. */
    public data class Failure(val error: VideoKitStableError) : CallbackOutcome<Nothing>
}
