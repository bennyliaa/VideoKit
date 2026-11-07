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
 * [create] assembles the real implementation of `videokit-platform-android` (core runtime + Media3 playback engine +
 * Android capability probe). That module is looked up by name, so hosts that only compile against the API do not
 * pull the engine in; when it is not packaged, [create] throws [IllegalStateException] with
 * [IMPLEMENTATION_UNAVAILABLE] (tests and demos then use `FakeVideoKit` from `videokit-testkit`).
 */
public object VideoKitFactory {
    /** Error message used when no implementation is packaged (English, not user facing). */
    public const val IMPLEMENTATION_UNAVAILABLE: String =
        "VIDEOKIT_IMPLEMENTATION_UNAVAILABLE: no VideoKit implementation is available in this build " +
            "(add com.videokit:videokit-platform-android; use FakeVideoKit from videokit-testkit for tests)."

    /** Assembly object of `videokit-platform-android` (`AndroidVideoKitAssembly.create(Context, VideoKitConfig)`). */
    internal const val ASSEMBLY_CLASS: String = "com.videokit.platform.android.AndroidVideoKitAssembly"

    /** Creates a VideoKit instance. Only `context.applicationContext` is kept; no Activity is held. */
    public fun create(context: Context, config: VideoKitConfig): VideoKit {
        val assembly = try {
            Class.forName(ASSEMBLY_CLASS)
        } catch (missing: ClassNotFoundException) {
            throw IllegalStateException(IMPLEMENTATION_UNAVAILABLE, missing)
        }
        val instance = assembly.getField("INSTANCE").get(null)
        val method = assembly.getMethod("create", Context::class.java, VideoKitConfig::class.java)
        return try {
            method.invoke(instance, context.applicationContext, config) as VideoKit
        } catch (failure: java.lang.reflect.InvocationTargetException) {
            throw failure.targetException
        }
    }
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
