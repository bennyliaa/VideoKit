import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../history/app_storage.dart';
import 'library_models.dart';
import 'library_platform.dart';

/// Why a folder name was rejected (REQ-APP-13, FT01A-10).
enum FolderNameError {
  /// Empty or only spaces.
  empty,

  /// Another folder (or "全部媒体" / "未分类") has this name.
  duplicate,

  /// Longer than [LibraryStore.maxFolderName].
  tooLong,
}

/// A rejected folder name.
final class FolderNameException implements Exception {
  /// Creates the exception.
  const FolderNameException(this.error);

  /// Why.
  final FolderNameError error;

  @override
  String toString() => 'FolderNameException(${error.name})';
}

/// The media library index (REQ-APP-09/12/13): folders and items in the
/// App-private file `library.json`; the media files themselves are copies
/// in the private media directory ([LibraryPlatform]). Never records into
/// "最近播放".
class LibraryStore extends ChangeNotifier {
  /// Creates the store.
  LibraryStore({
    required this.storage,
    required this.platform,
    DateTime Function()? now,
    this.reservedNames = const {},
  }) : now = now ?? DateTime.now;

  /// Index storage.
  final AppStorage storage;

  /// Files and thumbnails.
  final LibraryPlatform platform;

  /// Clock.
  final DateTime Function() now;

  /// Names of the built-in rows ("全部媒体", "未分类"), which a folder may
  /// not take (compared trimmed, case-insensitive).
  Set<String> reservedNames;

  /// Index file.
  static const String fileName = 'library.json';

  /// Version of the index file.
  static const int fileSchema = 1;

  /// Longest folder name.
  static const int maxFolderName = 40;

  List<LibraryFolder> _folders = const [];
  List<LibraryItem> _items = const [];
  int _counter = 0;

  /// Folders in creation order.
  List<LibraryFolder> get folders => _folders;

  /// Items, newest import first.
  List<LibraryItem> get items => _items;

  /// Folder [id], or null.
  LibraryFolder? folderById(String id) =>
      _folders.where((f) => f.id == id).firstOrNull;

  /// Item [id], or null.
  LibraryItem? itemById(String id) =>
      _items.where((i) => i.id == id).firstOrNull;

  /// Loads the index (broken entries are dropped; items of a vanished
  /// folder go to "未分类").
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final j = jsonDecode(raw) as Map<String, Object?>;
      _counter = (j['counter'] as num?)?.toInt() ?? 0;
      _folders = [
        for (final e in j['folders'] as List<Object?>? ?? const [])
          if (e is Map<String, Object?>) ?LibraryFolder.fromJson(e),
      ];
      final ids = {for (final f in _folders) f.id};
      _items = [
        for (final e in j['items'] as List<Object?>? ?? const [])
          if (e is Map<String, Object?>)
            if (LibraryItem.fromJson(e) case final i?)
              i.folderId == null || ids.contains(i.folderId)
                  ? i
                  : i.inFolder(null),
      ];
    } on Object {
      _folders = const [];
      _items = const [];
    }
    notifyListeners();
  }

  /// A new ID ("item-12", "folder-3").
  String newId(String prefix) => '$prefix-${++_counter}';

  // ------------------------------------------------------------ queries --

  /// Items of [scope] that pass [filter], newest first.
  List<LibraryItem> itemsIn(
    LibraryScope scope, [
    LibraryFilter filter = LibraryFilter.all,
  ]) => [
    for (final i in _items)
      if (_inScope(i, scope) && filter.accepts(i)) i,
  ];

  bool _inScope(LibraryItem i, LibraryScope scope) => switch (scope) {
    AllMedia() => true,
    Unsorted() => i.folderId == null,
    InFolder(:final folderId) => i.folderId == folderId,
  };

  /// Number of items in [scope] (all types).
  int countIn(LibraryScope scope) =>
      _items.where((i) => _inScope(i, scope)).length;

  /// Page [page] of [scope] / [filter] at [pageSize] (REQ-APP-12).
  LibraryPageResult query(
    LibraryScope scope,
    LibraryFilter filter, {
    required int page,
    required int pageSize,
  }) => LibraryPageResult.of(itemsIn(scope, filter), page, pageSize);

  // ------------------------------------------------------------ folders --

  /// Checks [name] for a new folder, or for renaming folder [exceptId].
  FolderNameError? checkFolderName(String name, {String? exceptId}) {
    final n = name.trim();
    if (n.isEmpty) return FolderNameError.empty;
    if (n.length > maxFolderName) return FolderNameError.tooLong;
    final key = n.toLowerCase();
    if (reservedNames.any((r) => r.trim().toLowerCase() == key)) {
      return FolderNameError.duplicate;
    }
    final clash = _folders.any(
      (f) => f.id != exceptId && f.name.trim().toLowerCase() == key,
    );
    return clash ? FolderNameError.duplicate : null;
  }

  /// The folder named [name] (trimmed, case-insensitive), or null.
  LibraryFolder? folderByName(String name) {
    final key = name.trim().toLowerCase();
    return _folders
        .where((f) => f.name.trim().toLowerCase() == key)
        .firstOrNull;
  }

  /// [name] shortened to [maxFolderName] and made unique ("旅行 (2)").
  String uniqueFolderName(String name) {
    String fit(String s) => s.length <= maxFolderName
        ? s
        : s.substring(s.length - maxFolderName).trim();
    var candidate = fit(name.trim());
    if (candidate.isEmpty) candidate = '1';
    final base = candidate;
    for (var n = 2; checkFolderName(candidate) != null; n++) {
      final suffix = ' ($n)';
      candidate =
          '${base.length + suffix.length > maxFolderName ? base.substring(0, maxFolderName - suffix.length) : base}$suffix';
    }
    return candidate;
  }

  /// Creates a folder; throws [FolderNameException].
  Future<LibraryFolder> createFolder(String name) async {
    final error = checkFolderName(name);
    if (error != null) throw FolderNameException(error);
    final f = LibraryFolder(
      id: newId('folder'),
      name: name.trim(),
      createdAtEpochMs: now().millisecondsSinceEpoch,
    );
    _folders = [..._folders, f];
    await _write();
    return f;
  }

  /// Renames folder [id]; throws [FolderNameException]. Renaming to the
  /// same name is accepted (no change).
  Future<void> renameFolder(String id, String name) async {
    final error = checkFolderName(name, exceptId: id);
    if (error != null) throw FolderNameException(error);
    _folders = [
      for (final f in _folders) f.id == id ? f.renamed(name.trim()) : f,
    ];
    await _write();
  }

  /// Deletes folder [id]: its media are deleted too ([deleteMedia]) or
  /// moved to "未分类".
  Future<void> deleteFolder(String id, {required bool deleteMedia}) async {
    final inside = [
      for (final i in _items)
        if (i.folderId == id) i.id,
    ];
    _folders = [
      for (final f in _folders)
        if (f.id != id) f,
    ];
    if (deleteMedia) {
      await deleteItems(inside);
      return;
    }
    _items = [
      for (final i in _items) i.folderId == id ? i.inFolder(null) : i,
    ];
    await _write();
  }

  // -------------------------------------------------------------- items --

  /// Adds an imported item (newest first).
  Future<void> addItem(LibraryItem item) async {
    _items = [item, for (final i in _items) if (i.id != item.id) i];
    await _write();
  }

  /// Moves [ids] to [folderId] (null = "未分类").
  Future<void> moveItems(Iterable<String> ids, String? folderId) async {
    final set = ids.toSet();
    _items = [
      for (final i in _items) set.contains(i.id) ? i.inFolder(folderId) : i,
    ];
    await _write();
  }

  /// Deletes [ids] from the library: the private copies and thumbnails go
  /// too.
  Future<void> deleteItems(Iterable<String> ids) async {
    final set = ids.toSet();
    final gone = [
      for (final i in _items)
        if (set.contains(i.id)) i,
    ];
    _items = [
      for (final i in _items)
        if (!set.contains(i.id)) i,
    ];
    await _write();
    for (final i in gone) {
      await platform.delete(i.path);
      final thumb = i.thumbnailPath;
      if (thumb != null) await platform.delete(thumb);
    }
  }

  Future<void> _write() async {
    notifyListeners();
    await writeQuietly(
      storage,
      fileName,
      jsonEncode({
        'schema': fileSchema,
        'counter': _counter,
        'folders': [for (final f in _folders) f.toJson()],
        'items': [for (final i in _items) i.toJson()],
      }),
    );
  }
}
