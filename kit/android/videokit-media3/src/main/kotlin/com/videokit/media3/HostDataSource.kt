package com.videokit.media3

import android.net.Uri
import androidx.annotation.OptIn
import androidx.media3.common.C
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.BaseDataSource
import androidx.media3.datasource.DataSource
import androidx.media3.datasource.DataSpec

/**
 * Media3 [DataSource] over the host's random access `readAt` (06 §3, 15 §2.1): the bytes stay in memory (bounded
 * read-ahead, no disk cache), reads run on Media3's loader threads and are cancellable, and the single host read
 * handle of the playback is shared by all loads ([HostHandlePool]). For m2ts sources the data source presents the
 * logical TS stream ([M2tsReader]).
 */
@OptIn(UnstableApi::class)
internal class HostDataSource(pool: HostHandlePool, readTimeoutMs: Long, prefetchBytes: Int, private val m2ts: Boolean) :
    BaseDataSource(false) {
    private val reader = HostReader(pool, readTimeoutMs, prefetchBytes)
    private val m2tsReader = if (m2ts) M2tsReader(reader) else null
    private var uri: Uri? = null
    private var opened = false

    override fun open(dataSpec: DataSpec): Long {
        uri = dataSpec.uri
        transferInitializing(dataSpec)
        val length = if (dataSpec.length == C.LENGTH_UNSET.toLong()) HostReader.UNKNOWN else dataSpec.length
        val available = m2tsReader?.open(dataSpec.position, length) ?: reader.open(dataSpec.position, length)
        opened = true
        transferStarted(dataSpec)
        return if (available == HostReader.UNKNOWN) C.LENGTH_UNSET.toLong() else available
    }

    override fun read(buffer: ByteArray, offset: Int, length: Int): Int {
        val read = m2tsReader?.read(buffer, offset, length) ?: reader.read(buffer, offset, length)
        if (read == HostReader.END) return C.RESULT_END_OF_INPUT
        if (read > 0) bytesTransferred(read)
        return read
    }

    override fun getUri(): Uri? = uri

    override fun close() {
        uri = null
        if (m2tsReader != null) m2tsReader.close() else reader.close()
        if (opened) {
            opened = false
            transferEnded()
        }
    }

    /** Creates the data sources of one playback; all share [pool]. */
    class Factory(
        private val pool: HostHandlePool,
        private val readTimeoutMs: Long,
        private val prefetchBytes: Int,
        private val m2ts: Boolean,
    ) : DataSource.Factory {
        override fun createDataSource(): DataSource = HostDataSource(pool, readTimeoutMs, prefetchBytes, m2ts)
    }
}
