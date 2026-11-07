package com.videokit.flutter.debug

import android.content.Context
import com.videokit.api.MediaKind
import com.videokit.api.SinkCapabilities
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputSink
import com.videokit.flutter.VideoKitBackend
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeVideoKit
import com.videokit.testkit.FakeVideoKitOptions
import com.videokit.testkit.RecordingOutputSink
import com.videokit.testkit.android.AndroidTestPattern
import com.videokit.testkit.demo
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob

/**
 * M0 default backend of debug builds (14 §8.4 FakeBackend): the Kotlin Fake from videokit-testkit, with the
 * test pattern drawn onto SurfaceProducer surfaces at about 30 fps. This class exists only in the debug
 * source set, so release builds cannot reach it (14 §11.4). Found by reflection in VideoKitFlutter.
 */
object DebugFakeBackend : VideoKitBackend {
    override val isDemo: Boolean = true

    override fun create(context: Context, config: VideoKitConfig): VideoKit {
        val options = AndroidTestPattern.install(FakeVideoKitOptions(scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)))
        return FakeVideoKit.fromConfig(config, options).also { kit ->
            kit.clock.drive(CoroutineScope(SupervisorJob() + Dispatchers.Default))
        }
    }

    override fun demoSource(scenarioId: String, token: String, kind: MediaKind): VideoKitMediaSource =
        FakeMediaSources.demo(scenarioId, token, kind)

    override fun demoSink(): VideoKitOutputSink = RecordingOutputSink(SinkCapabilities(sequentialWrite = true, randomWrite = true))
}
