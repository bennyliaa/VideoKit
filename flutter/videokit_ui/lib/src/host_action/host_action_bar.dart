import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_badge.dart';
import '../common/vk_buttons.dart';
import '../common/vk_pressable.dart';
import '../common/vk_sheet_host.dart';
import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';

/// Result of [layoutHostActions].
@immutable
final class HostActionLayout {
  /// Creates a layout.
  HostActionLayout(
    List<HostActionState> visible,
    List<HostActionState> overflow,
  ) : visible = List.unmodifiable(visible),
      overflow = List.unmodifiable(overflow);

  /// Actions shown in the bar, in order.
  final List<HostActionState> visible;

  /// Actions in the overflow menu, in order.
  final List<HostActionState> overflow;
}

/// 14 §5.4 layout algorithm:
///
/// 1. keep [placements]; sort by `displayPriority` descending, stable for
///    equal priority (host order);
/// 2. `slots = available ÷ itemExtent`; if anything overflows one slot is
///    reserved for the overflow button;
/// 3. with [collapseSecondary] (large text or compact layout) the whole
///    SECONDARY_BAR group goes to overflow; OVERFLOW placement always does.
HostActionLayout layoutHostActions(
  List<HostActionState> actions, {
  required double available,
  required double itemExtent,
  bool collapseSecondary = false,
  Set<ActionPlacement> placements = const {
    ActionPlacement.primaryBar,
    ActionPlacement.secondaryBar,
  },
}) {
  final indexed = actions.indexed.toList()
    ..sort((a, b) {
      final p = b.$2.action.displayPriority.compareTo(
        a.$2.action.displayPriority,
      );
      return p != 0 ? p : a.$1.compareTo(b.$1);
    });
  final candidates = <HostActionState>[];
  final overflow = <HostActionState>[];
  for (final (_, a) in indexed) {
    final placement = a.action.placement;
    final toOverflow =
        placement == ActionPlacement.overflow ||
        !placements.contains(placement) ||
        (collapseSecondary && placement == ActionPlacement.secondaryBar);
    (toOverflow ? overflow : candidates).add(a);
  }
  var slots = itemExtent <= 0 ? 0 : (available / itemExtent).floor();
  if (slots < 0) slots = 0;
  if (candidates.length <= slots && overflow.isEmpty) {
    return HostActionLayout(candidates, const []);
  }
  final keep = (slots - 1).clamp(0, candidates.length);
  // Overflow menu lists everything not shown, again by priority.
  final menu = [...candidates.skip(keep), ...overflow];
  final order = {for (final (pos, e) in indexed.indexed) e.$2: pos};
  menu.sort((a, b) => order[a]!.compareTo(order[b]!));
  return HostActionLayout(candidates.take(keep).toList(), menu);
}

/// Resolves a host string key (labels/content descriptions are host keys or
/// plain text, 04 §7); defaults to the key itself.
typedef HostStringResolver = String Function(String key);

/// Resolves a host resource icon (native hosts); null → `icon.unknown`.
typedef HostIconResolver = IconData? Function(HostIconResource icon);

/// UI-04 host action bar (14 §5.4, design pages 6 and 9–10): items ordered
/// by priority, overflow menu, enabled/selected/pending/badge states.
/// Pending repeats are merged by the session (`Superseded`, 04A I1).
class HostActionBar extends StatelessWidget {
  /// Creates a bar.
  const HostActionBar({
    super.key,
    required this.actions,
    required this.onActionPressed,
    this.axis = Axis.horizontal,
    this.showLabels = true,
    this.resolveString,
    this.resolveIcon,
    this.placements = const {
      ActionPlacement.primaryBar,
      ActionPlacement.secondaryBar,
    },
    this.showOverflowButton = true,
    this.onOverflowChanged,
    this.onPicture = true,
  });

  /// Over the player picture (`apps.videokit.component.hostactionbar`) or on
  /// an ordinary page surface (`component.hostactionbar.surface`, R1-13).
  final bool onPicture;

  VkHostActionBarStyle _style(BuildContext context) {
    final c = VkTheme.of(context).components;
    return onPicture ? c.hostActionBar : c.hostActionBarSurface;
  }

  /// Action states (from `VideoKitSessionState.hostActions`).
  final List<HostActionState> actions;

  /// Called with the action ID.
  final ValueChanged<String> onActionPressed;

  /// Layout axis: horizontal chips (landscape top bar) or a vertical column
  /// of discs with labels (portrait).
  final Axis axis;

  /// Show text labels.
  final bool showLabels;

  /// Host string resolver.
  final HostStringResolver? resolveString;

  /// Host icon resolver.
  final HostIconResolver? resolveIcon;

  /// Placements shown in the bar.
  final Set<ActionPlacement> placements;

  /// Whether the bar shows its own overflow button. Owners of a single
  /// "more" panel (UI-01, 14 §7.2 M0-B2 rule) pass false and take the items
  /// from [onOverflowChanged].
  final bool showOverflowButton;

  /// Reports the current overflow items after every layout (the receiver
  /// compares before rebuilding).
  final ValueChanged<List<HostActionState>>? onOverflowChanged;

  void _report(BuildContext context, List<HostActionState> overflow) {
    final cb = onOverflowChanged;
    if (cb == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (context.mounted) cb(overflow);
    });
  }

  String _label(String key) => resolveString?.call(key) ?? key;

  IconData _icon(BuildContext context, HostIcon icon) {
    final icons = VkTheme.of(context).icons;
    return switch (icon) {
      HostIconBuiltIn(:final iconKey) => icons.resolve(iconKey),
      HostIconResource() => resolveIcon?.call(icon) ?? icons.resolve('unknown'),
    };
  }

  /// Vertical labels under the icons (14 §5.4, R1-12): only at normal text
  /// sizes; with large text the column shows icons only (each keeps its
  /// content description) so labels never wrap over the next item.
  bool _verticalLabels(BuildContext context, bool collapse) =>
      showLabels && axis == Axis.vertical && !collapse;

  /// Height of one label line at the current text scale.
  static double _labelLineHeight(BuildContext context) {
    final t = VkTheme.of(context);
    final label = t.components.hostActionBar.label;
    final size = MediaQuery.textScalerOf(context).scale(label.fontSize ?? 12);
    return size * (label.height ?? 1.4);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final style = _style(context);
    final collapse = VkLayoutClass.collapseSecondary(
      MediaQuery.textScalerOf(context),
    );
    return LayoutBuilder(
      builder: (context, c) {
        final horizontal = axis == Axis.horizontal;
        final extent = horizontal ? c.maxWidth : c.maxHeight;
        final labels = _verticalLabels(context, collapse);
        final itemExtent =
            (horizontal
                ? t.dimensions.targetMin * 2.5
                : t.dimensions.targetMin +
                      (labels ? _labelLineHeight(context) : 0)) +
            style.spacing;
        final layout = layoutHostActions(
          actions,
          available: extent.isFinite ? extent : double.maxFinite,
          itemExtent: itemExtent,
          collapseSecondary: collapse,
          placements: placements,
        );
        final children = <Widget>[
          for (final a in layout.visible) _item(context, a),
          if (showOverflowButton && layout.overflow.isNotEmpty)
            _overflowButton(context, layout.overflow),
        ];
        _report(context, layout.overflow);
        return Semantics(
          container: true,
          explicitChildNodes: true,
          child: Flex(
            direction: axis,
            mainAxisSize: MainAxisSize.min,
            children: [
              for (final (i, w) in children.indexed) ...[
                if (i > 0) SizedBox.square(dimension: style.spacing),
                w,
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _item(BuildContext context, HostActionState state) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final a = state.action;
    final style = _style(context);
    final label = _label(a.labelKey);
    final description = _label(a.contentDescriptionKey);
    final enabled = a.enabled;
    final hint = !enabled
        ? s.text('stateUnavailable')
        : (state.isPending ? s.text('statePending') : null);
    if (axis == Axis.horizontal && showLabels) {
      return VkPressable(
        style: style.item,
        semanticLabel: description,
        semanticHint: hint,
        selected: a.selected,
        onPressed: enabled ? () => onActionPressed(a.actionId) : null,
        builder: (context, box) => Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _icon(context, a.icon),
              size: t.dimensions.icon20,
              color: box.content,
            ),
            SizedBox(width: t.dimensions.spacing4),
            Flexible(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: t.typography.label.copyWith(color: box.content),
              ),
            ),
            if (state.isPending) ...[
              SizedBox(width: t.dimensions.spacing4),
              SizedBox.square(
                dimension: t.dimensions.icon16,
                child: CircularProgressIndicator(
                  strokeWidth: t.dimensions.focusRingWidth,
                  color: style.pendingIndicator,
                ),
              ),
            ],
            if (a.badgeText != null) ...[
              SizedBox(width: t.dimensions.spacing4),
              _BadgeChip(text: a.badgeText!),
            ],
          ],
        ),
      );
    }
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        VkIconButton(
          icon: _icon(context, a.icon),
          semanticLabel: description,
          style: style.item,
          selected: a.selected,
          pending: state.isPending,
          badgeText: a.badgeText,
          onPressed: enabled ? () => onActionPressed(a.actionId) : null,
        ),
        if (_verticalLabels(
          context,
          VkLayoutClass.collapseSecondary(MediaQuery.textScalerOf(context)),
        ))
          ExcludeSemantics(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: t.dimensions.targetMin * 2),
              child: Text(
                label,
                maxLines: 1,
                textAlign: TextAlign.center,
                overflow: TextOverflow.ellipsis,
                style: style.label,
              ),
            ),
          ),
      ],
    );
  }

  Widget _overflowButton(BuildContext context, List<HostActionState> overflow) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    return VkIconButton(
      icon: t.icons.resolve('more'),
      semanticLabel: s.text('hostActionMore'),
      style: _style(context).item,
      pending: overflow.any((a) => a.isPending),
      onPressed: () {
        final sheets = VkSheetHost.maybeOf(context);
        sheets?.show(
          VkSheetEntry(
            id: 'hostActionsOverflow',
            title: s.text('hostActionMore'),
            builder: (context) => Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final a in overflow)
                  HostActionMenuItem(
                    state: a,
                    resolveString: resolveString,
                    resolveIcon: resolveIcon,
                    onPressed: (id) {
                      sheets.close('hostActionsOverflow');
                      onActionPressed(id);
                    },
                  ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// One host action as a menu row (overflow menus and the player's single
/// "more" panel).
class HostActionMenuItem extends StatelessWidget {
  /// Creates a row.
  const HostActionMenuItem({
    super.key,
    required this.state,
    required this.onPressed,
    this.resolveString,
    this.resolveIcon,
  });

  /// Action state.
  final HostActionState state;

  /// Called with the action ID (never while disabled).
  final ValueChanged<String> onPressed;

  /// Host string resolver.
  final HostStringResolver? resolveString;

  /// Host icon resolver.
  final HostIconResolver? resolveIcon;

  @override
  Widget build(BuildContext context) {
    final icons = VkTheme.of(context).icons;
    String label(String k) => resolveString?.call(k) ?? k;
    final a = state.action;
    return VkMenuItem(
      icon: switch (a.icon) {
        HostIconBuiltIn(:final iconKey) => icons.resolve(iconKey),
        final HostIconResource r =>
          resolveIcon?.call(r) ?? icons.resolve('unknown'),
      },
      label: label(a.labelKey),
      semanticLabel: label(a.contentDescriptionKey),
      selected: a.selected,
      pending: state.isPending,
      onPressed: a.enabled ? () => onPressed(a.actionId) : null,
    );
  }
}

class _BadgeChip extends StatelessWidget {
  const _BadgeChip({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final b = t.components.hostActionBar.badge;
    final shown = VkBadge.clip(VkStrings.of(context), text);
    return Container(
      padding: b.padding,
      decoration: b.decoration,
      child: Text(shown, style: b.textStyle, maxLines: 1),
    );
  }
}

/// Menu row (`component.menu.default`) used by overflow menus.
class VkMenuItem extends StatelessWidget {
  /// Creates a menu item.
  const VkMenuItem({
    super.key,
    required this.icon,
    required this.label,
    required this.onPressed,
    this.semanticLabel,
    this.selected = false,
    this.pending = false,
    this.trailing,
  });

  /// Icon.
  final IconData icon;

  /// Label.
  final String label;

  /// Screen-reader label (defaults to [label]).
  final String? semanticLabel;

  /// Callback; null disables.
  final VoidCallback? onPressed;

  /// Selected.
  final bool selected;

  /// Pending.
  final bool pending;

  /// Trailing widget.
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    return VkPressable(
      style: t.components.menu,
      semanticLabel: semanticLabel ?? label,
      semanticHint: onPressed == null
          ? s.text('stateUnavailable')
          : (pending ? s.text('statePending') : null),
      selected: selected,
      onPressed: onPressed,
      builder: (context, box) => Row(
        children: [
          Icon(icon, size: t.dimensions.icon24, color: box.content),
          SizedBox(width: t.dimensions.spacing12),
          Expanded(child: Text(label, style: box.textStyle)),
          if (pending)
            SizedBox.square(
              dimension: t.dimensions.icon16,
              child: CircularProgressIndicator(
                strokeWidth: t.dimensions.focusRingWidth,
                color: t.components.hostActionBar.pendingIndicator,
              ),
            ),
          if (selected)
            Icon(
              t.icons.check,
              size: t.dimensions.icon20,
              color: t.colors.primary,
            ),
          ?trailing,
        ],
      ),
    );
  }
}
