package com.videokit.spike.s4

import android.app.Service
import android.content.Intent
import androidx.media3.muxer.BufferInfo
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.Message
import android.os.Messenger
import android.os.ParcelFileDescriptor
import android.os.Process
import android.system.Os
import android.system.OsConstants
import android.util.Log
import androidx.media3.common.Format
import androidx.media3.common.MediaItem
import androidx.media3.common.Metadata
import androidx.media3.common.util.Clock
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.DataSource
import androidx.media3.datasource.DataSourceBitmapLoader
import androidx.media3.effect.Presentation
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.muxer.Mp4Muxer
import androidx.media3.muxer.Muxer
import androidx.media3.transformer.Composition
import androidx.media3.transformer.DefaultAssetLoaderFactory
import androidx.media3.transformer.DefaultDecoderFactory
import androidx.media3.transformer.EditedMediaItem
import androidx.media3.transformer.Effects
import androidx.media3.transformer.ExportException
import androidx.media3.transformer.ExportResult
import androidx.media3.transformer.Transformer
import com.google.common.collect.ImmutableList
import java.io.FileOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong

/**
 * S4 export worker in an `isolatedProcess` (15 §2.8). Input: [BrokerDataSource] over the main process binder; output:
 * the file descriptor the main process opened (the worker can open no file itself). After the first written video
 * sample it injects the requested [S4Protocol.Fault]. The worker never deletes or validates output: the main process
 * owns the file and aborts it.
 */
@UnstableApi
class ExportWorkerService : Service() {
    private val main = Handler(Looper.getMainLooper())
    private var transformer: Transformer? = null
    private var reply: Messenger? = null
    private val messenger = Messenger(Handler(Looper.getMainLooper()) { message -> onMessage(message); true })

    override fun onBind(intent: Intent): IBinder = messenger.binder

    private fun onMessage(message: Message) {
        message.replyTo?.let { reply = it }
        when (message.what) {
            S4Protocol.START -> start(message.data)
            S4Protocol.CANCEL -> {
                transformer?.cancel()
                send(S4Protocol.CANCELLED)
            }
        }
    }

    private fun start(data: Bundle) {
        val broker = data.getBinder(S4Protocol.KEY_BROKER) ?: return send(S4Protocol.ERROR, code = "NO_BROKER")
        @Suppress("DEPRECATION")
        val output = data.getParcelable<ParcelFileDescriptor>(S4Protocol.KEY_OUTPUT) ?: return send(S4Protocol.ERROR, code = "NO_OUTPUT")
        val fault = S4Protocol.Fault.valueOf(data.getString(S4Protocol.KEY_FAULT) ?: "NONE")
        val clipMs = data.getLong(S4Protocol.KEY_CLIP_MS, 8_000L)
        val muxer = FdMuxerFactory(output) { samples, bytes ->
            send(S4Protocol.SAMPLE, samples = samples, bytes = bytes)
            if (samples == 1L) inject(fault)
        }
        val loader = data.getString(S4Protocol.KEY_LOADER) ?: S4Protocol.LOADER_JAVA
        // S4 attempt 1: Media3 must not register broadcast receivers in the isolated process.
        val context = IsolatedContext(this)
        val assets = when (loader) {
            // Attempt 2: blocks forever in ExoPlayerImpl's audio session id (media.audio_flinger); kept for comparison.
            S4Protocol.LOADER_EXO -> DefaultAssetLoaderFactory(
                context,
                DefaultDecoderFactory.Builder(context).build(),
                Clock.DEFAULT,
                DefaultMediaSourceFactory(DataSource.Factory { BrokerDataSource(broker) }),
                DataSourceBitmapLoader(context),
            )

            // Attempt 3: platform MediaExtractor; blocks on media.extractor. Kept for comparison.
            S4Protocol.LOADER_EXTRACTOR -> ExtractorAssetLoader.Factory(broker, clipMs * 1_000L)

            // Attempt 4 (a′): pure-Java Media3 extractors, no system service.
            else -> JavaExtractorAssetLoader.Factory(broker, clipMs * 1_000L)
        }
        Log.i(TAG, "start fault=$fault loader=$loader")
        if (data.getBoolean(S4Protocol.KEY_PROBE, false)) {
            // Attempt 4: can this process decode at all? Bounded steps, reported before the export starts.
            send(S4Protocol.PROBE, code = "probe=START")
            DecodeProbe(broker) { line -> send(S4Protocol.PROBE, code = line) }.run()
        }
        dumpThreadsIfStuck(muxer)
        val built = Transformer.Builder(context)
            .setAssetLoaderFactory(assets)
            .setMuxerFactory(muxer)
            .setVideoMimeType("video/avc")
            .setAudioMimeType("audio/mp4a-latm")
            .addListener(
                object : Transformer.Listener {
                    override fun onCompleted(composition: Composition, exportResult: ExportResult) {
                        send(S4Protocol.DONE, samples = muxer.samples.get(), bytes = muxer.bytes.get())
                    }

                    override fun onError(composition: Composition, exportResult: ExportResult, exportException: ExportException) {
                        send(S4Protocol.ERROR, code = "EXPORT_${exportException.errorCode}")
                    }
                },
            )
            .build()
        transformer = built
        val item = MediaItem.Builder()
            .setUri("s4://input")
            .setClippingConfiguration(MediaItem.ClippingConfiguration.Builder().setEndPositionMs(clipMs).build())
            .build()
        val edited = EditedMediaItem.Builder(item).setEffects(Effects(listOf(), listOf(Presentation.createForHeight(360)))).build()
        send(S4Protocol.STARTED)
        // Transformer needs a path; the muxer factory ignores it and writes to the descriptor of the main process.
        built.start(edited, "/s4-fd-only-output.mp4")
    }

    /**
     * S4 attempts 3-4: when no sample was written [STACK_DUMP_MS] after the start, logs every thread's stack (tag
     * `S4STACK`) so a blocking call is identified at runtime, before the main process watchdog unbinds the worker.
     */
    private fun dumpThreadsIfStuck(muxer: FdMuxerFactory) {
        Thread({
            try {
                Thread.sleep(STACK_DUMP_MS)
            } catch (interrupted: InterruptedException) {
                return@Thread
            }
            if (muxer.samples.get() > 0) return@Thread
            Thread.getAllStackTraces().forEach { (thread, frames) ->
                Log.w(STACK_TAG, "thread ${thread.name} state=${thread.state}")
                frames.take(STACK_DEPTH).forEach { frame -> Log.w(STACK_TAG, "  at $frame") }
            }
        }, "s4-stack-dump").apply { isDaemon = true }.start()
    }

    private fun inject(fault: S4Protocol.Fault) {
        when (fault) {
            S4Protocol.Fault.NONE, S4Protocol.Fault.CANCEL -> Unit

            S4Protocol.Fault.SIGSEGV -> main.post { Process.sendSignal(Process.myPid(), OsConstants.SIGSEGV) }

            S4Protocol.Fault.OOM -> Thread({
                val hog = ArrayList<ByteArray>()
                while (true) hog += ByteArray(OOM_CHUNK)
            }, "s4-oom").start()

            // The muxer thread spins forever: no progress, no answers (the main process watchdog must notice).
            S4Protocol.Fault.LOOP -> {
                var spin = 0L
                while (true) spin++
            }

            S4Protocol.Fault.KILL -> Os.kill(Process.myPid(), OsConstants.SIGKILL)
        }
    }

    private fun send(what: Int, code: String? = null, samples: Long = 0L, bytes: Long = 0L) {
        val message = Message.obtain(null, what).apply {
            data = Bundle().apply {
                putString(S4Protocol.KEY_CODE, code)
                putLong(S4Protocol.KEY_SAMPLES, samples)
                putLong(S4Protocol.KEY_BYTES, bytes)
            }
        }
        runCatching { reply?.send(message) }
    }

    private companion object {
        const val OOM_CHUNK = 32 * 1024 * 1024
        const val TAG = "S4Worker"
        const val STACK_TAG = "S4STACK"
        const val STACK_DUMP_MS = 3_000L
        const val STACK_DEPTH = 25
    }
}

/** Muxer over the main process' file descriptor (after D1 `FdOutputMuxer`); counts samples. */
@UnstableApi
class FdMuxerFactory(private val output: ParcelFileDescriptor, private val onSample: (Long, Long) -> Unit) : Muxer.Factory {
    val samples = AtomicLong()
    val bytes = AtomicLong()
    private val created = AtomicBoolean()

    override fun create(path: String): Muxer {
        check(created.compareAndSet(false, true)) { "OUTPUT_REOPEN_REJECTED" }
        val stream = FileOutputStream(output.fileDescriptor)
        val actual = Mp4Muxer.Builder(stream).build()
        return object : Muxer {
            override fun addTrack(format: Format): Int = actual.addTrack(format)

            override fun writeSampleData(trackId: Int, data: ByteBuffer, bufferInfo: BufferInfo) {
                actual.writeSampleData(trackId, data, bufferInfo)
                val count = samples.incrementAndGet()
                bytes.addAndGet(bufferInfo.size.toLong())
                onSample(count, bytes.get())
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
        androidx.media3.common.C.TRACK_TYPE_VIDEO -> ImmutableList.of("video/avc")
        androidx.media3.common.C.TRACK_TYPE_AUDIO -> ImmutableList.of("audio/mp4a-latm")
        else -> ImmutableList.of()
    }
}
