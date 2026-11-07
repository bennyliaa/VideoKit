import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import '../theme/theme_scope.dart';

/// Mini map shown while zoomed (14 §5.3 `MiniMap`): the whole picture as a
/// frame with the visible part outlined in the primary colour.
class VkMiniMap extends StatelessWidget {
  /// Creates a mini map.
  const VkMiniMap({
    super.key,
    required this.transform,
    required this.mediaSize,
    required this.label,
  });

  /// Current transform (scale ≥ 1, pan normalized to the picture size).
  final MediaTransform transform;

  /// Picture size (aspect ratio), null = 16:9.
  final VideoSize? mediaSize;

  /// Screen-reader label.
  final String label;

  /// Visible part in picture coordinates (0–1).
  static Rect visibleRect(MediaTransform t) {
    final w = (1 / math.max(1.0, t.scale)).clamp(0.0, 1.0);
    final cx = 0.5 - t.panX / math.max(1.0, t.scale);
    final cy = 0.5 - t.panY / math.max(1.0, t.scale);
    final left = (cx - w / 2).clamp(0.0, 1.0 - w);
    final top = (cy - w / 2).clamp(0.0, 1.0 - w);
    return Rect.fromLTWH(left, top, w, w);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final m = mediaSize;
    var ratio = m == null || m.height == 0 ? 16 / 9 : m.width / m.height;
    if (transform.rotationDeg % 180 != 0) ratio = 1 / ratio;
    final width = d.targetMin * 2;
    return Semantics(
      container: true,
      label: label,
      image: true,
      child: Container(
        width: width,
        height: width / ratio,
        decoration: BoxDecoration(
          color: t.drawables.glassPlayer.color,
          borderRadius: BorderRadius.circular(d.cornerSmall),
          border: Border.all(color: t.colors.borderStrong),
        ),
        child: CustomPaint(
          painter: _MiniMapPainter(
            visible: visibleRect(transform),
            color: t.colors.primary,
            stroke: d.focusRingWidth,
          ),
        ),
      ),
    );
  }
}

class _MiniMapPainter extends CustomPainter {
  _MiniMapPainter({
    required this.visible,
    required this.color,
    required this.stroke,
  });

  final Rect visible;
  final Color color;
  final double stroke;

  @override
  void paint(Canvas canvas, Size size) {
    final r = Rect.fromLTWH(
      visible.left * size.width,
      visible.top * size.height,
      visible.width * size.width,
      visible.height * size.height,
    ).deflate(stroke / 2);
    canvas.drawRect(
      r,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = stroke,
    );
  }

  @override
  bool shouldRepaint(_MiniMapPainter old) =>
      old.visible != visible || old.color != color || old.stroke != stroke;
}
