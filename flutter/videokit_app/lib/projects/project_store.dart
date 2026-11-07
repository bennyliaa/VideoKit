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

  /// Parses [json]; null when broken (never fatal).
  static RecentProject? fromJson(Map<String, Object?> json) {
    try {
      return RecentProject(
        id: json['id']! as String,
        savedAtEpochMs: (json['savedAtEpochMs']! as num).toInt(),
        clipCount: (json['clipCount']! as num).toInt(),
        durationUs: (json['durationUs'] as num?)?.toInt(),
        snapshot: SerializedEditProject(
          schemaVersion: (json['schemaVersion']! as num).toInt(),
          json: json['snapshot']! as String,
        ),
      );
    } on Object {
      return null;
    }
  }

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
  /// is not kept (and removes an older save of the same project).
  Future<void> save(String id, VideoKitEditProject project) async {
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
    await _write();
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

  Future<void> _write() async {
    notifyListeners();
    await writeQuietly(
      storage,
      fileName,
      jsonEncode({
        'schema': 1,
        'counter': _counter,
        'projects': [for (final p in _projects) p.toJson()],
      }),
    );
  }
}
