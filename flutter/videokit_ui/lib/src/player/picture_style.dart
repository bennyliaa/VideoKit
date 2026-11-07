import 'package:flutter/widgets.dart';

import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';

/// Icon button style for controls drawn over the picture (UI-01/03/05,
/// package internal): `component.button.icon` with the player controls
/// content colour.
VkStateStyle<VkBoxStyle> vkOnPictureIconStyle(BuildContext context) {
  final t = VkTheme.of(context);
  final base = t.components.buttonIcon;
  final white = t.colors.playerControlsContent;
  return VkStateStyle<VkBoxStyle>(
    normal: base.normal.copyWith(content: white),
    pressed: base.pressed.copyWith(
      content: white,
      background: white.withValues(alpha: 0.16),
    ),
    focused: base.focused.copyWith(content: white),
    disabled: base.disabled.copyWith(content: white.withValues(alpha: 0.38)),
    selected: base.selected.copyWith(
      content: t.colors.primary,
      background: white.withValues(alpha: 0.12),
    ),
    hovered: base.hovered.copyWith(
      content: white,
      background: white.withValues(alpha: 0.08),
    ),
  );
}
