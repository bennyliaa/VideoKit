package com.videokit.playback

import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitSession
import com.videokit.core.CoreOptions
import com.videokit.core.CoreVideoKit
import com.videokit.core.SessionContext
import com.videokit.core.SessionFactory
import com.videokit.core.spi.PlatformEngines
import kotlinx.coroutines.CoroutineScope

/** [SessionFactory] of the playback runtime: every session is a [PlaybackSession]. */
public object PlaybackSessionFactory : SessionFactory {
    override fun create(context: SessionContext): VideoKitSession = PlaybackSession(context)
}

/** Assembly of the real VideoKit with the playback runtime (02 §4.0); platforms pass their engines. */
public object PlaybackVideoKit {
    /** A [CoreVideoKit] whose sessions are [PlaybackSession]s over [engines]. */
    public fun create(
        config: VideoKitConfig,
        engines: PlatformEngines,
        options: CoreOptions = CoreOptions(),
        parentScope: CoroutineScope? = null,
    ): VideoKit = CoreVideoKit(config, engines, PlaybackSessionFactory, options, parentScope)
}
