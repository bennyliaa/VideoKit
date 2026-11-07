import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../error/unsupported_reason.dart';
import '../util/undefined.dart';
import 'mask.dart';
import 'tracking.dart';

/// Edit command (14 §3.3, 08 §2.2). Continuous gestures submit one command
/// at gesture end (14 §6.3).
@immutable
sealed class VideoKitEditCommand {
  const VideoKitEditCommand();

  /// Whether a successful application is pushed on the undo stack.
  bool get undoable => true;
}

/// Append/insert a clip `[inUs, outUs)` of [sourceId] at [index] (null =
/// end).
final class AddClip extends VideoKitEditCommand {
  /// Creates the command.
  const AddClip(this.sourceId, this.inUs, this.outUs, {this.index});

  /// Source ID.
  final String sourceId;

  /// In (µs).
  final int inUs;

  /// Out (µs).
  final int outUs;

  /// Insert index, null = append.
  final int? index;

  /// Returns a copy with the given fields replaced.
  AddClip copyWith({
    String? sourceId,
    int? inUs,
    int? outUs,
    Object? index = undefined,
  }) => AddClip(
    sourceId ?? this.sourceId,
    inUs ?? this.inUs,
    outUs ?? this.outUs,
    index: pick<int?>(index, this.index),
  );

  @override
  bool operator ==(Object other) =>
      other is AddClip &&
      other.sourceId == sourceId &&
      other.inUs == inUs &&
      other.outUs == outUs &&
      other.index == index;

  @override
  int get hashCode => Object.hash(AddClip, sourceId, inUs, outUs, index);

  @override
  String toString() => 'AddClip($sourceId, $inUs–$outUs, at: $index)';
}

/// Split [clipId] at output time [atUs] (08 `SplitClip`).
final class SplitAt extends VideoKitEditCommand {
  /// Creates the command.
  const SplitAt(this.clipId, this.atUs);

  /// Clip ID.
  final String clipId;

  /// Output-timeline time (µs).
  final int atUs;

  /// Returns a copy with the given fields replaced.
  SplitAt copyWith({String? clipId, int? atUs}) =>
      SplitAt(clipId ?? this.clipId, atUs ?? this.atUs);

  @override
  bool operator ==(Object other) =>
      other is SplitAt && other.clipId == clipId && other.atUs == atUs;

  @override
  int get hashCode => Object.hash(SplitAt, clipId, atUs);

  @override
  String toString() => 'SplitAt($clipId, $atUs)';
}

/// Set source in/out points of [clipId].
final class TrimClip extends VideoKitEditCommand {
  /// Creates the command.
  const TrimClip(this.clipId, this.inUs, this.outUs);

  /// Clip ID.
  final String clipId;

  /// New in (µs).
  final int inUs;

  /// New out (µs).
  final int outUs;

  /// Returns a copy with the given fields replaced.
  TrimClip copyWith({String? clipId, int? inUs, int? outUs}) =>
      TrimClip(clipId ?? this.clipId, inUs ?? this.inUs, outUs ?? this.outUs);

  @override
  bool operator ==(Object other) =>
      other is TrimClip &&
      other.clipId == clipId &&
      other.inUs == inUs &&
      other.outUs == outUs;

  @override
  int get hashCode => Object.hash(TrimClip, clipId, inUs, outUs);

  @override
  String toString() => 'TrimClip($clipId, $inUs–$outUs)';
}

/// Remove [clipId].
final class RemoveClip extends VideoKitEditCommand {
  /// Creates the command.
  const RemoveClip(this.clipId);

  /// Clip ID.
  final String clipId;

  /// Returns a copy with the given fields replaced.
  RemoveClip copyWith({String? clipId}) => RemoveClip(clipId ?? this.clipId);

  @override
  bool operator ==(Object other) =>
      other is RemoveClip && other.clipId == clipId;

  @override
  int get hashCode => Object.hash(RemoveClip, clipId);

  @override
  String toString() => 'RemoveClip($clipId)';
}

/// Move [clipId] to [toIndex].
final class MoveClip extends VideoKitEditCommand {
  /// Creates the command.
  const MoveClip(this.clipId, this.toIndex);

  /// Clip ID.
  final String clipId;

  /// Target index.
  final int toIndex;

  /// Returns a copy with the given fields replaced.
  MoveClip copyWith({String? clipId, int? toIndex}) =>
      MoveClip(clipId ?? this.clipId, toIndex ?? this.toIndex);

  @override
  bool operator ==(Object other) =>
      other is MoveClip && other.clipId == clipId && other.toIndex == toIndex;

  @override
  int get hashCode => Object.hash(MoveClip, clipId, toIndex);

  @override
  String toString() => 'MoveClip($clipId → $toIndex)';
}

/// Add a mask covering `[startUs, endUs)` with an initial keyframe at
/// [startUs]. The new mask ID is returned in `EditApplied.createdId`.
final class AddMask extends VideoKitEditCommand {
  /// Creates the command.
  const AddMask(
    this.type,
    this.region,
    this.startUs,
    this.endUs, {
    this.style = MaskStyle.mosaic,
    this.strength = 0.5,
  });

  /// Type.
  final MaskType type;

  /// Initial region.
  final NormalizedRect region;

  /// Start (µs).
  final int startUs;

  /// End (µs).
  final int endUs;

  /// Style.
  final MaskStyle style;

  /// Strength 0–1.
  final double strength;

  /// Returns a copy with the given fields replaced.
  AddMask copyWith({
    MaskType? type,
    NormalizedRect? region,
    int? startUs,
    int? endUs,
    MaskStyle? style,
    double? strength,
  }) => AddMask(
    type ?? this.type,
    region ?? this.region,
    startUs ?? this.startUs,
    endUs ?? this.endUs,
    style: style ?? this.style,
    strength: strength ?? this.strength,
  );

  @override
  bool operator ==(Object other) =>
      other is AddMask &&
      other.type == type &&
      other.region == region &&
      other.startUs == startUs &&
      other.endUs == endUs &&
      other.style == style &&
      other.strength == strength;

  @override
  int get hashCode =>
      Object.hash(AddMask, type, region, startUs, endUs, style, strength);

  @override
  String toString() =>
      'AddMask(${type.name}, $region, $startUs–$endUs, ${style.name} $strength)';
}

/// Create/update the user keyframe of [maskId] at [atUs].
final class UpdateMaskKeyframe extends VideoKitEditCommand {
  /// Creates the command.
  const UpdateMaskKeyframe(this.maskId, this.atUs, this.region);

  /// Mask ID.
  final String maskId;

  /// Time (µs).
  final int atUs;

  /// Region.
  final NormalizedRect region;

  /// Returns a copy with the given fields replaced.
  UpdateMaskKeyframe copyWith({
    String? maskId,
    int? atUs,
    NormalizedRect? region,
  }) => UpdateMaskKeyframe(
    maskId ?? this.maskId,
    atUs ?? this.atUs,
    region ?? this.region,
  );

  @override
  bool operator ==(Object other) =>
      other is UpdateMaskKeyframe &&
      other.maskId == maskId &&
      other.atUs == atUs &&
      other.region == region;

  @override
  int get hashCode => Object.hash(UpdateMaskKeyframe, maskId, atUs, region);

  @override
  String toString() => 'UpdateMaskKeyframe($maskId, $atUs, $region)';
}

/// Remove the keyframe of [maskId] at [atUs].
final class RemoveMaskKeyframe extends VideoKitEditCommand {
  /// Creates the command.
  const RemoveMaskKeyframe(this.maskId, this.atUs);

  /// Mask ID.
  final String maskId;

  /// Time (µs).
  final int atUs;

  /// Returns a copy with the given fields replaced.
  RemoveMaskKeyframe copyWith({String? maskId, int? atUs}) =>
      RemoveMaskKeyframe(maskId ?? this.maskId, atUs ?? this.atUs);

  @override
  bool operator ==(Object other) =>
      other is RemoveMaskKeyframe &&
      other.maskId == maskId &&
      other.atUs == atUs;

  @override
  int get hashCode => Object.hash(RemoveMaskKeyframe, maskId, atUs);

  @override
  String toString() => 'RemoveMaskKeyframe($maskId, $atUs)';
}

/// Set style and strength of [maskId].
final class SetMaskStyle extends VideoKitEditCommand {
  /// Creates the command.
  const SetMaskStyle(this.maskId, this.style, this.strength);

  /// Mask ID.
  final String maskId;

  /// Style.
  final MaskStyle style;

  /// Strength 0–1.
  final double strength;

  /// Returns a copy with the given fields replaced.
  SetMaskStyle copyWith({String? maskId, MaskStyle? style, double? strength}) =>
      SetMaskStyle(
        maskId ?? this.maskId,
        style ?? this.style,
        strength ?? this.strength,
      );

  @override
  bool operator ==(Object other) =>
      other is SetMaskStyle &&
      other.maskId == maskId &&
      other.style == style &&
      other.strength == strength;

  @override
  int get hashCode => Object.hash(SetMaskStyle, maskId, style, strength);

  @override
  String toString() => 'SetMaskStyle($maskId, ${style.name}, $strength)';
}

/// Enable/disable [maskId].
final class SetMaskEnabled extends VideoKitEditCommand {
  /// Creates the command.
  const SetMaskEnabled(this.maskId, this.enabled);

  /// Mask ID.
  final String maskId;

  /// Enabled.
  final bool enabled;

  /// Returns a copy with the given fields replaced.
  SetMaskEnabled copyWith({String? maskId, bool? enabled}) =>
      SetMaskEnabled(maskId ?? this.maskId, enabled ?? this.enabled);

  @override
  bool operator ==(Object other) =>
      other is SetMaskEnabled &&
      other.maskId == maskId &&
      other.enabled == enabled;

  @override
  int get hashCode => Object.hash(SetMaskEnabled, maskId, enabled);

  @override
  String toString() => 'SetMaskEnabled($maskId, $enabled)';
}

/// Remove [maskId].
final class RemoveMask extends VideoKitEditCommand {
  /// Creates the command.
  const RemoveMask(this.maskId);

  /// Mask ID.
  final String maskId;

  /// Returns a copy with the given fields replaced.
  RemoveMask copyWith({String? maskId}) => RemoveMask(maskId ?? this.maskId);

  @override
  bool operator ==(Object other) =>
      other is RemoveMask && other.maskId == maskId;

  @override
  int get hashCode => Object.hash(RemoveMask, maskId);

  @override
  String toString() => 'RemoveMask($maskId)';
}

/// Start automatic tracking of [maskId] from [atUs] seeded with
/// [seedRegion] (a picked face candidate or a user box). Not undoable.
final class StartTracking extends VideoKitEditCommand {
  /// Creates the command.
  const StartTracking(this.maskId, this.kind, this.atUs, this.seedRegion);

  /// Mask ID (an automatic mask added with [AddMask]).
  final String maskId;

  /// Kind.
  final TrackingKind kind;

  /// Seed time (µs).
  final int atUs;

  /// Seed region.
  final NormalizedRect seedRegion;

  @override
  bool get undoable => false;

  /// Returns a copy with the given fields replaced.
  StartTracking copyWith({
    String? maskId,
    TrackingKind? kind,
    int? atUs,
    NormalizedRect? seedRegion,
  }) => StartTracking(
    maskId ?? this.maskId,
    kind ?? this.kind,
    atUs ?? this.atUs,
    seedRegion ?? this.seedRegion,
  );

  @override
  bool operator ==(Object other) =>
      other is StartTracking &&
      other.maskId == maskId &&
      other.kind == kind &&
      other.atUs == atUs &&
      other.seedRegion == seedRegion;

  @override
  int get hashCode =>
      Object.hash(StartTracking, maskId, kind, atUs, seedRegion);

  @override
  String toString() =>
      'StartTracking($maskId, ${kind.name}, $atUs, $seedRegion)';
}

/// Re-specify the target at [atUs]; results after it are invalidated and
/// recomputed (09 §3). The correction keyframe itself is undoable.
final class CorrectTracking extends VideoKitEditCommand {
  /// Creates the command.
  const CorrectTracking(this.maskId, this.atUs, this.region);

  /// Mask ID.
  final String maskId;

  /// Time (µs).
  final int atUs;

  /// Corrected region.
  final NormalizedRect region;

  /// Returns a copy with the given fields replaced.
  CorrectTracking copyWith({
    String? maskId,
    int? atUs,
    NormalizedRect? region,
  }) => CorrectTracking(
    maskId ?? this.maskId,
    atUs ?? this.atUs,
    region ?? this.region,
  );

  @override
  bool operator ==(Object other) =>
      other is CorrectTracking &&
      other.maskId == maskId &&
      other.atUs == atUs &&
      other.region == region;

  @override
  int get hashCode => Object.hash(CorrectTracking, maskId, atUs, region);

  @override
  String toString() => 'CorrectTracking($maskId, $atUs, $region)';
}

/// Cancel tracking of [maskId]. Not undoable.
final class CancelTracking extends VideoKitEditCommand {
  /// Creates the command.
  const CancelTracking(this.maskId);

  /// Mask ID.
  final String maskId;

  @override
  bool get undoable => false;

  /// Returns a copy with the given fields replaced.
  CancelTracking copyWith({String? maskId}) =>
      CancelTracking(maskId ?? this.maskId);

  @override
  bool operator ==(Object other) =>
      other is CancelTracking && other.maskId == maskId;

  @override
  int get hashCode => Object.hash(CancelTracking, maskId);

  @override
  String toString() => 'CancelTracking($maskId)';
}

/// Explicitly accept an uncovered interval of [maskId] (09 §4
/// `AcceptTrackingRange`); recorded as an export warning.
final class AcceptTrackingRange extends VideoKitEditCommand {
  /// Creates the command.
  const AcceptTrackingRange(this.maskId, this.startUs, this.endUs);

  /// Mask ID.
  final String maskId;

  /// Start (µs).
  final int startUs;

  /// End (µs).
  final int endUs;

  /// Returns a copy with the given fields replaced.
  AcceptTrackingRange copyWith({String? maskId, int? startUs, int? endUs}) =>
      AcceptTrackingRange(
        maskId ?? this.maskId,
        startUs ?? this.startUs,
        endUs ?? this.endUs,
      );

  @override
  bool operator ==(Object other) =>
      other is AcceptTrackingRange &&
      other.maskId == maskId &&
      other.startUs == startUs &&
      other.endUs == endUs;

  @override
  int get hashCode => Object.hash(AcceptTrackingRange, maskId, startUs, endUs);

  @override
  String toString() => 'AcceptTrackingRange($maskId, $startUs–$endUs)';
}

/// Result of an edit command / undo / redo (04 §6 `EditCommandResult`).
@immutable
sealed class EditCommandResult {
  const EditCommandResult();
}

/// Applied; [revision] is the new project revision. [createdId] carries the
/// ID of a created clip/mask, if any.
final class EditApplied extends EditCommandResult {
  /// Creates the result.
  const EditApplied(this.revision, {this.createdId});

  /// New revision.
  final int revision;

  /// Created entity ID.
  final String? createdId;

  /// Returns a copy with the given fields replaced.
  EditApplied copyWith({int? revision, Object? createdId = undefined}) =>
      EditApplied(
        revision ?? this.revision,
        createdId: pick<String?>(createdId, this.createdId),
      );

  @override
  bool operator ==(Object other) =>
      other is EditApplied &&
      other.revision == revision &&
      other.createdId == createdId;

  @override
  int get hashCode => Object.hash(EditApplied, revision, createdId);

  @override
  String toString() => 'EditApplied(rev: $revision, created: $createdId)';
}

/// Refused (illegal phase, out of range, overlap…).
final class EditRejected extends EditCommandResult {
  /// Creates the result.
  const EditRejected(this.error);

  /// Why.
  final VideoKitStableError error;

  /// Returns a copy with the given fields replaced.
  EditRejected copyWith({VideoKitStableError? error}) =>
      EditRejected(error ?? this.error);

  @override
  bool operator ==(Object other) =>
      other is EditRejected && other.error == error;

  @override
  int get hashCode => Object.hash(EditRejected, error);

  @override
  String toString() => 'EditRejected($error)';
}

/// Not supported by capability (e.g. tracking module missing).
final class EditUnsupported extends EditCommandResult {
  /// Creates the result.
  const EditUnsupported(this.reason);

  /// Why.
  final UnsupportedReason reason;

  /// Returns a copy with the given fields replaced.
  EditUnsupported copyWith({UnsupportedReason? reason}) =>
      EditUnsupported(reason ?? this.reason);

  @override
  bool operator ==(Object other) =>
      other is EditUnsupported && other.reason == reason;

  @override
  int get hashCode => Object.hash(EditUnsupported, reason);

  @override
  String toString() => 'EditUnsupported(${reason.name})';
}

/// The project is released.
final class EditProjectReleased extends EditCommandResult {
  /// Creates the result.
  const EditProjectReleased();

  @override
  bool operator ==(Object other) => other is EditProjectReleased;

  @override
  int get hashCode => (EditProjectReleased).hashCode;

  @override
  String toString() => 'EditProjectReleased()';
}
