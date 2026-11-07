import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// One animation token: duration + curve.
@immutable
final class VkAnimation {
  /// Creates an animation token.
  const VkAnimation(this.duration, [this.curve = Curves.easeOutCubic]);

  /// Disabled animation (reduced motion): switch directly.
  static const VkAnimation disabled = VkAnimation(Duration.zero, Curves.linear);

  /// Duration.
  final Duration duration;

  /// Curve.
  final Curve curve;

  /// Whether this animation is disabled.
  bool get isDisabled => duration == Duration.zero;

  @override
  bool operator ==(Object other) =>
      other is VkAnimation &&
      other.duration == duration &&
      other.curve == curve;

  @override
  int get hashCode => Object.hash(duration, curve);

  @override
  String toString() => 'VkAnimation(${duration.inMilliseconds} ms, $curve)';
}

/// Animation tokens (`animation.press/small/normal/page`; 14 §7.2:
/// 100/160/200/280 ms, easeOutCubic; all disabled with reduced motion).
@immutable
class VkAnimations extends ThemeExtension<VkAnimations> {
  /// Creates animations from a complete key → value map.
  VkAnimations(Map<String, VkAnimation> values, {this.reduced = false})
    : assert(
        VkTokenKeys.ofType(VkTokenType.animation)
            .every((k) => values.containsKey(k.key)),
        'VkAnimations needs a value for every animation key',
      ),
      _values = Map.unmodifiable(values);

  /// 14 §7.2 values.
  factory VkAnimations.standard() => VkAnimations({
    VkTokenKeys.animPress.key: const VkAnimation(Duration(milliseconds: 100)),
    VkTokenKeys.animSmall.key: const VkAnimation(Duration(milliseconds: 160)),
    VkTokenKeys.animNormal.key: const VkAnimation(Duration(milliseconds: 200)),
    VkTokenKeys.animPage.key: const VkAnimation(Duration(milliseconds: 280)),
  });

  final Map<String, VkAnimation> _values;

  /// Whether reduced motion is active (every token disabled).
  final bool reduced;

  /// Value of [key].
  VkAnimation operator [](VkTokenKey key) => _values[key.key]!;

  /// All values by key string.
  Map<String, VkAnimation> get values => _values;

  VkAnimation get press => this[VkTokenKeys.animPress];
  VkAnimation get small => this[VkTokenKeys.animSmall];
  VkAnimation get normal => this[VkTokenKeys.animNormal];
  VkAnimation get page => this[VkTokenKeys.animPage];

  /// This, or every token disabled when [reduce] is true.
  VkAnimations resolve({required bool reduce}) => !reduce || reduced
      ? this
      : VkAnimations({
          for (final k in _values.keys) k: VkAnimation.disabled,
        }, reduced: true);

  @override
  VkAnimations copyWith({Map<String, VkAnimation>? values, bool? reduced}) =>
      VkAnimations({..._values, ...?values}, reduced: reduced ?? this.reduced);

  @override
  VkAnimations lerp(covariant VkAnimations? other, double t) =>
      t < 0.5 || other == null ? this : other;

  @override
  bool operator ==(Object other) =>
      other is VkAnimations &&
      other.reduced == reduced &&
      mapEquals(other._values, _values);

  @override
  int get hashCode => Object.hash(
    reduced,
    Object.hashAllUnordered(
      _values.entries.map((e) => Object.hash(e.key, e.value)),
    ),
  );
}
