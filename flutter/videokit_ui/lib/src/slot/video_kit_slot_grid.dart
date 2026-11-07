import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../foundation/layout_class.dart';
import '../theme/theme_scope.dart';

/// Grid shapes of [VideoKitSlotGrid] (14 §5.5).
enum SlotGridLayout {
  /// Chosen from the slot count and layout class.
  auto,

  /// 2 columns × 2 rows.
  grid2x2,

  /// 3 × 3.
  grid3x3,

  /// 4 columns × 3 rows.
  grid3x4,
}

/// UI-05 multi-view grid (14 §5.5, design page 14): at most
/// [VideoKitSlotGrid.maxSlots] slots. Each slot is its own widget with its
/// own selector, so one slot changing (error, progress) never rebuilds the
/// others; slots should carry stable keys (e.g. the session ID).
class VideoKitSlotGrid extends StatelessWidget {
  /// Creates a grid.
  const VideoKitSlotGrid({
    super.key,
    required this.slots,
    this.layout = SlotGridLayout.auto,
    this.minCellHeight,
  });

  /// Upper limit of slots (videos: 12, 07 §3).
  static const int maxSlots = 12;

  /// Slots (usually `VideoKitSlot`s); extra ones beyond [maxSlots] are not
  /// shown.
  final List<Widget> slots;

  /// Grid shape.
  final SlotGridLayout layout;

  /// Below this cell height the grid scrolls instead of shrinking; default
  /// four touch targets.
  final double? minCellHeight;

  /// Columns for [count] slots: `auto` uses 2 on compact widths (phone
  /// default 2×2) and 2/3/4 by count on wider ones (tablet default 3×3).
  static int columnsFor(
    int count,
    SlotGridLayout layout,
    VkLayoutClass layoutClass,
  ) => switch (layout) {
    SlotGridLayout.grid2x2 => 2,
    SlotGridLayout.grid3x3 => 3,
    SlotGridLayout.grid3x4 => 4,
    SlotGridLayout.auto =>
      layoutClass == VkLayoutClass.compact
          ? (count <= 1 ? 1 : 2)
          : (count <= 1
                ? 1
                : count <= 4
                ? 2
                : count <= 9
                ? 3
                : 4),
  };

  /// Rows the shape shows without scrolling (auto: as many as needed).
  static int rowsFor(int count, int columns, SlotGridLayout layout) {
    final needed = (count / columns).ceil();
    return switch (layout) {
      SlotGridLayout.grid2x2 => math.max(2, needed),
      SlotGridLayout.grid3x3 => math.max(3, needed),
      SlotGridLayout.grid3x4 => math.max(3, needed),
      SlotGridLayout.auto => math.max(1, needed),
    };
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final gap = d.spacing12;
    final shown = slots.take(maxSlots).toList();
    return LayoutBuilder(
      builder: (context, c) {
        final width = c.maxWidth.isFinite ? c.maxWidth : d.targetMin * 16;
        final cols = columnsFor(
          shown.length,
          layout,
          VkLayoutClass.fromWidth(width),
        );
        final rows = rowsFor(shown.length, cols, layout);
        final cellWidth = (width - gap * (cols - 1)) / cols;
        final minHeight = minCellHeight ?? d.targetMin * 4;
        final fitHeight = c.maxHeight.isFinite
            ? (c.maxHeight - gap * (rows - 1)) / rows
            : double.infinity;
        final scroll = !fitHeight.isFinite || fitHeight < minHeight;
        final cellHeight = scroll
            ? math.max(minHeight, cellWidth * 9 / 16)
            : fitHeight;
        final rowWidgets = <Widget>[
          for (var r = 0; r * cols < shown.length; r++)
            Padding(
              padding: EdgeInsetsDirectional.only(top: r == 0 ? 0 : gap),
              child: SizedBox(
                height: cellHeight,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    for (var i = 0; i < cols; i++) ...[
                      if (i > 0) SizedBox(width: gap),
                      SizedBox(
                        width: cellWidth,
                        child: r * cols + i < shown.length
                            ? shown[r * cols + i]
                            : const SizedBox.shrink(),
                      ),
                    ],
                  ],
                ),
              ),
            ),
        ];
        final column = Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: rowWidgets,
        );
        return scroll
            ? SingleChildScrollView(child: column)
            : Align(alignment: AlignmentDirectional.topStart, child: column);
      },
    );
  }
}
