package com.videokit.testkit.spi

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.MediaKind
import com.videokit.api.MediaProbeResult
import com.videokit.api.OpenPurpose
import com.videokit.api.PlaybackFeatures
import com.videokit.api.SeekMode
import com.videokit.api.Size
import com.videokit.api.SupportLevel
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.CapabilityProbe
import com.videokit.core.spi.Clock
import com.videokit.core.spi.EngineState
import com.videokit.core.spi.EngineStatus
import com.videokit.core.spi.PlatformEngines
import com.videokit.core.spi.PlaybackEngine
import com.videokit.core.spi.PlaybackHandle
import com.videokit.core.spi.PlaybackOpenOptions
import com.videokit.core.spi.Scheduler
import com.videokit.core.spi.SpiException
import com.videokit.testkit.FakeClock
import com.videokit.testkit.FakeScenario
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
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

/** A render target the fake engines accept (any other target type is "foreign", 04A I13). */
public class FakeRenderTarget(override val width: Int = 1920, override val height: Int = 1080) : com.videokit.api.VideoKitSurfaceTarget

/** Options of the fake platform engines. */
public data class FakeEngineOptions(
    /** Media clock; position advances with it while playing. */
    val clock: FakeClock = FakeClock(),
    /** Scenario per opened source (latencies, faults, tracks); default `demo:<name>` tokens. */
    val scenarioResolver: (VideoKitMediaSource) -> FakeScenario = FakeScenario::forSource,
    /** Render target types the engine accepts. */
    val supportsTarget: (VideoKitSurfaceTarget) -> Boolean = { it is FakeRenderTarget },
    /** Suggested hardware video sessions of the fake device. */
    val suggestedHardwareVideoSessions: Int = 4,
)

/**
 * The platform engines of 02 §4.2 for JVM tests of the real runtime (`CoreVideoKit` + `videokit-playback`): no
 * media is decoded, but host sources are opened, probed and closed like a real engine does, and playback position,
 * buffering, faults and end of media follow the [FakeScenario] on the [FakeClock].
 */
public object FakeEngines {
    /** Engines running on [dispatcher] (pass the test dispatcher for virtual time). */
    public fun platform(dispatcher: CoroutineDispatcher, options: FakeEngineOptions = FakeEngineOptions()): PlatformEngines =
        PlatformEngines(
            playback = FakePlaybackEngine(options),
            capabilities = FakeCapabilityProbe(options),
            clock = FakeSpiClock(options.clock),
            scheduler = FakeScheduler(dispatcher),
            images = FakeImageEngine(options),
            frames = FakeFrameSource(),
        )
}

/** [Clock] over the [FakeClock]. */
public class FakeSpiClock(private val clock: FakeClock, private val epochBaseMs: Long = 1_700_000_000_000L) : Clock {
    override fun monotonicUs(): Long = clock.elapsedUs.value

    override fun epochMs(): Long = epochBaseMs + clock.elapsedUs.value / 1_000L
}

/** [Scheduler] that runs everything on one dispatcher (tests: the test dispatcher). */
public class FakeScheduler(private val dispatcher: CoroutineDispatcher) : Scheduler {
    override val io: CoroutineDispatcher get() = dispatcher

    override val compute: CoroutineDispatcher get() = dispatcher

    override fun serial(name: String): CoroutineDispatcher = dispatcher
}

/** Fake [CapabilityProbe]: a mid-range device; a media probe opens and reads the source like a real probe. */
public class FakeCapabilityProbe(private val options: FakeEngineOptions = FakeEngineOptions()) : CapabilityProbe {
    override suspend fun device(): VideoKitCapabilities = VideoKitCapabilities(
        isDemo = true,
        suggestedHardwareVideoSessions = options.suggestedHardwareVideoSessions,
        maxSuggestedResolution = Size(3840, 2160),
        maxSuggestedFrameRate = 60,
        playbackFeatures = PlaybackFeatures(
            subtitles = SupportLevel.PARTIAL,
            audioTrackSelection = true,
            speeds = listOf(0.5f, 0.75f, 1f, 1.25f, 1.5f, 2f),
            exactSeek = true,
        ),
        imageFeatures = com.videokit.api.ImageFeatures(staticImages = true, animatedImages = true, largeImageTiling = true),
    )

    override suspend fun media(source: VideoKitMediaSource): MediaProbeResult {
        val scenario = options.scenarioResolver(source)
        try {
            val probe = source.sourceFactory.open(OpenPurpose.PROBE)
            try {
                probe.readAt(0, ByteArray(PROBE_BYTES), 0, PROBE_BYTES)
            } finally {
                probe.close()
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
        val playable = if (scenario.unsupportedContainer || (scenario.unsupportedVideoCodec && source.mediaKind == MediaKind.VIDEO)) {
            SupportLevel.UNSUPPORTED
        } else {
            SupportLevel.SUPPORTED
        }
        return MediaProbeResult(
            mediaToken = source.mediaToken,
            playable = playable,
            editable = SupportLevel.UNSUPPORTED,
            durationUs = if (source.mediaKind == MediaKind.VIDEO) scenario.durationUs else null,
            size = scenario.videoSize,
        )
    }

    private companion object {
        const val PROBE_BYTES = 64
    }
}

/** Fake [PlaybackEngine] (see [FakeEngines]). */
public class FakePlaybackEngine(private val options: FakeEngineOptions = FakeEngineOptions()) : PlaybackEngine {
    /** Handles that are open (diagnostics: closed handles leave the set). */
    public val openHandles: Int get() = open.value

    /** The most recently opened handle (test hooks such as [FakePlaybackHandle.loseAudioFocus]). */
    public var lastOpened: FakePlaybackHandle? = null
        private set

    private val open = MutableStateFlow(0)

    override fun supports(target: VideoKitSurfaceTarget): Boolean = options.supportsTarget(target)

    override suspend fun open(source: VideoKitMediaSource, options: PlaybackOpenOptions): PlaybackHandle {
        val scenario = this.options.scenarioResolver(source)
        if (scenario.resourceExhausted) {
            throw SpiException(
                StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "SCENARIO"),
            )
        }
        var playbackHandle: VideoKitReadHandle? = null
        try {
            val probe = source.sourceFactory.open(OpenPurpose.PROBE)
            try {
                probe.readAt(0, ByteArray(PROBE_BYTES), 0, PROBE_BYTES)
            } finally {
                probe.close()
            }
            playbackHandle = source.sourceFactory.open(OpenPurpose.PLAYBACK)
            delay(scenario.loadDelayMs)
            if (scenario.unsupportedContainer) {
                throw SpiException(
                    StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "SCENARIO"),
                )
            }
            if (scenario.unsupportedVideoCodec) {
                throw SpiException(StableErrors.of(ErrorCode.UNSUPPORTED_VIDEO_CODEC, ErrorStage.PROBE, "SCENARIO"))
            }
        } catch (failure: Throwable) {
            runCatching { playbackHandle?.close() }
            when (failure) {
                is CancellationException, is SpiException -> throw failure
                is Exception -> throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.BIND))
                else -> throw failure
            }
        }
        open.update { it + 1 }
        return FakePlaybackHandle(scenario, playbackHandle, options, this.options.clock) { open.update { it - 1 } }.also { lastOpened = it }
    }

    private companion object {
        const val PROBE_BYTES = 64
    }
}

/** One fake playback: position follows the clock while playing; faults and buffering come from the scenario. */
public class FakePlaybackHandle internal constructor(
    private val scenario: FakeScenario,
    private val readHandle: VideoKitReadHandle?,
    openOptions: PlaybackOpenOptions,
    private val clock: FakeClock,
    private val onClosed: () -> Unit,
) : PlaybackHandle {
    private val scope = CoroutineScope(SupervisorJob())
    private val mutex = Mutex()
    private val audio = scenario.audioTracks.map { if (scenario.unsupportedAudioCodec) it.copy(supported = false) else it }
    private val mutableState = MutableStateFlow(
        EngineState(
            status = EngineStatus.READY,
            playing = false,
            positionUs = openOptions.startPositionUs.coerceIn(0L, scenario.durationUs),
            durationUs = scenario.durationUs,
            bufferedUs = minOf(scenario.durationUs, BUFFER_AHEAD_US),
            videoSize = scenario.videoSize,
            audioTracks = audio,
            subtitleTracks = scenario.subtitleTracks,
            selectedAudioTrackId = audio.firstOrNull { it.supported }?.id,
            mediaInfo = com.videokit.api.MediaInfo(
                container = "mp4",
                videoCodec = "video/avc",
                audioCodec = audio.firstOrNull()?.codec,
                width = scenario.videoSize.width,
                height = scenario.videoSize.height,
                frameRate = 30f,
                durationUs = scenario.durationUs,
                // R2-06: the size the host reports for the open handle, not only the descriptor.
                fileSizeBytes = readHandle?.length,
            ),
        ),
    )
    private var speed = 1f
    private var looping = openOptions.looping
    private var bufferingDone = false
    private var bufferingRemainingUs = 0L
    private var lastClockUs = clock.elapsedUs.value
    private var closed = false
    private val clockJob: Job

    /** Whether audio output is enabled (diagnostics for multi-view tests). */
    public var audioEnabled: Boolean = openOptions.audioEnabled
        private set

    /** Current volume (diagnostics). */
    public var volume: Float = 1f
        private set

    /** The attached render target, if any. */
    public var target: VideoKitSurfaceTarget? = null
        private set

    override val state: StateFlow<EngineState> = mutableState.asStateFlow()

    init {
        clockJob = scope.launch(kotlinx.coroutines.Dispatchers.Unconfined) {
            clock.elapsedUs.collect { now -> mutex.withLock { onClock(now) } }
        }
    }

    override suspend fun play() {
        mutex.withLock { mutableState.update { if (it.status == EngineStatus.FAILED) it else it.copy(playing = true) } }
    }

    override suspend fun pause() {
        mutex.withLock { mutableState.update { it.copy(playing = false) } }
    }

    override suspend fun seekTo(positionUs: Long, mode: SeekMode) {
        delay(scenario.seekDelayMs)
        mutex.withLock {
            mutableState.update {
                val target = positionUs.coerceIn(0L, it.durationUs ?: positionUs)
                val status = if (it.status == EngineStatus.ENDED && target < (it.durationUs ?: 0L)) EngineStatus.READY else it.status
                it.copy(positionUs = target, status = status)
            }
        }
    }

    override suspend fun setSpeed(speed: Float) {
        mutex.withLock { this.speed = speed }
    }

    override suspend fun setVolume(volume: Float) {
        mutex.withLock { this.volume = volume }
    }

    override suspend fun setAudioEnabled(enabled: Boolean) {
        mutex.withLock { audioEnabled = enabled }
    }

    override suspend fun selectAudioTrack(trackId: String?) {
        mutex.withLock { mutableState.update { it.copy(selectedAudioTrackId = trackId ?: audio.firstOrNull { t -> t.supported }?.id) } }
    }

    override suspend fun selectSubtitleTrack(trackId: String?) {
        mutex.withLock { mutableState.update { it.copy(selectedSubtitleTrackId = trackId) } }
    }

    override suspend fun setLooping(looping: Boolean) {
        mutex.withLock { this.looping = looping }
    }

    /** Simulates another app taking the audio focus for good: the engine pauses and counts the loss (07 §4). */
    public suspend fun loseAudioFocus() {
        mutex.withLock { mutableState.update { it.copy(playing = false, audioFocusLosses = it.audioFocusLosses + 1) } }
    }

    override fun attach(target: VideoKitSurfaceTarget) {
        this.target = target
    }

    override fun detach() {
        target = null
    }

    override fun close() {
        if (closed) return
        closed = true
        clockJob.cancel()
        scope.cancel()
        target = null
        runCatching { readHandle?.close() }
        onClosed()
    }

    private fun onClock(nowUs: Long) {
        val delta = nowUs - lastClockUs
        lastClockUs = nowUs
        if (delta <= 0 || closed) return
        val current = mutableState.value
        if (!current.playing) return
        when (current.status) {
            EngineStatus.BUFFERING -> {
                bufferingRemainingUs -= delta
                if (bufferingRemainingUs <= 0) mutableState.update { it.copy(status = EngineStatus.READY) }
            }

            EngineStatus.READY -> advance(current, delta)

            else -> Unit
        }
    }

    private fun advance(current: EngineState, clockDeltaUs: Long) {
        val duration = current.durationUs ?: return
        val from = current.positionUs
        val to = from + (clockDeltaUs * speed).toLong()
        val buffering = scenario.buffering?.takeIf { !bufferingDone && it.atUs > from && it.atUs <= to }
        val corrupt = scenario.corruptAtUs?.takeIf { it > from && it <= to }
        val disconnect = scenario.disconnectAtUs?.takeIf { it > from && it <= to }
        val first = listOfNotNull(
            buffering?.atUs?.let { it to 0 },
            corrupt?.let { it to 1 },
            disconnect?.let { it to 2 },
            if (to >= duration) duration to 3 else null,
        ).minByOrNull { it.first }
        val position = first?.first ?: to
        mutableState.update { it.copy(positionUs = position, bufferedUs = minOf(duration, position + BUFFER_AHEAD_US)) }
        when (first?.second) {
            0 -> {
                bufferingDone = true
                bufferingRemainingUs = scenario.buffering?.forUs ?: 0L
                mutableState.update { it.copy(status = EngineStatus.BUFFERING) }
            }

            1 -> fail(StableErrors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "SCENARIO"))

            2 -> fail(StableErrors.of(ErrorCode.SOURCE_DISCONNECTED, ErrorStage.PLAYBACK, "SCENARIO"))

            3 -> if (looping) {
                mutableState.update { it.copy(positionUs = 0L) }
            } else {
                mutableState.update { it.copy(status = EngineStatus.ENDED, playing = false) }
            }

            else -> Unit
        }
    }

    private fun fail(error: com.videokit.api.VideoKitStableError) {
        mutableState.update { it.copy(status = EngineStatus.FAILED, playing = false, error = error) }
    }

    private companion object {
        const val BUFFER_AHEAD_US = 10_000_000L
    }
}

/** Fake [com.videokit.core.spi.FrameSource]: opens the source like a real frame extractor and returns the demo JPEG. */
public class FakeFrameSource : com.videokit.core.spi.FrameSource {
    override suspend fun open(source: VideoKitMediaSource): com.videokit.core.spi.FrameReader {
        val handle = try {
            source.sourceFactory.open(OpenPurpose.PROBE)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
        return object : com.videokit.core.spi.FrameReader {
            override suspend fun frameAt(
                timeUs: Long,
                maxSize: Size,
                format: com.videokit.core.spi.PixelFormat,
            ): com.videokit.core.spi.FrameData = com.videokit.core.spi.FrameData(
                maxSize.width,
                maxSize.height,
                timeUs,
                format,
                ByteArray(maxSize.width * maxSize.height * 4),
            )

            override suspend fun thumbnailAt(timeUs: Long, maxSize: Size): com.videokit.api.ThumbnailResult.Captured =
                com.videokit.testkit.DemoThumbnail.captured()

            override fun close() {
                handle.close()
            }
        }
    }
}
