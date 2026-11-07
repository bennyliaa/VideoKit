import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'tokens/vk_animations.dart';
import 'tokens/vk_colors.dart';
import 'tokens/vk_component_styles.dart';
import 'tokens/vk_dimensions.dart';
import 'tokens/vk_drawables.dart';
import 'tokens/vk_icons.dart';
import 'tokens/vk_token_keys.dart';
import 'tokens/vk_typography.dart';

/// Current token schema version (03 §5.5). New tokens added later must have
/// keys, types and light/dark defaults.
const int themeSchemaVersion = 1;

/// Why a host override was ignored.
enum VkOverrideIssue { unknownKey, wrongType, outOfRange, notOverridable }

/// Diagnostic for an ignored host override (14 §7.1).
@immutable
final class VkThemeDiagnostic {
  /// Creates a diagnostic.
  const VkThemeDiagnostic(this.key, this.issue);

  /// Override key as given by the host.
  final String key;

  /// Issue.
  final VkOverrideIssue issue;

  @override
  bool operator ==(Object other) =>
      other is VkThemeDiagnostic && other.key == key && other.issue == issue;

  @override
  int get hashCode => Object.hash(key, issue);

  @override
  String toString() => 'VkThemeDiagnostic($key, ${issue.name})';
}

/// Immutable theme snapshot used for one render (14 §7.1): the seven
/// SkinKit-aligned categories.
@immutable
final class VideoKitThemeData {
  /// Creates theme data.
  VideoKitThemeData({
    required this.brightness,
    required this.colors,
    required this.typography,
    required this.dimensions,
    required this.animations,
    required this.icons,
    required this.drawables,
    required this.components,
    this.schemaVersion = themeSchemaVersion,
    List<VkThemeDiagnostic> diagnostics = const [],
  }) : diagnostics = List.unmodifiable(diagnostics);

  /// Brightness.
  final Brightness brightness;

  /// Colours.
  final VkColors colors;

  /// Typography.
  final VkTypography typography;

  /// Dimensions.
  final VkDimensions dimensions;

  /// Animations.
  final VkAnimations animations;

  /// Icons.
  final VkIcons icons;

  /// Drawables.
  final VkDrawables drawables;

  /// Component styles.
  final VkComponentStyles components;

  /// Token schema version.
  final int schemaVersion;

  /// Host overrides that were ignored.
  final List<VkThemeDiagnostic> diagnostics;

  /// The seven theme extensions.
  List<ThemeExtension<dynamic>> get extensions => [
    colors,
    typography,
    dimensions,
    animations,
    icons,
    drawables,
    components,
  ];

  /// Value of any registered token by key (completeness checks, gallery).
  Object? valueOf(VkTokenKey key) => switch (key.type) {
    VkTokenType.color => colors.values[key.key],
    VkTokenType.typography => typography.values[key.key],
    VkTokenType.dimension => dimensions.values[key.key],
    VkTokenType.animation => animations.values[key.key],
    VkTokenType.icon => icons.resolve(key.key),
    VkTokenType.drawable => drawables[key],
    VkTokenType.component => components[key],
  };

  /// Injects the Vk* extensions into [base] and sets a matching
  /// [ColorScheme]; the host's other extensions are kept.
  ThemeData toMaterialTheme(ThemeData base) {
    final c = colors;
    final scheme = ColorScheme(
      brightness: brightness,
      primary: c.primary,
      onPrimary: c.onPrimary,
      primaryContainer: c.primaryContainer,
      onPrimaryContainer: c.onPrimaryContainer,
      secondary: c.selection,
      onSecondary: c.background,
      error: c.error,
      onError: c.errorContent,
      errorContainer: c.errorContainer,
      surface: c.surface,
      onSurface: c.textPrimary,
      onSurfaceVariant: c.textSecondary,
      surfaceContainerHighest: c.surfaceHigh,
      surfaceContainerHigh: c.surfaceHigh,
      surfaceContainer: c.surfaceVariant,
      outline: c.border,
      outlineVariant: c.divider,
      scrim: c.scrim,
    );
    final keep = [
      for (final e in base.extensions.values)
        if (!_isVk(e)) e,
    ];
    return base.copyWith(
      brightness: brightness,
      colorScheme: scheme,
      scaffoldBackgroundColor: c.background,
      dividerColor: c.divider,
      extensions: [...keep, ...extensions],
    );
  }

  static bool _isVk(Object e) =>
      e is VkColors ||
      e is VkTypography ||
      e is VkDimensions ||
      e is VkAnimations ||
      e is VkIcons ||
      e is VkDrawables ||
      e is VkComponentStyles;

  /// Returns a copy with the given fields replaced.
  VideoKitThemeData copyWith({
    Brightness? brightness,
    VkColors? colors,
    VkTypography? typography,
    VkDimensions? dimensions,
    VkAnimations? animations,
    VkIcons? icons,
    VkDrawables? drawables,
    VkComponentStyles? components,
    List<VkThemeDiagnostic>? diagnostics,
  }) => VideoKitThemeData(
    brightness: brightness ?? this.brightness,
    colors: colors ?? this.colors,
    typography: typography ?? this.typography,
    dimensions: dimensions ?? this.dimensions,
    animations: animations ?? this.animations,
    icons: icons ?? this.icons,
    drawables: drawables ?? this.drawables,
    components: components ?? this.components,
    schemaVersion: schemaVersion,
    diagnostics: diagnostics ?? this.diagnostics,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitThemeData &&
      other.brightness == brightness &&
      other.colors == colors &&
      other.typography == typography &&
      other.dimensions == dimensions &&
      other.animations == animations &&
      other.icons == icons &&
      other.drawables == drawables &&
      other.components == components &&
      other.schemaVersion == schemaVersion &&
      listEquals(other.diagnostics, diagnostics);

  @override
  int get hashCode => Object.hash(
    brightness,
    colors,
    typography,
    dimensions,
    animations,
    icons,
    drawables,
    components,
    schemaVersion,
    Object.hashAll(diagnostics),
  );
}

/// Host overrides by token key (14 §7.1, REQ-UX-06). Hosts may override
/// only `color.*` ([Color] or ARGB `int`) and `icon.*` ([IconData]) tokens;
/// text goes through `VideoKitStrings`. Other categories, wrong types,
/// out-of-range values and unknown keys are ignored and reported in
/// [VideoKitThemeData.diagnostics]. Legal `0`/transparent colours are valid.
@immutable
final class VideoKitThemeOverrides {
  /// Creates overrides.
  VideoKitThemeOverrides({Map<String, Object?> values = const {}})
    : values = Map.unmodifiable(values);

  /// Only the primary colour (derived colours are computed).
  factory VideoKitThemeOverrides.primary(Color primary) =>
      VideoKitThemeOverrides(values: {VkTokenKeys.primary.key: primary});

  /// Key → value.
  final Map<String, Object?> values;

  /// Whether nothing is overridden.
  bool get isEmpty => values.isEmpty;

  @override
  bool operator ==(Object other) =>
      other is VideoKitThemeOverrides && mapEquals(other.values, values);

  @override
  int get hashCode => Object.hashAllUnordered(
    values.entries.map((e) => Object.hash(e.key, e.value)),
  );
}
