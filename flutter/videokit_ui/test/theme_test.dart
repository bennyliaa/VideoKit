import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_ui/videokit_ui.dart';

void main() {
  const source = DefaultThemeSource();
  final dark = source.resolve(Brightness.dark, null);
  final light = source.resolve(Brightness.light, null);

  group('14 §7.2 values', () {
    test('colours (design + derived)', () {
      final d = dark.colors;
      expect(d.background, const Color(0xFF0E1015));
      expect(d.surface, const Color(0xFF171A21));
      expect(d.surfaceVariant, const Color(0xFF1F232C));
      expect(d.surfaceHigh, const Color(0xFF2A2F3A));
      expect(d.border, const Color(0xFF343A46));
      expect(d.divider, const Color(0xFF262B35));
      expect(d.textPrimary, const Color(0xFFEEF0F4));
      expect(d.textSecondary, const Color(0xFFA3A9B5));
      expect(d.textTertiary, const Color(0xFF858C9B));
      expect(d.borderStrong, const Color(0xFF6E7582));
      expect(d.primary, const Color(0xFFFF7A45));
      expect(d.onPrimary, const Color(0xFF1A0E08));
      expect(d.primaryContainer, const Color(0xFF3A2219));
      expect(d.onPrimaryContainer, const Color(0xFFFFD3C0));
      expect(d.focusRing, const Color(0xFF4CC9F0));
      expect(d.scrim, const Color(0x99000000));
      expect(d.success, const Color(0xFF34D399));
      expect(d.successContent, const Color(0xFF062A1C));
      expect(d.successContainer, const Color(0xFF123A2C));
      expect(d.errorContainer, const Color(0xFF3D1818));
      expect(d.infoContent, const Color(0xFF05222C));
      expect(d.trackAmbiguous, const Color(0xFFA78BFA));
      expect(d.demo, const Color(0xFFEC4899));
      expect(d.playerCanvas, const Color(0xFF000000));
      expect(d.playerControlsContent, const Color(0xFFFFFFFF));

      final l = light.colors;
      expect(l.background, const Color(0xFFF4F5F7));
      expect(l.surface, const Color(0xFFFFFFFF));
      expect(l.divider, const Color(0xFFE6E8EC));
      expect(l.primary, const Color(0xFFC2410C));
      expect(l.success, const Color(0xFF047857));
      expect(l.error, const Color(0xFFC53030));
      expect(l.textTertiary, const Color(0xFF646B78));
      expect(l.borderStrong, const Color(0xFF7C828E));
      expect(l.onPrimary, const Color(0xFFFFFFFF));
      expect(l.primaryContainer, const Color(0xFFFFE8DC));
      expect(l.onPrimaryContainer, const Color(0xFF7A2E06));
      expect(l.focusRing, const Color(0xFF0E7FA8));
      expect(l.disabledContent, const Color(0xFF8A909B));
      expect(l.warning, const Color(0xFFA16207));
      expect(l.warningContainer, const Color(0xFFFDF1D8));
      expect(l.trackTracked, const Color(0xFF047857));
      expect(l.trackAmbiguous, const Color(0xFF7C5CD6));
      expect(l.trackLost, const Color(0xFFD64545));
      expect(l.demo, const Color(0xFFD63384));
      for (final c in [d, l]) {
        expect(c.selection, const Color(0xFF4CC9F0));
        expect(c.playerCanvas, const Color(0xFF000000));
      }
    });

    test('typography, dimensions, animations, drawables', () {
      final t = dark.typography;
      expect([t.display.fontSize, t.display.height], [28, 36 / 28]);
      expect([t.titleLarge.fontSize, t.titleLarge.height], [22, 30 / 22]);
      expect([t.title.fontSize, t.title.fontWeight], [20, FontWeight.w600]);
      expect([t.body.fontSize, t.bodySmall.fontSize], [14, 13]);
      expect(
        [t.label.fontSize, t.label.height, t.label.fontWeight],
        [12, 16 / 12, FontWeight.w500],
      );
      expect(t.caption.color, dark.colors.textSecondary);
      expect(
        t.timecode.fontFeatures,
        contains(const FontFeature.tabularFigures()),
      );
      expect(t.body.fontFamily, isNull, reason: 'platform font, none bundled');

      final d = dark.dimensions;
      expect(
        [
          d.spacing4,
          d.spacing8,
          d.spacing12,
          d.spacing16,
          d.spacing24,
          d.spacing32,
        ],
        [4, 8, 12, 16, 24, 32],
      );
      expect(
        [
          d.cornerSmall,
          d.cornerMedium,
          d.cornerLarge,
          d.cornerXLarge,
          d.cornerFull,
        ],
        [6, 10, 14, 20, 999],
      );
      expect([d.targetMin, d.icon16, d.icon20, d.icon24], [48, 16, 20, 24]);
      expect(d.controlBarHeight, 56);
      expect(
        [d.seekBarTrack, d.seekBarTrackActive, d.seekBarThumb],
        [4, 6, 14],
      );
      expect(
        [d.timelineClipRow, d.timelineMaskRow, d.timelineCoverageStrip],
        [56, 20, 8],
      );
      expect(
        [d.maskBoxStroke, d.maskBoxHandle, d.maskBoxHandleTarget],
        [2, 10, 24],
      );
      final shadow = d.modalShadow(dark.colors.shadowModal);
      expect([shadow.offset.dy, shadow.blurRadius], [8, 24]);

      final a = dark.animations;
      expect(
        [
          a.press,
          a.small,
          a.normal,
          a.page,
        ].map((x) => x.duration.inMilliseconds),
        [100, 160, 200, 280],
      );
      expect(a.normal.curve, Curves.easeOutCubic);
      final r = a.resolve(reduce: true);
      expect(r.reduced, isTrue);
      expect(
        [r.press, r.small, r.normal, r.page].every((x) => x.isDisabled),
        isTrue,
      );

      final g = dark.drawables.glassPlayer;
      expect([g.tint, g.opacity, g.blur], [VkContrast.black, 0.55, 0]);
      expect(g.fallbackSurface, dark.colors.scrim);
      expect(dark.icons.resolve('icon.play'), Icons.play_arrow_rounded);
      expect(dark.icons.resolve('nope'), dark.icons.resolve('unknown'));
      expect(vkIconsMatchRegistry(), isTrue);
    });

    test('component styles: every state, derived from tokens', () {
      final c = dark.components;
      final p = c.buttonPrimary;
      expect(p.normal.background, dark.colors.primary);
      expect(p.normal.content, dark.colors.onPrimary);
      expect(p.normal.minSize, 48);
      expect(p.pressed.background, isNot(p.normal.background));
      expect(p.hovered.background, isNot(p.pressed.background));
      expect(p.focused.border, dark.colors.focusRing);
      expect(p.focused.borderWidth, 2);
      expect(p.disabled.content, dark.colors.disabledContent);
      expect(p.selected.background, dark.colors.primaryContainer);
      expect(
        p.resolve({WidgetState.disabled, WidgetState.pressed}),
        p.disabled,
      );
      expect(p.resolve({WidgetState.pressed, WidgetState.focused}), p.pressed);
      expect(p.resolve({}), p.normal);
      for (final s in VkInteractionState.values) {
        expect(
          c.buttonSecondary.of(s).textStyle.color,
          c.buttonSecondary.of(s).content,
        );
      }
      expect(
        c.buttonText.normal.background.a,
        0,
        reason: 'transparent is a valid value',
      );
      expect(c.buttonIcon.normal.radius, 999);
      expect(c.chip.selected.border, dark.colors.primary);
      expect(c.badge.normal, c.badge.pressed);
      expect(c.seekBar.played, dark.colors.primary);
      expect(
        [
          c.seekBar.trackHeight,
          c.seekBar.trackHeightActive,
          c.seekBar.thumbSize,
        ],
        [4, 6, 14],
      );
      expect(
        c.seekBar.bubble.textStyle.fontFeatures,
        contains(const FontFeature.tabularFigures()),
      );
      expect(c.buttonPrimary.normal.padding, isA<EdgeInsetsDirectional>());
    });
  });

  group('host overrides by key (14 §7.1)', () {
    test('primary-only override derives on/container colours', () {
      for (final b in Brightness.values) {
        for (final p in const [
          Color(0xFF1565C0),
          Color(0xFFFFEB3B),
          Color(0xFF2E7D32),
          Color(0xFF6A1B9A),
        ]) {
          final t = source.resolve(b, VideoKitThemeOverrides.primary(p));
          final c = t.colors;
          expect(c.primary, p);
          expect(
            VkContrast.ratio(c.onPrimary, c.primary),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            c.primaryContainer,
            VkContrast.blend(
              p,
              c.surface,
              DefaultThemeSource.primaryContainerAmount,
            ),
          );
          expect(
            VkContrast.ratio(c.onPrimaryContainer, c.primaryContainer),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            t.components.buttonPrimary.normal.background,
            p,
            reason: 'component styles follow the primary',
          );
          final base = b == Brightness.dark ? dark.colors : light.colors;
          expect(c.trackLost, base.trackLost, reason: 'tracking colours fixed');
          expect(c.trackTracked, base.trackTracked);
          expect(t.diagnostics, isEmpty);
        }
      }
    });

    test('explicit low-contrast on colour is corrected, good one kept', () {
      final bad = source.resolve(
        Brightness.light,
        VideoKitThemeOverrides(
          values: const {
            'color.primary': Color(0xFFFFEB3B),
            'color.onprimary': Color(0xFFFFFFFF),
          },
        ),
      );
      expect(bad.colors.onPrimary, VkContrast.black);
      final good = source.resolve(
        Brightness.light,
        VideoKitThemeOverrides(
          values: const {
            'color.primary': Color(0xFF0D47A1),
            'color.onprimary': Color(0xFFFFFDE7),
          },
        ),
      );
      expect(good.colors.onPrimary, const Color(0xFFFFFDE7));
    });

    test('only color.* and icon.* are overridable; the rest is diagnosed', () {
      final t = source.resolve(
        Brightness.dark,
        VideoKitThemeOverrides(
          values: {
            'color.surface': 0xFF101010, // ARGB int
            'color.scrim': const Color(0x00000000), // transparent is valid
            'icon.play': Icons.play_circle,
            // not open to hosts (REQ-UX-06):
            'typography.title': const TextStyle(fontSize: 30),
            'dimension.spacing.s4': 0,
            'animation.page': 0,
            'drawable.glass.player': dark.drawables.glassPlayer,
            'component.badge.default': dark.components.chip,
            // invalid:
            'color.primary': 'orange',
            'icon.pause': 'pause',
            'color.unknown': const Color(0xFF000000),
            'color.border': 0x1FFFFFFFF,
          },
        ),
      );
      expect(t.colors.surface, const Color(0xFF101010));
      expect(t.colors.scrim, const Color(0x00000000));
      expect(t.icons.play, Icons.play_circle);
      expect(t.typography, dark.typography);
      expect(t.dimensions, dark.dimensions);
      expect(t.animations, dark.animations);
      expect(t.drawables.glassPlayer.tint, dark.drawables.glassPlayer.tint);
      expect(t.components.badge, dark.components.badge);
      expect(t.colors.primary, dark.colors.primary);
      expect(t.icons.pause, dark.icons.pause);
      const n = VkOverrideIssue.notOverridable;
      expect(t.diagnostics.toSet(), {
        const VkThemeDiagnostic('typography.title', n),
        const VkThemeDiagnostic('dimension.spacing.s4', n),
        const VkThemeDiagnostic('animation.page', n),
        const VkThemeDiagnostic('drawable.glass.player', n),
        const VkThemeDiagnostic('component.badge.default', n),
        const VkThemeDiagnostic('color.primary', VkOverrideIssue.wrongType),
        const VkThemeDiagnostic('icon.pause', VkOverrideIssue.wrongType),
        const VkThemeDiagnostic('color.unknown', VkOverrideIssue.unknownKey),
        const VkThemeDiagnostic('color.border', VkOverrideIssue.outOfRange),
      });
      expect(VideoKitThemeOverrides().isEmpty, isTrue);
    });
  });

  group('extensions and Material theme', () {
    test('value semantics and lerp', () {
      expect(dark, source.resolve(Brightness.dark, null));
      expect(dark.hashCode, source.resolve(Brightness.dark, null).hashCode);
      expect(dark, isNot(light));
      expect(dark.colors.lerp(light.colors, 0), dark.colors);
      expect(dark.colors.lerp(light.colors, 1), light.colors);
      expect(dark.typography.lerp(light.typography, 1), light.typography);
      expect(dark.dimensions.lerp(light.dimensions, 0.5), dark.dimensions);
      expect(
        dark.animations
            .lerp(dark.animations.resolve(reduce: true), 0.9)
            .reduced,
        isTrue,
      );
      expect(dark.components.lerp(light.components, 0.9), light.components);
      expect(
        dark.copyWith(brightness: Brightness.light).brightness,
        Brightness.light,
      );
      expect(dark.extensions, hasLength(7));
    });

    test('toMaterialTheme injects the seven extensions, keeps host ones', () {
      final t = dark.toMaterialTheme(ThemeData(extensions: const [_HostExt()]));
      expect(t.extension<VkColors>(), dark.colors);
      expect(t.extension<VkDimensions>(), dark.dimensions);
      expect(t.extension<VkComponentStyles>(), dark.components);
      expect(t.extension<VkDrawables>(), dark.drawables);
      expect(t.extension<_HostExt>(), isNotNull);
      expect(t.colorScheme.primary, dark.colors.primary);
      expect(t.colorScheme.outline, dark.colors.border);
      expect(t.scaffoldBackgroundColor, dark.colors.background);
    });
  });

  group('VideoKitThemeScope / VkTheme.of', () {
    Future<VideoKitThemeData> read(
      WidgetTester tester,
      Widget Function(Widget child) wrap, {
      bool disableAnimations = false,
    }) async {
      late VideoKitThemeData data;
      await tester.pumpWidget(
        MediaQuery(
          data: MediaQueryData(disableAnimations: disableAnimations),
          child: wrap(
            Builder(
              builder: (context) {
                data = VkTheme.of(context);
                return const SizedBox();
              },
            ),
          ),
        ),
      );
      return data;
    }

    testWidgets('fallbacks, modes, overrides, reduced motion', (tester) async {
      var d = await read(
        tester,
        (c) => Theme(data: ThemeData.dark(), child: c),
      );
      expect(d.colors, dark.colors);
      d = await read(tester, (c) => Theme(data: ThemeData.light(), child: c));
      expect(d.colors.primary, const Color(0xFFC2410C));
      d = await read(
        tester,
        (c) => Theme(
          data: ThemeData.light(),
          child: VideoKitThemeScope(mode: VideoKitThemeMode.dark, child: c),
        ),
      );
      expect(d.brightness, Brightness.dark);
      d = await read(
        tester,
        (c) => Theme(
          data: ThemeData.dark(),
          child: VideoKitThemeScope(
            overrides: VideoKitThemeOverrides.primary(const Color(0xFF1565C0)),
            child: c,
          ),
        ),
      );
      expect(d.colors.primary, const Color(0xFF1565C0));
      d = await read(
        tester,
        (c) => VideoKitThemeScope(child: c),
        disableAnimations: true,
      );
      expect(d.animations.reduced, isTrue);
      d = await read(
        tester,
        (c) => VideoKitThemeScope(reduceMotion: false, child: c),
        disableAnimations: true,
      );
      expect(d.animations.reduced, isFalse);
      d = await read(
        tester,
        (c) => Theme(data: light.toMaterialTheme(ThemeData.light()), child: c),
        disableAnimations: true,
      );
      expect(d.components, light.components);
      expect(d.animations.reduced, isTrue);
    });

    testWidgets('source changes rebuild the scope', (tester) async {
      final src = _SwitchableSource();
      await tester.pumpWidget(
        VideoKitThemeScope(
          source: src,
          mode: VideoKitThemeMode.dark,
          child: Builder(
            builder: (context) => Text(
              VkTheme.of(context).colors.primary.toARGB32().toRadixString(16),
              textDirection: TextDirection.ltr,
            ),
          ),
        ),
      );
      expect(find.text('ffff7a45'), findsOneWidget);
      src.flip();
      await tester.pump();
      expect(find.text('ff123456'), findsOneWidget);
    });
  });
}

class _HostExt extends ThemeExtension<_HostExt> {
  const _HostExt();
  @override
  _HostExt copyWith() => this;
  @override
  _HostExt lerp(covariant _HostExt? other, double t) => this;
}

class _SwitchableSource extends ChangeNotifier implements VideoKitThemeSource {
  bool _alt = false;
  void flip() {
    _alt = true;
    notifyListeners();
  }

  @override
  Listenable? get changes => this;

  @override
  int get themeSchemaVersion => 1;

  @override
  VideoKitThemeData resolve(Brightness b, VideoKitThemeOverrides? o) =>
      const DefaultThemeSource().resolve(
        b,
        _alt ? VideoKitThemeOverrides.primary(const Color(0xFF123456)) : o,
      );
}
