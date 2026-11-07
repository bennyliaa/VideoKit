import 'package:flutter/material.dart';

import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'vk_badge.dart';
import 'vk_pressable.dart';

/// Button variants (`component.button.*`, design page 6).
enum VkButtonVariant { primary, secondary, text }

/// Text button using the `component.button.*` styles. Width follows the
/// label (no fixed widths; labels may be 30–50 % longer in other locales).
class VkButton extends StatelessWidget {
  /// Creates a button.
  const VkButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = VkButtonVariant.primary,
    this.icon,
    this.selected = false,
  });

  /// Label (from ARB).
  final String label;

  /// Callback; null disables.
  final VoidCallback? onPressed;

  /// Variant.
  final VkButtonVariant variant;

  /// Optional leading icon.
  final IconData? icon;

  /// Selected.
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final style = switch (variant) {
      VkButtonVariant.primary => t.components.buttonPrimary,
      VkButtonVariant.secondary => t.components.buttonSecondary,
      VkButtonVariant.text => t.components.buttonText,
    };
    return VkPressable(
      style: style,
      semanticLabel: label,
      selected: selected,
      onPressed: onPressed,
      builder: (context, s) => Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: t.dimensions.icon20, color: s.content),
            SizedBox(width: t.dimensions.spacing8),
          ],
          Flexible(child: Text(label, style: s.textStyle)),
        ],
      ),
    );
  }
}

/// Icon button (`component.button.icon` by default) with optional pending
/// ring and badge (host actions, 14 §5.4).
class VkIconButton extends StatelessWidget {
  /// Creates an icon button.
  const VkIconButton({
    super.key,
    required this.icon,
    required this.semanticLabel,
    required this.onPressed,
    this.style,
    this.selected = false,
    this.pending = false,
    this.badgeText,
    this.semanticValue,
    this.iconSize,
    this.focusNode,
  });

  /// Icon.
  final IconData icon;

  /// Screen-reader label.
  final String semanticLabel;

  /// Callback; null disables.
  final VoidCallback? onPressed;

  /// Style override (e.g. host action bar items); defaults to
  /// `component.button.icon`.
  final VkStateStyle<VkBoxStyle>? style;

  /// Selected.
  final bool selected;

  /// Shows a pending ring (merged repeat clicks, 04A I1).
  final bool pending;

  /// Badge text.
  final String? badgeText;

  /// Screen-reader value.
  final String? semanticValue;

  /// Icon size; defaults to `dimension.icon.s24`.
  final double? iconSize;

  /// Focus node.
  final FocusNode? focusNode;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final size = iconSize ?? t.dimensions.icon24;
    final pendingHint = pending
        ? VkStrings.of(context).text('statePending')
        : null;
    return VkPressable(
      style: style ?? t.components.buttonIcon,
      semanticLabel: semanticLabel,
      semanticValue: semanticValue,
      semanticHint: pendingHint,
      selected: selected,
      onPressed: onPressed,
      focusNode: focusNode,
      builder: (context, s) => Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.center,
        children: [
          Icon(icon, size: size, color: s.content),
          if (pending)
            PositionedDirectional(
              top: -t.dimensions.spacing4,
              end: -t.dimensions.spacing4,
              child: SizedBox.square(
                dimension: t.dimensions.icon16,
                child: CircularProgressIndicator(
                  strokeWidth: t.dimensions.focusRingWidth,
                  color: t.components.hostActionBar.pendingIndicator,
                ),
              ),
            ),
          if (badgeText != null && badgeText!.isNotEmpty)
            PositionedDirectional(
              top: -t.dimensions.spacing8,
              end: -t.dimensions.spacing8,
              child: VkBadge(text: badgeText!),
            ),
        ],
      ),
    );
  }
}
