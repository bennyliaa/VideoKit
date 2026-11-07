import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import 'state_mapping.dart';

/// UI-09 unified state view (14 §5.9, design page 12): loading, buffering,
/// ended, errors, released and locked — every state explains why and offers
/// the next step. Actions go to [onStateAction]; states without actions show
/// only the explanation.
class VideoKitStateView extends StatelessWidget {
  /// Creates a state view for [model].
  const VideoKitStateView({
    super.key,
    required this.model,
    this.onStateAction,
    this.compact = false,
  });

  /// Builds the view directly from session state; empty when nothing needs
  /// showing.
  static Widget forSession({
    Key? key,
    required VideoKitSessionState state,
    ValueChanged<StateAction>? onStateAction,
    bool compact = false,
  }) {
    final model = mapSessionState(
      phase: state.phase,
      error: state.error,
      mediaKind: state.mediaKind,
      hiddenForLock: state.hiddenForLock,
    );
    if (model == null) return SizedBox.shrink(key: key);
    return VideoKitStateView(
      key: key,
      model: model,
      onStateAction: onStateAction,
      compact: compact,
    );
  }

  /// Model.
  final StateViewModel model;

  /// Action handler.
  final ValueChanged<StateAction>? onStateAction;

  /// One-line variant for small slots (multi-view, 14 §5.5).
  final bool compact;

  /// Title text for [model].
  static String title(VkStrings s, StateViewModel model) =>
      model.titleText ??
      switch (model.kind) {
        StateViewKind.loading => s.text('stateLoadingTitle'),
        StateViewKind.buffering => s.text('stateBuffering'),
        StateViewKind.ended => s.text('stateEndedTitle'),
        StateViewKind.released => s.text('stateReleasedTitle'),
        StateViewKind.locked => s.text('stateLockedTitle'),
        StateViewKind.error => s.error(model.error!.code),
      };

  /// Detail text for [model], if any.
  static String? detail(VkStrings s, StateViewModel model) =>
      model.detailText ??
      switch (model.detail) {
        null => null,
        StateDetail.loading => s.text('stateLoadingDetail'),
        StateDetail.connection => s.text('stateDetailConnection'),
        StateDetail.permission => s.text('stateDetailPermission'),
        StateDetail.unsupported => s.text('stateDetailUnsupported'),
        StateDetail.corrupt => s.text('stateDetailCorrupt'),
        StateDetail.resources => s.text('stateDetailResources'),
        StateDetail.trackingLost => s.text('stateDetailTrackingLost'),
        StateDetail.space => s.text('stateDetailSpace'),
        StateDetail.generic => s.text('stateDetailGeneric'),
      };

  /// Label of [action].
  static String actionLabel(VkStrings s, StateAction action) =>
      action == StateAction.replay
      ? s.text('actionReplay')
      : s.action(action.suggested!)!;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    // Small boxes (thumbnails, split views) fall back to the compact row.
    builder: (context, c) => _build(
      context,
      compact:
          compact || c.maxHeight < VkTheme.of(context).dimensions.targetMin * 3,
    ),
  );

  Widget _build(BuildContext context, {required bool compact}) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final onCanvas = t.colors.playerControlsContent;
    final spinning =
        model.kind == StateViewKind.loading ||
        model.kind == StateViewKind.buffering;
    final icon = spinning
        ? SizedBox.square(
            dimension: compact ? d.icon24 : d.targetMin,
            child: CircularProgressIndicator(
              strokeWidth: t.components.progress.height,
              color: t.components.progress.indicator,
              backgroundColor: t.components.progress.track,
            ),
          )
        : Icon(
            t.icons.resolve(model.iconName),
            size: compact ? d.icon24 : d.targetMin,
            color: model.kind == StateViewKind.error
                ? t.colors.error
                : onCanvas,
          );
    final titleText = title(s, model);
    final detailText = detail(s, model);
    final content = compact
        ? Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              icon,
              SizedBox(width: d.spacing8),
              Flexible(
                child: Text(
                  titleText,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: t.typography.bodySmall.copyWith(color: onCanvas),
                ),
              ),
              for (final a in model.actions.take(1))
                VkIconButton(
                  icon: t.icons.resolve('retry'),
                  semanticLabel: actionLabel(s, a),
                  onPressed: onStateAction == null
                      ? null
                      : () => onStateAction!(a),
                ),
            ],
          )
        : Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              icon,
              SizedBox(height: d.spacing12),
              Text(
                titleText,
                textAlign: TextAlign.center,
                style: t.typography.body.copyWith(color: onCanvas),
              ),
              if (detailText != null) ...[
                SizedBox(height: d.spacing4),
                Text(
                  detailText,
                  textAlign: TextAlign.center,
                  style: t.typography.bodySmall.copyWith(
                    color: t.colors.playerControlsContent.withValues(
                      alpha: 0.72,
                    ),
                  ),
                ),
              ],
              if (model.actions.isNotEmpty) ...[
                SizedBox(height: d.spacing16),
                Wrap(
                  alignment: WrapAlignment.center,
                  spacing: d.spacing8,
                  runSpacing: d.spacing8,
                  children: [
                    for (final (i, a) in model.actions.indexed)
                      VkButton(
                        label: actionLabel(s, a),
                        variant: i == 0
                            ? VkButtonVariant.primary
                            : VkButtonVariant.secondary,
                        onPressed: onStateAction == null
                            ? null
                            : () => onStateAction!(a),
                      ),
                  ],
                ),
              ],
            ],
          );
    return Semantics(
      container: true,
      liveRegion: true,
      child: ColoredBox(
        color: model.keepsPicture
            ? t.colors.scrim.withValues(alpha: 0)
            : t.colors.playerCanvas.withValues(
                alpha: model.kind == StateViewKind.locked ? 1 : 0.85,
              ),
        // Large text scales scroll instead of overflowing (03 §7.3).
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsetsDirectional.all(d.spacing16),
            child: content,
          ),
        ),
      ),
    );
  }
}
