import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../session/session_state.dart';
import '../util/collections.dart';
import '../util/undefined.dart';
import 'export_progress.dart';

/// Known export warning codes (08 §7, 09 §4; 04A K3): upper snake case,
/// registered in the `exportWarnings` group of `spec/notices.json`. On the
/// wire a warning is the code alone or `CODE:argument` (e.g. the mask id);
/// compare with [codeOf].
abstract final class ExportWarnings {
  /// Boundaries aligned to keyframes in fast concat.
  static const String boundaryAlignedToKeyframe =
      'BOUNDARY_ALIGNED_TO_KEYFRAME';

  /// Silence inserted for inputs without audio.
  static const String silenceInserted = 'SILENCE_INSERTED';

  /// The tracking of a mask did not complete (argument: mask id).
  static const String trackingIncomplete = 'TRACKING_INCOMPLETE';

  /// User accepted uncovered tracking intervals: not fully masked
  /// (argument: mask id).
  static const String trackingCoverageAccepted = 'TRACKING_COVERAGE_ACCEPTED';

  /// Tracking has lost ranges that were not accepted (argument: mask id).
  static const String trackingLostRanges = 'TRACKING_LOST_RANGES';

  /// Demo backend: no real media file was produced.
  static const String demoNoRealFile = 'DEMO_OUTPUT_NOT_REAL_MEDIA';

  /// The engine refused fast (remux) concatenation; the export transcodes
  /// instead (M4, UI explains it on the export page).
  static const String fastConcatRejected = 'FAST_CONCAT_REJECTED';

  /// Every code above, in registry order.
  static const List<String> all = [
    boundaryAlignedToKeyframe,
    silenceInserted,
    trackingIncomplete,
    trackingCoverageAccepted,
    trackingLostRanges,
    demoNoRealFile,
    fastConcatRejected,
  ];

  /// The code of a wire warning (`CODE` or `CODE:argument`).
  static String codeOf(String warning) {
    final i = warning.indexOf(':');
    return i < 0 ? warning : warning.substring(0, i);
  }

  /// Whether [warnings] contain [code] (with or without an argument).
  static bool has(Iterable<String> warnings, String code) =>
      warnings.any((w) => codeOf(w) == code);
}

/// Description of a successfully exported media (08 §7).
@immutable
final class VideoKitExportedMedia {
  /// Creates the description.
  VideoKitExportedMedia({
    required this.outputToken,
    required this.container,
    required this.extension,
    required this.width,
    required this.height,
    required this.durationUs,
    required this.sizeBytes,
    required this.createdAt,
    required this.editProjectId,
    required this.exportPresetId,
    this.videoCodec,
    this.audioCodec,
    this.orientation = MediaOrientation.unknown,
    this.frameRate,
    this.audioPresent = false,
    List<String> sourceTokens = const [],
    List<String> warnings = const [],
    this.isDemo = false,
  }) : sourceTokens = frozenList(sourceTokens),
       warnings = frozenList(warnings);

  /// Opaque host output token.
  final String outputToken;

  /// Container (e.g. `mp4`).
  final String container;

  /// File extension.
  final String extension;

  /// Video codec.
  final String? videoCodec;

  /// Audio codec.
  final String? audioCodec;

  /// Width.
  final int width;

  /// Height.
  final int height;

  /// Orientation.
  final MediaOrientation orientation;

  /// Duration (µs).
  final int durationUs;

  /// Size (bytes).
  final int sizeBytes;

  /// Frame rate.
  final double? frameRate;

  /// Has audio.
  final bool audioPresent;

  /// Creation time (UTC).
  final DateTime createdAt;

  /// Input media tokens.
  final List<String> sourceTokens;

  /// Edit project ID.
  final String editProjectId;

  /// Preset ID.
  final String exportPresetId;

  /// Warning codes, see [ExportWarnings].
  final List<String> warnings;

  /// Produced by a demo backend: no real media file exists.
  final bool isDemo;

  /// Returns a copy with the given fields replaced.
  VideoKitExportedMedia copyWith({
    String? outputToken,
    String? container,
    String? extension,
    Object? videoCodec = undefined,
    Object? audioCodec = undefined,
    int? width,
    int? height,
    MediaOrientation? orientation,
    int? durationUs,
    int? sizeBytes,
    Object? frameRate = undefined,
    bool? audioPresent,
    DateTime? createdAt,
    List<String>? sourceTokens,
    String? editProjectId,
    String? exportPresetId,
    List<String>? warnings,
    bool? isDemo,
  }) => VideoKitExportedMedia(
    outputToken: outputToken ?? this.outputToken,
    container: container ?? this.container,
    extension: extension ?? this.extension,
    videoCodec: pick<String?>(videoCodec, this.videoCodec),
    audioCodec: pick<String?>(audioCodec, this.audioCodec),
    width: width ?? this.width,
    height: height ?? this.height,
    orientation: orientation ?? this.orientation,
    durationUs: durationUs ?? this.durationUs,
    sizeBytes: sizeBytes ?? this.sizeBytes,
    frameRate: pick<double?>(frameRate, this.frameRate),
    audioPresent: audioPresent ?? this.audioPresent,
    createdAt: createdAt ?? this.createdAt,
    sourceTokens: sourceTokens ?? this.sourceTokens,
    editProjectId: editProjectId ?? this.editProjectId,
    exportPresetId: exportPresetId ?? this.exportPresetId,
    warnings: warnings ?? this.warnings,
    isDemo: isDemo ?? this.isDemo,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitExportedMedia &&
      other.outputToken == outputToken &&
      other.container == container &&
      other.extension == extension &&
      other.videoCodec == videoCodec &&
      other.audioCodec == audioCodec &&
      other.width == width &&
      other.height == height &&
      other.orientation == orientation &&
      other.durationUs == durationUs &&
      other.sizeBytes == sizeBytes &&
      other.frameRate == frameRate &&
      other.audioPresent == audioPresent &&
      other.createdAt == createdAt &&
      listEquals(other.sourceTokens, sourceTokens) &&
      other.editProjectId == editProjectId &&
      other.exportPresetId == exportPresetId &&
      listEquals(other.warnings, warnings) &&
      other.isDemo == isDemo;

  @override
  int get hashCode => Object.hashAll([
    outputToken,
    container,
    extension,
    videoCodec,
    audioCodec,
    width,
    height,
    orientation,
    durationUs,
    sizeBytes,
    frameRate,
    audioPresent,
    createdAt,
    hashList(sourceTokens),
    editProjectId,
    exportPresetId,
    hashList(warnings),
    isDemo,
  ]);

  @override
  String toString() =>
      'VideoKitExportedMedia($outputToken, $container, ${width}x$height, '
      '$durationUs µs, $sizeBytes B, preset: $exportPresetId, '
      'warnings: $warnings, demo: $isDemo)';
}

/// Outcome of `VideoKitEditProject.export` (08 §6–§7).
@immutable
sealed class VideoKitExportResult {
  const VideoKitExportResult(this.exportId);

  /// Export ID.
  final String exportId;
}

/// Written, verified and `markReady`'d.
final class ExportSucceeded extends VideoKitExportResult {
  /// Creates the result.
  const ExportSucceeded(super.exportId, this.media);

  /// Output description.
  final VideoKitExportedMedia media;

  @override
  bool operator ==(Object other) =>
      other is ExportSucceeded &&
      other.exportId == exportId &&
      other.media == media;

  @override
  int get hashCode => Object.hash(ExportSucceeded, exportId, media);

  @override
  String toString() => 'ExportSucceeded($exportId, $media)';
}

/// Failed; the sink was aborted and nothing was `markReady`'d.
final class ExportFailed extends VideoKitExportResult {
  /// Creates the result.
  const ExportFailed(super.exportId, this.error, {this.stage});

  /// Error.
  final VideoKitStableError error;

  /// Stage where it failed, if it started.
  final ExportStage? stage;

  @override
  bool operator ==(Object other) =>
      other is ExportFailed &&
      other.exportId == exportId &&
      other.error == error &&
      other.stage == stage;

  @override
  int get hashCode => Object.hash(ExportFailed, exportId, error, stage);

  @override
  String toString() => 'ExportFailed($exportId, $error, stage: $stage)';
}

/// Cancelled; the sink was aborted.
final class ExportCancelled extends VideoKitExportResult {
  /// Creates the result.
  const ExportCancelled(super.exportId, {this.partialOutputRemoved = true});

  /// Whether the sink reported partial output removed (UI text differs).
  final bool partialOutputRemoved;

  @override
  bool operator ==(Object other) =>
      other is ExportCancelled &&
      other.exportId == exportId &&
      other.partialOutputRemoved == partialOutputRemoved;

  @override
  int get hashCode =>
      Object.hash(ExportCancelled, exportId, partialOutputRemoved);

  @override
  String toString() =>
      'ExportCancelled($exportId, partialRemoved: $partialOutputRemoved)';
}
