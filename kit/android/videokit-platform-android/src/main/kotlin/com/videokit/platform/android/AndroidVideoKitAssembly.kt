package com.videokit.platform.android

import android.content.Context
import android.os.SystemClock
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.core.CoreOptions
import com.videokit.core.spi.Clock
import com.videokit.core.spi.PlatformEngines
import com.videokit.core.spi.Scheduler
import com.videokit.image.android.AndroidImageEngine
import com.videokit.media3.Media3PlaybackEngine
import com.videokit.media3.RetrieverFrameSource
import com.videokit.playback.PlaybackVideoKit
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi

/**
 * The real VideoKit on Android (02 §4.0.1 `VideoKitFactory` assembly): core runtime and playback sessions over the
 * Media3 playback engine, the platform image engine (VK-M2) and the Android capability probe. Reached through
 * `VideoKitFactory.create`; editing and export (VK-M4+) are not assembled yet and the capability report says so.
 */
public object AndroidVideoKitAssembly {
    /** Creates the real VideoKit; keeps only the application context. */
    public fun create(context: Context, config: VideoKitConfig): VideoKit {
        val appContext = context.applicationContext
        val engines = PlatformEngines(
            playback = Media3PlaybackEngine(appContext),
            capabilities = AndroidCapabilityProbe(appContext),
            clock = AndroidClock,
            scheduler = AndroidScheduler,
            images = AndroidImageEngine(),
            frames = RetrieverFrameSource(),
        )
        return PlaybackVideoKit.create(config, engines, CoreOptions())
    }
}

/** System clocks: monotonic elapsed realtime and wall clock. */
internal object AndroidClock : Clock {
    override fun monotonicUs(): Long = SystemClock.elapsedRealtimeNanos() / 1_000L

    override fun epochMs(): Long = System.currentTimeMillis()
}

/** Dispatchers of the runtime (02 §5): host reads on IO, work on Default, one serial lane per name. */
internal object AndroidScheduler : Scheduler {
    override val io: CoroutineDispatcher get() = Dispatchers.IO

    override val compute: CoroutineDispatcher get() = Dispatchers.Default

    @OptIn(ExperimentalCoroutinesApi::class)
    override fun serial(name: String): CoroutineDispatcher = Dispatchers.Default.limitedParallelism(1)
}
