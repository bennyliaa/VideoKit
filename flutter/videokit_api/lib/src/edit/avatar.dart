import 'package:flutter/foundation.dart';

import '../media/media_source.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import 'mask.dart';

/// Avatar cut-out availability on this device (04A E6 4).
enum AvatarSupport {
  /// `prepareAvatar` / `refineAvatar` work.
  available,

  /// The cut-out model is not installed; hosts can still supply their own
  /// transparent PNG.
  modelMissing,

  /// The device cannot run the cut-out; host PNGs still work.
  unsupported;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [unsupported].
  static AvatarSupport fromName(String? name) =>
      enumFromName(values, name, unsupported);
}

/// Options of [VideoKitAvatarTools.prepareAvatar] (design page 25).
@immutable
final class AvatarPrepareOptions {
  /// Creates options.
  const AvatarPrepareOptions({
    this.cropToHead = true,
    this.feather = 0.5,
    this.faceIndex,
  });

  /// Crop to the head including hair ("裁到头部（含头发）").
  final bool cropToHead;

  /// Edge softening 0–1 ("边缘柔化").
  final double feather;

  /// Which face when there are several; null = the largest.
  final int? faceIndex;

  /// Returns a copy with the given fields replaced.
  AvatarPrepareOptions copyWith({
    bool? cropToHead,
    double? feather,
    int? faceIndex,
  }) => AvatarPrepareOptions(
    cropToHead: cropToHead ?? this.cropToHead,
    feather: feather ?? this.feather,
    faceIndex: faceIndex ?? this.faceIndex,
  );

  @override
  bool operator ==(Object other) =>
      other is AvatarPrepareOptions &&
      other.cropToHead == cropToHead &&
      other.feather == feather &&
      other.faceIndex == faceIndex;

  @override
  int get hashCode => Object.hash(cropToHead, feather, faceIndex);

  @override
  String toString() =>
      'AvatarPrepareOptions(crop: $cropToHead, feather: $feather, '
      'face: $faceIndex)';
}

/// A prepared avatar: a transparent PNG and where the head is (REQ-ED-07).
/// The host stores [png] and gives it an `avatarToken` (04A E5 1).
@immutable
final class AvatarImage {
  /// Creates an avatar image.
  AvatarImage({
    required this.avatarId,
    required this.png,
    required this.width,
    required this.height,
    required this.headBox,
    this.sourceFaceBox,
    this.feather = 0.5,
    this.cropToHead = true,
    List<String> warnings = const [],
    this.isDemo = false,
  }) : warnings = frozenList(warnings);

  /// ID of this result (Kit generated).
  final String avatarId;

  /// Transparent PNG (RGBA).
  final Uint8List png;

  /// PNG width in pixels.
  final int width;

  /// PNG height in pixels.
  final int height;

  /// Head box inside the PNG (normalized); aligned to the tracked box.
  final MaskRegion headBox;

  /// Face box in the original picture (normalized), for the "原图" view.
  final MaskRegion? sourceFaceBox;

  /// Edge softening in effect.
  final double feather;

  /// Whether the result was cropped to the head.
  final bool cropToHead;

  /// Warnings (e.g. [multipleFaces]); unknown values are ignored.
  final List<String> warnings;

  /// Fake / demo result (a synthetic picture).
  final bool isDemo;

  /// Warning: the picture has several faces.
  static const String multipleFaces = 'MULTIPLE_FACES';

  /// Warning: the cut-out is uncertain.
  static const String lowConfidence = 'LOW_CONFIDENCE';

  /// Returns a copy with the given fields replaced.
  AvatarImage copyWith({
    Uint8List? png,
    int? width,
    int? height,
    MaskRegion? headBox,
    double? feather,
    bool? cropToHead,
  }) => AvatarImage(
    avatarId: avatarId,
    png: png ?? this.png,
    width: width ?? this.width,
    height: height ?? this.height,
    headBox: headBox ?? this.headBox,
    sourceFaceBox: sourceFaceBox,
    feather: feather ?? this.feather,
    cropToHead: cropToHead ?? this.cropToHead,
    warnings: warnings,
    isDemo: isDemo,
  );

  @override
  bool operator ==(Object other) =>
      other is AvatarImage &&
      other.avatarId == avatarId &&
      listEquals(other.png, png) &&
      other.width == width &&
      other.height == height &&
      other.headBox == headBox &&
      other.sourceFaceBox == sourceFaceBox &&
      other.feather == feather &&
      other.cropToHead == cropToHead &&
      listEquals(other.warnings, warnings) &&
      other.isDemo == isDemo;

  @override
  int get hashCode => Object.hash(
    avatarId,
    png.length,
    width,
    height,
    headBox,
    sourceFaceBox,
    feather,
    cropToHead,
    hashList(warnings),
    isDemo,
  );

  @override
  String toString() =>
      'AvatarImage($avatarId, ${width}x$height, head: $headBox, '
      'demo: $isDemo)';
}

/// Brush of an [AvatarStroke] ("擦除" / "恢复").
enum AvatarBrush {
  /// Make pixels transparent.
  erase,

  /// Bring back the original pixels.
  restore;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [erase].
  static AvatarBrush fromName(String? name) =>
      enumFromName(values, name, erase);
}

/// One brush stroke on the avatar PNG (normalized coordinates).
@immutable
final class AvatarStroke {
  /// Creates a stroke.
  AvatarStroke({
    required this.brush,
    required List<(double, double)> points,
    required this.radius,
  }) : points = frozenList(points);

  /// Erase or restore.
  final AvatarBrush brush;

  /// Points `(x, y)`, normalized to the PNG.
  final List<(double, double)> points;

  /// Brush radius, normalized to the PNG width ("笔刷大小").
  final double radius;

  @override
  bool operator ==(Object other) =>
      other is AvatarStroke &&
      other.brush == brush &&
      listEquals(other.points, points) &&
      other.radius == radius;

  @override
  int get hashCode => Object.hash(brush, hashList(points), radius);

  @override
  String toString() =>
      'AvatarStroke(${brush.name}, ${points.length} pts, r: $radius)';
}

/// What the editor asks the host for when the user taps "更换头像"
/// (04A E6 5).
@immutable
final class AvatarRequest {
  /// Creates a request.
  const AvatarRequest({
    required this.projectId,
    required this.maskId,
    this.currentToken,
  });

  /// Edit project.
  final String projectId;

  /// Mask that gets the avatar.
  final String maskId;

  /// The avatar the mask has now, if any.
  final String? currentToken;

  @override
  bool operator ==(Object other) =>
      other is AvatarRequest &&
      other.projectId == projectId &&
      other.maskId == maskId &&
      other.currentToken == currentToken;

  @override
  int get hashCode => Object.hash(projectId, maskId, currentToken);

  @override
  String toString() => 'AvatarRequest($projectId, $maskId)';
}

/// Optional avatar cut-out tools of a Kit (REQ-ED-07, 04A E5/E6): a host
/// may use them to prepare a picture, or supply its own transparent PNG.
/// Check `kit is VideoKitAvatarTools` and
/// `VideoKitCapabilities.avatar == AvatarSupport.available`. Everything
/// runs on the device; nothing is uploaded.
abstract interface class VideoKitAvatarTools {
  /// Finds the face in [image], crops to the head (with hair), removes the
  /// background and softens the edge. Throws `VideoKitException` with
  /// `AVATAR_NO_FACE` or `AVATAR_IMAGE_UNSUPPORTED`.
  Future<AvatarImage> prepareAvatar(
    VideoKitMediaSource image, {
    AvatarPrepareOptions options = const AvatarPrepareOptions(),
  });

  /// Erases / restores edge pixels along [strokes] and re-applies the
  /// softening ([feather], default: the avatar's). Does not re-detect.
  Future<AvatarImage> refineAvatar(
    AvatarImage avatar,
    List<AvatarStroke> strokes, {
    double? feather,
  });

  /// Number of Kit built-in avatars (`builtin:1` … `builtin:N`, 04A E5 5).
  int get builtinAvatarCount;

  /// PNG of built-in avatar [index] (1-based), for hosts to show it.
  Future<Uint8List> builtinAvatar(int index);
}
