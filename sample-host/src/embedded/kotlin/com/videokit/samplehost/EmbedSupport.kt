package com.videokit.samplehost

import android.app.Activity
import android.app.Application
import android.content.Intent
import com.videokit.api.VideoKit
import com.videokit.ui.android.VideoKitFlutter
import com.videokit.ui.android.VideoKitFlutterConfig

/**
 * embedded flavor: initializes the add-to-app bridge with the host's VideoKit (14 §9.1) when the Flutter module
 * (its generated plugin registrant and runtime) is packaged; otherwise the embed page is reported as unavailable.
 * Prewarming is done by the main screen (launch extra `prewarm`), so the 14 §9.3 first-frame measurement can compare
 * prewarmed and cold engines.
 */
internal object EmbedSupport {
    val inFlavor: Boolean = true

    private const val FLUTTER_MODULE_MARKER = "io.flutter.plugins.GeneratedPluginRegistrant"

    fun isAvailable(): Boolean = runCatching { Class.forName(FLUTTER_MODULE_MARKER) }.isSuccess

    fun initialize(app: Application, videoKit: VideoKit) {
        if (isAvailable()) VideoKitFlutter.initialize(app, VideoKitFlutterConfig(videoKit = videoKit, prewarmOnInit = false))
    }

    fun prewarm() {
        if (VideoKitFlutter.isInitialized) {
            VideoKitFlutter.prewarm()
            Metrics.log("prewarm")
        }
    }

    fun open(activity: Activity, page: String) {
        val intent = when (page) {
            MainActivity.PAGE_MULTIVIEW_FOUR -> MultiViewActivity.intent(activity, MultiViewActivity.MODE_FOUR_ENGINES)
            MainActivity.PAGE_MULTIVIEW_ONE -> MultiViewActivity.intent(activity, MultiViewActivity.MODE_ONE_ENGINE)
            else -> Intent(activity, EmbedActivity::class.java)
        }
        activity.startActivity(intent)
    }
}
