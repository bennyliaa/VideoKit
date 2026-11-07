import 'package:flutter/foundation.dart';

/// Integer pixel size, orientation-corrected (04 §9.2, 14 §3.2).
///
/// Defined here instead of `dart:ui` `Size` so `videokit_api` depends only on
/// `package:flutter/foundation.dart`.
@immutable
final class VideoSize {
  /// Creates a size; both sides must be non-negative.
  const VideoSize(this.width, this.height)
    : assert(width >= 0),
      assert(height >= 0);

  /// Width in pixels.
  final int width;

  /// Height in pixels.
  final int height;

  /// Width / height, or 0 when height is 0.
  double get aspectRatio => height == 0 ? 0 : width / height;

  /// Longest side.
  int get longEdge => width > height ? width : height;

  /// Whether height exceeds width.
  bool get isPortrait => height > width;

  /// Returns a copy with the given fields replaced.
  VideoSize copyWith({int? width, int? height}) =>
      VideoSize(width ?? this.width, height ?? this.height);

  @override
  bool operator ==(Object other) =>
      other is VideoSize && other.width == width && other.height == height;

  @override
  int get hashCode => Object.hash(width, height);

  @override
  String toString() => 'VideoSize(${width}x$height)';
}
