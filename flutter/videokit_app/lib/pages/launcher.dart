import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../picker/media_picker.dart';
import 'concat_page.dart';
import 'image_page.dart';
import 'multi_view_page.dart';
import 'player_page.dart';

/// Opening media from the home page, the picker or other apps: records
/// history (when enabled), checks access and routes to the module's
/// player / image viewer / multi-view / editor.
abstract final class MediaLauncher {
  /// Picks files and opens them.
  static Future<void> pickAndOpen(BuildContext origin) async {
    // The caller (e.g. the empty state) may unmount once history changes;
    // the navigator context stays.
    final context = Navigator.of(origin).context;
    final scope = AppScope.of(context);
    final picked = await scope.backend.picker.pick(context);
    if (!context.mounted || picked.isEmpty) return;
    await openPicked(context, picked);
  }

  /// Opens freshly picked or incoming media (one record per file).
  /// The history entry for [m] (recorded when the history is on, a
  /// transient one otherwise).
  static Future<HistoryEntry> entryFor(AppScope scope, PickedMedia m) async =>
      scope.settings.value.recordHistory
      ? await scope.history.recordOpened(m)
      : HistoryEntry(
          id: 'transient:${m.uri}',
          uri: m.uri,
          displayName: m.displayName,
          kind: m.kind,
          mimeType: m.mimeType,
          lastOpenedAtEpochMs: scope.history.now().millisecondsSinceEpoch,
          persistable: m.persistable,
        );

  static Future<void> openPicked(
    BuildContext origin,
    List<PickedMedia> media,
  ) async {
    final context = Navigator.of(origin).context;
    if (media.isEmpty) return;
    final scope = AppScope.of(context);
    final entries = <HistoryEntry>[
      for (final m in media) await entryFor(scope, m),
    ];
    if (!context.mounted) return;
    if (entries.length == 1) {
      await openEntry(context, entries.single, record: false);
      return;
    }
    await _chooseMulti(context, entries);
  }

  static Future<void> _chooseMulti(
    BuildContext context,
    List<HistoryEntry> entries,
  ) async {
    final t = AppText.of(context);
    final allVideo = entries.every((e) => e.kind == MediaKind.video);
    final choice = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: VkTheme.of(context).colors.surface,
      builder: (context) {
        final th = VkTheme.of(context);
        final d = th.dimensions;
        return SafeArea(
          child: Padding(
            padding: EdgeInsetsDirectional.all(d.spacing16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Semantics(
                  header: true,
                  child: Text(
                    t(t.l.openChoiceTitle(entries.length)),
                    style: th.typography.title.copyWith(
                      color: th.colors.textPrimary,
                    ),
                  ),
                ),
                SizedBox(height: d.spacing16),
                VkButton(
                  label: t(t.l.openMultiView),
                  icon: th.icons.resolve('grid'),
                  onPressed: () => Navigator.of(context).pop('multi'),
                ),
                if (allVideo) ...[
                  SizedBox(height: d.spacing8),
                  VkButton(
                    label: t(t.l.openConcat),
                    variant: VkButtonVariant.secondary,
                    icon: th.icons.resolve('clips'),
                    onPressed: () => Navigator.of(context).pop('concat'),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
    if (!context.mounted || choice == null) return;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => choice == 'concat'
            ? ConcatPage(entries: entries)
            : MultiViewPage(entries: entries),
      ),
    );
  }

  /// Opens one record; files that moved or lost permission are marked
  /// "无法打开" (never silently deleted).
  static Future<void> openEntry(
    BuildContext origin,
    HistoryEntry entry, {
    bool fromStart = false,
    bool record = true,
  }) async {
    final context = Navigator.of(origin).context;
    final scope = AppScope.of(context);
    final t = AppText.of(context);
    final access = await scope.backend.picker.checkAccess(entry.uri);
    if (!context.mounted) return;
    if (access != MediaAccess.ok) {
      await scope.history.markUnavailable(entry.id);
      if (!context.mounted) return;
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(content: Text(t(t.l.openFailed(entry.displayName)))),
        );
      return;
    }
    var e = entry;
    if (record && scope.settings.value.recordHistory) {
      e = await scope.history.recordOpened(
        PickedMedia(
          uri: entry.uri,
          displayName: entry.displayName,
          kind: entry.kind,
          mimeType: entry.mimeType,
          persistable: entry.persistable,
        ),
      );
    }
    if (fromStart) await scope.history.resetPosition(e.id);
    e = scope.history.byId(e.id) ?? e;
    if (!context.mounted) return;
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (_) => e.isImage
            ? ImagePage(entry: e)
            : PlayerPage(entry: e, fromStart: fromStart),
      ),
    );
  }

  /// Opens several records in the multi-view (from the "更多" menu).
  static Future<void> openMultiView(
    BuildContext context,
    List<HistoryEntry> entries,
  ) => Navigator.of(context).push(
    MaterialPageRoute<void>(builder: (_) => MultiViewPage(entries: entries)),
  );

  /// "重新选择": locate the file again, relink the record, open it.
  static Future<void> reselect(BuildContext origin, HistoryEntry e) async {
    final context = Navigator.of(origin).context;
    final scope = AppScope.of(context);
    final picked = await scope.backend.picker.reselect(
      context,
      PickedMedia(
        uri: e.uri,
        displayName: e.displayName,
        kind: e.kind,
        mimeType: e.mimeType,
      ),
    );
    if (picked == null || !context.mounted) return;
    final next = await scope.history.relink(e.id, picked);
    if (next == null || !context.mounted) return;
    unawaited(openEntry(context, next, record: false));
  }
}
