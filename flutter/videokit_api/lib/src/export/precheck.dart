import 'package:flutter/foundation.dart';

import '../edit/edit_state.dart';
import '../edit/tracking.dart';
import '../error/stable_error.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// How the export will write to the sink (08 §5).
enum SinkWriteMode {
  /// Through a file descriptor.
  fileDescriptor,

  /// Random-access writes.
  randomWrite,

  /// Sequential writes only (fragmented output or private staging copy).
  sequential;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [sequential].
  static SinkWriteMode fromName(String? name) =>
      enumFromName(values, name, sequential);
}

/// A tracking interval not covered by an automatic mask (Dart detail for
/// the coverage check sheet, 14 §5.7).
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

/// Result of `checkExport` (08 §6, 04A S2): export may start only without
/// [problems]; [warnings] are recorded in the result (warning codes, see
/// `ExportWarnings`).
@immutable
final class ExportPrecheck {
  /// Creates a precheck result.
  ExportPrecheck({
    List<VideoKitStableError> problems = const [],
    List<String> warnings = const [],
    this.writeMode,
    this.estimate = EditEstimate.unknown,
    List<UncoveredRange> uncoveredRanges = const [],
  }) : problems = frozenList(problems),
       warnings = frozenList(warnings),
       uncoveredRanges = frozenList(uncoveredRanges);

  /// Blocking problems as stable errors (code + params).
  final List<VideoKitStableError> problems;

  /// Non-blocking warning codes.
  final List<String> warnings;

  /// Chosen sink write mode, if export is possible.
  final SinkWriteMode? writeMode;

  /// Output estimate.
  final EditEstimate estimate;

  /// Uncovered tracking intervals (for the coverage check sheet).
  final List<UncoveredRange> uncoveredRanges;

  /// Whether export may start (Kotlin `ok`).
  bool get ok => problems.isEmpty;

  /// Same as [ok].
  bool get canExport => ok;

  /// Returns a copy with the given fields replaced.
  ExportPrecheck copyWith({
    List<VideoKitStableError>? problems,
    List<String>? warnings,
    Object? writeMode = undefined,
    EditEstimate? estimate,
    List<UncoveredRange>? uncoveredRanges,
  }) => ExportPrecheck(
    problems: problems ?? this.problems,
    warnings: warnings ?? this.warnings,
    writeMode: pick<SinkWriteMode?>(writeMode, this.writeMode),
    estimate: estimate ?? this.estimate,
    uncoveredRanges: uncoveredRanges ?? this.uncoveredRanges,
  );

  @override
  bool operator ==(Object other) =>
      other is ExportPrecheck &&
      listEquals(other.problems, problems) &&
      listEquals(other.warnings, warnings) &&
      other.writeMode == writeMode &&
      other.estimate == estimate &&
      listEquals(other.uncoveredRanges, uncoveredRanges);

  @override
  int get hashCode => Object.hash(
    hashList(problems),
    hashList(warnings),
    writeMode,
    estimate,
    hashList(uncoveredRanges),
  );

  @override
  String toString() =>
      'ExportPrecheck(ok: $ok, problems: $problems, warnings: $warnings, '
      'mode: ${writeMode?.name}, $estimate, uncovered: $uncoveredRanges)';
}
