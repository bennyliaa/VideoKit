import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

import 'channel_session.dart';
import 'msg_mapping.dart';

/// [VideoKitEditProject] proxy over the channel (14 §8.5); state is replaced from `EditUpdateMessage`s.
final class ChannelEditProject implements VideoKitEditProject {
  ChannelEditProject({
    required this.projectId,
    required this._api,
    required this.isDemo,
    required this._sessionFor,
  });

  final VideoKitHostApi _api;
  final ChannelSession Function(String sessionId) _sessionFor;

  @override
  final String projectId;

  @override
  final bool isDemo;

  final ValueNotifier<VideoKitEditState> _state = ValueNotifier(
    VideoKitEditState(phase: EditPhase.created),
  );
  final StreamController<VideoKitEditEvent> _events =
      StreamController.broadcast();
  int _lastSeq = 0;
  int _exportCounter = 0;
  bool _closed = false;

  @override
  ValueListenable<VideoKitEditState> get state => _state;

  @override
  Stream<VideoKitEditEvent> get events => _events.stream;

  /// Applies one update from the native stream; returns `false` for duplicates or stale messages.
  bool handleUpdate(EditUpdateMessage message) {
    if (message.seq <= _lastSeq || _closed) return false;
    _lastSeq = message.seq;
    final stateMsg = message.state;
    if (stateMsg != null) _state.value = editStateFromMsg(stateMsg);
    final event = message.event;
    if (event != null) {
      // Only notices are forwarded; tracking and export completion are visible in state and results.
      if (event.type == 'WARNING' && event.code != null) {
        _events.add(EditNotice(event.code!));
      }
      if (event.type == 'TRACKING_LOST') {
        _events.add(const EditNotice('TRACKING_LOST'));
      }
    }
    return true;
  }

  Never _released() => throw const VideoKitException(
    VideoKitStableError(
      code: ErrorCode.sessionReleased,
      stage: ErrorStage.edit,
      diagnostic: 'PROJECT_RELEASED',
    ),
  );

  Future<EditCommandResult> _edit(Future<EditResultMsg> Function() call) async {
    if (_closed) return const EditProjectReleased();
    try {
      return editResultFromMsg(await call());
    } on Object catch (failure) {
      return EditRejected(channelError(failure));
    }
  }

  @override
  Future<SourceToken> addSource(VideoKitMediaSource source) async {
    if (_closed) _released();
    final msg = mediaSourceToMsg(source);
    if (msg == null) {
      throw VideoKitException(
        VideoKitStableError(
          code: ErrorCode.invalidArgument,
          stage: ErrorStage.edit,
          diagnostic: 'DART_SOURCE_NOT_SUPPORTED',
        ),
      );
    }
    final result = await _api.addSource(projectId, msg);
    final id = result.id;
    if (id == null) {
      throw VideoKitException(
        result.error == null
            ? channelError('MissingError')
            : errorFromMsg(result.error!),
      );
    }
    return SourceToken(sourceId: id, mediaToken: source.mediaToken);
  }

  @override
  Future<EditCommandResult> apply(VideoKitEditCommand command) =>
      _edit(() => _api.applyEdit(projectId, editCommandToMsg(command)));

  @override
  Future<EditCommandResult> undo() => _edit(() => _api.undo(projectId));

  @override
  Future<EditCommandResult> redo() => _edit(() => _api.redo(projectId));

  @override
  Future<SerializedEditProject> snapshot() async {
    final msg = await _api.snapshot(projectId);
    if (msg == null) _released();
    return SerializedEditProject(
      schemaVersion: msg.schemaVersion,
      json: msg.json,
    );
  }

  @override
  Future<VideoKitSession> previewSession() async {
    final result = await _api.previewSession(projectId);
    final id = result.id;
    if (id == null) {
      throw VideoKitException(
        result.error == null
            ? channelError('MissingError')
            : errorFromMsg(result.error!),
      );
    }
    return _sessionFor(id);
  }

  @override
  Future<CandidateDetectionResult> detectCandidates(int atUs) async {
    try {
      return candidatesFromMsg(await _api.detectCandidates(projectId, atUs));
    } on Object catch (failure) {
      return CandidateDetectionResult(error: channelError(failure));
    }
  }

  @override
  Future<ExportPrecheck> checkExport(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  ) async => precheckFromMsg(
    await _api.checkExport(
      projectId,
      exportRequestToMsg(request, sink, _nextExportId()),
    ),
  );

  @override
  Future<VideoKitExportResult> export(
    VideoKitExportRequest request,
    VideoKitOutputSink sink,
  ) async {
    final msg = exportRequestToMsg(request, sink, _nextExportId());
    VideoKitExportResult result;
    try {
      result = exportResultFromMsg(await _api.exportProject(projectId, msg));
    } on Object catch (failure) {
      result = ExportFailed(msg.exportId, channelError(failure));
    }
    if (!_closed) _events.add(ExportFinished(result));
    return result;
  }

  String _nextExportId() => '$projectId-export-${++_exportCounter}';

  @override
  Future<void> cancelExport(String exportId) =>
      _api.cancelExport(projectId, exportId);

  @override
  Future<void> close() async {
    if (_closed) return;
    _closed = true;
    try {
      await _api.closeEditProject(projectId);
    } on Object {
      // The native project is released with its engine anyway.
    }
    await _events.close();
  }
}
