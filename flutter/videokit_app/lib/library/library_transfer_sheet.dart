import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'library_folder_import.dart';
import 'library_import.dart';
import 'library_import_sheet.dart';
import 'library_models.dart';
import 'library_platform.dart';
import 'library_transfer.dart';

/// Text of a transfer failure.
String transferFailureText(AppText a, TransferFailure f) => a(switch (f) {
  TransferFailure.noSpace => a.l.libraryXferNoSpace,
  TransferFailure.unreadable => a.l.libraryXferUnreadable,
  TransferFailure.unwritable => a.l.libraryXferUnwritable,
  TransferFailure.mismatch => a.l.libraryXferMismatch,
  TransferFailure.cancelled || TransferFailure.other => a.l.libraryXferOther,
});

/// The library folder name an item goes under when moved out.
String folderNameOf(BuildContext context, LibraryItem item) {
  final a = AppText.of(context);
  final id = item.folderId;
  final f = id == null ? null : AppScope.of(context).library.folderById(id);
  return f?.name ?? a(a.l.libraryUnsorted);
}

/// A prominent warning before media stop being private (REQ-APP-14);
/// true when the user goes on.
Future<bool> confirmNotPrivate(
  BuildContext context, {
  required String title,
  required String body,
  required String action,
}) async =>
    await showDialog<bool>(
      context: context,
      builder: (context) {
        final t = VkTheme.of(context);
        final s = VkStrings.of(context);
        final d = t.dimensions;
        return AlertDialog(
          backgroundColor: t.colors.surfaceHigh,
          icon: Icon(
            t.icons.resolve('warning'),
            color: t.colors.warning,
            size: d.icon24 * 1.5,
          ),
          title: Text(
            title,
            textAlign: TextAlign.center,
            style: t.typography.title.copyWith(color: t.colors.warning),
          ),
          content: Text(
            body,
            style: t.typography.body.copyWith(color: t.colors.textPrimary),
          ),
          actions: [
            VkButton(
              label: s.text('commonCancel'),
              variant: VkButtonVariant.text,
              onPressed: () => Navigator.of(context).pop(false),
            ),
            VkButton(
              label: action,
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    ) ??
    false;

/// "导出到相册" for [items] (FT01A-17): warning, then progress.
Future<TransferProgress?> exportToGallery(
  BuildContext context,
  List<LibraryItem> items,
) async {
  if (items.isEmpty) return null;
  final a = AppText.of(context);
  final go = await confirmNotPrivate(
    context,
    title: a(a.l.libraryExportConfirmTitle),
    body: a(a.l.libraryExportConfirmBody(items.length)),
    action: a(a.l.libraryExportAction),
  );
  if (!go || !context.mounted) return null;
  final job = LibraryTransfer(
    store: AppScope.of(context).library,
    items: items,
    target: TransferTarget.gallery,
    folderNameOf: (i) => folderNameOf(context, i),
  );
  return _runTransfer(context, job);
}

/// "移动到文件夹" for [items] (FT01A-20): warning, directory picker,
/// verified copies, removal from the library item by item.
Future<TransferProgress?> moveOut(
  BuildContext context,
  List<LibraryItem> items,
) async {
  if (items.isEmpty) return null;
  final a = AppText.of(context);
  final go = await confirmNotPrivate(
    context,
    title: a(a.l.libraryMoveOutConfirmTitle),
    body: a(a.l.libraryMoveOutConfirmBody(items.length)),
    action: a(a.l.libraryMoveOutAction),
  );
  if (!go || !context.mounted) return null;
  final scope = AppScope.of(context);
  final tree = await scope.backend.library.pickDirectory();
  if (tree == null || !context.mounted) return null;
  // Names are resolved now: the items leave the library during the run.
  final names = {for (final i in items) i.id: folderNameOf(context, i)};
  final job = LibraryTransfer(
    store: scope.library,
    items: items,
    target: TransferTarget.directory,
    treeUri: tree,
    folderNameOf: (i) => names[i.id]!,
  );
  return _runTransfer(context, job);
}

Future<TransferProgress> _runTransfer(
  BuildContext context,
  LibraryTransfer job,
) async {
  final done = job.run();
  await showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    isDismissible: false,
    enableDrag: false,
    backgroundColor: VkTheme.of(context).colors.surface,
    builder: (_) => LibraryTransferSheet(job: job),
  );
  final r = await done;
  job.dispose();
  return r;
}

/// "导入整个文件夹" (FT01A-21): directory picker, plan (non-media skipped),
/// clash questions, then the import sheet.
Future<ImportProgress?> importFolder(BuildContext context) async {
  final a = AppText.of(context);
  final scope = AppScope.of(context);
  final platform = scope.backend.library;
  final tree = await platform.pickDirectory();
  if (tree == null || !context.mounted) return null;
  final listing = await platform.listTree(tree);
  if (!context.mounted) return null;
  void say(String text) => ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(content: Text(text)));
  if (listing == null) {
    say(a(a.l.libraryFolderUnreadable));
    return null;
  }
  final plan = planFolderImport(listing);
  if (plan.media.isEmpty) {
    say(a(a.l.libraryFolderNoMedia));
    return null;
  }
  final job = await prepareFolderImport(
    scope.library,
    plan,
    onClash: (name) => _askClash(context, name),
  );
  if (job == null || !context.mounted) return null;
  final done = job.run();
  await showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    isDismissible: false,
    enableDrag: false,
    backgroundColor: VkTheme.of(context).colors.surface,
    builder: (_) => LibraryImportSheet(job: job, folderName: listing.name),
  );
  final r = await done;
  job.dispose();
  return r;
}

Future<FolderClashChoice?> _askClash(BuildContext context, String name) {
  if (!context.mounted) return Future.value();
  return showDialog<FolderClashChoice>(
    context: context,
    builder: (context) {
      final t = VkTheme.of(context);
      final a = AppText.of(context);
      final s = VkStrings.of(context);
      return AlertDialog(
        backgroundColor: t.colors.surfaceHigh,
        title: Text(
          a(a.l.libraryClashTitle(name)),
          style: t.typography.title.copyWith(color: t.colors.textPrimary),
        ),
        content: Text(
          a(a.l.libraryClashBody),
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
        actions: [
          VkButton(
            label: s.text('commonCancel'),
            variant: VkButtonVariant.text,
            onPressed: () => Navigator.of(context).pop(),
          ),
          VkButton(
            label: a(a.l.libraryClashSeparate),
            variant: VkButtonVariant.secondary,
            onPressed: () =>
                Navigator.of(context).pop(FolderClashChoice.separate),
          ),
          VkButton(
            label: a(a.l.libraryClashMerge),
            onPressed: () => Navigator.of(context).pop(FolderClashChoice.merge),
          ),
        ],
      );
    },
  );
}

/// Progress of an export or move-out: count, bar, per-item failures,
/// note, cancel / done.
class LibraryTransferSheet extends StatelessWidget {
  /// Creates the sheet.
  const LibraryTransferSheet({super.key, required this.job});

  /// Running transfer.
  final LibraryTransfer job;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final gallery = job.target == TransferTarget.gallery;
    Widget card(Widget child) => Container(
      padding: EdgeInsetsDirectional.all(d.spacing16),
      decoration: BoxDecoration(
        color: t.colors.surfaceHigh,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: child,
    );
    return SafeArea(
      child: ValueListenableBuilder<TransferProgress>(
        valueListenable: job,
        builder: (context, p, _) {
          final failed = p.failed;
          final status = !p.finished
              ? (gallery
                    ? a(a.l.libraryExporting(p.current, p.total))
                    : a(a.l.libraryMovingOut(p.current, p.total)))
              : p.cancelled
              ? (gallery
                    ? a(a.l.libraryExportCancelled(p.succeeded))
                    : a(a.l.libraryMoveOutCancelled(p.succeeded)))
              : (gallery
                    ? a(a.l.libraryExportDone(p.succeeded, failed.length))
                    : a(a.l.libraryMoveOutDone(p.succeeded, failed.length)));
          return SingleChildScrollView(
            padding: EdgeInsetsDirectional.all(d.spacing24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Semantics(
                  header: true,
                  child: Text(
                    gallery
                        ? a(a.l.libraryExportToGallery)
                        : a(a.l.libraryMoveOut),
                    style: t.typography.titleLarge.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
                SizedBox(height: d.spacing16),
                card(
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Semantics(
                              liveRegion: true,
                              child: Text(
                                status,
                                style: t.typography.title.copyWith(
                                  color: t.colors.textPrimary,
                                ),
                              ),
                            ),
                          ),
                          Text(
                            VkFormat.percent(s, p.fraction),
                            style: t.typography.body.copyWith(
                              color: t.colors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: d.spacing12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(d.cornerFull),
                        child: LinearProgressIndicator(
                          value: p.fraction,
                          minHeight: d.spacing8,
                          color: t.colors.primary,
                          backgroundColor: t.colors.surfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                if (failed.isNotEmpty) ...[
                  SizedBox(height: d.spacing12),
                  card(
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        for (final f in failed)
                          Padding(
                            padding: EdgeInsetsDirectional.symmetric(
                              vertical: d.spacing4,
                            ),
                            child: Text(
                              a(
                                a.l.libraryImportFailedItem(
                                  f.item.displayName,
                                  transferFailureText(a, f.failure!),
                                ),
                              ),
                              style: t.typography.bodySmall.copyWith(
                                color: t.colors.error,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
                SizedBox(height: d.spacing12),
                card(
                  Row(
                    children: [
                      Icon(
                        t.icons.resolve('warning'),
                        size: d.icon20,
                        color: t.colors.warning,
                      ),
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: Text(
                          gallery
                              ? a(a.l.libraryExportNote)
                              : a(a.l.libraryMoveOutNote),
                          style: t.typography.bodySmall.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: d.spacing24),
                if (p.finished)
                  VkButton(
                    label: a(a.l.libraryDone),
                    onPressed: () => Navigator.of(context).pop(),
                  )
                else
                  VkButton(
                    label: s.text('commonCancel'),
                    variant: VkButtonVariant.outline,
                    onPressed: job.cancel,
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
