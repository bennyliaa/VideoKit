import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../util/undefined.dart';

/// Read-only facts about the bound media (04A P2), filled after bind.
/// Every field is optional: what the engine cannot tell is null.
@immutable
final class MediaInfo {
  /// Creates media facts.
  const MediaInfo({
    this.container,
    this.videoCodec,
    this.audioCodec,
    this.width,
    this.height,
    this.frameRate,
    this.bitrateBps,
    this.rotationDeg,
    this.durationUs,
    this.fileSizeBytes,
  });

  /// Container MIME type (e.g. `video/mp4`, `image/heic`).
  final String? container;

  /// Video codec MIME type (e.g. `video/avc`); null for still images.
  final String? videoCodec;

  /// Audio codec MIME type.
  final String? audioCodec;

  /// Coded width (px).
  final int? width;

  /// Coded height (px).
  final int? height;

  /// Frame rate (fps).
  final double? frameRate;

  /// Overall bitrate (bits/s).
  final int? bitrateBps;

  /// Rotation metadata (0/90/180/270).
  final int? rotationDeg;

  /// Duration (µs).
  final int? durationUs;

  /// File size (bytes).
  final int? fileSizeBytes;

  /// Returns a copy with the given fields replaced.
  MediaInfo copyWith({
    Object? container = undefined,
    Object? videoCodec = undefined,
    Object? audioCodec = undefined,
    Object? width = undefined,
    Object? height = undefined,
    Object? frameRate = undefined,
    Object? bitrateBps = undefined,
    Object? rotationDeg = undefined,
    Object? durationUs = undefined,
    Object? fileSizeBytes = undefined,
  }) => MediaInfo(
    container: pick<String?>(container, this.container),
    videoCodec: pick<String?>(videoCodec, this.videoCodec),
    audioCodec: pick<String?>(audioCodec, this.audioCodec),
    width: pick<int?>(width, this.width),
    height: pick<int?>(height, this.height),
    frameRate: pick<double?>(frameRate, this.frameRate),
    bitrateBps: pick<int?>(bitrateBps, this.bitrateBps),
    rotationDeg: pick<int?>(rotationDeg, this.rotationDeg),
    durationUs: pick<int?>(durationUs, this.durationUs),
    fileSizeBytes: pick<int?>(fileSizeBytes, this.fileSizeBytes),
  );

  @override
  bool operator ==(Object other) =>
      other is MediaInfo &&
      other.container == container &&
      other.videoCodec == videoCodec &&
      other.audioCodec == audioCodec &&
      other.width == width &&
      other.height == height &&
      other.frameRate == frameRate &&
      other.bitrateBps == bitrateBps &&
      other.rotationDeg == rotationDeg &&
      other.durationUs == durationUs &&
      other.fileSizeBytes == fileSizeBytes;

  @override
  int get hashCode => Object.hash(
    container,
    videoCodec,
    audioCodec,
    width,
    height,
    frameRate,
    bitrateBps,
    rotationDeg,
    durationUs,
    fileSizeBytes,
  );

  @override
  String toString() =>
      'MediaInfo($container, $videoCodec/$audioCodec, ${width}x$height, '
      '$frameRate fps, $bitrateBps bps, rot $rotationDeg, $durationUs µs, '
      '$fileSizeBytes B)';
}

/// Result of `captureThumbnail` (04A P1).
sealed class ThumbnailResult {
  const ThumbnailResult();
}

/// A small encoded picture of the media.
final class ThumbnailCaptured extends ThumbnailResult {
  /// Creates a result.
  const ThumbnailCaptured({
    required this.bytes,
    required this.width,
    required this.height,
    this.mimeType = 'image/jpeg',
  });

  /// Encoded image bytes.
  final Uint8List bytes;

  /// Actual width (px).
  final int width;

  /// Actual height (px).
  final int height;

  /// Encoding (`image/jpeg` from the native Kit; the Dart Fake encodes
  /// `image/png`).
  final String mimeType;

  @override
  bool operator ==(Object other) =>
      other is ThumbnailCaptured &&
      listEquals(other.bytes, bytes) &&
      other.width == width &&
      other.height == height &&
      other.mimeType == mimeType;

  @override
  int get hashCode =>
      Object.hash(Object.hashAll(bytes), width, height, mimeType);

  @override
  String toString() =>
      'ThumbnailCaptured(${width}x$height, $mimeType, ${bytes.length} B)';
}

/// No thumbnail (not bound, unsupported, decode failure).
final class ThumbnailFailed extends ThumbnailResult {
  /// Creates a result.
  const ThumbnailFailed(this.error);

  /// Stable error.
  final VideoKitStableError error;

  @override
  bool operator ==(Object other) =>
      other is ThumbnailFailed && other.error == error;

  @override
  int get hashCode => error.hashCode;

  @override
  String toString() => 'ThumbnailFailed(${error.code.name})';
}
