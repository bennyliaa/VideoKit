package com.videokit.api.android

import android.content.Context
import android.os.ParcelFileDescriptor
import android.view.Surface
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.VideoKitWriteHandle

/**
 * Android entry point of VideoKit (04 §2, 02 §4.0.1).
 *
 * The real implementation (assembled in `videokit-platform-android`) arrives with VK-M1. Until then
 * [create] throws [IllegalStateException]; tests and demos use `FakeVideoKit` from `videokit-testkit`.
 */
public object VideoKitFactory {
    /** Error message used while no implementation is available (English, not user facing). */
    public const val IMPLEMENTATION_UNAVAILABLE: String =
        "VIDEOKIT_IMPLEMENTATION_UNAVAILABLE: no VideoKit implementation is available in this build " +
            "(the real implementation is delivered from VK-M1; use FakeVideoKit from videokit-testkit for M0)."

    /**
     * Creates a VideoKit instance. Only `context.applicationContext` is kept; no Activity is held.
     */
    @Suppress("UNUSED_PARAMETER") // Part of the stable signature; unused until VK-M1.
    public fun create(context: Context, config: VideoKitConfig): VideoKit = throw IllegalStateException(IMPLEMENTATION_UNAVAILABLE)
}

/**
 * Android render target (04 §4.4): the Flutter plugin passes the surface of a
 * `TextureRegistry.SurfaceProducer`; native engine-only hosts pass the surface of their own
 * `SurfaceView`/`TextureView`. VideoKit never releases the surface; its owner does.
 */
public class AndroidSurface(
    /** The surface to render into. */
    public val surface: Surface,
    override val width: Int,
    override val height: Int,
) : VideoKitSurfaceTarget {
    override fun toString(): String = "AndroidSurface(${width}x$height)"
}

/**
 * Write handle of a sink that declares `SinkCapabilities.fileDescriptor` (08 §5). The descriptor belongs to
 * the sink; VideoKit does not close it.
 */
public interface FileDescriptorWriteHandle : VideoKitWriteHandle {
    /** Descriptor of the temporary output, opened for read/write. */
    public fun fileDescriptor(): ParcelFileDescriptor
}
