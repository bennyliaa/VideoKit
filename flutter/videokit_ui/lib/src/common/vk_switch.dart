import 'package:flutter/material.dart';

import '../theme/theme_scope.dart';

/// On/off switch drawn from tokens (track `primary` / `border.strong`,
/// thumb `on.primary` / `text.secondary`); 48 dp touch target, toggled
/// semantics.
class VkSwitch extends StatelessWidget {
  /// Creates a switch.
  const VkSwitch({
    super.key,
    required this.value,
    required this.semanticLabel,
    required this.onChanged,
  });

  /// Current value.
  final bool value;

  /// Screen-reader label.
  final String semanticLabel;

  /// Change callback; null disables.
  final ValueChanged<bool>? onChanged;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final enabled = onChanged != null;
    final track = !enabled
        ? t.colors.disabledContainer
        : (value ? t.colors.primary : t.colors.borderStrong);
    final thumb = !enabled
        ? t.colors.disabledContent
        : (value ? t.colors.onPrimary : t.colors.textSecondary);
    final w = d.targetMin * 1.1;
    final h = d.spacing24 + d.spacing4;
    return Semantics(
      toggled: value,
      enabled: enabled,
      label: semanticLabel,
      onTap: enabled ? () => onChanged!(!value) : null,
      child: ExcludeSemantics(
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: enabled ? () => onChanged!(!value) : null,
          child: SizedBox(
            width: d.targetMin * 1.25,
            height: d.targetMin,
            child: Center(
              child: AnimatedContainer(
                duration: t.animations.small.duration,
                curve: t.animations.small.curve,
                width: w,
                height: h,
                padding: EdgeInsetsDirectional.all(d.spacing4),
                alignment: value
                    ? AlignmentDirectional.centerEnd
                    : AlignmentDirectional.centerStart,
                decoration: BoxDecoration(
                  color: track,
                  borderRadius: BorderRadius.circular(d.cornerFull),
                ),
                child: Container(
                  width: h - d.spacing8,
                  height: h - d.spacing8,
                  decoration: BoxDecoration(
                    color: thumb,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
