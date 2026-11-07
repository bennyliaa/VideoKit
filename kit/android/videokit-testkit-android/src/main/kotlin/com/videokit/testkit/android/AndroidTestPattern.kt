package com.videokit.testkit.android

import android.graphics.Canvas
import android.graphics.Paint
import android.view.Surface
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.android.AndroidSurface
import com.videokit.testkit.FakeVideoKitOptions
import com.videokit.testkit.TestPatternFrame
import com.videokit.testkit.TestPatternTarget

/**
 * Draws the Fake test pattern (color blocks + time code + last 4 characters of the session id + `DEMO`
 * marker, 14 §8.4) onto an Android [Surface] with [Surface.lockHardwareCanvas].
 *
 * The time code, session tag and `DEMO` marker are technical, locale independent markers of demo
 * content, not user-facing copy (13 §3.1); the time code is formatted with ASCII digits.
 */
public class SurfaceTestPatternTarget(private val surface: Surface) : TestPatternTarget {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    @Volatile
    private var released = false

    override fun draw(frame: TestPatternFrame): Boolean {
        if (released || !surface.isValid) return false
        val canvas: Canvas = try {
            surface.lockHardwareCanvas() ?: return false
        } catch (_: IllegalStateException) {
            return false
        } catch (_: IllegalArgumentException) {
            return false
        }
        try {
            render(canvas, frame)
        } finally {
            surface.unlockCanvasAndPost(canvas)
        }
        return true
    }

    override fun release() {
        released = true
    }

    private fun render(canvas: Canvas, frame: TestPatternFrame) {
        val w = canvas.width.toFloat().takeIf { it > 0f } ?: frame.width.toFloat()
        val h = canvas.height.toFloat().takeIf { it > 0f } ?: frame.height.toFloat()
        canvas.drawColor(frame.backgroundArgb)
        paint.style = Paint.Style.FILL
        frame.blocks.forEach { block ->
            paint.color = block.argb
            canvas.drawRect(block.left * w, block.top * h, block.right * w, block.bottom * h, paint)
        }
        paint.color = 0xFFFFFFFF.toInt()
        paint.textSize = h * 0.08f
        canvas.drawText(frame.timecode, w * 0.05f, h * 0.82f, paint)
        canvas.drawText("#${frame.sessionTag}", w * 0.05f, h * 0.94f, paint)
        paint.textSize = h * 0.1f
        canvas.drawText(frame.label, w * 0.7f, h * 0.94f, paint)
    }
}

/** Android wiring of the Fake test pattern. */
public object AndroidTestPattern {
    /** Pattern target factory for `FakeVideoKitOptions.patternTargetFactory`: draws on [AndroidSurface] targets only. */
    public val targetFactory: (VideoKitSurfaceTarget) -> TestPatternTarget? = { target ->
        (target as? AndroidSurface)?.let { SurfaceTestPatternTarget(it.surface) }
    }

    /** [options] with the Android test pattern renderer installed. */
    public fun install(options: FakeVideoKitOptions = FakeVideoKitOptions()): FakeVideoKitOptions =
        options.copy(patternTargetFactory = targetFactory)
}
