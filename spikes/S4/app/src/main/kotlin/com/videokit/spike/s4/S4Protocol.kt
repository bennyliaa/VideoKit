package com.videokit.spike.s4

import android.net.Uri
import android.os.Binder
import android.os.IBinder
import android.os.Parcel
import android.os.RemoteException
import androidx.media3.common.C
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.BaseDataSource
import androidx.media3.datasource.DataSpec
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

/** Messages between the main process and the export worker (Messenger `what` codes and Bundle keys). */
object S4Protocol {
    const val START = 1
    const val CANCEL = 2
    const val STARTED = 10
    const val SAMPLE = 11
    const val DONE = 12
    const val ERROR = 13
    const val CANCELLED = 14

    const val KEY_TASK = "task"
    const val KEY_BROKER = "broker"
    const val KEY_OUTPUT = "output"
    const val KEY_FAULT = "fault"
    const val KEY_CLIP_MS = "clipMs"
    const val KEY_CODE = "code"
    const val KEY_SAMPLES = "samples"
    const val KEY_BYTES = "bytes"
    const val KEY_LOADER = "loader"
    const val KEY_PID = "pid"
    const val KEY_PROBE = "probe"

    /** Worker to main: one decode probe step result (attempt 4), in KEY_CODE. */
    const val PROBE = 15

    /**
     * Asset loaders of the worker. From attempt 5 (option c1, non-isolated) the default is [LOADER_EXO], the Media3
     * ExoPlayer asset loader the Kit export will use; in the isolated attempts it blocked on media.audio_flinger (2).
     * [LOADER_JAVA] (pure-Java extractors, attempt 4) and [LOADER_EXTRACTOR] (platform MediaExtractor, attempt 3) stay
     * for comparison.
     */
    const val LOADER_EXO = "EXO"
    const val LOADER_JAVA = "JAVA"
    const val LOADER_EXTRACTOR = "EXTRACTOR"

    /** Faults injected in the worker after its first written video sample (15 §4 S4). */
    enum class Fault { NONE, CANCEL, SIGSEGV, OOM, LOOP, KILL }

    const val BROKER_DESCRIPTOR = "com.videokit.spike.s4.Broker"
    const val BROKER_READ = IBinder.FIRST_CALL_TRANSACTION
    const val BROKER_LENGTH = IBinder.FIRST_CALL_TRANSACTION + 1
    const val MAX_READ = 64 * 1024
}

/**
 * Main process side of the input proxy: the worker has no file access; it reads the source through this binder,
 * bounded to [S4Protocol.MAX_READ] per call. Stands in for the host `readAt` (the export input of 15 §2.8 is read in the
 * main process). The worker has the app uid (option c1), so callers are told apart by pid: the main process itself is
 * refused, the first other caller is pinned and every later caller with another pid is refused.
 */
class InputBroker(private val file: File) : Binder() {
    private val channel = RandomAccessFile(file, "r").channel
    val reads = AtomicLong()
    val calls = AtomicInteger()
    private val pinnedPid = AtomicInteger()

    @Volatile var revoked = false
        private set

    fun revoke() {
        revoked = true
        runCatching { channel.close() }
    }

    override fun onTransact(code: Int, data: Parcel, reply: Parcel?, flags: Int): Boolean {
        if (code != S4Protocol.BROKER_READ && code != S4Protocol.BROKER_LENGTH) return super.onTransact(code, data, reply, flags)
        data.enforceInterface(S4Protocol.BROKER_DESCRIPTOR)
        val out = reply ?: return true
        val caller = getCallingPid()
        val allowed = caller != android.os.Process.myPid() && (pinnedPid.compareAndSet(0, caller) || pinnedPid.get() == caller)
        if (!allowed || revoked) {
            out.writeException(SecurityException(if (revoked) "REVOKED" else "CALLER_REJECTED"))
            return true
        }
        calls.incrementAndGet()
        try {
            if (code == S4Protocol.BROKER_LENGTH) {
                out.writeNoException()
                out.writeLong(file.length())
                return true
            }
            val offset = data.readLong()
            val length = data.readInt().coerceIn(0, S4Protocol.MAX_READ)
            val buffer = java.nio.ByteBuffer.allocate(length)
            val read = channel.read(buffer, offset)
            out.writeNoException()
            out.writeInt(read)
            out.writeByteArray(if (read > 0) buffer.array().copyOf(read) else ByteArray(0))
            if (read > 0) reads.addAndGet(read.toLong())
        } catch (failure: Exception) {
            out.writeException(IllegalStateException("READ_FAILED"))
        }
        return true
    }
}

/** Worker side: a Media3 [BaseDataSource] reading through the [InputBroker] binder. */
@UnstableApi
class BrokerDataSource(private val broker: IBinder) : BaseDataSource(false) {
    private var uri: Uri? = null
    private var position = 0L
    private var remaining = 0L

    override fun open(dataSpec: DataSpec): Long {
        transferInitializing(dataSpec)
        val length = call(S4Protocol.BROKER_LENGTH) { }.readLong()
        uri = dataSpec.uri
        position = dataSpec.position
        remaining = if (dataSpec.length != C.LENGTH_UNSET.toLong()) dataSpec.length else length - position
        transferStarted(dataSpec)
        return remaining
    }

    override fun read(buffer: ByteArray, offset: Int, length: Int): Int {
        if (length == 0) return 0
        if (remaining == 0L) return C.RESULT_END_OF_INPUT
        val wanted = minOf(length.toLong(), remaining, S4Protocol.MAX_READ.toLong()).toInt()
        val reply = call(S4Protocol.BROKER_READ) {
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
        remaining -= read
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
            data.writeInterfaceToken(S4Protocol.BROKER_DESCRIPTOR)
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
