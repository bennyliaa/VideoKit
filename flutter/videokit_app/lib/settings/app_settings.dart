import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/app_storage.dart';

/// Home layout.
enum HomeLayout {
  /// One row per record (design page 7 left).
  list,

  /// Two-column grid (design page 7 right).
  grid,
}

/// App settings (REQ-APP-04/08, design page 8).
@immutable
final class AppSettings {
  /// Creates settings.
  const AppSettings({
    this.recordHistory = true,
    this.themeMode = VideoKitThemeMode.dark,
    this.reduceMotion,
    this.layout = HomeLayout.list,
  });

  /// Record the play history (default on).
  final bool recordHistory;

  /// Theme: dark, light or follow system.
  final VideoKitThemeMode themeMode;

  /// Reduced motion; null follows the system setting (default).
  final bool? reduceMotion;

  /// Home list/grid.
  final HomeLayout layout;

  /// Returns a copy with the given fields replaced.
  AppSettings copyWith({
    bool? recordHistory,
    VideoKitThemeMode? themeMode,
    bool? Function()? reduceMotion,
    HomeLayout? layout,
  }) => AppSettings(
    recordHistory: recordHistory ?? this.recordHistory,
    themeMode: themeMode ?? this.themeMode,
    reduceMotion: reduceMotion == null ? this.reduceMotion : reduceMotion(),
    layout: layout ?? this.layout,
  );

  /// JSON form.
  Map<String, Object?> toJson() => {
    'recordHistory': recordHistory,
    'themeMode': themeMode.name,
    'reduceMotion': ?reduceMotion,
    'layout': layout.name,
  };

  /// Parses [json] with defaults for missing or unknown values.
  static AppSettings fromJson(Map<String, Object?> json) => AppSettings(
    recordHistory: json['recordHistory'] as bool? ?? true,
    themeMode:
        VideoKitThemeMode.values
            .where((m) => m.name == json['themeMode'])
            .firstOrNull ??
        VideoKitThemeMode.dark,
    reduceMotion: json['reduceMotion'] as bool?,
    layout:
        HomeLayout.values.where((l) => l.name == json['layout']).firstOrNull ??
        HomeLayout.list,
  );

  @override
  bool operator ==(Object other) =>
      other is AppSettings &&
      other.recordHistory == recordHistory &&
      other.themeMode == themeMode &&
      other.reduceMotion == reduceMotion &&
      other.layout == layout;

  @override
  int get hashCode =>
      Object.hash(recordHistory, themeMode, reduceMotion, layout);
}

/// Persists [AppSettings] in the app-private directory.
class SettingsStore extends ValueNotifier<AppSettings> {
  /// Creates a store.
  SettingsStore(this.storage) : super(const AppSettings());

  /// Document name.
  static const String fileName = 'settings.json';

  /// Storage.
  final AppStorage storage;

  /// Loads saved settings (defaults when missing or broken).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      value = AppSettings.fromJson(jsonDecode(raw) as Map<String, Object?>);
    } on Object {
      value = const AppSettings();
    }
  }

  /// Updates and saves.
  Future<void> update(AppSettings next) async {
    value = next;
    await writeQuietly(storage, fileName, jsonEncode(next.toJson()));
  }
}
