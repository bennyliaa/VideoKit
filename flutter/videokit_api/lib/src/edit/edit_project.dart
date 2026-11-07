import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../export/export_request.dart';
import '../export/export_result.dart';
import '../export/precheck.dart';
import '../media/media_source.dart';
import '../session/session.dart';
import '../util/collections.dart';
import '../util/undefined.dart';
import 'edit_command.dart';
import 'edit_state.dart';
import 'tracking.dart';

/// Edit project options (04 §2 `EditProjectConfig`).
@immutable
final class EditProjectConfig {
  /// Creates a config.
  EditProjectConfig({
    this.debugLabel,
    List<String> allowedPresetIds = ExportPresets.all,
    this.undoLimit = 100,
  }) : allowedPresetIds = frozenList(allowedPresetIds);

  /// Label for diagnostics.
  final String? debugLabel;

  /// Export presets the host allows.
  final List<String> allowedPresetIds;

  /// Undo stack limit (final value frozen in M4).
  final int undoLimit;

  /// Returns a copy with the given fields replaced.
  EditProjectConfig copyWith({
    Object? debugLabel = undefined,
    List<String>? allowedPresetIds,
    int? undoLimit,
  }) => EditProjectConfig(
    debugLabel: pick<String?>(debugLabel, this.debugLabel),
    allowedPresetIds: allowedPresetIds ?? this.allowedPresetIds,
    undoLimit: undoLimit ?? this.undoLimit,
  );

  @override
  bool operator ==(Object other) =>
      other is EditProjectConfig &&
      other.debugLabel == debugLabel &&
      listEquals(other.allowedPresetIds, allowedPresetIds) &&
      other.undoLimit == undoLimit;

  @override
  int get hashCode =>
      Object.hash(debugLabel, hashList(allowedPresetIds), undoLimit);

  @override
  String toString() =>
      'EditProjectConfig($debugLabel, presets: $allowedPresetIds, '
      'undo: $undoLimit)';
}

/// Versioned JSON snapshot of an edit project (08 §2.1).
@immutable
final class SerializedEditProject {
  /// Creates a snapshot.
  const SerializedEditProject({
    required this.schemaVersion,
    required this.json,
  });

  /// Current schema major version.
  static const int currentSchemaVersion = 1;

  /// Schema major version.
  final int schemaVersion;

  /// JSON text.
  final String json;

  /// Returns a copy with the given fields replaced.
  SerializedEditProject copyWith({int? schemaVersion, String? json}) =>
      SerializedEditProject(
        schemaVersion: schemaVersion ?? this.schemaVersion,
        json: json ?? this.json,
      );

  @override
  bool operator ==(Object other) =>
      other is SerializedEditProject &&
      other.schemaVersion == schemaVersion &&
      other.json == json;

  @override
  int get hashCode => Object.hash(schemaVersion, json);

  @override
  String toString() =>
      'SerializedEditProject(v$schemaVersion, ${json.length} chars)';
}

/// Handle to an added source (04 §6 `SourceToken`).
@immutable
final class SourceToken {
  /// Creates a token.
  const SourceToken({required this.sourceId, required this.mediaToken});

  /// Project-local source ID.
  final String sourceId;

  /// Host media token.
  final String mediaToken;

  /// Returns a copy with the given fields replaced.
  SourceToken copyWith({String? sourceId, String? mediaToken}) => SourceToken(
    sourceId: sourceId ?? this.sourceId,
    mediaToken: mediaToken ?? this.mediaToken,
  );

  @override
  bool operator ==(Object other) =>
      other is SourceToken &&
      other.sourceId == sourceId &&
      other.mediaToken == mediaToken;

  @override
  int get hashCode => Object.hash(sourceId, mediaToken);

  @override
  String toString() => 'SourceToken($sourceId, $mediaToken)';
}

/// One-shot edit project event.
@immutable
sealed class VideoKitEditEvent {
  const VideoKitEditEvent();
}

/// A tracking run finished (completed, cancelled or failed).
final class TrackingFinished extends VideoKitEditEvent {
  /// Creates the event.
  const TrackingFinished(this.maskId, this.status, {this.error});

  /// Mask ID.
  final String maskId;

  /// Final status.
  final TrackingRunStatus status;

  /// Error when failed.
  final VideoKitStableError? error;

  @override
  bool operator ==(Object other) =>
      other is TrackingFinished &&
      other.maskId == maskId &&
      other.status == status &&
      other.error == error;

  @override
  int get hashCode => Object.hash(TrackingFinished, maskId, status, error);

  @override
  String toString() => 'TrackingFinished($maskId, ${status.name}, $error)';
}

/// An export finished (confirmation of cancel included, 08 §6).
final class ExportFinished extends VideoKitEditEvent {
  /// Creates the event.
  const ExportFinished(this.result);

  /// Result.
  final VideoKitExportResult result;

  @override
  bool operator ==(Object other) =>
      other is ExportFinished && other.result == result;

  @override
  int get hashCode => Object.hash(ExportFinished, result);

  @override
  String toString() => 'ExportFinished($result)';
}

/// Short-lived notice for the editor UI.
final class EditNotice extends VideoKitEditEvent {
  /// Creates the event.
  const EditNotice(this.code);

  /// Notice code.
  final String code;

  @override
  bool operator ==(Object other) => other is EditNotice && other.code == code;

  @override
  int get hashCode => Object.hash(EditNotice, code);

  @override
  String toString() => 'EditNotice($code)';
}

/// Edit project (04 §6). Sources are read-only; output goes only to the
/// host sink.
abstract interface class VideoKitEditProject {
  /// Project ID.
  String get projectId;

  /// State.
  ValueListenable<VideoKitEditState> get state;

  /// Events.
  Stream<VideoKitEditEvent> get events;

  /// Driven by demo data.
  bool get isDemo;

  /// Adds and probes a source.
  Future<SourceToken> addSource(VideoKitMediaSource source);

  /// Applies an edit command.
  Future<EditCommandResult> apply(VideoKitEditCommand command);

  /// Undo.
  Future<EditCommandResult> undo();

  /// Redo.
  Future<EditCommandResult> redo();

  /// Serialises the project.
  Future<SerializedEditProject> snapshot();

  /// Preview session sharing the export plan. Same instance on repeated
  /// calls; released with the project.
  Future<VideoKitSession> previewSession();

  /// Detects tracking candidates (faces) at [atUs] (Dart addition, see
  /// report).
  Future<CandidateDetectionResult> detectCandidates(int atUs);

  /// Export precheck.
  Future<ExportPrecheck> checkExport(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  );

  /// Exports; completes when finished, failed or cancelled.
  Future<VideoKitExportResult> export(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  );

  /// Cancels the export [exportId]; unknown IDs are ignored.
  Future<void> cancelExport(String exportId);

  /// Releases the project and its preview session. Idempotent.
  Future<void> close();
}
