import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import 'clock/fake_clock.dart';
import 'demo/demo_data.dart';
import 'fake_session.dart';
import 'scenario/scenario.dart';

/// Undoable part of the project.
@immutable
final class _Model {
  const _Model(this.timeline, this.masks, this.tracking);

  final Timeline timeline;
  final List<MaskTrack> masks;
  final Map<String, TrackingRun> tracking;
}

/// In-memory Fake edit project (14 §11.1): timeline, masks, undo stack,
/// scripted tracking coverage and staged, cancellable export. Never writes
/// files; successful exports are flagged demo (`demo_no_real_file`).
class FakeEditProject implements VideoKitEditProject {
  /// Creates a project in `CREATED`.
  FakeEditProject({
    required this.projectId,
    required this.clock,
    required this.config,
    required this._scenario,
    required this._createPreviewSession,
    this._onReleased,
  });

  @override
  final String projectId;

  /// Clock.
  final FakeClock clock;

  /// Config.
  final EditProjectConfig config;

  final Scenario _scenario;
  final Future<FakeSession> Function() _createPreviewSession;
  final void Function(FakeEditProject project)? _onReleased;

  final ValueNotifier<VideoKitEditState> _state = ValueNotifier(
    VideoKitEditState.initial(),
  );
  final StreamController<VideoKitEditEvent> _events =
      StreamController<VideoKitEditEvent>.broadcast();
  final List<_Model> _undo = [];
  final List<_Model> _redo = [];
  int _idCounter = 0;
  int _pendingProbes = 0;
  Future<FakeSession>? _preview;
  String? _currentExportId;
  bool _cancelRequested = false;
  Completer<void>? _exportDone;

  /// Fake encoding speed relative to real time.
  static const double encodeSpeed = 4.0;

  /// Fake tracking speed relative to real time.
  static const double trackingSpeed = 4.0;

  /// Demo bitrate used for size estimates (video + audio, bits/s).
  static const int demoBitrate = 8000000 + 128000;

  VideoKitEditState get _s => _state.value;

  @override
  ValueListenable<VideoKitEditState> get state => _state;

  @override
  Stream<VideoKitEditEvent> get events => _events.stream;

  @override
  bool get isDemo => true;

  bool get _released => _s.phase.isReleasingOrReleased;

  String _nextId(String prefix) => '$prefix-${++_idCounter}';

  _Model get _model => _Model(_s.timeline, _s.masks, _s.tracking);

  void _set(VideoKitEditState next) {
    if (next != _s) _state.value = next;
  }

  void _emit(VideoKitEditEvent e) {
    if (!_events.isClosed) _events.add(e);
  }

  static VideoKitStableError _illegal(
    String what, [
    ErrorStage stage = ErrorStage.edit,
  ]) => VideoKitStableError(
    code: ErrorCode.internalErrorRedacted,
    stage: stage,
    diagnostic: what,
  );

  EditEstimate _estimate(Timeline t) {
    final d = t.durationUs;
    if (t.clips.isEmpty) return const EditEstimate(durationUs: 0, sizeBytes: 0);
    return EditEstimate(
      durationUs: d,
      sizeBytes: d * demoBitrate ~/ 8 ~/ 1000000,
    );
  }

  // ------------------------------------------------------------- sources --

  @override
  Future<SourceToken> addSource(VideoKitMediaSource source) async {
    if (_released ||
        _s.phase == EditPhase.exporting ||
        _s.phase == EditPhase.cancelling) {
      throw VideoKitException(
        _illegal('illegal_transition:${_s.phase.wireName}:addSource'),
      );
    }
    if (source.mediaKind != MediaKind.video) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.unsupportedContainer,
          stage: ErrorStage.probe,
          suggestedAction: SuggestedAction.chooseOtherSource,
        ),
      );
    }
    _pendingProbes++;
    final before = _s.phase;
    _set(_s.copyWith(phase: EditPhase.preparing));
    await clock.delay(const Duration(milliseconds: 200));
    _pendingProbes--;
    if (_released) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.edit,
        ),
      );
    }
    final profile = DemoDataGenerator.profileFor(source);
    final sourceId = _nextId('src');
    final editSource = EditSource(
      sourceId: sourceId,
      mediaToken: source.mediaToken,
      displayName: source.displayName,
      probe: SourceProbe(
        durationUs: profile.durationUs ?? 0,
        width: profile.size.width,
        height: profile.size.height,
        fps: 30,
        videoCodec: 'video/avc',
        audioCodec: 'audio/mp4a-latm',
        hasAudio: true,
      ),
    );
    final timeline = _s.timeline.copyWith(
      sources: [..._s.timeline.sources, editSource],
    );
    _set(
      _s.copyWith(
        phase: _pendingProbes > 0
            ? EditPhase.preparing
            : (before == EditPhase.tracking
                  ? EditPhase.tracking
                  : EditPhase.ready),
        timeline: timeline,
        estimate: _estimate(timeline),
      ),
    );
    return SourceToken(sourceId: sourceId, mediaToken: source.mediaToken);
  }

  // ------------------------------------------------------------ commands --

  @override
  Future<EditCommandResult> apply(VideoKitEditCommand command) async {
    if (_released) return const EditProjectReleased();
    final phase = _s.phase;
    final duringTracking =
        phase == EditPhase.tracking &&
        (command is CancelTracking ||
            command is SetMaskEnabled ||
            command is SetMaskStyle);
    if (!phase.acceptsEdits && !duringTracking) {
      return EditRejected(_illegal('illegal_transition:${phase.wireName}'));
    }
    final before = _model;
    final String? createdId;
    try {
      createdId = _applyToModel(command);
    } on _Invalid catch (e) {
      return EditRejected(_illegal('invalid_argument:${e.what}'));
    }
    if (command.undoable) {
      _undo.add(before);
      if (_undo.length > config.undoLimit) _undo.removeAt(0);
      _redo.clear();
      _commit(revisionBump: true);
    } else {
      _commit(revisionBump: false);
    }
    return EditApplied(_s.revision, createdId: createdId);
  }

  void _commit({required bool revisionBump}) {
    final finishedExport =
        _s.phase == EditPhase.completed ||
        _s.phase == EditPhase.failed ||
        _s.phase == EditPhase.cancelled;
    _set(
      _s.copyWith(
        revision: revisionBump ? _s.revision + 1 : null,
        canUndo: _undo.isNotEmpty,
        canRedo: _redo.isNotEmpty,
        estimate: _estimate(_s.timeline),
        phase: finishedExport && revisionBump ? EditPhase.ready : null,
        export: finishedExport && revisionBump ? null : _s.export,
        error: revisionBump ? null : _s.error,
      ),
    );
    unawaited(_syncPreview());
  }

  /// Applies [c] to the current state (without revision/undo bookkeeping).
  /// Returns a created ID or null. Throws [_Invalid].
  String? _applyToModel(VideoKitEditCommand c) {
    final tl = _s.timeline;
    final clips = [...tl.clips];
    int clipIndex(String id) {
      final i = clips.indexWhere((x) => x.clipId == id);
      if (i < 0) throw _Invalid('clip_not_found');
      return i;
    }

    MaskTrack mask(String id) =>
        _s.maskById(id) ?? (throw _Invalid('mask_not_found'));
    void checkRect(NormalizedRect r) {
      if (r.width <= 0 ||
          r.height <= 0 ||
          r.left < 0 ||
          r.top < 0 ||
          r.right > 1.0001 ||
          r.bottom > 1.0001) {
        throw _Invalid('region_out_of_range');
      }
    }

    void setMasks(List<MaskTrack> masks) => _set(_s.copyWith(masks: masks));
    List<MaskTrack> replaceMask(MaskTrack m) => [
      for (final x in _s.masks) x.maskId == m.maskId ? m : x,
    ];

    switch (c) {
      case AddClip(:final sourceId, :final inUs, :final outUs, :final index):
        final src =
            tl.sourceById(sourceId) ?? (throw _Invalid('source_not_found'));
        if (inUs < 0 || outUs <= inUs || outUs > src.probe.durationUs) {
          throw _Invalid('clip_range');
        }
        final at = index ?? clips.length;
        if (at < 0 || at > clips.length) throw _Invalid('index');
        final id = _nextId('clip');
        clips.insert(
          at,
          EditClip(clipId: id, sourceId: sourceId, inUs: inUs, outUs: outUs),
        );
        _set(_s.copyWith(timeline: tl.copyWith(clips: clips)));
        return id;
      case SplitAt(:final clipId, :final atUs):
        final i = clipIndex(clipId);
        final start = tl.clipStartUs(clipId)!;
        final clip = clips[i];
        final offset = atUs - start;
        if (offset <= 0 || offset >= clip.durationUs) {
          throw _Invalid('split_point');
        }
        final id = _nextId('clip');
        clips
          ..[i] = clip.copyWith(outUs: clip.inUs + offset)
          ..insert(i + 1, clip.copyWith(clipId: id, inUs: clip.inUs + offset));
        _set(_s.copyWith(timeline: tl.copyWith(clips: clips)));
        return id;
      case TrimClip(:final clipId, :final inUs, :final outUs):
        final i = clipIndex(clipId);
        final src = tl.sourceById(clips[i].sourceId)!;
        if (inUs < 0 || outUs <= inUs || outUs > src.probe.durationUs) {
          throw _Invalid('clip_range');
        }
        clips[i] = clips[i].copyWith(inUs: inUs, outUs: outUs);
        _set(_s.copyWith(timeline: tl.copyWith(clips: clips)));
        return null;
      case RemoveClip(:final clipId):
        clips.removeAt(clipIndex(clipId));
        _set(_s.copyWith(timeline: tl.copyWith(clips: clips)));
        return null;
      case MoveClip(:final clipId, :final toIndex):
        final i = clipIndex(clipId);
        if (toIndex < 0 || toIndex >= clips.length) throw _Invalid('index');
        final clip = clips.removeAt(i);
        clips.insert(toIndex, clip);
        _set(_s.copyWith(timeline: tl.copyWith(clips: clips)));
        return null;
      case AddMask(
        :final type,
        :final region,
        :final startUs,
        :final endUs,
        :final style,
        :final strength,
      ):
        checkRect(region);
        if (startUs < 0 || endUs <= startUs || endUs > tl.durationUs) {
          throw _Invalid('mask_range');
        }
        if (strength < 0 || strength > 1) throw _Invalid('strength');
        final id = _nextId('mask');
        setMasks([
          ..._s.masks,
          MaskTrack(
            maskId: id,
            type: type,
            style: style,
            strength: strength,
            startUs: startUs,
            endUs: endUs,
            keyframes: [MaskKeyframe(atUs: startUs, region: region)],
          ),
        ]);
        return id;
      case UpdateMaskKeyframe(:final maskId, :final atUs, :final region):
        checkRect(region);
        final m = mask(maskId);
        if (atUs < m.startUs || atUs >= m.endUs) {
          throw _Invalid('keyframe_time');
        }
        setMasks(
          replaceMask(
            m.copyWith(
              keyframes: [
                for (final k in m.keyframes)
                  if (k.atUs != atUs) k,
                MaskKeyframe(atUs: atUs, region: region),
              ],
            ),
          ),
        );
        return null;
      case RemoveMaskKeyframe(:final maskId, :final atUs):
        final m = mask(maskId);
        if (!m.keyframes.any((k) => k.atUs == atUs)) {
          throw _Invalid('keyframe_not_found');
        }
        if (m.keyframes.length == 1) throw _Invalid('last_keyframe');
        setMasks(
          replaceMask(
            m.copyWith(
              keyframes: [
                for (final k in m.keyframes)
                  if (k.atUs != atUs) k,
              ],
            ),
          ),
        );
        return null;
      case SetMaskStyle(:final maskId, :final style, :final strength):
        if (strength < 0 || strength > 1) throw _Invalid('strength');
        setMasks(
          replaceMask(mask(maskId).copyWith(style: style, strength: strength)),
        );
        return null;
      case SetMaskEnabled(:final maskId, :final enabled):
        setMasks(replaceMask(mask(maskId).copyWith(enabled: enabled)));
        return null;
      case RemoveMask(:final maskId):
        mask(maskId);
        _cancelRun(maskId, silent: true);
        _set(
          _s.copyWith(
            masks: [
              for (final m in _s.masks)
                if (m.maskId != maskId) m,
            ],
            tracking: {..._s.tracking}..remove(maskId),
          ),
        );
        return null;
      case StartTracking(
        :final maskId,
        :final kind,
        :final atUs,
        :final seedRegion,
      ):
        final m = mask(maskId);
        if (!m.type.isAutomatic) throw _Invalid('mask_not_automatic');
        if (_s.tracking[maskId]?.status == TrackingRunStatus.running) {
          throw _Invalid('already_tracking');
        }
        checkRect(seedRegion);
        if (atUs < m.startUs || atUs >= m.endUs) throw _Invalid('seed_time');
        _startRun(m, kind, fromUs: m.startUs, keepBeforeUs: null);
        return null;
      case CorrectTracking(:final maskId, :final atUs, :final region):
        checkRect(region);
        final m = mask(maskId);
        final run = _s.tracking[maskId];
        if (!m.type.isAutomatic || run == null) throw _Invalid('no_tracking');
        if (atUs < m.startUs || atUs >= m.endUs) {
          throw _Invalid('keyframe_time');
        }
        final corrected = m.copyWith(
          keyframes: [
            for (final k in m.keyframes)
              if (k.atUs < atUs || k.source == KeyframeSource.user)
                if (k.atUs != atUs) k,
            MaskKeyframe(atUs: atUs, region: region),
          ],
        );
        setMasks(replaceMask(corrected));
        _startRun(
          corrected,
          run.kind,
          fromUs: atUs,
          keepBeforeUs: atUs,
          correction: true,
        );
        return null;
      case CancelTracking(:final maskId):
        if (_s.tracking[maskId]?.status != TrackingRunStatus.running) {
          throw _Invalid('not_tracking');
        }
        _cancelRun(maskId);
        return null;
      case AcceptTrackingRange(:final maskId, :final startUs, :final endUs):
        final run = _s.tracking[maskId] ?? (throw _Invalid('no_tracking'));
        var matched = false;
        final segments = [
          for (final seg in run.coverage.segments)
            if (seg.state.blocksExport &&
                seg.startUs >= startUs &&
                seg.endUs <= endUs)
              () {
                matched = true;
                return seg.copyWith(accepted: true);
              }()
            else
              seg,
        ];
        if (!matched) throw _Invalid('no_uncovered_segment');
        _set(
          _s.copyWith(
            tracking: {
              ..._s.tracking,
              maskId: run.copyWith(
                coverage: CoverageReport(segments: segments),
              ),
            },
          ),
        );
        return null;
    }
  }

  // ------------------------------------------------------------ tracking --

  void _startRun(
    MaskTrack m,
    TrackingKind kind, {
    required int fromUs,
    required int? keepBeforeUs,
    bool correction = false,
  }) {
    final requestId = _nextId('track');
    final previous = _s.tracking[m.maskId];
    final kept = <CoverageSegment>[
      if (keepBeforeUs != null && previous != null)
        for (final seg in previous.coverage.segments)
          if (seg.startUs < keepBeforeUs)
            seg.copyWith(endUs: math.min(seg.endUs, keepBeforeUs)),
    ];
    final run = TrackingRun(
      maskId: m.maskId,
      requestId: requestId,
      projectRevision: _s.revision,
      kind: kind,
      status: TrackingRunStatus.running,
      progress: 0,
      coverage: CoverageReport(
        segments: [
          ...kept,
          CoverageSegment(
            startUs: fromUs,
            endUs: m.endUs,
            state: TrackingState.notAnalyzed,
          ),
        ],
      ),
    );
    _set(
      _s.copyWith(
        phase: EditPhase.tracking,
        tracking: {..._s.tracking, m.maskId: run},
      ),
    );
    final totalUs = m.endUs - fromUs;
    final wall = Duration(
      microseconds: math.max(500000, totalUs ~/ trackingSpeed),
    );
    const step = Duration(milliseconds: 250);
    var elapsed = Duration.zero;
    void tick() {
      final cur = _s.tracking[m.maskId];
      // Stale or released: drop the result (09 §3).
      if (_released || cur == null || cur.requestId != requestId) return;
      if (cur.status != TrackingRunStatus.running) return;
      elapsed += step;
      if (elapsed < wall) {
        _set(
          _s.copyWith(
            tracking: {
              ..._s.tracking,
              m.maskId: cur.copyWith(
                progress: elapsed.inMicroseconds / wall.inMicroseconds,
              ),
            },
          ),
        );
        clock.schedule(step, tick);
        return;
      }
      _finishRun(m.maskId, requestId, fromUs, kept, correction: correction);
    }

    clock.schedule(step, tick);
  }

  void _finishRun(
    String maskId,
    String requestId,
    int fromUs,
    List<CoverageSegment> kept, {
    required bool correction,
  }) {
    final m = _s.maskById(maskId);
    final run = _s.tracking[maskId];
    if (m == null || run == null || run.requestId != requestId) return;
    // Scripted LOST ranges (a correction resolves the ones after it).
    final lost = correction
        ? const <TimeRange>[]
        : _scenario.trackingLostRanges;
    final segments = <CoverageSegment>[...kept];
    var t = fromUs;
    final sortedLost = [...lost]..sort((a, b) => a.start.compareTo(b.start));
    for (final r in sortedLost) {
      final ls = math.max(r.start.inMicroseconds, fromUs);
      final le = math.min(r.end.inMicroseconds, m.endUs);
      if (le <= ls || ls < t) continue;
      if (ls > t) {
        segments.add(
          CoverageSegment(startUs: t, endUs: ls, state: TrackingState.tracked),
        );
      }
      segments.add(
        CoverageSegment(startUs: ls, endUs: le, state: TrackingState.lost),
      );
      t = le;
    }
    if (t < m.endUs) {
      segments.add(
        CoverageSegment(
          startUs: t,
          endUs: m.endUs,
          state: TrackingState.tracked,
        ),
      );
    }
    // Tracker keyframes every 500 ms (deterministic drift), user keys win.
    final base = m.regionAt(fromUs) ?? m.keyframes.first.region;
    final userTimes = {
      for (final k in m.keyframes)
        if (k.source == KeyframeSource.user) k.atUs,
    };
    final trackerKeys = <MaskKeyframe>[
      for (var at = fromUs; at < m.endUs; at += 500000)
        if (!userTimes.contains(at))
          MaskKeyframe(
            atUs: at,
            region: base.copyWith(
              left: (base.left + 0.02 * math.sin(at / 1e6)).clamp(
                0.0,
                1.0 - base.width,
              ),
            ),
            source: KeyframeSource.tracker,
            state: CoverageReport(segments: segments).stateAt(at),
          ),
    ];
    final updatedMask = m.copyWith(
      keyframes: [
        for (final k in m.keyframes)
          if (k.source == KeyframeSource.user || k.atUs < fromUs) k,
        ...trackerKeys,
      ],
    );
    final stillRunning = _s.tracking.entries.any(
      (e) => e.key != maskId && e.value.status == TrackingRunStatus.running,
    );
    _set(
      _s.copyWith(
        phase: stillRunning ? EditPhase.tracking : EditPhase.ready,
        masks: [for (final x in _s.masks) x.maskId == maskId ? updatedMask : x],
        tracking: {
          ..._s.tracking,
          maskId: run.copyWith(
            status: TrackingRunStatus.completed,
            progress: 1.0,
            coverage: CoverageReport(segments: segments),
          ),
        },
      ),
    );
    _emit(TrackingFinished(maskId, TrackingRunStatus.completed));
  }

  void _cancelRun(String maskId, {bool silent = false}) {
    final run = _s.tracking[maskId];
    if (run == null || run.status != TrackingRunStatus.running) return;
    final stillRunning = _s.tracking.entries.any(
      (e) => e.key != maskId && e.value.status == TrackingRunStatus.running,
    );
    _set(
      _s.copyWith(
        phase: stillRunning ? EditPhase.tracking : EditPhase.ready,
        tracking: {
          ..._s.tracking,
          maskId: run.copyWith(status: TrackingRunStatus.cancelled),
        },
      ),
    );
    if (!silent) _emit(TrackingFinished(maskId, TrackingRunStatus.cancelled));
  }

  @override
  Future<CandidateDetectionResult> detectCandidates(int atUs) async {
    if (_released) {
      return CandidateDetectionResult(
        error: const VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.tracking,
        ),
      );
    }
    await clock.delay(const Duration(milliseconds: 300));
    final rnd = DemoRandom(stableHash('$projectId:$atUs'));
    return CandidateDetectionResult(
      candidates: [
        for (var i = 0; i < 2; i++)
          TrackingCandidate(
            candidateId: 'face-${i + 1}',
            kind: TrackingKind.face,
            region: NormalizedRect(
              left: 0.15 + i * 0.45 + rnd.nextDouble() * 0.05,
              top: 0.2 + rnd.nextDouble() * 0.1,
              width: 0.18,
              height: 0.24,
            ),
            confidence: 0.8 + rnd.nextDouble() * 0.15,
          ),
      ],
    );
  }

  // ---------------------------------------------------------- undo/redo --

  @override
  Future<EditCommandResult> undo() => _undoRedo(_undo, _redo, 'undo');

  @override
  Future<EditCommandResult> redo() => _undoRedo(_redo, _undo, 'redo');

  Future<EditCommandResult> _undoRedo(
    List<_Model> from,
    List<_Model> to,
    String what,
  ) async {
    if (_released) return const EditProjectReleased();
    if (!_s.phase.acceptsEdits) {
      return EditRejected(
        _illegal('illegal_transition:${_s.phase.wireName}:$what'),
      );
    }
    if (from.isEmpty) return EditRejected(_illegal('${what}_empty'));
    to.add(_model);
    final m = from.removeLast();
    _set(
      _s.copyWith(timeline: m.timeline, masks: m.masks, tracking: m.tracking),
    );
    _commit(revisionBump: true);
    return EditApplied(_s.revision);
  }

  // ------------------------------------------------------------ snapshot --

  @override
  Future<SerializedEditProject> snapshot() async => SerializedEditProject(
    schemaVersion: SerializedEditProject.currentSchemaVersion,
    json: jsonEncode(FakeEditProjectCodec.encode(projectId, _s)),
  );

  /// Restores model state from a decoded snapshot (used by `FakeVideoKit`).
  void restoreFrom(VideoKitEditState decoded, int idCounter) {
    _idCounter = idCounter;
    _set(
      decoded.copyWith(
        phase: EditPhase.ready,
        canUndo: false,
        canRedo: false,
        estimate: _estimate(decoded.timeline),
      ),
    );
  }

  // ------------------------------------------------------------- preview --

  @override
  Future<VideoKitSession> previewSession() => _preview ??= () async {
    final session = await _createPreviewSession();
    await session.bind(
      VideoKitMediaSource(
        mediaToken: 'preview-$projectId',
        mediaKind: MediaKind.video,
        sourceRef: const DemoSourceRef('normal'),
      ),
    );
    session.debugSetDuration(_s.timeline.durationUs);
    return session;
  }();

  Future<void> _syncPreview() async {
    final p = _preview;
    if (p == null) return;
    (await p).debugSetDuration(_s.timeline.durationUs);
  }

  // -------------------------------------------------------------- export --

  @override
  Future<ExportPrecheck> checkExport(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  ) async {
    final issues = <PrecheckIssue>[];
    final tl = _s.timeline;
    if (tl.clips.isEmpty) {
      issues.add(
        const PrecheckIssue(
          kind: PrecheckIssueKind.emptyTimeline,
          error: VideoKitStableError(
            code: ErrorCode.exportFailed,
            stage: ErrorStage.export,
          ),
        ),
      );
    }
    if (!config.allowedPresetIds.contains(request.presetId) ||
        !ExportPresets.all.contains(request.presetId)) {
      issues.add(
        const PrecheckIssue(
          kind: PrecheckIssueKind.presetUnavailable,
          error: VideoKitStableError(
            code: ErrorCode.encoderUnavailable,
            stage: ErrorStage.export,
            suggestedAction: SuggestedAction.reduceQuality,
          ),
        ),
      );
    }
    final caps = sink.capabilities;
    if (!caps.fileDescriptor && !caps.randomWrite && !caps.sequentialWrite) {
      issues.add(
        const PrecheckIssue(
          kind: PrecheckIssueKind.sinkCapabilityUnsupported,
          error: VideoKitStableError(
            code: ErrorCode.outputCapabilityUnsupported,
            stage: ErrorStage.sink,
          ),
        ),
      );
    }
    final estimate = _estimate(tl);
    final free = caps.knownFreeSpaceBytes;
    if (free != null &&
        estimate.sizeBytes != null &&
        free < estimate.sizeBytes!) {
      issues.add(
        const PrecheckIssue(
          kind: PrecheckIssueKind.spaceInsufficient,
          error: VideoKitStableError(
            code: ErrorCode.outputSpaceInsufficient,
            stage: ErrorStage.sink,
            suggestedAction: SuggestedAction.freeSpace,
          ),
        ),
      );
    }
    if (tl.sources.any((s) => s.mismatch)) {
      issues.add(const PrecheckIssue(kind: PrecheckIssueKind.sourceMismatch));
    }
    final uncovered = <UncoveredRange>[];
    for (final m in _s.masks) {
      if (!m.enabled || !m.type.isAutomatic) continue;
      final run = _s.tracking[m.maskId];
      if (run == null) {
        uncovered.add(
          UncoveredRange(
            maskId: m.maskId,
            startUs: m.startUs,
            endUs: m.endUs,
            state: TrackingState.notAnalyzed,
          ),
        );
        continue;
      }
      for (final seg in run.coverage.blockingSegments) {
        uncovered.add(
          UncoveredRange(
            maskId: m.maskId,
            startUs: seg.startUs,
            endUs: seg.endUs,
            state: seg.state,
          ),
        );
      }
    }
    if (uncovered.isNotEmpty) {
      issues.add(
        PrecheckIssue(
          kind: PrecheckIssueKind.trackingCoverageIncomplete,
          blocking: !request.acceptUncoveredTracking,
          error: const VideoKitStableError(
            code: ErrorCode.trackingLost,
            stage: ErrorStage.tracking,
            suggestedAction: SuggestedAction.correctTracking,
          ),
        ),
      );
    }
    return ExportPrecheck(
      issues: issues,
      uncoveredRanges: uncovered,
      estimatedDurationUs: estimate.durationUs,
      estimatedSizeBytes: estimate.sizeBytes,
    );
  }

  @override
  Future<VideoKitExportResult> export(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  ) async {
    final exportId = request.exportId ?? _nextId('export');
    if (_released) {
      return ExportFailed(
        exportId,
        const VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.export,
        ),
      );
    }
    if (!_s.phase.acceptsEdits) {
      return ExportFailed(
        exportId,
        _illegal(
          'illegal_transition:${_s.phase.wireName}:export',
          ErrorStage.export,
        ),
      );
    }
    final precheck = await checkExport(request, sink);
    if (!precheck.canExport) {
      final error =
          precheck.issues.firstWhere((i) => i.blocking).error ??
          const VideoKitStableError(
            code: ErrorCode.exportFailed,
            stage: ErrorStage.export,
          );
      _set(_s.copyWith(phase: EditPhase.failed, error: error, export: null));
      final result = ExportFailed(exportId, error);
      _emit(ExportFinished(result));
      return result;
    }

    _currentExportId = exportId;
    _cancelRequested = false;
    _exportDone = Completer<void>();
    final hasAuto = _s.masks.any((m) => m.enabled && m.type.isAutomatic);
    final stages = <(ExportStage, Duration)>[
      (ExportStage.preparing, const Duration(milliseconds: 500)),
      if (hasAuto) (ExportStage.tracking, const Duration(milliseconds: 500)),
      (
        ExportStage.encoding,
        Duration(
          microseconds: math.max(
            1000000,
            _s.timeline.durationUs ~/ encodeSpeed,
          ),
        ),
      ),
      (ExportStage.verifying, const Duration(milliseconds: 250)),
      (ExportStage.writing, const Duration(milliseconds: 250)),
    ];
    _set(
      _s.copyWith(
        phase: EditPhase.exporting,
        error: null,
        export: ExportProgress(
          exportId: exportId,
          stage: ExportStage.preparing,
        ),
      ),
    );

    VideoKitExportResult result;
    try {
      result = await _runStages(exportId, stages, request, precheck);
    } finally {
      _currentExportId = null;
      _exportDone?.complete();
      _exportDone = null;
    }
    _emit(ExportFinished(result));
    return result;
  }

  Future<VideoKitExportResult> _runStages(
    String exportId,
    List<(ExportStage, Duration)> stages,
    VideoKitExportRequest request,
    ExportPrecheck precheck,
  ) async {
    const step = Duration(milliseconds: 250);
    final totalUs = _s.timeline.durationUs;
    var bytes = 0;
    for (final (stage, length) in stages) {
      var elapsed = Duration.zero;
      while (elapsed < length) {
        final determinate = stage == ExportStage.encoding;
        final fraction = elapsed.inMicroseconds / length.inMicroseconds;
        if (!_cancelRequested && !_released) {
          _set(
            _s.copyWith(
              export: ExportProgress(
                exportId: exportId,
                stage: stage,
                fraction: determinate ? fraction : null,
                processedUs: determinate ? (totalUs * fraction).round() : null,
                outputBytes: determinate ? bytes : null,
                remainingUs: determinate
                    ? (length - elapsed).inMicroseconds
                    : null,
              ),
            ),
          );
        }
        await clock.delay(step);
        elapsed += step;
        if (determinate) {
          bytes =
              ((precheck.estimatedSizeBytes ?? 0) *
                      math.min(
                        1.0,
                        elapsed.inMicroseconds / length.inMicroseconds,
                      ))
                  .round();
        }
        if (_cancelRequested || _released) return _finishCancel(exportId);
        final failure = _scenario.exportFailure;
        if (failure != null &&
            failure.stage == stage &&
            elapsed * 2 >= length) {
          final error = VideoKitStableError(
            code: failure.code,
            stage: stage == ExportStage.writing
                ? ErrorStage.sink
                : ErrorStage.export,
            retryable: failure.code != ErrorCode.outputPermissionDenied,
            suggestedAction: switch (failure.code) {
              ErrorCode.outputSpaceInsufficient => SuggestedAction.freeSpace,
              ErrorCode.encoderUnavailable => SuggestedAction.reduceQuality,
              ErrorCode.outputPermissionDenied =>
                SuggestedAction.grantPermission,
              _ => SuggestedAction.retry,
            },
          );
          _set(
            _s.copyWith(phase: EditPhase.failed, error: error, export: null),
          );
          return ExportFailed(exportId, error, stage: stage);
        }
      }
    }
    final first = _s.timeline.sources.isEmpty
        ? null
        : _s.timeline.sources.first;
    final media = VideoKitExportedMedia(
      outputToken: 'demo-output-$exportId',
      container: 'mp4',
      extension: 'mp4',
      videoCodec: 'video/avc',
      audioCodec: 'audio/mp4a-latm',
      width: first?.probe.width ?? 1920,
      height: first?.probe.height ?? 1080,
      orientation: (first?.probe.height ?? 0) > (first?.probe.width ?? 1)
          ? MediaOrientation.portrait
          : MediaOrientation.landscape,
      durationUs: totalUs,
      sizeBytes: precheck.estimatedSizeBytes ?? 0,
      frameRate: 30,
      audioPresent: true,
      createdAt: DateTime.utc(2026, 1, 1).add(clock.now),
      sourceTokens: [for (final s in _s.timeline.sources) s.mediaToken],
      editProjectId: projectId,
      exportPresetId: request.presetId,
      warnings: [
        ExportWarnings.demoNoRealFile,
        if (precheck.uncoveredRanges.isNotEmpty || _hasAcceptedRanges())
          ExportWarnings.trackingCoverageAccepted,
      ],
      isDemo: true,
    );
    _set(_s.copyWith(phase: EditPhase.completed, export: null));
    return ExportSucceeded(exportId, media);
  }

  bool _hasAcceptedRanges() =>
      _s.tracking.values.any((r) => r.coverage.segments.any((s) => s.accepted));

  Future<VideoKitExportResult> _finishCancel(String exportId) async {
    if (!_released) {
      await clock.delay(
        _scenario.exportCancelSlow
            ? const Duration(seconds: 2)
            : const Duration(milliseconds: 250),
      );
    }
    if (!_released) _set(_s.copyWith(phase: EditPhase.cancelled, export: null));
    return ExportCancelled(exportId);
  }

  @override
  Future<void> cancelExport(String exportId) async {
    if (_currentExportId != exportId || _cancelRequested) return;
    _cancelRequested = true;
    final progress = _s.export;
    _set(
      _s.copyWith(
        phase: EditPhase.cancelling,
        export: progress?.copyWith(cancellable: false),
      ),
    );
  }

  // ------------------------------------------------------------- release --

  Future<void>? _closing;

  @override
  Future<void> close() => _closing ??= () async {
    final wasExporting = _currentExportId != null;
    _set(_s.copyWith(phase: EditPhase.releasing));
    for (final id in _s.tracking.keys.toList()) {
      _cancelRun(id, silent: true);
    }
    _set(_s.copyWith(phase: EditPhase.releasing));
    final preview = _preview;
    if (preview != null) await (await preview).release();
    if (wasExporting) await _exportDone?.future;
    _set(_s.copyWith(phase: EditPhase.released, export: null));
    await _events.close();
    _onReleased?.call(this);
  }();
}

final class _Invalid implements Exception {
  _Invalid(this.what);
  final String what;
}

/// JSON codec of the edit project schema (08 §2.1).
abstract final class FakeEditProjectCodec {
  /// Encodes [state] of [projectId].
  static Map<String, Object?> encode(
    String projectId,
    VideoKitEditState state,
  ) => {
    'schemaVersion': SerializedEditProject.currentSchemaVersion,
    'projectId': projectId,
    'revision': state.revision,
    'sources': [
      for (final s in state.timeline.sources)
        {
          'sourceId': s.sourceId,
          'mediaToken': s.mediaToken,
          'displayName': s.displayName,
          'probe': {
            'durationUs': s.probe.durationUs,
            'width': s.probe.width,
            'height': s.probe.height,
            'rotation': s.probe.rotationDeg,
            'fps': s.probe.fps,
            'videoCodec': s.probe.videoCodec,
            'audioCodec': s.probe.audioCodec,
            'hasAudio': s.probe.hasAudio,
          },
        },
    ],
    'timeline': {
      'clips': [
        for (final c in state.timeline.clips)
          {
            'clipId': c.clipId,
            'sourceId': c.sourceId,
            'inUs': c.inUs,
            'outUs': c.outUs,
          },
      ],
    },
    'masks': [
      for (final m in state.masks)
        {
          'maskId': m.maskId,
          'type': m.type.wireName,
          'style': m.style.wireName,
          'strength': m.strength,
          'enabled': m.enabled,
          'rangeUs': [m.startUs, m.endUs],
          'keyframes': [
            for (final k in m.keyframes)
              {
                'atUs': k.atUs,
                'region': _rect(k.region),
                'source': k.source.wireName,
                'state': k.state?.wireName,
              },
          ],
        },
    ],
    'tracking': [
      for (final e in state.tracking.entries)
        {
          'maskId': e.key,
          'requestId': e.value.requestId,
          'projectRevision': e.value.projectRevision,
          'kind': e.value.kind.wireName,
          'progress': e.value.progress,
          // A running task cannot survive a snapshot; restore as cancelled.
          'status':
              (e.value.status == TrackingRunStatus.running
                      ? TrackingRunStatus.cancelled
                      : e.value.status)
                  .wireName,
          'coverage': [
            for (final s in e.value.coverage.segments)
              {
                'startUs': s.startUs,
                'endUs': s.endUs,
                'state': s.state.wireName,
                'accepted': s.accepted,
              },
          ],
        },
    ],
  };

  static Map<String, Object?> _rect(NormalizedRect r) => {
    'left': r.left,
    'top': r.top,
    'width': r.width,
    'height': r.height,
    'rotation': r.rotationDeg,
  };

  static double _d(Object? v, [double fallback = 0]) =>
      v is num ? v.toDouble() : fallback;

  static NormalizedRect _decodeRect(Map<String, Object?> j) => NormalizedRect(
    left: _d(j['left']),
    top: _d(j['top']),
    width: _d(j['width']),
    height: _d(j['height']),
    rotationDeg: _d(j['rotation']),
  );

  static List<Map<String, Object?>> _list(Object? v) => [
    if (v is List)
      for (final e in v)
        if (e is Map) e.cast<String, Object?>(),
  ];

  /// Decodes [serialized]. Throws [VideoKitException] for an unknown future
  /// major version or malformed data (04 §10).
  static (String projectId, VideoKitEditState state, int maxId) decode(
    SerializedEditProject serialized,
  ) {
    VideoKitException reject(String why) => VideoKitException(
      VideoKitStableError(
        code: ErrorCode.internalErrorRedacted,
        stage: ErrorStage.edit,
        diagnostic: why,
      ),
    );
    if (serialized.schemaVersion > SerializedEditProject.currentSchemaVersion ||
        serialized.schemaVersion < 1) {
      throw reject('edit_schema_unsupported');
    }
    final Object? raw;
    try {
      raw = jsonDecode(serialized.json);
    } on FormatException {
      throw reject('edit_snapshot_malformed');
    }
    if (raw is! Map) throw reject('edit_snapshot_malformed');
    final j = raw.cast<String, Object?>();
    final version = j['schemaVersion'];
    if (version is int &&
        version > SerializedEditProject.currentSchemaVersion) {
      throw reject('edit_schema_unsupported');
    }
    var maxId = 0;
    void noteId(String id) {
      final n = int.tryParse(id.split('-').last);
      if (n != null && n > maxId) maxId = n;
    }

    final sources = [
      for (final s in _list(j['sources']))
        () {
          final p = (s['probe'] as Map?)?.cast<String, Object?>() ?? const {};
          final id = s['sourceId'] as String? ?? 'src-0';
          noteId(id);
          return EditSource(
            sourceId: id,
            mediaToken: s['mediaToken'] as String? ?? '',
            displayName: s['displayName'] as String?,
            probe: SourceProbe(
              durationUs: (p['durationUs'] as int?) ?? 0,
              width: (p['width'] as int?) ?? 0,
              height: (p['height'] as int?) ?? 0,
              rotationDeg: (p['rotation'] as int?) ?? 0,
              fps: p['fps'] is num ? (p['fps']! as num).toDouble() : null,
              videoCodec: p['videoCodec'] as String? ?? '',
              audioCodec: p['audioCodec'] as String?,
              hasAudio: (p['hasAudio'] as bool?) ?? false,
            ),
          );
        }(),
    ];
    final timelineJson =
        (j['timeline'] as Map?)?.cast<String, Object?>() ?? const {};
    final clips = [
      for (final c in _list(timelineJson['clips']))
        () {
          final id = c['clipId'] as String? ?? 'clip-0';
          noteId(id);
          return EditClip(
            clipId: id,
            sourceId: c['sourceId'] as String? ?? '',
            inUs: (c['inUs'] as int?) ?? 0,
            outUs: (c['outUs'] as int?) ?? 0,
          );
        }(),
    ];
    final masks = [
      for (final m in _list(j['masks']))
        () {
          final range = (m['rangeUs'] as List?)?.cast<int>() ?? const [0, 0];
          final id = m['maskId'] as String? ?? 'mask-0';
          noteId(id);
          return MaskTrack(
            maskId: id,
            type: MaskType.fromName(m['type'] as String?),
            style: MaskStyle.fromName(m['style'] as String?),
            strength: _d(m['strength'], 0.5),
            enabled: (m['enabled'] as bool?) ?? true,
            startUs: range.isNotEmpty ? range[0] : 0,
            endUs: range.length > 1 ? range[1] : 0,
            keyframes: [
              for (final k in _list(m['keyframes']))
                MaskKeyframe(
                  atUs: (k['atUs'] as int?) ?? 0,
                  region: _decodeRect(
                    (k['region'] as Map?)?.cast<String, Object?>() ?? const {},
                  ),
                  source: KeyframeSource.fromName(k['source'] as String?),
                  state: k['state'] == null
                      ? null
                      : TrackingState.fromName(k['state'] as String?),
                ),
            ],
          );
        }(),
    ];
    final tracking = <String, TrackingRun>{
      for (final t in _list(j['tracking']))
        (t['maskId'] as String? ?? ''): TrackingRun(
          maskId: t['maskId'] as String? ?? '',
          requestId: t['requestId'] as String? ?? '',
          projectRevision: (t['projectRevision'] as int?) ?? 0,
          kind: TrackingKind.fromName(t['kind'] as String?),
          status: TrackingRunStatus.fromName(t['status'] as String?),
          progress: t['progress'] is num
              ? (t['progress']! as num).toDouble()
              : null,
          coverage: CoverageReport(
            segments: [
              for (final s in _list(t['coverage']))
                CoverageSegment(
                  startUs: (s['startUs'] as int?) ?? 0,
                  endUs: (s['endUs'] as int?) ?? 0,
                  state: TrackingState.fromName(s['state'] as String?),
                  accepted: (s['accepted'] as bool?) ?? false,
                ),
            ],
          ),
        ),
    };
    for (final r in tracking.values) {
      noteId(r.requestId);
    }
    final state = VideoKitEditState(
      phase: EditPhase.ready,
      revision: (j['revision'] as int?) ?? 0,
      timeline: Timeline(sources: sources, clips: clips),
      masks: masks,
      tracking: tracking,
    );
    return (j['projectId'] as String? ?? '', state, maxId);
  }
}
