import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../history/app_storage.dart';

/// One saved edit project ("最近工程", M4, App business).
@immutable
final class RecentProject {
  /// Creates an entry.
  const RecentProject({
    required this.id,
    required this.savedAtEpochMs,
    required this.clipCount,
    required this.snapshot,
    this.durationUs,
  });

  /// App ID (stable across saves of the same project).
  final String id;

  /// Last save.
  final int savedAtEpochMs;

  /// Clips on the timeline when saved.
  final int clipCount;

  /// Output duration, if the project estimated it.
  final int? durationUs;

  /// `VideoKitEditProject.snapshot()` (08 §2.1).
  final SerializedEditProject snapshot;

  /// JSON form.
  Map<String, Object?> toJson() => {
    'id': id,
    'savedAtEpochMs': savedAtEpochMs,
    'clipCount': clipCount,
    'durationUs': ?durationUs,
    'schemaVersion': snapshot.schemaVersion,
    'snapshot': snapshot.json,
  };

  /// Parses [json]; null when broken (never fatal). An entry written before
  /// the App recorded `schemaVersion` beside the snapshot (M4-A2) takes it
  /// from the snapshot's own JSON; the module migrates it on restore.
  static RecentProject? fromJson(Map<String, Object?> json) {
    try {
      final snapshot = json['snapshot']! as String;
      final version =
          (json['schemaVersion'] as num?)?.toInt() ??
          _embeddedSchemaVersion(snapshot);
      if (version == null) return null;
      return RecentProject(
        id: json['id']! as String,
        savedAtEpochMs: (json['savedAtEpochMs']! as num).toInt(),
        clipCount: (json['clipCount']! as num).toInt(),
        durationUs: (json['durationUs'] as num?)?.toInt(),
        snapshot: SerializedEditProject(schemaVersion: version, json: snapshot),
      );
    } on Object {
      return null;
    }
  }

  static int? _embeddedSchemaVersion(String snapshot) {
    try {
      final j = jsonDecode(snapshot);
      return j is Map ? (j['schemaVersion'] as num?)?.toInt() : null;
    } on Object {
      return null;
    }
  }

  /// Whether the snapshot was written by an older module schema (restore
  /// migrates it; the App saves the migrated form back).
  bool get needsMigration =>
      snapshot.schemaVersion < SerializedEditProject.currentSchemaVersion;

  @override
  bool operator ==(Object other) =>
      other is RecentProject &&
      other.id == id &&
      other.savedAtEpochMs == savedAtEpochMs &&
      other.clipCount == clipCount &&
      other.durationUs == durationUs &&
      other.snapshot == snapshot;

  @override
  int get hashCode =>
      Object.hash(id, savedAtEpochMs, clipCount, durationUs, snapshot);
}

/// Saved edit projects, newest first, at most [limit] (App-private file
/// `projects.json`). The snapshots are the module's own JSON; the App never
/// reads inside them.
class ProjectStore extends ChangeNotifier {
  /// Creates the store.
  ProjectStore({required this.storage, DateTime Function()? now})
    : now = now ?? DateTime.now;

  /// Storage.
  final AppStorage storage;

  /// Clock.
  final DateTime Function() now;

  /// File name.
  static const String fileName = 'projects.json';

  /// Kept projects.
  static const int limit = 20;

  List<RecentProject> _projects = const [];
  int _counter = 0;

  /// Projects, newest first.
  List<RecentProject> get projects => _projects;

  /// Loads the file (broken entries are dropped).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final json = jsonDecode(raw) as Map<String, Object?>;
      _counter = (json['counter'] as num?)?.toInt() ?? 0;
      _projects = [
        for (final e in json['projects'] as List<Object?>? ?? const [])
          if (e is Map<String, Object?>) ?RecentProject.fromJson(e),
      ];
    } on Object {
      _projects = const [];
    }
    notifyListeners();
  }

  /// A new project ID.
  String newId() => 'project-${++_counter}';

  /// Saves [project] under [id] (moves it to the front). An empty timeline
  /// is not kept (and removes an older save of the same project). With
  /// [strict] a failed write throws (editor autosave shows "not saved");
  /// otherwise it is only logged.
  Future<void> save(
    String id,
    VideoKitEditProject project, {
    bool strict = false,
  }) async {
    final st = project.state.value;
    if (st.timeline.clips.isEmpty) {
      await remove(id);
      return;
    }
    final snap = await project.snapshot();
    final entry = RecentProject(
      id: id,
      savedAtEpochMs: now().millisecondsSinceEpoch,
      clipCount: st.timeline.clips.length,
      durationUs: st.estimate.durationUs,
      snapshot: snap,
    );
    _projects = [
      entry,
      for (final p in _projects)
        if (p.id != id) p,
    ].take(limit).toList();
    await _write(strict: strict);
  }

  /// Deletes [id].
  Future<void> remove(String id) async {
    if (!_projects.any((p) => p.id == id)) return;
    _projects = [
      for (final p in _projects)
        if (p.id != id) p,
    ];
    await _write();
  }

  /// Version of `projects.json` itself (the App's file, not the module's
  /// snapshot schema).
  static const int fileSchema = 1;

  Future<void> _write({bool strict = false}) async {
    notifyListeners();
    final json = jsonEncode({
      'schema': fileSchema,
      'counter': _counter,
      'projects': [for (final p in _projects) p.toJson()],
    });
    if (strict) {
      await storage.write(fileName, json);
    } else {
      await writeQuietly(storage, fileName, json);
    }
  }
}
