package com.videokit.export.android

import android.net.Uri
import android.os.Binder
import android.os.IBinder
import android.os.Parcel
import android.os.Process
import android.os.RemoteException
import androidx.media3.common.C
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.BaseDataSource
import androidx.media3.datasource.DataSpec
import com.videokit.api.VideoKitReadHandle
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import java.io.IOException
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

/**
 * Main process side of the export input (15 §2.8: the export input is read in the main process through the host
 * `readAt`, S4): serves [handle] over binder, at most [WorkerProtocol.MAX_READ] bytes per call. The worker has the app
 * uid (option c1), so callers are told apart by pid: the main process itself is refused, the first other caller is
 * pinned, later callers with another pid are refused. [revoke] ends all access (task end, cancel, kill).
 *
 * Binder threads block on the suspending host read, bounded by [readTimeoutMs]; a host read that does not return is
 * a read failure for the worker, which then fails the export instead of hanging.
 */
internal class SourceBroker(private val handle: VideoKitReadHandle, private val readTimeoutMs: Long) : Binder() {
    private val pinnedPid = AtomicInteger()
    val bytesRead = AtomicLong()
    val calls = AtomicInteger()

    @Volatile var revoked = false
        private set

    fun revoke() {
        revoked = true
    }

    override fun onTransact(code: Int, data: Parcel, reply: Parcel?, flags: Int): Boolean {
        if (code != WorkerProtocol.BROKER_READ && code != WorkerProtocol.BROKER_LENGTH) return super.onTransact(code, data, reply, flags)
        data.enforceInterface(WorkerProtocol.BROKER_DESCRIPTOR)
        val out = reply ?: return true
        val caller = getCallingPid()
        val allowed = caller != Process.myPid() && (pinnedPid.compareAndSet(0, caller) || pinnedPid.get() == caller)
        if (!allowed || revoked) {
            out.writeException(SecurityException(if (revoked) "REVOKED" else "CALLER_REJECTED"))
            return true
        }
        calls.incrementAndGet()
        try {
            if (code == WorkerProtocol.BROKER_LENGTH) {
                out.writeNoException()
                out.writeLong(handle.length ?: -1L)
                return true
            }
            val offset = data.readLong()
            val length = data.readInt().coerceIn(0, WorkerProtocol.MAX_READ)
            val buffer = ByteArray(length)
            val read = runBlocking { withTimeout(readTimeoutMs) { handle.readAt(offset, buffer, 0, length) } }
            out.writeNoException()
            out.writeInt(read)
            out.writeByteArray(if (read > 0) buffer.copyOf(read) else ByteArray(0))
            if (read > 0) bytesRead.addAndGet(read.toLong())
        } catch (failure: Exception) {
            // Never the message: it may contain a path.
            out.writeException(IllegalStateException("READ_FAILED"))
        }
        return true
    }
}

/** Worker side: a Media3 [BaseDataSource] reading through the [SourceBroker] binder (S4 `BrokerDataSource`). */
@UnstableApi
internal class BrokerDataSource(private val broker: IBinder) : BaseDataSource(false) {
    private var uri: Uri? = null
    private var position = 0L
    private var remaining = 0L

    override fun open(dataSpec: DataSpec): Long {
        transferInitializing(dataSpec)
        val reply = call(WorkerProtocol.BROKER_LENGTH) { }
        val length = reply.readLong()
        reply.recycle()
        uri = dataSpec.uri
        position = dataSpec.position
        remaining = when {
            dataSpec.length != C.LENGTH_UNSET.toLong() -> dataSpec.length
            length >= 0 -> length - position
            else -> C.LENGTH_UNSET.toLong()
        }
        transferStarted(dataSpec)
        return remaining
    }

    override fun read(buffer: ByteArray, offset: Int, length: Int): Int {
        if (length == 0) return 0
        if (remaining == 0L) return C.RESULT_END_OF_INPUT
        val cap = if (remaining == C.LENGTH_UNSET.toLong()) Long.MAX_VALUE else remaining
        val wanted = minOf(length.toLong(), cap, WorkerProtocol.MAX_READ.toLong()).toInt()
        val reply = call(WorkerProtocol.BROKER_READ) {
            writeLong(position)
            writeInt(wanted)
        }
        val read = reply.readInt()
        val data = reply.createByteArray() ?: ByteArray(0)
        reply.recycle()
        if (read <= 0) return C.RESULT_END_OF_INPUT
        if (read > wanted || data.size != read) throw IOException("INVALID_READ")
        System.arraycopy(data, 0, buffer, offset, read)
        position += read
        if (remaining != C.LENGTH_UNSET.toLong()) remaining -= read
        bytesTransferred(read)
        return read
    }

    override fun getUri(): Uri? = uri

    override fun close() {
        if (uri != null) transferEnded()
        uri = null
    }

    private inline fun call(code: Int, write: Parcel.() -> Unit): Parcel {
        val data = Parcel.obtain()
        val reply = Parcel.obtain()
        try {
            data.writeInterfaceToken(WorkerProtocol.BROKER_DESCRIPTOR)
            data.write()
            if (!broker.transact(code, data, reply, 0)) throw IOException("BROKER_PROTOCOL")
            reply.readException()
            return reply
        } catch (gone: RemoteException) {
            reply.recycle()
            throw IOException("SOURCE_DISCONNECTED")
        } catch (failure: RuntimeException) {
            reply.recycle()
            throw IOException("SOURCE_IO_FAILED")
        } finally {
            data.recycle()
        }
    }
}
