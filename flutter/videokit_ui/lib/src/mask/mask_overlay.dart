import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../l10n/vk_strings.dart';
import '../theme/theme_data.dart';
import '../theme/theme_scope.dart';

/// Displayed picture rectangle inside [box] for [media] with "fit"
/// (normalized mask coordinates map onto this rectangle).
Rect vkDisplayRect(Size box, VideoSize? media) {
  final m = media ?? const VideoSize(16, 9);
  final ratio = m.height == 0 ? 16 / 9 : m.width / m.height;
  var w = box.width;
  var h = w / ratio;
  if (h > box.height) {
    h = box.height;
    w = h * ratio;
  }
  return Rect.fromLTWH((box.width - w) / 2, (box.height - h) / 2, w, h);
}

/// Region ↔ pixel rectangle inside [picture].
Rect vkRegionToRect(MaskRegion r, Rect picture) => Rect.fromLTWH(
  picture.left + r.x * picture.width,
  picture.top + r.y * picture.height,
  r.width * picture.width,
  r.height * picture.height,
);

/// Pixel rectangle → region (clamped to the picture, minimum size 2 %).
MaskRegion vkRectToRegion(Rect rect, Rect picture) {
  final l = ((rect.left - picture.left) / picture.width).clamp(0.0, 0.98);
  final t = ((rect.top - picture.top) / picture.height).clamp(0.0, 0.98);
  final w = (rect.width / picture.width).clamp(0.02, 1.0 - l);
  final h = (rect.height / picture.height).clamp(0.02, 1.0 - t);
  return MaskRegion(x: l, y: t, width: w, height: h);
}

/// A box drawn on the picture.
@immutable
final class OverlayBox {
  /// Creates a box.
  const OverlayBox({
    required this.id,
    required this.region,
    required this.label,
    this.selected = false,
    this.dashed = false,
    this.reference = false,
    this.semanticLabel,
  });

  /// ID (mask or candidate).
  final String id;

  /// Region.
  final MaskRegion region;

  /// Label above the box.
  final String label;

  /// Selected (cyan, editable).
  final bool selected;

  /// Dashed white (unselected face candidate).
  final bool dashed;

  /// Red dashed reference (position before a loss, design page 19).
  final bool reference;

  /// Screen-reader label when it differs from [label].
  final String? semanticLabel;
}

/// What a drag on the overlay does.
enum OverlayDrawMode {
  /// Move/resize the selected box only.
  edit,

  /// Draw a new rectangle (object selection, correction).
  draw,
}

/// UI-07 `MaskOverlay` (14 §5.7): boxes over the preview picture; the
/// selected box has 8 handles (touch target ≥ 24 dp) and a move area. A
/// drag changes only the local rectangle; [onCommit] fires once on
/// release with the normalized region (UpdateMaskKeyframe / CorrectTracking
/// / StartTracking seed).
class MaskOverlay extends StatefulWidget {
  /// Creates an overlay.
  const MaskOverlay({
    super.key,
    required this.boxes,
    required this.mediaSize,
    this.mode = OverlayDrawMode.edit,
    this.onCommit,
    this.onTapBox,
  });

  /// Boxes (at most one selected).
  final List<OverlayBox> boxes;

  /// Picture size (aspect ratio).
  final VideoSize? mediaSize;

  /// Drag behaviour.
  final OverlayDrawMode mode;

  /// Edited or drawn region on release.
  final ValueChanged<MaskRegion>? onCommit;

  /// A box was tapped (candidate selection).
  final ValueChanged<String>? onTapBox;

  @override
  State<MaskOverlay> createState() => _MaskOverlayState();
}

enum _Grip { move, n, s, e, w, ne, nw, se, sw, draw }

class _MaskOverlayState extends State<MaskOverlay> {
  Rect? _local;
  _Grip? _grip;
  Offset? _anchor;
  Rect? _startRect;

  OverlayBox? get _selected =>
      widget.boxes.where((b) => b.selected).firstOrNull;

  _Grip? _hit(Offset p, Rect r, double target) {
    final half = target / 2;
    bool near(Offset a) => (p - a).distance <= half;
    if (near(r.topLeft)) return _Grip.nw;
    if (near(r.topRight)) return _Grip.ne;
    if (near(r.bottomLeft)) return _Grip.sw;
    if (near(r.bottomRight)) return _Grip.se;
    if (near(r.topCenter)) return _Grip.n;
    if (near(r.bottomCenter)) return _Grip.s;
    if (near(r.centerLeft)) return _Grip.w;
    if (near(r.centerRight)) return _Grip.e;
    if (r.contains(p)) return _Grip.move;
    return null;
  }

  void _start(Offset p, Rect picture, double target) {
    final sel = _selected;
    if (widget.mode == OverlayDrawMode.draw) {
      setState(() {
        _grip = _Grip.draw;
        _anchor = p;
        _local = Rect.fromPoints(p, p);
      });
      return;
    }
    if (sel == null) return;
    final r = vkRegionToRect(sel.region, picture);
    final g = _hit(p, r, target);
    if (g == null) return;
    setState(() {
      _grip = g;
      _anchor = p;
      _startRect = r;
      _local = r;
    });
  }

  void _update(Offset p, Rect picture) {
    final g = _grip;
    final a = _anchor;
    if (g == null || a == null) return;
    if (g == _Grip.draw) {
      setState(() => _local = Rect.fromPoints(a, p).intersect(picture));
      return;
    }
    final r = _startRect!;
    final d = p - a;
    var l = r.left, t = r.top, rr = r.right, b = r.bottom;
    switch (g) {
      case _Grip.move:
        final dx = d.dx.clamp(picture.left - r.left, picture.right - r.right);
        final dy = d.dy.clamp(picture.top - r.top, picture.bottom - r.bottom);
        l += dx;
        rr += dx;
        t += dy;
        b += dy;
      case _Grip.n:
        t += d.dy;
      case _Grip.s:
        b += d.dy;
      case _Grip.e:
        rr += d.dx;
      case _Grip.w:
        l += d.dx;
      case _Grip.ne:
        t += d.dy;
        rr += d.dx;
      case _Grip.nw:
        t += d.dy;
        l += d.dx;
      case _Grip.se:
        b += d.dy;
        rr += d.dx;
      case _Grip.sw:
        b += d.dy;
        l += d.dx;
      case _Grip.draw:
        break;
    }
    setState(
      () => _local = Rect.fromLTRB(
        math.min(l, rr),
        math.min(t, b),
        math.max(l, rr),
        math.max(t, b),
      ).intersect(picture),
    );
  }

  void _end(Rect picture) {
    final r = _local;
    final g = _grip;
    setState(() {
      _grip = null;
      _anchor = null;
      _startRect = null;
      _local = null;
    });
    if (r == null || g == null || r.width < 4 || r.height < 4) return;
    widget.onCommit?.call(vkRectToRegion(r, picture));
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final target = t.dimensions.maskBoxHandleTarget;
    return LayoutBuilder(
      builder: (context, c) {
        final box = Size(c.maxWidth, c.maxHeight);
        final picture = vkDisplayRect(box, widget.mediaSize);
        final sel = _selected;
        return Stack(
          children: [
            Positioned.fill(
              child: GestureDetector(
                excludeFromSemantics: true,
                behavior: HitTestBehavior.translucent,
                onTapUp: (d) {
                  for (final b in widget.boxes.reversed) {
                    if (vkRegionToRect(
                      b.region,
                      picture,
                    ).contains(d.localPosition)) {
                      widget.onTapBox?.call(b.id);
                      return;
                    }
                  }
                },
                onPanStart: (d) => _start(d.localPosition, picture, target),
                onPanUpdate: (d) => _update(d.localPosition, picture),
                onPanEnd: (_) => _end(picture),
                child: CustomPaint(
                  painter: _OverlayPainter(
                    boxes: widget.boxes,
                    picture: picture,
                    local: _local,
                    drawing: _grip == _Grip.draw,
                    theme: t,
                    textDirection: Directionality.of(context),
                    fontFamily: DefaultTextStyle.of(context).style.fontFamily,
                  ),
                ),
              ),
            ),
            // Semantics: one node per box (tap selects candidates).
            for (final b in widget.boxes)
              Positioned.fromRect(
                // At least one touch target, centred on the box (a11y).
                rect: _semanticRect(
                  vkRegionToRect(b.region, picture),
                  t.dimensions.targetMin,
                ),
                child: Semantics(
                  container: true,
                  button: widget.onTapBox != null,
                  selected: b.selected,
                  label: b.semanticLabel ?? b.label,
                  hint: identical(b, sel) ? s.text('maskBoxHint') : null,
                  onTap: widget.onTapBox == null
                      ? null
                      : () => widget.onTapBox!(b.id),
                  child: const IgnorePointer(child: SizedBox.expand()),
                ),
              ),
          ],
        );
      },
    );
  }
}

class _OverlayPainter extends CustomPainter {
  _OverlayPainter({
    required this.boxes,
    required this.picture,
    required this.local,
    required this.drawing,
    required this.theme,
    required this.textDirection,
    this.fontFamily,
  });

  final List<OverlayBox> boxes;
  final Rect picture;
  final Rect? local;
  final bool drawing;
  final VideoKitThemeData theme;
  final TextDirection textDirection;
  final String? fontFamily;

  void _dashed(Canvas canvas, Rect r, Paint p) {
    final path = Path()..addRect(r);
    final dash = theme.dimensions.spacing8;
    for (final m in path.computeMetrics()) {
      for (var d = 0.0; d < m.length; d += dash * 1.6) {
        canvas.drawPath(m.extractPath(d, d + dash), p);
      }
    }
  }

  void _label(Canvas canvas, String text, Rect r, Color bg, Color fg) {
    final d = theme.dimensions;
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: theme.typography.label.copyWith(
          color: fg,
          fontFamily: fontFamily,
        ),
      ),
      textDirection: textDirection,
      maxLines: 1,
    )..layout();
    final pad = d.spacing8;
    final chip = Rect.fromLTWH(
      r.left,
      r.top - tp.height - d.spacing8 - d.spacing4,
      tp.width + pad * 2,
      tp.height + d.spacing4,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(chip, Radius.circular(d.cornerFull)),
      Paint()..color = bg,
    );
    tp.paint(canvas, Offset(chip.left + pad, chip.top + d.spacing4 / 2));
  }

  @override
  void paint(Canvas canvas, Size size) {
    final c = theme.colors;
    final d = theme.dimensions;
    for (final b in boxes) {
      var r = vkRegionToRect(b.region, picture);
      if (b.selected && local != null && !drawing) r = local!;
      final color = b.reference
          ? c.trackLost
          : (b.dashed ? c.playerControlsContent : c.selection);
      // Design pages 17–18: a chosen target or the current mask is a solid
      // cyan box (handles only when editable); candidates stay white dashed.
      final p = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = d.maskBoxStroke;
      if (b.dashed || b.reference) {
        _dashed(canvas, r, p);
        _label(canvas, b.label, r, c.playerCanvas, c.playerControlsContent);
      } else {
        canvas.drawRect(r, p);
        _label(canvas, b.label, r, color, c.playerCanvas);
      }
      if (b.selected && !b.reference) {
        final handle = Paint()..color = c.selection;
        final inner = Paint()..color = c.playerControlsContent;
        for (final o in [
          r.topLeft,
          r.topRight,
          r.bottomLeft,
          r.bottomRight,
          r.topCenter,
          r.bottomCenter,
          r.centerLeft,
          r.centerRight,
        ]) {
          canvas
            ..drawCircle(o, d.maskBoxHandle / 2, handle)
            ..drawCircle(o, d.maskBoxHandle / 2 - d.borderWidth * 2, inner);
        }
      }
    }
    final l = local;
    if (drawing && l != null) {
      _dashed(
        canvas,
        l,
        Paint()
          ..color = c.selection
          ..style = PaintingStyle.stroke
          ..strokeWidth = d.maskBoxStroke,
      );
    }
  }

  @override
  bool shouldRepaint(_OverlayPainter old) =>
      old.fontFamily != fontFamily ||
      old.boxes != boxes ||
      old.picture != picture ||
      old.local != local ||
      old.drawing != drawing ||
      old.theme != theme;
}

Rect _semanticRect(Rect r, double min) => Rect.fromCenter(
  center: r.center,
  width: math.max(r.width, min),
  height: math.max(r.height, min),
);
