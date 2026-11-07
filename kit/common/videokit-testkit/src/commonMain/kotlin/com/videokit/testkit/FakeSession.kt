package com.videokit.testkit

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionState
import com.videokit.api.HostActionStatus
import com.videokit.api.ImageDetails
import com.videokit.api.MediaInfo
import com.videokit.api.MediaKind
import com.videokit.api.MediaOrientation
import com.videokit.api.MediaTransform
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.OpenPurpose
import com.videokit.api.RecoveryDecision
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceRequest
import com.videokit.api.Seekability
import com.videokit.api.SessionPhase
import com.videokit.api.SessionVisibility
import com.videokit.api.Size
import com.videokit.api.ThumbnailResult
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSessionState
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.core.runtime.VisibilityPolicy
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.AtomicValue
import com.videokit.testkit.internal.CallbackOutcome
import com.videokit.testkit.internal.Errors
import com.videokit.testkit.internal.typeName
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.cancel
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.concurrent.Volatile

/**
 * Fake session with the complete state machine of 04 §3.1. Commands are serialized by a mutex;
 * seeks wait outside the lock so that rapid seeks supersede each other (04 §4.3).
 *
 * Playback position advances with [FakeClock]; latencies come from the bound [FakeScenario].
 */
public class FakeSession internal constructor(
    override val sessionId: String,
    config: VideoKitSessionConfig,
    private val kit: FakeVideoKit,
) : VideoKitSession {
    private val options = kit.options
    private val timeouts = options.callbackTimeouts
    private val scope = CoroutineScope(kit.scope.coroutineContext + SupervisorJob(kit.scope.coroutineContext[Job]))
    private val mutex = Mutex()
    private val mutableState = MutableStateFlow(
        VideoKitSessionState(visibility = config.initialVisibility, activeAudio = config.initialActiveAudio),
    )
    private val mutableEvents = MutableSharedFlow<VideoKitEvent>(extraBufferCapacity = 64, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val priority: ResourcePriority = config.priority

    // Guarded by mutex.
    private var source: VideoKitMediaSource? = null
    private var retrySource: VideoKitMediaSource? = null
    private var lastMediaToken: String? = null
    private var boundAtEpochMs: Long? = null
    private var currentScenario: FakeScenario = FakeScenario.normal()
    private var playbackHandle: VideoKitReadHandle? = null
    private var lease: ResourceLease? = null
    private var clockJob: Job? = null
    private var lastClockUs = 0L
    private var bufferingRemainingUs = 0L
    private var bufferingDone = false
    private var acceptedAudioEpoch = Long.MIN_VALUE
    private var seekGeneration = 0L
    private var pendingSeek: CompletableDeferred<VideoKitCommandResult>? = null
    private var watchAccumUs = 0L
    private var tickAccumUs = 0L
    private var retriesLeft = MAX_RETRIES
    private val inFlightActions = mutableSetOf<String>()

    // Visibility policy (07 §5.3, VisibilityPolicy of videokit-core): the decoder lease is released, the media stays bound.
    private var suspended = false
    private var resumeOnVisible = false
    private var visibilityJob: Job? = null

    @Volatile
    private var activeBind: Deferred<VideoKitCommandResult>? = null
    private val releaseResult = AtomicValue<CompletableDeferred<VideoKitPlaybackState>?>(null)

    private val rendering = AtomicValue<Rendering?>(null)
    private val framesRendered = AtomicCounter()

    override val state: StateFlow<VideoKitSessionState> = mutableState.asStateFlow()

    override val events: Flow<VideoKitEvent> = mutableEvents.asSharedFlow()

    override val isDemo: Boolean get() = true

    /** Number of test pattern frames drawn so far. */
    public val renderedFrames: Long get() = framesRendered.value

    /** Whether a render target is attached. */
    public val hasSurface: Boolean get() = rendering.value != null

    /** Name of the scenario of the bound (or last bound) source. */
    public val scenarioName: String get() = currentScenario.name

    private val released: Boolean get() = releaseResult.value != null

    // ---------------------------------------------------------------- bind

    override suspend fun bind(
        source: VideoKitMediaSource,
        initialState: VideoKitPlaybackState?,
        hostActions: List<VideoKitHostAction>,
    ): VideoKitCommandResult {
        if (released) return VideoKitCommandResult.SessionReleased
        val job = scope.async { mutex.withLock { bindLocked(source, initialState, hostActions) } }
        activeBind = job
        return try {
            job.await()
        } catch (cancelled: CancellationException) {
            if (released && currentCoroutineContext().isActive) return VideoKitCommandResult.SessionReleased
            withContext(NonCancellable) { job.cancelAndJoin() }
            throw cancelled
        } finally {
            if (activeBind === job) activeBind = null
        }
    }

    private suspend fun bindLocked(
        src: VideoKitMediaSource,
        initial: VideoKitPlaybackState?,
        actions: List<VideoKitHostAction>,
    ): VideoKitCommandResult {
        val phase = mutableState.value.phase
        if (phase.isReleasedOrReleasing) return VideoKitCommandResult.SessionReleased
        if (phase == SessionPhase.ERROR_FATAL) {
            return VideoKitCommandResult.Rejected(Errors.illegalState(ErrorStage.BIND, "BIND_IN_ERROR_FATAL"))
        }
        releaseSourceLocked()
        source = src
        retrySource = src
        lastMediaToken = src.mediaToken
        boundAtEpochMs = options.wallClockMs()
        currentScenario = options.scenarioResolver(src)
        bufferingDone = false
        mutableState.update {
            it.copy(
                phase = SessionPhase.BINDING,
                mediaKind = src.mediaKind,
                positionUs = 0L,
                durationUs = null,
                bufferedUs = null,
                playWhenReady = false,
                audioTracks = emptyList(),
                subtitleTracks = emptyList(),
                selectedAudioTrackId = null,
                selectedSubtitleTrackId = null,
                error = null,
                seekingToUs = null,
                videoSize = null,
                orientation = it.orientation.copy(contentOrientation = MediaOrientation.UNKNOWN),
                hostActions = actions.map { action -> HostActionState(action) },
            )
        }
        try {
            if (src.mediaKind == MediaKind.VIDEO) {
                if (currentScenario.resourceExhausted) {
                    return failLocked(Errors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "SCENARIO"))
                }
                val request =
                    ResourceRequest(
                        sessionId,
                        ResourceKind.VIDEO_DECODER,
                        ResourceEstimate(currentScenario.videoSize.width, currentScenario.videoSize.height),
                        priority,
                    )
                when (val reservation = options.resourceBudget.reserve(request)) {
                    is ReservationResult.Granted -> lease = reservation.lease

                    is ReservationResult.Denied -> {
                        return failLocked(
                            Errors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "BUDGET:${reservation.suggestion}"),
                        )
                    }
                }
            }
            withTimeout(options.sourceTimeoutMs) {
                val probe = src.sourceFactory.open(OpenPurpose.PROBE)
                try {
                    probe.readAt(0, ByteArray(PROBE_BYTES), 0, PROBE_BYTES)
                } finally {
                    probe.close()
                }
                playbackHandle = src.sourceFactory.open(OpenPurpose.PLAYBACK)
            }
            mutableState.update { it.copy(resourcesHeld = true) }
            delay(currentScenario.loadDelayMs)
            if (currentScenario.unsupportedContainer) {
                return failLocked(Errors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "SCENARIO"))
            }
            if (currentScenario.unsupportedVideoCodec && src.mediaKind == MediaKind.VIDEO) {
                return failLocked(Errors.of(ErrorCode.UNSUPPORTED_VIDEO_CODEC, ErrorStage.PROBE, "SCENARIO"))
            }
            becomeReadyLocked(src, initial)
            return VideoKitCommandResult.Executed
        } catch (timeout: TimeoutCancellationException) {
            return failLocked(Errors.fromSourceFailure(timeout, ErrorStage.BIND))
        } catch (cancelled: CancellationException) {
            withContext(NonCancellable) {
                releaseSourceLocked()
                if (!released) {
                    mutableState.update {
                        it.copy(
                            phase = SessionPhase.ERROR_RECOVERABLE,
                            error = Errors.of(ErrorCode.CANCELLED, ErrorStage.BIND, "BIND_CANCELLED"),
                        )
                    }
                }
            }
            throw cancelled
        } catch (failure: Exception) {
            return failLocked(Errors.fromSourceFailure(failure, ErrorStage.BIND))
        }
    }

    private fun becomeReadyLocked(src: VideoKitMediaSource, initial: VideoKitPlaybackState?) {
        val scenario = currentScenario
        val isVideo = src.mediaKind == MediaKind.VIDEO
        val duration = when {
            isVideo -> scenario.durationUs
            src.mediaKind == MediaKind.IMAGE_ANIMATED -> scenario.animationLoopUs
            else -> null
        }
        val audio = if (isVideo) {
            scenario.audioTracks.map {
                if (scenario.unsupportedAudioCodec) it.copy(supported = false) else it
            }
        } else {
            emptyList()
        }
        val subtitles = if (isVideo) scenario.subtitleTracks else emptyList()
        mutableState.update { current ->
            val ready = current.copy(
                phase = SessionPhase.READY,
                durationUs = duration,
                bufferedUs = if (isVideo) minOf(scenario.durationUs, BUFFER_AHEAD_US) else null,
                audioTracks = audio,
                subtitleTracks = subtitles,
                selectedAudioTrackId = audio.firstOrNull { it.supported }?.id,
                selectedSubtitleTrackId = null,
                videoSize = scenario.videoSize,
                orientation = current.orientation.copy(contentOrientation = orientationOf(scenario.videoSize)),
                looping = src.mediaKind == MediaKind.IMAGE_ANIMATED,
                mediaInfo = mediaInfoFor(src, scenario),
                imageDetails = imageDetailsFor(src.mediaKind, scenario),
                resourcesHeld = true,
                error = null,
            )
            if (initial != null) applyInitial(ready, initial, isVideo) else ready
        }
        if (isVideo && scenario.unsupportedAudioCodec) mutableEvents.tryEmit(VideoKitEvent.TransientNotice(NOTICE_AUDIO_UNSUPPORTED))
        startClockLocked()
        notifyPlayState()
    }

    private fun applyInitial(state: VideoKitSessionState, initial: VideoKitPlaybackState, isVideo: Boolean): VideoKitSessionState {
        val transform = MediaTransform(initial.zoom, initial.panX, initial.panY, initial.rotationDeg, initial.fitMode)
        var result = state.copy(
            transform = if (isValidTransform(transform)) transform else state.transform,
            orientation = state.orientation.copy(request = initial.preferredOrientation, fullscreen = initial.fullscreen),
        )
        // 04A L3: a saved looping preference overrides the default (static images never loop).
        initial.looping?.let { looping ->
            if (state.mediaKind == MediaKind.VIDEO || state.mediaKind == MediaKind.IMAGE_ANIMATED) result = result.copy(looping = looping)
        }
        if (!isVideo) return result
        val duration = state.durationUs ?: 0L
        initial.positionUs?.let { result = result.copy(positionUs = it.coerceIn(0L, duration)) }
        initial.speed?.takeIf(::isValidSpeed)?.let { result = result.copy(speed = it) }
        initial.volume?.takeIf { it in 0f..1f }?.let { result = result.copy(volume = it) }
        initial.muted?.let { result = result.copy(muted = it) }
        initial.audioTrackId?.let { id ->
            if (state.audioTracks.any { it.id == id && it.supported }) result = result.copy(selectedAudioTrackId = id)
        }
        when (initial.subtitlesEnabled) {
            false -> result = result.copy(selectedSubtitleTrackId = null)

            else -> initial.subtitleTrackId?.let { id ->
                if (state.subtitleTracks.any { it.id == id }) result = result.copy(selectedSubtitleTrackId = id)
            }
        }
        return result
    }

    private fun failLocked(error: VideoKitStableError): VideoKitCommandResult {
        releaseSourceLocked()
        val fatal = error.code in FATAL_CODES
        mutableState.update {
            it.copy(
                phase = if (fatal) SessionPhase.ERROR_FATAL else SessionPhase.ERROR_RECOVERABLE,
                error = error,
                resourcesHeld = false,
                playWhenReady = false,
                seekingToUs = null,
            )
        }
        raise(error, fatal)
        return VideoKitCommandResult.Rejected(error)
    }

    private fun raise(error: VideoKitStableError, fatal: Boolean) {
        mutableEvents.tryEmit(VideoKitEvent.ErrorRaised(error))
        notifyPlayState()
        if (fatal) {
            kit.callbacks.notify("onFatalSessionError") { onFatalSessionError(sessionId, error) }
            return
        }
        kit.scope.launch {
            val outcome = kit.callbacks.request("onRecoverableError", timeouts.recoveryDecisionMs) { onRecoverableError(sessionId, error) }
            val decision = (outcome as? CallbackOutcome.Success)?.value ?: RecoveryDecision.KEEP_ERROR
            when (decision) {
                RecoveryDecision.RETRY -> retry()
                RecoveryDecision.RELEASE -> release()
                RecoveryDecision.KEEP_ERROR -> Unit
            }
        }
    }

    private suspend fun retry() {
        val (target, actions) = mutex.withLock {
            if (released || retriesLeft <= 0 || mutableState.value.phase != SessionPhase.ERROR_RECOVERABLE) return
            retriesLeft--
            (retrySource ?: return) to mutableState.value.hostActions.map { it.action }
        }
        bind(target, null, actions)
    }

    /** Closes handles and the lease of the bound source and reports SourceReleased. */
    private fun releaseSourceLocked() {
        val src = source ?: return
        source = null
        visibilityJob?.cancel()
        visibilityJob = null
        suspended = false
        resumeOnVisible = false
        clockJob?.cancel()
        clockJob = null
        runCatching { playbackHandle?.close() }
        playbackHandle = null
        runCatching { lease?.close() }
        lease = null
        pendingSeek?.complete(VideoKitCommandResult.Superseded)
        pendingSeek = null
        mutableState.update { it.copy(resourcesHeld = false, seekingToUs = null) }
        mutableEvents.tryEmit(VideoKitEvent.SourceReleased(src.mediaToken))
        kit.callbacks.notify("onSourceReleased") { onSourceReleased(sessionId, src.mediaToken) }
        kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.SessionEnded(sessionId, src.mediaToken)) }
    }

    // ---------------------------------------------------------------- clock

    private fun startClockLocked() {
        clockJob?.cancel()
        lastClockUs = options.clock.elapsedUs.value
        clockJob = scope.launch {
            options.clock.elapsedUs.collect { now -> mutex.withLock { onClockLocked(now) } }
        }
    }

    private fun onClockLocked(nowUs: Long) {
        val delta = nowUs - lastClockUs
        lastClockUs = nowUs
        if (delta <= 0 || source == null) return
        val current = mutableState.value
        when (current.phase) {
            SessionPhase.PLAYING -> advancePlaying(current, delta)

            SessionPhase.BUFFERING -> {
                bufferingRemainingUs -= delta
                if (bufferingRemainingUs <= 0) {
                    mutableState.update { it.copy(phase = SessionPhase.PLAYING) }
                    val forUs = currentScenario.buffering?.forUs ?: 0L
                    kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.BufferingEnded(sessionId, forUs)) }
                    notifyPlayState()
                }
            }

            else -> Unit
        }
    }

    private fun advancePlaying(current: VideoKitSessionState, clockDeltaUs: Long) {
        if (current.seekingToUs != null) return
        val mediaDelta = (clockDeltaUs * current.speed).toLong()
        val from = current.positionUs
        if (current.mediaKind == MediaKind.IMAGE_ANIMATED) {
            val loop = currentScenario.animationLoopUs.coerceAtLeast(1L)
            when {
                current.looping -> mutableState.update { it.copy(positionUs = (from + mediaDelta) % loop) }

                from + mediaDelta < loop -> mutableState.update { it.copy(positionUs = from + mediaDelta) }

                // Not looping: stop on the last frame and end (04A L1).
                else -> {
                    mutableState.update { it.copy(positionUs = loop) }
                    endLocked()
                }
            }
            return
        }
        val duration = current.durationUs ?: return
        val to = from + mediaDelta
        val scenario = currentScenario
        val triggers = buildList {
            scenario.buffering?.takeIf { !bufferingDone && it.atUs > from && it.atUs <= to }?.let { add(it.atUs to Trigger.BUFFERING) }
            scenario.corruptAtUs?.takeIf { it > from && it <= to }?.let { add(it to Trigger.CORRUPT) }
            scenario.disconnectAtUs?.takeIf { it > from && it <= to }?.let { add(it to Trigger.DISCONNECT) }
            if (to >= duration) add(duration to Trigger.END)
        }
        val first = triggers.minByOrNull { it.first }
        val newPosition = first?.first ?: to
        accumulateWatchTime(current, newPosition - from)
        mutableState.update { it.copy(positionUs = newPosition, bufferedUs = minOf(duration, newPosition + BUFFER_AHEAD_US)) }
        when (first?.second) {
            Trigger.BUFFERING -> {
                bufferingDone = true
                bufferingRemainingUs = scenario.buffering?.forUs ?: 0L
                mutableState.update { it.copy(phase = SessionPhase.BUFFERING) }
                kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.BufferingStarted(sessionId, newPosition)) }
                notifyPlayState()
            }

            Trigger.CORRUPT -> failLocked(Errors.of(ErrorCode.CORRUPT_MEDIA, ErrorStage.DECODE, "SCENARIO"))

            Trigger.DISCONNECT -> failLocked(Errors.of(ErrorCode.SOURCE_DISCONNECTED, ErrorStage.PLAYBACK, "SCENARIO"))

            Trigger.END -> if (current.looping) {
                // Looping video (04A L1): restart from the beginning, never ENDED, no PlaybackEnded.
                mutableState.update { it.copy(positionUs = 0L) }
            } else {
                endLocked()
            }

            null -> Unit
        }
    }

    /** End of media without looping (04A L1): stays on the last frame, ENDED, PlaybackEnded. */
    private fun endLocked() {
        mutableState.update { it.copy(phase = SessionPhase.ENDED, playWhenReady = false) }
        mutableEvents.tryEmit(VideoKitEvent.PlaybackEnded)
        notifyPlayState()
        notifySnapshot()
    }

    /** Image facts of the Fake (04A L2): frames from the loop length, decoded ARGB bytes, no subsampling. */
    private fun imageDetailsFor(kind: MediaKind?, scenario: FakeScenario): ImageDetails? {
        if (kind == null || !kind.isImage) return null
        val frames = if (kind == MediaKind.IMAGE_ANIMATED) (scenario.animationLoopUs / ANIMATION_FRAME_US).toInt().coerceAtLeast(1) else 1
        val size = scenario.videoSize
        return ImageDetails(frameCount = frames, decodedBytes = size.width.toLong() * size.height * BYTES_PER_PIXEL, sampleSize = 1)
    }

    private fun accumulateWatchTime(current: VideoKitSessionState, advancedUs: Long) {
        if (advancedUs <= 0) return
        tickAccumUs += advancedUs
        if (tickAccumUs >= POSITION_TICK_US) {
            tickAccumUs = 0L
            val position = current.positionUs + advancedUs
            kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.PositionTick(sessionId, position)) }
        }
        if (current.visibility != SessionVisibility.VISIBLE) return
        watchAccumUs += advancedUs
        if (watchAccumUs >= WATCH_TIME_REPORT_US) {
            val delta = watchAccumUs
            watchAccumUs = 0L
            kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.WatchTimeAccumulated(sessionId, delta)) }
        }
    }

    // ---------------------------------------------------------------- commands

    override suspend fun execute(command: VideoKitCommand): VideoKitCommandResult {
        if (command == VideoKitCommand.Release) {
            if (released) return VideoKitCommandResult.SessionReleased
            release()
            return VideoKitCommandResult.Executed
        }
        if (released) return VideoKitCommandResult.SessionReleased
        if (command is VideoKitCommand.SeekTo) return seek(command)
        return mutex.withLock { executeLocked(command) }
    }

    private suspend fun executeLocked(command: VideoKitCommand): VideoKitCommandResult {
        val current = mutableState.value
        if (current.phase.isReleasedOrReleasing) return VideoKitCommandResult.SessionReleased
        if (current.phase == SessionPhase.ERROR_FATAL) {
            return rejected(ErrorStage.PLAYBACK, "${commandName(command)}_IN_ERROR_FATAL")
        }
        return when (command) {
            VideoKitCommand.Play -> play(current)

            VideoKitCommand.Pause -> pause(current)

            is VideoKitCommand.SetSpeed -> mediaCommand(current, command, videoOnly = true) {
                if (!isValidSpeed(command.speed)) return rejectedArgument("SPEED")
                mutableState.update { it.copy(speed = command.speed) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetLooping -> {
                bindRequired(current, "SET_LOOPING")?.let { return it }
                if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
                    return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
                }
                mutableState.update { it.copy(looping = command.looping) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetMuted -> preferenceCommand(current) {
                mutableState.update { it.copy(muted = command.muted) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetVolume -> preferenceCommand(current) {
                if (!command.volume.isFinite() || command.volume !in 0f..1f) return rejectedArgument("VOLUME")
                mutableState.update { it.copy(volume = command.volume) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SelectAudioTrack -> mediaCommand(current, command, videoOnly = true) {
                selectAudio(current, command.trackId)
            }

            is VideoKitCommand.SelectSubtitleTrack -> mediaCommand(current, command, videoOnly = true) {
                val id = command.trackId
                if (id != null && current.subtitleTracks.none { it.id == id }) return rejectedArgument("SUBTITLE_TRACK")
                mutableState.update { it.copy(selectedSubtitleTrackId = id) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetTransform -> {
                if (!isValidTransform(command.transform)) return rejectedArgument("TRANSFORM")
                mutableState.update { it.copy(transform = command.transform) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetOrientation -> {
                mutableState.update { it.copy(orientation = it.orientation.copy(request = command.request)) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetFullscreen -> {
                mutableState.update { it.copy(orientation = it.orientation.copy(fullscreen = command.fullscreen)) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetVisibility -> setVisibility(current, command.visibility)

            is VideoKitCommand.SetActiveAudio -> setActiveAudio(current, command)

            is VideoKitCommand.HideContentForLock -> {
                mutableState.update {
                    if (command.hidden) it.copy(hiddenForLock = true, activeAudio = false) else it.copy(hiddenForLock = false)
                }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SeekTo, VideoKitCommand.Release -> error("handled by execute")
        }
    }

    private suspend fun play(current: VideoKitSessionState): VideoKitCommandResult {
        bindRequired(current, "PLAY")?.let { return it }
        if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
            return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        }
        // A decoder released by the visibility policy is re-reserved first (one attempt, no retry loop).
        if (suspended && !resumeLocked()) {
            return VideoKitCommandResult.Rejected(Errors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.PLAYBACK, "RESUME_DENIED"))
        }
        when (current.phase) {
            SessionPhase.PLAYING, SessionPhase.BUFFERING -> mutableState.update { it.copy(playWhenReady = true) }
            SessionPhase.ENDED -> mutableState.update { it.copy(phase = SessionPhase.PLAYING, playWhenReady = true, positionUs = 0L) }
            else -> mutableState.update { it.copy(phase = SessionPhase.PLAYING, playWhenReady = true) }
        }
        notifyPlayState()
        return VideoKitCommandResult.Executed
    }

    private fun pause(current: VideoKitSessionState): VideoKitCommandResult {
        bindRequired(current, "PAUSE")?.let { return it }
        if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
            return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        }
        mutableState.update {
            if (it.phase == SessionPhase.PLAYING || it.phase == SessionPhase.BUFFERING) {
                it.copy(phase = SessionPhase.PAUSED, playWhenReady = false)
            } else {
                it.copy(playWhenReady = false)
            }
        }
        notifyPlayState()
        notifySnapshot()
        return VideoKitCommandResult.Executed
    }

    private fun selectAudio(current: VideoKitSessionState, trackId: String?): VideoKitCommandResult {
        val track = if (trackId == null) {
            current.audioTracks.firstOrNull { it.supported }
        } else {
            current.audioTracks.firstOrNull { it.id == trackId } ?: return rejectedArgument("AUDIO_TRACK")
        }
        if (track != null && !track.supported) return VideoKitCommandResult.Unsupported(UnsupportedReason.FORMAT)
        mutableState.update { it.copy(selectedAudioTrackId = track?.id) }
        return VideoKitCommandResult.Executed
    }

    /** Visibility policy of 07 §5.3, the same rules as the real session (`VisibilityPolicy` of videokit-core). */
    private suspend fun setVisibility(current: VideoKitSessionState, visibility: SessionVisibility): VideoKitCommandResult {
        if (current.visibility == visibility) return VideoKitCommandResult.Executed
        mutableState.update { it.copy(visibility = visibility) }
        kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.VisibilityChanged(sessionId, visibility)) }
        val wasForeground = current.visibility != SessionVisibility.BACKGROUND
        val isForeground = visibility != SessionVisibility.BACKGROUND
        if (wasForeground != isForeground) {
            kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.ForegroundChanged(sessionId, isForeground)) }
        }
        visibilityJob?.cancel()
        visibilityJob = null
        if (VisibilityPolicy.pauses(visibility)) {
            if (current.phase == SessionPhase.PLAYING || current.phase == SessionPhase.BUFFERING) {
                resumeOnVisible = true
                mutableState.update { it.copy(phase = SessionPhase.PAUSED, playWhenReady = false) }
                notifyPlayState()
            }
            val delayMs = VisibilityPolicy.releaseDelayMs(visibility, options.offscreenReleaseMs, options.backgroundReleaseMs)
            if (delayMs != null && source != null && !suspended) {
                visibilityJob = scope.launch {
                    delay(delayMs)
                    mutex.withLock { if (!released && VisibilityPolicy.pauses(mutableState.value.visibility)) suspendLocked() }
                }
            }
            return VideoKitCommandResult.Executed
        }
        val resumed = resumeLocked()
        if (resumeOnVisible && resumed) {
            resumeOnVisible = false
            return play(mutableState.value)
        }
        resumeOnVisible = false
        return VideoKitCommandResult.Executed
    }

    /** Releases the decoder lease of a bound, paused session; the media stays bound. */
    private fun suspendLocked() {
        if (source == null || suspended || mutableState.value.phase !in SUSPENDABLE_PHASES) return
        // Like a real engine: the decoder and its read handle are closed; the media stays bound.
        runCatching { playbackHandle?.close() }
        playbackHandle = null
        runCatching { lease?.close() }
        lease = null
        suspended = true
        mutableState.update { it.copy(resourcesHeld = false) }
    }

    /** Re-reserves the decoder of a suspended session; `false` with a recoverable error event when denied. */
    private suspend fun resumeLocked(): Boolean {
        if (!suspended) return true
        val src = source ?: return false
        if (src.mediaKind == MediaKind.VIDEO) {
            val size = currentScenario.videoSize
            val request = ResourceRequest(sessionId, ResourceKind.VIDEO_DECODER, ResourceEstimate(size.width, size.height), priority)
            when (val reservation = options.resourceBudget.reserve(request)) {
                is ReservationResult.Granted -> lease = reservation.lease

                is ReservationResult.Denied -> {
                    val error = Errors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "BUDGET:${reservation.suggestion}")
                    mutableEvents.tryEmit(VideoKitEvent.ErrorRaised(error))
                    mutableEvents.tryEmit(VideoKitEvent.TransientNotice(com.videokit.api.NoticeCodes.RESOURCE_DEGRADED))
                    return false
                }
            }
        }
        try {
            playbackHandle = src.sourceFactory.open(OpenPurpose.PLAYBACK)
        } catch (cancelled: CancellationException) {
            runCatching { lease?.close() }
            lease = null
            throw cancelled
        } catch (failure: Exception) {
            runCatching { lease?.close() }
            lease = null
            mutableEvents.tryEmit(VideoKitEvent.ErrorRaised(Errors.fromSourceFailure(failure, ErrorStage.BIND)))
            return false
        }
        suspended = false
        mutableState.update { it.copy(resourcesHeld = true) }
        return true
    }

    private fun setActiveAudio(current: VideoKitSessionState, command: VideoKitCommand.SetActiveAudio): VideoKitCommandResult {
        if (command.audioEpoch < acceptedAudioEpoch) return rejected(ErrorStage.PLAYBACK, "STALE_AUDIO_EPOCH")
        if (command.active && current.hiddenForLock) return rejected(ErrorStage.PLAYBACK, "LOCKED")
        acceptedAudioEpoch = command.audioEpoch
        mutableState.update { it.copy(activeAudio = command.active) }
        return VideoKitCommandResult.Executed
    }

    private inline fun mediaCommand(
        current: VideoKitSessionState,
        command: VideoKitCommand,
        videoOnly: Boolean,
        block: () -> VideoKitCommandResult,
    ): VideoKitCommandResult {
        bindRequired(current, commandName(command))?.let { return it }
        if (videoOnly && current.mediaKind?.isImage == true) return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        return block()
    }

    private inline fun preferenceCommand(current: VideoKitSessionState, block: () -> VideoKitCommandResult): VideoKitCommandResult {
        if (current.mediaKind?.isImage == true) return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        return block()
    }

    private fun bindRequired(current: VideoKitSessionState, name: String): VideoKitCommandResult? = when (current.phase) {
        SessionPhase.READY, SessionPhase.PLAYING, SessionPhase.PAUSED, SessionPhase.BUFFERING, SessionPhase.ENDED -> null
        else -> rejected(ErrorStage.PLAYBACK, "${name}_IN_${current.phase}")
    }

    private suspend fun seek(command: VideoKitCommand.SeekTo): VideoKitCommandResult {
        val outcome = CompletableDeferred<VideoKitCommandResult>()
        val generation: Long
        val delayMs: Long
        mutex.withLock {
            val current = mutableState.value
            if (current.phase.isReleasedOrReleasing) return VideoKitCommandResult.SessionReleased
            if (current.phase == SessionPhase.ERROR_FATAL) return rejected(ErrorStage.PLAYBACK, "SEEK_IN_ERROR_FATAL")
            bindRequired(current, "SEEK")?.let { return it }
            if (current.mediaKind?.isImage == true) return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
            if (source?.seekability ==
                Seekability.SEQUENTIAL_ONLY
            ) {
                return VideoKitCommandResult.Unsupported(UnsupportedReason.SOURCE_SEQUENTIAL_ONLY)
            }
            if (command.positionUs < 0) return rejectedArgument("POSITION")
            val target = command.positionUs.coerceAtMost(current.durationUs ?: command.positionUs)
            pendingSeek?.complete(VideoKitCommandResult.Superseded)
            pendingSeek = outcome
            generation = ++seekGeneration
            delayMs = currentScenario.seekDelayMs
            mutableState.update { it.copy(seekingToUs = target) }
        }
        val early = withTimeoutOrNull(delayMs) { outcome.await() }
        if (early != null) return early
        mutex.withLock {
            if (generation == seekGeneration && !outcome.isCompleted) {
                val current = mutableState.value
                val target = current.seekingToUs ?: current.positionUs
                val from = current.positionUs
                mutableState.update {
                    val endedPhase = if (it.phase == SessionPhase.ENDED && target < (it.durationUs ?: 0L)) SessionPhase.PAUSED else it.phase
                    it.copy(positionUs = target, seekingToUs = null, phase = endedPhase)
                }
                pendingSeek = null
                kit.callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.UserSeek(sessionId, from, target)) }
                outcome.complete(VideoKitCommandResult.Executed)
            }
        }
        return outcome.await()
    }

    // ---------------------------------------------------------------- host actions, navigation, controls

    override suspend fun updateHostActions(actions: List<VideoKitHostAction>) {
        mutex.withLock {
            if (released) return
            mutableState.update { current ->
                val previous = current.hostActions.associateBy { it.action.actionId }
                current.copy(
                    hostActions = actions.map { action ->
                        val old = previous[action.actionId]
                        HostActionState(
                            action = action,
                            pending = action.pending || action.actionId in inFlightActions,
                            lastStatus = old?.lastStatus,
                            lastError = old?.lastError,
                        )
                    },
                )
            }
        }
    }

    override suspend fun requestHostAction(actionId: String): VideoKitCommandResult {
        val request: HostActionRequest
        val simulateTimeout: Boolean
        mutex.withLock {
            val current = mutableState.value
            if (current.phase.isReleasedOrReleasing) return VideoKitCommandResult.SessionReleased
            val token = source?.mediaToken ?: return rejected(ErrorStage.CALLBACK, "HOST_ACTION_WITHOUT_MEDIA")
            val entry = current.hostActions.firstOrNull { it.action.actionId == actionId } ?: return rejectedArgument("HOST_ACTION_ID")
            if (!entry.action.enabled) return rejected(ErrorStage.CALLBACK, "HOST_ACTION_DISABLED")
            if (entry.pending || actionId in inFlightActions) return VideoKitCommandResult.Superseded
            inFlightActions += actionId
            updateAction(actionId) { it.copy(pending = true, lastError = null) }
            request = HostActionRequest(actionId, sessionId, token)
            simulateTimeout = actionId in currentScenario.hostActionTimeoutIds
        }
        var outcome: CallbackOutcome<com.videokit.api.HostActionResult>? = null
        try {
            outcome = if (simulateTimeout) {
                delay(timeouts.hostActionMs)
                CallbackOutcome.Failure(Errors.callbackFailed("onHostActionRequested", null, timedOut = true))
            } else {
                kit.callbacks.request("onHostActionRequested", timeouts.hostActionMs) { onHostActionRequested(request) }
            }
        } finally {
            withContext(NonCancellable) {
                mutex.withLock {
                    inFlightActions -= actionId
                    if (outcome == null) updateAction(actionId) { it.copy(pending = false) }
                }
            }
        }
        return mutex.withLock {
            if (released) return@withLock VideoKitCommandResult.SessionReleased
            when (val result = outcome) {
                is CallbackOutcome.Success -> {
                    val answer = result.value
                    val stillPending = answer.status == HostActionStatus.PENDING
                    updateAction(actionId) {
                        val action = (answer.updatedAction ?: it.action).copy(pending = stillPending)
                        HostActionState(action, pending = stillPending, lastStatus = answer.status, lastError = null)
                    }
                    answer.messageKey?.let { mutableEvents.tryEmit(VideoKitEvent.TransientNotice(it)) }
                    VideoKitCommandResult.Executed
                }

                is CallbackOutcome.Failure -> {
                    updateAction(actionId) { it.copy(pending = false, lastStatus = HostActionStatus.FAILED, lastError = result.error) }
                    mutableEvents.tryEmit(VideoKitEvent.HostActionFailed(actionId, result.error))
                    VideoKitCommandResult.Rejected(result.error)
                }
            }
        }
    }

    private fun updateAction(actionId: String, transform: (HostActionState) -> HostActionState) {
        mutableState.update { current ->
            current.copy(hostActions = current.hostActions.map { if (it.action.actionId == actionId) transform(it) else it })
        }
    }

    override suspend fun requestNavigation(direction: NavigationDirection): NavigationResult {
        if (released) return NavigationResult.UNAVAILABLE
        val token = mutex.withLock { source?.mediaToken ?: lastMediaToken }
        val request = NavigationRequest(sessionId, token, direction)
        val outcome = kit.callbacks.request("onNavigationRequested", timeouts.navigationMs) { onNavigationRequested(request) }
        return (outcome as? CallbackOutcome.Success)?.value ?: NavigationResult.FAILED
    }

    override fun setControlsVisible(visible: Boolean) {
        if (released) return
        var changed = false
        mutableState.update { current ->
            changed = current.controlsVisible != visible
            current.copy(controlsVisible = visible)
        }
        if (changed) kit.callbacks.notify("onControlsVisibilityChanged") { onControlsVisibilityChanged(sessionId, visible) }
    }

    // ---------------------------------------------------------------- media info & thumbnails

    /** Demo media parameters of [src] (04A P2): what a real engine reads from the container and the tracks. */
    private fun mediaInfoFor(src: VideoKitMediaSource, scenario: FakeScenario): MediaInfo {
        val size = scenario.videoSize
        return if (src.mediaKind == MediaKind.VIDEO) {
            MediaInfo(
                container = src.extension ?: "mp4",
                videoCodec = "video/avc",
                audioCodec = scenario.audioTracks.firstOrNull()?.codec,
                width = size.width,
                height = size.height,
                frameRate = DEMO_FRAME_RATE,
                bitrateBps = DEMO_BITRATE_BPS,
                rotationDeg = 0,
                durationUs = scenario.durationUs,
                fileSizeBytes = playbackHandle?.length ?: src.knownLength,
            )
        } else {
            MediaInfo(
                container = src.extension,
                width = size.width,
                height = size.height,
                fileSizeBytes =
                playbackHandle?.length ?: src.knownLength,
            )
        }
    }

    /** 04A P1: the [FakeVideoKitOptions.thumbnailFactory] picture (the demo JPEG unless the platform installs one). */
    override suspend fun captureThumbnail(atUs: Long, maxWidth: Int, maxHeight: Int): ThumbnailResult {
        if (released) return ThumbnailResult.Failed(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.PLAYBACK, "THUMBNAIL_RELEASED"))
        if (atUs < 0 || maxWidth <= 0 ||
            maxHeight <= 0
        ) {
            return ThumbnailResult.Failed(Errors.invalidArgument(ErrorStage.PLAYBACK, "THUMBNAIL"))
        }
        val bound = mutex.withLock { source != null }
        if (!bound) return ThumbnailResult.Failed(Errors.illegalState(ErrorStage.PLAYBACK, "THUMBNAIL_WITHOUT_MEDIA"))
        return options.thumbnailFactory(sessionId, atUs, maxWidth, maxHeight)
    }

    // ---------------------------------------------------------------- snapshot & release

    override suspend fun captureState(): VideoKitPlaybackState {
        releaseResult.value?.let { return it.await() }
        return mutex.withLock { snapshotOf(mutableState.value) }
    }

    private fun snapshotOf(current: VideoKitSessionState): VideoKitPlaybackState {
        val isVideo = current.mediaKind == MediaKind.VIDEO
        return VideoKitPlaybackState(
            sessionId = sessionId,
            mediaToken = source?.mediaToken ?: lastMediaToken,
            zoom = current.transform.scale,
            panX = current.transform.panX,
            panY = current.transform.panY,
            rotationDeg = current.transform.rotationDeg,
            fitMode = current.transform.fitMode,
            preferredOrientation = current.orientation.request,
            fullscreen = current.orientation.fullscreen,
            positionUs = if (isVideo) current.seekingToUs ?: current.positionUs else null,
            speed = if (isVideo) current.speed else null,
            volume = if (isVideo) current.volume else null,
            muted = if (isVideo) current.muted else null,
            subtitleTrackId = if (isVideo) current.selectedSubtitleTrackId else null,
            subtitlesEnabled = if (isVideo) current.selectedSubtitleTrackId != null else null,
            audioTrackId = if (isVideo) current.selectedAudioTrackId else null,
            lastViewedAtEpochMs = boundAtEpochMs,
            looping = if (current.mediaKind == MediaKind.VIDEO || current.mediaKind == MediaKind.IMAGE_ANIMATED) current.looping else null,
        )
    }

    override suspend fun release(): VideoKitPlaybackState {
        val mine = CompletableDeferred<VideoKitPlaybackState>()
        if (!releaseResult.compareAndSet(null, mine)) return releaseResult.value!!.await()
        activeBind?.cancel()
        val snapshot = withContext(NonCancellable) {
            activeBind?.join()
            mutex.withLock {
                mutableState.update { it.copy(phase = SessionPhase.RELEASING) }
                val snap = snapshotOf(mutableState.value)
                stopRendering()
                releaseSourceLocked()
                clockJob?.cancel()
                pendingSeek?.complete(VideoKitCommandResult.SessionReleased)
                pendingSeek = null
                mutableState.update {
                    it.copy(phase = SessionPhase.RELEASED, resourcesHeld = false, playWhenReady = false, seekingToUs = null)
                }
                snap
            }
        }
        kit.callbacks.notify("onPlaybackSnapshot") { onPlaybackSnapshot(snapshot) }
        notifyPlayState()
        kit.onSessionReleased(sessionId)
        mine.complete(snapshot)
        scope.cancel()
        return snapshot
    }

    override fun close() {
        if (released) return
        kit.scope.launch { release() }
    }

    // ---------------------------------------------------------------- rendering

    /**
     * Attaches [target] (04A I13). Target types the platform pattern factory does not support are refused with
     * `Unsupported(DEVICE_CAPABILITY)`; the previous target stays attached.
     */
    override fun attachSurface(target: VideoKitSurfaceTarget): VideoKitCommandResult {
        if (released) return VideoKitCommandResult.SessionReleased
        val drawing = options.patternTargetFactory(target)
            ?: return VideoKitCommandResult.Unsupported(UnsupportedReason.DEVICE_CAPABILITY)
        val job = scope.launch {
            while (isActive) {
                val current = mutableState.value
                if (!current.hiddenForLock) {
                    val frame = TestPattern.frame(sessionId, current.seekingToUs ?: current.positionUs, target.width, target.height)
                    if (drawing.draw(frame)) framesRendered.incrementAndGet()
                }
                delay(options.renderIntervalMs)
            }
        }
        rendering.getAndSet(Rendering(job, drawing))?.stop()
        return VideoKitCommandResult.Executed
    }

    override fun detachSurface() {
        stopRendering()
    }

    private fun stopRendering() {
        rendering.getAndSet(null)?.stop()
    }

    private class Rendering(val job: Job?, val target: TestPatternTarget?) {
        fun stop() {
            job?.cancel()
            target?.release()
        }
    }

    // ---------------------------------------------------------------- edit preview

    internal suspend fun updatePreviewDuration(durationUs: Long) {
        mutex.withLock {
            if (source == null) return
            mutableState.update { it.copy(durationUs = durationUs, positionUs = it.positionUs.coerceAtMost(durationUs)) }
        }
    }

    // ---------------------------------------------------------------- helpers

    private fun notifyPlayState() {
        val current = mutableState.value
        kit.callbacks.notify("onPlaybackEvent") {
            onPlaybackEvent(VideoKitPlaybackEvent.PlayStateChanged(sessionId, current.phase, current.playWhenReady))
        }
    }

    private fun notifySnapshot() {
        val snapshot = snapshotOf(mutableState.value)
        kit.callbacks.notify("onPlaybackSnapshot") { onPlaybackSnapshot(snapshot) }
    }

    private fun rejected(stage: ErrorStage, what: String): VideoKitCommandResult =
        VideoKitCommandResult.Rejected(Errors.illegalState(stage, what))

    private fun rejectedArgument(what: String): VideoKitCommandResult =
        VideoKitCommandResult.Rejected(Errors.invalidArgument(ErrorStage.PLAYBACK, what))

    private enum class Trigger { BUFFERING, CORRUPT, DISCONNECT, END }

    private companion object {
        const val PROBE_BYTES = 64
        const val MAX_RETRIES = 1

        /** Phases in which the visibility policy may release the decoder. */
        val SUSPENDABLE_PHASES = setOf(SessionPhase.READY, SessionPhase.PAUSED, SessionPhase.ENDED)
        const val BUFFER_AHEAD_US = 10_000_000L
        const val ANIMATION_FRAME_US = 100_000L
        const val DEMO_FRAME_RATE = 30f
        const val DEMO_BITRATE_BPS = 8_000_000L
        const val BYTES_PER_PIXEL = 4L
        const val POSITION_TICK_US = 250_000L
        const val WATCH_TIME_REPORT_US = 1_000_000L
        const val NOTICE_AUDIO_UNSUPPORTED = com.videokit.api.NoticeCodes.AUDIO_UNSUPPORTED_PLAYING_SILENT
        val FATAL_CODES = setOf(ErrorCode.CORRUPT_MEDIA)
        val VALID_ROTATIONS = setOf(0, 90, 180, 270)

        fun isValidSpeed(speed: Float): Boolean = speed.isFinite() && speed in 0.25f..4f

        fun isValidTransform(transform: MediaTransform): Boolean = transform.scale.isFinite() &&
            transform.scale > 0f &&
            transform.scale <= 10f &&
            transform.panX.isFinite() &&
            transform.panY.isFinite() &&
            transform.rotationDeg in VALID_ROTATIONS

        fun orientationOf(size: Size): MediaOrientation = when {
            size.width <= 0 || size.height <= 0 -> MediaOrientation.UNKNOWN
            size.width > size.height -> MediaOrientation.LANDSCAPE
            size.width < size.height -> MediaOrientation.PORTRAIT
            else -> MediaOrientation.SQUARE
        }

        fun commandName(command: VideoKitCommand): String = command.typeName().uppercase()
    }
}
