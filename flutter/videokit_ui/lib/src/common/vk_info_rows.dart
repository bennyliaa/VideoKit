import 'package:flutter/material.dart';

import '../theme/theme_scope.dart';

/// Label/value rows of the info panels (image info, player "参数"): label
/// in secondary text, value in primary text, dividers between rows; each
/// row is read as one item by screen readers; long values wrap below the
/// label at large text scales.
class VkInfoRows extends StatelessWidget {
  /// Creates the rows.
  const VkInfoRows({super.key, required this.rows});

  /// (label, value) pairs in display order.
  final List<(String, String)> rows;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final (i, (label, value)) in rows.indexed)
          Container(
            padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing12),
            decoration: BoxDecoration(
              border: i == rows.length - 1
                  ? null
                  : Border(
                      bottom: BorderSide(
                        color: t.colors.divider,
                        width: d.borderWidth,
                      ),
                    ),
            ),
            child: MergeSemantics(
              child: Wrap(
                spacing: d.spacing16,
                runSpacing: d.spacing4,
                children: [
                  ConstrainedBox(
                    constraints: BoxConstraints(minWidth: d.targetMin * 2),
                    child: Text(
                      label,
                      style: t.typography.body.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  ),
                  Text(
                    value,
                    style: t.typography.body.copyWith(
                      color: t.colors.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
