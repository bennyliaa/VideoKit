package com.videokit.core.runtime

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.VideoKitStableError
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.flow.updateAndGet

/** Message types between the host process and an isolated worker (07 §5.2). */
public enum class IsolationMessageType {
    /** Host → worker: run an operation. */
    CALL,

    /** Worker → host: result of a call. */
    RESULT,

    /** Worker → host: stable error of a call. */
    ERROR,

    /** Worker → host: read bytes of the call's source (the worker has no file access). */
    READ_REQUEST,

    /** Host → worker: the bytes of a read request (empty at the end of the source). */
    READ_DATA,

    /** Host → worker: inject a fault. */
    FAULT,

    /** Host → worker: liveness check. */
    PING,

    /** Worker → host: answer to a ping. */
    PONG,
}

/**
 * One protocol message. Every message carries the protocol [version], the [taskId], the worker [generation], the
 * sender's strictly increasing [seq] and the [callSeq] of the call it belongs to (07 §5.2).
 */
public class IsolationMessage(
    /** Protocol version. */
    public val version: Int,
    /** Task id. */
    public val taskId: String,
    /** Worker generation. */
    public val generation: Int,
    /** Sender sequence number, strictly increasing per direction. */
    public val seq: Long,
    /** Type. */
    public val type: IsolationMessageType,
    /** Sequence number of the call this message belongs to (the call itself for CALL). */
    public val callSeq: Long = seq,
    /** Operation of a CALL, the fault name of a FAULT, the error code of an ERROR. */
    public val name: String? = null,
    /** Offset of a READ_REQUEST. */
    public val offset: Long = 0L,
    /** Length of a READ_REQUEST. */
    public val length: Int = 0,
    /** Payload (call arguments, result, read data). */
    public val payload: ByteArray = ByteArray(0),
)

/** Validation rules of the isolation protocol, shared by both sides (07 §5.2: version, task, generation, seq, length). */
public object IsolationProtocol {
    /** Current protocol version. */
    public const val VERSION: Int = 1

    /** Largest payload of one message. */
    public const val MAX_PAYLOAD_BYTES: Int = 256 * 1024

    /** Largest read of one READ_REQUEST. */
    public const val MAX_READ_BYTES: Int = 64 * 1024

    /** Longest operation / fault / error name. */
    public const val MAX_NAME_LENGTH: Int = 64

    /**
     * Why [message] must be refused by a receiver that expects [taskId] and [generation] and last accepted
     * [lastSeq] from this sender, or `null` when it is valid.
     */
    public fun refusal(message: IsolationMessage, taskId: String, generation: Int, lastSeq: Long): String? = when {
        message.version != VERSION -> "VERSION:${message.version}"
        message.taskId != taskId -> "TASK"
        message.generation < generation -> "STALE_GENERATION:${message.generation}"
        message.generation != generation -> "GENERATION:${message.generation}"
        message.seq <= lastSeq -> "SEQ:${message.seq}"
        message.payload.size > MAX_PAYLOAD_BYTES -> "PAYLOAD:${message.payload.size}"
        (message.name?.length ?: 0) > MAX_NAME_LENGTH -> "NAME"
        message.type == IsolationMessageType.READ_REQUEST && (message.length !in 1..MAX_READ_BYTES || message.offset < 0) -> "READ_BOUNDS"
        else -> null
    }
}

/**
 * Host side bookkeeping of one isolated task: sequence numbers, pending calls, validation of everything the worker
 * sends and the failure of all pending calls when the worker dies or misbehaves (07 §5.2: only this task fails, no
 * replay). Platform transports (Android: Messenger) deliver the messages; this class makes the decisions.
 */
public class IsolatedCalls(
    /** Task id. */
    public val taskId: String,
    /** Worker generation. */
    public val generation: Int,
) {
    private val state = MutableStateFlow(State())

    private class State(
        val nextSeq: Long = 0L,
        val lastWorkerSeq: Long = 0L,
        val failure: VideoKitStableError? = null,
        val pending: Map<Long, CompletableDeferred<IsolationMessage>> = emptyMap(),
    ) {
        fun copy(
            nextSeq: Long = this.nextSeq,
            lastWorkerSeq: Long = this.lastWorkerSeq,
            failure: VideoKitStableError? = this.failure,
            pending: Map<Long, CompletableDeferred<IsolationMessage>> = this.pending,
        ) = State(nextSeq, lastWorkerSeq, failure, pending)
    }

    /** What the transport must do with a message from the worker. */
    public sealed interface Incoming {
        /** Delivered to its pending call (nothing else to do). */
        public data object Delivered : Incoming

        /** The worker asks for source bytes of a pending call; answer with [readData]. */
        public data class Read(val callSeq: Long, val offset: Long, val length: Int) : Incoming

        /** A valid PONG. */
        public data object Pong : Incoming

        /** Invalid message: the task is failed (all pending calls fail); stop the worker. */
        public data class Refused(val reason: String) : Incoming
    }

    /** A new outgoing message (sequence assigned). */
    public fun outgoing(
        type: IsolationMessageType,
        callSeq: Long? = null,
        name: String? = null,
        payload: ByteArray = ByteArray(0),
    ): IsolationMessage {
        val seq = state.updateAndGet { it.copy(nextSeq = it.nextSeq + 1) }.nextSeq
        return IsolationMessage(IsolationProtocol.VERSION, taskId, generation, seq, type, callSeq ?: seq, name, payload = payload)
    }

    /** Registers [call] (a CALL from [outgoing]) and returns its answer; fails at once when the task already failed. */
    public fun register(call: IsolationMessage): CompletableDeferred<IsolationMessage> {
        val answer = CompletableDeferred<IsolationMessage>()
        val after = state.updateAndGet { if (it.failure != null) it else it.copy(pending = it.pending + (call.seq to answer)) }
        after.failure?.let { answer.completeExceptionally(SpiException(it)) }
        return answer
    }

    /** A message from the worker. */
    public fun onMessage(message: IsolationMessage): Incoming {
        while (true) {
            val current = state.value
            if (current.failure != null) return Incoming.Refused("FAILED")
            val refusal = IsolationProtocol.refusal(message, taskId, generation, current.lastWorkerSeq)
            if (refusal != null) return refuse("PROTOCOL:$refusal")
            val accepted = current.copy(lastWorkerSeq = message.seq)
            when (message.type) {
                IsolationMessageType.RESULT, IsolationMessageType.ERROR -> {
                    val call = current.pending[message.callSeq] ?: return refuse("PROTOCOL:UNKNOWN_CALL")
                    if (!state.compareAndSet(current, accepted.copy(pending = current.pending - message.callSeq))) continue
                    call.complete(message)
                    return Incoming.Delivered
                }

                IsolationMessageType.READ_REQUEST -> {
                    if (message.callSeq !in current.pending) return refuse("PROTOCOL:UNKNOWN_CALL")
                    if (!state.compareAndSet(current, accepted)) continue
                    return Incoming.Read(message.callSeq, message.offset, message.length)
                }

                IsolationMessageType.PONG -> {
                    if (!state.compareAndSet(current, accepted)) continue
                    return Incoming.Pong
                }

                else -> return refuse("PROTOCOL:TYPE:${message.type}")
            }
        }
    }

    /** The answer to a [Incoming.Read]. */
    public fun readData(callSeq: Long, bytes: ByteArray): IsolationMessage =
        outgoing(IsolationMessageType.READ_DATA, callSeq = callSeq, payload = bytes)

    /** The worker died or stopped answering: every pending and later call fails with [reason]. */
    public fun fail(reason: String) {
        val error = StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, "ISOLATED:$reason")
        var failed: Collection<CompletableDeferred<IsolationMessage>> = emptyList()
        state.update { current ->
            if (current.failure != null) {
                failed = emptyList()
                current
            } else {
                failed = current.pending.values
                current.copy(failure = error, pending = emptyMap())
            }
        }
        failed.forEach { it.completeExceptionally(SpiException(error)) }
    }

    /** Number of pending calls (diagnostics). */
    public val pendingCalls: Int get() = state.value.pending.size

    /** Whether the task failed. */
    public val failed: Boolean get() = state.value.failure != null

    private fun refuse(reason: String): Incoming {
        fail(reason)
        return Incoming.Refused(reason)
    }

    /** Result bytes of a RESULT, or the [SpiException] of an ERROR. */
    public fun resultOf(answer: IsolationMessage): ByteArray {
        if (answer.type == IsolationMessageType.RESULT) return answer.payload
        val code = answer.name?.let { ErrorCode.fromWireName(it) } ?: ErrorCode.INTERNAL_ERROR_REDACTED
        throw SpiException(StableErrors.of(code, ErrorStage.UNKNOWN, "ISOLATED_ERROR"))
    }
}
