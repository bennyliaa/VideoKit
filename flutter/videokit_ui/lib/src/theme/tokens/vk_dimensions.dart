import 'dart:ui' show lerpDouble;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Dimension tokens in logical pixels (`dimension.*`,
/// `apps.videokit.dimension.*`; 14 §7.2).
@immutable
class VkDimensions extends ThemeExtension<VkDimensions> {
  /// Creates dimensions from a complete key → value map.
  VkDimensions(Map<String, double> values)
    : assert(
        VkTokenKeys.ofType(VkTokenType.dimension)
            .every((k) => values.containsKey(k.key)),
        'VkDimensions needs a value for every dimension key',
      ),
      _values = Map.unmodifiable(values);

  /// 14 §7.2 values.
  factory VkDimensions.standard() => VkDimensions({
    VkTokenKeys.spacing4.key: 4,
    VkTokenKeys.spacing8.key: 8,
    VkTokenKeys.spacing12.key: 12,
    VkTokenKeys.spacing16.key: 16,
    VkTokenKeys.spacing24.key: 24,
    VkTokenKeys.spacing32.key: 32,
    VkTokenKeys.cornerSmall.key: 6,
    VkTokenKeys.cornerMedium.key: 10,
    VkTokenKeys.cornerLarge.key: 14,
    VkTokenKeys.cornerXLarge.key: 20,
    VkTokenKeys.cornerFull.key: 999,
    VkTokenKeys.targetMin.key: 48,
    VkTokenKeys.icon16.key: 16,
    VkTokenKeys.icon20.key: 20,
    VkTokenKeys.icon24.key: 24,
    VkTokenKeys.borderWidth.key: 1,
    VkTokenKeys.focusRingWidth.key: 2,
    VkTokenKeys.floatingOffsetY.key: 2,
    VkTokenKeys.floatingBlur.key: 8,
    VkTokenKeys.modalOffsetY.key: 8,
    VkTokenKeys.modalBlur.key: 24,
    VkTokenKeys.controlBarHeight.key: 56,
    VkTokenKeys.seekBarTrack.key: 4,
    VkTokenKeys.seekBarTrackActive.key: 6,
    VkTokenKeys.seekBarThumb.key: 14,
    VkTokenKeys.timelineClipRow.key: 56,
    VkTokenKeys.timelineMaskRow.key: 20,
    VkTokenKeys.timelineCoverageStrip.key: 8,
    VkTokenKeys.maskBoxStroke.key: 2,
    VkTokenKeys.maskBoxHandle.key: 10,
    VkTokenKeys.maskBoxHandleTarget.key: 24,
  });

  final Map<String, double> _values;

  /// Value of [key].
  double operator [](VkTokenKey key) => _values[key.key]!;

  /// All values by key string.
  Map<String, double> get values => _values;

  double get spacing4 => this[VkTokenKeys.spacing4];
  double get spacing8 => this[VkTokenKeys.spacing8];
  double get spacing12 => this[VkTokenKeys.spacing12];
  double get spacing16 => this[VkTokenKeys.spacing16];
  double get spacing24 => this[VkTokenKeys.spacing24];
  double get spacing32 => this[VkTokenKeys.spacing32];
  double get cornerSmall => this[VkTokenKeys.cornerSmall];
  double get cornerMedium => this[VkTokenKeys.cornerMedium];
  double get cornerLarge => this[VkTokenKeys.cornerLarge];
  double get cornerXLarge => this[VkTokenKeys.cornerXLarge];
  double get cornerFull => this[VkTokenKeys.cornerFull];
  double get targetMin => this[VkTokenKeys.targetMin];
  double get icon16 => this[VkTokenKeys.icon16];
  double get icon20 => this[VkTokenKeys.icon20];
  double get icon24 => this[VkTokenKeys.icon24];
  double get borderWidth => this[VkTokenKeys.borderWidth];
  double get focusRingWidth => this[VkTokenKeys.focusRingWidth];
  double get controlBarHeight => this[VkTokenKeys.controlBarHeight];
  double get seekBarTrack => this[VkTokenKeys.seekBarTrack];
  double get seekBarTrackActive => this[VkTokenKeys.seekBarTrackActive];
  double get seekBarThumb => this[VkTokenKeys.seekBarThumb];
  double get timelineClipRow => this[VkTokenKeys.timelineClipRow];
  double get timelineMaskRow => this[VkTokenKeys.timelineMaskRow];
  double get timelineCoverageStrip => this[VkTokenKeys.timelineCoverageStrip];
  double get maskBoxStroke => this[VkTokenKeys.maskBoxStroke];
  double get maskBoxHandle => this[VkTokenKeys.maskBoxHandle];
  double get maskBoxHandleTarget => this[VkTokenKeys.maskBoxHandleTarget];

  /// Elevation "floating" shadow in [color] (design category, 03 §5.2).
  BoxShadow floatingShadow(Color color) => BoxShadow(
    color: color,
    offset: Offset(0, this[VkTokenKeys.floatingOffsetY]),
    blurRadius: this[VkTokenKeys.floatingBlur],
  );

  /// Elevation "modal" shadow in [color].
  BoxShadow modalShadow(Color color) => BoxShadow(
    color: color,
    offset: Offset(0, this[VkTokenKeys.modalOffsetY]),
    blurRadius: this[VkTokenKeys.modalBlur],
  );

  @override
  VkDimensions copyWith({Map<String, double>? values}) =>
      values == null ? this : VkDimensions({..._values, ...values});

  @override
  VkDimensions lerp(covariant VkDimensions? other, double t) => other == null
      ? this
      : VkDimensions({
          for (final k in _values.keys)
            k: lerpDouble(_values[k], other._values[k], t)!,
        });

  @override
  bool operator ==(Object other) =>
      other is VkDimensions && mapEquals(other._values, _values);

  @override
  int get hashCode => Object.hashAllUnordered(
    _values.entries.map((e) => Object.hash(e.key, e.value)),
  );
}
