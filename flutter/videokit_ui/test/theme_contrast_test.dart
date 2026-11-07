import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// 14 §7.1: every registered foreground/background pair meets its minimum
/// in both modes (text 4.5:1 on surface/surfacevariant/background, non-text
/// 3:1). No "known exceptions".
void main() {
  test('contrast helpers follow WCAG', () {
    expect(
      VkContrast.ratio(VkContrast.black, VkContrast.white),
      closeTo(21, 0.01),
    );
    expect(VkContrast.bestOn(const Color(0xFFFFFF00)), VkContrast.black);
    expect(VkContrast.bestOn(const Color(0xFF1A237E)), VkContrast.white);
  });

  test('registry covers the 14 §7.1 groups', () {
    final fg = VkContrastPairs.all.map((p) => p.foreground).toSet();
    expect(
      fg,
      containsAll([
        VkTokenKeys.textTertiary,
        VkTokenKeys.onPrimary,
        VkTokenKeys.successContent,
        VkTokenKeys.playerControlsContent,
        VkTokenKeys.focusRing,
        VkTokenKeys.borderStrong,
        VkTokenKeys.trackLost,
      ]),
    );
    for (final exempt in [
      VkTokenKeys.border,
      VkTokenKeys.divider,
      VkTokenKeys.disabledContent,
    ]) {
      expect(fg.contains(exempt), isFalse, reason: '$exempt is exempt');
    }
  });

  for (final b in Brightness.values) {
    test('every registered pair passes (${b.name})', () {
      final c = const DefaultThemeSource().resolve(b, null).colors;
      final failures = [
        for (final p in VkContrastPairs.all)
          if (VkContrast.ratio(c[p.foreground], c[p.background]) < p.minimum)
            '$p: ${VkContrast.ratio(c[p.foreground], c[p.background]).toStringAsFixed(2)}',
      ];
      expect(failures, isEmpty);
    });
  }

  test('host primary overrides always meet 4.5:1 for on colours', () {
    for (final b in Brightness.values) {
      for (var hue = 0; hue < 360; hue += 30) {
        final p = HSVColor.fromAHSV(1, hue.toDouble(), 0.8, 0.8).toColor();
        final c = const DefaultThemeSource()
            .resolve(b, VideoKitThemeOverrides.primary(p))
            .colors;
        expect(
          VkContrast.ratio(c.onPrimary, c.primary),
          greaterThanOrEqualTo(4.5),
        );
        expect(
          VkContrast.ratio(c.onPrimaryContainer, c.primaryContainer),
          greaterThanOrEqualTo(4.5),
        );
      }
    }
  });
}
