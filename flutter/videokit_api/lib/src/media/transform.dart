import 'package:flutter/foundation.dart';

import '../util/enum_codec.dart';

/// How media fits its viewport (05 §3, 06 §4).
enum FitMode {
  /// Whole picture visible, letterboxed.
  fit,

  /// Viewport filled, picture cropped.
  fill,

  /// 1 media pixel = 1 logical pixel ("原尺寸").
  original;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [fit].
  static FitMode fromName(String? name) => enumFromName(values, name, fit);
}

/// Zoom/pan/rotation/fit state, stored by the session and returned in
/// snapshots (06 §4).
@immutable
final class MediaTransform {
  /// Creates a transform. [rotationDeg] must be 0, 90, 180 or 270.
  const MediaTransform({
    this.scale = 1.0,
    this.panX = 0.0,
    this.panY = 0.0,
    this.rotationDeg = 0,
    this.fitMode = FitMode.fit,
  }) : assert(
         rotationDeg == 0 ||
             rotationDeg == 90 ||
             rotationDeg == 180 ||
             rotationDeg == 270,
       );

  /// Identity transform.
  static const MediaTransform identity = MediaTransform();

  /// Zoom factor relative to [fitMode] (1 = no zoom).
  final double scale;

  /// Horizontal pan, normalized to the displayed picture width.
  final double panX;

  /// Vertical pan, normalized to the displayed picture height.
  final double panY;

  /// Clockwise rotation in degrees (0/90/180/270).
  final int rotationDeg;

  /// Fit mode.
  final FitMode fitMode;

  /// Whether zoomed beyond the fit scale (pan gestures win over paging).
  bool get isZoomed => scale > 1.0;

  /// Returns a copy with the given fields replaced.
  MediaTransform copyWith({
    double? scale,
    double? panX,
    double? panY,
    int? rotationDeg,
    FitMode? fitMode,
  }) => MediaTransform(
    scale: scale ?? this.scale,
    panX: panX ?? this.panX,
    panY: panY ?? this.panY,
    rotationDeg: rotationDeg ?? this.rotationDeg,
    fitMode: fitMode ?? this.fitMode,
  );

  @override
  bool operator ==(Object other) =>
      other is MediaTransform &&
      other.scale == scale &&
      other.panX == panX &&
      other.panY == panY &&
      other.rotationDeg == rotationDeg &&
      other.fitMode == fitMode;

  @override
  int get hashCode => Object.hash(scale, panX, panY, rotationDeg, fitMode);

  @override
  String toString() =>
      'MediaTransform(scale: $scale, pan: ($panX, $panY), '
      'rotation: $rotationDeg, fit: ${fitMode.name})';
}
