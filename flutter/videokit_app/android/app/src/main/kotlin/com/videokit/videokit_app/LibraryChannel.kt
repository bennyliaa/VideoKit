package com.videokit.videokit_app

import android.app.Activity
import android.app.KeyguardManager
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.hardware.biometrics.BiometricManager
import android.hardware.biometrics.BiometricPrompt
import android.media.MediaMetadataRetriever
import android.media.ThumbnailUtils
import android.net.Uri
import android.os.CancellationSignal
import android.os.Handler
import android.os.Looper
import android.os.StatFs
import android.provider.DocumentsContract
import android.provider.MediaStore
import android.provider.OpenableColumns
import android.util.Size
import android.view.WindowManager
import io.flutter.plugin.common.BinaryMessenger
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileNotFoundException
import java.io.FileOutputStream
import java.io.IOException
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * Method channel `com.videokit.app/library` (contract: Dart `ChannelLibraryPlatform`, REQ-APP-09–11, APP-LIB-A1).
 * App business only; it does not touch the Kit.
 *
 * * Private copies live in `filesDir/library` (not scanned by the media store, not readable by other apps).
 * * `copy` reports `progress` back to Dart and stops on `cancelCopy`; a failed or cancelled copy leaves no file.
 * * `deleteOriginals`: `MediaStore.createDeleteRequest`, so the system asks the user; only confirmed deletes happen.
 * * `authenticateBiometric`: the framework BiometricPrompt (API 30+, minSdk is 31), no extra library.
 * * `confirmDeviceCredential`: the device screen lock through BiometricPrompt with DEVICE_CREDENTIAL, after
 *   `KeyguardManager.isDeviceSecure` (the "忘记密码" path).
 * * `setSecure`: `FLAG_SECURE` on the window while library pages are open.
 */
class LibraryChannel(private val activity: Activity, messenger: BinaryMessenger) : MethodChannel.MethodCallHandler {
    private val channel = MethodChannel(messenger, NAME)
    private val io: ExecutorService = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private val cancelled = ConcurrentHashMap.newKeySet<Int>()
    private var pendingDelete: Pair<MethodChannel.Result, List<String>>? = null
    private var pendingTree: MethodChannel.Result? = null

    init {
        channel.setMethodCallHandler(this)
    }

    private val mediaDir: File
        get() = File(activity.filesDir, "library").also { it.mkdirs() }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "mediaDirectory" -> result.success(mediaDir.absolutePath)
            "freeBytes" -> background(result) { StatFs(mediaDir.absolutePath).availableBytes }
            "copy" -> copy(call, result)
            "cancelCopy" -> {
                call.argument<Int>("job")?.let(cancelled::add)
                result.success(null)
            }
            "probe" -> background(result) {
                probe(requireNotNull(call.argument<String>("path")), call.argument<Boolean>("image") == true)
            }
            "thumbnail" -> background(result) {
                thumbnail(
                    requireNotNull(call.argument<String>("path")),
                    call.argument<Boolean>("image") == true,
                    requireNotNull(call.argument<String>("dest")),
                )
            }
            "delete" -> background(result) {
                val path = requireNotNull(call.argument<String>("path"))
                if (isPrivate(path)) File(path).delete()
                null
            }
            "deleteOriginals" -> deleteOriginals(call.argument<List<String>>("uris").orEmpty(), result)
            "canUseBiometrics" -> result.success(canUseBiometrics())
            "authenticateBiometric" -> authenticate(
                result,
                call.argument<String>("title").orEmpty(),
                negative = call.argument<String>("negative").orEmpty(),
                credential = false,
            )
            "hasDeviceCredential" -> result.success(keyguard().isDeviceSecure)
            "confirmDeviceCredential" -> {
                if (!keyguard().isDeviceSecure) {
                    result.success("unavailable")
                } else {
                    authenticate(result, call.argument<String>("title").orEmpty(), negative = "", credential = true)
                }
            }
            "exportToGallery" -> background(result) {
                exportToGallery(
                    requireNotNull(call.argument<String>("path")),
                    call.argument<String>("name").orEmpty(),
                    call.argument<Boolean>("image") == true,
                    call.argument<String>("mimeType"),
                )
            }
            "pickDirectory" -> pickDirectory(result)
            "ensureDirectory" -> background(result) {
                ensureDirectory(
                    Uri.parse(requireNotNull(call.argument<String>("tree"))),
                    requireNotNull(call.argument<String>("name")),
                )
            }
            "copyToDirectory" -> {
                val job = call.argument<Int>("job") ?: 0
                val path = requireNotNull(call.argument<String>("path"))
                val dir = Uri.parse(requireNotNull(call.argument<String>("dir")))
                val name = requireNotNull(call.argument<String>("name"))
                val mime = call.argument<String>("mimeType") ?: "application/octet-stream"
                io.execute {
                    val outcome = runCatching { copyToDirectory(job, path, dir, name, mime) }.getOrDefault("other")
                    cancelled.remove(job)
                    main.post { result.success(outcome) }
                }
            }
            "listTree" -> background(result) {
                listTree(Uri.parse(requireNotNull(call.argument<String>("tree"))))
            }
            "setSecure" -> {
                val secure = call.argument<Boolean>("secure") == true
                activity.runOnUiThread {
                    if (secure) {
                        activity.window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    } else {
                        activity.window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    }
                }
                result.success(null)
            }
            else -> result.notImplemented()
        }
    }

    /** Only files inside the private library directory may be deleted from Dart. */
    private fun isPrivate(path: String): Boolean =
        File(path).canonicalPath.startsWith(mediaDir.canonicalPath + File.separator)

    // ------------------------------------------------------------------ copy --

    private fun copy(call: MethodCall, result: MethodChannel.Result) {
        val job = call.argument<Int>("job") ?: 0
        val uri = Uri.parse(requireNotNull(call.argument<String>("uri")))
        val dest = File(requireNotNull(call.argument<String>("dest")))
        io.execute {
            val outcome = copyNow(job, uri, dest)
            cancelled.remove(job)
            main.post { result.success(outcome) }
        }
    }

    private fun copyNow(job: Int, uri: Uri, dest: File): Map<String, Any> {
        if (!isPrivate(dest.absolutePath)) return mapOf("failure" to "other")
        dest.parentFile?.mkdirs()
        val tmp = File(dest.parentFile, dest.name + ".part")
        val resolver = activity.contentResolver
        val known = sizeOf(uri)
        if (known != null && known > StatFs(mediaDir.absolutePath).availableBytes) {
            return mapOf("failure" to "noSpace")
        }
        var written = 0L
        try {
            val input = resolver.openInputStream(uri) ?: return mapOf("failure" to "unreadable")
            input.use { ins ->
                FileOutputStream(tmp).use { out ->
                    val buffer = ByteArray(BUFFER)
                    var lastReport = 0L
                    while (true) {
                        if (cancelled.contains(job)) {
                            tmp.delete()
                            return mapOf("failure" to "other")
                        }
                        val n = ins.read(buffer)
                        if (n < 0) break
                        out.write(buffer, 0, n)
                        written += n
                        if (written - lastReport >= REPORT_EVERY) {
                            lastReport = written
                            val bytes = written
                            main.post { channel.invokeMethod("progress", mapOf("job" to job, "bytes" to bytes)) }
                        }
                    }
                    out.fd.sync()
                }
            }
        } catch (e: FileNotFoundException) {
            tmp.delete()
            return mapOf("failure" to "unreadable")
        } catch (e: SecurityException) {
            tmp.delete()
            return mapOf("failure" to "unreadable")
        } catch (e: IOException) {
            tmp.delete()
            val noSpace = e.message.orEmpty().let { "ENOSPC" in it || "No space" in it }
            return mapOf("failure" to if (noSpace) "noSpace" else "unreadable")
        }
        if (!tmp.renameTo(dest)) {
            tmp.delete()
            return mapOf("failure" to "other")
        }
        return mapOf("bytes" to written)
    }

    private fun sizeOf(uri: Uri): Long? = runCatching {
        activity.contentResolver.query(uri, arrayOf(OpenableColumns.SIZE), null, null, null)?.use { c ->
            if (c.moveToFirst() && !c.isNull(0)) c.getLong(0) else null
        }
    }.getOrNull()

    // ---------------------------------------------------- probe / thumbnail --

    private fun probe(path: String, image: Boolean): Map<String, Any>? {
        if (!isPrivate(path)) return null
        if (image) {
            val o = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeFile(path, o)
            if (o.outWidth <= 0 || o.outHeight <= 0) return null
            return mapOf("width" to o.outWidth, "height" to o.outHeight)
        }
        val r = MediaMetadataRetriever()
        return try {
            r.setDataSource(path)
            val durationMs = r.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLongOrNull()
                ?: return null
            var w = r.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)?.toIntOrNull()
            var h = r.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)?.toIntOrNull()
            val rotation = r.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION)?.toIntOrNull() ?: 0
            if (rotation == 90 || rotation == 270) {
                val t = w
                w = h
                h = t
            }
            buildMap {
                put("durationUs", durationMs * 1000)
                w?.let { put("width", it) }
                h?.let { put("height", it) }
            }
        } catch (e: RuntimeException) {
            null
        } finally {
            r.release()
        }
    }

    private fun thumbnail(path: String, image: Boolean, dest: String): Boolean {
        if (!isPrivate(path) || !isPrivate(dest)) return false
        val size = Size(THUMB_WIDTH, THUMB_HEIGHT)
        val bitmap: Bitmap = try {
            if (image) {
                ThumbnailUtils.createImageThumbnail(File(path), size, CancellationSignal())
            } else {
                ThumbnailUtils.createVideoThumbnail(File(path), size, CancellationSignal())
            }
        } catch (e: IOException) {
            return false
        }
        val out = File(dest)
        out.parentFile?.mkdirs()
        return try {
            FileOutputStream(out).use { bitmap.compress(Bitmap.CompressFormat.JPEG, THUMB_QUALITY, it) }
        } catch (e: IOException) {
            false
        } finally {
            bitmap.recycle()
        }
    }

    // ------------------------------------------------------- delete originals --

    private fun deleteOriginals(uris: List<String>, result: MethodChannel.Result) {
        if (pendingDelete != null) {
            result.error("BUSY", "a delete request is already open", null)
            return
        }
        // Only documents the media store knows can be deleted through the system confirmation.
        val pairs = uris.mapNotNull { s ->
            val u = Uri.parse(s)
            val media = runCatching {
                when {
                    u.authority == MediaStore.AUTHORITY -> u
                    DocumentsContract.isDocumentUri(activity, u) -> MediaStore.getMediaUri(activity, u)
                    else -> null
                }
            }.getOrNull()
            media?.let { s to it }
        }
        if (pairs.isEmpty()) {
            result.success(emptyList<String>())
            return
        }
        val request = MediaStore.createDeleteRequest(activity.contentResolver, pairs.map { it.second })
        pendingDelete = result to pairs.map { it.first }
        try {
            activity.startIntentSenderForResult(request.intentSender, REQUEST_DELETE, null, 0, 0, 0)
        } catch (e: android.content.IntentSender.SendIntentException) {
            pendingDelete = null
            result.success(emptyList<String>())
        }
    }

    /** Forwarded from [MainActivity.onActivityResult]; true when the request was ours. */
    fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?): Boolean {
        if (requestCode == REQUEST_TREE) {
            val result = pendingTree ?: return true
            pendingTree = null
            val tree = if (resultCode == Activity.RESULT_OK) data?.data else null
            if (tree != null) {
                // Kept for the run only; released by the system on uninstall.
                runCatching {
                    activity.contentResolver.takePersistableUriPermission(
                        tree,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION,
                    )
                }
            }
            result.success(tree?.toString())
            return true
        }
        if (requestCode != REQUEST_DELETE) return false
        val (result, uris) = pendingDelete ?: return true
        pendingDelete = null
        result.success(if (resultCode == Activity.RESULT_OK) uris else emptyList<String>())
        return true
    }

    // ------------------------------------------- REQ-APP-14: export / move --

    /**
     * "导出到相册": a MediaStore entry under Movies/VideoKit or Pictures/VideoKit (IS_PENDING while written; no
     * storage permission needed for the App's own inserts on API 29+). The private file stays.
     */
    private fun exportToGallery(path: String, name: String, image: Boolean, mime: String?): String {
        if (!isPrivate(path)) return "unreadable"
        val src = File(path)
        if (!src.isFile) return "unreadable"
        val collection = if (image) {
            MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        } else {
            MediaStore.Video.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        }
        // Shared storage (/storage/emulated) lives on the data partition on current devices.
        val free = runCatching { StatFs(android.os.Environment.getDataDirectory().path).availableBytes }.getOrNull()
        if (free != null && free < src.length()) return "noSpace"
        val values = android.content.ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, name.ifEmpty { src.name })
            put(MediaStore.MediaColumns.MIME_TYPE, mime ?: if (image) "image/jpeg" else "video/mp4")
            put(
                MediaStore.MediaColumns.RELATIVE_PATH,
                if (image) "Pictures/$GALLERY_DIR" else "Movies/$GALLERY_DIR",
            )
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        }
        val resolver = activity.contentResolver
        val uri = resolver.insert(collection, values) ?: return "unwritable"
        try {
            val out = resolver.openOutputStream(uri) ?: run {
                resolver.delete(uri, null, null)
                return "unwritable"
            }
            out.use { o -> src.inputStream().use { it.copyTo(o, BUFFER) } }
            values.clear()
            values.put(MediaStore.MediaColumns.IS_PENDING, 0)
            resolver.update(uri, values, null, null)
            return "ok"
        } catch (e: IOException) {
            resolver.delete(uri, null, null)
            val noSpace = e.message.orEmpty().let { "ENOSPC" in it || "No space" in it }
            return if (noSpace) "noSpace" else "unwritable"
        }
    }

    private fun pickDirectory(result: MethodChannel.Result) {
        if (pendingTree != null) {
            result.error("BUSY", "a directory picker is already open", null)
            return
        }
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).addFlags(
            Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION,
        )
        pendingTree = result
        try {
            activity.startActivityForResult(intent, REQUEST_TREE)
        } catch (e: android.content.ActivityNotFoundException) {
            pendingTree = null
            result.success(null)
        }
    }

    /** Child directory [name] of the picked tree (existing one reused), or null. */
    private fun ensureDirectory(tree: Uri, name: String): String? {
        val resolver = activity.contentResolver
        val root = DocumentsContract.buildDocumentUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree))
        childOf(tree, DocumentsContract.getDocumentId(root), name, directory = true)?.let { return it.toString() }
        return runCatching {
            DocumentsContract.createDocument(resolver, root, DocumentsContract.Document.MIME_TYPE_DIR, name)
        }.getOrNull()?.toString()
    }

    private fun childOf(tree: Uri, parentId: String, name: String, directory: Boolean): Uri? {
        val children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, parentId)
        val cols = arrayOf(
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE,
        )
        activity.contentResolver.query(children, cols, null, null, null)?.use { c ->
            while (c.moveToNext()) {
                val isDir = c.getString(2) == DocumentsContract.Document.MIME_TYPE_DIR
                if (c.getString(1) == name && isDir == directory) {
                    return DocumentsContract.buildDocumentUriUsingTree(tree, c.getString(0))
                }
            }
        }
        return null
    }

    /**
     * Copies a private file into [dir] as [name], then reads the copy back: size and SHA-256 must equal the
     * source's. Any failure or cancel deletes the new document, so no half file remains. Never overwrites: the
     * provider renames on a clash ("a (1).mp4").
     */
    private fun copyToDirectory(job: Int, path: String, dir: Uri, name: String, mime: String): String {
        if (!isPrivate(path)) return "unreadable"
        val src = File(path)
        if (!src.isFile) return "unreadable"
        val resolver = activity.contentResolver
        val doc = runCatching { DocumentsContract.createDocument(resolver, dir, mime, name) }.getOrNull()
            ?: return "unwritable"
        fun fail(reason: String): String {
            runCatching { DocumentsContract.deleteDocument(resolver, doc) }
            return reason
        }
        val sourceDigest = java.security.MessageDigest.getInstance("SHA-256")
        try {
            val out = resolver.openOutputStream(doc, "w") ?: return fail("unwritable")
            out.use { o ->
                src.inputStream().use { ins ->
                    val buffer = ByteArray(BUFFER)
                    while (true) {
                        if (cancelled.contains(job)) return fail("cancelled")
                        val n = ins.read(buffer)
                        if (n < 0) break
                        o.write(buffer, 0, n)
                        sourceDigest.update(buffer, 0, n)
                    }
                    o.flush()
                }
            }
        } catch (e: IOException) {
            val noSpace = e.message.orEmpty().let { "ENOSPC" in it || "No space" in it }
            return fail(if (noSpace) "noSpace" else "unwritable")
        } catch (e: SecurityException) {
            return fail("unwritable")
        }
        // Read back.
        val copyDigest = java.security.MessageDigest.getInstance("SHA-256")
        var copied = 0L
        try {
            val input = resolver.openInputStream(doc) ?: return fail("mismatch")
            input.use { ins ->
                val buffer = ByteArray(BUFFER)
                while (true) {
                    if (cancelled.contains(job)) return fail("cancelled")
                    val n = ins.read(buffer)
                    if (n < 0) break
                    copyDigest.update(buffer, 0, n)
                    copied += n
                }
            }
        } catch (e: IOException) {
            return fail("unwritable")
        }
        if (copied != src.length() || !copyDigest.digest().contentEquals(sourceDigest.digest())) {
            return fail("mismatch")
        }
        return "ok"
    }

    /** All files under the tree with their directory path relative to it (depth-first). */
    private fun listTree(tree: Uri): Map<String, Any> {
        val rootId = DocumentsContract.getTreeDocumentId(tree)
        val rootName = activity.contentResolver.query(
            DocumentsContract.buildDocumentUriUsingTree(tree, rootId),
            arrayOf(DocumentsContract.Document.COLUMN_DISPLAY_NAME),
            null,
            null,
            null,
        )?.use { c -> if (c.moveToFirst()) c.getString(0) else null } ?: "VideoKit"
        val entries = mutableListOf<Map<String, Any?>>()
        val cols = arrayOf(
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE,
            DocumentsContract.Document.COLUMN_SIZE,
        )
        val stack = ArrayDeque<Pair<String, String>>().apply { add(rootId to "") }
        while (stack.isNotEmpty() && entries.size < MAX_TREE_ENTRIES) {
            val (id, rel) = stack.removeFirst()
            val children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, id)
            activity.contentResolver.query(children, cols, null, null, null)?.use { c ->
                while (c.moveToNext()) {
                    val childId = c.getString(0)
                    val name = c.getString(1) ?: continue
                    val mime = c.getString(2)
                    if (mime == DocumentsContract.Document.MIME_TYPE_DIR) {
                        stack.add(childId to if (rel.isEmpty()) name else "$rel/$name")
                    } else {
                        entries += mapOf(
                            "dir" to rel,
                            "uri" to DocumentsContract.buildDocumentUriUsingTree(tree, childId).toString(),
                            "name" to name,
                            "mimeType" to mime,
                            "size" to if (c.isNull(3)) null else c.getLong(3),
                        )
                    }
                }
            }
        }
        return mapOf("name" to rootName, "entries" to entries)
    }

    // ------------------------------------------------------------ biometrics --

    private fun keyguard(): KeyguardManager = activity.getSystemService(KeyguardManager::class.java)

    private fun canUseBiometrics(): Boolean {
        val m = activity.getSystemService(BiometricManager::class.java) ?: return false
        return m.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_WEAK) == BiometricManager.BIOMETRIC_SUCCESS
    }

    private fun authenticate(result: MethodChannel.Result, title: String, negative: String, credential: Boolean) {
        if (!credential && !canUseBiometrics()) {
            result.success("unavailable")
            return
        }
        val executor = activity.mainExecutor
        var answered = false
        fun answer(value: String) {
            if (answered) return
            answered = true
            result.success(value)
        }
        val builder = BiometricPrompt.Builder(activity).setTitle(title)
        if (credential) {
            builder.setAllowedAuthenticators(BiometricManager.Authenticators.DEVICE_CREDENTIAL)
        } else {
            builder.setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_WEAK)
            builder.setNegativeButton(negative, executor) { _, _ -> answer("cancelled") }
        }
        val callback = object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(r: BiometricPrompt.AuthenticationResult?) = answer("success")

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence?) {
                val cancelledByUser = errorCode == BiometricPrompt.BIOMETRIC_ERROR_USER_CANCELED ||
                    errorCode == BiometricPrompt.BIOMETRIC_ERROR_CANCELED ||
                    errorCode == BiometricPrompt.BIOMETRIC_ERROR_NEGATIVE_BUTTON
                answer(if (cancelledByUser) "cancelled" else "failed")
            }
        }
        try {
            builder.build().authenticate(CancellationSignal(), executor, callback)
        } catch (e: RuntimeException) {
            answer("unavailable")
        }
    }

    // ----------------------------------------------------------------- misc --

    private fun background(result: MethodChannel.Result, work: () -> Any?) {
        io.execute {
            val outcome = runCatching(work)
            main.post {
                outcome.fold(
                    onSuccess = { result.success(it) },
                    onFailure = { result.error("LIBRARY_FAILED", it.javaClass.simpleName, null) },
                )
            }
        }
    }

    /** Detaches from the engine. */
    fun dispose() {
        channel.setMethodCallHandler(null)
        pendingDelete?.first?.success(emptyList<String>())
        pendingDelete = null
        pendingTree?.success(null)
        pendingTree = null
        io.shutdown()
    }

    companion object {
        /** Channel name (Dart `ChannelLibraryPlatform.channelName`). */
        const val NAME: String = "com.videokit.app/library"
        private const val REQUEST_DELETE = 0x5611
        private const val REQUEST_TREE = 0x5612
        private const val GALLERY_DIR = "VideoKit"
        private const val MAX_TREE_ENTRIES = 10_000
        private const val BUFFER = 256 * 1024
        private const val REPORT_EVERY = 1024L * 1024L
        private const val THUMB_WIDTH = 320
        private const val THUMB_HEIGHT = 180
        private const val THUMB_QUALITY = 80
    }
}
