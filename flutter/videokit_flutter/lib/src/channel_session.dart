import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

import 'msg_mapping.dart';

/// [VideoKitSession] proxy over the channel (14 §8.5). The native session is the source of truth: every
/// `SessionUpdateMessage.state` replaces [state] as a whole; messages with an old `seq` are dropped (14 §8.3).
final class ChannelSession implements VideoKitSession {
  ChannelSession({
    required this.sessionId,
    required this._api,
    required this.isDemo,
    this.textureSize = const VideoSize(1280, 720),
    this.textureDisposeDelay = const Duration(seconds: 2),
  });

  final VideoKitHostApi _api;

  @override
  final String sessionId;

  @override
  final bool isDemo;

  /// Delay between the last lease release and the native texture destruction (14 §8.5).
  final Duration textureDisposeDelay;

  /// Initial texture size when the content size is still unknown (resized later through [resizeTexture]).
  final VideoSize textureSize;

  final ValueNotifier<VideoKitSessionState> _state = ValueNotifier(
    VideoKitSessionState.initial(),
  );
  final ValueNotifier<int?> _textureId = ValueNotifier(null);
  final ValueNotifier<VideoSize?> _videoSize = ValueNotifier(null);
  final StreamController<VideoKitEvent> _events = StreamController.broadcast();
  int _lastSeq = 0;
  bool _textureRequested = false;
  int _leases = 0;
  int _textureGeneration = 0;
  VideoSize? _textureSize;
  Timer? _disposeTimer;
  bool _closed = false;
  VideoKitPlaybackState? _finalSnapshot;

  @override
  ValueListenable<VideoKitSessionState> get state => _state;

  @override
  Stream<VideoKitEvent> get events => _events.stream;

  @override
  ValueListenable<int?> get textureId => _textureId;

  @override
  ValueListenable<VideoSize?> get videoSize => _videoSize;

  /// Last processed sequence number (diagnostics and tests).
  int get lastSeq => _lastSeq;

  /// Applies one update from the native stream; returns `false` when it was a duplicate or stale message.
  bool handleUpdate(SessionUpdateMessage message) {
    if (message.seq <= _lastSeq || _closed) return false;
    _lastSeq = message.seq;
    final stateMsg = message.state;
    if (stateMsg != null) {
      _state.value = sessionStateFromMsg(stateMsg);
      _videoSize.value = videoSizeFromMsg(stateMsg);
      _maybeResizeTexture();
    }
    final eventMsg = message.event;
    if (eventMsg != null) {
      final event = eventFromMsg(eventMsg);
      if (event != null) _events.add(event);
    }
    return true;
  }

  /// The native surface was recycled or recreated (14 §8.4).
  void handleTextureChanged(int? textureId) {
    if (!_closed && _textureRequested) _textureId.value = textureId;
  }

  /// Number of live texture leases (diagnostics and tests).
  int get textureLeaseCount => _leases;

  /// Texture lease (04A S7): the first lease creates the native texture; after the last lease is released
  /// the texture is destroyed with a delay of [textureDisposeDelay] (14 §8.5), so a quick re-display (page
  /// swipe, rebuild) reuses it.
  @override
  VideoKitTextureLease acquireTexture() {
    if (_closed || _finalSnapshot != null) {
      return _TextureLease(this, released: true);
    }
    _leases++;
    _disposeTimer?.cancel();
    _disposeTimer = null;
    _createTexture();
    return _TextureLease(this);
  }

  void _releaseLease() {
    if (_leases == 0) return;
    _leases--;
    if (_leases > 0 || !_textureRequested) return;
    _disposeTimer?.cancel();
    _disposeTimer = Timer(textureDisposeDelay, _disposeTexture);
  }

  void _createTexture() {
    if (_textureRequested || _closed) return;
    _textureRequested = true;
    final size = _videoSize.value ?? textureSize;
    _textureSize = size;
    final generation = ++_textureGeneration;
    unawaited(
      _api.createTexture(sessionId, size.width, size.height).then((id) {
        if (!_closed &&
            _textureRequested &&
            generation == _textureGeneration &&
            id >= 0) {
          _textureId.value = id;
        }
      }, onError: (Object _) {}),
    );
  }

  void _disposeTexture() {
    _disposeTimer = null;
    if (!_textureRequested) return;
    _textureRequested = false;
    _textureGeneration++;
    _textureSize = null;
    _textureId.value = null;
    unawaited(_api.disposeTexture(sessionId).catchError((Object _) {}));
  }

  // The content size became known or changed: follow it with the native texture.
  void _maybeResizeTexture() {
    final size = _videoSize.value;
    if (!_textureRequested || size == null || size == _textureSize) return;
    _textureSize = size;
    unawaited(
      _api
          .resizeTexture(sessionId, size.width, size.height)
          .catchError((Object _) {}),
    );
  }

  /// Resizes the native texture, for example when the widget size changes.
  Future<void> resizeTexture(int width, int height) =>
      _api.resizeTexture(sessionId, width, height);

  Future<VideoKitCommandResult> _call(
    Future<CommandResultMsg> Function() call,
  ) async {
    if (_closed) return const SessionReleased();
    try {
      return commandResultFromMsg(await call());
    } on Object catch (failure) {
      return Rejected(channelError(failure));
    }
  }

  @override
  Future<VideoKitCommandResult> bind(
    VideoKitMediaSource source, {
    VideoKitPlaybackState? initialState,
    List<VideoKitHostAction> hostActions = const [],
  }) async {
    final msg = mediaSourceToMsg(source);
    // Dart-implemented readAt sources are not carried in protocol 1 (14 §8.3).
    if (msg == null) return const Unsupported(UnsupportedReason.notImplemented);
    return _call(
      () => _api.bind(
        sessionId,
        msg,
        initialState == null ? null : playbackStateToMsg(initialState),
        hostActions.map(hostActionToMsg).toList(),
      ),
    );
  }

  @override
  Future<VideoKitCommandResult> execute(VideoKitCommand command) {
    final id = sessionId;
    return switch (command) {
      Play() => _call(() => _api.play(id)),
      Pause() => _call(() => _api.pause(id)),
      SeekTo(:final positionUs, :final mode) => _call(
        () => _api.seekTo(id, positionUs, seekModeToMsg(mode)),
      ),
      SetSpeed(:final speed) => _call(() => _api.setSpeed(id, speed)),
      SetMuted(:final muted) => _call(() => _api.setMuted(id, muted)),
      SetVolume(:final volume) => _call(() => _api.setVolume(id, volume)),
      SelectAudioTrack(:final trackId) => _call(
        () => _api.selectAudioTrack(id, trackId),
      ),
      SelectSubtitleTrack(:final trackId) => _call(
        () => _api.selectSubtitleTrack(id, trackId),
      ),
      SetTransform(:final transform) => _call(
        () => _api.setTransform(id, transformToMsg(transform)),
      ),
      SetOrientation(:final request) => _call(
        () => _api.setOrientation(id, wireOf(request)),
      ),
      SetFullscreen(:final fullscreen) => _call(
        () => _api.setFullscreen(id, fullscreen),
      ),
      SetVisibility(:final visibility) => _call(
        () => _api.setVisibility(id, wireOf(visibility)),
      ),
      SetActiveAudio(:final active, :final audioEpoch) => _call(
        () => _api.setActiveAudio(id, active, audioEpoch),
      ),
      HideContentForLock(:final hidden) => _call(
        () => _api.hideContentForLock(id, hidden),
      ),
      SetLooping(:final looping) => _call(() => _api.setLooping(id, looping)),
      Release() => release().then((_) => const Executed()),
    };
  }

  @override
  Future<void> updateHostActions(List<VideoKitHostAction> actions) async {
    if (_closed) return;
    await _api.updateHostActions(
      sessionId,
      actions.map(hostActionToMsg).toList(),
    );
  }

  @override
  Future<VideoKitCommandResult> requestHostAction(String actionId) =>
      _call(() => _api.requestHostAction(sessionId, actionId));

  @override
  Future<NavigationResult> requestNavigation(
    NavigationDirection direction,
  ) async {
    if (_closed) return NavigationResult.unavailable;
    try {
      return enumOf(
        NavigationResult.values,
        await _api.requestNavigation(sessionId, wireOf(direction)),
        NavigationResult.failed,
      );
    } on Object {
      return NavigationResult.failed;
    }
  }

  @override
  void setControlsVisible(bool visible) {
    if (_closed) return;
    unawaited(
      _api.setControlsVisible(sessionId, visible).catchError((Object _) {}),
    );
  }

  /// 04A P1: JPEG of the frame nearest to [atUs] fitting [maxWidth] x [maxHeight], from the native session.
  /// Channel failures are returned as [ThumbnailFailed], never thrown.
  @override
  Future<ThumbnailResult> captureThumbnail(
    int atUs,
    int maxWidth,
    int maxHeight,
  ) async {
    if (_closed || _finalSnapshot != null) {
      return const ThumbnailFailed(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.playback,
        ),
      );
    }
    try {
      return thumbnailFromMsg(
        await _api.captureThumbnail(sessionId, atUs, maxWidth, maxHeight),
      );
    } on Object catch (failure) {
      return ThumbnailFailed(channelError(failure));
    }
  }

  @override
  Future<VideoKitPlaybackState> captureState() async {
    final finalSnapshot = _finalSnapshot;
    if (finalSnapshot != null) return finalSnapshot;
    final msg = await _api.captureState(sessionId);
    return msg == null
        ? VideoKitPlaybackState(sessionId: sessionId)
        : playbackStateFromMsg(msg);
  }

  @override
  Future<VideoKitPlaybackState> release() async {
    final existing = _finalSnapshot;
    if (existing != null) return existing;
    PlaybackStateMsg? msg;
    try {
      msg = await _api.release(sessionId);
    } on Object {
      msg = null;
    }
    final snapshot = msg == null
        ? VideoKitPlaybackState(sessionId: sessionId)
        : playbackStateFromMsg(msg);
    _finalSnapshot ??= snapshot;
    _disposeTimer?.cancel();
    _leases = 0;
    _disposeTexture();
    return _finalSnapshot!;
  }

  @override
  Future<void> close() async {
    await release();
    _closed = true;
    await _events.close();
  }
}

final class _TextureLease implements VideoKitTextureLease {
  _TextureLease(this._session, {this._released = false});

  final ChannelSession _session;
  bool _released;

  @override
  ValueListenable<int?> get textureId => _session.textureId;

  @override
  void release() {
    if (_released) return;
    _released = true;
    _session._releaseLease();
  }
}
