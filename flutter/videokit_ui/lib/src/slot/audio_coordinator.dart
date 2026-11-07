import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// Host helper for the single audio source of a multi-view grid (07 §4,
/// UI-05). The host owns a monotonically increasing audio epoch and sends
/// `SetActiveAudio(active, epoch)`:
///
/// 1. the previous source is muted first and must answer before
/// 2. the new source is unmuted with the same epoch.
///
/// A later [activate] or [muteAll] supersedes an earlier one still in
/// flight (its remaining steps are skipped); a session rejecting a command
/// as stale (lower epoch than it accepted) is left as it is. When the
/// target is released during the switch, or the current source is
/// released ([onReleased]), everything stays muted until the user picks
/// again. The sessions' own state (`activeAudio`, `muted`) is what slots
/// show; [active] is the host's view.
class VideoKitAudioCoordinator extends ChangeNotifier {
  /// Creates a coordinator; [startEpoch] continues an earlier one.
  VideoKitAudioCoordinator({int startEpoch = 0}) : _epoch = startEpoch;

  int _epoch;
  VideoKitSession? _active;
  bool _disposed = false;

  /// Last epoch issued.
  int get epoch => _epoch;

  /// Session ID of the audio source, or null (all muted).
  String? get active => _active?.sessionId;

  /// Makes [target] the only audio source. Returns true when this call
  /// finished as the latest one and [target] accepted.
  Future<bool> activate(VideoKitSession target) async {
    final e = ++_epoch;
    final previous = _active;
    if (previous != null && !identical(previous, target)) {
      await _mute(previous, e);
      if (e != _epoch) return false;
    }
    if (target.state.value.phase == SessionPhase.released) {
      _setActive(null);
      return false;
    }
    final r = await target.execute(SetActiveAudio(true, e));
    if (e != _epoch) return false;
    if (r is! Executed) {
      // The target refused (released, locked, stale): nobody is audible.
      _setActive(null);
      return false;
    }
    await target.execute(const SetMuted(false));
    if (e != _epoch) return false;
    _setActive(target);
    return true;
  }

  /// Mutes the current source; the user picks a new one afterwards.
  Future<void> muteAll() async {
    final e = ++_epoch;
    final previous = _active;
    _setActive(null);
    if (previous != null) await _mute(previous, e);
  }

  /// [sessionId] was released or removed: if it was the source, all stay
  /// muted (07 §4) and a switch still in flight is abandoned.
  void onReleased(String sessionId) {
    if (_active?.sessionId != sessionId) return;
    _epoch++;
    _setActive(null);
  }

  /// The source lost audio by itself (another app took the system audio
  /// focus, `AUDIO_FOCUS_LOST`): all stay muted until the user picks again.
  void onAudioLost(String sessionId) => onReleased(sessionId);

  Future<void> _mute(VideoKitSession s, int e) async {
    if (s.state.value.phase == SessionPhase.released) return;
    await s.execute(SetActiveAudio(false, e));
    await s.execute(const SetMuted(true));
  }

  void _setActive(VideoKitSession? s) {
    if (identical(_active, s)) return;
    _active = s;
    if (!_disposed) notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}
