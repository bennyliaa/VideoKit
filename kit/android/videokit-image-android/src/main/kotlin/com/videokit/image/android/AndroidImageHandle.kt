package com.videokit.image.android

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.BitmapRegionDecoder
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.ImageDecoder
import android.graphics.Matrix
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.drawable.Animatable2
import android.graphics.drawable.AnimatedImageDrawable
import android.graphics.drawable.Drawable
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import android.os.SystemClock
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.android.AndroidSurface
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.ImageEngineState
import com.videokit.core.spi.ImageHandle
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageOpenOptions
import com.videokit.core.spi.ImageRenderPlan
import com.videokit.core.spi.ImageStatus
import com.videokit.core.spi.ImageTile
import com.videokit.core.spi.PixelRect
import com.videokit.core.spi.SpiException
import com.videokit.image.ImageRules
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.coroutines.CoroutineContext

/**
 * One opened image (see [AndroidImageEngine]). Decoding runs on `Dispatchers.IO`; bitmaps, the animation and the
 * surface are only touched on the image thread, which also runs the frame callbacks of the animation.
 *
 * Drawing: the whole image is fitted into the surface (the UI zooms the texture, 06 §5); tiles are drawn over the
 * base at their place. Static images draw with a hardware canvas; animations draw with a software canvas, where
 * `AnimatedImageDrawable` schedules its next frame through the drawable callback.
 */
internal class AndroidImageHandle(
    private val bytes: ByteArray,
    probed: ProbedImage,
    options: ImageOpenOptions,
    private val config: AndroidImageConfig,
) : ImageHandle {
    override val info: ImageInfo = probed.info
    private val storedSize = probed.storedSize
    private val thread = HandlerThread("videokit-image").apply { start() }
    private val handler = Handler(thread.looper)
    private val dispatcher = ImageThreadDispatcher(handler)
    private val mutableState = MutableStateFlow(ImageEngineState(ImageStatus.OPENED))
    private val paint = Paint(Paint.FILTER_BITMAP_FLAG)

    // Image thread only.
    private var target: AndroidSurface? = null
    private var base: Bitmap? = null
    private var tiles: Map<ImageTile, Bitmap> = emptyMap()
    private var animation: AnimatedImageDrawable? = null
    private var looping = options.looping
    private var animating = false
    private var ended = false
    private var playedUs = 0L
    private var resumedAtMs = 0L
    private var drawPosted = false
    private var closed = false

    @Volatile
    private var regionDecoder: BitmapRegionDecoder? = null

    @Volatile
    private var regionDecoderFailed = false

    override val state: StateFlow<ImageEngineState> = mutableState.asStateFlow()

    private val drawCallback = object : Drawable.Callback {
        override fun invalidateDrawable(who: Drawable) {
            postDraw()
        }

        override fun scheduleDrawable(who: Drawable, what: Runnable, `when`: Long) {
            handler.postAtTime(what, who, `when`)
        }

        override fun unscheduleDrawable(who: Drawable, what: Runnable) {
            handler.removeCallbacks(what, who)
        }
    }

    private val ticker = object : Runnable {
        override fun run() {
            if (closed || !animating) return
            publishPosition()
            handler.postDelayed(this, TICK_MS)
        }
    }

    // ------------------------------------------------------------------ decoding

    override suspend fun render(plan: ImageRenderPlan) {
        if (info.animated) renderAnimation(plan) else renderStatic(plan)
    }

    private suspend fun renderStatic(plan: ImageRenderPlan) {
        val current = withContext(dispatcher) { base?.takeIf { it.width == plan.decodeSize.width && it.height == plan.decodeSize.height } }
        val newBase = current ?: decode(ErrorStage.DECODE) { decodeWhole(plan.decodeSize, ImageDecoder.ALLOCATOR_DEFAULT) }
        val kept = withContext(dispatcher) { tiles.filterKeys { it in plan.tiles } }
        val decoded = mutableMapOf<ImageTile, Bitmap>()
        try {
            for (tile in plan.tiles) {
                if (tile in kept) continue
                currentCoroutineContext().ensureActive()
                decodeTile(tile)?.let { decoded[tile] = it }
            }
        } catch (failure: Throwable) {
            decoded.values.forEach(Bitmap::recycle)
            if (newBase !== current) newBase.recycle()
            throw failure
        }
        withContext(dispatcher) {
            if (closed) {
                decoded.values.forEach(Bitmap::recycle)
                if (newBase !== current) newBase.recycle()
                return@withContext
            }
            if (newBase !== base) base?.recycle()
            base = newBase
            tiles.forEach { (tile, bitmap) -> if (tile !in kept) bitmap.recycle() }
            tiles = kept + decoded
            mutableState.update {
                it.copy(status = ImageStatus.READY, decodedBytes = heldBytes(), plan = plan, error = null)
            }
            draw()
        }
    }

    private suspend fun renderAnimation(plan: ImageRenderPlan) {
        val current = withContext(dispatcher) { animation?.takeIf { mutableState.value.plan?.decodeSize == plan.decodeSize } }
        if (current != null) {
            withContext(dispatcher) { mutableState.update { it.copy(plan = plan) } }
            return
        }
        val drawable = decode(ErrorStage.DECODE) { decodeAnimation(plan.decodeSize) }
        withContext(dispatcher) {
            if (closed) return@withContext
            val wasAnimating = animating
            replaceAnimation(drawable)
            mutableState.update {
                it.copy(
                    status = if (ended) ImageStatus.ENDED else ImageStatus.READY,
                    decodedBytes = ImageRules.baseBytes(info, plan.decodeSize),
                    plan = plan,
                    error = null,
                )
            }
            if (wasAnimating) startAnimation() else draw()
        }
    }

    /** Runs a decode on IO, mapping failures to stable errors and reporting FAILED. */
    private suspend fun <T> decode(stage: ErrorStage, block: () -> T): T = withContext(Dispatchers.IO) {
        try {
            block()
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Throwable) {
            if (failure !is Exception && failure !is OutOfMemoryError) throw failure
            val error = ImageErrors.decodeFailure(failure, stage)
            mutableState.update { it.copy(status = ImageStatus.FAILED, error = error) }
            throw SpiException(error)
        }
    }

    private fun decodeWhole(size: Size, allocator: Int): Bitmap =
        ImageDecoder.decodeBitmap(ImageDecoder.createSource(ByteBuffer.wrap(bytes))) { decoder, _, _ ->
            decoder.setTargetSize(size.width, size.height)
            decoder.allocator = allocator
        }

    private fun decodeAnimation(size: Size): AnimatedImageDrawable {
        val drawable = ImageDecoder.decodeDrawable(ImageDecoder.createSource(ByteBuffer.wrap(bytes))) { decoder, _, _ ->
            decoder.setTargetSize(size.width, size.height)
            // The software canvas of the animation path cannot draw hardware bitmaps.
            decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
        }
        return drawable as? AnimatedImageDrawable
            ?: throw SpiException(StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "IMAGE_NOT_ANIMATED"))
    }

    /** One tile from the region decoder, rotated to the oriented image; `null` when regions cannot be decoded. */
    private fun decodeTile(tile: ImageTile): Bitmap? {
        val decoder = regionDecoder() ?: return null
        val stored = TileGeometry.toStored(tile.region, storedSize, info.orientationDeg)
        val options = BitmapFactory.Options().apply { inSampleSize = tile.sampleSize }
        val raw = try {
            synchronized(decoder) { decoder.decodeRegion(Rect(stored.left, stored.top, stored.right, stored.bottom), options) }
        } catch (failure: Exception) {
            throw SpiException(ImageErrors.decodeFailure(failure, ErrorStage.DECODE))
        } catch (failure: OutOfMemoryError) {
            throw SpiException(ImageErrors.decodeFailure(failure, ErrorStage.DECODE))
        } ?: return null
        if (info.orientationDeg == 0) return raw
        val matrix = Matrix().apply { postRotate(info.orientationDeg.toFloat()) }
        return Bitmap.createBitmap(raw, 0, 0, raw.width, raw.height, matrix, true).also { if (it !== raw) raw.recycle() }
    }

    private fun regionDecoder(): BitmapRegionDecoder? {
        if (!info.regionDecodable || regionDecoderFailed) return null
        regionDecoder?.let { return it }
        synchronized(this) {
            regionDecoder?.let { return it }
            return try {
                BitmapRegionDecoder.newInstance(bytes, 0, bytes.size).also { regionDecoder = it }
            } catch (_: Exception) {
                // Tiles are an enhancement: the base decode stays on screen (15 §2.3).
                regionDecoderFailed = true
                null
            }
        }
    }

    private fun heldBytes(): Long = (base?.allocationByteCount?.toLong() ?: 0L) + tiles.values.sumOf { it.allocationByteCount.toLong() }

    // ------------------------------------------------------------------ drawing (image thread)

    override fun attach(target: VideoKitSurfaceTarget) {
        val surface = target as? AndroidSurface ?: return
        handler.post {
            if (closed) return@post
            this.target = surface
            draw()
        }
    }

    override fun detach() {
        handler.post { target = null }
    }

    private fun postDraw() {
        if (drawPosted) return
        drawPosted = true
        handler.post {
            drawPosted = false
            draw()
        }
    }

    private fun draw() {
        val surface = target?.surface ?: return
        if (closed || !surface.isValid) return
        val drawable = animation
        val image = base
        if (drawable == null && image == null) return
        val canvas: Canvas = try {
            if (drawable != null) surface.lockCanvas(null) else surface.lockHardwareCanvas()
        } catch (_: Exception) {
            return
        }
        try {
            canvas.drawColor(Color.TRANSPARENT, PorterDuff.Mode.CLEAR)
            val dest = fittedRect(canvas.width, canvas.height)
            if (drawable != null) {
                drawable.setBounds(dest.left.toInt(), dest.top.toInt(), dest.right.toInt(), dest.bottom.toInt())
                drawable.draw(canvas)
            } else if (image != null) {
                canvas.drawBitmap(image, null, dest, paint)
                val scaleX = dest.width() / info.size.width
                val scaleY = dest.height() / info.size.height
                tiles.forEach { (tile, bitmap) ->
                    val r = tile.region
                    val tileDest = RectF(
                        dest.left + r.left * scaleX,
                        dest.top + r.top * scaleY,
                        dest.left + r.right * scaleX,
                        dest.top + r.bottom * scaleY,
                    )
                    canvas.drawBitmap(bitmap, null, tileDest, paint)
                }
            }
        } finally {
            runCatching { surface.unlockCanvasAndPost(canvas) }
        }
    }

    /** The whole image fitted (up or down) into a surface of [width] × [height], centred. */
    private fun fittedRect(width: Int, height: Int): RectF {
        val factor = minOf(width.toFloat() / info.size.width, height.toFloat() / info.size.height)
        val fittedWidth = info.size.width * factor
        val fittedHeight = info.size.height * factor
        val left = (width - fittedWidth) / 2f
        val top = (height - fittedHeight) / 2f
        return RectF(left, top, left + fittedWidth, top + fittedHeight)
    }

    // ------------------------------------------------------------------ animation (image thread)

    private fun replaceAnimation(drawable: AnimatedImageDrawable) {
        animation?.let {
            it.stop()
            it.callback = null
            it.clearAnimationCallbacks()
        }
        drawable.repeatCount = if (looping) AnimatedImageDrawable.REPEAT_INFINITE else 0
        drawable.callback = drawCallback
        drawable.registerAnimationCallback(
            object : Animatable2.AnimationCallback() {
                override fun onAnimationEnd(drawable: Drawable) {
                    if (closed || drawable !== animation) return
                    onEnded()
                }
            },
        )
        animation = drawable
    }

    private fun startAnimation() {
        val drawable = animation ?: return
        if (!animating) resumedAtMs = SystemClock.uptimeMillis()
        animating = true
        drawable.start()
        handler.removeCallbacks(ticker)
        handler.post(ticker)
        publishPosition()
        postDraw()
    }

    private fun onEnded() {
        if (animating) playedUs += (SystemClock.uptimeMillis() - resumedAtMs) * 1_000L
        animating = false
        ended = true
        handler.removeCallbacks(ticker)
        mutableState.update { it.copy(status = ImageStatus.ENDED, animating = false, positionUs = info.loopDurationUs ?: playedUs) }
    }

    private fun publishPosition() {
        val elapsed = playedUs + if (animating) (SystemClock.uptimeMillis() - resumedAtMs) * 1_000L else 0L
        val loop = info.loopDurationUs
        val position = when {
            loop == null || loop <= 0L -> elapsed
            looping -> elapsed % loop
            else -> minOf(elapsed, loop)
        }
        mutableState.update { it.copy(positionUs = position, animating = animating) }
    }

    override suspend fun play() {
        if (!info.animated) return
        withContext(dispatcher) {
            if (closed || ended || mutableState.value.status == ImageStatus.FAILED) return@withContext
            startAnimation()
        }
    }

    override suspend fun pause() {
        if (!info.animated) return
        withContext(dispatcher) {
            if (!animating) return@withContext
            playedUs += (SystemClock.uptimeMillis() - resumedAtMs) * 1_000L
            animating = false
            animation?.stop()
            handler.removeCallbacks(ticker)
            publishPosition()
        }
    }

    override suspend fun restart() {
        if (!info.animated) return
        // A fresh drawable starts at the first frame, whatever the platform does on start() after stop().
        val size = mutableState.value.plan?.decodeSize ?: ImageRules.fitWithin(info.size, ImageRules.textureSizeFor(info.size))
        val drawable = decode(ErrorStage.DECODE) { decodeAnimation(size) }
        withContext(dispatcher) {
            if (closed) return@withContext
            val wasAnimating = animating
            replaceAnimation(drawable)
            ended = false
            playedUs = 0L
            animating = false
            mutableState.update { it.copy(status = ImageStatus.READY, positionUs = 0L, animating = false) }
            if (wasAnimating) startAnimation() else draw()
        }
    }

    override suspend fun setLooping(looping: Boolean) {
        withContext(dispatcher) {
            this@AndroidImageHandle.looping = looping
            animation?.repeatCount = if (looping) AnimatedImageDrawable.REPEAT_INFINITE else 0
        }
    }

    // ------------------------------------------------------------------ thumbnails

    override suspend fun thumbnail(maxSize: Size): ThumbnailResult.Captured {
        val size = ImageRules.fitWithin(info.size, maxSize)
        val bitmap = decode(ErrorStage.DECODE) { decodeWhole(size, ImageDecoder.ALLOCATOR_SOFTWARE) }
        return withContext(Dispatchers.IO) {
            try {
                val out = ByteArrayOutputStream()
                if (!bitmap.compress(Bitmap.CompressFormat.JPEG, config.jpegQuality, out)) {
                    throw SpiException(StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.DECODE, "THUMBNAIL:ENCODE"))
                }
                ThumbnailResult.Captured(out.toByteArray(), bitmap.width, bitmap.height)
            } finally {
                bitmap.recycle()
            }
        }
    }

    // ------------------------------------------------------------------ release

    override fun close() {
        if (Looper.myLooper() == handler.looper) {
            releaseOnThread()
        } else {
            val done = CountDownLatch(1)
            if (handler.post {
                    releaseOnThread()
                    done.countDown()
                }
            ) {
                done.await(CLOSE_TIMEOUT_MS, TimeUnit.MILLISECONDS)
            }
        }
        thread.quitSafely()
    }

    private fun releaseOnThread() {
        if (closed) return
        closed = true
        handler.removeCallbacksAndMessages(null)
        animation?.let {
            it.stop()
            it.callback = null
            it.clearAnimationCallbacks()
        }
        animation = null
        base?.recycle()
        base = null
        tiles.values.forEach(Bitmap::recycle)
        tiles = emptyMap()
        target = null
        regionDecoder?.recycle()
        regionDecoder = null
        animating = false
        mutableState.update { it.copy(animating = false, decodedBytes = 0L) }
    }

    private companion object {
        const val TICK_MS = 250L
        const val CLOSE_TIMEOUT_MS = 2_000L
    }
}

/** Coordinates between the oriented image (plans) and the stored image (BitmapRegionDecoder). */
internal object TileGeometry {
    /** [rect] of the image oriented by [rotationDeg] (clockwise) in stored coordinates of a [stored] image. */
    fun toStored(rect: PixelRect, stored: Size, rotationDeg: Int): PixelRect = when (((rotationDeg % 360) + 360) % 360) {
        // Oriented (x, y) = stored rotated clockwise: stored x = y', stored y = H - x'.
        90 -> PixelRect(rect.top, stored.height - rect.right, rect.bottom, stored.height - rect.left)

        180 -> PixelRect(stored.width - rect.right, stored.height - rect.bottom, stored.width - rect.left, stored.height - rect.top)

        // Stored x = W - y', stored y = x'.
        270 -> PixelRect(stored.width - rect.bottom, rect.left, stored.width - rect.top, rect.right)

        else -> rect
    }
}

/** Dispatcher on the image thread. */
internal class ImageThreadDispatcher(private val handler: Handler) : CoroutineDispatcher() {
    override fun isDispatchNeeded(context: CoroutineContext): Boolean = Looper.myLooper() != handler.looper

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        if (!handler.post(block)) throw CancellationException("image thread stopped")
    }
}
