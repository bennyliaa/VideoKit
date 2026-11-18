import 'dart:io';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../pages/image_page.dart';
import '../pages/player_page.dart';
import 'library_models.dart';

/// Prefix of the transient record IDs of library items: they are never
/// stored in "最近播放" (REQ-APP-10), the player and viewer only record
/// entries the history knows.
const String libraryEntryPrefix = 'library:';

/// The record the module pages open for [item] (never added to the
/// history).
HistoryEntry libraryEntry(LibraryItem item) => HistoryEntry(
  id: '$libraryEntryPrefix${item.id}',
  uri: item.path.startsWith('/') ? Uri.file(item.path).toString() : item.path,
  displayName: item.displayName,
  kind: item.kind,
  lastOpenedAtEpochMs: item.importedAtEpochMs,
  mimeType: item.mimeType,
  durationUs: item.durationUs,
  width: item.width,
  height: item.height,
  persistable: false,
);

/// Opens [item] in the module's player or image viewer (REQ-APP-09);
/// images page through [pageItems] (the images of the current page).
Future<void> openLibraryItem(
  BuildContext context,
  LibraryItem item, {
  List<LibraryItem> pageItems = const [],
}) {
  final e = libraryEntry(item);
  return Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (_) => item.isImage
          ? ImagePage(
              entry: e,
              pageList: [
                for (final i in pageItems)
                  if (i.isImage) libraryEntry(i),
              ],
            )
          : PlayerPage(entry: e),
    ),
  );
}

/// Thumbnail of a library item: the cached file, otherwise the backend's
/// placeholder (demo picture / plain icon); "图片" badge or duration chip.
class LibraryThumbnail extends StatelessWidget {
  /// Creates the thumbnail.
  const LibraryThumbnail({super.key, required this.item});

  /// Item.
  final LibraryItem item;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final scope = AppScope.of(context);
    final entry = libraryEntry(item);
    final thumb = item.thumbnailPath;
    final fallback = scope.backend.thumbnail(context, entry);
    final duration = item.durationUs;
    return ExcludeSemantics(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(d.cornerMedium),
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (thumb != null && thumb.startsWith('/'))
              Image(
                image: FileImage(File(thumb)),
                fit: BoxFit.cover,
                excludeFromSemantics: true,
                errorBuilder: (context, _, _) => fallback,
              )
            else
              fallback,
            if (item.isImage)
              PositionedDirectional(
                top: d.spacing8,
                start: d.spacing8,
                child: _Chip(text: a(a.l.imageBadge)),
              ),
            if (!item.isImage && duration != null)
              PositionedDirectional(
                bottom: d.spacing8,
                end: d.spacing8,
                child: _Chip(text: VkFormat.timecode(duration)),
              ),
          ],
        ),
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing4 / 2,
      ),
      decoration: BoxDecoration(
        color: t.drawables.glassPlayer.color,
        borderRadius: BorderRadius.circular(d.cornerFull),
      ),
      child: Text(
        text,
        style: t.typography.label.copyWith(
          color: t.colors.playerControlsContent,
        ),
      ),
    );
  }
}
