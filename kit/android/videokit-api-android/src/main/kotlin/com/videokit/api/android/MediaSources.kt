package com.videokit.api.android

import android.annotation.SuppressLint
import android.content.Context
import android.net.Uri
import android.os.ParcelFileDescriptor
import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Seekability
import com.videokit.api.SourceErrorCode
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceException
import com.videokit.api.VideoKitSourceFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream
import java.io.FileNotFoundException
import java.io.IOException
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.channels.FileChannel
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Optional Android source adapters (04 §5, original requirement §14.3). Hosts may use them for local
 * files, content URIs and file descriptors; core edit plans never depend on these Android types.
 *
 * All reads run on [Dispatchers.IO]. Missing files map to [SourceErrorCode.NOT_FOUND] and security
 * failures to [SourceErrorCode.PERMISSION_DENIED].
 */
public object MediaSources {
    /**
     * A content or file [uri] opened read-only through the application context's content resolver.
     * Only the application context is kept.
     */
    // The descriptor is handed over to the read handle, which closes it in ChannelReadHandle.close().
    @SuppressLint("Recycle")
    public fun fromUri(
        context: Context,
        uri: Uri,
        token: String,
        mediaKind: MediaKind,
        displayName: String? = null,
        mimeType: String? = null,
    ): VideoKitMediaSource {
        val appContext = context.applicationContext ?: context
        return fromFileDescriptor(
            pfdProvider = {
                appContext.contentResolver.openFileDescriptor(uri, "r")
                    ?: throw VideoKitSourceException(SourceErrorCode.NOT_FOUND, "provider returned no descriptor")
            },
            token = token,
            mediaKind = mediaKind,
            displayName = displayName,
            mimeType = mimeType,
        )
    }

    /**
     * A source backed by file descriptors. [pfdProvider] is called once per opened handle; VideoKit
     * closes each descriptor when the handle is closed.
     */
    public fun fromFileDescriptor(
        pfdProvider: suspend () -> ParcelFileDescriptor,
        token: String,
        mediaKind: MediaKind,
        displayName: String? = null,
        mimeType: String? = null,
    ): VideoKitMediaSource = VideoKitMediaSource(
        mediaToken = token,
        mediaKind = mediaKind,
        displayName = displayName,
        mimeType = mimeType,
        seekability = Seekability.RANDOM_ACCESS,
        sourceFactory = VideoKitSourceFactory { _: OpenPurpose ->
            val pfd = withContext(Dispatchers.IO) { mapOpenFailures { pfdProvider() } }
            val stream = FileInputStream(pfd.fileDescriptor)
            ChannelReadHandle(stream.channel) {
                stream.close()
                pfd.close()
            }
        },
    )

    /** A local [file] opened read-only. The display name defaults to `null`; the path is never exposed. */
    public fun fromFile(
        file: File,
        token: String,
        mediaKind: MediaKind,
        displayName: String? = null,
        mimeType: String? = null,
    ): VideoKitMediaSource = VideoKitMediaSource(
        mediaToken = token,
        mediaKind = mediaKind,
        displayName = displayName,
        knownLength = file.length().takeIf { file.isFile },
        mimeType = mimeType,
        extension = file.extension.takeIf { it.isNotEmpty() }?.lowercase(),
        seekability = Seekability.RANDOM_ACCESS,
        sourceFactory = VideoKitSourceFactory { _: OpenPurpose ->
            val raf = withContext(Dispatchers.IO) { mapOpenFailures { RandomAccessFile(file, "r") } }
            ChannelReadHandle(raf.channel) { raf.close() }
        },
    )

    private inline fun <T> mapOpenFailures(block: () -> T): T = try {
        block()
    } catch (e: VideoKitSourceException) {
        throw e
    } catch (e: FileNotFoundException) {
        throw VideoKitSourceException(SourceErrorCode.NOT_FOUND, "source not found", e)
    } catch (e: SecurityException) {
        throw VideoKitSourceException(SourceErrorCode.PERMISSION_DENIED, "source access denied", e)
    }
}

/** Positional reads on a [FileChannel]; thread safe, does not move the channel position. */
internal class ChannelReadHandle(private val channel: FileChannel, private val onClose: () -> Unit) : VideoKitReadHandle {
    private val closed = AtomicBoolean(false)

    override val length: Long?
        get() = if (closed.get()) null else runCatching { channel.size() }.getOrNull()

    override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
        require(offset >= 0) { "offset must not be negative" }
        require(targetOffset >= 0 && length >= 0 && targetOffset + length <= target.size) { "invalid target range" }
        check(!closed.get()) { "read handle is closed" }
        if (length == 0) return 0
        return withContext(Dispatchers.IO) {
            try {
                channel.read(ByteBuffer.wrap(target, targetOffset, length), offset)
            } catch (e: IOException) {
                throw VideoKitSourceException(SourceErrorCode.DISCONNECTED, "read failed", e)
            }
        }
    }

    override fun close() {
        if (closed.compareAndSet(false, true)) onClose()
    }
}
