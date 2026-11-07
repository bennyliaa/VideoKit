package com.videokit.platform.android.isolation

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Messenger
import android.os.RemoteException
import android.os.SystemClock
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.OpenPurpose
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.core.runtime.IsolatedCalls
import com.videokit.core.runtime.IsolationMessage
import com.videokit.core.runtime.IsolationMessageType
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.IsolatedTask
import com.videokit.core.spi.IsolatedTaskKind
import com.videokit.core.spi.IsolationEvent
import com.videokit.core.spi.IsolationFault
import com.videokit.core.spi.IsolationHost
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

/** Timeouts of [AndroidIsolationHost]. */
public data class IsolationConfig(
    /** Time to bind a worker. */
    val startTimeoutMs: Long = 10_000L,
    /** Interval of liveness pings. */
    val pingIntervalMs: Long = 1_000L,
    /** A worker that answered no ping for this long is treated as hung and stopped. */
    val unresponsiveMs: Long = 5_000L,
    /** Timeout of one host read for a worker. */
    val readTimeoutMs: Long = 10_000L,
)

/**
 * [IsolationHost] with `isolatedProcess` services (07 §5.2, 15 §2.8): every task gets its own worker process
 * ([IsolatedWorkerService] bound with `bindIsolatedService`, the task id as instance name) and its own generation.
 * A crash (binder death), a hang (no ping answer within [IsolationConfig.unresponsiveMs]) or an invalid message
 * fails only that task: pending calls throw INTERNAL_ERROR_REDACTED, the event flow reports Crashed, the worker is
 * unbound; nothing is replayed and other tasks and the playback in this process continue.
 *
 * Isolation counts as verified only after the fault injection runs on devices (07 §5.2, S4); until then hosts must
 * treat it as unverified.
 */
public class AndroidIsolationHost(context: Context, private val config: IsolationConfig = IsolationConfig()) : IsolationHost {
    private val appContext = context.applicationContext
    private val generations = AtomicInteger()

    override val isolated: Boolean get() = true

    override suspend fun start(kind: IsolatedTaskKind): IsolatedTask {
        val generation = generations.incrementAndGet()
        val task = AndroidIsolatedTask(appContext, "${kind.name.lowercase()}-$generation", generation, config)
        try {
            task.connect()
        } catch (failure: Throwable) {
            task.close()
            throw failure
        }
        return task
    }
}

private class AndroidIsolatedTask(
    private val context: Context,
    private val taskId: String,
    override val generation: Int,
    private val config: IsolationConfig,
) : IsolatedTask {
    private val calls = IsolatedCalls(taskId, generation)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val thread = HandlerThread("videokit-isolation-$taskId").apply { start() }
    private val replies = Messenger(
        Handler(thread.looper) { message ->
            onWorkerMessage(message)
            true
        },
    )
    private val mutableEvents = MutableSharedFlow<IsolationEvent>(replay = EVENT_REPLAY, extraBufferCapacity = EVENT_REPLAY)
    private val mutableAlive = MutableStateFlow(false)
    private val connected = CompletableDeferred<Unit>()
    private val sources = ConcurrentHashMap<Long, VideoKitMediaSource>()
    private val handles = ConcurrentHashMap<Long, VideoKitReadHandle>()

    @Volatile
    private var worker: Messenger? = null

    @Volatile
    private var binder: IBinder? = null

    @Volatile
    private var lastPongMs = SystemClock.uptimeMillis()

    @Volatile
    private var ended = false

    override val events: Flow<IsolationEvent> = mutableEvents.asSharedFlow()

    override val alive: StateFlow<Boolean> = mutableAlive.asStateFlow()

    private val death = IBinder.DeathRecipient { died("CRASHED") }

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, service: IBinder) {
            try {
                service.linkToDeath(death, 0)
            } catch (_: RemoteException) {
                died("CRASHED")
                return
            }
            binder = service
            worker = Messenger(service)
            lastPongMs = SystemClock.uptimeMillis()
            mutableAlive.value = true
            mutableEvents.tryEmit(IsolationEvent.Started)
            connected.complete(Unit)
            scope.launch { watchdog() }
        }

        override fun onServiceDisconnected(name: ComponentName) {
            died("DISCONNECTED")
        }

        override fun onBindingDied(name: ComponentName) {
            died("BINDING_DIED")
        }

        override fun onNullBinding(name: ComponentName) {
            died("NULL_BINDING")
        }
    }

    suspend fun connect() {
        val intent = Intent(context, IsolatedWorkerService::class.java)
            .putExtra(IsolationBundles.EXTRA_TASK, taskId)
            .putExtra(IsolationBundles.EXTRA_GENERATION, generation)
        val bound = context.bindIsolatedService(intent, Context.BIND_AUTO_CREATE, taskId, context.mainExecutor, connection)
        if (!bound) throw SpiException(StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, "ISOLATED:BIND"))
        try {
            withTimeout(config.startTimeoutMs) { connected.await() }
        } catch (failure: Exception) {
            throw SpiException(StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, "ISOLATED:START"))
        }
    }

    override suspend fun call(operation: String, payload: ByteArray, source: VideoKitMediaSource?): ByteArray {
        val message = calls.outgoing(IsolationMessageType.CALL, name = operation, payload = payload)
        val answer = calls.register(message)
        source?.let { sources[message.seq] = it }
        try {
            send(message)
            return calls.resultOf(answer.await())
        } finally {
            sources.remove(message.seq)
            handles.remove(message.seq)?.let { handle -> withContext(NonCancellable + Dispatchers.IO) { runCatching { handle.close() } } }
        }
    }

    override suspend fun injectFault(fault: IsolationFault) {
        send(calls.outgoing(IsolationMessageType.FAULT, name = fault.name))
    }

    private fun send(message: IsolationMessage) {
        val target = worker ?: return
        try {
            target.send(IsolationBundles.message(message).also { it.replyTo = replies })
        } catch (_: RemoteException) {
            died("SEND")
        }
    }

    private fun onWorkerMessage(raw: android.os.Message) {
        val message = IsolationBundles.decode(raw)
        val outcome = if (message == null) {
            calls.fail("PROTOCOL:DECODE")
            IsolatedCalls.Incoming.Refused("PROTOCOL:DECODE")
        } else {
            calls.onMessage(message)
        }
        when (outcome) {
            is IsolatedCalls.Incoming.Read -> scope.launch { serveRead(outcome) }
            IsolatedCalls.Incoming.Pong -> lastPongMs = SystemClock.uptimeMillis()
            is IsolatedCalls.Incoming.Refused -> died(outcome.reason)
            IsolatedCalls.Incoming.Delivered -> Unit
        }
    }

    /** Serves a worker read from the host source of the call (bounded by the protocol, 07 §5.2). */
    private suspend fun serveRead(read: IsolatedCalls.Incoming.Read) {
        val bytes = try {
            val source = sources[read.callSeq] ?: throw IllegalStateException("call without source")
            val handle = handles[read.callSeq] ?: source.sourceFactory.open(OpenPurpose.PROBE).also { handles[read.callSeq] = it }
            val buffer = ByteArray(read.length)
            val count = withTimeout(config.readTimeoutMs) { handle.readAt(read.offset, buffer, 0, read.length) }
            if (count <= 0) ByteArray(0) else buffer.copyOf(count)
        } catch (_: Exception) {
            // The worker sees the end of the source; the call then fails or returns what it has.
            ByteArray(0)
        }
        send(calls.readData(read.callSeq, bytes))
    }

    private suspend fun watchdog() {
        while (scope.isActive && !ended) {
            delay(config.pingIntervalMs)
            if (SystemClock.uptimeMillis() - lastPongMs > config.unresponsiveMs) {
                died("UNRESPONSIVE")
                return
            }
            send(calls.outgoing(IsolationMessageType.PING))
        }
    }

    /** The worker is gone or misbehaved: fail this task only (07 §5.2). */
    private fun died(reason: String) {
        if (ended) return
        ended = true
        calls.fail(reason)
        mutableAlive.value = false
        mutableEvents.tryEmit(IsolationEvent.Crashed(reason))
        if (!connected.isCompleted) {
            connected.completeExceptionally(
                SpiException(StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, "ISOLATED:$reason")),
            )
        }
        release()
    }

    override fun close() {
        if (!ended) {
            ended = true
            calls.fail("CLOSED")
            mutableAlive.value = false
            mutableEvents.tryEmit(IsolationEvent.Finished)
        }
        release()
    }

    private fun release() {
        runCatching { binder?.unlinkToDeath(death, 0) }
        binder = null
        worker = null
        runCatching { context.unbindService(connection) }
        handles.values.forEach { runCatching { it.close() } }
        handles.clear()
        scope.cancel()
        thread.quitSafely()
    }

    private companion object {
        const val EVENT_REPLAY = 8
    }
}
