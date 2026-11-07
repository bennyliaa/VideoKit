import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';
import 'mask.dart';

/// Per-interval tracking certainty (09 §1).
enum TrackingState {
  tracked,
  lowConfidence,
  ambiguous,
  lost,

  /// Frames not analysed yet; never counts as covered (09 §3).
  notAnalyzed;

  /// Whether the interval blocks export unless corrected or accepted
  /// (09 §4).
  bool get blocksExport =>
      this == ambiguous || this == lost || this == notAnalyzed;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [notAnalyzed]
  /// (conservative).
  static TrackingState fromName(String? name) =>
      enumFromName(values, name, notAnalyzed);
}

/// Kind of automatic tracking.
enum TrackingKind {
  face,
  object;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [object].
  static TrackingKind fromName(String? name) =>
      enumFromName(values, name, object);
}

/// One interval of a [CoverageReport].
@immutable
final class CoverageSegment {
  /// Creates a segment `[startUs, endUs)`.
  const CoverageSegment({
    required this.startUs,
    required this.endUs,
    required this.state,
    this.accepted = false,
  });

  /// Start (µs).
  final int startUs;

  /// End (µs, exclusive).
  final int endUs;

  /// State.
  final TrackingState state;

  /// User explicitly accepted this uncovered interval (recorded as an export
  /// warning; result is never "fully masked", 09 §4).
  final bool accepted;

  /// Duration (µs).
  int get durationUs => endUs - startUs;

  /// Returns a copy with the given fields replaced.
  CoverageSegment copyWith({
    int? startUs,
    int? endUs,
    TrackingState? state,
    bool? accepted,
  }) => CoverageSegment(
    startUs: startUs ?? this.startUs,
    endUs: endUs ?? this.endUs,
    state: state ?? this.state,
    accepted: accepted ?? this.accepted,
  );

  @override
  bool operator ==(Object other) =>
      other is CoverageSegment &&
      other.startUs == startUs &&
      other.endUs == endUs &&
      other.state == state &&
      other.accepted == accepted;

  @override
  int get hashCode => Object.hash(startUs, endUs, state, accepted);

  @override
  String toString() =>
      'CoverageSegment($startUs–$endUs, ${state.name}'
      '${accepted ? ', accepted' : ''})';
}

/// Coverage report of a tracked mask (09 §3).
@immutable
final class CoverageReport {
  /// Creates a report; [segments] are sorted by start.
  CoverageReport({List<CoverageSegment> segments = const []})
    : segments = frozenList(
        [...segments]..sort((a, b) => a.startUs.compareTo(b.startUs)),
      );

  /// Empty report.
  factory CoverageReport.empty() => CoverageReport();

  /// Segments sorted by start.
  final List<CoverageSegment> segments;

  /// Segments blocking export (lost/ambiguous/not analysed, not accepted).
  List<CoverageSegment> get blockingSegments => List.unmodifiable(
    segments.where((s) => s.state.blocksExport && !s.accepted),
  );

  /// Whether every segment is covered or accepted.
  bool get isComplete => segments.isNotEmpty && blockingSegments.isEmpty;

  /// State at [atUs], or null outside all segments.
  TrackingState? stateAt(int atUs) {
    for (final s in segments) {
      if (atUs >= s.startUs && atUs < s.endUs) return s.state;
    }
    return null;
  }

  /// Returns a copy with the given fields replaced.
  CoverageReport copyWith({List<CoverageSegment>? segments}) =>
      CoverageReport(segments: segments ?? this.segments);

  @override
  bool operator ==(Object other) =>
      other is CoverageReport && listEquals(other.segments, segments);

  @override
  int get hashCode => hashList(segments);

  @override
  String toString() => 'CoverageReport($segments)';
}

/// Status of a tracking run.
enum TrackingRunStatus {
  running,
  completed,
  cancelled,
  failed;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [failed].
  static TrackingRunStatus fromName(String? name) =>
      enumFromName(values, name, failed);
}

/// Progress and result of tracking one mask (14 §3.3).
@immutable
final class TrackingRun {
  /// Creates a run.
  const TrackingRun({
    required this.maskId,
    required this.requestId,
    required this.projectRevision,
    required this.kind,
    required this.status,
    required this.coverage,
    this.progress,
    this.error,
  });

  /// Mask ID.
  final String maskId;

  /// Request ID; stale results are dropped (09 §3).
  final String requestId;

  /// Project revision the run was started on.
  final int projectRevision;

  /// Kind.
  final TrackingKind kind;

  /// Status.
  final TrackingRunStatus status;

  /// Progress 0–1, null when not estimable.
  final double? progress;

  /// Coverage so far.
  final CoverageReport coverage;

  /// Error when failed.
  final VideoKitStableError? error;

  /// Returns a copy with the given fields replaced.
  TrackingRun copyWith({
    String? maskId,
    String? requestId,
    int? projectRevision,
    TrackingKind? kind,
    TrackingRunStatus? status,
    Object? progress = undefined,
    CoverageReport? coverage,
    Object? error = undefined,
  }) => TrackingRun(
    maskId: maskId ?? this.maskId,
    requestId: requestId ?? this.requestId,
    projectRevision: projectRevision ?? this.projectRevision,
    kind: kind ?? this.kind,
    status: status ?? this.status,
    progress: pick<double?>(progress, this.progress),
    coverage: coverage ?? this.coverage,
    error: pick<VideoKitStableError?>(error, this.error),
  );

  @override
  bool operator ==(Object other) =>
      other is TrackingRun &&
      other.maskId == maskId &&
      other.requestId == requestId &&
      other.projectRevision == projectRevision &&
      other.kind == kind &&
      other.status == status &&
      other.progress == progress &&
      other.coverage == coverage &&
      other.error == error;

  @override
  int get hashCode => Object.hash(
    maskId,
    requestId,
    projectRevision,
    kind,
    status,
    progress,
    coverage,
    error,
  );

  @override
  String toString() =>
      'TrackingRun($maskId, $requestId, rev: $projectRevision, ${kind.name}, '
      '${status.name}, progress: $progress, $coverage)';
}

/// A detected tracking candidate (e.g. a face) the user can pick (09 §1).
@immutable
final class TrackingCandidate {
  /// Creates a candidate.
  const TrackingCandidate({
    required this.candidateId,
    required this.kind,
    required this.region,
    this.confidence,
  });

  /// Candidate ID (valid within the project only).
  final String candidateId;

  /// Kind.
  final TrackingKind kind;

  /// Region at the detection time.
  final NormalizedRect region;

  /// Confidence 0–1.
  final double? confidence;

  /// Returns a copy with the given fields replaced.
  TrackingCandidate copyWith({
    String? candidateId,
    TrackingKind? kind,
    NormalizedRect? region,
    Object? confidence = undefined,
  }) => TrackingCandidate(
    candidateId: candidateId ?? this.candidateId,
    kind: kind ?? this.kind,
    region: region ?? this.region,
    confidence: pick<double?>(confidence, this.confidence),
  );

  @override
  bool operator ==(Object other) =>
      other is TrackingCandidate &&
      other.candidateId == candidateId &&
      other.kind == kind &&
      other.region == region &&
      other.confidence == confidence;

  @override
  int get hashCode => Object.hash(candidateId, kind, region, confidence);

  @override
  String toString() =>
      'TrackingCandidate($candidateId, ${kind.name}, $region, $confidence)';
}

/// Result of candidate detection.
@immutable
final class CandidateDetectionResult {
  /// Creates a result.
  CandidateDetectionResult({
    List<TrackingCandidate> candidates = const [],
    this.error,
  }) : candidates = frozenList(candidates);

  /// Candidates.
  final List<TrackingCandidate> candidates;

  /// Error (e.g. `TRACKING_MODEL_UNAVAILABLE`).
  final VideoKitStableError? error;

  /// Returns a copy with the given fields replaced.
  CandidateDetectionResult copyWith({
    List<TrackingCandidate>? candidates,
    Object? error = undefined,
  }) => CandidateDetectionResult(
    candidates: candidates ?? this.candidates,
    error: pick<VideoKitStableError?>(error, this.error),
  );

  @override
  bool operator ==(Object other) =>
      other is CandidateDetectionResult &&
      listEquals(other.candidates, candidates) &&
      other.error == error;

  @override
  int get hashCode => Object.hash(hashList(candidates), error);

  @override
  String toString() => 'CandidateDetectionResult($candidates, $error)';
}
