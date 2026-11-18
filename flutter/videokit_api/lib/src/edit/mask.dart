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
  blur,

  /// Avatar replacement (REQ-ED-07, 04A E5/E6): the mask's [MaskAvatar] is
  /// drawn over the tracked head. A reader that does not know IMAGE reads
  /// MOSAIC (schema `x-unknown`), so the head is never left uncovered.
  image;

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
    this.rollDeg,
  });

  /// Head roll in degrees from the line between the eyes, when the tracker
  /// reports it (04A E5 3); used by an avatar with
  /// [MaskAvatar.followRotation]. Null when unknown.
  final double? rollDeg;

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
    Object? rollDeg = undefined,
  }) => MaskKeyframe(
    atUs: atUs ?? this.atUs,
    region: region ?? this.region,
    source: source ?? this.source,
    state: pick<TrackingState?>(state, this.state),
    rollDeg: pick<double?>(rollDeg, this.rollDeg),
  );

  @override
  bool operator ==(Object other) =>
      other is MaskKeyframe &&
      other.atUs == atUs &&
      other.region == region &&
      other.source == source &&
      other.state == state &&
      other.rollDeg == rollDeg;

  @override
  int get hashCode => Object.hash(atUs, region, source, state, rollDeg);

  @override
  String toString() =>
      'MaskKeyframe($atUs, $region, ${source.name}, ${state?.name})';
}

/// The avatar of a [MaskStyle.image] mask (REQ-ED-07, 04A E5/E6): which
/// picture and how it sits on the tracked head. One value for the whole
/// mask in v1 (E5 4).
@immutable
final class MaskAvatar {
  /// Creates avatar settings.
  const MaskAvatar({
    required this.avatarToken,
    this.scale = 1.0,
    this.offsetX = 0,
    this.offsetY = 0,
    this.followRotation = true,
  });

  /// Opaque host token of the transparent PNG (the host stores it, E5 1),
  /// or `builtin:N` for a Kit built-in avatar (E5 5).
  final String avatarToken;

  /// Size relative to the tracked head box (design page 25 "大小").
  final double scale;

  /// Offset relative to the head box width.
  final double offsetX;

  /// Offset relative to the head box height.
  final double offsetY;

  /// Turn with the head ([MaskKeyframe.rollDeg]); design "随头部转动".
  final bool followRotation;

  /// Prefix of the built-in avatar tokens.
  static const String builtinPrefix = 'builtin:';

  /// Whether [avatarToken] names a Kit built-in avatar.
  bool get isBuiltin => avatarToken.startsWith(builtinPrefix);

  /// Returns a copy with the given fields replaced.
  MaskAvatar copyWith({
    String? avatarToken,
    double? scale,
    double? offsetX,
    double? offsetY,
    bool? followRotation,
  }) => MaskAvatar(
    avatarToken: avatarToken ?? this.avatarToken,
    scale: scale ?? this.scale,
    offsetX: offsetX ?? this.offsetX,
    offsetY: offsetY ?? this.offsetY,
    followRotation: followRotation ?? this.followRotation,
  );

  @override
  bool operator ==(Object other) =>
      other is MaskAvatar &&
      other.avatarToken == avatarToken &&
      other.scale == scale &&
      other.offsetX == offsetX &&
      other.offsetY == offsetY &&
      other.followRotation == followRotation;

  @override
  int get hashCode =>
      Object.hash(avatarToken, scale, offsetX, offsetY, followRotation);

  @override
  String toString() =>
      'MaskAvatar(<token>, scale: $scale, offset: $offsetX/$offsetY, '
      'follow: $followRotation)';
}

/// A half-open time range `[startUs, endUs)` in microseconds (same name and
/// meaning as Kotlin `TimeRangeUs`, 04A E4).
@immutable
final class TimeRangeUs {
  /// Creates a range.
  const TimeRangeUs(this.startUs, this.endUs);

  /// Start, inclusive.
  final int startUs;

  /// End, exclusive.
  final int endUs;

  /// Duration in microseconds.
  int get durationUs => endUs - startUs;

  /// Whether `0 <= startUs < endUs`.
  bool get isValid => startUs >= 0 && startUs < endUs;

  /// Whether [timeUs] is inside the range.
  bool contains(int timeUs) => timeUs >= startUs && timeUs < endUs;

  /// Whether `[startUs, endUs)` of [other] lies inside this range.
  bool covers(int otherStartUs, int otherEndUs) =>
      startUs <= otherStartUs && otherEndUs <= endUs;

  @override
  bool operator ==(Object other) =>
      other is TimeRangeUs && other.startUs == startUs && other.endUs == endUs;

  @override
  int get hashCode => Object.hash(startUs, endUs);

  @override
  String toString() => 'TimeRangeUs($startUs–$endUs)';
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
    List<TimeRangeUs> acceptedRanges = const [],
    this.avatar,
  }) : keyframes = frozenList(
         [...keyframes]..sort((a, b) => a.atUs.compareTo(b.atUs)),
       ),
       acceptedRanges = frozenList(acceptedRanges);

  /// Avatar of a [MaskStyle.image] mask (REQ-ED-07); may stay set while
  /// another style is chosen, so switching back keeps the picture.
  final MaskAvatar? avatar;

  /// Ranges the user explicitly accepted although tracking did not cover
  /// them (09 §4; 04A E2, E4). `CoverageRange.accepted` is derived from
  /// these.
  final List<TimeRangeUs> acceptedRanges;

  /// Whether `[startUs, endUs)` lies inside an accepted range.
  bool isAccepted(int startUs, int endUs) =>
      acceptedRanges.any((r) => r.covers(startUs, endUs));

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

  /// Head roll at [atUs] in degrees (04A E5 3, E7 Q2): keyframes without a
  /// roll take it from the neighbouring keyframes that have one (linear),
  /// held at the ends; 0 when no keyframe has a roll. Null only outside
  /// the range. Shared by preview and export like [regionAt].
  double? rollAt(int atUs) {
    if (atUs < startUs || atUs >= endUs) return null;
    final keys = [
      for (final k in keyframes)
        if (k.rollDeg != null) k,
    ];
    if (keys.isEmpty) return 0;
    if (atUs <= keys.first.atUs) return keys.first.rollDeg;
    if (atUs >= keys.last.atUs) return keys.last.rollDeg;
    for (var i = 0; i < keys.length - 1; i++) {
      final a = keys[i];
      final b = keys[i + 1];
      if (atUs >= a.atUs && atUs <= b.atUs) {
        final span = b.atUs - a.atUs;
        final t = span == 0 ? 0.0 : (atUs - a.atUs) / span;
        return a.rollDeg! + (b.rollDeg! - a.rollDeg!) * t;
      }
    }
    return keys.last.rollDeg;
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
    List<TimeRangeUs>? acceptedRanges,
    Object? avatar = undefined,
  }) => MaskTrack(
    maskId: maskId ?? this.maskId,
    type: type ?? this.type,
    style: style ?? this.style,
    strength: strength ?? this.strength,
    enabled: enabled ?? this.enabled,
    startUs: startUs ?? this.startUs,
    endUs: endUs ?? this.endUs,
    keyframes: keyframes ?? this.keyframes,
    acceptedRanges: acceptedRanges ?? this.acceptedRanges,
    avatar: pick<MaskAvatar?>(avatar, this.avatar),
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
      listEquals(other.keyframes, keyframes) &&
      listEquals(other.acceptedRanges, acceptedRanges) &&
      other.avatar == avatar;

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
    hashList(acceptedRanges),
    avatar,
  );

  @override
  String toString() =>
      'MaskTrack($maskId, ${type.name}, ${style.name} $strength, '
      'enabled: $enabled, $startUs–$endUs, ${keyframes.length} kf)';
}
