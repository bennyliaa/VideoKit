package com.videokit.samplehost

import android.app.Application
import com.videokit.api.VideoKit

/**
 * The host owns one native VideoKit for the whole process, as LocalVideoBrowser would (05). The embedded flavor
 * hands the same instance to the add-to-app bridge.
 */
class SampleHostApp : Application() {
    /** Host callbacks (mock Browser). */
    val host: MockBrowserHost = MockBrowserHost()

    /** The host's VideoKit; `null` when the implementation is unavailable (release builds before VK-M1). */
    var videoKit: VideoKit? = null
        private set

    /** Why [videoKit] is unavailable (English diagnostic). */
    var unavailableReason: String? = null
        private set

    override fun onCreate() {
        super.onCreate()
        videoKit = runCatching { HostKits.create(this, host) }
            .onFailure { unavailableReason = it.message }
            .getOrNull()
        videoKit?.let { EmbedSupport.initialize(this, it) }
    }
}
