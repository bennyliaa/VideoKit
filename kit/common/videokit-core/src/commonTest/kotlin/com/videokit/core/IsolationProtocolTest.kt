package com.videokit.core

import com.videokit.api.ErrorCode
import com.videokit.core.runtime.IsolatedCalls
import com.videokit.core.runtime.IsolationMessage
import com.videokit.core.runtime.IsolationMessageType
import com.videokit.core.runtime.IsolationProtocol
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** Isolation protocol of 07 §5.2: version, task, generation, sequence and size checks; failure of the task only. */
class IsolationProtocolTest {
    private fun reply(
        seq: Long,
        callSeq: Long,
        type: IsolationMessageType = IsolationMessageType.RESULT,
        generation: Int = 3,
        version: Int = IsolationProtocol.VERSION,
        task: String = "t1",
        payload: ByteArray = byteArrayOf(1, 2),
        name: String? = null,
        length: Int = 0,
    ) = IsolationMessage(version, task, generation, seq, type, callSeq, name, length = length, payload = payload)

    @Test
    fun resultsReachTheirCall() = runTest {
        val calls = IsolatedCalls("t1", generation = 3)
        val call = calls.outgoing(IsolationMessageType.CALL, name = "probe.header")
        val answer = calls.register(call)
        assertEquals(1, calls.pendingCalls)
        val read =
            assertIs<IsolatedCalls.Incoming.Read>(calls.onMessage(reply(1, call.seq, IsolationMessageType.READ_REQUEST, length = 4096)))
        assertEquals(4096, read.length)
        assertEquals(call.seq, calls.readData(call.seq, ByteArray(10)).callSeq)
        assertEquals(IsolatedCalls.Incoming.Delivered, calls.onMessage(reply(2, call.seq)))
        assertContentEquals(byteArrayOf(1, 2), calls.resultOf(answer.await()))
        assertEquals(0, calls.pendingCalls)
    }

    @Test
    fun errorsCarryTheWorkersStableCode() = runTest {
        val calls = IsolatedCalls("t1", 3)
        val call = calls.outgoing(IsolationMessageType.CALL, name = "probe.header")
        val answer = calls.register(call)
        calls.onMessage(reply(1, call.seq, IsolationMessageType.ERROR, name = "UNSUPPORTED_CONTAINER", payload = ByteArray(0)))
        val failure = assertFailsWith<SpiException> { calls.resultOf(answer.await()) }
        assertEquals(ErrorCode.UNSUPPORTED_CONTAINER, failure.error.code)
        // The task keeps working after a stable error.
        assertTrue(!calls.failed)
    }

    @Test
    fun invalidMessagesFailTheTask() = runTest {
        val cases = listOf(
            "VERSION" to { c: Long -> reply(1, c, version = 99) },
            "TASK" to { c: Long -> reply(1, c, task = "other") },
            "STALE_GENERATION" to { c: Long -> reply(1, c, generation = 2) },
            "PAYLOAD" to { c: Long -> reply(1, c, payload = ByteArray(IsolationProtocol.MAX_PAYLOAD_BYTES + 1)) },
            "READ_BOUNDS" to { c: Long -> reply(1, c, IsolationMessageType.READ_REQUEST, length = IsolationProtocol.MAX_READ_BYTES + 1) },
            "UNKNOWN_CALL" to { c: Long -> reply(1, c + 100) },
            "TYPE" to { c: Long -> reply(1, c, IsolationMessageType.CALL) },
        )
        for ((reason, message) in cases) {
            val calls = IsolatedCalls("t1", 3)
            val call = calls.outgoing(IsolationMessageType.CALL, name = "x")
            val answer = calls.register(call)
            val refused = assertIs<IsolatedCalls.Incoming.Refused>(calls.onMessage(message(call.seq)), reason)
            assertTrue(reason in refused.reason, "$reason: ${refused.reason}")
            assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, assertFailsWith<SpiException> { answer.await() }.error.code)
            assertTrue(calls.failed)
            // Later calls fail at once; nothing is replayed.
            val later = calls.register(calls.outgoing(IsolationMessageType.CALL, name = "x"))
            assertFailsWith<SpiException> { later.await() }
        }
    }

    @Test
    fun repeatedOrOldSequenceNumbersAreRefused() = runTest {
        val calls = IsolatedCalls("t1", 3)
        val first = calls.outgoing(IsolationMessageType.CALL, name = "x")
        calls.register(first)
        val second = calls.outgoing(IsolationMessageType.CALL, name = "x")
        calls.register(second)
        assertEquals(IsolatedCalls.Incoming.Delivered, calls.onMessage(reply(5, first.seq)))
        assertIs<IsolatedCalls.Incoming.Refused>(calls.onMessage(reply(5, second.seq)))
    }

    @Test
    fun deathFailsPendingCalls() = runTest {
        val calls = IsolatedCalls("t1", 1)
        val answer = calls.register(calls.outgoing(IsolationMessageType.CALL, name = "x"))
        calls.fail("CRASHED")
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, assertFailsWith<SpiException> { answer.await() }.error.code)
        assertEquals(IsolatedCalls.Incoming.Refused("FAILED"), calls.onMessage(reply(1, 1)))
    }

    @Test
    fun refusalIsNullForAValidMessage() {
        assertNull(IsolationProtocol.refusal(reply(2, 1), "t1", 3, lastSeq = 1))
        assertEquals("GENERATION:4", IsolationProtocol.refusal(reply(2, 1, generation = 4), "t1", 3, lastSeq = 1))
    }
}
