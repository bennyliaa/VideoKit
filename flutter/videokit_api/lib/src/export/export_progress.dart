import 'package:flutter/foundation.dart';

import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Export pipeline stage (08 §6, UI-08).
enum ExportStage {
  preparing,
  tracking,
  encoding,
  verifying,
  writing;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [preparing].
  static ExportStage fromName(String? name) =>
      enumFromName(values, name, preparing);
}

/// Export progress (14 §3.3). [fraction] is null when progress cannot be
/// estimated reliably; never fabricated (08 §6).
@immutable
final class ExportProgress {
  /// Creates progress.
  const ExportProgress({
    required this.exportId,
    required this.stage,
    this.fraction,
    this.processedUs,
    this.outputBytes,
    this.remainingUs,
    this.cancellable = true,
  });

  /// Export ID.
  final String exportId;

  /// Current stage.
  final ExportStage stage;

  /// Stage progress 0–1, null when indeterminate.
  final double? fraction;

  /// Processed media time (µs).
  final int? processedUs;

  /// Bytes written so far.
  final int? outputBytes;

  /// Estimated remaining wall time (µs).
  final int? remainingUs;

  /// Whether cancel is currently possible.
  final bool cancellable;

  /// Returns a copy with the given fields replaced.
  ExportProgress copyWith({
    String? exportId,
    ExportStage? stage,
    Object? fraction = undefined,
    Object? processedUs = undefined,
    Object? outputBytes = undefined,
    Object? remainingUs = undefined,
    bool? cancellable,
  }) => ExportProgress(
    exportId: exportId ?? this.exportId,
    stage: stage ?? this.stage,
    fraction: pick<double?>(fraction, this.fraction),
    processedUs: pick<int?>(processedUs, this.processedUs),
    outputBytes: pick<int?>(outputBytes, this.outputBytes),
    remainingUs: pick<int?>(remainingUs, this.remainingUs),
    cancellable: cancellable ?? this.cancellable,
  );

  @override
  bool operator ==(Object other) =>
      other is ExportProgress &&
      other.exportId == exportId &&
      other.stage == stage &&
      other.fraction == fraction &&
      other.processedUs == processedUs &&
      other.outputBytes == outputBytes &&
      other.remainingUs == remainingUs &&
      other.cancellable == cancellable;

  @override
  int get hashCode => Object.hash(
    exportId,
    stage,
    fraction,
    processedUs,
    outputBytes,
    remainingUs,
    cancellable,
  );

  @override
  String toString() =>
      'ExportProgress($exportId, ${stage.name}, $fraction, '
      'processed: $processedUs, bytes: $outputBytes, '
      'cancellable: $cancellable)';
}
