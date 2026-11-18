import 'package:flutter/widgets.dart';

import 'avatar/avatar_store.dart';
import 'backend/app_backend.dart';
import 'entitlement/entitlement_service.dart';
import 'history/app_storage.dart';
import 'history/history_store.dart';
import 'library/library_lock.dart';
import 'library/library_store.dart';
import 'projects/export_journal.dart';
import 'projects/project_store.dart';
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
    required this.projects,
    required this.avatars,
    required this.exportJournal,
    required this.library,
    required this.libraryLock,
    required this.entitlements,
    required super.child,
  });

  /// What the user may use (REQ-APP-15; VK-A2: always subscribed).
  final EntitlementService entitlements;

  /// Media library index (REQ-APP-09–13).
  final LibraryStore library;

  /// Media library lock and settings (REQ-APP-10).
  final LibraryLock libraryLock;

  /// The export in progress (M6-A1).
  final ExportJournal exportJournal;

  /// The App's avatars (REQ-ED-07, M5A).
  final AvatarStore avatars;

  /// VideoKit backend (M0: Dart Fake).
  final AppBackend backend;

  /// App-private storage (thumbnail images).
  final AppStorage storage;

  /// Play history.
  final HistoryStore history;

  /// Settings.
  final SettingsStore settings;

  /// Saved edit projects ("最近工程", M4).
  final ProjectStore projects;

  /// Nearest scope.
  static AppScope of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppScope>()!;

  @override
  bool updateShouldNotify(AppScope old) =>
      old.backend != backend ||
      old.history != history ||
      old.settings != settings ||
      old.projects != projects ||
      old.avatars != avatars ||
      old.exportJournal != exportJournal ||
      old.library != library ||
      old.libraryLock != libraryLock ||
      old.entitlements != entitlements;
}
