import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import 'clock/fake_clock.dart';
import 'demo/demo_data.dart';
import 'demo/demo_media_info.dart';
import 'host_bridge.dart';
import 'scenario/scenario.dart';

/// Resolves the scenario used for a bound source.
typedef ScenarioResolver = Scenario Function(VideoKitMediaSource source);

/// Dart Fake session implementing the full state machine of 04 §3.1.
///
/// Driven by a [FakeClock]; never decodes media ([textureId] is null, the UI
/// shows `DemoPicture`). [isDemo] is always true.
class FakeSession implements VideoKitSession {
  /// Creates a session in `CREATED`.
  FakeSession({
    required this.sessionId,
    required this.clock,
    required this._host,
    required this._scenarioFor,
    this.config = const VideoKitSessionConfig(),
    this._onReleased,
    this._decoderAvailable,
    this.offscreenReleaseDelay = const Duration(seconds: 5),
  }) {
    _state.value = VideoKitSessionState(
      phase: SessionPhase.created,
      visibility: config.initialVisibility,
    );
    clock.addTickListener(_onTick);
  }

  @override
  final String sessionId;

  /// Clock.
  final FakeClock clock;

  /// Whether a video decoder is free for this session (M3 budget; null =
  /// unlimited).
  final bool Function(FakeSession session)? _decoderAvailable;

  /// How long an offscreen or background session keeps its decoder before
  /// releasing it (07 §5.3; state stays restorable).
  final Duration offscreenReleaseDelay;

  bool _resumeOnVisible = false;
  int _visibilityGeneration = 0;

  /// Whether this session holds a video decoder now (M3 budget).
  bool get holdsDecoder {
    final s = _state.value;
    return s.mediaKind == MediaKind.video &&
        s.resourcesHeld &&
        (s.phase.isBound || s.phase == SessionPhase.ended);
  }

  /// Test hook (M3): fails this session only, as a decoder crash or bad
  /// media would. Other sessions are not affected.
  void injectFault(VideoKitStableError error) {
    if (_released) return;
    _enterError(error);
    _set(_s.copyWith(resourcesHeld: false));
  }

  /// Test hook: another app took the system audio focus (04A K2, Android
  /// convention). For good: playback pauses (not muted, the session stays
  /// the audio source) and `AUDIO_FOCUS_LOST` is sent. [transient]: it
  /// pauses without a notice and [regainAudioFocus] resumes it.
  void loseAudioFocus({bool transient = false}) {
    if (_released || !_s.activeAudio) return;
    final wasPlaying = _s.phase == SessionPhase.playing || _s.playWhenReady;
    if (wasPlaying) unawaited(execute(const Pause()));
    if (transient) {
      _resumeOnFocus = wasPlaying;
      return;
    }
    _resumeOnFocus = false;
    _emit(const TransientNotice(NoticeCodes.audioFocusLost));
  }

  /// Test hook: a transient focus loss ended; playback resumes if it was
  /// playing before.
  void regainAudioFocus() {
    if (_released || !_resumeOnFocus) return;
    _resumeOnFocus = false;
    unawaited(execute(const Play()));
  }

  bool _resumeOnFocus = false;

  /// Creation config.
  final VideoKitSessionConfig config;

  final FakeHostBridge _host;
  final ScenarioResolver _scenarioFor;
  final void Function(FakeSession session)? _onReleased;

  final ValueNotifier<VideoKitSessionState> _state = ValueNotifier(
    VideoKitSessionState.initial(),
  );
  final ValueNotifier<int?> _textureId = ValueNotifier(null);
  final ValueNotifier<VideoSize?> _videoSize = ValueNotifier(null);
  final StreamController<VideoKitEvent> _events =
      StreamController<VideoKitEvent>.broadcast();

  VideoKitMediaSource? _source;
  DemoMediaItem? _profile;
  Scenario _scenario = const Scenario.normal();
  int _bindGeneration = 0;
  int _acceptedAudioEpoch = -1;
  bool _subtitlesChosen = false;
  final Set<String> _inFlight = {};
  final Set<String> _consumedOnceErrors = {};
  final Set<BufferingWindow> _firedBuffering = {};
  FakeClockTask? _seekTask;
  Completer<VideoKitCommandResult>? _pendingSeek;
  FakeClockTask? _bufferingTask;
  Future<VideoKitPlaybackState>? _releaseFuture;
  VideoKitPlaybackState? _finalSnapshot;

  /// Scenario of the current binding (tests/diagnostics).
  Scenario get scenario => _scenario;

  /// Demo profile of the bound media, if any.
  DemoMediaItem? get profile => _profile;

  VideoKitSessionState get _s => _state.value;

  @override
  ValueListenable<VideoKitSessionState> get state => _state;

  @override
  Stream<VideoKitEvent> get events => _events.stream;

  @override
  ValueListenable<int?> get textureId => _textureId;

  @override
  VideoKitTextureLease acquireTexture() => _FakeTextureLease(_textureId);

  @override
  ValueListenable<VideoSize?> get videoSize => _videoSize;

  @override
  bool get isDemo => true;

  bool get _released => _s.phase.isReleasingOrReleased;

  void _set(VideoKitSessionState next) {
    final previous = _s;
    if (next == previous) return;
    _state.value = next;
    if (next.phase != previous.phase) {
      _host.notify(
        (c) => c.onPlaybackEvent(
          PlayStateChanged(sessionId, next.phase, next.playWhenReady),
        ),
      );
    }
  }

  void _emit(VideoKitEvent event) {
    if (!_events.isClosed) _events.add(event);
  }

  static VideoKitStableError _illegal(SessionPhase phase, String kind) =>
      VideoKitStableError.invalidState(
        stage: ErrorStage.playback,
        diagnostic: 'illegal_transition:${phase.wireName}:$kind',
        params: {'phase': phase.wireName, 'command': kind},
      );

  static VideoKitStableError _invalidArgument(String what) =>
      VideoKitStableError.invalidArgument(
        stage: ErrorStage.playback,
        diagnostic: 'invalid_argument:$what',
        params: {'argument': what},
      );

  // ---------------------------------------------------------------- bind --

  @override
  Future<VideoKitCommandResult> bind(
    VideoKitMediaSource source, {
    VideoKitPlaybackState? initialState,
    List<VideoKitHostAction> hostActions = const [],
  }) async {
    if (_released) return const SessionReleased();
    if (_s.phase == SessionPhase.errorFatal) {
      return Rejected(_illegal(_s.phase, 'bind'));
    }
    _releaseCurrentSource();
    final generation = ++_bindGeneration;
    _source = source;
    final profile = DemoDataGenerator.profileFor(source);
    _profile = profile;
    _scenario = _scenarioFor(source);
    _firedBuffering.clear();
    _videoSize.value = null;
    _subtitlesChosen = initialState?.subtitlesEnabled != null;
    _set(
      _s.copyWith(
        phase: SessionPhase.binding,
        mediaKind: profile.kind,
        positionUs: 0,
        durationUs: null,
        bufferedUs: null,
        seekingToUs: null,
        playWhenReady: _s.phase == SessionPhase.binding && _s.playWhenReady,
        audioTracks: const [],
        subtitleTracks: const [],
        selectedAudioTrackId: null,
        selectedSubtitleTrackId: null,
        error: null,
        resourcesHeld: true,
        hostActions: [for (final a in hostActions) HostActionState(action: a)],
        // 04A L1 default per media kind; L2 details arrive with the probe.
        looping: profile.kind == MediaKind.imageAnimated,
        imageDetails: null,
      ),
    );

    await clock.delay(_scenario.loadDelay);
    if (_released) return const SessionReleased();
    if (generation != _bindGeneration) return const Superseded();

    // M3: no decoder left on the device (budget) → recoverable denial;
    // the host decides what to show (07 §3), nothing is retried here.
    if (profile.kind == MediaKind.video &&
        !(_decoderAvailable?.call(this) ?? true)) {
      const denied = VideoKitStableError(
        code: ErrorCode.decoderResourceExhausted,
        stage: ErrorStage.bind,
        retryable: true,
        suggestedAction: SuggestedAction.closeOtherSessions,
        diagnostic: 'decoder_budget',
      );
      _enterError(denied);
      _set(_s.copyWith(resourcesHeld: false));
      return const Rejected(denied);
    }
    final bindError = _onceError('bind', _scenario.bindError);
    if (bindError != null) {
      _enterError(bindError);
      return Rejected(bindError);
    }

    final isVideo = profile.kind == MediaKind.video;
    final duration = profile.durationUs;
    final supportedAudio = profile.audioTracks.where((t) => t.supported);
    var next = _s.copyWith(
      phase: SessionPhase.ready,
      durationUs: duration,
      bufferedUs: duration == null ? null : math.min(duration, 10000000),
      audioTracks: profile.audioTracks,
      subtitleTracks: profile.subtitleTracks,
      selectedAudioTrackId: supportedAudio.isEmpty
          ? null
          : supportedAudio.first.id,
      mediaInfo: demoMediaInfo(profile, source.mimeType),
      imageDetails: isVideo
          ? null
          : ImageDetails(
              frameCount: profile.kind == MediaKind.imageAnimated ? 48 : 1,
              decodedBytes: profile.size.width * profile.size.height * 4,
              sampleSize: 1,
            ),
      orientation: _s.orientation.copyWith(
        contentOrientation: profile.size.width == profile.size.height
            ? MediaOrientation.square
            : (profile.size.isPortrait
                  ? MediaOrientation.portrait
                  : MediaOrientation.landscape),
      ),
    );
    if (initialState != null) {
      final loops = isVideo || profile.kind == MediaKind.imageAnimated;
      next = next.copyWith(
        transform: initialState.transform,
        // 04A L3: a saved loop setting overrides the media-kind default.
        looping: loops ? (initialState.looping ?? next.looping) : null,
        orientation: next.orientation.copyWith(
          request: initialState.preferredOrientation,
          fullscreen: initialState.fullscreen,
        ),
      );
      if (isVideo) {
        final pos = initialState.positionUs ?? 0;
        next = next.copyWith(
          positionUs: duration == null ? pos : pos.clamp(0, duration),
          speed: initialState.speed ?? next.speed,
          volume: initialState.volume ?? next.volume,
          muted: initialState.muted ?? next.muted,
          selectedAudioTrackId:
              _trackExists(profile.audioTracks, initialState.audioTrackId)
              ? initialState.audioTrackId
              : next.selectedAudioTrackId,
          selectedSubtitleTrackId:
              _trackExists(profile.subtitleTracks, initialState.subtitleTrackId)
              ? initialState.subtitleTrackId
              : null,
        );
      }
    }
    if (next.playWhenReady &&
        (isVideo || profile.kind == MediaKind.imageAnimated)) {
      next = next.copyWith(phase: SessionPhase.playing);
    }
    _videoSize.value = profile.size;
    _set(next);
    return const Executed();
  }

  static bool _trackExists(List<TrackInfo> tracks, String? id) =>
      id != null && tracks.any((t) => t.id == id && t.supported);

  /// Returns [error] unless an error of this [kind] already fired once for the
  /// current media and is retryable (recoverable errors happen once).
  VideoKitStableError? _onceError(String kind, VideoKitStableError? error) {
    if (error == null) return null;
    final key = '${_source?.mediaToken}:$kind';
    if (error.retryable) {
      if (_consumedOnceErrors.contains(key)) return null;
      _consumedOnceErrors.add(key);
    }
    return error;
  }

  void _enterError(VideoKitStableError error) {
    _cancelSeek();
    _bufferingTask?.cancel();
    final phase = error.retryable
        ? SessionPhase.errorRecoverable
        : SessionPhase.errorFatal;
    _set(_s.copyWith(phase: phase, error: error, playWhenReady: false));
    _emit(ErrorRaised(error));
    if (error.retryable) {
      final source = _source;
      unawaited(
        _host
            .guarded(
              () => _host.callbacks.onRecoverableError(sessionId, error),
              _host.timeouts.recoveryDecision,
            )
            .then((decision) async {
              if (_released || source == null || _source != source) return;
              switch (decision ?? RecoveryDecision.keepError) {
                case RecoveryDecision.retry:
                  await bind(source, initialState: await captureState());
                case RecoveryDecision.release:
                  await release();
                case RecoveryDecision.keepError:
                  break;
              }
            }),
      );
    } else {
      _host.notify((c) => c.onFatalSessionError(sessionId, error));
    }
  }

  void _releaseCurrentSource() {
    _cancelSeek();
    _bufferingTask?.cancel();
    final old = _source;
    if (old != null) {
      _source = null;
      _emit(SourceReleased(old.mediaToken));
      _host.notify((c) => c.onSourceReleased(sessionId, old.mediaToken));
    }
  }

  void _cancelSeek() {
    _seekTask?.cancel();
    _seekTask = null;
    final pending = _pendingSeek;
    _pendingSeek = null;
    if (pending != null && !pending.isCompleted) {
      pending.complete(
        _released ? const SessionReleased() : const Superseded(),
      );
    }
  }

  // --------------------------------------------------------------- ticks --

  void _onTick(Duration delta) {
    final s = _s;
    if (s.phase != SessionPhase.playing || s.seekingToUs != null) return;
    final duration = s.durationUs;
    if (duration == null || duration <= 0) return;
    final deltaUs = (delta.inMicroseconds * s.speed).round();
    final from = s.positionUs;
    var to = from + deltaUs;

    // 04A L1: looping wraps without PlaybackEnded; otherwise the media
    // stops on its last frame (below for videos, here for animations).
    if (s.mediaKind == MediaKind.imageAnimated) {
      if (s.looping || to < duration) {
        _set(s.copyWith(positionUs: to % duration));
      } else {
        _set(
          s.copyWith(
            positionUs: duration,
            phase: SessionPhase.ended,
            playWhenReady: false,
          ),
        );
        _emit(const PlaybackEnded());
      }
      return;
    }

    // Scripted interruptions crossing [from, to].
    bool crosses(Duration at) =>
        from < at.inMicroseconds && to >= at.inMicroseconds;
    final corruptAt = _scenario.corruptAt;
    if (corruptAt != null && crosses(corruptAt)) {
      _set(s.copyWith(positionUs: corruptAt.inMicroseconds));
      _enterError(
        const VideoKitStableError(
          code: ErrorCode.corruptMedia,
          stage: ErrorStage.decode,
        ),
      );
      return;
    }
    final disconnectAt = _scenario.disconnectAt;
    if (disconnectAt != null && crosses(disconnectAt)) {
      final err = _onceError(
        'disconnect',
        const VideoKitStableError(
          code: ErrorCode.sourceDisconnected,
          stage: ErrorStage.playback,
          retryable: true,
          suggestedAction: SuggestedAction.retry,
        ),
      );
      if (err != null) {
        _set(s.copyWith(positionUs: disconnectAt.inMicroseconds));
        _enterError(err);
        return;
      }
    }
    for (final w in _scenario.bufferingWindows) {
      if (!_firedBuffering.contains(w) && crosses(w.at)) {
        _firedBuffering.add(w);
        _set(
          s.copyWith(
            positionUs: w.at.inMicroseconds,
            bufferedUs: w.at.inMicroseconds,
            phase: SessionPhase.buffering,
          ),
        );
        _host.notify(
          (c) => c.onPlaybackEvent(
            BufferingStarted(sessionId, w.at.inMicroseconds),
          ),
        );
        _bufferingTask = clock.schedule(w.duration, () {
          if (_s.phase != SessionPhase.buffering) return;
          _host.notify(
            (c) => c.onPlaybackEvent(
              BufferingEnded(sessionId, w.duration.inMicroseconds),
            ),
          );
          _set(
            _s.copyWith(
              phase: _s.playWhenReady
                  ? SessionPhase.playing
                  : SessionPhase.paused,
              bufferedUs: math.min(duration, _s.positionUs + 10000000),
            ),
          );
        });
        return;
      }
    }

    if (to >= duration && s.looping) {
      _set(s.copyWith(positionUs: to % duration));
      return;
    }
    if (to >= duration) {
      to = duration;
      _set(
        s.copyWith(
          positionUs: to,
          bufferedUs: duration,
          phase: SessionPhase.ended,
          playWhenReady: false,
        ),
      );
      _emit(const PlaybackEnded());
      return;
    }
    _set(
      s.copyWith(
        positionUs: to,
        bufferedUs: math.min(
          duration,
          math.max(s.bufferedUs ?? 0, to + 10000000),
        ),
      ),
    );
    if (s.visibility.isOnScreen) {
      _host.notify(
        (c) => c.onPlaybackEvent(WatchTimeAccumulated(sessionId, to - from)),
      );
    }
  }

  /// 07 §5.3: offscreen / background pause (and resume when visible
  /// again); the decoder is released after [offscreenReleaseDelay] while the
  /// position, tracks and transform stay.
  void _applyVisibility(SessionVisibility v) {
    final gen = ++_visibilityGeneration;
    // 04A V1: partly visible keeps playing (an engine may lower quality).
    if (v.isOnScreen) {
      if (!_s.resourcesHeld && _s.phase.isBound) {
        _set(_s.copyWith(resourcesHeld: true));
      }
      if (_resumeOnVisible) {
        _resumeOnVisible = false;
        unawaited(execute(const Play()));
      }
      return;
    }
    if (_s.phase == SessionPhase.playing || _s.playWhenReady) {
      _resumeOnVisible = true;
      unawaited(execute(const Pause()));
    }
    unawaited(
      clock.delay(offscreenReleaseDelay).then((_) {
        if (_released || gen != _visibilityGeneration) return;
        if (!_s.visibility.isOnScreen && _s.resourcesHeld) {
          _set(_s.copyWith(resourcesHeld: false));
        }
      }),
    );
  }

  // ------------------------------------------------------------ commands --

  @override
  Future<VideoKitCommandResult> execute(VideoKitCommand command) async {
    if (_released) return const SessionReleased();
    switch (command) {
      case Play():
        return _playPause(play: true, kind: command.kind);
      case Pause():
        return _playPause(play: false, kind: command.kind);
      case SeekTo():
        return _seek(command);
      case SetSpeed(:final speed):
        return _videoOnly(command.kind, () {
          if (speed < 0.25 || speed > 4.0 || speed.isNaN) {
            return Rejected(_invalidArgument('speed'));
          }
          _set(_s.copyWith(speed: speed));
          return const Executed();
        });
      case SetLooping(:final looping):
        // 04A L1: videos and animated images; static images unsupported.
        final phase = _s.phase;
        if (!(phase.isBound || phase == SessionPhase.binding)) {
          return Rejected(_illegal(phase, command.kind));
        }
        if (_s.mediaKind != MediaKind.video &&
            _s.mediaKind != MediaKind.imageAnimated) {
          return const Unsupported(UnsupportedReason.mediaKind);
        }
        _set(_s.copyWith(looping: looping));
        return const Executed();
      case SetMuted(:final muted):
        return _videoOnly(command.kind, () {
          _set(_s.copyWith(muted: muted));
          return const Executed();
        });
      case SetVolume(:final volume):
        return _videoOnly(command.kind, () {
          if (volume < 0 || volume > 1 || volume.isNaN) {
            return Rejected(_invalidArgument('volume'));
          }
          _set(_s.copyWith(volume: volume));
          return const Executed();
        });
      case SelectAudioTrack(:final trackId):
        return _videoOnly(command.kind, () {
          if (trackId == null) {
            final first = _s.audioTracks.where((t) => t.supported);
            _set(
              _s.copyWith(
                selectedAudioTrackId: first.isEmpty ? null : first.first.id,
              ),
            );
            return const Executed();
          }
          final track = _s.audioTracks.where((t) => t.id == trackId);
          if (track.isEmpty) {
            return Rejected(_invalidArgument('trackId'));
          }
          if (!track.first.supported) {
            return const Unsupported(UnsupportedReason.deviceCapability);
          }
          _set(_s.copyWith(selectedAudioTrackId: trackId));
          return const Executed();
        });
      case SelectSubtitleTrack(:final trackId):
        return _videoOnly(command.kind, () {
          if (trackId != null &&
              !_s.subtitleTracks.any((t) => t.id == trackId)) {
            return Rejected(_invalidArgument('trackId'));
          }
          _subtitlesChosen = true;
          _set(_s.copyWith(selectedSubtitleTrackId: trackId));
          return const Executed();
        });
      case SetTransform(:final transform):
        final clamped = transform.copyWith(
          scale: transform.scale.clamp(0.25, 16.0),
          panX: transform.panX.clamp(-1.0, 1.0),
          panY: transform.panY.clamp(-1.0, 1.0),
        );
        _set(_s.copyWith(transform: clamped));
        return const Executed();
      case SetOrientation(:final request):
        _set(
          _s.copyWith(orientation: _s.orientation.copyWith(request: request)),
        );
        return const Executed();
      case SetFullscreen(:final fullscreen):
        _set(
          _s.copyWith(
            orientation: _s.orientation.copyWith(fullscreen: fullscreen),
          ),
        );
        return const Executed();
      case SetVisibility(:final visibility):
        if (visibility != _s.visibility) {
          _set(_s.copyWith(visibility: visibility));
          _applyVisibility(visibility);
          _host.notify(
            (c) => c.onPlaybackEvent(VisibilityChanged(sessionId, visibility)),
          );
        }
        return const Executed();
      case SetActiveAudio(:final active, :final audioEpoch):
        if (audioEpoch < _acceptedAudioEpoch) {
          return Rejected(
            VideoKitStableError.invalidState(
              stage: ErrorStage.playback,
              diagnostic: 'stale_audio_epoch',
              params: {'audioEpoch': '$audioEpoch'},
            ),
          );
        }
        if (active && _s.hiddenForLock) {
          // Lock wins over audio activation (06 §4.2, vector lock.*).
          return Rejected(_illegal(_s.phase, command.kind));
        }
        _acceptedAudioEpoch = audioEpoch;
        _set(_s.copyWith(activeAudio: active));
        return const Executed();
      case HideContentForLock(:final hidden):
        var next = _s.copyWith(hiddenForLock: hidden);
        if (hidden && next.phase == SessionPhase.playing) {
          next = next.copyWith(
            phase: SessionPhase.paused,
            playWhenReady: false,
          );
        }
        _set(next);
        return const Executed();
      case Release():
        await release();
        return const Executed();
    }
  }

  VideoKitCommandResult _videoOnly(
    String kind,
    VideoKitCommandResult Function() run,
  ) {
    final phase = _s.phase;
    if (!(phase.isBound || phase == SessionPhase.binding)) {
      return Rejected(_illegal(phase, kind));
    }
    if (_s.mediaKind != MediaKind.video) {
      return const Unsupported(UnsupportedReason.mediaKind);
    }
    return run();
  }

  VideoKitCommandResult _playPause({required bool play, required String kind}) {
    final s = _s;
    if (s.phase == SessionPhase.binding) {
      _set(s.copyWith(playWhenReady: play));
      return const Executed();
    }
    if (!s.phase.isBound) return Rejected(_illegal(s.phase, kind));
    if (s.mediaKind != MediaKind.video &&
        s.mediaKind != MediaKind.imageAnimated) {
      return const Unsupported(UnsupportedReason.mediaKind);
    }
    if (play && s.hiddenForLock) {
      return const Unsupported(UnsupportedReason.contentLocked);
    }
    if (play) {
      final restart = s.phase == SessionPhase.ended;
      _set(
        s.copyWith(
          phase: s.phase == SessionPhase.buffering
              ? SessionPhase.buffering
              : SessionPhase.playing,
          playWhenReady: true,
          positionUs: restart ? 0 : s.positionUs,
        ),
      );
    } else {
      final next = switch (s.phase) {
        SessionPhase.playing || SessionPhase.buffering => SessionPhase.paused,
        _ => s.phase,
      };
      _set(s.copyWith(phase: next, playWhenReady: false));
    }
    return const Executed();
  }

  Future<VideoKitCommandResult> _seek(SeekTo command) {
    final s = _s;
    if (!s.phase.isBound) {
      return Future.value(Rejected(_illegal(s.phase, command.kind)));
    }
    if (s.mediaKind != MediaKind.video) {
      return Future.value(const Unsupported(UnsupportedReason.mediaKind));
    }
    if (_source?.seekability == Seekability.sequentialOnly) {
      return Future.value(
        const Unsupported(UnsupportedReason.sourceSequentialOnly),
      );
    }
    if (command.positionUs < 0) {
      return Future.value(Rejected(_invalidArgument('positionUs')));
    }
    _cancelSeek();
    final duration = s.durationUs ?? 0;
    final target = command.positionUs.clamp(0, duration);
    if (target != command.positionUs) {
      _emit(const TransientNotice(NoticeCodes.seekClamped));
    }
    final from = s.positionUs;
    final completer = Completer<VideoKitCommandResult>();
    _pendingSeek = completer;
    _set(s.copyWith(seekingToUs: target));
    final latency = command.mode == SeekMode.preview
        ? _scenario.seekLatency ~/ 2
        : _scenario.seekLatency;
    _seekTask = clock.schedule(latency, () {
      if (!identical(_pendingSeek, completer)) return;
      _pendingSeek = null;
      _seekTask = null;
      final cur = _s;
      _set(
        cur.copyWith(
          positionUs: target,
          seekingToUs: null,
          phase: cur.phase == SessionPhase.ended ? SessionPhase.paused : null,
          bufferedUs: math.min(duration, target + 10000000),
        ),
      );
      if (command.mode != SeekMode.preview) {
        _host.notify(
          (c) => c.onPlaybackEvent(UserSeek(sessionId, from, target)),
        );
      }
      completer.complete(const Executed());
    });
    return completer.future;
  }

  // -------------------------------------------------------- host actions --

  @override
  Future<VideoKitCommandResult> requestHostAction(String actionId) async {
    if (_released) return const SessionReleased();
    // Host actions need bound media (errors included: e.g. "delete" on a
    // broken file); vector host_action.before_bind.rejected.
    if (!_s.phase.isBound && !_s.phase.isError) {
      return Rejected(_illegal(_s.phase, 'requestHostAction'));
    }
    final index = _s.hostActions.indexWhere(
      (a) => a.action.actionId == actionId,
    );
    if (index < 0) return Rejected(_invalidArgument('actionId'));
    if (!_s.hostActions[index].action.enabled) {
      return const Unsupported(UnsupportedReason.hostDisabled);
    }
    // Pending duplicate: merged, host not called again (04A I1).
    if (_s.hostActions[index].pending) return const Superseded();
    _inFlight.add(actionId);
    _updateAction(actionId, (a) => a.copyWith(pending: true));
    unawaited(_runHostAction(actionId));
    return const Executed();
  }

  Future<void> _runHostAction(String actionId) async {
    final request = HostActionRequest(
      actionId: actionId,
      sessionId: sessionId,
      mediaToken: _source?.mediaToken ?? '',
    );
    final HostActionResult? result;
    if (_scenario.hostActionTimeouts.contains(actionId)) {
      // Simulated host that never answers.
      result = await _host.guarded(
        () => Completer<HostActionResult>().future,
        _host.timeouts.hostAction,
      );
    } else {
      result = await _host.guarded(
        () => _host.callbacks.onHostActionRequested(request),
        _host.timeouts.hostAction,
      );
    }
    _inFlight.remove(actionId);
    if (_released) return;
    if (result == null || result.status == HostActionStatus.failed) {
      final error = result == null
          ? FakeHostBridge.callbackFailed
          : FakeHostBridge.callbackFailed.copyWith(
              params: const {'reason': 'hostReported'},
            );
      _updateAction(
        actionId,
        (a) => a.copyWith(
          pending: a.action.pending,
          lastStatus: HostActionStatus.failed,
          lastError: error,
        ),
      );
      _emit(HostActionFailed(actionId, error, messageKey: result?.messageKey));
      return;
    }
    final updated = result.updatedAction;
    _updateAction(
      actionId,
      (a) => a.copyWith(
        action: updated ?? a.action,
        // PENDING keeps the action pending until the host updates it
        // (04A S1; Kotlin vector runner HOST_ACTIONS_SETTLED).
        pending:
            result!.status == HostActionStatus.pending ||
            (updated ?? a.action).pending,
        lastStatus: result.status,
        lastError: null,
      ),
    );
  }

  void _updateAction(
    String actionId,
    HostActionState Function(HostActionState) f,
  ) {
    _set(
      _s.copyWith(
        hostActions: [
          for (final a in _s.hostActions)
            a.action.actionId == actionId ? f(a) : a,
        ],
      ),
    );
  }

  @override
  Future<void> updateHostActions(List<VideoKitHostAction> actions) async {
    if (_released) return;
    final previous = {for (final a in _s.hostActions) a.action.actionId: a};
    _set(
      _s.copyWith(
        hostActions: [
          for (final a in actions)
            (previous[a.actionId] ?? HostActionState(action: a)).copyWith(
              action: a,
              pending: _inFlight.contains(a.actionId) || a.pending,
            ),
        ],
      ),
    );
  }

  @override
  Future<NavigationResult> requestNavigation(
    NavigationDirection direction,
  ) async {
    if (_released) return NavigationResult.failed;
    final result = await _host.guarded(
      () => _host.callbacks.onNavigationRequested(
        NavigationRequest(
          sessionId: sessionId,
          direction: direction,
          mediaToken: _source?.mediaToken,
        ),
      ),
      _host.timeouts.navigation,
    );
    return result ?? NavigationResult.failed;
  }

  @override
  void setControlsVisible(bool visible) {
    if (_released || _s.controlsVisible == visible) return;
    _set(_s.copyWith(controlsVisible: visible));
    _host.notify((c) => c.onControlsVisibilityChanged(sessionId, visible));
  }

  // ------------------------------------------------------------ snapshot --

  /// Demo thumbnail (04A P1): a PNG fitting [maxWidth]×[maxHeight] drawn
  /// from the media seed with a marker at [atUs].
  @override
  Future<ThumbnailResult> captureThumbnail(
    int atUs,
    int maxWidth,
    int maxHeight,
  ) async {
    if (_released) {
      return const ThumbnailFailed(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.playback,
        ),
      );
    }
    final phase = _s.phase;
    if (!(phase.isBound || phase == SessionPhase.ended)) {
      return const ThumbnailFailed(
        VideoKitStableError.invalidState(stage: ErrorStage.playback),
      );
    }
    if (maxWidth <= 0 || maxHeight <= 0 || atUs < 0) {
      return const ThumbnailFailed(
        VideoKitStableError.invalidArgument(stage: ErrorStage.playback),
      );
    }
    final size = _videoSize.value ?? const VideoSize(16, 9);
    final (w, h) = fitThumbnail(size.width, size.height, maxWidth, maxHeight);
    final d = _s.durationUs ?? 0;
    return ThumbnailCaptured(
      bytes: demoThumbnailPng(
        w,
        h,
        stableHash(_source?.mediaToken ?? sessionId),
        d <= 0 ? 0 : atUs / d,
      ),
      width: w,
      height: h,
      mimeType: 'image/png',
    );
  }

  @override
  Future<VideoKitPlaybackState> captureState() async =>
      _finalSnapshot ?? _snapshot();

  VideoKitPlaybackState _snapshot() {
    final s = _s;
    final isVideo = s.mediaKind == MediaKind.video;
    return VideoKitPlaybackState(
      sessionId: sessionId,
      mediaToken: _source?.mediaToken,
      zoom: s.transform.scale,
      panX: s.transform.panX,
      panY: s.transform.panY,
      rotationDeg: s.transform.rotationDeg,
      fitMode: s.transform.fitMode,
      preferredOrientation: s.orientation.request,
      fullscreen: s.orientation.fullscreen,
      positionUs: isVideo ? (s.seekingToUs ?? s.positionUs) : null,
      speed: isVideo ? s.speed : null,
      volume: isVideo ? s.volume : null,
      muted: isVideo ? s.muted : null,
      subtitleTrackId: isVideo ? s.selectedSubtitleTrackId : null,
      subtitlesEnabled: isVideo && _subtitlesChosen
          ? s.selectedSubtitleTrackId != null
          : null,
      audioTrackId: isVideo ? s.selectedAudioTrackId : null,
      // 04A L3: only media that can loop carry the setting.
      looping: isVideo || s.mediaKind == MediaKind.imageAnimated
          ? s.looping
          : null,
    );
  }

  // ------------------------------------------------------------- release --

  @override
  Future<VideoKitPlaybackState> release() => _releaseFuture ??= _doRelease();

  Future<VideoKitPlaybackState> _doRelease() async {
    final snapshot = _snapshot();
    _bindGeneration++;
    _set(_s.copyWith(phase: SessionPhase.releasing));
    _releaseCurrentSource();
    _host.notify((c) => c.onPlaybackSnapshot(snapshot));
    await Future<void>.delayed(Duration.zero);
    _finalSnapshot = snapshot;
    clock.removeTickListener(_onTick);
    _set(
      _s.copyWith(
        phase: SessionPhase.released,
        playWhenReady: false,
        seekingToUs: null,
        resourcesHeld: false,
        activeAudio: false,
        hostActions: [
          for (final a in _s.hostActions) a.copyWith(pending: false),
        ],
      ),
    );
    _host.notify(
      (c) => c.onPlaybackEvent(SessionEnded(sessionId, snapshot.mediaToken)),
    );
    await _events.close();
    _onReleased?.call(this);
    return snapshot;
  }

  @override
  Future<void> close() async {
    unawaited(release());
  }

  // ----------------------------------------------------- preview support --

  /// Updates duration of a bound preview session (used by `FakeEditProject`
  /// when the timeline changes).
  void debugSetDuration(int durationUs) {
    if (!_s.phase.isBound) return;
    _set(
      _s.copyWith(
        durationUs: durationUs,
        positionUs: math.min(_s.positionUs, durationUs),
        bufferedUs: math.min(_s.bufferedUs ?? 0, durationUs),
      ),
    );
  }
}

/// Texture lease of the Fake: the texture ID is always null (04A S7).
final class _FakeTextureLease implements VideoKitTextureLease {
  _FakeTextureLease(this.textureId);

  @override
  final ValueListenable<int?> textureId;

  @override
  void release() {}
}
