import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../picker/media_picker.dart';
import 'library_import.dart';
import 'library_platform.dart';
import 'library_store.dart';

/// What to do when an imported directory has the name of an existing
/// library folder (FT01A-21).
enum FolderClashChoice {
  /// Add to the existing folder.
  merge,

  /// Make a new folder ("旅行 (2)").
  separate,
}

/// "导入整个文件夹" before it runs: which files go to which library
/// folder, and what was skipped.
@immutable
final class FolderImportPlan {
  /// Creates a plan.
  const FolderImportPlan({
    required this.media,
    required this.folderNames,
    required this.skipped,
  });

  /// Media to import, in listing order.
  final List<PickedMedia> media;

  /// Library folder name of each item (parallel to [media]).
  final List<String> folderNames;

  /// Non-media files (relative path), reported and not imported.
  final List<String> skipped;

  /// Distinct folder names, in first-use order.
  List<String> get folders => folderNames.toSet().toList();
}

/// Library folder name of directory [dir] of a tree named [root]: the root
/// itself is [root]; a sub-directory keeps its path ("海边 / 2025") so the
/// one-level library still shows where it came from.
String folderNameFor(String root, String dir) =>
    dir.isEmpty ? root : dir.split('/').where((p) => p.isNotEmpty).join(' / ');

/// Media kind of a listed file, or null when it is not a video or image.
MediaKind? kindOf(TreeEntry e) {
  final mime = e.mimeType?.toLowerCase() ?? '';
  if (mime.startsWith('video/')) return MediaKind.video;
  if (mime == 'image/gif') return MediaKind.imageAnimated;
  if (mime.startsWith('image/')) return MediaKind.imageStatic;
  return null;
}

/// Plans the import of [listing]. Empty directories make no folder.
FolderImportPlan planFolderImport(TreeListing listing) {
  final media = <PickedMedia>[];
  final names = <String>[];
  final skipped = <String>[];
  for (final e in listing.entries) {
    final kind = kindOf(e);
    if (kind == null) {
      skipped.add(e.dir.isEmpty ? e.name : '${e.dir}/${e.name}');
      continue;
    }
    media.add(
      PickedMedia(
        uri: e.uri,
        displayName: e.name,
        kind: kind,
        mimeType: e.mimeType,
        sizeBytes: e.sizeBytes,
        persistable: false,
      ),
    );
    names.add(folderNameFor(listing.name, e.dir));
  }
  return FolderImportPlan(media: media, folderNames: names, skipped: skipped);
}

/// Creates (or, on a clash, merges into) the library folders of [plan] and
/// returns the import job. [onClash] is asked once per clashing name; null
/// from it cancels the whole import (returns null, nothing created).
Future<LibraryImport?> prepareFolderImport(
  LibraryStore store,
  FolderImportPlan plan, {
  required Future<FolderClashChoice?> Function(String name) onClash,
}) async {
  final choices = <String, FolderClashChoice>{};
  for (final name in plan.folders) {
    if (store.folderByName(name) != null) {
      final c = await onClash(name);
      if (c == null) return null;
      choices[name] = c;
    }
  }
  final ids = <String, String>{};
  for (final name in plan.folders) {
    final existing = store.folderByName(name);
    if (existing != null && choices[name] == FolderClashChoice.merge) {
      ids[name] = existing.id;
    } else {
      ids[name] = (await store.createFolder(store.uniqueFolderName(name))).id;
    }
  }
  return LibraryImport(
    store: store,
    media: plan.media,
    folderId: null,
    folderIds: [for (final n in plan.folderNames) ids[n]],
    skipped: plan.skipped,
  );
}
