package com.videokit.samplehost

import android.content.Context
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.android.VideoKitFactory

/**
 * Release builds never contain the Fake (14 §11.4): they use the real implementation (VK-M1, Media3). Release
 * builds have no demo media: a real source (document picker) is part of the next sample host batch.
 */
internal object HostKits {
    val isDemo: Boolean = false

    fun create(context: Context, callbacks: VideoKitHostCallbacks): VideoKit =
        VideoKitFactory.create(context, VideoKitConfig(hostCallbacks = callbacks, resourceBudget = SampleResourceBudget))

    @Suppress("UNUSED_PARAMETER")
    fun demoSource(scenarioId: String, token: String): VideoKitMediaSource =
        throw IllegalStateException("Release builds have no demo media; pick a real source (VK-M1)")
}
