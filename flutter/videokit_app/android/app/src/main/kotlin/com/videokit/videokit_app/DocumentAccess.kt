package com.videokit.videokit_app

import android.content.ContentResolver
import android.content.Intent
import android.net.Uri
import android.provider.OpenableColumns
import java.io.FileNotFoundException

/**
 * Document helpers shared by [DocumentsChannel] and [IncomingChannel] (REQ-APP-01/02/03).
 *
 * The document map matches `ChannelMediaPicker.fromMap` on the Dart side:
 * `{uri, displayName, mimeType, sizeBytes?, persistable}`. URIs go to the module unchanged as `uri:` source
 * references (Dart `UriSourceRef`); the App never turns them into paths.
 */
internal object DocumentAccess {
    /** MIME types the App opens. */
    val SUPPORTED_MIME_PREFIXES: List<String> = listOf("video/", "image/")

    /**
     * Takes the long-term read permission when the grant allows it (`FLAG_GRANT_PERSISTABLE_URI_PERMISSION`).
     * Returns false for temporary grants ("打开方式" / share) and providers that refuse.
     */
    fun takeRead(resolver: ContentResolver, uri: Uri, grantFlags: Int): Boolean {
        if (grantFlags and Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION == 0) return false
        return try {
            resolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
            true
        } catch (_: SecurityException) {
            false
        }
    }

    /** Releases the long-term permission (record deleted or evicted beyond 200 records). */
    fun releaseRead(resolver: ContentResolver, uri: Uri) {
        try {
            resolver.releasePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
        } catch (_: SecurityException) {
            // Not held (temporary grant, already released): nothing to release.
        }
    }

    /** Whether the App holds a long-term read permission for [uri]. */
    fun holdsRead(resolver: ContentResolver, uri: Uri): Boolean =
        resolver.persistedUriPermissions.any { it.uri == uri && it.isReadPermission }

    /** `"OK"` / `"MISSING"` / `"REVOKED"` for a recorded document. */
    fun checkAccess(resolver: ContentResolver, uri: Uri): String = try {
        resolver.openAssetFileDescriptor(uri, "r")?.use { "OK" } ?: "MISSING"
    } catch (_: FileNotFoundException) {
        "MISSING"
    } catch (_: SecurityException) {
        "REVOKED"
    } catch (_: IllegalArgumentException) {
        // Provider no longer knows the document id.
        "MISSING"
    } catch (_: IllegalStateException) {
        "MISSING"
    }

    /** Document map, or null when [uri] is not a supported video/image. */
    fun describe(resolver: ContentResolver, uri: Uri, persistable: Boolean, fallbackMime: String? = null): Map<String, Any?>? {
        val mime = runCatching { resolver.getType(uri) }.getOrNull() ?: fallbackMime
        if (mime != null && SUPPORTED_MIME_PREFIXES.none { mime.startsWith(it) }) return null
        var name: String? = null
        var size: Long? = null
        runCatching {
            resolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE), null, null, null)?.use { c ->
                if (c.moveToFirst()) {
                    val n = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    val s = c.getColumnIndex(OpenableColumns.SIZE)
                    if (n >= 0 && !c.isNull(n)) name = c.getString(n)
                    if (s >= 0 && !c.isNull(s)) size = c.getLong(s)
                }
            }
        }
        return mapOf(
            "uri" to uri.toString(),
            "displayName" to (name ?: uri.lastPathSegment.orEmpty()),
            "mimeType" to mime,
            "sizeBytes" to size,
            "persistable" to persistable,
        )
    }

    /** URIs carried by a picker result or an incoming intent (`data` and `clipData`). */
    fun urisOf(intent: Intent?): List<Uri> {
        if (intent == null) return emptyList()
        val out = LinkedHashSet<Uri>()
        intent.data?.let(out::add)
        intent.clipData?.let { clip ->
            for (i in 0 until clip.itemCount) clip.getItemAt(i).uri?.let(out::add)
        }
        return out.toList()
    }
}
