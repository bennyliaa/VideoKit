import 'package:flutter/widgets.dart';

import 'backend/app_backend.dart';
import 'history/app_storage.dart';
import 'history/history_store.dart';
import 'settings/app_settings.dart';

/// App services for the widget tree: backend, play history, settings.
class AppScope extends InheritedWidget {
  /// Creates the scope.
  const AppScope({
    super.key,
    required this.backend,
    required this.storage,
    required this.history,
    required this.settings,
    required super.child,
  });

  /// VideoKit backend (M0: Dart Fake).
  final AppBackend backend;

  /// App-private storage (thumbnail images).
  final AppStorage storage;

  /// Play history.
  final HistoryStore history;

  /// Settings.
  final SettingsStore settings;

  /// Nearest scope.
  static AppScope of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppScope>()!;

  @override
  bool updateShouldNotify(AppScope old) =>
      old.backend != backend ||
      old.history != history ||
      old.settings != settings;
}
