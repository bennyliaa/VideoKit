import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// Executes a command (normally `VideoKitSession.execute`).
typedef CommandExecutor = Future<VideoKitCommandResult> Function(
  VideoKitCommand command,
);

/// Requests a host action (normally `VideoKitSession.requestHostAction`).
typedef HostActionExecutor = Future<VideoKitCommandResult> Function(
  String actionId,
);

/// Feedback the owning controller turns into UI (14 §4.3).
@immutable
sealed class DispatchFeedback {
  const DispatchFeedback(this.kind, [this.command]);

  /// Stable kind: the command kind, or `hostAction:<actionId>`.
  final String kind;

  /// Command that produced the feedback (null for host actions).
  final VideoKitCommand? command;
}

/// Show a short hint with the error code's text.
final class RejectedFeedback extends DispatchFeedback {
  /// Creates feedback.
  const RejectedFeedback(super.kind, super.command, this.error);

  /// Error (`INTERNAL_ERROR_REDACTED` for exceptions).
  final VideoKitStableError error;
}

/// Grey out the control and show [reason]; it stays disabled.
final class UnsupportedFeedback extends DispatchFeedback {
  /// Creates feedback.
  const UnsupportedFeedback(super.kind, super.command, this.reason);

  /// Reason.
  final UnsupportedReason reason;
}

/// The session is released: become read-only and show the state view.
final class SessionReleasedFeedback extends DispatchFeedback {
  /// Creates feedback.
  const SessionReleasedFeedback(super.kind, [super.command]);
}

/// Central command dispatch for a UI controller (14 §4.3):
///
/// | Rule | Behaviour |
/// | --- | --- |
/// | debounce | Play/Pause: while one is in flight, only the latest intent is kept and sent afterwards (if it differs). Other kinds and host actions: a repeat while the same kind is in flight is ignored. |
/// | continuous seek | [seekDrag] sends `SeekTo(preview)` at most every [previewSeekInterval] (latest value kept); [seekEnd] sends `SeekTo(closestSync)`; `Superseded` is silent. |
/// | results | `Rejected` → [RejectedFeedback]; `Unsupported` → kind marked unsupported + [UnsupportedFeedback]; `SessionReleased` → [readOnly] + [SessionReleasedFeedback]. |
/// | exceptions | turned into `INTERNAL_ERROR_REDACTED` feedback, never rethrown. |
/// | lifecycle | after [dispose], results are dropped (no feedback, no notify). |
///
/// Notifies listeners when [readOnly] or the unsupported set changes.
class CommandDispatcher extends ChangeNotifier {
  /// Creates a dispatcher.
  CommandDispatcher({
    required this._execute,
    required this._onFeedback,
    this._requestHostAction,
    this.previewSeekInterval = const Duration(milliseconds: 100),
  });

  final CommandExecutor _execute;
  final ValueChanged<DispatchFeedback> _onFeedback;
  final HostActionExecutor? _requestHostAction;

  /// Minimum spacing of preview seeks while dragging (14 §12: ≥ 100 ms).
  final Duration previewSeekInterval;

  final Set<String> _inFlight = {};
  final Map<String, UnsupportedReason> _unsupported = {};
  bool _readOnly = false;
  bool _disposed = false;

  // Play/Pause merge.
  bool _toggleInFlight = false;
  VideoKitCommand? _pendingToggle;
  VideoKitCommand? _lastSentToggle;

  // Seek throttle: a cooldown timer (works under fakeAsync).
  Timer? _cooldown;
  int? _pendingPreviewUs;

  /// Whether the session is released and commands are no longer sent.
  bool get readOnly => _readOnly;

  /// Whether commands of [kind] were reported `Unsupported`.
  bool isUnsupported(String kind) => _unsupported.containsKey(kind);

  /// Reason for an unsupported [kind], if any.
  UnsupportedReason? unsupportedReason(String kind) => _unsupported[kind];

  /// Kind key of a host action.
  static String hostActionKind(String actionId) => 'hostAction:$actionId';

  static bool _isToggle(VideoKitCommand c) => c is Play || c is Pause;

  /// Dispatches [command] under the rules above. Completes with the result,
  /// or null when the command was merged/ignored or the dispatcher was
  /// disposed.
  Future<VideoKitCommandResult?> dispatch(VideoKitCommand command) async {
    if (_disposed) return null;
    if (_readOnly) return const SessionReleased();
    if (command is SeekTo) return _send(command);
    if (_isToggle(command)) return _dispatchToggle(command);
    return _guarded(command.kind, () => _send(command));
  }

  /// Requests a host action (04A I1) with the same in-flight and feedback
  /// rules; `Superseded` (pending duplicate) is silent.
  Future<VideoKitCommandResult?> requestHostAction(String actionId) async {
    final run = _requestHostAction;
    if (_disposed || run == null) return null;
    if (_readOnly) return const SessionReleased();
    final kind = hostActionKind(actionId);
    return _guarded(kind, () => _run(kind, null, () => run(actionId)));
  }

  Future<VideoKitCommandResult?> _guarded(
    String key,
    Future<VideoKitCommandResult?> Function() body,
  ) async {
    if (_inFlight.contains(key)) return null;
    _inFlight.add(key);
    try {
      return await body();
    } finally {
      _inFlight.remove(key);
    }
  }

  Future<VideoKitCommandResult?> _dispatchToggle(
    VideoKitCommand command,
  ) async {
    if (_toggleInFlight) {
      _pendingToggle = command;
      return null;
    }
    _toggleInFlight = true;
    _lastSentToggle = command;
    VideoKitCommandResult? result;
    try {
      result = await _send(command);
    } finally {
      _toggleInFlight = false;
    }
    final pending = _pendingToggle;
    _pendingToggle = null;
    if (pending != null && pending != _lastSentToggle && !_disposed) {
      return _dispatchToggle(pending);
    }
    return result;
  }

  /// Play when [play] is true, else pause (merged per the debounce rule).
  Future<VideoKitCommandResult?> setPlaying(bool play) =>
      dispatch(play ? const Play() : const Pause());

  /// Drag update: throttled `SeekTo(preview)`; the latest value during a
  /// cooldown is sent when it ends.
  void seekDrag(int positionUs) {
    if (_disposed || _readOnly) return;
    if (_cooldown != null) {
      _pendingPreviewUs = positionUs;
      return;
    }
    _sendPreview(positionUs);
  }

  void _sendPreview(int positionUs) {
    unawaited(_send(SeekTo(positionUs, mode: SeekMode.preview)));
    _cooldown = Timer(previewSeekInterval, () {
      _cooldown = null;
      final us = _pendingPreviewUs;
      _pendingPreviewUs = null;
      if (us != null && !_disposed && !_readOnly) _sendPreview(us);
    });
  }

  /// Drag end: cancels pending previews and sends the final seek.
  Future<VideoKitCommandResult?> seekEnd(
    int positionUs, {
    SeekMode mode = SeekMode.closestSync,
  }) {
    _cooldown?.cancel();
    _cooldown = null;
    _pendingPreviewUs = null;
    return dispatch(SeekTo(positionUs, mode: mode));
  }

  Future<VideoKitCommandResult?> _send(VideoKitCommand command) =>
      _run(command.kind, command, () => _execute(command));

  Future<VideoKitCommandResult?> _run(
    String kind,
    VideoKitCommand? command,
    Future<VideoKitCommandResult> Function() call,
  ) async {
    VideoKitCommandResult result;
    try {
      result = await call();
    } catch (_) {
      result = const Rejected(
        VideoKitStableError.internal(diagnostic: 'dispatch_exception'),
      );
    }
    if (_disposed) return null;
    switch (result) {
      case Executed() || Superseded():
        break;
      case Rejected(:final error):
        _onFeedback(RejectedFeedback(kind, command, error));
      case Unsupported(:final reason):
        if (_unsupported[kind] != reason) {
          _unsupported[kind] = reason;
          notifyListeners();
        }
        _onFeedback(UnsupportedFeedback(kind, command, reason));
      case SessionReleased():
        if (!_readOnly) {
          _readOnly = true;
          _cooldown?.cancel();
          notifyListeners();
        }
        _onFeedback(SessionReleasedFeedback(kind, command));
    }
    return result;
  }

  @override
  void dispose() {
    _disposed = true;
    _cooldown?.cancel();
    _cooldown = null;
    super.dispose();
  }
}
