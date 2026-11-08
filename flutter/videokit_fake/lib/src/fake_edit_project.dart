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

  int _nowMs() =>
      DateTime.utc(2026, 1, 1).add(clock.now).millisecondsSinceEpoch;

  /// Snapshot metadata (08 §2.1, 04A E2): created / last changed (epoch
  /// ms on the Fake clock) and the preset last exported with.
  late FakeSnapshotMeta meta = FakeSnapshotMeta(
    createdAtMs: _nowMs(),
    updatedAtMs: _nowMs(),
  );

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
  ]) => VideoKitStableError.invalidState(stage: stage, diagnostic: what);

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
    if (_released) {
      throw const VideoKitException(
        VideoKitStableError(
          code: ErrorCode.sessionReleased,
          stage: ErrorStage.edit,
        ),
      );
    }
    if (_s.phase == EditPhase.exporting || _s.phase == EditPhase.cancelling) {
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
    // CREATED accepts commands too: they fail argument validation (no
    // sources / empty timeline), vector empty.add_clip_unknown_source.
    if (!phase.acceptsEdits && phase != EditPhase.created && !duringTracking) {
      return EditRejected(_illegal('illegal_transition:${phase.wireName}'));
    }
    final before = _model;
    final String? createdId;
    try {
      createdId = _applyToModel(command);
    } on _IllegalState catch (e) {
      return EditRejected(_illegal('illegal_transition:${e.what}'));
    } on _Invalid catch (e) {
      return EditRejected(
        VideoKitStableError.invalidArgument(
          stage: ErrorStage.edit,
          diagnostic: 'invalid_argument:${e.what}',
          params: {'argument': e.what},
        ),
      );
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
    if (revisionBump) {
      meta = FakeSnapshotMeta(
        createdAtMs: meta.createdAtMs,
        updatedAtMs: _nowMs(),
        exportPresetId: meta.exportPresetId,
      );
    }
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
    void checkRect(MaskRegion r) {
      if (r.width <= 0 ||
          r.height <= 0 ||
          r.x < 0 ||
          r.y < 0 ||
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
        // A source restored without probe data (04A E4) has no known
        // length: clips on it are refused until it is probed.
        final length =
            src.probe?.durationUs ?? (throw _Invalid('source_not_probed'));
        if (inUs < 0 || outUs <= inUs || outUs > length) {
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
        final length =
            src.probe?.durationUs ?? (throw _Invalid('source_not_probed'));
        if (inUs < 0 || outUs <= inUs || outUs > length) {
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
      case StartTracking(:final maskId, :final kind, :final seedRegion):
        final m = mask(maskId);
        if (!m.type.isAutomatic) throw _Invalid('mask_not_automatic');
        if (_s.tracking[maskId]?.status == TrackingRunStatus.running) {
          throw _Invalid('already_tracking');
        }
        if (seedRegion != null) checkRect(seedRegion);
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
          throw _IllegalState('not_tracking');
        }
        _cancelRun(maskId);
        return null;
      case AcceptTrackingRange(:final maskId, :final startUs, :final endUs):
        final m = mask(maskId);
        if (!m.type.isAutomatic) throw _Invalid('mask_not_automatic');
        if (startUs < m.startUs || endUs > m.endUs || endUs <= startUs) {
          throw _Invalid('accept_range');
        }
        final run =
            _s.tracking[maskId] ??
            TrackingRun(
              maskId: maskId,
              requestId: _nextId('track'),
              projectRevision: _s.revision,
              kind: m.type == MaskType.object
                  ? TrackingKind.object
                  : TrackingKind.face,
              status: TrackingRunStatus.cancelled,
              coverage: CoverageReport(
                segments: [
                  CoverageRange(
                    startUs: m.startUs,
                    endUs: m.endUs,
                    state: TrackingState.notAnalyzed,
                  ),
                ],
              ),
            );
        var matched = false;
        final segments = <CoverageRange>[];
        for (final seg in run.coverage.segments) {
          final lo = math.max(seg.startUs, startUs);
          final hi = math.min(seg.endUs, endUs);
          if (!seg.state.blocksExport || seg.accepted || hi <= lo) {
            segments.add(seg);
            continue;
          }
          matched = true;
          if (seg.startUs < lo) segments.add(seg.copyWith(endUs: lo));
          segments.add(seg.copyWith(startUs: lo, endUs: hi, accepted: true));
          if (hi < seg.endUs) segments.add(seg.copyWith(startUs: hi));
        }
        if (!matched) throw _Invalid('no_uncovered_segment');
        // 04A E2/E4: the accepted range belongs to the mask; coverage
        // `accepted` is derived from it.
        _set(
          _s.copyWith(
            masks: replaceMask(
              m.copyWith(
                acceptedRanges: [
                  ...m.acceptedRanges,
                  TimeRangeUs(startUs, endUs),
                ]..sort((a, b) => a.startUs.compareTo(b.startUs)),
              ),
            ),
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
    final kept = <CoverageRange>[
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
        segments: _derivedAccepted(m, [
          ...kept,
          CoverageRange(
            startUs: fromUs,
            endUs: m.endUs,
            state: TrackingState.notAnalyzed,
          ),
        ]),
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

  /// Coverage `accepted` derived from the mask's accepted ranges (04A E4;
  /// Kotlin keeps acceptance on the mask across re-tracking).
  static List<CoverageRange> _derivedAccepted(
    MaskTrack m,
    List<CoverageRange> segments,
  ) => [
    for (final s in segments)
      s.copyWith(accepted: m.isAccepted(s.startUs, s.endUs)),
  ];

  void _finishRun(
    String maskId,
    String requestId,
    int fromUs,
    List<CoverageRange> kept, {
    required bool correction,
  }) {
    final m = _s.maskById(maskId);
    final run = _s.tracking[maskId];
    if (m == null || run == null || run.requestId != requestId) return;
    // Scripted LOST ranges (a correction resolves the ones after it).
    final lost = correction
        ? const <TimeRange>[]
        : _scenario.trackingLostRanges;
    final segments = <CoverageRange>[...kept];
    var t = fromUs;
    final sortedLost = [...lost]..sort((a, b) => a.start.compareTo(b.start));
    for (final r in sortedLost) {
      final ls = math.max(r.start.inMicroseconds, fromUs);
      final le = math.min(r.end.inMicroseconds, m.endUs);
      if (le <= ls || ls < t) continue;
      if (ls > t) {
        segments.add(
          CoverageRange(startUs: t, endUs: ls, state: TrackingState.tracked),
        );
      }
      segments.add(
        CoverageRange(startUs: ls, endUs: le, state: TrackingState.lost),
      );
      t = le;
    }
    if (t < m.endUs) {
      segments.add(
        CoverageRange(startUs: t, endUs: m.endUs, state: TrackingState.tracked),
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
              x: (base.x + 0.02 * math.sin(at / 1e6)).clamp(
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
            coverage: CoverageReport(
              segments: _derivedAccepted(updatedMask, segments),
            ),
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
    if (atUs < 0 || atUs >= _s.timeline.durationUs) {
      return CandidateDetectionResult(
        error: VideoKitStableError.invalidArgument(
          stage: ErrorStage.tracking,
          diagnostic: 'invalid_argument:atUs',
          params: const {'argument': 'atUs'},
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
            region: MaskRegion(
              x: 0.15 + i * 0.45 + rnd.nextDouble() * 0.05,
              y: 0.2 + rnd.nextDouble() * 0.1,
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
    json: jsonEncode(FakeEditProjectCodec.encode(projectId, _s, meta: meta)),
  );

  /// Restores model state from a decoded snapshot (used by `FakeVideoKit`).
  void restoreFrom(
    VideoKitEditState decoded,
    int idCounter, [
    FakeSnapshotMeta? restoredMeta,
  ]) {
    _idCounter = idCounter;
    if (restoredMeta != null) meta = restoredMeta;
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
    // Problems are stable errors (code + params) and block the export;
    // warnings are recorded in the result (04A S2).
    final problems = <VideoKitStableError>[];
    final warnings = <String>[];
    final tl = _s.timeline;
    if (tl.clips.isEmpty) {
      problems.add(
        const VideoKitStableError(
          code: ErrorCode.exportFailed,
          stage: ErrorStage.export,
          params: {'reason': 'emptyTimeline'},
        ),
      );
    }
    if (!config.allowedPresetIds.contains(request.presetId) ||
        !ExportPresets.all.contains(request.presetId)) {
      problems.add(
        VideoKitStableError(
          code: ErrorCode.encoderUnavailable,
          stage: ErrorStage.export,
          suggestedAction: SuggestedAction.reduceQuality,
          params: {'presetId': request.presetId},
        ),
      );
    }
    final caps = sink.capabilities;
    final SinkWriteMode? mode = caps.fileDescriptor
        ? SinkWriteMode.fileDescriptor
        : caps.randomWrite
        ? SinkWriteMode.randomWrite
        : caps.sequentialWrite
        ? SinkWriteMode.sequential
        : null;
    if (mode == null) {
      problems.add(
        const VideoKitStableError(
          code: ErrorCode.outputCapabilityUnsupported,
          stage: ErrorStage.sink,
        ),
      );
    }
    // M4: the engine may refuse fast concatenation (scenario); the path
    // falls back to a transcode and the UI explains why.
    if (_scenario.fastConcatRejected && tl.sources.length > 1) {
      warnings.add(ExportWarnings.fastConcatRejected);
    }
    final estimate = _estimate(tl);
    final free = caps.knownFreeSpaceBytes;
    if (free != null &&
        estimate.sizeBytes != null &&
        free < estimate.sizeBytes!) {
      problems.add(
        VideoKitStableError(
          code: ErrorCode.outputSpaceInsufficient,
          stage: ErrorStage.sink,
          retryable: true,
          suggestedAction: SuggestedAction.freeSpace,
          // J8 (spec/errors.json): the shortfall, estimate minus free.
          params: {'requiredBytes': '${estimate.sizeBytes! - free}'},
        ),
      );
    }
    if (tl.sources.any((s) => s.mismatch)) {
      problems.add(
        const VideoKitStableError.invalidState(
          stage: ErrorStage.edit,
          diagnostic: 'source_mismatch',
          params: {'reason': 'sourceMismatch'},
        ),
      );
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
      if (request.acceptUncoveredTracking) {
        warnings.add(ExportWarnings.trackingCoverageAccepted);
      } else {
        problems.add(
          VideoKitStableError(
            code: ErrorCode.trackingLost,
            stage: ErrorStage.tracking,
            retryable: true,
            suggestedAction: SuggestedAction.correctTracking,
            params: {'uncoveredRanges': '${uncovered.length}'},
          ),
        );
      }
    } else if (_hasAcceptedRanges()) {
      warnings.add(ExportWarnings.trackingCoverageAccepted);
    }
    return ExportPrecheck(
      problems: problems,
      warnings: warnings,
      writeMode: problems.isEmpty ? mode : null,
      estimate: estimate,
      uncoveredRanges: uncovered,
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
          precheck.problems.firstOrNull ??
          const VideoKitStableError(
            code: ErrorCode.exportFailed,
            stage: ErrorStage.export,
          );
      // Precheck failures do not start an export: phase is unchanged
      // (vector export.empty_timeline.failed).
      _set(_s.copyWith(error: error, export: null));
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
              ((precheck.estimate.sizeBytes ?? 0) *
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
                SuggestedAction.checkPermission,
              _ => SuggestedAction.retry,
            },
            // J8: a sink running out of space mid-write reports the
            // shortfall (here: the half not yet written).
            params: failure.code == ErrorCode.outputSpaceInsufficient
                ? {
                    'requiredBytes':
                        '${math.max(1, (_estimate(_s.timeline).sizeBytes ?? 0) ~/ 2)}',
                  }
                : const {},
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
      width: first?.probe?.width ?? 1920,
      height: first?.probe?.height ?? 1080,
      orientation: (first?.probe?.height ?? 0) > (first?.probe?.width ?? 1)
          ? MediaOrientation.portrait
          : MediaOrientation.landscape,
      durationUs: totalUs,
      sizeBytes: precheck.estimate.sizeBytes ?? 0,
      frameRate: 30,
      audioPresent: true,
      createdAt: DateTime.utc(2026, 1, 1).add(clock.now),
      sourceTokens: [for (final s in _s.timeline.sources) s.mediaToken],
      editProjectId: projectId,
      exportPresetId: request.presetId,
      warnings: [ExportWarnings.demoNoRealFile, ...precheck.warnings],
      isDemo: true,
    );
    // 08 §2.1: the snapshot remembers the preset last exported with.
    meta = FakeSnapshotMeta(
      createdAtMs: meta.createdAtMs,
      updatedAtMs: meta.updatedAtMs,
      exportPresetId: request.presetId,
    );
    _set(_s.copyWith(phase: EditPhase.completed, export: null));
    return ExportSucceeded(exportId, media);
  }

  bool _hasAcceptedRanges() => _s.masks.any((m) => m.acceptedRanges.isNotEmpty);

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

final class _IllegalState implements Exception {
  _IllegalState(this.what);
  final String what;
}

/// Snapshot metadata kept beside the model (08 §2.1, 04A E2).
@immutable
final class FakeSnapshotMeta {
  /// Creates metadata.
  const FakeSnapshotMeta({
    required this.createdAtMs,
    required this.updatedAtMs,
    this.exportPresetId,
  });

  /// Creation time (epoch ms).
  final int createdAtMs;

  /// Last change (epoch ms).
  final int updatedAtMs;

  /// Preset last used for an export, if any.
  final String? exportPresetId;
}

/// One migration step: the JSON of schema `v` to that of `v + 1`.
typedef FakeSnapshotMigration = Map<String, Object?> Function(
  Map<String, Object?> json,
);

/// JSON codec of the edit project snapshot, schema v1 as frozen by 04A E2
/// (08 §2.1). The single source is `spec/schema/edit-project.v1.json`
/// (Coder B, M4-B1); this codec is checked against it once it lands.
///
/// * top level: `schemaVersion`, `projectId`, `revision`, `createdAt`,
///   `updatedAt` (epoch ms), `exportPresetId` (nullable), `sources`,
///   `timeline.clips`, `masks`, `tracking`;
/// * every time range is an object `{startUs, endUs}` (E2 4);
/// * accepted tracking ranges belong to the mask: `acceptedRanges` (E2 2);
/// * a tracking entry keeps only `{maskId, status, coverage: [{startUs,
///   endUs, quality}]}` (E2 3); request ID, revision, kind and progress
///   are runtime state and are rebuilt on restore;
/// * keyframe `state` and coverage `quality` share one enum (E2 5);
/// * missing optional fields read as defaults; a higher major version is
///   rejected; older versions run through [migrations] (E2 6).
abstract final class FakeEditProjectCodec {
  /// Steps from older schema versions to the next one. v1 is the first
  /// frozen version; v0 is the synthetic pre-freeze form (ranges as
  /// arrays, `accepted` flags on coverage, coverage `state`), kept so the
  /// framework is tested (04A E2 6).
  static final Map<int, FakeSnapshotMigration> migrations = {0: migrateV0ToV1};

  /// Minor version written beside the major `schemaVersion` (04A E2 (b)):
  /// any minor of the same major is readable; unknown fields are ignored.
  static const int currentSchemaMinor = 0;

  /// Encodes [state] of [projectId].
  static Map<String, Object?> encode(
    String projectId,
    VideoKitEditState state, {
    FakeSnapshotMeta meta = const FakeSnapshotMeta(
      createdAtMs: 0,
      updatedAtMs: 0,
    ),
  }) {
    Map<String, Object?> range(int s, int e) => {'startUs': s, 'endUs': e};
    return {
      'schemaVersion': SerializedEditProject.currentSchemaVersion,
      'schemaMinor': currentSchemaMinor,
      'projectId': projectId,
      'revision': state.revision,
      'createdAt': meta.createdAtMs,
      'updatedAt': meta.updatedAtMs,
      'exportPresetId': meta.exportPresetId,
      'sources': [
        for (final s in state.timeline.sources)
          {
            'sourceId': s.sourceId,
            'mediaToken': s.mediaToken,
            'displayName': s.displayName,
            'probe': switch (s.probe) {
              null => null,
              final p => {
                'durationUs': p.durationUs,
                'width': p.width,
                'height': p.height,
                'rotation': p.rotationDeg,
                'fps': p.fps,
                'videoCodec': p.videoCodec,
                'audioCodec': p.audioCodec,
                'hasAudio': p.hasAudio,
              },
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
            'rangeUs': range(m.startUs, m.endUs),
            'keyframes': [
              for (final k in m.keyframes)
                {
                  'atUs': k.atUs,
                  'region': _rect(k.region),
                  'source': k.source.wireName,
                  'state': k.state?.wireName,
                },
            ],
            'acceptedRanges': [
              for (final r in m.acceptedRanges) range(r.startUs, r.endUs),
            ],
          },
      ],
      'tracking': [
        for (final e in state.tracking.entries)
          {
            'maskId': e.key,
            // A running task cannot survive a snapshot: restore as
            // cancelled.
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
                  'quality': s.state.wireName,
                },
            ],
          },
      ],
    };
  }

  /// v0 (pre-freeze) to v1: ranges as objects, `accepted` flags moved to
  /// the mask, coverage `state` renamed `quality`, runtime tracking fields
  /// dropped, timestamps added as 0.
  static Map<String, Object?> migrateV0ToV1(Map<String, Object?> v0) {
    Object? range(Object? r) =>
        r is List && r.length == 2 ? {'startUs': r[0], 'endUs': r[1]} : r;
    final accepted = <String, List<Map<String, Object?>>>{};
    final tracking = [
      for (final t in _list(v0['tracking']))
        {
          'maskId': t['maskId'],
          'status': t['status'],
          'coverage': [
            for (final s in _list(t['coverage']))
              () {
                if (s['accepted'] == true) {
                  (accepted[t['maskId'] as String? ?? ''] ??= []).add({
                    'startUs': s['startUs'],
                    'endUs': s['endUs'],
                  });
                }
                return {
                  'startUs': s['startUs'],
                  'endUs': s['endUs'],
                  'quality': s['quality'] ?? s['state'],
                };
              }(),
          ],
        },
    ];
    return {
      ...v0,
      'schemaVersion': 1,
      'schemaMinor': 0,
      'createdAt': v0['createdAt'] ?? 0,
      'updatedAt': v0['updatedAt'] ?? 0,
      'masks': [
        for (final m in _list(v0['masks']))
          {
            ...m,
            'rangeUs': range(m['rangeUs']),
            'acceptedRanges': [
              if (m['acceptedRanges'] case final List<Object?> items)
                for (final r in items) range(r),
              ...?accepted[m['maskId']],
            ],
          },
      ],
      'tracking': tracking,
    };
  }

  static Map<String, Object?> _rect(MaskRegion r) => {
    'x': r.x,
    'y': r.y,
    'width': r.width,
    'height': r.height,
    'rotation': r.rotationDeg,
  };

  static List<Map<String, Object?>> _list(Object? v) => [
    if (v is List)
      for (final e in v)
        if (e is Map) e.cast<String, Object?>(),
  ];

  /// Decodes [serialized] (spec/schema/edit-project.v1.json, 04A E2).
  ///
  /// * R1: the payload's `schemaVersion` wins over the envelope's; a major
  ///   above the reader's (payload or envelope) is rejected with
  ///   `UNSUPPORTED_SNAPSHOT_VERSION`; a lower one is migrated step by
  ///   step, and one without a migration path is rejected likewise;
  /// * R2: any `schemaMinor`; unknown properties are ignored;
  /// * R3: missing optional properties read as their defaults; a missing
  ///   required property, a wrong type, or text that is not a JSON object
  ///   is rejected with `INVALID_ARGUMENT` (diagnostics never carry
  ///   snapshot content);
  /// * R4: unknown enum values read as the schema's `x-unknown`;
  /// * R5: no undo history; the revision is the snapshot's; new ids
  ///   continue after the highest numeric suffix;
  /// * R6: `RUNNING` reads as `CANCELLED`.
  static (String projectId, VideoKitEditState state, int maxId) decode(
    SerializedEditProject serialized,
  ) {
    final (id, state, maxId, _) = decodeWithMeta(serialized);
    return (id, state, maxId);
  }

  static VideoKitException _reject(String why) => VideoKitException(
    VideoKitStableError(
      code: why == 'edit_schema_unsupported'
          ? ErrorCode.unsupportedSnapshotVersion
          : ErrorCode.invalidArgument,
      stage: ErrorStage.edit,
      diagnostic: why,
    ),
  );

  /// [decode] plus the snapshot metadata.
  static (
    String projectId,
    VideoKitEditState state,
    int maxId,
    FakeSnapshotMeta meta,
  )
  decodeWithMeta(SerializedEditProject serialized) {
    const current = SerializedEditProject.currentSchemaVersion;
    if (serialized.schemaVersion > current) {
      throw _reject('edit_schema_unsupported');
    }
    final Object? raw;
    try {
      raw = jsonDecode(serialized.json);
    } on FormatException {
      throw _reject('edit_snapshot_malformed');
    }
    if (raw is! Map) throw _reject('edit_snapshot_malformed');
    var j = raw.cast<String, Object?>();
    final payloadVersion = j['schemaVersion'];
    if (payloadVersion != null && payloadVersion is! int) {
      throw _reject('edit_snapshot_malformed');
    }
    var version = (payloadVersion as int?) ?? serialized.schemaVersion;
    if (version > current) throw _reject('edit_schema_unsupported');
    while (version < current) {
      final step = migrations[version];
      if (step == null) throw _reject('edit_schema_unsupported');
      j = step(j);
      version++;
    }
    try {
      return _readV1(j);
    } on _Malformed {
      throw _reject('edit_snapshot_malformed');
    }
  }

  // Strict readers (R3). Each throws _Malformed on a wrong type.

  static Object? _req(Map<String, Object?> m, String key) =>
      m.containsKey(key) && m[key] != null ? m[key] : throw _Malformed();

  static String _str(Object? v) => v is String ? v : throw _Malformed();

  static String? _strOrNull(Object? v) =>
      v == null ? null : (v is String ? v : throw _Malformed());

  static int _int(Object? v) {
    if (v is int) return v;
    if (v is double && v == v.roundToDouble() && v.isFinite) return v.toInt();
    throw _Malformed();
  }

  static int _intOr(Map<String, Object?> m, String key, int fallback) =>
      m[key] == null ? fallback : _int(m[key]);

  static double _num(Object? v) => v is num ? v.toDouble() : throw _Malformed();

  static double _numOr(Map<String, Object?> m, String key, double fallback) =>
      m[key] == null ? fallback : _num(m[key]);

  static double? _numOrNull(Object? v) => v == null ? null : _num(v);

  static bool _boolOr(Map<String, Object?> m, String key, bool fallback) {
    final v = m[key];
    if (v == null) return fallback;
    return v is bool ? v : throw _Malformed();
  }

  static Map<String, Object?> _obj(Object? v) =>
      v is Map ? v.cast<String, Object?>() : throw _Malformed();

  static List<Map<String, Object?>> _objList(Map<String, Object?> m, String k) {
    final v = m[k];
    if (v == null) return const [];
    if (v is! List) throw _Malformed();
    return [for (final e in v) _obj(e)];
  }

  static (int, int) _rangeOf(Object? v) {
    final r = _obj(v);
    return (_int(_req(r, 'startUs')), _int(_req(r, 'endUs')));
  }

  /// An enum value by wire name; unknown or missing names read as
  /// [unknown] (R4); a non-string is malformed.
  static T _enum<T extends Enum>(
    List<T> values,
    Object? v,
    String Function(T) wire,
    T unknown,
  ) {
    if (v == null) return unknown;
    if (v is! String) throw _Malformed();
    for (final e in values) {
      if (wire(e) == v) return e;
    }
    return unknown;
  }

  static TrackingState _quality(Object? v) => _enum(
    TrackingState.values,
    v,
    (e) => e.wireName,
    TrackingState.notAnalyzed,
  );

  static (
    String projectId,
    VideoKitEditState state,
    int maxId,
    FakeSnapshotMeta meta,
  )
  _readV1(Map<String, Object?> j) {
    var maxId = 0;
    void noteId(String id) {
      final n = int.tryParse(id.split('-').last);
      if (n != null && n > maxId) maxId = n;
    }

    final projectId = _str(_req(j, 'projectId'));
    if (j['schemaMinor'] != null) _int(j['schemaMinor']);
    final revision = _intOr(j, 'revision', 0);
    final sources = [
      for (final s in _objList(j, 'sources'))
        () {
          final id = _str(_req(s, 'sourceId'));
          noteId(id);
          final p = s['probe'] == null ? null : _obj(s['probe']);
          return EditSource(
            sourceId: id,
            mediaToken: _str(_req(s, 'mediaToken')),
            displayName: _strOrNull(s['displayName']),
            // null while not probed (04A E4).
            probe: p == null
                ? null
                : SourceProbe(
                    durationUs: _intOr(p, 'durationUs', 0),
                    width: _intOr(p, 'width', 0),
                    height: _intOr(p, 'height', 0),
                    rotationDeg: _intOr(p, 'rotation', 0),
                    fps: _numOrNull(p['fps']),
                    videoCodec: _strOrNull(p['videoCodec']),
                    audioCodec: _strOrNull(p['audioCodec']),
                    hasAudio: _boolOr(p, 'hasAudio', false),
                  ),
          );
        }(),
    ];
    final timelineJson = j['timeline'] == null
        ? const <String, Object?>{}
        : _obj(j['timeline']);
    final clips = [
      for (final c in _objList(timelineJson, 'clips'))
        () {
          final id = _str(_req(c, 'clipId'));
          noteId(id);
          return EditClip(
            clipId: id,
            sourceId: _str(_req(c, 'sourceId')),
            inUs: _int(_req(c, 'inUs')),
            outUs: _int(_req(c, 'outUs')),
          );
        }(),
    ];
    final masks = [
      for (final m in _objList(j, 'masks'))
        () {
          final id = _str(_req(m, 'maskId'));
          noteId(id);
          final (start, end) = _rangeOf(_req(m, 'rangeUs'));
          return MaskTrack(
            acceptedRanges: [
              for (final r in _objList(m, 'acceptedRanges'))
                () {
                  final (s, e) = _rangeOf(r);
                  return TimeRangeUs(s, e);
                }(),
            ],
            maskId: id,
            type: _enum(
              MaskType.values,
              _req(m, 'type'),
              (e) => e.wireName,
              MaskType.manual,
            ),
            style: _enum(
              MaskStyle.values,
              m['style'],
              (e) => e.wireName,
              MaskStyle.mosaic,
            ),
            strength: _numOr(m, 'strength', 0.5),
            enabled: _boolOr(m, 'enabled', true),
            startUs: start,
            endUs: end,
            keyframes: [
              for (final k in _objList(m, 'keyframes'))
                () {
                  final r = _obj(_req(k, 'region'));
                  return MaskKeyframe(
                    atUs: _int(_req(k, 'atUs')),
                    region: MaskRegion(
                      x: _num(_req(r, 'x')),
                      y: _num(_req(r, 'y')),
                      width: _num(_req(r, 'width')),
                      height: _num(_req(r, 'height')),
                      rotationDeg: _numOr(r, 'rotation', 0),
                    ),
                    source: _enum(
                      KeyframeSource.values,
                      k['source'],
                      (e) => e.wireName,
                      KeyframeSource.user,
                    ),
                    state: k['state'] == null ? null : _quality(k['state']),
                  );
                }(),
            ],
          );
        }(),
    ];
    final masksById = {for (final m in masks) m.maskId: m};
    // Coverage `accepted` is derived from the mask's ranges (04A E4).
    bool inside(String maskId, int s, int e) =>
        masksById[maskId]?.isAccepted(s, e) ?? false;
    var restoredRuns = 0;
    final tracking = <String, TrackingRun>{};
    for (final t in _objList(j, 'tracking')) {
      final maskId = _str(_req(t, 'maskId'));
      var status = _enum(
        TrackingRunStatus.values,
        _req(t, 'status'),
        (e) => e.wireName,
        TrackingRunStatus.failed,
      );
      // R6: a run in progress cannot be resumed from a snapshot.
      if (status == TrackingRunStatus.running) {
        status = TrackingRunStatus.cancelled;
      }
      tracking[maskId] = TrackingRun(
        maskId: maskId,
        // Runtime state (04A E2 3), rebuilt on restore.
        requestId: 'restored-${++restoredRuns}',
        projectRevision: revision,
        kind: masksById[maskId]?.type == MaskType.object
            ? TrackingKind.object
            : TrackingKind.face,
        status: status,
        coverage: CoverageReport(
          segments: [
            for (final s in _objList(t, 'coverage'))
              () {
                final start = _int(_req(s, 'startUs'));
                final end = _int(_req(s, 'endUs'));
                return CoverageRange(
                  startUs: start,
                  endUs: end,
                  state: _quality(_req(s, 'quality')),
                  accepted: inside(maskId, start, end),
                );
              }(),
          ],
        ),
      );
    }
    final state = VideoKitEditState(
      phase: EditPhase.ready,
      revision: revision,
      timeline: Timeline(sources: sources, clips: clips),
      masks: masks,
      tracking: tracking,
    );
    final meta = FakeSnapshotMeta(
      createdAtMs: _intOr(j, 'createdAt', 0),
      updatedAtMs: _intOr(j, 'updatedAt', 0),
      exportPresetId: _strOrNull(j['exportPresetId']),
    );
    return (projectId, state, maxId, meta);
  }
}

/// Malformed snapshot content (R3); mapped to `INVALID_ARGUMENT`.
final class _Malformed implements Exception {}
