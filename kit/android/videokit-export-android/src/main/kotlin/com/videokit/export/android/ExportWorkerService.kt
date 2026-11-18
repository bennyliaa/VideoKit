package com.videokit.export.android

import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.Message
import android.os.Messenger
import android.os.ParcelFileDescriptor
import android.os.Process
import android.os.SystemClock
import android.system.Os
import androidx.media3.common.C
import androidx.media3.common.Format
import androidx.media3.common.MediaItem
import androidx.media3.common.Metadata
import androidx.media3.common.MimeTypes
import androidx.media3.common.util.UnstableApi
import androidx.media3.effect.Presentation
import androidx.media3.muxer.BufferInfo
import androidx.media3.muxer.Mp4Muxer
import androidx.media3.muxer.Muxer
import androidx.media3.muxer.SeekableMuxerOutput
import androidx.media3.transformer.Composition
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.Effects
import androidx.media3.transformer.ExportException
import androidx.media3.transformer.ExportResult
import androidx.media3.transformer.Transformer
import com.google.common.collect.ImmutableList
import com.videokit.api.ErrorCode
import com.videokit.api.ExportFailureReasons
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * Export worker (15 §1.5 / §2.8 option c1, M6-B1): runs in the separate, non-isolated `:videokit_export` process of
 * the app uid. One task per process: the main process kills the process after every task (a same-uid process is not
 * reclaimed on unbind, S4 attempt 5).
 *
 * - Input: [BrokerDataSource] over the main process [SourceBroker]; no path is ever given to the worker.
 * - Output: the file descriptor the main process opened from the host sink; the worker writes and closes its copy,
 *   it never validates, commits or deletes (the main process does).
 * - Demux: [ClipAssetLoader] (pure-Java Media3 extractors): no ExoPlayer and no audio initialization in the worker.
 * - Constraint 4 (S4 attempt 5): any uncaught exception on any thread first reports `EXPORT_FAILED` /
 *   `WORKER_CRASHED`, then kills the process at once, so a crashing worker can never deliver DONE afterwards.
 */
@UnstableApi
public class ExportWorkerService : Service() {
    private val main = Handler(Looper.getMainLooper())
    private var transformer: Transformer? = null

    @Volatile private var reply: Messenger? = null
    private val started = AtomicBoolean()
    private val messenger = Messenger(
        Handler(Looper.getMainLooper()) { message ->
            onMessage(message)
            true
        },
    )

    override fun onCreate() {
        super.onCreate()
        Thread.setDefaultUncaughtExceptionHandler { _, failure ->
            runCatching { error(ErrorCode.EXPORT_FAILED, ExportFailureReasons.WORKER_CRASHED, "UNCAUGHT:${failure.javaClass.simpleName}") }
            Process.killProcess(Process.myPid())
        }
    }

    override fun onBind(intent: Intent): IBinder = messenger.binder

    private fun onMessage(message: Message) {
        message.replyTo?.let { reply = it }
        when (message.what) {
            WorkerProtocol.START -> if (started.compareAndSet(false, true)) start(message.data)

            WorkerProtocol.CANCEL -> {
                transformer?.cancel()
                send(WorkerProtocol.CANCELLED)
            }
        }
    }

    private fun start(data: Bundle) {
        val broker = data.getBinder(WorkerProtocol.KEY_BROKER) ?: return error(ErrorCode.EXPORT_FAILED, null, "NO_BROKER")

        @Suppress("DEPRECATION")
        val output = data.getParcelable<ParcelFileDescriptor>(WorkerProtocol.KEY_OUTPUT)
            ?: return error(ErrorCode.EXPORT_FAILED, null, "NO_OUTPUT")
        val inUs = data.getLong(WorkerProtocol.KEY_IN_US)
        val outUs = data.getLong(WorkerProtocol.KEY_OUT_US)
        val targetHeight = data.getInt(WorkerProtocol.KEY_TARGET_HEIGHT)
        var effectiveInUs = inUs
        val muxer = FdMuxerFactory(output) { samples, bytes, processedUs ->
            sendProgress(samples, bytes, processedUs)
        }
        val effects = if (targetHeight > 0) Effects(listOf(), listOf(Presentation.createForHeight(targetHeight))) else Effects.EMPTY
        val built = Transformer.Builder(this)
            .setAssetLoaderFactory(ClipAssetLoader.Factory(broker, inUs, outUs) { effectiveInUs = it })
            .setMuxerFactory(muxer)
            .setVideoMimeType(MimeTypes.VIDEO_H264)
            .setAudioMimeType(MimeTypes.AUDIO_AAC)
            .addListener(
                object : Transformer.Listener {
                    override fun onCompleted(composition: Composition, exportResult: ExportResult) {
                        send(WorkerProtocol.DONE) {
                            putBundle(WorkerProtocol.KEY_METADATA, metadata(exportResult, muxer, effectiveInUs))
                        }
                    }

                    override fun onError(composition: Composition, exportResult: ExportResult, exportException: ExportException) {
                        // A failure of the media pipeline, not of the worker process: no reason.
                        error(ErrorCode.EXPORT_FAILED, null, "TRANSFORMER:${exportException.errorCode}")
                    }
                },
            )
            .build()
        transformer = built
        val item = EditedMediaItem.Builder(MediaItem.Builder().setUri("videokit-export://input").build()).setEffects(effects).build()
        send(WorkerProtocol.STARTED) { putInt(WorkerProtocol.KEY_PID, Process.myPid()) }
        // Transformer needs a path; the muxer factory ignores it and writes to the descriptor of the main process.
        built.start(item, "/videokit-export-fd-only.mp4")
    }

    private fun metadata(result: ExportResult, muxer: FdMuxerFactory, effectiveInUs: Long): Bundle = Bundle().apply {
        putInt("width", result.width)
        putInt("height", result.height)
        putLong("durationUs", if (result.durationMs == C.TIME_UNSET) -1L else result.durationMs * 1_000L)
        putLong("sizeBytes", result.fileSizeBytes)
        putInt("videoFrames", result.videoFrameCount)
        putBoolean("audioPresent", result.channelCount != C.LENGTH_UNSET && result.channelCount > 0)
        putLong("samples", muxer.samples.get())
        putLong("effectiveInUs", effectiveInUs)
        putString("videoCodec", result.videoMimeType)
        putString("audioCodec", result.audioMimeType)
    }

    private var lastProgressAt = 0L

    private fun sendProgress(samples: Long, bytes: Long, processedUs: Long) {
        val now = SystemClock.elapsedRealtime()
        // The first sample always (the watchdog switches from the startup grace to the hang limit), then throttled.
        if (samples != 1L && now - lastProgressAt < WorkerProtocol.PROGRESS_INTERVAL_MS) return
        lastProgressAt = now
        send(WorkerProtocol.PROGRESS) {
            putLong(WorkerProtocol.KEY_SAMPLES, samples)
            putLong(WorkerProtocol.KEY_BYTES, bytes)
            putLong(WorkerProtocol.KEY_PROCESSED_US, processedUs)
        }
    }

    private fun error(code: ErrorCode, reason: String?, diagnostic: String) {
        send(WorkerProtocol.ERROR) {
            putString(WorkerProtocol.KEY_CODE, code.name)
            putString(WorkerProtocol.KEY_REASON, reason)
            putString(WorkerProtocol.KEY_DIAGNOSTIC, diagnostic)
        }
    }

    private inline fun send(what: Int, fill: Bundle.() -> Unit = {}) {
        val message = Message.obtain(null, what).apply { data = Bundle().apply(fill) }
        runCatching { reply?.send(message) }
    }

    override fun onDestroy() {
        runCatching { transformer?.cancel() }
        main.removeCallbacksAndMessages(null)
        super.onDestroy()
    }
}

/** Muxer over the main process' file descriptor (S4 `FdMuxerFactory`); counts samples and the processed time. */
@UnstableApi
internal class FdMuxerFactory(
    private val output: ParcelFileDescriptor,
    private val onSample: (samples: Long, bytes: Long, processedUs: Long) -> Unit,
) : Muxer.Factory {
    val samples = AtomicLong()
    val bytes = AtomicLong()
    private val created = AtomicBoolean()

    override fun create(path: String): Muxer {
        check(created.compareAndSet(false, true)) { "OUTPUT_REOPEN_REJECTED" }
        val stream = FileOutputStream(output.fileDescriptor)
        val actual = Mp4Muxer.Builder(SeekableMuxerOutput.of(stream)).build()
        return object : Muxer {
            override fun addTrack(format: Format): Int = actual.addTrack(format)

            override fun writeSampleData(trackId: Int, data: ByteBuffer, bufferInfo: BufferInfo) {
                actual.writeSampleData(trackId, data, bufferInfo)
                val count = samples.incrementAndGet()
                onSample(count, bytes.addAndGet(bufferInfo.size.toLong()), bufferInfo.presentationTimeUs)
            }

            override fun addMetadataEntry(metadataEntry: Metadata.Entry) {
                runCatching { actual.addMetadataEntry(metadataEntry) }
            }

            override fun close() {
                try {
                    actual.close()
                    Os.fsync(output.fileDescriptor)
                } finally {
                    runCatching { stream.close() }
                    runCatching { output.close() }
                }
            }
        }
    }

    override fun getSupportedSampleMimeTypes(trackType: Int): ImmutableList<String> = when (trackType) {
        C.TRACK_TYPE_VIDEO -> ImmutableList.of(MimeTypes.VIDEO_H264)
        C.TRACK_TYPE_AUDIO -> ImmutableList.of(MimeTypes.AUDIO_AAC)
        else -> ImmutableList.of()
    }
}
