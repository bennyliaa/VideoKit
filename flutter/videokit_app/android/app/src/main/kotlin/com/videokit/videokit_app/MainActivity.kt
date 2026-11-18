package com.videokit.videokit_app

import android.content.Intent
import android.os.Bundle
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine

/**
 * VideoKit App activity (`singleTop`): hosts the App's document channels (REQ-APP-01/02/03).
 *
 * * Cold start: the launch intent ("打开方式" / share) goes to [IncomingChannel], which buffers it until Dart
 *   listens. It is not handled again when the activity is recreated (configuration change, restore from
 *   recents).
 * * Warm start: [onNewIntent].
 */
class MainActivity : FlutterActivity() {
    private var documents: DocumentsChannel? = null
    private var incoming: IncomingChannel? = null
    private var library: LibraryChannel? = null
    private var restored = false

    override fun onCreate(savedInstanceState: Bundle?) {
        restored = savedInstanceState != null ||
            (intent?.flags ?: 0) and Intent.FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY != 0
        super.onCreate(savedInstanceState)
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        val messenger = flutterEngine.dartExecutor.binaryMessenger
        documents = DocumentsChannel(this, messenger)
        // APP-LIB-A1: the private media library (copies, lock, FLAG_SECURE).
        library = LibraryChannel(this, messenger)
        incoming = IncomingChannel(applicationContext.contentResolver, messenger).also {
            if (!restored) it.handle(intent)
        }
    }

    override fun cleanUpFlutterEngine(flutterEngine: FlutterEngine) {
        documents?.dispose()
        incoming?.dispose()
        library?.dispose()
        documents = null
        incoming = null
        library = null
        super.cleanUpFlutterEngine(flutterEngine)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        incoming?.handle(intent)
    }

    // FlutterActivity is not a ComponentActivity, so the Activity Result API is not available here.
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (documents?.onActivityResult(requestCode, resultCode, data) == true) return
        if (library?.onActivityResult(requestCode, resultCode, data) == true) return
        super.onActivityResult(requestCode, resultCode, data)
    }
}
