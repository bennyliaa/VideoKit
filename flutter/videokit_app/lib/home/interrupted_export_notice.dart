import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../entitlement/entitlement_gate.dart';
import '../entitlement/entitlement_service.dart';
import '../l10n/app_text.dart';
import '../pages/concat_page.dart';
import '../projects/export_journal.dart';

/// Home notice after the App stopped during an export (M6-A1, 08 §6
/// "进程终止"): the source is untouched, the unfinished output is discarded,
/// and the saved project can be exported again.
class InterruptedExportNotice extends StatelessWidget {
  /// Creates the notice.
  const InterruptedExportNotice({super.key, required this.interrupted});

  /// What was running.
  final InterruptedExport interrupted;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final scope = AppScope.of(context);
    final project = scope.projects.projects
        .where((p) => p.id == interrupted.projectId)
        .firstOrNull;
    return Padding(
      padding: EdgeInsetsDirectional.fromSTEB(
        d.spacing16,
        0,
        d.spacing16,
        d.spacing12,
      ),
      child: Semantics(
        container: true,
        liveRegion: true,
        child: Container(
          padding: EdgeInsetsDirectional.all(d.spacing12),
          decoration: BoxDecoration(
            color: t.colors.warningContainer,
            borderRadius: BorderRadius.circular(d.cornerMedium),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                a(a.l.exportInterruptedTitle),
                style: t.typography.body.copyWith(
                  fontWeight: FontWeight.w600,
                  color: t.colors.textPrimary,
                ),
              ),
              SizedBox(height: d.spacing4),
              Text(
                a(a.l.exportInterruptedDetail),
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textPrimary,
                ),
              ),
              SizedBox(height: d.spacing8),
              Wrap(
                spacing: d.spacing8,
                runSpacing: d.spacing8,
                alignment: WrapAlignment.end,
                children: [
                  VkButton(
                    label: a(a.l.exportInterruptedDismiss),
                    variant: VkButtonVariant.text,
                    onPressed: () =>
                        unawaited(scope.exportJournal.dismiss()),
                  ),
                  if (project != null)
                    VkButton(
                      label: a(a.l.exportInterruptedAgain),
                      // REQ-APP-15: editing is paid; the prompt first.
                      onPressed: () async {
                        if (!await ensureEntitled(context, AppFeature.edit)) {
                          return;
                        }
                        unawaited(scope.exportJournal.dismiss());
                        if (!context.mounted) return;
                        unawaited(
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) => ConcatPage(restore: project),
                            ),
                          ),
                        );
                      },
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
