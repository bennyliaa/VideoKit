package com.videokit.playback

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionState
import com.videokit.api.HostActionStatus
import com.videokit.api.MediaInfo
import com.videokit.api.MediaKind
import com.videokit.api.MediaOrientation
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.RecoveryDecision
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourceRequest
import com.videokit.api.SeekMode
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
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionState
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.core.SessionContext
import com.videokit.core.runtime.AtomicValue
import com.videokit.core.runtime.CallbackOutcome
import com.videokit.core.runtime.StableErrors
import com.videokit.core.runtime.typeName
import com.videokit.core.spi.EngineState
import com.videokit.core.spi.EngineStatus
import com.videokit.core.spi.PlaybackHandle
import com.videokit.core.spi.PlaybackOpenOptions
import com.videokit.core.spi.SpiException
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
import kotlin.concurrent.Volatile

/**
 * The real video session (06 §2): state machine of 04 §3.1 over a platform [com.videokit.core.spi.PlaybackEngine].
 *
 * - Commands are serialized by a mutex (02 §5 serial executor); seeks wait outside the lock so that a newer seek
 *   supersedes an older one (04 §4.3).
 * - The engine state drives position, buffering, end of media and playback failures; the session adds the rules
 *   (validation, audio and lock policy, host callbacks, events, statistics, snapshots).
 * - Release order of 06 §7: stop, cancel reads, release the engine (decoders, surface, read handles), then
 *   SourceReleased, then the resource lease, then RELEASED.
 *
 * Images arrive in VK-M2: binding an image source answers `Unsupported(NOT_IMPLEMENTED)` until an image engine is
 * assembled.
 */
public class PlaybackSession internal constructor(context: SessionContext) : VideoKitSession {
    override val sessionId: String = context.sessionId
    private val runtime = context.runtime
    private val engines = runtime.engines
    private val callbacks = runtime.callbacks
    private val timeouts = callbacks.timeouts
    private val scope = CoroutineScope(runtime.scope.coroutineContext + SupervisorJob(runtime.scope.coroutineContext[Job]))
    private val mutex = Mutex()
    private val priority = context.config.priority
    private val mutableState = MutableStateFlow(
        VideoKitSessionState(visibility = context.config.initialVisibility, activeAudio = context.config.initialActiveAudio),
    )
    private val mutableEvents = MutableSharedFlow<VideoKitEvent>(extraBufferCapacity = 64, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val statistics = PlaybackStatistics()

    // Guarded by mutex.
    private var source: VideoKitMediaSource? = null
    private var retrySource: VideoKitMediaSource? = null
    private var lastMediaToken: String? = null
    private var boundAtEpochMs: Long? = null
    private var handle: PlaybackHandle? = null
    private var lease: ResourceLease? = null
    private var engineJob: Job? = null
    private var bufferingSinceUs: Long? = null
    private var acceptedAudioEpoch = Long.MIN_VALUE
    private var seekGeneration = 0L
    private var pendingSeek: CompletableDeferred<VideoKitCommandResult>? = null
    private var retriesLeft = MAX_RETRIES
    private val inFlightActions = mutableSetOf<String>()

    @Volatile
    private var target: VideoKitSurfaceTarget? = null

    @Volatile
    private var activeBind: Deferred<VideoKitCommandResult>? = null
    private val releaseResult = AtomicValue<CompletableDeferred<VideoKitPlaybackState>?>(null)

    override val state: StateFlow<VideoKitSessionState> = mutableState.asStateFlow()

    override val events: Flow<VideoKitEvent> = mutableEvents.asSharedFlow()

    override val isDemo: Boolean get() = runtime.options.isDemo

    private val released: Boolean get() = releaseResult.value != null

    // ---------------------------------------------------------------- bind

    override suspend fun bind(
        source: VideoKitMediaSource,
        initialState: VideoKitPlaybackState?,
        hostActions: List<VideoKitHostAction>,
    ): VideoKitCommandResult {
        if (released) return VideoKitCommandResult.SessionReleased
        if (source.mediaKind.isImage && engines.images == null) return VideoKitCommandResult.Unsupported(UnsupportedReason.NOT_IMPLEMENTED)
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
            return VideoKitCommandResult.Rejected(StableErrors.illegalState(ErrorStage.BIND, "BIND_IN_ERROR_FATAL"))
        }
        releaseSourceLocked()
        source = src
        retrySource = src
        lastMediaToken = src.mediaToken
        boundAtEpochMs = engines.clock.epochMs()
        statistics.reset()
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
                looping = false,
                imageDetails = null,
                orientation = it.orientation.copy(contentOrientation = MediaOrientation.UNKNOWN),
                hostActions = actions.map { action -> HostActionState(action) },
            )
        }
        try {
            val request = ResourceRequest(sessionId, ResourceKind.VIDEO_DECODER, ResourceEstimate(), priority)
            when (val reservation = runtime.budget.reserve(request)) {
                is ReservationResult.Granted -> lease = reservation.lease

                is ReservationResult.Denied -> return failLocked(
                    StableErrors.of(ErrorCode.DECODER_RESOURCE_EXHAUSTED, ErrorStage.BIND, "BUDGET:${reservation.suggestion}"),
                )
            }
            val current = mutableState.value
            val opened = withTimeout(runtime.options.sourceTimeoutMs) {
                engines.playback.open(
                    src,
                    PlaybackOpenOptions(
                        audioEnabled = PlaybackRules.audioEnabled(current),
                        handleAudioFocus = PlaybackRules.audioEnabled(current),
                        startPositionUs = initial?.positionUs?.coerceAtLeast(0L) ?: 0L,
                    ),
                )
            }
            handle = opened
            mutableState.update { it.copy(resourcesHeld = true) }
            becomeReadyLocked(opened, initial)
            return VideoKitCommandResult.Executed
        } catch (timeout: TimeoutCancellationException) {
            return failLocked(StableErrors.fromSourceFailure(timeout, ErrorStage.BIND))
        } catch (cancelled: CancellationException) {
            withContext(NonCancellable) {
                releaseSourceLocked()
                if (!released) {
                    mutableState.update {
                        it.copy(
                            phase = SessionPhase.ERROR_RECOVERABLE,
                            error = StableErrors.of(ErrorCode.CANCELLED, ErrorStage.BIND, "BIND_CANCELLED"),
                        )
                    }
                }
            }
            throw cancelled
        } catch (failure: SpiException) {
            return failLocked(failure.error)
        } catch (failure: Exception) {
            return failLocked(StableErrors.fromSourceFailure(failure, ErrorStage.BIND))
        }
    }

    private suspend fun becomeReadyLocked(opened: PlaybackHandle, initial: VideoKitPlaybackState?) {
        val engine = opened.state.value
        mutableState.update { current ->
            val ready = current.copy(
                phase = SessionPhase.READY,
                positionUs = engine.positionUs,
                durationUs = engine.durationUs,
                bufferedUs = engine.bufferedUs,
                audioTracks = engine.audioTracks,
                subtitleTracks = engine.subtitleTracks,
                selectedAudioTrackId = engine.selectedAudioTrackId ?: engine.audioTracks.firstOrNull { it.supported }?.id,
                selectedSubtitleTrackId = null,
                videoSize = engine.videoSize,
                orientation = current.orientation.copy(contentOrientation = PlaybackRules.orientationOf(engine.videoSize)),
                looping = PlaybackRules.defaultLooping(current.mediaKind),
                mediaInfo = withSourceSize(engine.mediaInfo),
                resourcesHeld = true,
                error = null,
            )
            if (initial != null) PlaybackRules.applyInitial(ready, initial) else ready
        }
        // Push the (possibly restored) settings to the engine.
        val state = mutableState.value
        if (state.speed != 1f) opened.setSpeed(state.speed)
        if (state.looping) opened.setLooping(true)
        opened.setVolume(PlaybackRules.outputVolume(state))
        if (state.selectedAudioTrackId != engine.selectedAudioTrackId) opened.selectAudioTrack(state.selectedAudioTrackId)
        opened.selectSubtitleTrack(state.selectedSubtitleTrackId)
        if (state.positionUs != engine.positionUs) opened.seekTo(state.positionUs, SeekMode.EXACT)
        if (engine.audioTracks.isNotEmpty() && engine.audioTracks.none { it.supported }) {
            // Video plays silently with a hint (15 §2.2: unsupported audio codec).
            mutableEvents.tryEmit(VideoKitEvent.TransientNotice(NOTICE_AUDIO_UNSUPPORTED))
        }
        target?.let { if (!state.hiddenForLock) opened.attach(it) }
        engineJob = scope.launch { opened.state.collect { engineState -> mutex.withLock { onEngineStateLocked(opened, engineState) } } }
        notifyPlayState()
    }

    private suspend fun failLocked(error: VideoKitStableError): VideoKitCommandResult {
        releaseSourceLocked()
        val fatal = error.code in PlaybackRules.FATAL_CODES
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
            callbacks.notify("onFatalSessionError") { onFatalSessionError(sessionId, error) }
            return
        }
        runtime.scope.launch {
            val outcome = callbacks.request("onRecoverableError", timeouts.recoveryDecisionMs) { onRecoverableError(sessionId, error) }
            when ((outcome as? CallbackOutcome.Success)?.value ?: RecoveryDecision.KEEP_ERROR) {
                RecoveryDecision.RETRY -> retry()
                RecoveryDecision.RELEASE -> release()
                RecoveryDecision.KEEP_ERROR -> Unit
            }
        }
    }

    private suspend fun retry() {
        val (retryTarget, actions) = mutex.withLock {
            if (released || retriesLeft <= 0 || mutableState.value.phase != SessionPhase.ERROR_RECOVERABLE) return
            retriesLeft--
            (retrySource ?: return) to mutableState.value.hostActions.map { it.action }
        }
        bind(retryTarget, null, actions)
    }

    /** Releases the engine (decoders, surface, read handles), then reports SourceReleased, then the lease (06 §7). */
    private suspend fun releaseSourceLocked() {
        val src = source ?: return
        source = null
        engineJob?.cancel()
        engineJob = null
        val opened = handle
        handle = null
        if (opened != null) withContext(NonCancellable + engines.scheduler.io) { runCatching { opened.close() } }
        pendingSeek?.complete(VideoKitCommandResult.Superseded)
        pendingSeek = null
        bufferingSinceUs = null
        mutableState.update { it.copy(resourcesHeld = false, seekingToUs = null) }
        mutableEvents.tryEmit(VideoKitEvent.SourceReleased(src.mediaToken))
        callbacks.notify("onSourceReleased") { onSourceReleased(sessionId, src.mediaToken) }
        callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.SessionEnded(sessionId, src.mediaToken)) }
        runCatching { lease?.close() }
        lease = null
    }

    // ---------------------------------------------------------------- engine state

    private suspend fun onEngineStateLocked(opened: PlaybackHandle, engine: EngineState) {
        if (handle !== opened) return
        val current = mutableState.value
        if (current.phase.isReleasedOrReleasing || current.phase == SessionPhase.ERROR_FATAL) return
        if (engine.status == EngineStatus.FAILED) {
            failLocked(engine.error ?: StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.PLAYBACK, "ENGINE_FAILED"))
            return
        }
        val advanced = engine.positionUs - current.positionUs
        mutableState.update {
            it.copy(
                positionUs = if (it.seekingToUs == null) engine.positionUs else it.positionUs,
                durationUs = engine.durationUs ?: it.durationUs,
                bufferedUs = engine.bufferedUs,
                audioTracks = engine.audioTracks,
                subtitleTracks = engine.subtitleTracks,
                videoSize = engine.videoSize ?: it.videoSize,
                mediaInfo = engine.mediaInfo?.let(::withSourceSize) ?: it.mediaInfo,
                orientation = it.orientation.copy(contentOrientation = PlaybackRules.orientationOf(engine.videoSize ?: it.videoSize)),
            )
        }
        if (current.phase == SessionPhase.PLAYING && current.seekingToUs == null) {
            // Wrap-around of a looping playback is not watch time.
            if (advanced > 0) report(statistics.onPlayed(engine.positionUs, advanced, current.visibility == SessionVisibility.VISIBLE))
        }
        when (engine.status) {
            EngineStatus.BUFFERING -> if (current.phase == SessionPhase.PLAYING) {
                bufferingSinceUs = engines.clock.monotonicUs()
                mutableState.update { it.copy(phase = SessionPhase.BUFFERING) }
                callbacks.notify("onPlaybackEvent") {
                    onPlaybackEvent(VideoKitPlaybackEvent.BufferingStarted(sessionId, engine.positionUs))
                }
                notifyPlayState()
            }

            EngineStatus.READY -> if (current.phase == SessionPhase.BUFFERING) {
                val forUs = bufferingSinceUs?.let { engines.clock.monotonicUs() - it } ?: 0L
                bufferingSinceUs = null
                mutableState.update { it.copy(phase = if (it.playWhenReady) SessionPhase.PLAYING else SessionPhase.PAUSED) }
                callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.BufferingEnded(sessionId, forUs)) }
                notifyPlayState()
            }

            EngineStatus.ENDED -> if (current.phase == SessionPhase.PLAYING || current.phase == SessionPhase.BUFFERING) {
                // Not looping (04A L1): stays on the last frame.
                mutableState.update {
                    it.copy(
                        phase = SessionPhase.ENDED,
                        playWhenReady = false,
                        positionUs =
                        it.durationUs ?: engine.positionUs,
                    )
                }
                mutableEvents.tryEmit(VideoKitEvent.PlaybackEnded)
                notifyPlayState()
                notifySnapshot()
            }

            else -> Unit
        }
    }

    private fun report(step: PlaybackStatistics.Step) {
        step.tickAtUs?.let { position ->
            callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.PositionTick(sessionId, position)) }
        }
        step.watchTimeUs?.let { delta ->
            callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.WatchTimeAccumulated(sessionId, delta)) }
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
        if (current.phase == SessionPhase.ERROR_FATAL) return rejected(ErrorStage.PLAYBACK, "${commandName(command)}_IN_ERROR_FATAL")
        return when (command) {
            VideoKitCommand.Play -> play(current)

            VideoKitCommand.Pause -> pause(current)

            is VideoKitCommand.SetSpeed -> mediaCommand(current, command) {
                if (!PlaybackRules.isValidSpeed(command.speed)) return rejectedArgument("SPEED")
                handle?.setSpeed(command.speed)
                mutableState.update { it.copy(speed = command.speed) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetLooping -> {
                bindRequired(current, "SET_LOOPING")?.let { return it }
                if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
                    return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
                }
                handle?.setLooping(command.looping)
                mutableState.update { it.copy(looping = command.looping) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetMuted -> preferenceCommand(current) {
                mutableState.update { it.copy(muted = command.muted) }
                pushAudio()
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetVolume -> preferenceCommand(current) {
                if (!PlaybackRules.isValidVolume(command.volume)) return rejectedArgument("VOLUME")
                mutableState.update { it.copy(volume = command.volume) }
                pushAudio()
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SelectAudioTrack -> mediaCommand(current, command) { selectAudio(current, command.trackId) }

            is VideoKitCommand.SelectSubtitleTrack -> mediaCommand(current, command) {
                val id = command.trackId
                if (id != null && current.subtitleTracks.none { it.id == id }) return rejectedArgument("SUBTITLE_TRACK")
                handle?.selectSubtitleTrack(id)
                mutableState.update { it.copy(selectedSubtitleTrackId = id) }
                VideoKitCommandResult.Executed
            }

            is VideoKitCommand.SetTransform -> {
                // Zoom, pan and rotation are applied by the UI on the texture (15 §2.6); the session keeps them.
                if (!PlaybackRules.isValidTransform(command.transform)) return rejectedArgument("TRANSFORM")
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

            is VideoKitCommand.HideContentForLock -> hideForLock(command.hidden)

            is VideoKitCommand.SeekTo, VideoKitCommand.Release -> error("handled by execute")
        }
    }

    private suspend fun play(current: VideoKitSessionState): VideoKitCommandResult {
        bindRequired(current, "PLAY")?.let { return it }
        if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
            return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        }
        val opened = handle
        when (current.phase) {
            SessionPhase.PLAYING, SessionPhase.BUFFERING -> mutableState.update { it.copy(playWhenReady = true) }

            SessionPhase.ENDED -> {
                // Replay from the start (06 §4).
                opened?.seekTo(0L, SeekMode.EXACT)
                mutableState.update { it.copy(phase = SessionPhase.PLAYING, playWhenReady = true, positionUs = 0L) }
            }

            else -> mutableState.update { it.copy(phase = SessionPhase.PLAYING, playWhenReady = true) }
        }
        opened?.play()
        notifyPlayState()
        return VideoKitCommandResult.Executed
    }

    private suspend fun pause(current: VideoKitSessionState): VideoKitCommandResult {
        bindRequired(current, "PAUSE")?.let { return it }
        if (current.mediaKind == MediaKind.IMAGE_STATIC || current.mediaKind == MediaKind.IMAGE_UNKNOWN) {
            return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
        }
        handle?.pause()
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

    private suspend fun selectAudio(current: VideoKitSessionState, trackId: String?): VideoKitCommandResult {
        val track = PlaybackRules.resolveAudioTrack(current.audioTracks, trackId)
        if (trackId != null && track == null) return rejectedArgument("AUDIO_TRACK")
        if (track != null && !track.supported) return VideoKitCommandResult.Unsupported(UnsupportedReason.FORMAT)
        handle?.selectAudioTrack(track?.id)
        mutableState.update { it.copy(selectedAudioTrackId = track?.id) }
        return VideoKitCommandResult.Executed
    }

    private fun setVisibility(current: VideoKitSessionState, visibility: SessionVisibility): VideoKitCommandResult {
        // M1: visibility is reported and counted (watch time); decoder release for off-screen slots is VK-M3 (07 §5.3).
        if (current.visibility == visibility) return VideoKitCommandResult.Executed
        mutableState.update { it.copy(visibility = visibility) }
        callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.VisibilityChanged(sessionId, visibility)) }
        val wasForeground = current.visibility != SessionVisibility.BACKGROUND
        val isForeground = visibility != SessionVisibility.BACKGROUND
        if (wasForeground != isForeground) {
            callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.ForegroundChanged(sessionId, isForeground)) }
        }
        return VideoKitCommandResult.Executed
    }

    private suspend fun setActiveAudio(current: VideoKitSessionState, command: VideoKitCommand.SetActiveAudio): VideoKitCommandResult {
        if (command.audioEpoch < acceptedAudioEpoch) return rejected(ErrorStage.PLAYBACK, "STALE_AUDIO_EPOCH")
        if (command.active && current.hiddenForLock) return rejected(ErrorStage.PLAYBACK, "LOCKED")
        acceptedAudioEpoch = command.audioEpoch
        mutableState.update { it.copy(activeAudio = command.active) }
        pushAudio()
        return VideoKitCommandResult.Executed
    }

    private suspend fun hideForLock(hidden: Boolean): VideoKitCommandResult {
        // 06 §4.2: stop rendering to the visible surface immediately and silence; the lock wins over audio commands.
        mutableState.update { if (hidden) it.copy(hiddenForLock = true, activeAudio = false) else it.copy(hiddenForLock = false) }
        val opened = handle
        if (opened != null) {
            if (hidden) opened.detach() else target?.let(opened::attach)
        }
        pushAudio()
        return VideoKitCommandResult.Executed
    }

    /** Sends the output volume and the audio track/focus policy of the current state to the engine. */
    private suspend fun pushAudio() {
        val opened = handle ?: return
        val state = mutableState.value
        opened.setVolume(PlaybackRules.outputVolume(state))
        opened.setAudioEnabled(PlaybackRules.audioEnabled(state))
    }

    private inline fun mediaCommand(
        current: VideoKitSessionState,
        command: VideoKitCommand,
        block: () -> VideoKitCommandResult,
    ): VideoKitCommandResult {
        bindRequired(current, commandName(command))?.let { return it }
        if (current.mediaKind?.isImage == true) return VideoKitCommandResult.Unsupported(UnsupportedReason.MEDIA_KIND)
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
        val opened: PlaybackHandle
        val target: Long
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
            opened = handle ?: return rejected(ErrorStage.PLAYBACK, "SEEK_WITHOUT_ENGINE")
            target = command.positionUs.coerceAtMost(current.durationUs ?: command.positionUs)
            pendingSeek?.complete(VideoKitCommandResult.Superseded)
            pendingSeek = outcome
            generation = ++seekGeneration
            mutableState.update { it.copy(seekingToUs = target) }
        }
        // The engine seek runs outside the lock; a newer seek completes this one as Superseded (04 §4.3).
        scope.launch {
            val failure = try {
                opened.seekTo(target, command.mode)
                null
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: Exception) {
                failure
            }
            mutex.withLock {
                if (generation != seekGeneration || outcome.isCompleted) return@withLock
                pendingSeek = null
                if (failure != null) {
                    mutableState.update { it.copy(seekingToUs = null) }
                    outcome.complete(
                        VideoKitCommandResult.Rejected(
                            StableErrors.of(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.PLAYBACK, "SEEK:${failure.typeName()}"),
                        ),
                    )
                    return@withLock
                }
                val from = mutableState.value.positionUs
                mutableState.update {
                    val endedPhase = if (it.phase == SessionPhase.ENDED && target < (it.durationUs ?: 0L)) SessionPhase.PAUSED else it.phase
                    it.copy(positionUs = target, seekingToUs = null, phase = endedPhase)
                }
                callbacks.notify("onPlaybackEvent") { onPlaybackEvent(VideoKitPlaybackEvent.UserSeek(sessionId, from, target)) }
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
        mutex.withLock {
            val current = mutableState.value
            if (current.phase.isReleasedOrReleasing) return VideoKitCommandResult.SessionReleased
            val token = source?.mediaToken ?: return rejected(ErrorStage.CALLBACK, "HOST_ACTION_WITHOUT_MEDIA")
            val entry = current.hostActions.firstOrNull { it.action.actionId == actionId } ?: return rejectedArgument("HOST_ACTION_ID")
            if (!entry.action.enabled) return rejected(ErrorStage.CALLBACK, "HOST_ACTION_DISABLED")
            // 04A I1: repeated requests while pending are merged and never reach the host again.
            if (entry.pending || actionId in inFlightActions) return VideoKitCommandResult.Superseded
            inFlightActions += actionId
            updateAction(actionId) { it.copy(pending = true, lastError = null) }
            request = HostActionRequest(actionId, sessionId, token)
        }
        var outcome: CallbackOutcome<HostActionResult>? = null
        try {
            outcome = callbacks.request("onHostActionRequested", timeouts.hostActionMs) { onHostActionRequested(request) }
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
        val outcome = callbacks.request("onNavigationRequested", timeouts.navigationMs) { onNavigationRequested(request) }
        return (outcome as? CallbackOutcome.Success)?.value ?: NavigationResult.FAILED
    }

    override fun setControlsVisible(visible: Boolean) {
        if (released) return
        var changed = false
        mutableState.update { current ->
            changed = current.controlsVisible != visible
            current.copy(controlsVisible = visible)
        }
        if (changed) callbacks.notify("onControlsVisibilityChanged") { onControlsVisibilityChanged(sessionId, visible) }
    }

    // ---------------------------------------------------------------- media info & thumbnails

    /** [info] completed with the host's source size (04A P2); `null` when nothing is known. Called under the mutex. */
    private fun withSourceSize(info: MediaInfo?): MediaInfo? {
        val size = info?.fileSizeBytes ?: source?.knownLength
        if (info == null && size == null) return null
        return (info ?: MediaInfo()).copy(fileSizeBytes = size)
    }

    /**
     * 04A P1: the frame nearest to [atUs] through the platform [com.videokit.core.spi.FrameSource], encoded by the
     * platform. Image thumbnails need the image engine (VK-M2). Failures are results, never exceptions.
     */
    override suspend fun captureThumbnail(atUs: Long, maxWidth: Int, maxHeight: Int): ThumbnailResult {
        if (released) return ThumbnailResult.Failed(StableErrors.of(ErrorCode.SESSION_RELEASED, ErrorStage.PLAYBACK, "THUMBNAIL_RELEASED"))
        if (atUs < 0 || maxWidth <= 0 || maxHeight <= 0) {
            return ThumbnailResult.Failed(StableErrors.invalidArgument(ErrorStage.PLAYBACK, "THUMBNAIL"))
        }
        val (bound, durationUs) = mutex.withLock { source to mutableState.value.durationUs }
        val media = bound ?: return ThumbnailResult.Failed(StableErrors.illegalState(ErrorStage.PLAYBACK, "THUMBNAIL_WITHOUT_MEDIA"))
        val frames = engines.frames
        if (frames == null || media.mediaKind.isImage) {
            return ThumbnailResult.Failed(StableErrors.of(ErrorCode.INVALID_STATE, ErrorStage.PLAYBACK, "THUMBNAILS_NOT_AVAILABLE"))
        }
        return try {
            withTimeout(runtime.options.sourceTimeoutMs) {
                val reader = frames.open(media)
                try {
                    reader.thumbnailAt(atUs.coerceAtMost(durationUs ?: atUs), Size(maxWidth, maxHeight))
                } finally {
                    withContext(NonCancellable + engines.scheduler.io) { runCatching { reader.close() } }
                }
            }
        } catch (timeout: TimeoutCancellationException) {
            ThumbnailResult.Failed(StableErrors.fromSourceFailure(timeout, ErrorStage.PLAYBACK))
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: SpiException) {
            ThumbnailResult.Failed(failure.error)
        } catch (failure: Exception) {
            ThumbnailResult.Failed(StableErrors.fromSourceFailure(failure, ErrorStage.PLAYBACK))
        }
    }

    // ---------------------------------------------------------------- snapshot & release

    override suspend fun captureState(): VideoKitPlaybackState {
        releaseResult.value?.let { return it.await() }
        return mutex.withLock { snapshotLocked() }
    }

    private fun snapshotLocked(): VideoKitPlaybackState =
        PlaybackRules.snapshotOf(sessionId, source?.mediaToken ?: lastMediaToken, mutableState.value, boundAtEpochMs)

    override suspend fun release(): VideoKitPlaybackState {
        val mine = CompletableDeferred<VideoKitPlaybackState>()
        if (!releaseResult.compareAndSet(null, mine)) return releaseResult.value!!.await()
        activeBind?.cancel()
        val snapshot = withContext(NonCancellable) {
            activeBind?.join()
            mutex.withLock {
                mutableState.update { it.copy(phase = SessionPhase.RELEASING) }
                val snap = snapshotLocked()
                target = null
                releaseSourceLocked()
                pendingSeek?.complete(VideoKitCommandResult.SessionReleased)
                pendingSeek = null
                mutableState.update {
                    it.copy(phase = SessionPhase.RELEASED, resourcesHeld = false, playWhenReady = false, seekingToUs = null)
                }
                snap
            }
        }
        callbacks.notify("onPlaybackSnapshot") { onPlaybackSnapshot(snapshot) }
        notifyPlayState()
        runtime.sessionReleased(sessionId)
        mine.complete(snapshot)
        scope.cancel()
        return snapshot
    }

    override fun close() {
        if (released) return
        runtime.scope.launch { release() }
    }

    // ---------------------------------------------------------------- rendering

    /**
     * Attaches [target] (04A I13). Target types the engine cannot draw into are refused with
     * `Unsupported(DEVICE_CAPABILITY)`; the previous target stays attached.
     */
    override fun attachSurface(target: VideoKitSurfaceTarget): VideoKitCommandResult {
        if (released) return VideoKitCommandResult.SessionReleased
        if (!engines.playback.supports(target)) return VideoKitCommandResult.Unsupported(UnsupportedReason.DEVICE_CAPABILITY)
        this.target = target
        val opened = handle
        if (opened != null && !mutableState.value.hiddenForLock) opened.attach(target)
        return VideoKitCommandResult.Executed
    }

    override fun detachSurface() {
        target = null
        handle?.detach()
    }

    // ---------------------------------------------------------------- helpers

    private fun notifyPlayState() {
        val current = mutableState.value
        callbacks.notify("onPlaybackEvent") {
            onPlaybackEvent(VideoKitPlaybackEvent.PlayStateChanged(sessionId, current.phase, current.playWhenReady))
        }
    }

    private fun notifySnapshot() {
        val snapshot = snapshotLocked()
        callbacks.notify("onPlaybackSnapshot") { onPlaybackSnapshot(snapshot) }
    }

    private fun rejected(stage: ErrorStage, what: String): VideoKitCommandResult =
        VideoKitCommandResult.Rejected(StableErrors.illegalState(stage, what))

    private fun rejectedArgument(what: String): VideoKitCommandResult =
        VideoKitCommandResult.Rejected(StableErrors.invalidArgument(ErrorStage.PLAYBACK, what))

    private companion object {
        const val MAX_RETRIES = 1
        const val NOTICE_AUDIO_UNSUPPORTED = "AUDIO_UNSUPPORTED_PLAYING_SILENT"

        fun commandName(command: VideoKitCommand): String = command.typeName().uppercase()
    }
}
