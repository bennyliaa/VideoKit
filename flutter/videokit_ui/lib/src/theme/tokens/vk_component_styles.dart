import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Interaction state of a component (03 §5.2). `loading` is mapped from
/// business state by each component.
enum VkInteractionState {
  normal,
  pressed,
  focused,
  disabled,
  selected,
  hovered,
}

/// A value per interaction state (14 §7.1).
@immutable
final class VkStateStyle<T> {
  /// Creates a state style.
  const VkStateStyle({
    required this.normal,
    required this.pressed,
    required this.focused,
    required this.disabled,
    required this.selected,
    required this.hovered,
  });

  /// Same value in every state.
  const VkStateStyle.all(T value)
    : normal = value,
      pressed = value,
      focused = value,
      disabled = value,
      selected = value,
      hovered = value;

  final T normal;
  final T pressed;
  final T focused;
  final T disabled;
  final T selected;
  final T hovered;

  /// Value for [state].
  T of(VkInteractionState state) => switch (state) {
    VkInteractionState.normal => normal,
    VkInteractionState.pressed => pressed,
    VkInteractionState.focused => focused,
    VkInteractionState.disabled => disabled,
    VkInteractionState.selected => selected,
    VkInteractionState.hovered => hovered,
  };

  /// Value for a set of Flutter [WidgetState]s. Priority: disabled >
  /// pressed > focused > hovered > selected > normal.
  T resolve(Set<WidgetState> states) {
    if (states.contains(WidgetState.disabled)) return disabled;
    if (states.contains(WidgetState.pressed)) return pressed;
    if (states.contains(WidgetState.focused)) return focused;
    if (states.contains(WidgetState.hovered)) return hovered;
    if (states.contains(WidgetState.selected)) return selected;
    return normal;
  }

  /// Every state value in [VkInteractionState] order.
  List<T> get values => [for (final s in VkInteractionState.values) of(s)];

  @override
  bool operator ==(Object other) =>
      other is VkStateStyle<T> && listEquals(other.values, values);

  @override
  int get hashCode => Object.hashAll(values);
}

/// Box-like component appearance for one state.
@immutable
final class VkBoxStyle {
  /// Creates a box style.
  const VkBoxStyle({
    required this.background,
    required this.content,
    required this.border,
    required this.borderWidth,
    required this.radius,
    required this.padding,
    required this.minSize,
    required this.textStyle,
  });

  /// Background.
  final Color background;

  /// Content (text/icon) colour.
  final Color content;

  /// Border colour (transparent = none).
  final Color border;

  /// Border width.
  final double borderWidth;

  /// Corner radius.
  final double radius;

  /// Padding (direction-independent).
  final EdgeInsetsDirectional padding;

  /// Minimum width/height (touch target for interactive components).
  final double minSize;

  /// Label text style (colour already set to [content]).
  final TextStyle textStyle;

  /// Returns a copy with the given fields replaced.
  VkBoxStyle copyWith({
    Color? background,
    Color? content,
    Color? border,
    double? borderWidth,
    double? radius,
    EdgeInsetsDirectional? padding,
    double? minSize,
    TextStyle? textStyle,
  }) {
    final c = content ?? this.content;
    return VkBoxStyle(
      background: background ?? this.background,
      content: c,
      border: border ?? this.border,
      borderWidth: borderWidth ?? this.borderWidth,
      radius: radius ?? this.radius,
      padding: padding ?? this.padding,
      minSize: minSize ?? this.minSize,
      textStyle: (textStyle ?? this.textStyle).copyWith(color: c),
    );
  }

  /// Decoration for this style.
  BoxDecoration get decoration => BoxDecoration(
    color: background,
    borderRadius: BorderRadius.circular(radius),
    border: borderWidth > 0 && border.a > 0
        ? Border.all(color: border, width: borderWidth)
        : null,
  );

  @override
  bool operator ==(Object other) =>
      other is VkBoxStyle &&
      other.background == background &&
      other.content == content &&
      other.border == border &&
      other.borderWidth == borderWidth &&
      other.radius == radius &&
      other.padding == padding &&
      other.minSize == minSize &&
      other.textStyle == textStyle;

  @override
  int get hashCode => Object.hash(
    background,
    content,
    border,
    borderWidth,
    radius,
    padding,
    minSize,
    textStyle,
  );
}

/// `apps.videokit.component.seekbar` style (played, buffered, drag preview,
/// thumb).
@immutable
final class VkSeekBarStyle {
  /// Creates a seek bar style.
  const VkSeekBarStyle({
    required this.track,
    required this.buffered,
    required this.played,
    required this.preview,
    required this.thumb,
    required this.trackHeight,
    required this.trackHeightActive,
    required this.thumbSize,
    required this.bubble,
  });

  /// Unplayed track.
  final Color track;

  /// Buffered range.
  final Color buffered;

  /// Played range.
  final Color played;

  /// Drag preview range.
  final Color preview;

  /// Thumb colour per state.
  final VkStateStyle<Color> thumb;

  /// Track height (4).
  final double trackHeight;

  /// Track height while dragging (6).
  final double trackHeightActive;

  /// Thumb diameter (14).
  final double thumbSize;

  /// Time bubble.
  final VkBoxStyle bubble;

  @override
  bool operator ==(Object other) =>
      other is VkSeekBarStyle &&
      other.track == track &&
      other.buffered == buffered &&
      other.played == played &&
      other.preview == preview &&
      other.thumb == thumb &&
      other.trackHeight == trackHeight &&
      other.trackHeightActive == trackHeightActive &&
      other.thumbSize == thumbSize &&
      other.bubble == bubble;

  @override
  int get hashCode => Object.hash(
    track,
    buffered,
    played,
    preview,
    thumb,
    trackHeight,
    trackHeightActive,
    thumbSize,
    bubble,
  );
}

/// Component style tokens (`component.*`, `apps.videokit.component.*`).
/// M0-B1 implements button/chip/badge/seekbar data; the remaining component
/// keys of 14 §7.2 follow with their components.
@immutable
class VkComponentStyles extends ThemeExtension<VkComponentStyles> {
  /// Creates component styles.
  const VkComponentStyles({
    required this.buttonPrimary,
    required this.buttonSecondary,
    required this.buttonText,
    required this.buttonIcon,
    required this.chip,
    required this.badge,
    required this.seekBar,
  });

  /// `component.button.primary`.
  final VkStateStyle<VkBoxStyle> buttonPrimary;

  /// `component.button.secondary`.
  final VkStateStyle<VkBoxStyle> buttonSecondary;

  /// `component.button.text`.
  final VkStateStyle<VkBoxStyle> buttonText;

  /// `component.button.icon`.
  final VkStateStyle<VkBoxStyle> buttonIcon;

  /// `component.chip.default`.
  final VkStateStyle<VkBoxStyle> chip;

  /// `component.badge.default`.
  final VkStateStyle<VkBoxStyle> badge;

  /// `apps.videokit.component.seekbar`.
  final VkSeekBarStyle seekBar;

  /// Value of [key], or null.
  Object? operator [](VkTokenKey key) => byKey[key.key];

  /// Values by key string.
  Map<String, Object> get byKey => {
    VkTokenKeys.buttonPrimary.key: buttonPrimary,
    VkTokenKeys.buttonSecondary.key: buttonSecondary,
    VkTokenKeys.buttonText.key: buttonText,
    VkTokenKeys.buttonIcon.key: buttonIcon,
    VkTokenKeys.chipDefault.key: chip,
    VkTokenKeys.badgeDefault.key: badge,
    VkTokenKeys.seekBar.key: seekBar,
  };

  /// Returns a copy with values from [overrides] (key string → value of the
  /// right type) applied; mismatched values are ignored.
  VkComponentStyles withValues(Map<String, Object> overrides) {
    VkStateStyle<VkBoxStyle> box(VkTokenKey k, VkStateStyle<VkBoxStyle> v) {
      final o = overrides[k.key];
      return o is VkStateStyle<VkBoxStyle> ? o : v;
    }

    final s = overrides[VkTokenKeys.seekBar.key];
    return VkComponentStyles(
      buttonPrimary: box(VkTokenKeys.buttonPrimary, buttonPrimary),
      buttonSecondary: box(VkTokenKeys.buttonSecondary, buttonSecondary),
      buttonText: box(VkTokenKeys.buttonText, buttonText),
      buttonIcon: box(VkTokenKeys.buttonIcon, buttonIcon),
      chip: box(VkTokenKeys.chipDefault, chip),
      badge: box(VkTokenKeys.badgeDefault, badge),
      seekBar: s is VkSeekBarStyle ? s : seekBar,
    );
  }

  @override
  VkComponentStyles copyWith({Map<String, Object>? values}) =>
      values == null ? this : withValues(values);

  @override
  VkComponentStyles lerp(covariant VkComponentStyles? other, double t) =>
      t < 0.5 || other == null ? this : other;

  @override
  bool operator ==(Object other) =>
      other is VkComponentStyles && mapEquals(other.byKey, byKey);

  @override
  int get hashCode => Object.hashAll(byKey.values);
}
