import 'dart:math' as math;

import 'package:flutter/foundation.dart';

/// Time ↔ pixel mapping of the timeline (14 §5.6 `TimelineScale`):
/// `x = (tUs / 1e6) * pxPerSecond - scrollX`.
@immutable
final class TimelineScale {
  /// Creates a scale.
  const TimelineScale({required this.pxPerSecond, this.scrollX = 0});

  /// Zoom limits (px per second).
  static const double minPxPerSecond = 10;

  /// Upper zoom limit.
  static const double maxPxPerSecond = 400;

  /// Pixels per second.
  final double pxPerSecond;

  /// Horizontal scroll offset (px).
  final double scrollX;

  /// X position of [us] in the viewport.
  double xForUs(int us) => us / 1e6 * pxPerSecond - scrollX;

  /// Time at viewport [x] (not clamped).
  int usForX(double x) => ((x + scrollX) / pxPerSecond * 1e6).round();

  /// Width of [us] in pixels.
  double widthForUs(int us) => us / 1e6 * pxPerSecond;

  /// Content width of a timeline [durationUs] long.
  double contentWidth(int durationUs) => widthForUs(durationUs);

  /// Zooms by [factor] keeping the time under [focusX] in place.
  TimelineScale zoomAround(double focusX, double factor) {
    final focusUs = (focusX + scrollX) / pxPerSecond;
    final next = (pxPerSecond * factor).clamp(minPxPerSecond, maxPxPerSecond);
    return TimelineScale(pxPerSecond: next, scrollX: focusUs * next - focusX);
  }

  /// Copy scrolled to [x], clamped to the content of [durationUs] in a
  /// viewport [viewport] wide.
  TimelineScale scrolledTo(double x, int durationUs, double viewport) {
    final maxScroll = math.max(0.0, contentWidth(durationUs) - viewport / 2);
    return TimelineScale(
      pxPerSecond: pxPerSecond,
      scrollX: x.clamp(-viewport / 2, maxScroll),
    );
  }

  /// Tick spacing (µs) giving labels at least [minLabelPx] apart.
  int tickStepUs({double minLabelPx = 64}) {
    const steps = [1, 2, 5, 10, 20, 30, 60, 120, 300, 600];
    for (final s in steps) {
      if (s * pxPerSecond >= minLabelPx) return s * 1000000;
    }
    return steps.last * 1000000;
  }

  /// Snaps [us] to the nearest of [targets] within [thresholdPx]; returns
  /// the snapped time or null when nothing is close enough (14 §5.6: 8 dp).
  int? snap(int us, Iterable<int> targets, double thresholdPx) {
    int? best;
    var bestPx = thresholdPx;
    for (final t in targets) {
      final d = widthForUs((t - us).abs());
      if (d <= bestPx) {
        bestPx = d;
        best = t;
      }
    }
    return best;
  }

  @override
  bool operator ==(Object other) =>
      other is TimelineScale &&
      other.pxPerSecond == pxPerSecond &&
      other.scrollX == scrollX;

  @override
  int get hashCode => Object.hash(pxPerSecond, scrollX);

  @override
  String toString() => 'TimelineScale($pxPerSecond px/s, scroll $scrollX)';
}
