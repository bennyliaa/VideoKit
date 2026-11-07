import 'package:flutter/material.dart';

import 'default_theme_source.dart';
import 'theme_data.dart';
import 'theme_source.dart';
import 'tokens/vk_colors.dart';
import 'tokens/vk_animations.dart';
import 'tokens/vk_component_styles.dart';
import 'tokens/vk_dimensions.dart';
import 'tokens/vk_drawables.dart';
import 'tokens/vk_icons.dart';
import 'tokens/vk_typography.dart';

/// Which brightness the VideoKit theme uses (03 §5.1).
enum VideoKitThemeMode {
  /// Follow the host's `Theme.of(context).brightness`.
  followHost,

  /// Follow the platform (`MediaQuery.platformBrightnessOf`).
  system,

  /// Always light.
  light,

  /// Always dark.
  dark,
}

/// Provides the VideoKit theme to a subtree (14 §7.1). Hosts may place it at
/// any level; without it components fall back to [DefaultThemeSource].
class VideoKitThemeScope extends StatelessWidget {
  /// Creates a scope.
  const VideoKitThemeScope({
    super.key,
    this.source = const DefaultThemeSource(),
    this.overrides,
    this.mode = VideoKitThemeMode.followHost,
    this.reduceMotion,
    required this.child,
  });

  /// Theme source.
  final VideoKitThemeSource source;

  /// Host overrides.
  final VideoKitThemeOverrides? overrides;

  /// Brightness mode.
  final VideoKitThemeMode mode;

  /// Explicit reduced-motion; null follows `MediaQuery.disableAnimations`.
  final bool? reduceMotion;

  /// Subtree.
  final Widget child;

  Brightness _brightness(BuildContext context) => switch (mode) {
    VideoKitThemeMode.light => Brightness.light,
    VideoKitThemeMode.dark => Brightness.dark,
    VideoKitThemeMode.system => MediaQuery.platformBrightnessOf(context),
    VideoKitThemeMode.followHost => Theme.of(context).brightness,
  };

  Widget _build(BuildContext context) {
    final resolved = source.resolve(_brightness(context), overrides);
    final reduce =
        reduceMotion ?? MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    final data = resolved.copyWith(
      animations: resolved.animations.resolve(reduce: reduce),
    );
    return Theme(
      data: data.toMaterialTheme(Theme.of(context)),
      child: _VkThemeMarker(data: data, child: child),
    );
  }

  @override
  Widget build(BuildContext context) {
    final changes = source.changes;
    if (changes == null) return _build(context);
    return ListenableBuilder(
      listenable: changes,
      builder: (context, _) => _build(context),
    );
  }
}

class _VkThemeMarker extends InheritedWidget {
  const _VkThemeMarker({required this.data, required super.child});

  final VideoKitThemeData data;

  @override
  bool updateShouldNotify(_VkThemeMarker oldWidget) => oldWidget.data != data;
}

/// Reads the VideoKit theme (14 §7.1 `VkTheme.of(context)`).
abstract final class VkTheme {
  /// Theme for [context]: the nearest [VideoKitThemeScope]; otherwise Vk*
  /// extensions found on `Theme.of(context)`; otherwise
  /// [DefaultThemeSource] for the ambient brightness. Motion honours
  /// `MediaQuery.disableAnimations` in the fallback paths.
  static VideoKitThemeData of(BuildContext context) {
    final marker = context.dependOnInheritedWidgetOfExactType<_VkThemeMarker>();
    if (marker != null) return marker.data;
    final theme = Theme.of(context);
    final fallback = const DefaultThemeSource().resolve(theme.brightness, null);
    final reduce = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    final animations = theme.extension<VkAnimations>() ?? fallback.animations;
    return VideoKitThemeData(
      brightness: theme.brightness,
      colors: theme.extension<VkColors>() ?? fallback.colors,
      typography: theme.extension<VkTypography>() ?? fallback.typography,
      dimensions: theme.extension<VkDimensions>() ?? fallback.dimensions,
      animations: animations.resolve(reduce: reduce),
      icons: theme.extension<VkIcons>() ?? fallback.icons,
      drawables: theme.extension<VkDrawables>() ?? fallback.drawables,
      components: theme.extension<VkComponentStyles>() ?? fallback.components,
    );
  }
}

/// Shorthand `context.vkTheme`.
extension VkThemeContext on BuildContext {
  /// [VkTheme.of] for this context.
  VideoKitThemeData get vkTheme => VkTheme.of(this);
}
