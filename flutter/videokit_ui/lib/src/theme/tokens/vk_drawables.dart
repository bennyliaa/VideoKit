import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Glass drawable (`drawable.glass.player`, 14 §7.2): local glass behind
/// player controls. V1.0 uses a gradient, no live blur.
@immutable
final class VkGlass {
  /// Creates a glass definition.
  const VkGlass({
    required this.tint,
    required this.opacity,
    required this.fallbackSurface,
    this.blur = 0,
    this.border,
  }) : assert(opacity >= 0 && opacity <= 1),
       assert(blur >= 0);

  /// Tint colour.
  final Color tint;

  /// Tint opacity 0–1.
  final double opacity;

  /// Blur sigma (0 = disabled in V1.0).
  final double blur;

  /// Optional border.
  final Color? border;

  /// Surface used when glass cannot be rendered.
  final Color fallbackSurface;

  /// Effective tint colour.
  Color get color => tint.withValues(alpha: opacity);

  /// Gradient fading the glass out towards the picture (top or bottom bar).
  LinearGradient gradient({required bool fromTop}) => LinearGradient(
    begin: fromTop ? Alignment.topCenter : Alignment.bottomCenter,
    end: fromTop ? Alignment.bottomCenter : Alignment.topCenter,
    colors: [color, tint.withValues(alpha: 0)],
  );

  @override
  bool operator ==(Object other) =>
      other is VkGlass &&
      other.tint == tint &&
      other.opacity == opacity &&
      other.blur == blur &&
      other.border == border &&
      other.fallbackSurface == fallbackSurface;

  @override
  int get hashCode => Object.hash(tint, opacity, blur, border, fallbackSurface);
}

/// Drawable tokens (`drawable.*`).
@immutable
class VkDrawables extends ThemeExtension<VkDrawables> {
  /// Creates drawables.
  const VkDrawables({required this.glassPlayer});

  /// `drawable.glass.player`.
  final VkGlass glassPlayer;

  /// Value of [key], or null when not a drawable key.
  Object? operator [](VkTokenKey key) =>
      key == VkTokenKeys.glassPlayer ? glassPlayer : null;

  @override
  VkDrawables copyWith({VkGlass? glassPlayer}) =>
      VkDrawables(glassPlayer: glassPlayer ?? this.glassPlayer);

  @override
  VkDrawables lerp(covariant VkDrawables? other, double t) =>
      t < 0.5 || other == null ? this : other;

  @override
  bool operator ==(Object other) =>
      other is VkDrawables && other.glassPlayer == glassPlayer;

  @override
  int get hashCode => glassPlayer.hashCode;
}
