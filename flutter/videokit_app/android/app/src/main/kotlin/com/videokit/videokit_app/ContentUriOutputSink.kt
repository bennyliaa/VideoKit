package com.videokit.videokit_app

import android.content.Context
import android.net.Uri
import android.os.ParcelFileDescriptor
import android.provider.DocumentsContract
import com.videokit.api.OutputOpenRequest
import com.videokit.api.SinkCapabilities
import com.videokit.api.SinkErrorCode
import com.videokit.api.VideoKitAbortReason
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitOutputToken
import com.videokit.api.VideoKitSinkException
import com.videokit.api.VideoKitWriteHandle
import com.videokit.api.android.FileDescriptorWriteHandle
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileNotFoundException
import java.io.IOException
import java.io.RandomAccessFile
import java.util.concurrent.ConcurrentHashMap
import kotlin.random.Random

/**
 * Export "另存为" sink of the App (REQ-APP-03 export part, 08 §5): one output for one document the user chose
 * with `ACTION_CREATE_DOCUMENT`.
 *
 * VideoKit writes a private temporary file (`cacheDir/exports`, descriptor and random access, so the muxer can
 * finalize in place). Only after VideoKit has verified the output ([markReady]) is it copied to [target]; a
 * cancelled or failed export ([abort]) deletes the temporary file and, best effort, the empty document. The
 * token is the document URI. [onFinished] runs once after `markReady` or `abort` (the channel unregisters the
 * sink there).
 */
class ContentUriOutputSink(
    context: Context,
    private val target: Uri,
    private val onFinished: () -> Unit,
) : VideoKitOutputSink {
    private val appContext = context.applicationContext
    private val handles = ConcurrentHashMap<String, TempFileHandle>()

    @Volatile
    private var finished = false

    override val capabilities: SinkCapabilities
        get() = SinkCapabilities(
            sequentialWrite = true,
            randomWrite = true,
            fileDescriptor = true,
            flush = true,
            knownFreeSpaceBytes = exportDir(appContext).usableSpace.takeIf { it > 0 },
        )

    override suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle = withContext(Dispatchers.IO) {
        if (finished || handles.isNotEmpty()) {
            throw VideoKitSinkException(SinkErrorCode.CAPABILITY_UNSUPPORTED, "one output per save-as sink")
        }
        val dir = exportDir(appContext)
        if (!dir.isDirectory && !dir.mkdirs()) throw VideoKitSinkException(SinkErrorCode.IO_FAILED, "export dir")
        val estimated = request.estimatedBytes
        if (estimated != null && estimated > dir.usableSpace) {
            throw VideoKitSinkException(SinkErrorCode.SPACE_INSUFFICIENT)
        }
        val file = try {
            File.createTempFile(TEMP_PREFIX, TEMP_SUFFIX, dir)
        } catch (e: IOException) {
            throw sinkError(e)
        }
        val handle = TempFileHandle("handle-" + Random.nextLong().toULong().toString(16), file)
        handles[handle.handleId] = handle
        handle
    }

    override suspend fun markReady(handleId: String, metadata: VideoKitOutputMetadata): VideoKitOutputToken =
        withContext(Dispatchers.IO) {
            val handle = handles.remove(handleId)
                ?: throw VideoKitSinkException(SinkErrorCode.IO_FAILED, "unknown handle")
            try {
                handle.close()
                copyToTarget(handle.file)
                VideoKitOutputToken(target.toString())
            } catch (e: VideoKitSinkException) {
                deleteTarget()
                throw e
            } finally {
                handle.file.delete()
                finish()
            }
        }

    override suspend fun abort(handleId: String, reason: VideoKitAbortReason) {
        withContext(Dispatchers.IO) {
            handles.remove(handleId)?.let {
                it.close()
                it.file.delete()
            }
            deleteTarget()
            finish()
        }
    }

    private fun copyToTarget(file: File) {
        val resolver = appContext.contentResolver
        try {
            // "wt": truncate, so a document chosen again is fully replaced.
            val out = resolver.openOutputStream(target, "wt")
                ?: throw VideoKitSinkException(SinkErrorCode.IO_FAILED, "no output stream")
            out.use { stream -> file.inputStream().use { it.copyTo(stream, COPY_BUFFER) } }
        } catch (e: SecurityException) {
            throw VideoKitSinkException(SinkErrorCode.PERMISSION_DENIED, "target not writable", e)
        } catch (e: FileNotFoundException) {
            throw VideoKitSinkException(SinkErrorCode.PERMISSION_DENIED, "target gone", e)
        } catch (e: IOException) {
            throw sinkError(e)
        }
    }

    private fun deleteTarget() {
        runCatching { DocumentsContract.deleteDocument(appContext.contentResolver, target) }
    }

    private fun finish() {
        if (finished) return
        finished = true
        onFinished()
    }

    /** Private temporary output with a read/write descriptor. Closing is idempotent. */
    private class TempFileHandle(override val handleId: String, val file: File) : FileDescriptorWriteHandle {
        private val lock = Any()
        private val raf = RandomAccessFile(file, "rw")
        private var descriptor: ParcelFileDescriptor? = null
        private var closed = false

        override fun fileDescriptor(): ParcelFileDescriptor = synchronized(lock) {
            check(!closed) { "handle closed" }
            descriptor ?: ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_WRITE).also { descriptor = it }
        }

        override suspend fun write(data: ByteArray, offset: Int, length: Int) = withContext(Dispatchers.IO) {
            io {
                raf.seek(raf.length())
                raf.write(data, offset, length)
            }
        }

        override suspend fun writeAt(position: Long, data: ByteArray, offset: Int, length: Int) =
            withContext(Dispatchers.IO) {
                io {
                    raf.seek(position)
                    raf.write(data, offset, length)
                }
            }

        override suspend fun flush() = withContext(Dispatchers.IO) {
            io {
                raf.fd.sync()
                descriptor?.fileDescriptor?.sync()
            }
        }

        override fun close() {
            synchronized(lock) {
                if (closed) return
                closed = true
                runCatching { descriptor?.close() }
                runCatching { raf.close() }
            }
        }

        private inline fun io(block: () -> Unit) = synchronized(lock) {
            if (closed) throw VideoKitSinkException(SinkErrorCode.IO_FAILED, "handle closed")
            try {
                block()
            } catch (e: IOException) {
                throw sinkError(e)
            }
        }
    }

    companion object {
        private const val TEMP_PREFIX = "export-"
        private const val TEMP_SUFFIX = ".part"
        private const val COPY_BUFFER = 1 shl 16

        /** App-private directory of export temporaries. */
        fun exportDir(context: Context): File = File(context.cacheDir, "exports")

        /** Deletes temporaries a killed process left behind (called before any export can run). */
        fun deleteStaleTemporaries(context: Context) {
            exportDir(context).listFiles()?.forEach {
                if (it.name.startsWith(TEMP_PREFIX) && it.name.endsWith(TEMP_SUFFIX)) it.delete()
            }
        }

        private fun sinkError(e: IOException): VideoKitSinkException {
            val message = e.message.orEmpty()
            val code = if ("ENOSPC" in message || "No space" in message) {
                SinkErrorCode.SPACE_INSUFFICIENT
            } else {
                SinkErrorCode.IO_FAILED
            }
            return VideoKitSinkException(code, e.javaClass.simpleName, e)
        }
    }
}

/**
 * Precheck-only sink `registered:app-export`: reports the capabilities and free space of the save-as sinks so
 * `checkExport` can run before the user chose a document. It never opens an output.
 */
class PrecheckOutputSink(context: Context) : VideoKitOutputSink {
    private val appContext = context.applicationContext

    override val capabilities: SinkCapabilities
        get() = SinkCapabilities(
            sequentialWrite = true,
            randomWrite = true,
            fileDescriptor = true,
            flush = true,
            knownFreeSpaceBytes = ContentUriOutputSink.exportDir(appContext).let { dir ->
                (if (dir.isDirectory) dir else appContext.cacheDir).usableSpace.takeIf { it > 0 }
            },
        )

    override suspend fun openTemporary(request: OutputOpenRequest): VideoKitWriteHandle =
        throw VideoKitSinkException(SinkErrorCode.CAPABILITY_UNSUPPORTED, "precheck sink; choose a document first")

    override suspend fun markReady(handleId: String, metadata: VideoKitOutputMetadata): VideoKitOutputToken =
        throw VideoKitSinkException(SinkErrorCode.IO_FAILED, "unknown handle")

    override suspend fun abort(handleId: String, reason: VideoKitAbortReason) = Unit
}
