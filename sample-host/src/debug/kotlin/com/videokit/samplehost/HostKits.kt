package com.videokit.samplehost

import android.content.Context
import com.videokit.api.MediaKind
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitHostCallbacks
import com.videokit.api.VideoKitMediaSource
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeVideoKit
import com.videokit.testkit.android.AndroidTestPattern
import com.videokit.testkit.demo

/** Debug builds: the Kotlin Fake, drawing its test pattern into host surfaces and Flutter textures (14 §8.4). */
internal object HostKits {
    val isDemo: Boolean = true

    @Suppress("UNUSED_PARAMETER")
    fun create(context: Context, callbacks: VideoKitHostCallbacks): VideoKit = FakeVideoKit(callbacks, AndroidTestPattern.install())

    /** A demo media for [scenarioId] (`FakeScenario.NAMES`). */
    fun demoSource(scenarioId: String, token: String): VideoKitMediaSource =
        FakeMediaSources.demo(scenarioId, token, MediaKind.VIDEO, displayName = "demo-$scenarioId")
}
