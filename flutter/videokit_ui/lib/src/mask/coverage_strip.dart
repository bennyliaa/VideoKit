import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_data.dart';
import '../theme/theme_scope.dart';

/// Label of a tracking [state].
String coverageStateLabel(VkStrings s, TrackingState state) =>
    s.text(switch (state) {
      TrackingState.tracked => 'coverageTracked',
      TrackingState.lowConfidence => 'coverageLow',
      TrackingState.ambiguous => 'coverageAmbiguous',
      TrackingState.lost => 'coverageLost',
      TrackingState.notAnalyzed => 'coverageNotAnalyzed',
    });

/// Colour of a tracking [state] (`color.track.*`; not analysed = border).
Color coverageStateColor(VideoKitThemeData t, TrackingState state) =>
    switch (state) {
      TrackingState.tracked => t.colors.trackTracked,
      TrackingState.lowConfidence => t.colors.trackLowConfidence,
      TrackingState.ambiguous => t.colors.trackAmbiguous,
      TrackingState.lost => t.colors.trackLost,
      TrackingState.notAnalyzed => t.colors.borderStrong,
    };

/// Paints coverage segments with colour **and** pattern (14 §5.7: LOW
/// diagonal lines, AMBIGUOUS dots, LOST crosses, not analysed dashed
/// outline), so the state never depends on colour alone.
class CoveragePainter extends CustomPainter {
  /// Creates a painter mapping `[0, totalUs]` onto the width, or onto
  /// [xForUs] when given (timeline coordinates).
  CoveragePainter({
    required this.segments,
    required this.totalUs,
    required this.theme,
    this.xForUs,
  });

  /// Segments to draw.
  final List<CoverageRange> segments;

  /// Timeline length.
  final int totalUs;

  /// Theme (colours, stroke widths).
  final VideoKitThemeData theme;

  /// Optional time → x mapping.
  final double Function(int us)? xForUs;

  double _x(int us, Size size) =>
      xForUs?.call(us) ??
      (totalUs <= 0 ? 0 : us / totalUs * size.width).toDouble();

  /// Paints one state into [r] (also used by the legend swatches).
  static void paintState(
    Canvas canvas,
    Rect r,
    TrackingState state,
    VideoKitThemeData t,
  ) {
    final radius = Radius.circular(r.height / 2);
    final rr = RRect.fromRectAndRadius(r, radius);
    final stroke = t.dimensions.borderWidth;
    if (state == TrackingState.notAnalyzed) {
      final paint = Paint()
        ..color = t.colors.borderStrong
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke;
      final path = Path()..addRRect(rr.deflate(stroke / 2));
      for (final metric in path.computeMetrics()) {
        final dash = r.height * 0.6;
        for (var d = 0.0; d < metric.length; d += dash * 2) {
          canvas.drawPath(metric.extractPath(d, d + dash), paint);
        }
      }
      return;
    }
    canvas.drawRRect(rr, Paint()..color = coverageStateColor(t, state));
    final ink = Paint()
      ..color = t.colors.playerCanvas.withValues(alpha: 0.55)
      ..strokeWidth = stroke * 1.5
      ..strokeCap = StrokeCap.round;
    canvas
      ..save()
      ..clipRRect(rr);
    final step = math.max(4.0, r.height);
    switch (state) {
      case TrackingState.lowConfidence:
        for (var x = r.left - r.height; x < r.right; x += step * 0.75) {
          canvas.drawLine(
            Offset(x, r.bottom),
            Offset(x + r.height, r.top),
            ink,
          );
        }
      case TrackingState.ambiguous:
        for (var x = r.left + step / 2; x < r.right; x += step) {
          canvas.drawCircle(Offset(x, r.center.dy), stroke * 1.2, ink);
        }
      case TrackingState.lost:
        final h = r.height * 0.3;
        for (var x = r.left + step / 2; x < r.right; x += step * 1.25) {
          final c = Offset(x, r.center.dy);
          canvas
            ..drawLine(c + Offset(-h, -h), c + Offset(h, h), ink)
            ..drawLine(c + Offset(-h, h), c + Offset(h, -h), ink);
        }
      case TrackingState.tracked || TrackingState.notAnalyzed:
        break;
    }
    canvas.restore();
  }

  @override
  void paint(Canvas canvas, Size size) {
    final gap = theme.dimensions.borderWidth;
    for (final seg in segments) {
      final l = _x(seg.startUs, size);
      final r = _x(seg.endUs, size);
      if (r <= l) continue;
      final rect = Rect.fromLTRB(
        l + gap,
        0,
        math.max(l + gap, r - gap),
        size.height,
      );
      paintState(canvas, rect, seg.state, theme);
      if (seg.accepted) {
        canvas.drawRect(
          Rect.fromLTWH(rect.left, size.height - gap * 2, rect.width, gap * 2),
          Paint()..color = theme.colors.textPrimary,
        );
      }
    }
  }

  @override
  bool shouldRepaint(CoveragePainter old) =>
      old.segments != segments ||
      old.totalUs != totalUs ||
      old.theme != theme ||
      old.xForUs != xForUs;
}

/// UI-07 `CoverageStrip` (14 §5.7, design pages 15/18): one target's
/// coverage across the timeline, with a screen-reader summary of every
/// segment.
class CoverageStrip extends StatelessWidget {
  /// Creates a strip.
  const CoverageStrip({
    super.key,
    required this.report,
    required this.totalUs,
    required this.name,
    this.height,
  });

  /// Coverage of the target.
  final CoverageReport report;

  /// Timeline length.
  final int totalUs;

  /// Target name (screen reader).
  final String name;

  /// Height (default: timeline coverage strip token × 2).
  final double? height;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final segments = report.segments;
    final value = [
      for (final seg in segments)
        s.coverageSegment(
          coverageStateLabel(s, seg.state),
          VkFormat.timecodeTenths(seg.startUs),
          VkFormat.timecodeTenths(seg.endUs),
        ),
    ].join('；');
    return Semantics(
      container: true,
      label: s.coverageStripLabel(name),
      value: value,
      child: SizedBox(
        height: height ?? t.dimensions.timelineCoverageStrip * 2,
        width: double.infinity,
        child: CustomPaint(
          painter: CoveragePainter(
            segments: segments.isEmpty
                ? [
                    CoverageRange(
                      startUs: 0,
                      endUs: totalUs,
                      state: TrackingState.notAnalyzed,
                    ),
                  ]
                : segments,
            totalUs: totalUs,
            theme: t,
          ),
        ),
      ),
    );
  }
}

/// Legend of the five coverage states (pattern swatch + label).
class CoverageLegend extends StatelessWidget {
  /// Creates the legend.
  const CoverageLegend({super.key});

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Wrap(
      spacing: d.spacing16,
      runSpacing: d.spacing8,
      children: [
        for (final state in TrackingState.values)
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              ExcludeSemantics(
                child: SizedBox(
                  width: d.spacing24,
                  height: d.timelineCoverageStrip * 1.5,
                  child: CustomPaint(painter: _SwatchPainter(state, t)),
                ),
              ),
              SizedBox(width: d.spacing8),
              Text(
                coverageStateLabel(s, state),
                style: t.typography.caption.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ],
          ),
      ],
    );
  }
}

class _SwatchPainter extends CustomPainter {
  _SwatchPainter(this.state, this.theme);

  final TrackingState state;
  final VideoKitThemeData theme;

  @override
  void paint(Canvas canvas, Size size) =>
      CoveragePainter.paintState(canvas, Offset.zero & size, state, theme);

  @override
  bool shouldRepaint(_SwatchPainter old) =>
      old.state != state || old.theme != theme;
}
