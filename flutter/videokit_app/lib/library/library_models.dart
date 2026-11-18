import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// One folder of the media library (REQ-APP-13: one level, no nesting).
@immutable
final class LibraryFolder {
  /// Creates a folder.
  const LibraryFolder({
    required this.id,
    required this.name,
    required this.createdAtEpochMs,
  });

  /// Stable ID.
  final String id;

  /// User-visible name (unique, never empty).
  final String name;

  /// Creation time (folders are listed in this order).
  final int createdAtEpochMs;

  /// JSON form.
  Map<String, Object?> toJson() => {
    'id': id,
    'name': name,
    'createdAtEpochMs': createdAtEpochMs,
  };

  /// Parses [j]; null when broken.
  static LibraryFolder? fromJson(Map<String, Object?> j) {
    try {
      return LibraryFolder(
        id: j['id']! as String,
        name: j['name']! as String,
        createdAtEpochMs: (j['createdAtEpochMs'] as num?)?.toInt() ?? 0,
      );
    } on Object {
      return null;
    }
  }

  /// Copy with a new name.
  LibraryFolder renamed(String name) =>
      LibraryFolder(id: id, name: name, createdAtEpochMs: createdAtEpochMs);

  @override
  bool operator ==(Object other) =>
      other is LibraryFolder &&
      other.id == id &&
      other.name == name &&
      other.createdAtEpochMs == createdAtEpochMs;

  @override
  int get hashCode => Object.hash(id, name, createdAtEpochMs);
}

/// One media item in the library (REQ-APP-09): a copy in the App-private
/// directory, invisible to the gallery and other apps.
@immutable
final class LibraryItem {
  /// Creates an item.
  const LibraryItem({
    required this.id,
    required this.path,
    required this.displayName,
    required this.kind,
    required this.importedAtEpochMs,
    this.folderId,
    this.mimeType,
    this.sizeBytes,
    this.durationUs,
    this.width,
    this.height,
    this.thumbnailPath,
  });

  /// Stable ID.
  final String id;

  /// Private file (absolute path; `memory:` in the demo).
  final String path;

  /// Name shown in the list (the original file name).
  final String displayName;

  /// Video or image.
  final MediaKind kind;

  /// Import time.
  final int importedAtEpochMs;

  /// Folder; null = "未分类".
  final String? folderId;

  /// MIME type.
  final String? mimeType;

  /// Size of the private copy.
  final int? sizeBytes;

  /// Video duration (µs).
  final int? durationUs;

  /// Pixel width.
  final int? width;

  /// Pixel height.
  final int? height;

  /// Cached thumbnail (App-private).
  final String? thumbnailPath;

  /// Whether this is an image.
  bool get isImage => kind.isImage;

  /// Returns a copy in [folderId] (null = "未分类").
  LibraryItem inFolder(String? folderId) => LibraryItem(
    id: id,
    path: path,
    displayName: displayName,
    kind: kind,
    importedAtEpochMs: importedAtEpochMs,
    folderId: folderId,
    mimeType: mimeType,
    sizeBytes: sizeBytes,
    durationUs: durationUs,
    width: width,
    height: height,
    thumbnailPath: thumbnailPath,
  );

  /// JSON form.
  Map<String, Object?> toJson() => {
    'id': id,
    'path': path,
    'displayName': displayName,
    'kind': kind.wireName,
    'importedAtEpochMs': importedAtEpochMs,
    'folderId': ?folderId,
    'mimeType': ?mimeType,
    'sizeBytes': ?sizeBytes,
    'durationUs': ?durationUs,
    'width': ?width,
    'height': ?height,
    'thumbnailPath': ?thumbnailPath,
  };

  /// Parses [j]; null when broken.
  static LibraryItem? fromJson(Map<String, Object?> j) {
    try {
      int? n(String k) => (j[k] as num?)?.toInt();
      return LibraryItem(
        id: j['id']! as String,
        path: j['path']! as String,
        displayName: j['displayName']! as String,
        kind: MediaKind.fromName(j['kind']! as String),
        importedAtEpochMs: n('importedAtEpochMs') ?? 0,
        folderId: j['folderId'] as String?,
        mimeType: j['mimeType'] as String?,
        sizeBytes: n('sizeBytes'),
        durationUs: n('durationUs'),
        width: n('width'),
        height: n('height'),
        thumbnailPath: j['thumbnailPath'] as String?,
      );
    } on Object {
      return null;
    }
  }

  @override
  bool operator ==(Object other) =>
      other is LibraryItem &&
      other.id == id &&
      other.path == path &&
      other.displayName == displayName &&
      other.kind == kind &&
      other.importedAtEpochMs == importedAtEpochMs &&
      other.folderId == folderId &&
      other.mimeType == mimeType &&
      other.sizeBytes == sizeBytes &&
      other.durationUs == durationUs &&
      other.width == width &&
      other.height == height &&
      other.thumbnailPath == thumbnailPath;

  @override
  int get hashCode => Object.hash(
    id,
    path,
    displayName,
    kind,
    importedAtEpochMs,
    folderId,
    mimeType,
    sizeBytes,
    durationUs,
    width,
    height,
    thumbnailPath,
  );
}

/// Type filter of the list (REQ-APP-12).
enum LibraryFilter {
  /// Everything.
  all,

  /// Videos.
  video,

  /// Images (static and animated).
  image;

  /// Whether [item] passes.
  bool accepts(LibraryItem item) => switch (this) {
    LibraryFilter.all => true,
    LibraryFilter.video => !item.isImage,
    LibraryFilter.image => item.isImage,
  };
}

/// Which folder the list shows.
@immutable
sealed class LibraryScope {
  const LibraryScope();
}

/// "全部媒体".
final class AllMedia extends LibraryScope {
  /// The scope.
  const AllMedia();

  @override
  bool operator ==(Object other) => other is AllMedia;

  @override
  int get hashCode => (AllMedia).hashCode;
}

/// "未分类" (items without a folder).
final class Unsorted extends LibraryScope {
  /// The scope.
  const Unsorted();

  @override
  bool operator ==(Object other) => other is Unsorted;

  @override
  int get hashCode => (Unsorted).hashCode;
}

/// One user folder.
final class InFolder extends LibraryScope {
  /// The scope of folder [folderId].
  const InFolder(this.folderId);

  /// Folder ID.
  final String folderId;

  @override
  bool operator ==(Object other) =>
      other is InFolder && other.folderId == folderId;

  @override
  int get hashCode => Object.hash(InFolder, folderId);
}

/// One page of the list: "第 21–40 项，共 42 项" (REQ-APP-12).
@immutable
final class LibraryPageResult {
  /// Creates a page.
  const LibraryPageResult({
    required this.items,
    required this.page,
    required this.pageCount,
    required this.total,
    required this.first,
    required this.last,
  });

  /// Items on this page.
  final List<LibraryItem> items;

  /// 1-based page number (1 when empty).
  final int page;

  /// Number of pages (at least 1).
  final int pageCount;

  /// Items in scope and filter.
  final int total;

  /// 1-based index of the first item (0 when empty).
  final int first;

  /// 1-based index of the last item (0 when empty).
  final int last;

  /// Computes page [page] of [all] at [pageSize]; an out-of-range page is
  /// clamped (e.g. after deleting the last item of the last page).
  static LibraryPageResult of(List<LibraryItem> all, int page, int pageSize) {
    final size = pageSize.clamp(1, 1 << 20);
    final count = all.isEmpty ? 1 : (all.length + size - 1) ~/ size;
    final p = page.clamp(1, count);
    final start = (p - 1) * size;
    final end = (start + size).clamp(0, all.length);
    return LibraryPageResult(
      items: List.unmodifiable(all.sublist(start.clamp(0, all.length), end)),
      page: p,
      pageCount: count,
      total: all.length,
      first: all.isEmpty ? 0 : start + 1,
      last: end,
    );
  }
}

/// Library export target (REQ-APP-09): edited exports are saved back into
/// [folderId] (null = the unsorted row).
@immutable
final class LibraryExportTarget {
  /// Creates the target.
  const LibraryExportTarget({required this.folderId, required this.folderName});

  /// Folder.
  final String? folderId;

  /// Folder name (notice text).
  final String folderName;
}
