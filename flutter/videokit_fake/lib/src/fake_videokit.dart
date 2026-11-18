import 'dart:async';
import 'dart:typed_data';

import 'package:videokit_api/videokit_api.dart';

import 'avatar/fake_avatar.dart';
import 'clock/fake_clock.dart';
import 'fake_edit_project.dart';
import 'fake_session.dart';
import 'host_bridge.dart';
import 'scenario/scenario.dart';

/// Dart Fake `VideoKit` (14 §11.1). [isDemo] is always true; every session
/// and project it creates is a demo object.
///
/// Scenario selection for a bound source, in order: [scenarioOverrides] by
/// media token → a non-`normal` `DemoSourceRef.scenarioId` from
/// [Scenarios.catalog] → [defaultScenario].
class FakeVideoKit implements VideoKit, VideoKitAvatarTools {
  /// Creates a Fake.
  FakeVideoKit({
    FakeClock? clock,
    this.config = const VideoKitConfig(),
    this.defaultScenario = const Scenario.normal(),
    Map<String, Scenario> scenarioOverrides = const {},
    this.maxSessions = 12,
    this.videoDecoderBudget,
    this.editingAvailable = true,
  }) : clock = clock ?? FakeClock(),
       _overrides = Map.of(scenarioOverrides) {
    _host = FakeHostBridge(
      callbacks: config.hostCallbacks,
      timeouts: config.callbackTimeouts,
      clock: this.clock,
    );
  }

  /// Clock driving all Fakes of this instance.
  final FakeClock clock;

  /// TEST-R3 R3-02: false behaves like a native Kit without the edit
  /// engine (before S3): `createEditProject` / `restoreEditProject` throw
  /// `INVALID_STATE` with diagnostic `EDITING_NOT_AVAILABLE` and the
  /// capability report lists no edit features.
  final bool editingAvailable;

  /// Diagnostic of the error thrown when editing is not available.
  static const String editingNotAvailable = 'EDITING_NOT_AVAILABLE';

  void _checkEditing() {
    if (editingAvailable) return;
    throw const VideoKitException(
      VideoKitStableError.invalidState(
        stage: ErrorStage.edit,
        diagnostic: editingNotAvailable,
      ),
    );
  }

  /// Config.
  final VideoKitConfig config;

  /// Feature switches and the host gate (REQ-API-10, VK-A2).
  VideoKitFeatureGate get features => config.featureGate;

  /// Throws `FEATURE_DISABLED` when [feature] is hidden, `FEATURE_DENIED`
  /// when the host's gate says no.
  Future<void> _requireFeature(
    VideoKitFeature feature, {
    ErrorStage stage = ErrorStage.edit,
    String? sessionId,
  }) async {
    if (!features.isEnabled(feature)) {
      throw VideoKitException(
        VideoKitFeatureGate.disabledError(feature, stage: stage),
      );
    }
    final access = await features.check(feature, sessionId: sessionId);
    if (!access.isAllowed) {
      throw VideoKitException(
        VideoKitFeatureGate.deniedError(
          feature,
          badge: access.badge,
          stage: stage,
        ),
      );
    }
  }

  /// Avatar cut-out (REQ-ED-07, optional tools, 04A E6).
  late final FakeAvatarTools avatarTools = FakeAvatarTools(clock);

  @override
  Future<AvatarImage> prepareAvatar(
    VideoKitMediaSource image, {
    AvatarPrepareOptions options = const AvatarPrepareOptions(),
  }) async {
    _checkOpen();
    _checkEditing();
    await _requireFeature(VideoKitFeature.avatar);
    return avatarTools.prepareAvatar(image, options: options);
  }

  @override
  Future<AvatarImage> refineAvatar(
    AvatarImage avatar,
    List<AvatarStroke> strokes, {
    double? feather,
  }) async {
    _checkOpen();
    _checkEditing();
    // Refining one already prepared: only the static switch.
    if (!features.isEnabled(VideoKitFeature.avatar)) {
      throw VideoKitException(
        VideoKitFeatureGate.disabledError(VideoKitFeature.avatar),
      );
    }
    return avatarTools.refineAvatar(avatar, strokes, feather: feather);
  }

  @override
  int get builtinAvatarCount => FakeAvatarTools.builtinCount;

  @override
  Future<Uint8List> builtinAvatar(int index) =>
      avatarTools.builtinAvatar(index);

  /// Fallback scenario.
  Scenario defaultScenario;

  /// Hard session limit (07 §3).
  final int maxSessions;

  /// Video decoders the demo "device" has (M3); null = unlimited. A video
  /// bind beyond it is denied with `DECODER_RESOURCE_EXHAUSTED`.
  final int? videoDecoderBudget;

  /// Test hook: another app takes the system audio focus (04A K2: the
  /// audio source pauses; [transient] sends no notice).
  void preemptAudio({bool transient = false}) {
    for (final s in _sessions.values) {
      s.loseAudioFocus(transient: transient);
    }
  }

  /// Test hook: a transient focus loss ended.
  void regainAudioFocus() {
    for (final s in _sessions.values) {
      s.regainAudioFocus();
    }
  }

  final Map<String, Scenario> _overrides;
  late final FakeHostBridge _host;
  final Map<String, FakeSession> _sessions = {};

  /// Live projects by identity: a restored project keeps its snapshot's
  /// projectId even while another instance with that ID is open (like
  /// Kotlin; vector snapshot.roundtrip).
  final Set<FakeEditProject> _projects = Set.identity();
  int _counter = 0;
  bool _closed = false;

  /// Host bridge (diagnostics: callback failure count).
  FakeHostBridge get hostBridge => _host;

  /// Live sessions.
  Iterable<FakeSession> get sessions => _sessions.values;

  /// Live projects.
  Iterable<FakeEditProject> get projects => _projects;

  /// Sets the scenario for [mediaToken].
  void setScenarioFor(String mediaToken, Scenario scenario) =>
      _overrides[mediaToken] = scenario;

  Scenario _resolve(VideoKitMediaSource source) {
    final byToken = _overrides[source.mediaToken];
    if (byToken != null) return byToken;
    final ref = source.sourceRef;
    if (ref is DemoSourceRef &&
        ref.scenarioId != 'normal' &&
        Scenarios.catalog.containsKey(ref.scenarioId)) {
      return Scenarios.catalog[ref.scenarioId]!;
    }
    return defaultScenario;
  }

  @override
  VideoKitApiVersion get apiVersion => VideoKitApiVersion.current;

  @override
  bool get isDemo => true;

  void _checkOpen() {
    if (_closed) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.bind,
        ),
      );
    }
  }

  @override
  Future<VideoKitCapabilities> capabilities(CapabilityRequest request) async {
    _checkOpen();
    final source = request.source;
    MediaProbeResult? probe;
    if (source != null) {
      final err = _resolve(source).bindError;
      probe = MediaProbeResult(
        playable: err == null,
        fastConcatEligible: err == null && source.mediaKind == MediaKind.video,
        reason: err == null ? null : UnsupportedReason.deviceCapability,
      );
    }
    return demoCapabilities(mediaProbe: probe, editing: editingAvailable);
  }

  /// Synthetic capability report (values are not measured; isDemo = true).
  static VideoKitCapabilities demoCapabilities({
    MediaProbeResult? mediaProbe,
    bool editing = true,
  }) => VideoKitCapabilities(
    // 04A E6 4: the Fake cut-out is always available with editing.
    avatar: editing ? AvatarSupport.available : AvatarSupport.unsupported,
    decoders: DecoderSummary(
      video: const [
        CodecInfo(
          mimeType: 'video/avc',
          hardwareAccelerated: true,
          maxResolution: VideoSize(3840, 2160),
        ),
        CodecInfo(
          mimeType: 'video/hevc',
          hardwareAccelerated: true,
          maxResolution: VideoSize(3840, 2160),
        ),
      ],
      audio: const [CodecInfo(mimeType: 'audio/mp4a-latm')],
    ),
    containerCodecSupport: const [
      FormatSupport(
        container: 'mp4',
        videoCodec: 'video/avc',
        audioCodec: 'audio/mp4a-latm',
        level: SupportLevel.supported,
      ),
      FormatSupport(
        container: 'mkv',
        videoCodec: 'video/hevc',
        level: SupportLevel.partial,
        reason: UnsupportedReason.deviceCapability,
      ),
    ],
    suggestedHardwareVideoSessions: 4,
    maxSuggestedResolution: const VideoSize(3840, 2160),
    maxSuggestedFrameRate: 60,
    playbackFeatures: PlaybackFeatures(
      subtitles: true,
      multipleAudioTracks: true,
      speedControl: true,
      exactSeek: true,
    ),
    imageFeatures: ImageFeatures(
      staticImages: true,
      animatedImages: true,
      largeImageTiling: true,
      formats: const ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    ),
    editFeatures: EditFeatures(
      singleVideoClips: editing,
      multiInputConcat: editing,
      fastConcat: editing,
      masks: editing,
    ),
    encoders: const [
      CodecInfo(mimeType: 'video/avc', hardwareAccelerated: true),
    ],
    outputFormats: const [
      OutputFormat(
        presetId: ExportPresets.original,
        container: 'mp4',
        videoCodec: 'video/avc',
        audioCodec: 'audio/mp4a-latm',
      ),
      OutputFormat(
        presetId: ExportPresets.p1080,
        container: 'mp4',
        videoCodec: 'video/avc',
        audioCodec: 'audio/mp4a-latm',
        maxLongEdge: 1920,
      ),
      OutputFormat(
        presetId: ExportPresets.p720,
        container: 'mp4',
        videoCodec: 'video/avc',
        audioCodec: 'audio/mp4a-latm',
        maxLongEdge: 1280,
      ),
    ],
    tracking: const TrackingStatus(
      face: TrackingModuleStatus.available,
      objectTracking: TrackingModuleStatus.available,
      suggestedResolution: VideoSize(640, 360),
      maxConcurrentTargets: 4,
    ),
    sinkRequirements: const SinkRequirements(sequentialFallback: true),
    mediaProbe: mediaProbe,
    isDemo: true,
  );

  FakeSession _newSession(VideoKitSessionConfig config) {
    _checkOpen();
    final id = 'fake-session-${++_counter}';
    final session = FakeSession(
      sessionId: id,
      clock: clock,
      host: _host,
      scenarioFor: _resolve,
      config: config,
      onReleased: (s) => _sessions.remove(s.sessionId),
      decoderAvailable: (FakeSession me) {
        final budget = videoDecoderBudget;
        if (budget == null) return true;
        final held = _sessions.values
            .where((o) => !identical(o, me) && o.holdsDecoder)
            .length;
        return held < budget;
      },
    );
    _sessions[id] = session;
    return session;
  }

  @override
  Future<VideoKitSession> createSession(VideoKitSessionConfig config) async {
    _checkOpen();
    if (_sessions.length >= maxSessions) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.decoderResourceExhausted,
          stage: ErrorStage.bind,
          suggestedAction: SuggestedAction.none,
          diagnostic: 'session_limit',
        ),
      );
    }
    return _newSession(config);
  }

  FakeEditProject _newProject(EditProjectConfig config, [String? id]) {
    _checkOpen();
    final projectId = id ?? 'fake-project-${++_counter}';
    final project = FakeEditProject(
      projectId: projectId,
      clock: clock,
      config: config,
      scenario: defaultScenario,
      createPreviewSession: () async =>
          _newSession(const VideoKitSessionConfig(debugLabel: 'preview')),
      onReleased: _projects.remove,
      features: features,
    );
    _projects.add(project);
    return project;
  }

  @override
  Future<VideoKitEditProject> createEditProject(
    EditProjectConfig config,
  ) async {
    _checkEditing();
    await _requireFeature(VideoKitFeature.edit);
    return _newProject(config);
  }

  @override
  Future<VideoKitEditProject> restoreEditProject(
    SerializedEditProject serialized,
    EditProjectConfig config,
  ) async {
    _checkOpen();
    _checkEditing();
    await _requireFeature(VideoKitFeature.edit);
    final (projectId, state, maxId, meta) = FakeEditProjectCodec.decodeWithMeta(
      serialized,
    );
    final project = _newProject(config, projectId.isEmpty ? null : projectId)
      ..restoreFrom(state, maxId, meta);
    return project;
  }

  @override
  Future<void> close() async {
    if (_closed) return;
    _closed = true;
    await Future.wait([
      for (final s in _sessions.values.toList()) s.release(),
      for (final p in _projects.toList()) p.close(),
    ]);
  }
}
