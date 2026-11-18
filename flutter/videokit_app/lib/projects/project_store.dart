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
    this.schemaMinor = 0,
    this.copyOf,
    this.avatarTokens = const [],
  });

  /// Snapshot schema minor (04A E2 (b); 0 when the entry predates it).
  final int schemaMinor;

  /// 04A E7 Q3 / R8: this entry is a copy saved because [copyOf] was written
  /// by a newer minor than this App reads; the original is kept untouched.
  final String? copyOf;

  /// 04A E7 Q4: App avatar tokens the project's masks use (never evicted
  /// from the avatar store while the project is kept).
  final List<String> avatarTokens;

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
    'schemaMinor': schemaMinor,
    'copyOf': ?copyOf,
    if (avatarTokens.isNotEmpty) 'avatarTokens': avatarTokens,
    'snapshot': snapshot.json,
  };

  /// R8: written by a newer minor than this App → never overwritten.
  bool get isNewerMinor =>
      snapshot.schemaVersion == SerializedEditProject.currentSchemaVersion &&
      schemaMinor > SerializedEditProject.currentSchemaMinor;

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
        schemaMinor:
            (json['schemaMinor'] as num?)?.toInt() ??
            embeddedSchemaMinor(snapshot),
        copyOf: json['copyOf'] as String?,
        avatarTokens: [
          for (final t in json['avatarTokens'] as List<Object?>? ?? const [])
            if (t is String) t,
        ],
      );
    } on Object {
      return null;
    }
  }

  static Object? _embedded(String snapshot, String key) {
    try {
      final j = jsonDecode(snapshot);
      return j is Map ? j[key] : null;
    } on Object {
      return null;
    }
  }

  static int? _embeddedSchemaVersion(String snapshot) =>
      (_embedded(snapshot, 'schemaVersion') as num?)?.toInt();

  /// `schemaMinor` inside a module snapshot (absent = 0, 04A E2 (b)).
  static int embeddedSchemaMinor(String snapshot) {
    final v = _embedded(snapshot, 'schemaMinor');
    return v is num ? v.toInt() : 0;
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
      other.snapshot == snapshot &&
      other.schemaMinor == schemaMinor &&
      other.copyOf == copyOf &&
      listEquals(other.avatarTokens, avatarTokens);

  @override
  int get hashCode => Object.hash(
    id,
    savedAtEpochMs,
    clipCount,
    durationUs,
    snapshot,
    schemaMinor,
    copyOf,
    Object.hashAll(avatarTokens),
  );
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

  /// R8: original ID → the copy this App saves to instead (04A E7 Q3).
  Map<String, String> _copies = const {};

  /// Projects, newest first.
  List<RecentProject> get projects => _projects;

  /// The ID saves of [id] actually go to (its copy when [id] was written by
  /// a newer minor, otherwise [id]).
  String resolveId(String id) => _copies[id] ?? id;

  /// App avatar tokens used by any kept project (04A E7 Q4: the avatar
  /// store never evicts these).
  Set<String> get referencedAvatars => {
    for (final p in _projects) ...p.avatarTokens,
  };

  /// App avatar tokens [project]'s masks use (Kit built-ins excluded).
  static List<String> avatarTokensOf(VideoKitEditProject project) => [
    for (final m in project.state.value.masks)
      if (m.avatar case final a? when !a.isBuiltin) a.avatarToken,
  ].toSet().toList();

  /// Loads the file (broken entries are dropped).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final json = jsonDecode(raw) as Map<String, Object?>;
      _counter = (json['counter'] as num?)?.toInt() ?? 0;
      _copies = {
        for (final e
            in (json['copies'] as Map<String, Object?>? ?? const {}).entries)
          if (e.value is String) e.key: e.value! as String,
      };
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
  ///
  /// R8 (04A E7 Q3): when the kept entry [id] was written by a newer schema
  /// minor than this App, it is never overwritten (nor removed): the save
  /// goes to a copy (`copyOf` = [id]) and later saves of [id] go there too.
  /// Returns the ID the project was saved under.
  Future<String> save(
    String id,
    VideoKitEditProject project, {
    bool strict = false,
  }) async {
    final st = project.state.value;
    var target = resolveId(id);
    final kept = _projects.where((p) => p.id == target).firstOrNull;
    if (kept != null && kept.isNewerMinor) {
      if (st.timeline.clips.isEmpty) return target;
      target = newId();
      _copies = {..._copies, id: target};
    }
    if (st.timeline.clips.isEmpty) {
      await remove(target);
      return target;
    }
    final snap = await project.snapshot();
    final entry = RecentProject(
      id: target,
      savedAtEpochMs: now().millisecondsSinceEpoch,
      clipCount: st.timeline.clips.length,
      durationUs: st.estimate.durationUs,
      snapshot: snap,
      schemaMinor: RecentProject.embeddedSchemaMinor(snap.json),
      copyOf: target == id
          ? _projects.where((p) => p.id == id).firstOrNull?.copyOf
          : id,
      avatarTokens: avatarTokensOf(project),
    );
    final id0 = target;
    _projects = [
      entry,
      for (final p in _projects)
        if (p.id != id0) p,
    ].take(limit).toList();
    await _write(strict: strict);
    return id0;
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
      if (_copies.isNotEmpty) 'copies': _copies,
      'projects': [for (final p in _projects) p.toJson()],
    });
    if (strict) {
      await storage.write(fileName, json);
    } else {
      await writeQuietly(storage, fileName, json);
    }
  }
}
