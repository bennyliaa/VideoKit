import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import '../pages/concat_page.dart';
import '../pages/launcher.dart';
import 'project_store.dart';

/// "最近工程" (M4, App business): edit projects saved when the user left the
/// editor; open restores the snapshot, delete removes it.
class RecentProjectsPage extends StatefulWidget {
  /// Creates the page.
  const RecentProjectsPage({super.key});

  @override
  State<RecentProjectsPage> createState() => _RecentProjectsPageState();
}

class _RecentProjectsPageState extends State<RecentProjectsPage> {
  /// TEST-R4 R4-02: the empty text only points at concatenation when the
  /// Kit can edit; otherwise it says editing is coming. Null while asking.
  bool? _editing;

  @override
  void initState() {
    super.initState();
    unawaited(
      Future(() async {
        if (!mounted) return;
        final scope = AppScope.of(context);
        final ok = await MediaLauncher.concatAvailable(scope);
        if (mounted) setState(() => _editing = ok);
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final scope = AppScope.of(context);
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.background,
        title: Text(
          a(a.l.recentProjects),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
      ),
      body: SafeArea(
        child: ListenableBuilder(
          listenable: scope.projects,
          builder: (context, _) {
            final list = scope.projects.projects;
            if (list.isEmpty) {
              return Center(
                child: Padding(
                  padding: EdgeInsetsDirectional.all(d.spacing24),
                  child: Text(
                    _editing == false
                        ? a(a.l.recentProjectsEmptyNoEditing)
                        : a(a.l.recentProjectsEmpty),
                    textAlign: TextAlign.center,
                    style: t.typography.body.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                ),
              );
            }
            return ListView.separated(
              padding: EdgeInsetsDirectional.all(d.spacing16),
              itemCount: list.length,
              separatorBuilder: (_, _) => SizedBox(height: d.spacing8),
              itemBuilder: (context, i) => _ProjectTile(project: list[i]),
            );
          },
        ),
      ),
    );
  }
}

class _ProjectTile extends StatelessWidget {
  const _ProjectTile({required this.project});

  final RecentProject project;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final scope = AppScope.of(context);
    final saved = DateTime.fromMillisecondsSinceEpoch(project.savedAtEpochMs);
    final duration = project.durationUs;
    final meta = [
      a(a.l.recentProjectClips(project.clipCount)),
      if (duration != null) VkFormat.timecode(duration),
    ];
    return Container(
      decoration: BoxDecoration(
        color: t.colors.surface,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: Row(
        children: [
          Expanded(
            child: MergeSemantics(
              child: InkWell(
                borderRadius: BorderRadius.circular(d.cornerLarge),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (_) => ConcatPage(restore: project),
                  ),
                ),
                child: Padding(
                  padding: EdgeInsetsDirectional.all(d.spacing12),
                  child: Row(
                    children: [
                      Icon(
                        t.icons.resolve('edit'),
                        size: d.icon24,
                        color: t.colors.textSecondary,
                      ),
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              a(a.l.concatTitle(project.clipCount)),
                              style: t.typography.title.copyWith(
                                color: t.colors.textPrimary,
                              ),
                            ),
                            for (final line in [
                              a(
                                a.l.recentProjectSaved(
                                  a.relative(saved, scope.history.now()),
                                ),
                              ),
                              ...meta,
                            ])
                              Text(
                                line,
                                style: t.typography.bodySmall.copyWith(
                                  color: t.colors.textSecondary,
                                ),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          VkIconButton(
            icon: t.icons.resolve('delete'),
            semanticLabel: a(a.l.recentProjectDelete),
            onPressed: () => unawaited(scope.projects.remove(project.id)),
          ),
        ],
      ),
    );
  }
}
