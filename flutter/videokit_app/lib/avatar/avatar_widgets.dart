import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// Checkerboard behind a transparent avatar (design page 25).
class AvatarChecker extends StatelessWidget {
  /// Creates the background with [child] on top.
  const AvatarChecker({super.key, this.child});

  /// Content.
  final Widget? child;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    return CustomPaint(
      painter: _CheckerPainter(
        light: t.colors.surfaceVariant,
        dark: t.colors.surface,
        cell: t.dimensions.spacing8,
      ),
      child: child,
    );
  }
}

class _CheckerPainter extends CustomPainter {
  _CheckerPainter({required this.light, required this.dark, required this.cell});

  final Color light;
  final Color dark;
  final double cell;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = dark);
    final p = Paint()..color = light;
    for (var y = 0; y * cell < size.height; y++) {
      for (var x = 0; x * cell < size.width; x++) {
        if ((x + y).isEven) {
          canvas.drawRect(Rect.fromLTWH(x * cell, y * cell, cell, cell), p);
        }
      }
    }
  }

  @override
  bool shouldRepaint(_CheckerPainter o) =>
      o.light != light || o.dark != dark || o.cell != cell;
}

/// Dashed rectangle over a picture (the face found in the original).
class DashedBox extends StatelessWidget {
  /// Creates the box for [region] (normalized).
  const DashedBox({super.key, required this.region});

  /// Region inside the parent.
  final MaskRegion region;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    return CustomPaint(
      painter: _DashedPainter(
        region: region,
        color: t.colors.selection,
        width: t.dimensions.focusRingWidth,
        dash: t.dimensions.spacing4,
      ),
      child: const SizedBox.expand(),
    );
  }
}

class _DashedPainter extends CustomPainter {
  _DashedPainter({
    required this.region,
    required this.color,
    required this.width,
    required this.dash,
  });

  final MaskRegion region;
  final Color color;
  final double width;
  final double dash;

  @override
  void paint(Canvas canvas, Size size) {
    final r = Rect.fromLTWH(
      region.x * size.width,
      region.y * size.height,
      region.width * size.width,
      region.height * size.height,
    );
    final p = Paint()
      ..color = color
      ..strokeWidth = width
      ..style = PaintingStyle.stroke;
    void line(Offset a, Offset b) {
      final len = (b - a).distance;
      final dir = (b - a) / len;
      for (var d = 0.0; d < len; d += dash * 2) {
        canvas.drawLine(a + dir * d, a + dir * (d + dash).clamp(0, len), p);
      }
    }

    line(r.topLeft, r.topRight);
    line(r.topRight, r.bottomRight);
    line(r.bottomRight, r.bottomLeft);
    line(r.bottomLeft, r.topLeft);
  }

  @override
  bool shouldRepaint(_DashedPainter o) =>
      o.region != region || o.color != color || o.width != width;
}

/// An avatar tile: checkerboard (or plain surface for built-ins) with the
/// picture, selectable, with a spoken label.
class AvatarTile extends StatelessWidget {
  /// Creates a tile.
  const AvatarTile({
    super.key,
    required this.image,
    required this.label,
    required this.onTap,
    this.selected = false,
    this.checker = true,
  });

  /// Picture; null shows a neutral icon.
  final ImageProvider? image;

  /// Screen-reader label.
  final String label;

  /// Tap.
  final VoidCallback onTap;

  /// Highlighted (the avatar in use).
  final bool selected;

  /// Checkerboard background (transparent avatars).
  final bool checker;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final picture = image == null
        ? Icon(t.icons.resolve('face'), color: t.colors.textSecondary)
        : Image(image: image!, fit: BoxFit.contain, gaplessPlayback: true);
    return Semantics(
      button: true,
      selected: selected,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Container(
          constraints: BoxConstraints(
            minWidth: d.targetMin,
            minHeight: d.targetMin,
          ),
          decoration: BoxDecoration(
            color: t.colors.surface,
            borderRadius: BorderRadius.circular(d.cornerMedium),
            border: Border.all(
              color: selected ? t.colors.primary : t.colors.surface,
              width: d.focusRingWidth,
            ),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(d.cornerMedium),
            child: AspectRatio(
              aspectRatio: 1,
              child: checker
                  ? AvatarChecker(
                      child: Center(child: picture),
                    )
                  : Padding(
                      padding: EdgeInsetsDirectional.all(d.spacing8),
                      child: Center(child: picture),
                    ),
            ),
          ),
        ),
      ),
    );
  }
}
