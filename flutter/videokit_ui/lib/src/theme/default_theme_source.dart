import 'package:flutter/material.dart';

import 'contrast.dart';
import 'default_tokens.dart';
import 'theme_data.dart';
import 'theme_source.dart';
import 'tokens/vk_animations.dart';
import 'tokens/vk_colors.dart';
import 'tokens/vk_dimensions.dart';
import 'tokens/vk_icons.dart';
import 'tokens/vk_token_keys.dart';
import 'tokens/vk_typography.dart';

/// Built-in theme source: UI design V1.0 values (14 §7.2) for dark and
/// light, host overrides by key with validation, and derived-colour contrast
/// rules (14 §7.1).
class DefaultThemeSource implements VideoKitThemeSource {
  /// Creates the default source.
  const DefaultThemeSource();

  /// Share of primary blended over surface for a derived primary container.
  static const double primaryContainerAmount = 0.15;

  @override
  int get themeSchemaVersion => 1;

  @override
  Listenable? get changes => null;

  /// Default colours for [brightness].
  static VkColors defaultColors(Brightness brightness) => VkColors(
    brightness == Brightness.dark
        ? VkDefaultTokens.darkColors
        : VkDefaultTokens.lightColors,
  );

  /// "On" colour → its background, derived when the background is
  /// overridden without the on colour, and kept ≥ 4.5:1 when given.
  static final Map<VkTokenKey, VkTokenKey> _onPairs = {
    VkTokenKeys.onPrimary: VkTokenKeys.primary,
    VkTokenKeys.onPrimaryContainer: VkTokenKeys.primaryContainer,
    VkTokenKeys.successContent: VkTokenKeys.success,
    VkTokenKeys.warningContent: VkTokenKeys.warning,
    VkTokenKeys.errorContent: VkTokenKeys.error,
    VkTokenKeys.infoContent: VkTokenKeys.info,
    VkTokenKeys.demoContent: VkTokenKeys.demo,
  };

  /// Applies validated colour [overrides] (key string → colour) to [base]:
  /// explicit values win, except "on" colours below 4.5:1 against their
  /// background (replaced with black/white); overriding only `primary`
  /// derives `onprimary`, `primarycontainer` (15 % over surface) and
  /// `onprimarycontainer`. Tracking colours never follow the primary
  /// (design page 22).
  static VkColors applyColorOverrides(
    VkColors base,
    Map<String, Color> overrides,
  ) {
    if (overrides.isEmpty) return base;
    final v = {...base.values, ...overrides};
    if (overrides.containsKey(VkTokenKeys.primary.key) &&
        !overrides.containsKey(VkTokenKeys.primaryContainer.key)) {
      v[VkTokenKeys.primaryContainer.key] = VkContrast.blend(
        v[VkTokenKeys.primary.key]!,
        v[VkTokenKeys.surface.key]!,
        primaryContainerAmount,
      );
    }
    final derivedBackgrounds = {
      ...overrides.keys,
      if (overrides.containsKey(VkTokenKeys.primary.key))
        VkTokenKeys.primaryContainer.key,
    };
    for (final e in _onPairs.entries) {
      final on = e.key.key;
      final bg = e.value.key;
      final explicit = overrides[on];
      if (explicit != null) {
        v[on] = VkContrast.ensure(explicit, v[bg]!);
      } else if (derivedBackgrounds.contains(bg)) {
        v[on] = VkContrast.bestOn(v[bg]!);
      }
    }
    return VkColors(v);
  }

  /// Validates [raw] overrides; returns typed values per category and the
  /// diagnostics of ignored entries. Only `color.*` and `icon.*` are open to
  /// hosts (REQ-UX-06, design page 22, 14 §7.1); every other category is
  /// ignored with [VkOverrideIssue.notOverridable].
  static ({
    Map<String, Color> colors,
    Map<String, IconData> icons,
    List<VkThemeDiagnostic> diagnostics,
  })
  validate(Map<String, Object?> raw) {
    final colors = <String, Color>{};
    final icons = <String, IconData>{};
    final diagnostics = <VkThemeDiagnostic>[];
    void bad(String k, VkOverrideIssue i) =>
        diagnostics.add(VkThemeDiagnostic(k, i));

    for (final MapEntry(:key, :value) in raw.entries) {
      final token = VkTokenKeys.byKey(key);
      if (token == null) {
        bad(key, VkOverrideIssue.unknownKey);
        continue;
      }
      switch (token.type) {
        case VkTokenType.color:
          if (value is Color) {
            colors[key] = value;
          } else if (value is int) {
            if (value < 0 || value > 0xFFFFFFFF) {
              bad(key, VkOverrideIssue.outOfRange);
            } else {
              colors[key] = Color(value);
            }
          } else {
            bad(key, VkOverrideIssue.wrongType);
          }
        case VkTokenType.icon:
          value is IconData
              ? icons[key] = value
              : bad(key, VkOverrideIssue.wrongType);
        case VkTokenType.typography ||
            VkTokenType.dimension ||
            VkTokenType.animation ||
            VkTokenType.drawable ||
            VkTokenType.component:
          bad(key, VkOverrideIssue.notOverridable);
      }
    }
    return (colors: colors, icons: icons, diagnostics: diagnostics);
  }

  @override
  VideoKitThemeData resolve(
    Brightness brightness,
    VideoKitThemeOverrides? overrides,
  ) {
    final o = validate(overrides?.values ?? const {});
    final colors = applyColorOverrides(defaultColors(brightness), o.colors);
    final typography = VkTypography.standard(
      primary: colors.textPrimary,
      secondary: colors.textSecondary,
    );
    final dimensions = VkDimensions.standard();
    return VideoKitThemeData(
      brightness: brightness,
      colors: colors,
      typography: typography,
      dimensions: dimensions,
      animations: VkAnimations.standard(),
      icons: VkIcons(o.icons),
      drawables: VkDefaultTokens.drawables(colors),
      components: VkDefaultTokens.components(colors, typography, dimensions),
      diagnostics: o.diagnostics,
    );
  }
}
