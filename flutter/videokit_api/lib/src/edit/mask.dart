import 'package:flutter/foundation.dart';

import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';
import 'tracking.dart';

/// Mask region (04A N6): normalised rectangle (0–1, relative to the
/// orientation-corrected source picture, origin top-left), optionally
/// rotated around its centre (08 §4).
@immutable
final class MaskRegion {
  /// Creates a region.
  const MaskRegion({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
    this.rotationDeg = 0.0,
  });

  /// Left edge.
  final double x;

  /// Top edge.
  final double y;

  /// Width.
  final double width;

  /// Height.
  final double height;

  /// Rotation around the centre (degrees, clockwise).
  final double rotationDeg;

  /// Right edge.
  double get right => x + width;

  /// Bottom edge.
  double get bottom => y + height;

  /// Linear interpolation between [a] and [b] at [t] ∈ [0, 1].
  static MaskRegion lerp(MaskRegion a, MaskRegion b, double t) {
    double mix(double p, double q) => p + (q - p) * t;
    return MaskRegion(
      x: mix(a.x, b.x),
      y: mix(a.y, b.y),
      width: mix(a.width, b.width),
      height: mix(a.height, b.height),
      rotationDeg: mix(a.rotationDeg, b.rotationDeg),
    );
  }

  /// Returns a copy with the given fields replaced.
  MaskRegion copyWith({
    double? x,
    double? y,
    double? width,
    double? height,
    double? rotationDeg,
  }) => MaskRegion(
    x: x ?? this.x,
    y: y ?? this.y,
    width: width ?? this.width,
    height: height ?? this.height,
    rotationDeg: rotationDeg ?? this.rotationDeg,
  );

  @override
  bool operator ==(Object other) =>
      other is MaskRegion &&
      other.x == x &&
      other.y == y &&
      other.width == width &&
      other.height == height &&
      other.rotationDeg == rotationDeg;

  @override
  int get hashCode => Object.hash(x, y, width, height, rotationDeg);

  @override
  String toString() =>
      'MaskRegion($x, $y, ${width}x$height, rot: $rotationDeg)';
}

/// Who produced a mask (08 §4).
enum MaskType {
  manual,
  face,
  object;

  /// Whether the mask is driven by automatic tracking.
  bool get isAutomatic => this != manual;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [manual].
  static MaskType fromName(String? name) => enumFromName(values, name, manual);
}

/// Mask rendering style (08 §4).
enum MaskStyle {
  mosaic,
  blur;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [mosaic].
  static MaskStyle fromName(String? name) => enumFromName(values, name, mosaic);
}

/// Keyframe origin; USER wins over TRACKER (09 §4).
enum KeyframeSource {
  user,
  tracker;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [user].
  static KeyframeSource fromName(String? name) =>
      enumFromName(values, name, user);
}

/// A mask keyframe (08 §4).
@immutable
final class MaskKeyframe {
  /// Creates a keyframe.
  const MaskKeyframe({
    required this.atUs,
    required this.region,
    this.source = KeyframeSource.user,
    this.state,
  });

  /// Output-timeline time (µs).
  final int atUs;

  /// Region.
  final MaskRegion region;

  /// Origin.
  final KeyframeSource source;

  /// Tracking state for tracker keyframes.
  final TrackingState? state;

  /// Returns a copy with the given fields replaced.
  MaskKeyframe copyWith({
    int? atUs,
    MaskRegion? region,
    KeyframeSource? source,
    Object? state = undefined,
  }) => MaskKeyframe(
    atUs: atUs ?? this.atUs,
    region: region ?? this.region,
    source: source ?? this.source,
    state: pick<TrackingState?>(state, this.state),
  );

  @override
  bool operator ==(Object other) =>
      other is MaskKeyframe &&
      other.atUs == atUs &&
      other.region == region &&
      other.source == source &&
      other.state == state;

  @override
  int get hashCode => Object.hash(atUs, region, source, state);

  @override
  String toString() =>
      'MaskKeyframe($atUs, $region, ${source.name}, ${state?.name})';
}

/// A mask track (08 §4). Keyframes are kept sorted by [MaskKeyframe.atUs].
@immutable
final class MaskTrack {
  /// Creates a mask track; [keyframes] are sorted by time.
  MaskTrack({
    required this.maskId,
    required this.type,
    required this.startUs,
    required this.endUs,
    this.style = MaskStyle.mosaic,
    this.strength = 0.5,
    this.enabled = true,
    List<MaskKeyframe> keyframes = const [],
  }) : keyframes = frozenList(
         [...keyframes]..sort((a, b) => a.atUs.compareTo(b.atUs)),
       );

  /// Mask ID.
  final String maskId;

  /// Type.
  final MaskType type;

  /// Style.
  final MaskStyle style;

  /// Strength 0–1.
  final double strength;

  /// Enabled.
  final bool enabled;

  /// Range start (µs, output timeline).
  final int startUs;

  /// Range end (µs, exclusive).
  final int endUs;

  /// Keyframes sorted by time.
  final List<MaskKeyframe> keyframes;

  /// Region at [atUs], linearly interpolated between keyframes; held
  /// constant before the first and after the last keyframe; null outside the
  /// range or without keyframes.
  ///
  /// This is the single interpolation function shared by preview and export
  /// (UI must not interpolate on its own, 14 §5.7).
  MaskRegion? regionAt(int atUs) {
    if (atUs < startUs || atUs >= endUs || keyframes.isEmpty) return null;
    if (atUs <= keyframes.first.atUs) return keyframes.first.region;
    if (atUs >= keyframes.last.atUs) return keyframes.last.region;
    for (var i = 0; i < keyframes.length - 1; i++) {
      final a = keyframes[i];
      final b = keyframes[i + 1];
      if (atUs >= a.atUs && atUs <= b.atUs) {
        final span = b.atUs - a.atUs;
        final t = span == 0 ? 0.0 : (atUs - a.atUs) / span;
        return MaskRegion.lerp(a.region, b.region, t);
      }
    }
    return keyframes.last.region;
  }

  /// Returns a copy with the given fields replaced.
  MaskTrack copyWith({
    String? maskId,
    MaskType? type,
    MaskStyle? style,
    double? strength,
    bool? enabled,
    int? startUs,
    int? endUs,
    List<MaskKeyframe>? keyframes,
  }) => MaskTrack(
    maskId: maskId ?? this.maskId,
    type: type ?? this.type,
    style: style ?? this.style,
    strength: strength ?? this.strength,
    enabled: enabled ?? this.enabled,
    startUs: startUs ?? this.startUs,
    endUs: endUs ?? this.endUs,
    keyframes: keyframes ?? this.keyframes,
  );

  @override
  bool operator ==(Object other) =>
      other is MaskTrack &&
      other.maskId == maskId &&
      other.type == type &&
      other.style == style &&
      other.strength == strength &&
      other.enabled == enabled &&
      other.startUs == startUs &&
      other.endUs == endUs &&
      listEquals(other.keyframes, keyframes);

  @override
  int get hashCode => Object.hash(
    maskId,
    type,
    style,
    strength,
    enabled,
    startUs,
    endUs,
    hashList(keyframes),
  );

  @override
  String toString() =>
      'MaskTrack($maskId, ${type.name}, ${style.name} $strength, '
      'enabled: $enabled, $startUs–$endUs, ${keyframes.length} kf)';
}
