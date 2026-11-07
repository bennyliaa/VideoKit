import 'dart:async';

import 'package:videokit_api/videokit_api.dart';

/// TEST-R3 R3-01 (04A A1): a session starts without the audio
/// (`activeAudio == false`). A single player is its host's only audio
/// source, so once a bind has succeeded it grants itself the audio with
/// `SetActiveAudio(true, epoch)` (07 §4). Multi-view hosts use their
/// coordinator instead and do not create this.
///
/// Grants once per bind: a new bind (phase `binding`) arms it again. Static
/// images, errors and content locks are left alone.
class VkSingleAudioGrant {
  /// Starts watching [session].
  VkSingleAudioGrant(this.session) {
    session.state.addListener(_onState);
    _onState();
  }

  /// Watched session.
  final VideoKitSession session;

  static int _epochs = 0;
  bool _granted = false;
  bool _disposed = false;

  /// Next epoch; monotonic within the process so a later grant is never
  /// older than an earlier one.
  static int nextEpoch() => ++_epochs;

  void _onState() {
    if (_disposed) return;
    final st = session.state.value;
    if (st.phase == SessionPhase.created || st.phase == SessionPhase.binding) {
      _granted = false;
      return;
    }
    if (_granted || st.activeAudio || st.hiddenForLock) return;
    if (!st.phase.isBound) return;
    if (st.mediaKind == MediaKind.imageStatic ||
        st.mediaKind == MediaKind.imageUnknown) {
      return;
    }
    _granted = true;
    unawaited(session.execute(SetActiveAudio(true, nextEpoch())));
  }

  /// Stops watching.
  void dispose() {
    _disposed = true;
    session.state.removeListener(_onState);
  }
}
