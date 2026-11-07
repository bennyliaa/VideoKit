package com.videokit.image

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.ImageDetails
import com.videokit.api.MediaTransform
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceBudget
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceRequest
import com.videokit.api.SeekMode
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.EngineState
import com.videokit.core.spi.EngineStatus
import com.videokit.core.spi.ImageEngine
import com.videokit.core.spi.ImageEngineState
import com.videokit.core.spi.ImageHandle
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageOpenOptions
import com.videokit.core.spi.ImageRenderPlan
import com.videokit.core.spi.ImageStatus
import com.videokit.core.spi.PlaybackHandle
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlin.concurrent.Volatile

/**
 * One bound image (06 §6) as a [PlaybackHandle], so that the media session drives static and animated images with
 * the same state machine as videos (PLAYING/PAUSED/ENDED and looping for animations, 04A L1).
 *
 * The controller owns the image memory lease of the session ([lease], closed by the session after SourceReleased,
 * 06 §7) and turns the render target and the transform into [ImageRenderPlan]s ([ImageRules.plan]); a newer plan
 * supersedes a render in progress. Video-only operations are no-ops (the session rejects them for images).
 */
public class ImageController private constructor(
    private val image: ImageHandle,
    /** Image memory lease; the session closes it after SourceReleased. */
    public val lease: ResourceLease,
    /** Bytes of the lease (the quota of every plan). */
    public val quotaBytes: Long,
    /** Whether the quota is smaller than the image wanted (06 §6.2: degraded sampling, reported in the state). */
    public val degraded: Boolean,
    parent: CoroutineScope,
) : PlaybackHandle {
    private val scope = CoroutineScope(parent.coroutineContext + SupervisorJob(parent.coroutineContext[Job]))
    private val renderLock = Mutex()
    private val mutableState = MutableStateFlow(map(image.state.value, null))

    @Volatile
    private var target: VideoKitSurfaceTarget? = null

    @Volatile
    private var transform: MediaTransform = MediaTransform()

    @Volatile
    private var renderJob: Job? = null

    @Volatile
    private var renderFailure: VideoKitStableError? = null

    @Volatile
    private var closed = false

    /** Image information. */
    public val info: ImageInfo get() = image.info

    override val state: StateFlow<EngineState> = mutableState.asStateFlow()

    init {
        scope.launch { image.state.collect { mutableState.value = map(it, renderFailure) } }
    }

    /** Image facts for the session state (04A L2). */
    public fun details(): ImageDetails = ImageRules.detailsOf(info, image.state.value)

    /** Plan for the current target and transform. */
    public fun currentPlan(): ImageRenderPlan = ImageRules.plan(info, targetSize(), transform, quotaBytes)

    /**
     * Decodes the current plan and waits for it (bind: READY reports what is decoded); throws [SpiException] when
     * the image cannot be decoded (06 §6.2: corrupt images fail the bind with CORRUPT_MEDIA).
     */
    public suspend fun renderNow() {
        renderJob?.cancel()
        render(currentPlan())
        renderFailure?.let { throw SpiException(it) }
        image.state.value.error?.let { throw SpiException(it) }
    }

    /** Uses [transform] for the next plans (zoomed images decode tiles of the visible region). */
    public fun setTransform(transform: MediaTransform) {
        if (this.transform == transform) return
        this.transform = transform
        rerender()
    }

    override fun attach(target: VideoKitSurfaceTarget) {
        val resized = this.target?.let { it.width != target.width || it.height != target.height } ?: true
        this.target = target
        image.attach(target)
        if (resized) rerender()
    }

    override fun detach() {
        target = null
        image.detach()
    }

    override suspend fun play() {
        image.play()
    }

    override suspend fun pause() {
        image.pause()
    }

    /** Images cannot seek; position 0 restarts an animation (replay after ENDED). */
    override suspend fun seekTo(positionUs: Long, mode: SeekMode) {
        if (positionUs == 0L) image.restart()
    }

    override suspend fun setLooping(looping: Boolean) {
        image.setLooping(looping)
    }

    override suspend fun setSpeed(speed: Float): Unit = Unit

    override suspend fun setVolume(volume: Float): Unit = Unit

    override suspend fun setAudioEnabled(enabled: Boolean): Unit = Unit

    override suspend fun selectAudioTrack(trackId: String?): Unit = Unit

    override suspend fun selectSubtitleTrack(trackId: String?): Unit = Unit

    /** A JPEG thumbnail of the image (04A P1). */
    public suspend fun thumbnail(maxSize: Size): ThumbnailResult.Captured = image.thumbnail(maxSize)

    /** Releases bitmaps, the animation, the target and the read handles; the [lease] stays with the session. */
    override fun close() {
        if (closed) return
        closed = true
        scope.cancel()
        target = null
        image.close()
    }

    private fun rerender() {
        if (closed) return
        val previous = renderJob
        renderJob = scope.launch {
            previous?.cancel()
            render(currentPlan())
        }
    }

    private suspend fun render(plan: ImageRenderPlan) {
        renderLock.withLock {
            if (closed || image.state.value.plan == plan) return
            try {
                image.render(plan)
                renderFailure = null
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: SpiException) {
                renderFailure = failure.error
            } catch (failure: Exception) {
                renderFailure = StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "RENDER:${failure::class.simpleName}")
            }
            mutableState.value = map(image.state.value, renderFailure)
        }
    }

    private fun targetSize(): Size = target?.let { Size(it.width, it.height) }?.takeIf { it.width > 0 && it.height > 0 }
        ?: ImageRules.textureSizeFor(info.size)

    private fun map(engine: ImageEngineState, failure: VideoKitStableError?): EngineState {
        val error = engine.error ?: failure
        val status = when {
            error != null || engine.status == ImageStatus.FAILED -> EngineStatus.FAILED
            engine.status == ImageStatus.ENDED -> EngineStatus.ENDED
            else -> EngineStatus.READY
        }
        return EngineState(
            status = status,
            playing = engine.animating,
            positionUs = engine.positionUs,
            durationUs = image.info.loopDurationUs.takeIf { image.info.animated },
            bufferedUs = null,
            videoSize = image.info.size,
            audioTracks = emptyList(),
            subtitleTracks = emptyList(),
            error = if (status == EngineStatus.FAILED) {
                error ?: StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "IMAGE_FAILED")
            } else {
                null
            },
            mediaInfo = ImageRules.mediaInfoOf(image.info),
        )
    }

    public companion object {
        /**
         * Opens [source] with [engine] and reserves its image memory in [budget] (06 §6.2): the reservation for the
         * default target first, then smaller ones (degraded sampling) when denied. Throws [SpiException] with
         * `DECODER_RESOURCE_EXHAUSTED` when not even the smallest useful decode fits. Cancelling closes the image.
         */
        public suspend fun open(
            engine: ImageEngine,
            source: VideoKitMediaSource,
            budget: ResourceBudget,
            sessionId: String,
            priority: ResourcePriority,
            options: ImageOpenOptions,
            scope: CoroutineScope,
        ): ImageController {
            val image = engine.open(source, options)
            try {
                val wanted = ImageRules.reservationFor(image.info)
                var bytes: Long? = wanted
                while (bytes != null) {
                    val request = ResourceRequest(sessionId, ResourceKind.IMAGE_MEMORY, ResourceEstimate(bytes = bytes), priority)
                    when (val reservation = budget.reserve(request)) {
                        is ReservationResult.Granted -> return ImageController(image, reservation.lease, bytes, bytes < wanted, scope)
                        is ReservationResult.Denied -> bytes = ImageRules.degradedReservation(image.info, bytes)
                    }
                }
                throw SpiException(StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "IMAGE_MEMORY"))
            } catch (failure: Throwable) {
                withContext(NonCancellable) { runCatching { image.close() } }
                throw failure
            }
        }
    }
}
