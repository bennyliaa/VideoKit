import 'package:flutter/material.dart';

import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';

/// Small count/status badge (`component.badge.default`). Shows at most
/// [maxChars] characters; longer text is cut and ends with "…" (14 §5.4).
class VkBadge extends StatelessWidget {
  /// Creates a badge.
  const VkBadge({super.key, required this.text, this.style});

  /// Maximum characters shown.
  static const int maxChars = 3;

  /// Text.
  final String text;

  /// Style override (defaults to the host action badge style).
  final VkBoxStyle? style;

  /// [text] shortened to [maxChars] characters (ellipsis from ARB).
  static String clip(VkStrings s, String text) {
    final runes = text.runes.toList();
    if (runes.length <= maxChars) return text;
    return s.badgeClipped(String.fromCharCodes(runes.take(maxChars - 1)));
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = style ?? t.components.hostActionBar.badge;
    return Container(
      constraints: BoxConstraints(minWidth: s.minSize, minHeight: s.minSize),
      padding: s.padding,
      decoration: s.decoration,
      child: Text(
        clip(VkStrings.of(context), text),
        style: s.textStyle,
        textAlign: TextAlign.center,
        maxLines: 1,
      ),
    );
  }
}

/// Permanent "演示模式 · 模拟数据" badge (03 §8.3). Never hidden with the
/// controls; shown whenever the session/project is demo data.
class DemoBadge extends StatelessWidget {
  /// Creates the badge.
  const DemoBadge({super.key});

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final text = VkStrings.of(context).demoBadge;
    return Semantics(
      label: text,
      container: true,
      child: ExcludeSemantics(
        child: Container(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4,
          ),
          decoration: BoxDecoration(
            color: t.colors.demo,
            borderRadius: BorderRadius.circular(d.cornerFull),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(t.icons.demo, size: d.icon16, color: t.colors.demoContent),
              SizedBox(width: d.spacing4),
              Flexible(
                child: Text(
                  text,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: t.typography.label.copyWith(
                    color: t.colors.demoContent,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
