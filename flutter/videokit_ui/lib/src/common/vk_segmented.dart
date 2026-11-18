import 'package:flutter/material.dart';

import '../foundation/layout_class.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'vk_pressable.dart';

/// One segment of a [VkSegmented].
@immutable
final class VkSegment<T> {
  /// Creates a segment.
  const VkSegment({
    required this.value,
    required this.label,
    this.enabled = true,
  });

  /// Value.
  final T value;

  /// Label (from ARB).
  final String label;

  /// Whether it can be chosen.
  final bool enabled;
}

/// Neutral segmented control (design pages 8, 11 and 17): a recessed
/// `surface.variant` track; the chosen segment is raised in `surface.high`
/// with primary text, the others are plain secondary text. Segments share
/// the width; each is at least one touch target high.
class VkSegmented<T> extends StatelessWidget {
  /// Creates the control.
  const VkSegmented({
    super.key,
    required this.segments,
    required this.selected,
    required this.onChanged,
    this.semanticLabel,
  });

  /// Segments in order.
  final List<VkSegment<T>> segments;

  /// Chosen value.
  final T selected;

  /// Change callback; null disables all segments.
  final ValueChanged<T>? onChanged;

  /// Group label for screen readers.
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final c = t.colors;
    final base = t.components.chip.normal.copyWith(
      background: c.surfaceVariant.withValues(alpha: 0),
      content: c.textSecondary,
      radius: d.cornerSmall,
      textStyle: t.typography.body,
    );
    final chosen = base.copyWith(
      background: c.surfaceHigh,
      content: c.textPrimary,
      textStyle: t.typography.body.copyWith(fontWeight: FontWeight.w600),
    );
    VkBoxStyle over(VkBoxStyle s, double a) => s.copyWith(
      background: Color.alphaBlend(
        s.content.withValues(alpha: a),
        s.background.a == 0 ? c.surfaceVariant : s.background,
      ),
    );
    final style = VkStateStyle<VkBoxStyle>(
      normal: base,
      pressed: over(base, 0.12),
      hovered: over(base, 0.08),
      focused: base.copyWith(
        border: c.focusRing,
        borderWidth: d.focusRingWidth,
      ),
      disabled: base.copyWith(content: c.disabledContent),
      selected: chosen,
    );
    return Semantics(
      container: true,
      label: semanticLabel,
      child: Container(
        padding: EdgeInsetsDirectional.all(d.spacing4),
        decoration: BoxDecoration(
          color: c.surfaceVariant,
          borderRadius: BorderRadius.circular(d.cornerMedium),
        ),
        child: Row(
          children: [
            for (final s in segments)
              Expanded(
                child: VkPressable(
                  style: style,
                  semanticLabel: s.label,
                  selected: s.value == selected,
                  onPressed: onChanged == null || !s.enabled
                      ? null
                      : () => onChanged!(s.value),
                  // UI-AUDIT-A4 (design page 8): one line ("跟随系统"); a
                  // label slightly too wide is scaled down instead of
                  // wrapping. Large text (collapse class) may wrap to two
                  // lines so it is never shrunk below the user's size.
                  builder: (context, st) => Center(
                    child: VkLayoutClass.collapseSecondary(
                          MediaQuery.textScalerOf(context),
                        )
                        ? Text(
                            s.label,
                            textAlign: TextAlign.center,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: st.textStyle,
                          )
                        : FittedBox(
                            fit: BoxFit.scaleDown,
                            child: Text(
                              s.label,
                              textAlign: TextAlign.center,
                              maxLines: 1,
                              softWrap: false,
                              style: st.textStyle,
                            ),
                          ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
