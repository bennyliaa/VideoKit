import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// Saves the project (host side, e.g. `snapshot()` into the App's store);
/// throws when the save failed.
typedef VideoKitAutosave = Future<void> Function();

/// Autosave state shown after the editor title (design page 15).
enum AutosaveStatus {
  /// Nothing edited since the editor opened.
  idle,

  /// Edited; a save follows after the debounce, or is running.
  saving,

  /// The last edit is saved ("已自动保存").
  saved,

  /// The last save failed ("未保存", with retry).
  failed,
}

/// Debounced autosave (UI-AUDIT-A3): every project revision restarts a
/// [delay] timer (2 s); when it fires [save] runs. Edits made while a save
/// runs schedule another save; only the latest outcome is shown. Leaving the
/// editor still saves on the host side.
class EditorAutosave extends ChangeNotifier {
  /// Watches [project].
  EditorAutosave({
    required this.project,
    required this.save,
    this.delay = const Duration(seconds: 2),
  }) : _revision = project.state.value.revision {
    project.state.addListener(_onState);
  }

  /// Project.
  final VideoKitEditProject project;

  /// Host save.
  final VideoKitAutosave save;

  /// Debounce after the last edit.
  final Duration delay;

  int _revision;
  int? _savingRevision;
  Timer? _timer;
  bool _disposed = false;
  AutosaveStatus _status = AutosaveStatus.idle;

  /// Current state.
  AutosaveStatus get status => _status;

  void _set(AutosaveStatus s) {
    if (_disposed || s == _status) return;
    _status = s;
    notifyListeners();
  }

  void _onState() {
    final rev = project.state.value.revision;
    if (rev == _revision) return;
    _revision = rev;
    _timer?.cancel();
    _timer = Timer(delay, () => unawaited(saveNow()));
    _set(AutosaveStatus.saving);
  }

  /// Saves at once (the debounce fired, or "重试" after a failure).
  Future<void> saveNow() async {
    _timer?.cancel();
    _timer = null;
    if (_disposed) return;
    final rev = _revision;
    _savingRevision = rev;
    _set(AutosaveStatus.saving);
    AutosaveStatus outcome;
    try {
      await save();
      outcome = AutosaveStatus.saved;
    } on Object {
      outcome = AutosaveStatus.failed;
    }
    if (_disposed || _savingRevision != rev) return;
    _savingRevision = null;
    // A newer edit is waiting for its own save: keep "正在保存…".
    if (_timer != null && _revision != rev) return;
    _set(outcome);
  }

  @override
  void dispose() {
    _disposed = true;
    _timer?.cancel();
    project.state.removeListener(_onState);
    super.dispose();
  }
}
