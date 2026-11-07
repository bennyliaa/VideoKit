import 'package:flutter/foundation.dart';

import '../edit/tracking.dart';
import '../error/stable_error.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Kind of a precheck finding (08 §6, 09 §4).
enum PrecheckIssueKind {
  emptyTimeline,
  presetUnavailable,
  encoderUnavailable,
  sinkCapabilityUnsupported,
  spaceInsufficient,
  trackingCoverageIncomplete,
  sourceMismatch,
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unknown].
  static PrecheckIssueKind fromName(String? name) =>
      enumFromName(values, name, unknown);
}

/// A tracking interval not covered by an automatic mask.
@immutable
final class UncoveredRange {
  /// Creates a range.
  const UncoveredRange({
    required this.maskId,
    required this.startUs,
    required this.endUs,
    required this.state,
  });

  /// Mask ID.
  final String maskId;

  /// Start (µs).
  final int startUs;

  /// End (µs).
  final int endUs;

  /// State.
  final TrackingState state;

  /// Returns a copy with the given fields replaced.
  UncoveredRange copyWith({
    String? maskId,
    int? startUs,
    int? endUs,
    TrackingState? state,
  }) => UncoveredRange(
    maskId: maskId ?? this.maskId,
    startUs: startUs ?? this.startUs,
    endUs: endUs ?? this.endUs,
    state: state ?? this.state,
  );

  @override
  bool operator ==(Object other) =>
      other is UncoveredRange &&
      other.maskId == maskId &&
      other.startUs == startUs &&
      other.endUs == endUs &&
      other.state == state;

  @override
  int get hashCode => Object.hash(maskId, startUs, endUs, state);

  @override
  String toString() =>
      'UncoveredRange($maskId, $startUs–$endUs, ${state.name})';
}

/// One precheck finding.
@immutable
final class PrecheckIssue {
  /// Creates an issue.
  const PrecheckIssue({required this.kind, this.blocking = true, this.error});

  /// Kind.
  final PrecheckIssueKind kind;

  /// Blocks export when true; otherwise a warning.
  final bool blocking;

  /// Mapped stable error, if any.
  final VideoKitStableError? error;

  /// Returns a copy with the given fields replaced.
  PrecheckIssue copyWith({
    PrecheckIssueKind? kind,
    bool? blocking,
    Object? error = undefined,
  }) => PrecheckIssue(
    kind: kind ?? this.kind,
    blocking: blocking ?? this.blocking,
    error: pick<VideoKitStableError?>(error, this.error),
  );

  @override
  bool operator ==(Object other) =>
      other is PrecheckIssue &&
      other.kind == kind &&
      other.blocking == blocking &&
      other.error == error;

  @override
  int get hashCode => Object.hash(kind, blocking, error);

  @override
  String toString() =>
      'PrecheckIssue(${kind.name}, blocking: $blocking, $error)';
}

/// Result of `checkExport` (08 §6).
@immutable
final class ExportPrecheck {
  /// Creates a precheck result.
  ExportPrecheck({
    List<PrecheckIssue> issues = const [],
    List<UncoveredRange> uncoveredRanges = const [],
    this.estimatedDurationUs,
    this.estimatedSizeBytes,
  }) : issues = frozenList(issues),
       uncoveredRanges = frozenList(uncoveredRanges);

  /// Findings.
  final List<PrecheckIssue> issues;

  /// Uncovered tracking intervals (for `CoverageCheckSheet`).
  final List<UncoveredRange> uncoveredRanges;

  /// Estimated output duration.
  final int? estimatedDurationUs;

  /// Estimated output size; null when not estimable.
  final int? estimatedSizeBytes;

  /// Whether export may start.
  bool get canExport => !issues.any((i) => i.blocking);

  /// Returns a copy with the given fields replaced.
  ExportPrecheck copyWith({
    List<PrecheckIssue>? issues,
    List<UncoveredRange>? uncoveredRanges,
    Object? estimatedDurationUs = undefined,
    Object? estimatedSizeBytes = undefined,
  }) => ExportPrecheck(
    issues: issues ?? this.issues,
    uncoveredRanges: uncoveredRanges ?? this.uncoveredRanges,
    estimatedDurationUs: pick<int?>(
      estimatedDurationUs,
      this.estimatedDurationUs,
    ),
    estimatedSizeBytes: pick<int?>(estimatedSizeBytes, this.estimatedSizeBytes),
  );

  @override
  bool operator ==(Object other) =>
      other is ExportPrecheck &&
      listEquals(other.issues, issues) &&
      listEquals(other.uncoveredRanges, uncoveredRanges) &&
      other.estimatedDurationUs == estimatedDurationUs &&
      other.estimatedSizeBytes == estimatedSizeBytes;

  @override
  int get hashCode => Object.hash(
    hashList(issues),
    hashList(uncoveredRanges),
    estimatedDurationUs,
    estimatedSizeBytes,
  );

  @override
  String toString() =>
      'ExportPrecheck(canExport: $canExport, $issues, '
      'uncovered: $uncoveredRanges, est: $estimatedDurationUs µs / '
      '$estimatedSizeBytes B)';
}
