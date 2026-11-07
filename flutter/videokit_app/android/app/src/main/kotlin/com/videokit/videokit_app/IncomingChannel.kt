package com.videokit.videokit_app

import android.content.ContentResolver
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.Looper
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.EventChannel
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Event channel `com.videokit.app/incoming` (REQ-APP-02): one list of document maps per `ACTION_VIEW`,
 * `ACTION_SEND` or `ACTION_SEND_MULTIPLE` intent, for cold starts (the launch intent) and warm starts
 * (`onNewIntent`). Events are buffered until Dart listens, so a cold-start intent is not lost while the Flutter
 * UI starts. `persistable` is true only when the sender granted a persistable permission and it was taken;
 * share / "打开方式" grants are usually temporary.
 */
class IncomingChannel(private val resolver: ContentResolver, messenger: BinaryMessenger) : EventChannel.StreamHandler {
    private val channel = EventChannel(messenger, NAME)
    private val io: ExecutorService = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private val buffered = ArrayDeque<List<Map<String, Any?>>>()
    private var sink: EventChannel.EventSink? = null

    init {
        channel.setStreamHandler(this)
    }

    override fun onListen(arguments: Any?, events: EventChannel.EventSink) {
        sink = events
        while (buffered.isNotEmpty()) events.success(buffered.removeFirst())
    }

    override fun onCancel(arguments: Any?) {
        sink = null
    }

    /** Handles [intent] if it opens media; returns whether it did. */
    fun handle(intent: Intent?): Boolean {
        if (intent == null) return false
        val uris = when (intent.action) {
            Intent.ACTION_VIEW -> listOfNotNull(intent.data)
            Intent.ACTION_SEND -> listOfNotNull(stream(intent)) + DocumentAccess.urisOf(intent)
            Intent.ACTION_SEND_MULTIPLE -> streams(intent) + DocumentAccess.urisOf(intent)
            else -> return false
        }.distinct().filter { it.scheme == ContentResolver.SCHEME_CONTENT }
        if (uris.isEmpty()) return false
        val flags = intent.flags
        val fallbackMime = intent.type
        io.execute {
            val docs = uris.mapNotNull { uri ->
                val persistable = DocumentAccess.takeRead(resolver, uri, flags)
                runCatching { DocumentAccess.describe(resolver, uri, persistable, fallbackMime) }.getOrNull()
            }
            if (docs.isNotEmpty()) main.post { emit(docs) }
        }
        return true
    }

    private fun emit(docs: List<Map<String, Any?>>) {
        val s = sink
        if (s == null) buffered.addLast(docs) else s.success(docs)
    }

    @Suppress("DEPRECATION")
    private fun stream(intent: Intent): Uri? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
    } else {
        intent.getParcelableExtra(Intent.EXTRA_STREAM)
    }

    @Suppress("DEPRECATION")
    private fun streams(intent: Intent): List<Uri> = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        intent.getParcelableArrayListExtra(Intent.EXTRA_STREAM, Uri::class.java).orEmpty()
    } else {
        intent.getParcelableArrayListExtra<Uri>(Intent.EXTRA_STREAM).orEmpty()
    }

    /** Detaches from the engine. */
    fun dispose() {
        channel.setStreamHandler(null)
        sink = null
        io.shutdown()
    }

    companion object {
        /** Channel name (Dart `AppDocumentChannels.incoming`). */
        const val NAME: String = "com.videokit.app/incoming"
    }
}
