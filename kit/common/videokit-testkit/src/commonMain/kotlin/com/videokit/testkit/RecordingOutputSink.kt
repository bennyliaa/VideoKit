package com.videokit.testkit

import com.videokit.api.OutputOpenRequest
import com.videokit.api.SinkCapabilities
import com.videokit.api.SinkErrorCode
import com.videokit.api.VideoKitAbortReason
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitOutputToken
import com.videokit.api.VideoKitSinkException
import com.videokit.api.VideoKitWriteHandle
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.AtomicFlag
import com.videokit.testkit.internal.RecordList
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.concurrent.Volatile

/** Fault injected into a [RecordingOutputSink]. */
public sealed interface SinkFault {
    /** `openTemporary` throws [code]. */
    public data class FailOnOpen(
        /** Code. */
        val code: SinkErrorCode,
    ) : SinkFault

    /** `write` throws [code] once more than [afterBytes] bytes were written. */
    public data class FailOnWrite(
        /** Code. */
        val code: SinkErrorCode,
        /** Bytes accepted before failing. */
        val afterBytes: Long = 0L,
    ) : SinkFault

    /** `markReady` throws [code]. */
    public data class FailOnMarkReady(
        /** Code. */
        val code: SinkErrorCode,
    ) : SinkFault
}

/**
 * In-memory [VideoKitOutputSink] that records every call (opened outputs, written bytes, markReady and
 * abort), for tests and the demo host's temporary sink. All record lists are immutable snapshots.
 */
public class RecordingOutputSink(
    override val capabilities: SinkCapabilities = SinkCapabilities(sequentialWrite = true, randomWrite = true),
    /** Optional injected fault. */
    public val fault: SinkFault? = null,
) : VideoKitOutputSink {
    private val ids = AtomicCounter()
    private val openRecord = RecordList<OutputOpenRequest>()
    private val handleRecord = RecordList<RecordingWriteHandle>()
    private val readyRecord = RecordList<Pair<String, VideoKitOutputMetadata>>()
    private val abortRecord = RecordList<Pair<String, VideoKitAbortReason>>()

    /** Open requests in order. */
    public val openRequests: List<OutputOpenRequest> get() = openRecord.snapshot

    /** Handles in order of opening. */
    public val handles: List<RecordingWriteHandle> get() = handleRecord.snapshot

    /** `markReady` calls: handle id and metadata. */
    public val readyCalls: List<Pair<String, VideoKitOutputMetadata>> get() = readyRecord.snapshot

    /** `abort` calls: handle id and reason. */
    public val abortCalls: List<Pair<String, VideoKitAbortReason>> get() = abortRecord.snapshot

    override suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle {
        openRecord.add(request)
        (fault as? SinkFault.FailOnOpen)?.let { throw VideoKitSinkException(it.code) }
        val handle = RecordingWriteHandle("out-${ids.incrementAndGet()}", fault as? SinkFault.FailOnWrite)
        handleRecord.add(handle)
        return handle
    }

    override suspend fun markReady(handleId: String, metadata: VideoKitOutputMetadata): VideoKitOutputToken {
        (fault as? SinkFault.FailOnMarkReady)?.let { throw VideoKitSinkException(it.code) }
        readyRecord.add(handleId to metadata)
        return VideoKitOutputToken("token-$handleId")
    }

    override suspend fun abort(handleId: String, reason: VideoKitAbortReason) {
        abortRecord.add(handleId to reason)
    }
}

/** Write handle of a [RecordingOutputSink]. */
public class RecordingWriteHandle internal constructor(override val handleId: String, private val failure: SinkFault.FailOnWrite?) :
    VideoKitWriteHandle {
    private val mutex = Mutex()
    private val closedFlag = AtomicFlag()

    @Volatile
    private var data = ByteArray(0)

    @Volatile
    private var randomWrites = 0

    /** Bytes written so far (copy). */
    public val bytes: ByteArray get() = data.copyOf()

    /** Number of `writeAt` calls. */
    public val randomWriteCount: Int get() = randomWrites

    /** Whether the handle was closed. */
    public val closed: Boolean get() = closedFlag.value

    override suspend fun write(data: ByteArray, offset: Int, length: Int) {
        check(!closedFlag.value) { "write after close" }
        mutex.withLock {
            val current = this.data
            if (failure != null && current.size + length > failure.afterBytes) throw VideoKitSinkException(failure.code)
            this.data = current + data.copyOfRange(offset, offset + length)
        }
    }

    override suspend fun writeAt(position: Long, data: ByteArray, offset: Int, length: Int) {
        check(!closedFlag.value) { "write after close" }
        mutex.withLock {
            randomWrites++
            val current = this.data
            val end = maxOf(current.size.toLong(), position + length).toInt()
            val updated = current.copyOf(end)
            data.copyInto(updated, position.toInt(), offset, offset + length)
            this.data = updated
        }
    }

    override suspend fun flush(): Unit = Unit

    override fun close() {
        closedFlag.setOnce()
    }
}
