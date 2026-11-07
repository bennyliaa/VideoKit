import 'dart:async';
import 'dart:typed_data';

import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

/// Simulated native side for unit tests: records calls and answers with scripted messages.
class FakeHostApi implements VideoKitHostApi {
  FakeHostApi({
    this.protocolVersion = 1,
    this.demo = true,
    this.handshakeError,
  });

  final int protocolVersion;
  final bool demo;
  final Object? handshakeError;
  final List<String> calls = [];
  HandshakeRequest? handshakeRequest;
  CommandResultMsg nextResult = CommandResultMsg(
    kind: CommandResultKind.executed,
  );
  int sessionCounter = 0;
  MediaSourceMsg? lastBoundSource;
  EditCommandMsg? lastEdit;
  ExportResultMsg? exportResult;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<HandshakeResponse> handshake(HandshakeRequest request) async {
    handshakeRequest = request;
    final error = handshakeError;
    if (error != null) throw error;
    return HandshakeResponse(
      protocolVersion: protocolVersion,
      nativeKitVersion: 'test',
      apiVersion: '1.0.0',
      demoBackend: demo,
    );
  }

  @override
  Future<CreateResultMsg> createSession(SessionConfigMsg config) async {
    calls.add('createSession:${config.priority}:${config.initialVisibility}');
    return CreateResultMsg(id: 'native-session-${++sessionCounter}');
  }

  Future<CommandResultMsg> _record(String name) async {
    calls.add(name);
    return nextResult;
  }

  @override
  Future<CommandResultMsg> bind(
    String sessionId,
    MediaSourceMsg source,
    PlaybackStateMsg? initial,
    List<HostActionMsg> actions,
  ) {
    lastBoundSource = source;
    return _record('bind:$sessionId:${source.sourceRef}:${actions.length}');
  }

  @override
  Future<CommandResultMsg> play(String sessionId) => _record('play:$sessionId');

  @override
  Future<CommandResultMsg> seekTo(
    String sessionId,
    int positionUs,
    SeekModeMsg mode,
  ) => _record('seekTo:$positionUs:${mode.name}');

  @override
  Future<CommandResultMsg> setVisibility(String sessionId, String visibility) =>
      _record('setVisibility:$visibility');

  @override
  Future<CommandResultMsg> setOrientation(String sessionId, String request) =>
      _record('setOrientation:$request');

  @override
  Future<CommandResultMsg> setActiveAudio(
    String sessionId,
    bool active,
    int audioEpoch,
  ) => _record('setActiveAudio:$active:$audioEpoch');

  @override
  Future<CommandResultMsg> setLooping(String sessionId, bool looping) =>
      _record('setLooping:$looping');

  @override
  Future<ThumbnailResultMsg> captureThumbnail(
    String sessionId,
    int atUs,
    int maxWidth,
    int maxHeight,
  ) async {
    calls.add('captureThumbnail:$atUs:$maxWidth x $maxHeight');
    if (atUs < 0) {
      return ThumbnailResultMsg(
        error: StableErrorMsg(
          code: 'INVALID_ARGUMENT',
          stage: 'PLAYBACK',
          retryable: false,
          suggestedAction: 'NONE',
          params: {},
        ),
      );
    }
    return ThumbnailResultMsg(
      bytes: Uint8List.fromList([0xFF, 0xD8, 0xFF, 0xD9]),
      width: 160,
      height: 90,
      mimeType: 'image/jpeg',
    );
  }

  @override
  Future<CommandResultMsg> requestHostAction(
    String sessionId,
    String actionId,
  ) => _record('requestHostAction:$actionId');

  @override
  Future<String> requestNavigation(String sessionId, String direction) async {
    calls.add('requestNavigation:$direction');
    return 'NAVIGATION_RESULT_FROM_THE_FUTURE';
  }

  @override
  Future<void> setControlsVisible(String sessionId, bool visible) async =>
      calls.add('setControlsVisible:$visible');

  @override
  Future<int> createTexture(String sessionId, int width, int height) async {
    calls.add('createTexture:$width x $height');
    return 42;
  }

  @override
  Future<void> disposeTexture(String sessionId) async =>
      calls.add('disposeTexture');

  @override
  Future<PlaybackStateMsg?> release(String sessionId) async {
    calls.add('release:$sessionId');
    return PlaybackStateMsg(
      schemaVersion: 1,
      sessionId: sessionId,
      mediaToken: 'tok',
      zoom: 1,
      panX: 0,
      panY: 0,
      rotationDeg: 0,
      fitMode: 'ORIGINAL',
      preferredOrientation: 'LANDSCAPE',
      fullscreen: true,
      positionUs: 5000000,
      subtitlesEnabled: false,
    );
  }

  /// Ids the "native host" shared (add-to-app).
  final Set<String> sharedSessions = {};

  @override
  Future<CreateResultMsg> adoptSession(String sessionId) async {
    calls.add('adoptSession:$sessionId');
    if (!sharedSessions.contains(sessionId)) {
      return CreateResultMsg(
        error: StableErrorMsg(
          code: 'SESSION_RELEASED',
          stage: 'BIND',
          retryable: false,
          suggestedAction: 'NONE',
          params: {},
        ),
      );
    }
    return CreateResultMsg(id: sessionId);
  }

  @override
  Future<CreateResultMsg> createEditProject(
    EditProjectConfigMsg config,
  ) async => CreateResultMsg(id: 'project-1');

  @override
  Future<CreateResultMsg> addSource(
    String projectId,
    MediaSourceMsg source,
  ) async => CreateResultMsg(id: 'src-1');

  @override
  Future<EditResultMsg> applyEdit(
    String projectId,
    EditCommandMsg command,
  ) async {
    lastEdit = command;
    return EditResultMsg(
      kind: EditResultKind.applied,
      revision: 3,
      createdId: 'clip-2',
    );
  }

  @override
  Future<ExportResultMsg> exportProject(
    String projectId,
    ExportRequestMsg request,
  ) async {
    calls.add('export:${request.preset}:${request.sinkRef}');
    return exportResult ??
        ExportResultMsg(
          kind: ExportResultKind.failed,
          exportId: request.exportId,
          error: StableErrorMsg(
            code: 'OUTPUT_SPACE_INSUFFICIENT',
            stage: 'SINK',
            retryable: true,
            suggestedAction: 'FREE_SPACE',
            params: {'requiredBytes': '1000'},
          ),
          stage: 'ENCODING',
        );
  }

  @override
  Future<void> closeAll() async => calls.add('closeAll');
}

/// [VideoKitPlatform] over [FakeHostApi] with controllable update streams.
class FakePlatform extends VideoKitPlatform {
  FakePlatform(this.api);

  final FakeHostApi api;
  // ignore: close_sinks, closed with the test isolate
  final StreamController<SessionUpdateMessage> sessions =
      StreamController.broadcast();
  // ignore: close_sinks, closed with the test isolate
  final StreamController<EditUpdateMessage> edits =
      StreamController.broadcast();
  VideoKitCallbacksApi? callbacks;

  @override
  VideoKitHostApi get hostApi => api;

  @override
  Stream<SessionUpdateMessage> sessionUpdates() => sessions.stream;

  @override
  Stream<EditUpdateMessage> editUpdates() => edits.stream;

  @override
  void setCallbacks(VideoKitCallbacksApi? callbacks) =>
      this.callbacks = callbacks;
}

SessionStateMsg stateMsg({
  SessionPhaseMsg phase = SessionPhaseMsg.ready,
  int positionUs = 0,
  bool looping = false,
  ImageDetailsMsg? imageDetails,
  MediaInfoMsg? mediaInfo,
}) => SessionStateMsg(
  phase: phase,
  mediaKind: MediaKindMsg.video,
  positionUs: positionUs,
  durationUs: 120000000,
  playWhenReady: false,
  speed: 1,
  volume: 1,
  muted: false,
  audioTracks: [
    TrackInfoMsg(id: 'a1', language: 'zh', supported: true, channelCount: 6),
  ],
  subtitleTracks: [],
  transform: TransformMsg(
    scale: 1,
    panX: 0,
    panY: 0,
    rotationDeg: 0,
    fitMode: 'FIT',
  ),
  orientation: OrientationStateMsg(
    request: 'AUTO',
    contentOrientation: 'LANDSCAPE',
    fullscreen: false,
  ),
  visibility: 'VISIBLE',
  activeAudio: true,
  controlsVisible: true,
  resourcesHeld: true,
  hostActions: [],
  videoWidth: 1920,
  videoHeight: 1080,
  hiddenForLock: false,
  looping: looping,
  imageDetails: imageDetails,
  mediaInfo: mediaInfo,
);
