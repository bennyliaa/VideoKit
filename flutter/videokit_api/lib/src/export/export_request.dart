import 'package:flutter/foundation.dart';

import '../util/undefined.dart';

/// Built-in export preset IDs (08 §8).
abstract final class ExportPresets {
  /// MP4/H.264/AAC, same size as the first source.
  static const String original = 'ORIGINAL';

  /// Long edge 1920.
  static const String p1080 = 'P1080';

  /// Long edge 1280.
  static const String p720 = 'P720';

  /// All built-in presets.
  static const List<String> all = [original, p1080, p720];
}

/// Export request (08 §6, UI-08).
@immutable
final class VideoKitExportRequest {
  /// Creates a request.
  const VideoKitExportRequest({
    this.presetId = ExportPresets.original,
    this.exportId,
    this.acceptUncoveredTracking = false,
  });

  /// Preset ID.
  final String presetId;

  /// Caller-chosen export ID; null lets VideoKit generate one.
  final String? exportId;

  /// User explicitly accepted uncovered tracking intervals; recorded as a
  /// warning and the result is never "fully masked" (09 §4).
  final bool acceptUncoveredTracking;

  /// Returns a copy with the given fields replaced.
  VideoKitExportRequest copyWith({
    String? presetId,
    Object? exportId = undefined,
    bool? acceptUncoveredTracking,
  }) => VideoKitExportRequest(
    presetId: presetId ?? this.presetId,
    exportId: pick<String?>(exportId, this.exportId),
    acceptUncoveredTracking:
        acceptUncoveredTracking ?? this.acceptUncoveredTracking,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitExportRequest &&
      other.presetId == presetId &&
      other.exportId == exportId &&
      other.acceptUncoveredTracking == acceptUncoveredTracking;

  @override
  int get hashCode => Object.hash(presetId, exportId, acceptUncoveredTracking);

  @override
  String toString() =>
      'VideoKitExportRequest($presetId, id: $exportId, '
      'acceptUncovered: $acceptUncoveredTracking)';
}

/// What an output sink can do (08 §5).
@immutable
final class SinkCapabilities {
  /// Creates capabilities.
  const SinkCapabilities({
    this.sequentialWrite = true,
    this.randomWrite = false,
    this.fileDescriptor = false,
    this.flush = true,
    this.knownFreeSpaceBytes,
  });

  /// Sequential writes.
  final bool sequentialWrite;

  /// Positional writes.
  final bool randomWrite;

  /// File-descriptor mode.
  final bool fileDescriptor;

  /// Flush support.
  final bool flush;

  /// Free space, if the host knows it.
  final int? knownFreeSpaceBytes;

  /// Returns a copy with the given fields replaced.
  SinkCapabilities copyWith({
    bool? sequentialWrite,
    bool? randomWrite,
    bool? fileDescriptor,
    bool? flush,
    Object? knownFreeSpaceBytes = undefined,
  }) => SinkCapabilities(
    sequentialWrite: sequentialWrite ?? this.sequentialWrite,
    randomWrite: randomWrite ?? this.randomWrite,
    fileDescriptor: fileDescriptor ?? this.fileDescriptor,
    flush: flush ?? this.flush,
    knownFreeSpaceBytes: pick<int?>(
      knownFreeSpaceBytes,
      this.knownFreeSpaceBytes,
    ),
  );

  @override
  bool operator ==(Object other) =>
      other is SinkCapabilities &&
      other.sequentialWrite == sequentialWrite &&
      other.randomWrite == randomWrite &&
      other.fileDescriptor == fileDescriptor &&
      other.flush == flush &&
      other.knownFreeSpaceBytes == knownFreeSpaceBytes;

  @override
  int get hashCode => Object.hash(
    sequentialWrite,
    randomWrite,
    fileDescriptor,
    flush,
    knownFreeSpaceBytes,
  );

  @override
  String toString() =>
      'SinkCapabilities(seq: $sequentialWrite, random: $randomWrite, '
      'fd: $fileDescriptor, flush: $flush, free: $knownFreeSpaceBytes)';
}

/// Dart handle of a host output sink (08 §5, 04 §12.3).
///
/// Sinks are implemented natively and registered under [sinkRef]; Dart only
/// names the sink and sees its capabilities. Writes never cross Dart.
@immutable
final class VideoKitOutputSink {
  /// Creates a sink reference.
  const VideoKitOutputSink({
    required this.sinkRef,
    this.capabilities = const SinkCapabilities(),
  });

  /// Registered sink reference (`registered:<id>` or `demo:<id>`).
  final String sinkRef;

  /// Capabilities.
  final SinkCapabilities capabilities;

  /// Returns a copy with the given fields replaced.
  VideoKitOutputSink copyWith({
    String? sinkRef,
    SinkCapabilities? capabilities,
  }) => VideoKitOutputSink(
    sinkRef: sinkRef ?? this.sinkRef,
    capabilities: capabilities ?? this.capabilities,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitOutputSink &&
      other.sinkRef == sinkRef &&
      other.capabilities == capabilities;

  @override
  int get hashCode => Object.hash(sinkRef, capabilities);

  @override
  String toString() => 'VideoKitOutputSink($sinkRef, $capabilities)';
}
