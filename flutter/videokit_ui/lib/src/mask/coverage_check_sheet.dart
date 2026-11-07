import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_data.dart';
import '../theme/theme_scope.dart';
import 'coverage_strip.dart';

/// UI-07 `CoverageCheckSheet` (14 §5.7, design page 19): the uncovered
/// tracking ranges from `ExportPrecheck.uncoveredRanges`, each with jump
/// to correct / manual keyframe / full-frame mask, plus "返回修正" and the
/// explicit force export that marks the result as incompletely masked.
class CoverageCheckSheet extends StatelessWidget {
  /// Creates the sheet content.
  const CoverageCheckSheet({
    super.key,
    required this.ranges,
    required this.targetName,
    required this.onJump,
    required this.onManualKeyframe,
    required this.onFullFrame,
    required this.onBack,
    required this.onForceExport,
  });

  /// Uncovered ranges.
  final List<UncoveredRange> ranges;

  /// Display name of a mask ("目标 A").
  final String Function(String maskId) targetName;

  /// Jump to the range and correct the tracking.
  final ValueChanged<UncoveredRange> onJump;

  /// Cover the range with a manual keyframe.
  final ValueChanged<UncoveredRange> onManualKeyframe;

  /// Mask the whole picture for the range.
  final ValueChanged<UncoveredRange> onFullFrame;

  /// Back to editing.
  final VoidCallback onBack;

  /// Export anyway (`acceptUncoveredTracking`).
  final VoidCallback onForceExport;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Center(
          child: Container(
            padding: EdgeInsetsDirectional.all(d.spacing16),
            decoration: BoxDecoration(
              color: t.colors.errorContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(
              t.icons.warning,
              size: d.icon24 * 1.5,
              color: t.colors.error,
            ),
          ),
        ),
        SizedBox(height: d.spacing12),
        Semantics(
          header: true,
          child: Text(
            s.checkTitle(ranges.length),
            textAlign: TextAlign.center,
            style: t.typography.titleLarge.copyWith(
              color: t.colors.textPrimary,
            ),
          ),
        ),
        Text(
          s.text('checkSubtitle'),
          textAlign: TextAlign.center,
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
        SizedBox(height: d.spacing16),
        for (final r in ranges)
          Padding(
            padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
            child: Container(
              padding: EdgeInsetsDirectional.all(d.spacing12),
              decoration: BoxDecoration(
                color: t.colors.surfaceVariant,
                borderRadius: BorderRadius.circular(d.cornerMedium),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  MergeSemantics(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            ExcludeSemantics(
                              child: SizedBox(
                                width: d.spacing16,
                                height: d.spacing16,
                                child: CustomPaint(
                                  painter: _Swatch(r.state, t),
                                ),
                              ),
                            ),
                            SizedBox(width: d.spacing8),
                            Expanded(
                              child: Text(
                                s.checkRange(
                                  targetName(r.maskId),
                                  VkFormat.timecode(r.startUs),
                                  VkFormat.timecode(r.endUs),
                                ),
                                style: t.typography.label.copyWith(
                                  color: t.colors.textPrimary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        Text(
                          coverageStateLabel(s, r.state),
                          style: t.typography.caption.copyWith(
                            color: t.colors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: d.spacing8),
                  Wrap(
                    spacing: d.spacing8,
                    runSpacing: d.spacing8,
                    children: [
                      VkButton(
                        label: s.text('checkJump'),
                        onPressed: () => onJump(r),
                      ),
                      VkButton(
                        label: s.text('checkManual'),
                        variant: VkButtonVariant.secondary,
                        onPressed: () => onManualKeyframe(r),
                      ),
                      VkButton(
                        label: s.text('checkFullFrame'),
                        variant: VkButtonVariant.secondary,
                        onPressed: () => onFullFrame(r),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        VkButton(label: s.text('checkBack'), onPressed: onBack),
        SizedBox(height: d.spacing8),
        VkButton(
          label: s.text('checkForce'),
          variant: VkButtonVariant.text,
          onPressed: onForceExport,
        ),
      ],
    );
  }
}

class _Swatch extends CustomPainter {
  _Swatch(this.state, this.theme);

  final TrackingState state;
  final VideoKitThemeData theme;

  @override
  void paint(Canvas canvas, Size size) =>
      CoveragePainter.paintState(canvas, Offset.zero & size, state, theme);

  @override
  bool shouldRepaint(_Swatch old) => old.state != state || old.theme != theme;
}
