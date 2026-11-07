import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../history/history_store.dart';
import '../l10n/app_text.dart';
import '../pages/launcher.dart';
import '../settings/app_settings.dart';
import '../settings/settings_page.dart';
import 'history_tile.dart';

/// Home filters (design page 7).
enum HomeFilter {
  /// Everything.
  all,

  /// Videos only.
  video,

  /// Images only.
  image,
}

/// App home "最近播放" (REQ-APP-07, design pages 7–8): list/grid,
/// all/video/image filter, resume progress, unavailable records with
/// "重新选择", more menu; first use shows the empty state.
class HomePage extends StatefulWidget {
  /// Creates the page.
  const HomePage({super.key});

  @override
  State<HomePage> createState() => HomePageState();
}

/// State (public for tests).
class HomePageState extends State<HomePage> {
  HomeFilter _filter = HomeFilter.all;

  /// Current filter.
  HomeFilter get filter => _filter;

  List<HistoryEntry> _filtered(List<HistoryEntry> all) => switch (_filter) {
    HomeFilter.all => all,
    HomeFilter.video => [
      for (final e in all)
        if (!e.isImage) e,
    ],
    HomeFilter.image => [
      for (final e in all)
        if (e.isImage) e,
    ],
  };

  Future<void> _menu(HistoryEntry e) async {
    final scope = AppScope.of(context);
    final t = AppText.of(context);
    final choice = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: VkTheme.of(context).colors.surface,
      builder: (context) {
        final th = VkTheme.of(context);
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: EdgeInsetsDirectional.all(th.dimensions.spacing16),
                child: Text(
                  e.displayName,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: th.typography.title.copyWith(
                    color: th.colors.textPrimary,
                  ),
                ),
              ),
              if (!e.isImage && !e.unavailable)
                VkMenuItem(
                  icon: th.icons.resolve('retry'),
                  label: t(t.l.menuFromStart),
                  onPressed: () => Navigator.of(context).pop('start'),
                ),
              if (!e.unavailable)
                VkMenuItem(
                  icon: th.icons.resolve('grid'),
                  label: t(t.l.menuMultiView),
                  onPressed: () => Navigator.of(context).pop('multi'),
                ),
              VkMenuItem(
                icon: th.icons.resolve('delete'),
                label: t(t.l.menuDelete),
                onPressed: () => Navigator.of(context).pop('delete'),
              ),
            ],
          ),
        );
      },
    );
    if (!mounted || choice == null) return;
    switch (choice) {
      case 'start':
        await MediaLauncher.openEntry(context, e, fromStart: true);
      case 'multi':
        final others = [
          for (final x in scope.history.entries)
            if (!x.unavailable && x.id != e.id) x,
        ];
        await MediaLauncher.openMultiView(context, [
          e,
          ...others.take(VideoKitSlotGrid.maxSlots - 1),
        ]);
      case 'delete':
        await scope.history.remove(e.id);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppScope.of(context);
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return ListenableBuilder(
      listenable: Listenable.merge([scope.history, scope.settings]),
      builder: (context, _) {
        final settings = scope.settings.value;
        final all = scope.history.entries;
        final entries = _filtered(all);
        final grid = settings.layout == HomeLayout.grid;
        return Scaffold(
          backgroundColor: t.colors.background,
          body: SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: EdgeInsetsDirectional.fromSTEB(
                    d.spacing16,
                    d.spacing8,
                    d.spacing8,
                    d.spacing8,
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Semantics(
                          header: true,
                          child: Text(
                            a(a.l.homeTitle),
                            style: t.typography.titleLarge.copyWith(
                              color: t.colors.textPrimary,
                            ),
                          ),
                        ),
                      ),
                      if (all.isNotEmpty)
                        VkIconButton(
                          icon: t.icons.resolve(grid ? 'list' : 'grid'),
                          semanticLabel: a(grid ? a.l.homeList : a.l.homeGrid),
                          onPressed: () => unawaited(
                            scope.settings.update(
                              settings.copyWith(
                                layout: grid
                                    ? HomeLayout.list
                                    : HomeLayout.grid,
                              ),
                            ),
                          ),
                        ),
                      VkIconButton(
                        icon: t.icons.resolve('settings'),
                        semanticLabel: a(a.l.homeSettings),
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute<void>(
                            builder: (_) => const SettingsPage(),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                if (all.isEmpty)
                  Expanded(
                    child: _EmptyState(historyOff: !settings.recordHistory),
                  )
                else ...[
                  Padding(
                    padding: EdgeInsetsDirectional.symmetric(
                      horizontal: d.spacing16,
                    ),
                    child: Wrap(
                      spacing: d.spacing8,
                      runSpacing: d.spacing8,
                      children: [
                        for (final f in HomeFilter.values)
                          VkButton(
                            label: a(switch (f) {
                              HomeFilter.all => a.l.filterAll,
                              HomeFilter.video => a.l.filterVideo,
                              HomeFilter.image => a.l.filterImage,
                            }),
                            variant: VkButtonVariant.secondary,
                            selected: f == _filter,
                            onPressed: () => setState(() => _filter = f),
                          ),
                      ],
                    ),
                  ),
                  SizedBox(height: d.spacing12),
                  Expanded(child: _list(context, entries, grid, settings)),
                ],
              ],
            ),
          ),
          floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
          floatingActionButton: all.isEmpty
              ? null
              : Semantics(
                  container: true,
                  child: VkButton(
                    label: a(a.l.openFile),
                    icon: t.icons.resolve('folder'),
                    onPressed: () =>
                        unawaited(MediaLauncher.pickAndOpen(context)),
                  ),
                ),
          bottomNavigationBar: scope.backend.isDemo
              ? SafeArea(
                  child: Padding(
                    padding: EdgeInsetsDirectional.only(bottom: d.spacing4),
                    child: const Center(heightFactor: 1, child: DemoBadge()),
                  ),
                )
              : null,
        );
      },
    );
  }

  Widget _list(
    BuildContext context,
    List<HistoryEntry> entries,
    bool grid,
    AppSettings settings,
  ) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final footer = Padding(
      padding: EdgeInsetsDirectional.fromSTEB(
        d.spacing16,
        d.spacing16,
        d.spacing16,
        d.targetMin * 2,
      ),
      child: Column(
        children: [
          if (!settings.recordHistory)
            Text(
              a(a.l.historyOff),
              textAlign: TextAlign.center,
              style: t.typography.bodySmall.copyWith(color: t.colors.warning),
            ),
          Text(
            a(a.l.footerLimit(HistoryStore.limit)),
            textAlign: TextAlign.center,
            style: t.typography.bodySmall.copyWith(
              color: t.colors.textSecondary,
            ),
          ),
        ],
      ),
    );
    if (entries.isEmpty) {
      return ListView(
        children: [
          Padding(
            padding: EdgeInsetsDirectional.all(d.spacing32),
            child: Text(
              a(a.l.emptyFiltered),
              textAlign: TextAlign.center,
              style: t.typography.body.copyWith(color: t.colors.textSecondary),
            ),
          ),
          footer,
        ],
      );
    }
    Widget tile(HistoryEntry e) => HistoryTile(
      key: ValueKey(e.id),
      entry: e,
      grid: grid,
      onOpen: () => unawaited(MediaLauncher.openEntry(context, e)),
      onReselect: () => unawaited(MediaLauncher.reselect(context, e)),
      onMenu: () => unawaited(_menu(e)),
    );
    if (!grid) {
      return ListView(
        padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
        children: [
          for (final e in entries)
            Padding(
              padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
              child: tile(e),
            ),
          footer,
        ],
      );
    }
    return LayoutBuilder(
      builder: (context, c) {
        final cols = c.maxWidth >= VkLayoutClass.expandedMinWidth
            ? 4
            : (c.maxWidth >= VkLayoutClass.mediumMinWidth ? 3 : 2);
        final rows = <Widget>[];
        for (var i = 0; i < entries.length; i += cols) {
          rows.add(
            Padding(
              padding: EdgeInsetsDirectional.only(bottom: d.spacing16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (var j = 0; j < cols; j++) ...[
                    if (j > 0) SizedBox(width: d.spacing12),
                    Expanded(
                      child: i + j < entries.length
                          ? tile(entries[i + j])
                          : const SizedBox.shrink(),
                    ),
                  ],
                ],
              ),
            ),
          );
        }
        return ListView(
          padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
          children: [...rows, footer],
        );
      },
    );
  }
}

/// First use (design page 8 left): one main action, "打开方式" hint.
class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.historyOff});

  final bool historyOff;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return Center(
      child: SingleChildScrollView(
        padding: EdgeInsetsDirectional.all(d.spacing24),
        child: ConstrainedBox(
          constraints: BoxConstraints(maxWidth: d.targetMin * 10),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: EdgeInsetsDirectional.all(d.spacing32),
                decoration: BoxDecoration(
                  color: t.colors.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  t.icons.resolve('movie'),
                  size: d.targetMin,
                  color: t.colors.primary,
                ),
              ),
              SizedBox(height: d.spacing24),
              Semantics(
                header: true,
                child: Text(
                  a(a.l.emptyTitle),
                  textAlign: TextAlign.center,
                  style: t.typography.titleLarge.copyWith(
                    color: t.colors.textPrimary,
                  ),
                ),
              ),
              SizedBox(height: d.spacing8),
              Text(
                a(a.l.emptyBody),
                textAlign: TextAlign.center,
                style: t.typography.body.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
              if (historyOff) ...[
                SizedBox(height: d.spacing8),
                Text(
                  a(a.l.historyOff),
                  textAlign: TextAlign.center,
                  style: t.typography.bodySmall.copyWith(
                    color: t.colors.warning,
                  ),
                ),
              ],
              SizedBox(height: d.spacing24),
              ConstrainedBox(
                constraints: BoxConstraints(minWidth: d.targetMin * 4),
                child: VkButton(
                  label: a(a.l.openFile),
                  onPressed: () =>
                      unawaited(MediaLauncher.pickAndOpen(context)),
                ),
              ),
              SizedBox(height: d.spacing12),
              Text(
                a(a.l.emptyMulti),
                textAlign: TextAlign.center,
                style: t.typography.bodySmall.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
              SizedBox(height: d.spacing24),
              Container(
                padding: EdgeInsetsDirectional.all(d.spacing16),
                decoration: BoxDecoration(
                  color: t.colors.surface,
                  borderRadius: BorderRadius.circular(d.cornerLarge),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(t.icons.info, color: t.colors.info),
                    SizedBox(width: d.spacing12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            a(a.l.otherAppsTitle),
                            style: t.typography.label.copyWith(
                              color: t.colors.textPrimary,
                            ),
                          ),
                          Text(
                            a(a.l.otherAppsBody),
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
            ],
          ),
        ),
      ),
    );
  }
}
