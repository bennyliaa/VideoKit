import 'dart:async';

import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

import 'channel_edit_project.dart';
import 'channel_session.dart';
import 'licenses.dart';
import 'msg_mapping.dart';

/// Why [FlutterVideoKit.connect] failed (14 §8.3). The UI shows a clear error and does not continue.
enum VideoKitInitFailure {
  /// The native protocol major version differs from [kChannelProtocolVersion].
  protocolMismatch,

  /// The native side has no backend (release build without `VideoKitFlutter.setBackend`, 14 §11.4).
  noBackend,

  /// The channel is not available (plugin not registered) or failed.
  channelUnavailable,
}

/// Thrown by [FlutterVideoKit.connect].
final class VideoKitInitException implements Exception {
  /// Creates the exception.
  const VideoKitInitException(this.failure, [this.diagnostic]);

  /// Reason.
  final VideoKitInitFailure failure;

  /// English, redacted diagnostic (13 §3.1).
  final String? diagnostic;

  @override
  String toString() =>
      'VideoKitInitException(${failure.name}${diagnostic == null ? '' : ': $diagnostic'})';
}

/// [VideoKit] over the native Kit through the Pigeon channel (14 §8.5).
///
/// Create it with [connect]; it performs the handshake, registers the host callbacks of [VideoKitConfig] and
/// dispatches the session and edit update streams to the proxies by id.
final class FlutterVideoKit implements VideoKit {
  FlutterVideoKit._(this._platform, this._config, HandshakeResponse handshake)
    : apiVersion = VideoKitApiVersion.parse(handshake.apiVersion),
      isDemo = handshake.demoBackend;

  final VideoKitPlatform _platform;
  final VideoKitConfig _config;
  final Map<String, ChannelSession> _sessions = {};
  final Map<String, ChannelEditProject> _projects = {};
  final List<StreamSubscription<Object?>> _subscriptions = [];
  bool _closed = false;

  @override
  final VideoKitApiVersion apiVersion;

  /// From the handshake (`demoBackend`); the UI then shows the demo badge on every surface (14 §8.5).
  @override
  final bool isDemo;

  VideoKitHostApi get _api => _platform.hostApi;

  /// Connects to the native Kit. Throws [VideoKitInitException] on protocol mismatch, missing backend or
  /// unavailable channel.
  static Future<FlutterVideoKit> connect(
    VideoKitConfig config, {
    VideoKitPlatform? platform,
  }) async {
    // 04A X1: the open source notices of the plugin and the Kit appear on the host's licence page.
    registerVideoKitLicenses();
    final p = platform ?? VideoKitPlatform.instance;
    final timeouts = config.callbackTimeouts;
    HandshakeResponse response;
    try {
      response = await p.hostApi.handshake(
        HandshakeRequest(
          protocolVersion: kChannelProtocolVersion,
          dartPackageVersion: kVideoKitFlutterPackageVersion,
          hostActionTimeoutMs: timeouts.hostAction.inMilliseconds,
          navigationTimeoutMs: timeouts.navigation.inMilliseconds,
          recoveryDecisionTimeoutMs: timeouts.recoveryDecision.inMilliseconds,
          notificationTimeoutMs: timeouts.notification.inMilliseconds,
          // REQ-API-10: the native runtime enforces the switches at its API
          // entry points and asks the gate back through checkFeature.
          featureGateTimeoutMs: timeouts.featureGate.inMilliseconds,
          features: featureModesToMsg(config.features),
        ),
      );
    } on Object catch (failure) {
      final text = failure.toString();
      throw VideoKitInitException(
        text.contains('VIDEOKIT_NO_BACKEND')
            ? VideoKitInitFailure.noBackend
            : VideoKitInitFailure.channelUnavailable,
        'HANDSHAKE:${failure.runtimeType}',
      );
    }
    if (response.protocolVersion != kChannelProtocolVersion) {
      throw VideoKitInitException(
        VideoKitInitFailure.protocolMismatch,
        'native=${response.protocolVersion} dart=$kChannelProtocolVersion',
      );
    }
    final kit = FlutterVideoKit._(p, config, response);
    kit._start();
    return kit;
  }

  void _start() {
    _platform.setCallbacks(_CallbacksBridge(this, _config.hostCallbacks));
    _subscriptions
      ..add(
        _platform.sessionUpdates().listen(
          (m) => _sessions[m.sessionId]?.handleUpdate(m),
          onError: (Object _) {},
        ),
      )
      ..add(
        _platform.editUpdates().listen(
          (m) => _projects[m.projectId]?.handleUpdate(m),
          onError: (Object _) {},
        ),
      );
  }

  ChannelSession _sessionFor(String id) => _sessions.putIfAbsent(
    id,
    () => ChannelSession(sessionId: id, api: _api, isDemo: isDemo),
  );

  @override
  Future<VideoKitCapabilities> capabilities(CapabilityRequest request) async =>
      capabilitiesFromMsg(
        await _api.capabilities(capabilityRequestToMsg(request)),
      );

  @override
  Future<VideoKitSession> createSession(VideoKitSessionConfig config) async {
    if (_closed) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.bind,
        ),
      );
    }
    final result = await _api.createSession(sessionConfigToMsg(config));
    final id = result.id;
    if (id == null) {
      throw VideoKitException(
        result.error == null
            ? channelError('MissingError')
            : errorFromMsg(result.error!),
      );
    }
    return _sessionFor(id);
  }

  /// Observes a session owned by the native host (add-to-app, 14 §9.1): the host shared it with
  /// `VideoKitFlutter.share` and passed its id to the embed. [VideoKitSession.release] on the returned proxy only
  /// stops observing it; the host decides when the session ends. Throws [VideoKitException] (SESSION_RELEASED)
  /// when the id is not shared or already released.
  Future<VideoKitSession> adoptSession(String sessionId) async {
    if (_closed) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.bind,
        ),
      );
    }
    final result = await _api.adoptSession(sessionId);
    final id = result.id;
    if (id == null) {
      throw VideoKitException(
        result.error == null
            ? channelError('MissingError')
            : errorFromMsg(result.error!),
      );
    }
    return _sessionFor(id);
  }

  @override
  Future<VideoKitEditProject> createEditProject(
    EditProjectConfig config,
  ) async => _project(await _api.createEditProject(editConfigToMsg(config)));

  @override
  Future<VideoKitEditProject> restoreEditProject(
    SerializedEditProject serialized,
    EditProjectConfig config,
  ) async => _project(
    await _api.restoreEditProject(
      SerializedProjectMsg(
        schemaVersion: serialized.schemaVersion,
        json: serialized.json,
      ),
      editConfigToMsg(config),
    ),
  );

  ChannelEditProject _project(CreateResultMsg result) {
    final id = result.id;
    if (id == null) {
      throw VideoKitException(
        result.error == null
            ? channelError('MissingError')
            : errorFromMsg(result.error!),
      );
    }
    return _projects.putIfAbsent(
      id,
      () => ChannelEditProject(
        projectId: id,
        api: _api,
        isDemo: isDemo,
        sessionFor: _sessionFor,
      ),
    );
  }

  /// Session proxy for [sessionId], if this instance created it.
  ChannelSession? sessionById(String sessionId) => _sessions[sessionId];

  @override
  Future<void> close() async {
    if (_closed) return;
    _closed = true;
    try {
      await _api.closeAll();
    } on Object {
      // The native side releases everything with its engine anyway.
    }
    for (final subscription in _subscriptions) {
      await subscription.cancel();
    }
    _platform.setCallbacks(null);
  }
}

/// Native → Dart host callbacks, forwarded to the Dart host's [VideoKitHostCallbacks] (04 §8). Timeouts
/// are applied on the native side (04A I8); an exception here reaches native as HOST_CALLBACK_FAILED.
final class _CallbacksBridge implements VideoKitCallbacksApi {
  _CallbacksBridge(this._kit, this._host);

  final FlutterVideoKit _kit;
  final VideoKitHostCallbacks _host;

  @override
  Future<HostActionResultMsg> onHostActionRequested(
    HostActionRequestMsg request,
  ) async => hostActionResultToMsg(
    await _host.onHostActionRequested(hostActionRequestFromMsg(request)),
  );

  @override
  Future<String> onNavigationRequested(NavigationRequestMsg request) async =>
      wireOf(
        await _host.onNavigationRequested(navigationRequestFromMsg(request)),
      );

  @override
  Future<void> onPlaybackSnapshot(PlaybackStateMsg snapshot) =>
      _host.onPlaybackSnapshot(playbackStateFromMsg(snapshot));

  @override
  Future<void> onPlaybackEvent(PlaybackEventMsg event) async {
    final mapped = playbackEventFromMsg(event);
    if (mapped != null) await _host.onPlaybackEvent(mapped);
  }

  @override
  Future<void> onControlsVisibilityChanged(String sessionId, bool visible) =>
      _host.onControlsVisibilityChanged(sessionId, visible);

  @override
  Future<void> onSourceReleased(String sessionId, String mediaToken) =>
      _host.onSourceReleased(sessionId, mediaToken);

  @override
  Future<String> onRecoverableError(
    String sessionId,
    StableErrorMsg error,
  ) async =>
      wireOf(await _host.onRecoverableError(sessionId, errorFromMsg(error)));

  @override
  Future<void> onFatalSessionError(String sessionId, StableErrorMsg error) =>
      _host.onFatalSessionError(sessionId, errorFromMsg(error));

  /// REQ-API-10: the native gate asks the Dart host; the native side applies
  /// the timeout, and an exception here counts as denied there.
  @override
  Future<FeatureAccessMsg> checkFeature(
    String feature,
    String? sessionId,
  ) async => featureAccessToMsg(
    await _host.checkFeature(VideoKitFeature.fromName(feature), sessionId),
  );

  @override
  void onTextureChanged(String sessionId, int? textureId) =>
      _kit.sessionById(sessionId)?.handleTextureChanged(textureId);
}
