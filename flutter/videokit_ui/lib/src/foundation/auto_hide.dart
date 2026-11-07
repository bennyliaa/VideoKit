import 'dart:async';

import 'package:flutter/foundation.dart';

/// Reasons that keep controls visible (14 §4.4).
enum AutoHideBlocker {
  /// Not playing (paused, ended, error, loading).
  notPlaying,

  /// Seek bar / gesture drag in progress.
  dragging,

  /// A panel or menu is open.
  panelOpen,

  /// Keyboard focus is inside the controls.
  focusInControls,

  /// A screen reader / accessible navigation is active.
  accessibleNavigation,

  /// The mouse hovers over the controls.
  hovered,

  /// A host action is pending.
  hostActionPending,
}

/// Controls visibility policy (14 §4.4): visible for [delay] after the last
/// interaction (default 3 s), never auto-hidden while any
/// [AutoHideBlocker] is active. Visibility is UI state; listeners forward
/// it to the session/host.
class AutoHidePolicy extends ChangeNotifier {
  /// Creates the policy (initially visible).
  AutoHidePolicy({this.delay = const Duration(seconds: 3)}) {
    _schedule();
  }

  /// Auto-hide delay.
  final Duration delay;

  final Set<AutoHideBlocker> _blockers = {};
  bool _visible = true;
  Timer? _timer;
  bool _disposed = false;

  /// Whether controls are visible.
  bool get visible => _visible;

  /// Active blockers.
  Set<AutoHideBlocker> get blockers => Set.unmodifiable(_blockers);

  /// Whether auto-hide is currently suppressed.
  bool get blocked => _blockers.isNotEmpty;

  /// Sets or clears [blocker]. Clearing the last blocker restarts the timer.
  void setBlocker(AutoHideBlocker blocker, bool active) {
    final changed = active ? _blockers.add(blocker) : _blockers.remove(blocker);
    if (!changed) return;
    if (active) {
      _timer?.cancel();
      _setVisible(true);
    } else {
      _schedule();
    }
  }

  /// User interaction: show and restart the timer.
  void kick() {
    _setVisible(true);
    _schedule();
  }

  /// Tap on the picture: toggles visibility. Hiding is refused while
  /// blocked.
  void toggle() {
    if (_visible) {
      hide();
    } else {
      kick();
    }
  }

  /// Shows controls (host handle).
  void show() => kick();

  /// Hides controls (a tap on the picture); returns whether they were
  /// hidden. "Not playing" only stops the automatic timer: a paused video or
  /// a static image (which never plays) can still be hidden by the user
  /// (M2). The other blockers (panel, drag, focus, screen reader, hover,
  /// pending action) refuse it.
  bool hide() {
    if (_blockers.any((b) => b != AutoHideBlocker.notPlaying)) return false;
    _timer?.cancel();
    _setVisible(false);
    return true;
  }

  void _schedule() {
    _timer?.cancel();
    if (blocked || _disposed) return;
    _timer = Timer(delay, () {
      if (!blocked) _setVisible(false);
    });
  }

  void _setVisible(bool v) {
    if (_visible == v || _disposed) return;
    _visible = v;
    notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    _timer?.cancel();
    super.dispose();
  }
}
