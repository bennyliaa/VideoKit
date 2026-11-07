import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../export/export_progress.dart';
import '../util/collections.dart';
import '../util/enum_codec.dart';
import '../util/undefined.dart';
import 'mask.dart';
import 'timeline.dart';
import 'tracking.dart';

/// Edit project phase (04 §6, original §19.2). No unknown value (state
/// machine enum, 14 §3.1).
enum EditPhase {
  created,
  preparing,
  ready,
  tracking,
  exporting,
  completed,
  failed,
  cancelling,
  cancelled,
  releasing,
  released;

  /// Whether editing commands are accepted in this phase.
  bool get acceptsEdits =>
      this == ready || this == completed || this == failed || this == cancelled;

  /// Whether the project is releasing or released.
  bool get isReleasingOrReleased => this == releasing || this == released;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; throws [ArgumentError] when unknown.
  static EditPhase fromName(String name) {
    for (final v in values) {
      if (v.name == name || v.wireName == name) return v;
    }
    throw ArgumentError.value(name, 'name', 'Unknown EditPhase');
  }
}

/// Output estimate; null fields mean "cannot estimate" — never fake numbers
/// (14 §5.6).
@immutable
final class EditEstimate {
  /// Creates an estimate.
  const EditEstimate({this.durationUs, this.sizeBytes});

  /// Unknown estimate.
  static const EditEstimate unknown = EditEstimate();

  /// Output duration (µs).
  final int? durationUs;

  /// Output size (bytes, estimate).
  final int? sizeBytes;

  /// Returns a copy with the given fields replaced.
  EditEstimate copyWith({
    Object? durationUs = undefined,
    Object? sizeBytes = undefined,
  }) => EditEstimate(
    durationUs: pick<int?>(durationUs, this.durationUs),
    sizeBytes: pick<int?>(sizeBytes, this.sizeBytes),
  );

  @override
  bool operator ==(Object other) =>
      other is EditEstimate &&
      other.durationUs == durationUs &&
      other.sizeBytes == sizeBytes;

  @override
  int get hashCode => Object.hash(durationUs, sizeBytes);

  @override
  String toString() => 'EditEstimate($durationUs µs, $sizeBytes B)';
}

/// Read-only edit project view for the UI (14 §3.3).
@immutable
final class VideoKitEditState {
  /// Creates a state.
  VideoKitEditState({
    required this.phase,
    this.revision = 0,
    Timeline? timeline,
    List<MaskTrack> masks = const [],
    Map<String, TrackingRun> tracking = const {},
    this.export,
    this.canUndo = false,
    this.canRedo = false,
    this.estimate = EditEstimate.unknown,
    this.error,
  }) : timeline = timeline ?? Timeline.empty(),
       masks = frozenList(masks),
       tracking = frozenMap(tracking);

  /// Initial state.
  factory VideoKitEditState.initial() =>
      VideoKitEditState(phase: EditPhase.created);

  /// Phase.
  final EditPhase phase;

  /// +1 on every successful edit; async results carry the revision they were
  /// computed on and stale ones are dropped.
  final int revision;

  /// Timeline.
  final Timeline timeline;

  /// Masks.
  final List<MaskTrack> masks;

  /// maskId → tracking run.
  final Map<String, TrackingRun> tracking;

  /// Export progress while exporting/cancelling.
  final ExportProgress? export;

  /// Undo available.
  final bool canUndo;

  /// Redo available.
  final bool canRedo;

  /// Output estimate.
  final EditEstimate estimate;

  /// Last error.
  final VideoKitStableError? error;

  /// Mask by ID, or null.
  MaskTrack? maskById(String maskId) {
    for (final m in masks) {
      if (m.maskId == maskId) return m;
    }
    return null;
  }

  /// Returns a copy with the given fields replaced.
  VideoKitEditState copyWith({
    EditPhase? phase,
    int? revision,
    Timeline? timeline,
    List<MaskTrack>? masks,
    Map<String, TrackingRun>? tracking,
    Object? export = undefined,
    bool? canUndo,
    bool? canRedo,
    EditEstimate? estimate,
    Object? error = undefined,
  }) => VideoKitEditState(
    phase: phase ?? this.phase,
    revision: revision ?? this.revision,
    timeline: timeline ?? this.timeline,
    masks: masks ?? this.masks,
    tracking: tracking ?? this.tracking,
    export: pick<ExportProgress?>(export, this.export),
    canUndo: canUndo ?? this.canUndo,
    canRedo: canRedo ?? this.canRedo,
    estimate: estimate ?? this.estimate,
    error: pick<VideoKitStableError?>(error, this.error),
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitEditState &&
      other.phase == phase &&
      other.revision == revision &&
      other.timeline == timeline &&
      listEquals(other.masks, masks) &&
      mapEquals(other.tracking, tracking) &&
      other.export == export &&
      other.canUndo == canUndo &&
      other.canRedo == canRedo &&
      other.estimate == estimate &&
      other.error == error;

  @override
  int get hashCode => Object.hash(
    phase,
    revision,
    timeline,
    hashList(masks),
    hashMap(tracking),
    export,
    canUndo,
    canRedo,
    estimate,
    error,
  );

  @override
  String toString() =>
      'VideoKitEditState(${phase.name}, rev: $revision, $timeline, '
      'masks: ${masks.length}, tracking: ${tracking.length}, '
      'export: $export, undo: $canUndo, redo: $canRedo, $estimate, '
      'error: ${error?.code.name})';
}
