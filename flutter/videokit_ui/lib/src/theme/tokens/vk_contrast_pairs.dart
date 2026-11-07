import 'package:flutter/foundation.dart';

import 'vk_token_keys.dart';

/// A registered foreground/background pair with its minimum contrast.
@immutable
final class VkContrastPair {
  /// Creates a pair.
  const VkContrastPair(this.foreground, this.background, this.minimum);

  /// Foreground key.
  final VkTokenKey foreground;

  /// Background key.
  final VkTokenKey background;

  /// Minimum ratio.
  final double minimum;

  @override
  String toString() => '$foreground on $background ≥ $minimum';
}

/// Contrast registry (14 §7.1, no "known exceptions"):
///
/// * body text (text.primary/secondary/tertiary on surface, surfacevariant
///   and background; onprimary, onprimarycontainer, status.*.content,
///   demo.content, player.controls.content on their backgrounds) ≥ 4.5:1;
/// * non-text (focusring, border.strong, track colours on surface,
///   surfacevariant and background) ≥ 3:1;
/// * exempt: `color.disabled.*`, `color.border`, `color.divider`
///   (decorative; identifiable boundaries use `color.border.strong`).
abstract final class VkContrastPairs {
  static const double text = 4.5;
  static const double nonText = 3.0;

  static const List<VkTokenKey> _surfaces = [
    VkTokenKeys.surface,
    VkTokenKeys.surfaceVariant,
    VkTokenKeys.background,
  ];

  /// All registered pairs.
  static final List<VkContrastPair> all = List.unmodifiable([
    for (final fg in [
      VkTokenKeys.textPrimary,
      VkTokenKeys.textSecondary,
      VkTokenKeys.textTertiary,
    ])
      for (final bg in _surfaces) VkContrastPair(fg, bg, text),
    const VkContrastPair(VkTokenKeys.onPrimary, VkTokenKeys.primary, text),
    const VkContrastPair(
      VkTokenKeys.onPrimaryContainer,
      VkTokenKeys.primaryContainer,
      text,
    ),
    const VkContrastPair(VkTokenKeys.successContent, VkTokenKeys.success, text),
    const VkContrastPair(VkTokenKeys.warningContent, VkTokenKeys.warning, text),
    const VkContrastPair(VkTokenKeys.errorContent, VkTokenKeys.error, text),
    const VkContrastPair(VkTokenKeys.infoContent, VkTokenKeys.info, text),
    const VkContrastPair(VkTokenKeys.demoContent, VkTokenKeys.demo, text),
    const VkContrastPair(
      VkTokenKeys.playerControlsContent,
      VkTokenKeys.playerCanvas,
      text,
    ),
    for (final fg in [
      VkTokenKeys.focusRing,
      VkTokenKeys.borderStrong,
      VkTokenKeys.trackTracked,
      VkTokenKeys.trackLowConfidence,
      VkTokenKeys.trackAmbiguous,
      VkTokenKeys.trackLost,
    ])
      for (final bg in _surfaces) VkContrastPair(fg, bg, nonText),
  ]);
}
