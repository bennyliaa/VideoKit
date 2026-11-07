package com.videokit.videokit_app

import android.app.Application
import com.videokit.flutter.VideoKitFlutter

/**
 * VideoKit App process (04A P3/P4): `lib/main.dart` always talks to the real native Kit, so the plugin uses the
 * real backend in debug builds too (the Dart demo entry `lib/main_demo.dart` never reaches the native Kit).
 *
 * Also registers the precheck sink `registered:app-export` (capabilities and free space for `checkExport`) and
 * removes export temporaries a killed process may have left behind.
 */
class VideoKitApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        VideoKitFlutter.useRealBackend()
        VideoKitFlutter.registerSink(PRECHECK_SINK_ID, PrecheckOutputSink(this))
        ContentUriOutputSink.deleteStaleTemporaries(this)
    }

    companion object {
        /** Sink id the Dart `PluginBackend.exportSink` refers to. */
        const val PRECHECK_SINK_ID: String = "app-export"
    }
}
