package com.videokit.samplehost

import android.app.Activity
import android.app.Application
import com.videokit.api.VideoKit

/** engine flavor: no Flutter, no add-to-app bridge (the size baseline of 14 §9.3). */
internal object EmbedSupport {
    val inFlavor: Boolean = false

    fun isAvailable(): Boolean = false

    @Suppress("UNUSED_PARAMETER")
    fun initialize(app: Application, videoKit: VideoKit) = Unit

    fun prewarm() = Unit

    @Suppress("UNUSED_PARAMETER")
    fun open(activity: Activity, page: String) = Unit
}
