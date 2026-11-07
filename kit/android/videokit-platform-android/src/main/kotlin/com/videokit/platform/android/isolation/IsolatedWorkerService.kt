package com.videokit.platform.android.isolation

import android.app.Service
import android.content.Intent
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Looper
import android.os.Message
import android.os.Messenger
import android.os.RemoteException
import com.videokit.api.ErrorCode
import com.videokit.core.runtime.IsolationMessage
import com.videokit.core.runtime.IsolationMessageType
import com.videokit.core.runtime.IsolationProtocol
import com.videokit.core.spi.IsolationFault
import com.videokit.image.ImageFormats
import com.videokit.platform.android.ContainerSniffer
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit

/**
 * The isolated worker (07 §5.2): `android:isolatedProcess="true"`, no file, network or app data access. One
 * instance per task (`bindIsolatedService` with the task id as instance name); it ends when the task unbinds.
 *
 * Inputs come only through the protocol: a call reads its source with READ_REQUEST messages that the host process
 * answers from the host `readAt` (bounded to [IsolationProtocol.MAX_READ_BYTES] per message). Messages that fail the
 * protocol checks are dropped. Operations of this version:
 * - [OP_PROBE_HEADER]: the container or image format from the first bytes of the source (the vehicle of the
 *   isolation and fault injection tests; real probing stays in the app process per 15 §2.8 until a native parser
 *   arrives, and export/tracking workers of VK-M4/M6 reuse this transport).
 */
public class IsolatedWorkerService : Service() {
    private lateinit var thread: HandlerThread
    private lateinit var handler: Handler
    private lateinit var messenger: Messenger
    private val work: ExecutorService = Executors.newSingleThreadExecutor { Thread(it, "videokit-worker-call") }

    // Handler thread only (seq numbers also from the call thread, see nextSeq()).
    private var taskId: String = ""
    private var generation: Int = -1
    private var lastHostSeq = 0L
    private var host: Messenger? = null
    private val reads = java.util.concurrent.ConcurrentHashMap<Long, LinkedBlockingQueue<ByteArray>>()
    private val seq = java.util.concurrent.atomic.AtomicLong()

    override fun onCreate() {
        super.onCreate()
        thread = HandlerThread("videokit-worker").apply { start() }
        handler = Handler(thread.looper) { message ->
            onHostMessage(message)
            true
        }
        messenger = Messenger(handler)
    }

    override fun onBind(intent: Intent): IBinder {
        taskId = intent.getStringExtra(IsolationBundles.EXTRA_TASK).orEmpty()
        generation = intent.getIntExtra(IsolationBundles.EXTRA_GENERATION, -1)
        return messenger.binder
    }

    override fun onDestroy() {
        work.shutdownNow()
        thread.quitSafely()
        super.onDestroy()
    }

    private fun onHostMessage(raw: Message) {
        val message = IsolationBundles.decode(raw) ?: return
        if (IsolationProtocol.refusal(message, taskId, generation, lastHostSeq) != null) return
        lastHostSeq = message.seq
        raw.replyTo?.let { host = it }
        when (message.type) {
            IsolationMessageType.CALL -> work.execute { runCall(message) }
            IsolationMessageType.READ_DATA -> reads[message.callSeq]?.offer(message.payload)
            IsolationMessageType.PING -> send(IsolationMessageType.PONG, message.seq)
            IsolationMessageType.FAULT -> inject(message.name)
            else -> Unit
        }
    }

    private fun runCall(call: IsolationMessage) {
        try {
            when (call.name) {
                OP_PROBE_HEADER -> {
                    val header = read(call.seq, 0L, ContainerSniffer.HEADER_BYTES)
                    val format =
                        ContainerSniffer.detect(header, header.size)
                            ?: ImageFormats.sniff(header.copyOf(minOf(header.size, ImageFormats.HEADER_BYTES)))
                    if (format == null) {
                        send(IsolationMessageType.ERROR, call.seq, name = ErrorCode.UNSUPPORTED_CONTAINER.name)
                    } else {
                        send(IsolationMessageType.RESULT, call.seq, payload = format.encodeToByteArray())
                    }
                }

                else -> send(IsolationMessageType.ERROR, call.seq, name = ErrorCode.INVALID_ARGUMENT.name)
            }
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
        } catch (_: Exception) {
            send(IsolationMessageType.ERROR, call.seq, name = ErrorCode.INTERNAL_ERROR_REDACTED.name)
        }
    }

    /** Reads up to [length] bytes at [offset] of the call's source through the host (blocking, bounded wait). */
    private fun read(callSeq: Long, offset: Long, length: Int): ByteArray {
        val queue = LinkedBlockingQueue<ByteArray>()
        reads[callSeq] = queue
        try {
            val out = java.io.ByteArrayOutputStream()
            var position = offset
            while (out.size() < length) {
                val chunk = minOf(IsolationProtocol.MAX_READ_BYTES, length - out.size())
                send(IsolationMessageType.READ_REQUEST, callSeq, offset = position, length = chunk)
                val data = queue.poll(READ_WAIT_MS, TimeUnit.MILLISECONDS) ?: throw IllegalStateException("read timeout")
                if (data.isEmpty()) break
                out.write(data)
                position += data.size
            }
            return out.toByteArray()
        } finally {
            reads.remove(callSeq)
        }
    }

    private fun send(
        type: IsolationMessageType,
        callSeq: Long,
        name: String? = null,
        offset: Long = 0L,
        length: Int = 0,
        payload: ByteArray = ByteArray(0),
        version: Int = IsolationProtocol.VERSION,
    ) {
        val message = IsolationMessage(version, taskId, generation, seq.incrementAndGet(), type, callSeq, name, offset, length, payload)
        try {
            host?.send(IsolationBundles.message(message))
        } catch (_: RemoteException) {
            // The host is gone; the system ends this process with the binding.
        }
    }

    private fun inject(name: String?) {
        when (IsolationFault.entries.firstOrNull { it.name == name }) {
            IsolationFault.CRASH -> Handler(Looper.getMainLooper()).post { throw IllegalStateException("VideoKit injected crash") }

            IsolationFault.OUT_OF_MEMORY -> Thread({
                val hog = ArrayList<ByteArray>()
                while (true) hog += ByteArray(OOM_CHUNK_BYTES)
            }, "videokit-worker-oom").start()

            // The handler thread stops: no more replies, pings time out on the host.
            IsolationFault.HANG -> handler.post { Thread.sleep(Long.MAX_VALUE) }

            IsolationFault.BAD_MESSAGE -> send(IsolationMessageType.RESULT, 0L, version = IsolationProtocol.VERSION + 1)

            null -> Unit
        }
    }

    public companion object {
        /** Operation: container / image format of the source's first bytes (UTF-8 name, or UNSUPPORTED_CONTAINER). */
        public const val OP_PROBE_HEADER: String = "probe.header"

        private const val READ_WAIT_MS = 10_000L
        private const val OOM_CHUNK_BYTES = 16 * 1024 * 1024
    }
}
