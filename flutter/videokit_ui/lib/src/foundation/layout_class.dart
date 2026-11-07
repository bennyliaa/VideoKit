import 'package:flutter/widgets.dart';

/// Layout class by the component's own width (14 §4.6, 03 §7.1):
/// compact < 600, medium 600–839, expanded ≥ 840 logical pixels.
enum VkLayoutClass {
  compact,
  medium,
  expanded;

  /// Lower bound of [medium].
  static const double mediumMinWidth = 600;

  /// Lower bound of [expanded].
  static const double expandedMinWidth = 840;

  /// Text scale above which secondary controls move to the overflow menu.
  static const double collapseTextScale = 1.3;

  /// Class for [width] (unbounded counts as expanded).
  static VkLayoutClass fromWidth(double width) {
    if (width >= expandedMinWidth) return expanded;
    if (width >= mediumMinWidth) return medium;
    return compact;
  }

  /// Class for the component's [constraints] (not the screen width).
  static VkLayoutClass of(BoxConstraints constraints) =>
      fromWidth(constraints.maxWidth);

  /// Whether text scaling demands moving secondary buttons to overflow.
  static bool collapseSecondary(TextScaler scaler) =>
      scaler.scale(1) > collapseTextScale;

  /// Largest icon scale (J9: icons follow the text scale up to 1.5×).
  static const double maxIconScale = 1.5;

  /// Icon and button scale for [context]'s text scale, 1–[maxIconScale]
  /// (design page 23: at 200 % buttons grow with the text).
  static double iconScale(BuildContext context) =>
      MediaQuery.textScalerOf(context).scale(1).clamp(1.0, maxIconScale);
}

/// [LayoutBuilder] that passes the [VkLayoutClass] of its own constraints.
class VkLayoutBuilder extends StatelessWidget {
  /// Creates the builder.
  const VkLayoutBuilder({super.key, required this.builder});

  /// Builder.
  final Widget Function(
    BuildContext context,
    VkLayoutClass layoutClass,
    BoxConstraints constraints,
  )
  builder;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) =>
        builder(context, VkLayoutClass.of(constraints), constraints),
  );
}
