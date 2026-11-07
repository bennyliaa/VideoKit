import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import 'demo_data.dart';

/// Synthetic demo frame (14 §11.1): seed-derived gradient blocks, a moving
/// shape, a timecode and a "DEMO" watermark. Decodes no media.
///
/// Colours here are demo-content pixels, not UI styling, so they live in
/// `videokit_fake` rather than in theme tokens.
class DemoPicture extends StatelessWidget {
  /// Creates a demo picture.
  const DemoPicture({
    super.key,
    required this.seed,
    required this.positionUs,
    this.durationUs,
    this.animated = false,
    this.label,
    this.semanticLabel,
  });

  /// Screen-reader label supplied by the UI from ARB (e.g. the demo badge
  /// text); null excludes the picture from semantics. The painted "DEMO"
  /// watermark is picture content, not UI text.
  final String? semanticLabel;

  /// Seed (per media).
  final int seed;

  /// Position (µs) drawn as timecode and used for motion.
  final int positionUs;

  /// Duration, if known.
  final int? durationUs;

  /// Loop-style motion for animated images.
  final bool animated;

  /// Optional label (e.g. last 4 chars of the session ID).
  final String? label;

  @override
  Widget build(BuildContext context) => Semantics(
    image: true,
    label: semanticLabel,
    excludeSemantics: semanticLabel == null,
    child: CustomPaint(
      painter: DemoPicturePainter(
        seed: seed,
        positionUs: positionUs,
        durationUs: durationUs,
        animated: animated,
        label: label,
      ),
      child: const SizedBox.expand(),
    ),
  );
}

/// Draws a [DemoPicture] for a session, following its state.
class DemoSessionPicture extends StatelessWidget {
  /// Creates the view.
  const DemoSessionPicture({
    super.key,
    required this.session,
    this.semanticLabel,
  });

  /// Session.
  final VideoKitSession session;

  /// Screen-reader label from ARB, see [DemoPicture.semanticLabel].
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) =>
      ValueListenableBuilder<VideoKitSessionState>(
        valueListenable: session.state,
        builder: (context, s, _) => DemoPicture(
          semanticLabel: semanticLabel,
          seed: stableHash(session.sessionId),
          positionUs: s.positionUs,
          durationUs: s.durationUs,
          animated: s.mediaKind == MediaKind.imageAnimated,
          label: session.sessionId.length > 4
              ? session.sessionId.substring(session.sessionId.length - 4)
              : session.sessionId,
        ),
      );
}

/// Painter behind [DemoPicture].
class DemoPicturePainter extends CustomPainter {
  /// Creates the painter.
  DemoPicturePainter({
    required this.seed,
    required this.positionUs,
    this.durationUs,
    this.animated = false,
    this.label,
  });

  /// Seed.
  final int seed;

  /// Position (µs).
  final int positionUs;

  /// Duration (µs).
  final int? durationUs;

  /// Animated.
  final bool animated;

  /// Label.
  final String? label;

  static Color _hsv(double h, double s, double v) =>
      HSVColor.fromAHSV(1, h % 360, s, v).toColor();

  @override
  void paint(Canvas canvas, Size size) {
    if (size.isEmpty) return;
    final rnd = DemoRandom(seed);
    final hue = rnd.nextDouble() * 360;
    final rect = Offset.zero & size;
    canvas.drawRect(
      rect,
      Paint()
        ..shader = LinearGradient(
          colors: [_hsv(hue, 0.55, 0.55), _hsv(hue + 60, 0.6, 0.35)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ).createShader(rect),
    );

    // Colour blocks.
    const cols = 4;
    final blockW = size.width / cols;
    for (var i = 0; i < cols; i++) {
      canvas.drawRect(
        Rect.fromLTWH(
          i * blockW,
          size.height * 0.82,
          blockW,
          size.height * 0.06,
        ),
        Paint()..color = _hsv(hue + i * 90, 0.7, 0.85),
      );
    }

    // Moving shape.
    final seconds = positionUs / 1e6;
    final period = animated ? 2.0 : 8.0;
    final phase = (seconds % period) / period * 2 * math.pi;
    final r = size.shortestSide * 0.08;
    final center = Offset(
      size.width / 2 + math.cos(phase) * size.width * 0.3,
      size.height * 0.45 + math.sin(phase) * size.height * 0.2,
    );
    canvas.drawCircle(center, r, Paint()..color = _hsv(hue + 180, 0.5, 1));

    // Timecode + label + watermark.
    final fontSize = math.max(10.0, size.shortestSide * 0.07);
    _text(
      canvas,
      size,
      _timecode(positionUs, durationUs),
      fontSize,
      Alignment.topLeft,
    );
    if (label != null) {
      _text(canvas, size, label!, fontSize * 0.7, Alignment.topRight);
    }
    _text(canvas, size, 'DEMO', fontSize * 1.8, Alignment.center, alpha: 0.35);
  }

  static String _timecode(int us, int? durationUs) {
    String f(int v) {
      final t = v ~/ 1000000;
      final m = (t ~/ 60).toString().padLeft(2, '0');
      final s = (t % 60).toString().padLeft(2, '0');
      final ms = ((v % 1000000) ~/ 10000).toString().padLeft(2, '0');
      return '$m:$s.$ms';
    }

    return durationUs == null ? f(us) : '${f(us)} / ${f(durationUs)}';
  }

  void _text(
    Canvas canvas,
    Size size,
    String text,
    double fontSize,
    Alignment alignment, {
    double alpha = 0.9,
  }) {
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: Color.fromRGBO(255, 255, 255, alpha),
          fontSize: fontSize,
          fontWeight: FontWeight.w700,
          fontFeatures: const [FontFeature.tabularFigures()],
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: size.width);
    final pad = size.shortestSide * 0.04;
    final free = Size(
      math.max(0, size.width - tp.width - 2 * pad),
      math.max(0, size.height - tp.height - 2 * pad),
    );
    final offset = alignment.alongSize(free) + Offset(pad, pad);
    tp.paint(canvas, offset);
    tp.dispose();
  }

  @override
  bool shouldRepaint(DemoPicturePainter oldDelegate) =>
      oldDelegate.seed != seed ||
      oldDelegate.positionUs != positionUs ||
      oldDelegate.durationUs != durationUs ||
      oldDelegate.animated != animated ||
      oldDelegate.label != label;
}
