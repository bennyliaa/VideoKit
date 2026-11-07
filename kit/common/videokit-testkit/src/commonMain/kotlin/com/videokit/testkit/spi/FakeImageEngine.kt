package com.videokit.testkit.spi

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.ImageEngine
import com.videokit.core.spi.ImageEngineState
import com.videokit.core.spi.ImageHandle
import com.videokit.core.spi.ImageInfo
import com.videokit.core.spi.ImageOpenOptions
import com.videokit.core.spi.ImageRenderPlan
import com.videokit.core.spi.ImageStatus
import com.videokit.core.spi.SpiException
import com.videokit.testkit.DemoThumbnail
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeScenario
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * The image engine of 02 §4.2 for JVM tests: reads the header through the host source like a real engine (probe
 * handle, then one kept handle), takes the size and loop length from the [FakeScenario], "decodes" plans by counting
 * their bytes and animates on the [FakeClock]. `demo:unsupported` images fail with UNSUPPORTED_CONTAINER,
 * `demo:corrupt` images fail their first decode with CORRUPT_MEDIA.
 */
public class FakeImageEngine(private val options: FakeEngineOptions = FakeEngineOptions()) : ImageEngine {
    /** Images that are open. */
    public val openHandles: Int get() = open.value

    /** Plans rendered so far, over all images (diagnostics for tile scheduling tests). */
    public val renderedPlans: List<ImageRenderPlan> get() = rendered.value

    private val open = MutableStateFlow(0)
    private val rendered = MutableStateFlow<List<ImageRenderPlan>>(emptyList())

    override fun supports(target: VideoKitSurfaceTarget): Boolean = options.supportsTarget(target)

    override suspend fun open(source: VideoKitMediaSource, options: ImageOpenOptions): ImageHandle {
        val scenario = this.options.scenarioResolver(source)
        var kept: VideoKitReadHandle? = null
        try {
            val probe = source.sourceFactory.open(OpenPurpose.PROBE)
            try {
                probe.readAt(0, ByteArray(HEADER_BYTES), 0, HEADER_BYTES)
            } finally {
                probe.close()
            }
            kept = source.sourceFactory.open(OpenPurpose.PLAYBACK)
            delay(scenario.loadDelayMs / 2)
            if (scenario.unsupportedContainer || scenario.unsupportedVideoCodec) {
                throw SpiException(StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "SCENARIO"))
            }
        } catch (failure: Throwable) {
            runCatching { kept?.close() }
            when (failure) {
                is CancellationException, is SpiException -> throw failure
                is Exception -> throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.BIND))
                else -> throw failure
            }
        }
        val animated = source.mediaKind == MediaKind.IMAGE_ANIMATED
        val info = ImageInfo(
            size = scenario.videoSize,
            animated = animated,
            loopDurationUs = scenario.animationLoopUs.takeIf { animated },
            frameCount = if (animated) (scenario.animationLoopUs / FRAME_US).toInt().coerceAtLeast(1) else 1,
            format = if (animated) "gif" else "png",
            hasAlpha = !animated,
            regionDecodable = !animated,
        )
        open.update { it + 1 }
        return FakeImageHandle(info, scenario, kept, options, this.options.clock, { plan -> rendered.update { it + plan } }) {
            open.update { it - 1 }
        }
    }

    private companion object {
        const val HEADER_BYTES = 32
        const val FRAME_US = 100_000L
    }
}

/** One fake image: decoded bytes follow the plans, the animation follows the clock. */
public class FakeImageHandle internal constructor(
    override val info: ImageInfo,
    private val scenario: FakeScenario,
    private val readHandle: VideoKitReadHandle?,
    openOptions: ImageOpenOptions,
    private val clock: FakeClock,
    private val onRendered: (ImageRenderPlan) -> Unit,
    private val onClosed: () -> Unit,
) : ImageHandle {
    private val scope = CoroutineScope(SupervisorJob())
    private val mutex = Mutex()
    private val mutableState = MutableStateFlow(ImageEngineState(ImageStatus.OPENED))
    private var looping = openOptions.looping
    private var lastClockUs = clock.elapsedUs.value
    private var closed = false
    private val clockJob: Job

    /** The attached render target, if any. */
    public var target: VideoKitSurfaceTarget? = null
        private set

    override val state: StateFlow<ImageEngineState> = mutableState.asStateFlow()

    init {
        clockJob = scope.launch(Dispatchers.Unconfined) { clock.elapsedUs.collect { now -> mutex.withLock { onClock(now) } } }
    }

    override suspend fun render(plan: ImageRenderPlan) {
        delay(DECODE_DELAY_MS)
        mutex.withLock {
            if (closed) return
            if (scenario.corruptAtUs != null) {
                val error = StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "SCENARIO")
                mutableState.update { it.copy(status = ImageStatus.FAILED, animating = false, error = error) }
                throw SpiException(error)
            }
            val base = plan.decodeSize.width.toLong() * plan.decodeSize.height * BYTES_PER_PIXEL * if (info.animated) 2 else 1
            val tiles = plan.tiles.sumOf { tile ->
                val width = (tile.region.width + tile.sampleSize - 1) / tile.sampleSize
                val height = (tile.region.height + tile.sampleSize - 1) / tile.sampleSize
                width.toLong() * height * BYTES_PER_PIXEL
            }
            mutableState.update {
                it.copy(
                    status = if (it.status ==
                        ImageStatus.OPENED
                    ) {
                        ImageStatus.READY
                    } else {
                        it.status
                    },
                    decodedBytes = base + tiles,
                    plan = plan,
                )
            }
            onRendered(plan)
        }
    }

    override fun attach(target: VideoKitSurfaceTarget) {
        this.target = target
    }

    override fun detach() {
        target = null
    }

    override suspend fun play() {
        if (!info.animated) return
        mutex.withLock { mutableState.update { if (it.status == ImageStatus.FAILED) it else it.copy(animating = true) } }
    }

    override suspend fun pause() {
        mutex.withLock { mutableState.update { it.copy(animating = false) } }
    }

    override suspend fun restart() {
        mutex.withLock {
            mutableState.update {
                if (it.status ==
                    ImageStatus.ENDED
                ) {
                    it.copy(status = ImageStatus.READY, positionUs = 0L)
                } else {
                    it.copy(positionUs = 0L)
                }
            }
        }
    }

    override suspend fun setLooping(looping: Boolean) {
        mutex.withLock { this.looping = looping }
    }

    override suspend fun thumbnail(maxSize: Size): ThumbnailResult.Captured {
        if (scenario.corruptAtUs != null) throw SpiException(StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "SCENARIO"))
        return DemoThumbnail.captured()
    }

    override fun close() {
        if (closed) return
        closed = true
        clockJob.cancel()
        scope.cancel()
        target = null
        mutableState.update { it.copy(animating = false, decodedBytes = 0L) }
        runCatching { readHandle?.close() }
        onClosed()
    }

    private fun onClock(nowUs: Long) {
        val delta = nowUs - lastClockUs
        lastClockUs = nowUs
        val current = mutableState.value
        if (delta <= 0 || closed || !current.animating || current.status != ImageStatus.READY) return
        val loop = (info.loopDurationUs ?: return).coerceAtLeast(1L)
        val to = current.positionUs + delta
        mutableState.update {
            when {
                to < loop -> it.copy(positionUs = to)

                looping -> it.copy(positionUs = to % loop)

                // Not looping (04A L1): stop on the last frame.
                else -> it.copy(positionUs = loop, status = ImageStatus.ENDED, animating = false)
            }
        }
    }

    private companion object {
        const val DECODE_DELAY_MS = 20L
        const val BYTES_PER_PIXEL = 4
    }
}
