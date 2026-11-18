import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'library_import.dart';
import 'library_platform.dart';

/// Picks media and imports them into [folderId] named [folderName]
/// (REQ-APP-11). Returns the finished progress, or null when nothing was
/// picked.
Future<ImportProgress?> pickAndImport(
  BuildContext context, {
  required String? folderId,
  required String folderName,
}) async {
  final scope = AppScope.of(context);
  final picked = await scope.backend.picker.pick(
    context,
    kinds: const {MediaKind.video, MediaKind.imageStatic},
  );
  if (picked.isEmpty || !context.mounted) return null;
  final job = LibraryImport(
    store: scope.library,
    media: picked,
    folderId: folderId,
  );
  final done = job.run();
  await showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    isDismissible: false,
    enableDrag: false,
    backgroundColor: VkTheme.of(context).colors.surface,
    builder: (_) => LibraryImportSheet(job: job, folderName: folderName),
  );
  final r = await done;
  job.dispose();
  return r;
}

/// The import sheet (design page 27): "导入到“旅行”", counts and size,
/// "正在导入 7 / 12" with a bar, "导入后删除手机里的原文件", the privacy
/// note, "取消导入"; when finished, the per-item failures and "完成".
class LibraryImportSheet extends StatelessWidget {
  /// Creates the sheet.
  const LibraryImportSheet({
    super.key,
    required this.job,
    required this.folderName,
  });

  /// The running import.
  final LibraryImport job;

  /// Target folder name.
  final String folderName;

  /// Reason text.
  static String reasonText(AppText a, ImportFailure f) => a(switch (f) {
    ImportFailure.noSpace => a.l.libraryFailNoSpace,
    ImportFailure.unreadable => a.l.libraryFailUnreadable,
    ImportFailure.corrupt => a.l.libraryFailCorrupt,
    ImportFailure.other => a.l.libraryFailOther,
  });

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget card(Widget child) => Container(
      padding: EdgeInsetsDirectional.all(d.spacing16),
      decoration: BoxDecoration(
        color: t.colors.surfaceHigh,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: child,
    );
    return SafeArea(
      child: ValueListenableBuilder<ImportProgress>(
        valueListenable: job,
        builder: (context, p, _) {
          final count = job.media.length;
          final summary = p.bytesTotal > 0
              ? a(
                  a.l.libraryImportSummary(
                    count,
                    job.videoCount,
                    job.imageCount,
                    VkFormat.fileSize(s, p.bytesTotal),
                  ),
                )
              : a(
                  a.l.libraryImportSummaryNoSize(
                    count,
                    job.videoCount,
                    job.imageCount,
                  ),
                );
          final failed = p.failed;
          return SingleChildScrollView(
            padding: EdgeInsetsDirectional.all(d.spacing24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: [
                Semantics(
                  header: true,
                  child: Text(
                    a(a.l.libraryImportTo(folderName)),
                    style: t.typography.titleLarge.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ),
                SizedBox(height: d.spacing8),
                Text(
                  summary,
                  style: t.typography.body.copyWith(
                    color: t.colors.textSecondary,
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
                            child: Text(
                              p.finished
                                  ? (p.cancelled
                                        ? a(
                                            a.l.libraryImportCancelled(
                                              p.imported,
                                            ),
                                          )
                                        : a(
                                            a.l.libraryImportDone(
                                              p.imported,
                                              failed.length,
                                            ),
                                          ))
                                  : a(
                                      a.l.libraryImporting(
                                        p.current,
                                        p.total,
                                      ),
                                    ),
                              style: t.typography.title.copyWith(
                                color: t.colors.textPrimary,
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
                                  f.media.displayName,
                                  reasonText(a, f.failure!),
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
                if (job.skipped.isNotEmpty) ...[
                  // FT01A-21: non-media files are skipped and reported.
                  SizedBox(height: d.spacing12),
                  card(
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          a(a.l.libraryImportSkipped(job.skipped.length)),
                          style: t.typography.body.copyWith(
                            color: t.colors.warning,
                          ),
                        ),
                        for (final name in job.skipped.take(20))
                          Text(
                            name,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: t.typography.bodySmall.copyWith(
                              color: t.colors.textSecondary,
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
                // A folder import has no originals to delete (the files
                // stay where they are; only picked documents are offered).
                if (job.folderIds == null) ...[
                  SizedBox(height: d.spacing12),
                  card(
                    _DeleteOriginalsRow(job: job, enabled: !p.finished),
                  ),
                ],
                if (p.originalsDeleted > 0 || p.originalsKept > 0) ...[
                  SizedBox(height: d.spacing8),
                  if (p.originalsDeleted > 0)
                    Text(
                      a(a.l.libraryOriginalsDeleted(p.originalsDeleted)),
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  if (p.originalsKept > 0)
                    Text(
                      a(a.l.libraryOriginalsKept(p.originalsKept)),
                      style: t.typography.bodySmall.copyWith(
                        color: t.colors.warning,
                      ),
                    ),
                ],
                SizedBox(height: d.spacing12),
                card(
                  Row(
                    children: [
                      Icon(
                        t.icons.resolve('info'),
                        size: d.icon20,
                        color: t.colors.textSecondary,
                      ),
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: Text(
                          a(a.l.libraryImportPrivacy),
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
                    label: a(a.l.libraryCancelImport),
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

class _DeleteOriginalsRow extends StatefulWidget {
  const _DeleteOriginalsRow({required this.job, required this.enabled});

  final LibraryImport job;
  final bool enabled;

  @override
  State<_DeleteOriginalsRow> createState() => _DeleteOriginalsRowState();
}

class _DeleteOriginalsRowState extends State<_DeleteOriginalsRow> {
  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                a(a.l.libraryDeleteOriginals),
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
              Text(
                a(a.l.libraryDeleteOriginalsHint),
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ],
          ),
        ),
        VkSwitch(
          value: widget.job.deleteOriginals,
          semanticLabel: a(a.l.libraryDeleteOriginals),
          onChanged: widget.enabled
              ? (v) => setState(() => widget.job.deleteOriginals = v)
              : null,
        ),
      ],
    );
  }
}
