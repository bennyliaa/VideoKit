package com.videokit.videokit_app

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Handler
import android.os.Looper
import com.videokit.flutter.VideoKitFlutter
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Method channel `com.videokit.app/documents` (contract: Dart `AppDocumentChannels`, REQ-APP-01/03).
 *
 * * `openDocuments` / `reselect`: `ACTION_OPEN_DOCUMENT` (video/image, multi-select), then
 *   `takePersistableUriPermission` for each document.
 * * `checkAccess`, `releaseAccess` (`releasePersistableUriPermission`; Dart calls it when a record is deleted or
 *   evicted beyond 200 records).
 * * `createDocument`: `ACTION_CREATE_DOCUMENT` for export "另存为"; `registerExportSink` /
 *   `unregisterExportSink` register a [ContentUriOutputSink] for the chosen document with the plugin.
 *
 * One system dialog at a time; a second request while one is open fails with `BUSY`. Provider queries run on a
 * background thread; results are delivered on the main thread.
 */
class DocumentsChannel(private val activity: Activity, messenger: BinaryMessenger) : MethodChannel.MethodCallHandler {
    private val channel = MethodChannel(messenger, NAME)
    private val io: ExecutorService = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private var pending: Pending? = null

    private sealed interface Pending {
        val result: MethodChannel.Result

        class Open(override val result: MethodChannel.Result, val single: Boolean) : Pending
        class Create(override val result: MethodChannel.Result) : Pending
    }

    init {
        channel.setMethodCallHandler(this)
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "openDocuments" -> open(
                result,
                call.argument<List<String>>("mimeTypes").orEmpty(),
                multiple = call.argument<Boolean>("multiple") ?: true,
                single = false,
            )
            "reselect" -> open(result, call.argument<List<String>>("mimeTypes").orEmpty(), multiple = false, single = true)
            "checkAccess" -> background(result) { DocumentAccess.checkAccess(activity.contentResolver, uriArg(call)) }
            "releaseAccess" -> background(result) {
                DocumentAccess.releaseRead(activity.contentResolver, uriArg(call))
                null
            }
            "createDocument" -> create(
                result,
                call.argument<String>("suggestedName") ?: "VideoKit.mp4",
                call.argument<String>("mimeType") ?: "video/mp4",
            )
            "registerExportSink" -> {
                val sinkId = call.argument<String>("sinkId")
                val uri = call.argument<String>("uri")
                if (sinkId.isNullOrEmpty() || uri.isNullOrEmpty()) {
                    result.error("INVALID_ARGUMENT", "sinkId and uri are required", null)
                    return
                }
                VideoKitFlutter.registerSink(
                    sinkId,
                    ContentUriOutputSink(activity, Uri.parse(uri)) { VideoKitFlutter.unregisterSink(sinkId) },
                )
                result.success(null)
            }
            "unregisterExportSink" -> {
                call.argument<String>("sinkId")?.let(VideoKitFlutter::unregisterSink)
                result.success(null)
            }
            else -> result.notImplemented()
        }
    }

    private fun uriArg(call: MethodCall): Uri = Uri.parse(requireNotNull(call.argument<String>("uri")) { "uri" })

    private fun open(result: MethodChannel.Result, mimeTypes: List<String>, multiple: Boolean, single: Boolean) {
        if (busy(result)) return
        val mimes = mimeTypes.ifEmpty { listOf("video/*", "image/*") }
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = if (mimes.size == 1) mimes[0] else "*/*"
            putExtra(Intent.EXTRA_MIME_TYPES, mimes.toTypedArray())
            putExtra(Intent.EXTRA_ALLOW_MULTIPLE, multiple)
            addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION,
            )
        }
        launch(Pending.Open(result, single), intent, REQUEST_OPEN)
    }

    private fun create(result: MethodChannel.Result, suggestedName: String, mimeType: String) {
        if (busy(result)) return
        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = mimeType
            putExtra(Intent.EXTRA_TITLE, suggestedName)
        }
        launch(Pending.Create(result), intent, REQUEST_CREATE)
    }

    private fun busy(result: MethodChannel.Result): Boolean {
        if (pending == null) return false
        result.error("BUSY", "a document dialog is already open", null)
        return true
    }

    private fun launch(p: Pending, intent: Intent, requestCode: Int) {
        pending = p
        try {
            activity.startActivityForResult(intent, requestCode)
        } catch (e: ActivityNotFoundException) {
            pending = null
            p.result.error("NO_DOCUMENTS_UI", "no activity for ${intent.action}", null)
        }
    }

    /** Forwarded from [MainActivity.onActivityResult]; true when the request was ours. */
    fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?): Boolean {
        if (requestCode != REQUEST_OPEN && requestCode != REQUEST_CREATE) return false
        val p = pending ?: return true
        pending = null
        val ok = resultCode == Activity.RESULT_OK
        when (p) {
            is Pending.Create -> p.result.success(if (ok) data?.data?.toString() else null)
            is Pending.Open -> {
                val uris = if (ok) DocumentAccess.urisOf(data) else emptyList()
                val flags = data?.flags ?: 0
                background(p.result) {
                    val resolver = activity.contentResolver
                    val docs = uris.mapNotNull { uri ->
                        val persistable = DocumentAccess.takeRead(resolver, uri, flags)
                        DocumentAccess.describe(resolver, uri, persistable)
                    }
                    if (p.single) docs.firstOrNull() else docs
                }
            }
        }
        return true
    }

    private fun background(result: MethodChannel.Result, work: () -> Any?) {
        io.execute {
            val outcome = runCatching(work)
            main.post {
                outcome.fold(
                    onSuccess = { result.success(it) },
                    onFailure = { result.error("DOCUMENT_ACCESS_FAILED", it.javaClass.simpleName, null) },
                )
            }
        }
    }

    /** Detaches from the engine; an open dialog's result is dropped. */
    fun dispose() {
        channel.setMethodCallHandler(null)
        pending?.result?.error("DETACHED", "activity detached", null)
        pending = null
        io.shutdown()
    }

    companion object {
        /** Channel name (Dart `AppDocumentChannels.documents`). */
        const val NAME: String = "com.videokit.app/documents"
        private const val REQUEST_OPEN = 0x5601
        private const val REQUEST_CREATE = 0x5602
    }
}
