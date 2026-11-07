import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';

/// Interactive box shared by VideoKit buttons: resolves a six-state
/// [VkStateStyle] (normal/pressed/focused/disabled/selected/hovered) from
/// pointer, keyboard and focus input, enforces the style's minimum size
/// (touch target) and owns the [Semantics] (role, label, state), which
/// host overrides never change (03 §5.1).
class VkPressable extends StatefulWidget {
  /// Creates a pressable.
  const VkPressable({
    super.key,
    required this.style,
    required this.semanticLabel,
    required this.builder,
    this.onPressed,
    this.selected = false,
    this.toggled,
    this.semanticValue,
    this.semanticHint,
    this.focusNode,
    this.autofocus = false,
  });

  /// State styles.
  final VkStateStyle<VkBoxStyle> style;

  /// Screen-reader label (from ARB or host strings).
  final String semanticLabel;

  /// Optional screen-reader value (e.g. "1.5×").
  final String? semanticValue;

  /// Optional screen-reader hint (e.g. "等待中").
  final String? semanticHint;

  /// Builds the content for the resolved style.
  final Widget Function(BuildContext context, VkBoxStyle style) builder;

  /// Activation callback; null disables the control.
  final VoidCallback? onPressed;

  /// Selected state.
  final bool selected;

  /// Toggle state for switches (null = not a toggle).
  final bool? toggled;

  /// Focus node.
  final FocusNode? focusNode;

  /// Autofocus.
  final bool autofocus;

  @override
  State<VkPressable> createState() => _VkPressableState();
}

class _VkPressableState extends State<VkPressable> {
  bool _pressed = false;
  bool _hovered = false;
  bool _focused = false;

  bool get _enabled => widget.onPressed != null;

  VkBoxStyle _resolve() {
    final s = widget.style;
    if (!_enabled) return s.disabled;
    if (_pressed) return s.pressed;
    if (_focused) return s.focused;
    if (_hovered) return s.hovered;
    if (widget.selected) return s.selected;
    return s.normal;
  }

  void _activate() {
    if (!_enabled) return;
    HapticFeedback.selectionClick();
    widget.onPressed!();
  }

  @override
  Widget build(BuildContext context) {
    final style = _resolve();
    final motion = VkTheme.of(context).animations.press;
    return Semantics(
      container: true,
      button: widget.toggled == null,
      toggled: widget.toggled,
      enabled: _enabled,
      selected: widget.toggled == null ? widget.selected : null,
      label: widget.semanticLabel,
      value: widget.semanticValue,
      hint: widget.semanticHint,
      onTap: _enabled ? _activate : null,
      child: ExcludeSemantics(
        child: FocusableActionDetector(
          enabled: _enabled,
          focusNode: widget.focusNode,
          autofocus: widget.autofocus,
          mouseCursor: _enabled
              ? SystemMouseCursors.click
              : SystemMouseCursors.basic,
          onShowFocusHighlight: (v) => setState(() => _focused = v),
          onShowHoverHighlight: (v) => setState(() => _hovered = v),
          actions: {
            ActivateIntent: CallbackAction<ActivateIntent>(
              onInvoke: (_) {
                _activate();
                return null;
              },
            ),
          },
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTapDown: _enabled ? (_) => setState(() => _pressed = true) : null,
            onTapUp: _enabled ? (_) => setState(() => _pressed = false) : null,
            onTapCancel: _enabled
                ? () => setState(() => _pressed = false)
                : null,
            onTap: _enabled ? _activate : null,
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minWidth: style.minSize,
                minHeight: style.minSize,
              ),
              child: AnimatedContainer(
                duration: motion.duration,
                curve: motion.curve,
                padding: style.padding,
                decoration: style.decoration,
                child: DefaultTextStyle.merge(
                  style: style.textStyle,
                  child: IconTheme.merge(
                    data: IconThemeData(color: style.content),
                    child: Center(
                      widthFactor: 1,
                      heightFactor: 1,
                      child: widget.builder(context, style),
                    ),
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
