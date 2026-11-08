import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../common/vk_buttons.dart';
import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import 'video_kit_slot_grid.dart';

/// UI-05 multi-view page chrome (design page 14), shared by every host so
/// the page looks the same everywhere: the title with "n / 12", "全部静音"
/// and the layout menu at the top end, an optional capability notice, the
/// [grid], and a bottom bar with the hint and "全部静音 / 添加媒体".
///
/// At large text (200 %, J9 / TEST-R4 R4-03) the page scrolls as one, the
/// bottom bar's actions and the layout move into the top bar's "更多"
/// menu, and the hint is left out, so nothing is pushed off screen.
class VideoKitMultiViewScaffold extends StatelessWidget {
  /// Creates the page.
  const VideoKitMultiViewScaffold({
    super.key,
    required this.grid,
    required this.count,
    this.title,
    this.leading,
    this.notice,
    this.onMuteAll,
    this.onAdd,
    this.layout = SlotGridLayout.auto,
    this.onLayoutChanged,
  });

  /// The grid (usually a [VideoKitSlotGrid] of `VideoKitSlot`s).
  final Widget grid;

  /// Slots shown (for "n / 12").
  final int count;

  /// Title (default "多画面").
  final String? title;

  /// Leading widget of the top bar (e.g. a back button).
  final Widget? leading;

  /// Capability notice (design page 14, ④), already localized.
  final String? notice;

  /// "全部静音"; null disables it (nothing has audio).
  final VoidCallback? onMuteAll;

  /// "添加媒体"; null hides it (the host cannot add, or the grid is full).
  final VoidCallback? onAdd;

  /// Current grid layout.
  final SlotGridLayout layout;

  /// Layout choice; null hides the layout menu.
  final ValueChanged<SlotGridLayout>? onLayoutChanged;

  /// Label of a grid layout.
  static String layoutLabel(VkStrings s, SlotGridLayout l) =>
      s.text(switch (l) {
        SlotGridLayout.auto => 'gridLayoutAuto',
        SlotGridLayout.grid2x2 => 'gridLayout2x2',
        SlotGridLayout.grid3x3 => 'gridLayout3x3',
        SlotGridLayout.grid3x4 => 'gridLayout3x4',
      });

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final large = VkLayoutClass.collapseSecondary(
      MediaQuery.textScalerOf(context),
    );
    final full = count >= VideoKitSlotGrid.maxSlots;
    final add = full ? null : onAdd;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.background,
        automaticallyImplyLeading: leading == null,
        leading: leading,
        title: Wrap(
          spacing: d.spacing12,
          crossAxisAlignment: WrapCrossAlignment.end,
          children: [
            Text(
              title ?? s.text('gridTitle'),
              style: t.typography.titleLarge.copyWith(
                color: t.colors.textPrimary,
              ),
            ),
            Text(
              s.gridCount(count, VideoKitSlotGrid.maxSlots),
              style: t.typography.body.copyWith(color: t.colors.textSecondary),
            ),
          ],
        ),
        actions: large
            ? [
                _MoreMenu(
                  onMuteAll: onMuteAll,
                  onAdd: onAdd == null ? null : add,
                  showAdd: onAdd != null,
                  layout: layout,
                  onLayoutChanged: onLayoutChanged,
                ),
              ]
            : [
                VkIconButton(
                  icon: t.icons.resolve('mute'),
                  semanticLabel: s.text('gridMuteAll'),
                  onPressed: onMuteAll,
                ),
                if (onLayoutChanged != null)
                  _LayoutMenu(selected: layout, onSelected: onLayoutChanged!),
              ],
      ),
      body: SafeArea(
        child: Padding(
          padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
          child: LayoutBuilder(
            builder: (context, c) {
              final scroll = large || c.maxHeight < d.targetMin * 12;
              final noticeBox = notice == null
                  ? null
                  : Padding(
                      padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
                      child: _Notice(text: notice!),
                    );
              final bar = large
                  ? null
                  : _BottomBar(
                      onMuteAll: onMuteAll,
                      onAdd: add,
                      showAdd: onAdd != null,
                    );
              if (scroll) {
                // One scroll for the notice, the grid and the bar (the grid
                // is unbounded here and lays out every row).
                return ListView(
                  key: const ValueKey('vk-multiview-scroll'),
                  children: [
                    ?noticeBox,
                    if (large)
                      grid
                    else
                      SizedBox(
                        height: math.max(c.maxHeight * 0.75, d.targetMin * 6),
                        child: grid,
                      ),
                    ?bar,
                    SizedBox(height: d.spacing12),
                  ],
                );
              }
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ?noticeBox,
                  Expanded(child: grid),
                  ?bar,
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _BottomBar extends StatelessWidget {
  const _BottomBar({
    required this.onMuteAll,
    required this.onAdd,
    required this.showAdd,
  });

  final VoidCallback? onMuteAll;
  final VoidCallback? onAdd;
  final bool showAdd;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing12),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: t.colors.surface,
          borderRadius: BorderRadius.circular(d.cornerLarge),
        ),
        child: Padding(
          padding: EdgeInsetsDirectional.all(d.spacing16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                s.text('gridHint'),
                style: t.typography.body.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
              SizedBox(height: d.spacing12),
              Wrap(
                spacing: d.spacing12,
                runSpacing: d.spacing8,
                alignment: WrapAlignment.spaceBetween,
                children: [
                  VkButton(
                    label: s.text('gridMuteAll'),
                    variant: VkButtonVariant.secondary,
                    onPressed: onMuteAll,
                  ),
                  if (showAdd)
                    VkButton(label: s.text('gridAddMedia'), onPressed: onAdd),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LayoutMenu extends StatelessWidget {
  const _LayoutMenu({required this.selected, required this.onSelected});

  final SlotGridLayout selected;
  final ValueChanged<SlotGridLayout> onSelected;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return MenuAnchor(
      style: MenuStyle(
        backgroundColor: WidgetStatePropertyAll(t.colors.surfaceHigh),
      ),
      menuChildren: [
        for (final l in SlotGridLayout.values)
          MenuItemButton(
            onPressed: () => onSelected(l),
            trailingIcon: l == selected
                ? Icon(t.icons.check, size: d.icon20, color: t.colors.primary)
                : null,
            child: Text(
              VideoKitMultiViewScaffold.layoutLabel(s, l),
              style: t.typography.body.copyWith(color: t.colors.textPrimary),
            ),
          ),
      ],
      builder: (context, menu, _) => VkIconButton(
        icon: t.icons.resolve('grid'),
        semanticLabel: s.text('gridLayout'),
        semanticValue: VideoKitMultiViewScaffold.layoutLabel(s, selected),
        onPressed: () => menu.isOpen ? menu.close() : menu.open(),
      ),
    );
  }
}

/// Large text: mute all, add media and the layouts in one "更多" menu.
class _MoreMenu extends StatelessWidget {
  const _MoreMenu({
    required this.onMuteAll,
    required this.onAdd,
    required this.showAdd,
    required this.layout,
    required this.onLayoutChanged,
  });

  final VoidCallback? onMuteAll;
  final VoidCallback? onAdd;
  final bool showAdd;
  final SlotGridLayout layout;
  final ValueChanged<SlotGridLayout>? onLayoutChanged;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget item(String text, VoidCallback? onPressed, {Widget? trailing}) =>
        MenuItemButton(
          onPressed: onPressed,
          trailingIcon: trailing,
          child: Text(
            text,
            style: t.typography.body.copyWith(
              color: onPressed == null
                  ? t.colors.textTertiary
                  : t.colors.textPrimary,
            ),
          ),
        );
    return MenuAnchor(
      style: MenuStyle(
        backgroundColor: WidgetStatePropertyAll(t.colors.surfaceHigh),
      ),
      menuChildren: [
        item(s.text('gridMuteAll'), onMuteAll),
        if (showAdd) item(s.text('gridAddMedia'), onAdd),
        if (onLayoutChanged != null)
          for (final l in SlotGridLayout.values)
            item(
              VideoKitMultiViewScaffold.layoutLabel(s, l),
              () => onLayoutChanged!(l),
              trailing: l == layout
                  ? Icon(t.icons.check, size: d.icon20, color: t.colors.primary)
                  : null,
            ),
      ],
      builder: (context, menu, _) => VkIconButton(
        icon: t.icons.resolve('more'),
        semanticLabel: s.text('commonMore'),
        onPressed: () => menu.isOpen ? menu.close() : menu.open(),
      ),
    );
  }
}

/// Capability notice (design page 14, ④): warning container colours.
class _Notice extends StatelessWidget {
  const _Notice({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Semantics(
      liveRegion: true,
      container: true,
      child: Container(
        padding: EdgeInsetsDirectional.all(d.spacing12),
        decoration: BoxDecoration(
          color: t.colors.warningContainer,
          borderRadius: BorderRadius.circular(d.cornerMedium),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              t.icons.resolve('info'),
              size: d.icon20,
              color: t.colors.warning,
            ),
            SizedBox(width: d.spacing8),
            Expanded(
              child: Text(
                text,
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
