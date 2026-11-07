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
        setSize(width, height)
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
        setSize(width, height)
        attach()
    }

    /**
     * Sizes the producer to the content, at most [MAX_TEXTURE_SIDE] on the longest side (large images: the engine
     * draws the whole image into the texture and adds tiles of zoomed regions, videokit-image `ImageRules`).
     */
    private fun setSize(width: Int, height: Int) {
        val w = width.coerceAtLeast(1)
        val h = height.coerceAtLeast(1)
        val factor = minOf(1.0, MAX_TEXTURE_SIDE.toDouble() / maxOf(w, h))
        producer.setSize((w * factor).toInt().coerceAtLeast(1), (h * factor).toInt().coerceAtLeast(1))
    }

    fun dispose() {
        if (disposed) return
        disposed = true
        session.detachSurface()
        producer.release()
    }
}

/** Longest texture side (same as `ImageRules.MAX_TEXTURE_SIDE` of videokit-image). */
internal const val MAX_TEXTURE_SIDE: Int = 4096
