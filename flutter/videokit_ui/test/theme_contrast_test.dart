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

  // R1-13 / R1-06: component colours used on ordinary surfaces (light and
  // dark), resolved from the default theme and checked as pairs.
  for (final b in Brightness.values) {
    test('surface component pairs reach their minimum (${b.name})', () {
      final theme = const DefaultThemeSource().resolve(b, null);
      final c = theme.colors;
      final k = theme.components;
      final host = k.hostActionBarSurface;
      final pairs = <(String, Color, Color, double)>[
        (
          'host item',
          host.item.normal.content,
          host.item.normal.background,
          4.5,
        ),
        (
          'host selected',
          host.item.selected.content,
          host.item.selected.background,
          4.5,
        ),
        ('host label on surface', host.label.color!, c.surface, 4.5),
        ('host label on background', host.label.color!, c.background, 4.5),
        ('host item edge on surface', host.item.normal.border, c.surface, 3),
        ('host badge', host.badge.content, host.badge.background, 4.5),
        ('chip', k.chip.normal.content, k.chip.normal.background, 4.5),
        (
          'chip selected',
          k.chip.selected.content,
          k.chip.selected.background,
          4.5,
        ),
        ('slider track on surface', k.sliderSurface.track, c.surface, 3),
        // J1: outline and danger buttons on page and panel surfaces.
        for (final bg in [c.background, c.surface]) ...[
          ('outline text', k.buttonOutline.normal.content, bg, 4.5),
          ('outline edge', k.buttonOutline.normal.border, bg, 3),
          ('danger text', k.buttonDanger.normal.content, bg, 4.5),
          ('danger edge', k.buttonDanger.normal.border, bg, 3),
        ],
      ];
      final failures = [
        for (final (name, fg, bg, min) in pairs)
          if (VkContrast.ratio(fg, bg) < min)
            '$name: ${VkContrast.ratio(fg, bg).toStringAsFixed(2)} < $min',
      ];
      expect(failures, isEmpty);
    });
  }
}
