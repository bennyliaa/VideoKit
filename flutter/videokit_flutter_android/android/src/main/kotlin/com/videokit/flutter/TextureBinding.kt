package com.videokit.flutter

import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitSession
import com.videokit.api.android.AndroidSurface
import io.flutter.view.TextureRegistry

/**
 * One `SurfaceProducer` per session (14 §8.4): the surface is attached to the session when available and
 * detached when Flutter recycles it (background, memory trim); recreation re-attaches and reports the
 * texture id through [onChanged].
 */
internal class TextureBinding(
    registry: TextureRegistry,
    private val session: VideoKitSession,
    width: Int,
    height: Int,
    private val onChanged: (Long?) -> Unit,
) {
    private val producer: TextureRegistry.SurfaceProducer = registry.createSurfaceProducer()

    @Volatile
    private var disposed = false

    /** Texture id for `Texture(textureId)` on the Dart side. */
    val textureId: Long get() = producer.id()

    init {
        producer.setSize(width.coerceAtLeast(1), height.coerceAtLeast(1))
        producer.setCallback(
            object : TextureRegistry.SurfaceProducer.Callback {
                override fun onSurfaceAvailable() {
                    if (disposed) return
                    attach()
                    onChanged(producer.id())
                }

                override fun onSurfaceDestroyed() {
                    session.detachSurface()
                    onChanged(null)
                }

                @Deprecated("Superseded by onSurfaceDestroyed; kept for engines that still call it.")
                override fun onSurfaceCleanup() {
                    session.detachSurface()
                }
            },
        )
    }

    /** Attaches the current surface; returns the session's result (Unsupported when the backend cannot draw). */
    fun attach(): VideoKitCommandResult = session.attachSurface(AndroidSurface(producer.surface, producer.width, producer.height))

    fun resize(width: Int, height: Int) {
        if (disposed) return
        producer.setSize(width.coerceAtLeast(1), height.coerceAtLeast(1))
        attach()
    }

    fun dispose() {
        if (disposed) return
        disposed = true
        session.detachSurface()
        producer.release()
    }
}
