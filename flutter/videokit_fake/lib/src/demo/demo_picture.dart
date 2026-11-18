import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import '../fake_session.dart';
import 'demo_data.dart';

/// A mask effect drawn on a [DemoPicture] (the Fake's stand-in for the
/// native preview composite, UI-AUDIT-A4 / design page 17).
@immutable
final class DemoMaskEffect {
  /// Creates an effect.
  const DemoMaskEffect({
    required this.region,
    required this.style,
    this.strength = 0.5,
  });

  /// Normalized region.
  final MaskRegion region;

  /// Mosaic or blur (IMAGE masks are drawn by the editor UI).
  final MaskStyle style;

  /// Strength 0–1 (cell size / blur radius).
  final double strength;

  @override
  bool operator ==(Object other) =>
      other is DemoMaskEffect &&
      other.region == region &&
      other.style == style &&
      other.strength == strength;

  @override
  int get hashCode => Object.hash(region, style, strength);
}

/// Mask effects of [state] at timeline time [atUs]: enabled MOSAIC / BLUR
/// masks with a region there (IMAGE masks: the editor draws the avatar).
List<DemoMaskEffect> demoMaskEffects(VideoKitEditState state, int atUs) => [
  for (final m in state.masks)
    if (m.enabled && m.style != MaskStyle.image)
      if (m.regionAt(atUs) case final r?)
        DemoMaskEffect(region: r, style: m.style, strength: m.strength),
];

/// Synthetic demo frame (14 §11.1, design page 24): colour bars, a moving
/// shape, a large centred timecode and a "FAKE · scenario · seed" line.
/// Decodes no media.
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
    this.scenario,
    this.effects = const [],
    this.semanticLabel,
  });

  /// Screen-reader label supplied by the UI from ARB (e.g. the demo badge
  /// text); null excludes the picture from semantics. The painted texts
  /// are picture content, not UI text.
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

  /// Scenario ID shown in the "FAKE · …" line.
  final String? scenario;

  /// Mosaic / blur regions (edit preview).
  final List<DemoMaskEffect> effects;

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
        scenario: scenario,
        effects: effects,
        fontFamily: DefaultTextStyle.of(context).style.fontFamily,
      ),
      child: const SizedBox.expand(),
    ),
  );
}

/// Draws a [DemoPicture] for a session, following its state; for a Fake
/// edit preview also the project's mosaic / blur masks.
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
  Widget build(BuildContext context) {
    final fake = session is FakeSession ? session as FakeSession : null;
    final edit = fake?.previewOf;
    return ListenableBuilder(
      listenable: Listenable.merge([session.state, ?edit]),
      builder: (context, _) {
        final s = session.state.value;
        return DemoPicture(
          semanticLabel: semanticLabel,
          seed: stableHash(session.sessionId),
          positionUs: s.positionUs,
          durationUs: s.durationUs,
          animated: s.mediaKind == MediaKind.imageAnimated,
          scenario: fake?.scenario.name,
          effects: edit == null
              ? const []
              : demoMaskEffects(edit.value, s.positionUs),
          label: session.sessionId.length > 4
              ? session.sessionId.substring(session.sessionId.length - 4)
              : session.sessionId,
        );
      },
    );
  }
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
    this.scenario,
    this.effects = const [],
    this.fontFamily,
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

  /// Scenario ID.
  final String? scenario;

  /// Mosaic / blur regions.
  final List<DemoMaskEffect> effects;

  /// Family of the surrounding text (null = platform default).
  final String? fontFamily;

  static Color _hsv(double h, double s, double v) =>
      HSVColor.fromAHSV(1, h % 360, s, v).toColor();

  /// SMPTE-like colour bars (75 %).
  static const List<Color> bars = [
    Color(0xFFBFBFBF),
    Color(0xFFBFBF00),
    Color(0xFF00BFBF),
    Color(0xFF00BF00),
    Color(0xFFBF00BF),
    Color(0xFFBF0000),
    Color(0xFF0000BF),
  ];

  /// Share of the height taken by the bars.
  static const double barsHeight = 0.66;

  double get _hue => DemoRandom(seed).nextDouble() * 360;

  Offset _shapeCenter(Size size) {
    final seconds = positionUs / 1e6;
    final period = animated ? 2.0 : 8.0;
    final phase = (seconds % period) / period * 2 * math.pi;
    return Offset(
      size.width / 2 + math.cos(phase) * size.width * 0.3,
      size.height * 0.45 + math.sin(phase) * size.height * 0.2,
    );
  }

  double _shapeRadius(Size size) => size.shortestSide * 0.08;

  /// Colour of the scene (without texts) at [p]: what a mosaic cell shows.
  Color sceneColorAt(Offset p, Size size) {
    if ((p - _shapeCenter(size)).distance <= _shapeRadius(size)) {
      return _hsv(_hue + 180, 0.5, 1);
    }
    if (p.dy < size.height * barsHeight) {
      final i = (p.dx / size.width * bars.length).floor().clamp(
        0,
        bars.length - 1,
      );
      return bars[i];
    }
    final t = (p.dx / size.width).clamp(0.0, 1.0);
    return Color.lerp(_hsv(_hue, 0.55, 0.35), _hsv(_hue + 60, 0.6, 0.2), t)!;
  }

  void _scene(Canvas canvas, Size size, {required bool texts}) {
    final barW = size.width / bars.length;
    for (final (i, c) in bars.indexed) {
      canvas.drawRect(
        Rect.fromLTWH(i * barW, 0, barW + 0.5, size.height * barsHeight),
        Paint()..color = c,
      );
    }
    final low = Rect.fromLTRB(0, size.height * barsHeight, size.width, size.height);
    canvas.drawRect(
      low,
      Paint()
        ..shader = LinearGradient(
          colors: [_hsv(_hue, 0.55, 0.35), _hsv(_hue + 60, 0.6, 0.2)],
        ).createShader(low),
    );
    canvas.drawCircle(
      _shapeCenter(size),
      _shapeRadius(size),
      Paint()..color = _hsv(_hue + 180, 0.5, 1),
    );
    if (!texts) return;
    final fontSize = math.max(10.0, size.shortestSide * 0.07);
    // Design page 24: large centred timecode on a dark plate.
    final tc = _layout(_timecode(positionUs, durationUs), fontSize * 1.6, size);
    final at = Offset(
      (size.width - tc.width) / 2,
      size.height * barsHeight / 2 - tc.height / 2,
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        (at & Size(tc.width, tc.height)).inflate(fontSize * 0.3),
        Radius.circular(fontSize * 0.3),
      ),
      Paint()..color = const Color(0xB3000000),
    );
    tc.paint(canvas, at);
    tc.dispose();
    final pad = size.shortestSide * 0.04;
    final fake = _layout(
      'FAKE · scenario=${scenario ?? 'normal'} · seed=$seed',
      fontSize * 0.6,
      size,
    );
    fake.paint(
      canvas,
      Offset(
        (size.width - fake.width) / 2,
        size.height - pad - fake.height,
      ),
    );
    fake.dispose();
    if (label != null) {
      final l = _layout(label!, fontSize * 0.6, size, alpha: 0.75);
      l.paint(canvas, Offset(size.width - pad - l.width, pad));
      l.dispose();
    }
  }

  @override
  void paint(Canvas canvas, Size size) {
    if (size.isEmpty) return;
    _scene(canvas, size, texts: true);
    for (final e in effects) {
      final r = Rect.fromLTWH(
        e.region.x * size.width,
        e.region.y * size.height,
        e.region.width * size.width,
        e.region.height * size.height,
      ).intersect(Offset.zero & size);
      if (r.isEmpty) continue;
      final k = e.strength.clamp(0.0, 1.0);
      canvas
        ..save()
        ..clipRect(r);
      if (e.style == MaskStyle.blur) {
        final sigma = size.shortestSide * (0.01 + 0.04 * k);
        canvas.saveLayer(
          r,
          Paint()..imageFilter = ui.ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
        );
        // Texts are blurred away; the scene shapes stay recognisable.
        _scene(canvas, size, texts: false);
        canvas.restore();
      } else {
        // Mosaic: square cells in the scene colour at each cell centre; the
        // texts beneath are covered.
        final cell = math.max(2.0, size.shortestSide * (0.02 + 0.08 * k));
        final x0 = (r.left / cell).floor() * cell;
        final y0 = (r.top / cell).floor() * cell;
        for (var y = y0; y < r.bottom; y += cell) {
          for (var x = x0; x < r.right; x += cell) {
            canvas.drawRect(
              Rect.fromLTWH(x, y, cell, cell),
              Paint()
                ..color = sceneColorAt(
                  Offset(x + cell / 2, y + cell / 2),
                  size,
                ),
            );
          }
        }
      }
      canvas.restore();
    }
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

  TextPainter _layout(
    String text,
    double fontSize,
    Size size, {
    double alpha = 0.92,
  }) => TextPainter(
    text: TextSpan(
      text: text,
      style: TextStyle(
        color: Color.fromRGBO(255, 255, 255, alpha),
        fontSize: fontSize,
        fontWeight: FontWeight.w700,
        fontFamily: fontFamily,
        fontFeatures: const [FontFeature.tabularFigures()],
      ),
    ),
    textDirection: TextDirection.ltr,
    maxLines: 1,
    ellipsis: '…',
  )..layout(maxWidth: size.width);

  @override
  bool shouldRepaint(DemoPicturePainter oldDelegate) =>
      oldDelegate.fontFamily != fontFamily ||
      oldDelegate.seed != seed ||
      oldDelegate.positionUs != positionUs ||
      oldDelegate.durationUs != durationUs ||
      oldDelegate.animated != animated ||
      oldDelegate.label != label ||
      oldDelegate.scenario != scenario ||
      !_sameEffects(oldDelegate.effects, effects);

  static bool _sameEffects(List<DemoMaskEffect> a, List<DemoMaskEffect> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
}
