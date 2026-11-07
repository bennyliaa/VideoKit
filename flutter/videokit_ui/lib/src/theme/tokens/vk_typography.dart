import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Text style tokens (`typography.*`, `apps.videokit.typography.timecode`).
@immutable
class VkTypography extends ThemeExtension<VkTypography> {
  /// Creates typography from a complete key → style map.
  VkTypography(Map<String, TextStyle> values)
    : assert(
        VkTokenKeys.ofType(VkTokenType.typography)
            .every((k) => values.containsKey(k.key)),
        'VkTypography needs a value for every typography key',
      ),
      _values = Map.unmodifiable(values);

  /// The 14 §7.2 scale (size/line height weight) in [primary]/[secondary]
  /// colours; [fontFamily] null = platform default (no bundled fonts).
  factory VkTypography.standard({
    required Color primary,
    required Color secondary,
    String? fontFamily,
  }) {
    TextStyle s(double size, double line, FontWeight w, Color c) => TextStyle(
      fontFamily: fontFamily,
      fontSize: size,
      height: line / size,
      fontWeight: w,
      color: c,
    );
    return VkTypography({
      VkTokenKeys.display.key: s(28, 36, FontWeight.w600, primary),
      VkTokenKeys.titleLarge.key: s(22, 30, FontWeight.w600, primary),
      VkTokenKeys.title.key: s(20, 28, FontWeight.w600, primary),
      VkTokenKeys.body.key: s(14, 20, FontWeight.w400, primary),
      VkTokenKeys.bodySmall.key: s(13, 18, FontWeight.w400, primary),
      VkTokenKeys.label.key: s(12, 16, FontWeight.w500, primary),
      VkTokenKeys.caption.key: s(12, 16, FontWeight.w400, secondary),
      VkTokenKeys.timecode.key: s(
        13,
        18,
        FontWeight.w500,
        primary,
      ).copyWith(fontFeatures: const [FontFeature.tabularFigures()]),
    });
  }

  final Map<String, TextStyle> _values;

  /// Value of [key].
  TextStyle operator [](VkTokenKey key) => _values[key.key]!;

  /// All values by key string.
  Map<String, TextStyle> get values => _values;

  TextStyle get display => this[VkTokenKeys.display];
  TextStyle get titleLarge => this[VkTokenKeys.titleLarge];
  TextStyle get title => this[VkTokenKeys.title];
  TextStyle get body => this[VkTokenKeys.body];
  TextStyle get bodySmall => this[VkTokenKeys.bodySmall];
  TextStyle get label => this[VkTokenKeys.label];
  TextStyle get caption => this[VkTokenKeys.caption];

  /// Timecode (tabular figures).
  TextStyle get timecode => this[VkTokenKeys.timecode];

  @override
  VkTypography copyWith({Map<String, TextStyle>? values}) =>
      values == null ? this : VkTypography({..._values, ...values});

  @override
  VkTypography lerp(covariant VkTypography? other, double t) => other == null
      ? this
      : VkTypography({
          for (final k in _values.keys)
            k: TextStyle.lerp(_values[k], other._values[k], t)!,
        });

  @override
  bool operator ==(Object other) =>
      other is VkTypography && mapEquals(other._values, _values);

  @override
  int get hashCode => Object.hashAllUnordered(
    _values.entries.map((e) => Object.hash(e.key, e.value)),
  );
}
