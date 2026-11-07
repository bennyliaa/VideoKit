import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Colour tokens (`color.*`, `apps.videokit.color.*`) as a [ThemeExtension].
/// Every registered colour key always has a value.
@immutable
class VkColors extends ThemeExtension<VkColors> {
  /// Creates colours from a complete key → colour map.
  VkColors(Map<String, Color> values)
    : assert(
        VkTokenKeys.ofType(VkTokenType.color)
            .every((k) => values.containsKey(k.key)),
        'VkColors needs a value for every colour key',
      ),
      _values = Map.unmodifiable(values);

  final Map<String, Color> _values;

  /// Value of [key].
  Color operator [](VkTokenKey key) => _values[key.key]!;

  /// All values by key string.
  Map<String, Color> get values => _values;

  Color get background => this[VkTokenKeys.background];
  Color get surface => this[VkTokenKeys.surface];
  Color get surfaceVariant => this[VkTokenKeys.surfaceVariant];
  Color get surfaceHigh => this[VkTokenKeys.surfaceHigh];
  Color get border => this[VkTokenKeys.border];
  Color get borderStrong => this[VkTokenKeys.borderStrong];
  Color get divider => this[VkTokenKeys.divider];
  Color get focusRing => this[VkTokenKeys.focusRing];
  Color get scrim => this[VkTokenKeys.scrim];
  Color get textPrimary => this[VkTokenKeys.textPrimary];
  Color get textSecondary => this[VkTokenKeys.textSecondary];
  Color get textTertiary => this[VkTokenKeys.textTertiary];
  Color get primary => this[VkTokenKeys.primary];
  Color get onPrimary => this[VkTokenKeys.onPrimary];
  Color get primaryContainer => this[VkTokenKeys.primaryContainer];
  Color get onPrimaryContainer => this[VkTokenKeys.onPrimaryContainer];
  Color get disabledContent => this[VkTokenKeys.disabledContent];
  Color get disabledContainer => this[VkTokenKeys.disabledContainer];
  Color get success => this[VkTokenKeys.success];
  Color get successContent => this[VkTokenKeys.successContent];
  Color get successContainer => this[VkTokenKeys.successContainer];
  Color get warning => this[VkTokenKeys.warning];
  Color get warningContent => this[VkTokenKeys.warningContent];
  Color get warningContainer => this[VkTokenKeys.warningContainer];
  Color get error => this[VkTokenKeys.error];
  Color get errorContent => this[VkTokenKeys.errorContent];
  Color get errorContainer => this[VkTokenKeys.errorContainer];
  Color get info => this[VkTokenKeys.info];
  Color get infoContent => this[VkTokenKeys.infoContent];
  Color get infoContainer => this[VkTokenKeys.infoContainer];
  Color get shadowFloating => this[VkTokenKeys.shadowFloating];
  Color get shadowModal => this[VkTokenKeys.shadowModal];
  Color get selection => this[VkTokenKeys.selection];
  Color get trackTracked => this[VkTokenKeys.trackTracked];
  Color get trackLowConfidence => this[VkTokenKeys.trackLowConfidence];
  Color get trackAmbiguous => this[VkTokenKeys.trackAmbiguous];
  Color get trackLost => this[VkTokenKeys.trackLost];
  Color get demo => this[VkTokenKeys.demo];
  Color get demoContent => this[VkTokenKeys.demoContent];
  Color get playerCanvas => this[VkTokenKeys.playerCanvas];
  Color get playerControlsContent => this[VkTokenKeys.playerControlsContent];

  /// Returns a copy with [overrides] (key string → colour) applied.
  VkColors withValues(Map<String, Color> overrides) =>
      VkColors({..._values, ...overrides});

  @override
  VkColors copyWith({Map<String, Color>? values}) =>
      values == null ? this : withValues(values);

  @override
  VkColors lerp(covariant VkColors? other, double t) => other == null
      ? this
      : VkColors({
          for (final k in _values.keys)
            k: Color.lerp(_values[k], other._values[k], t)!,
        });

  @override
  bool operator ==(Object other) =>
      other is VkColors && mapEquals(other._values, _values);

  @override
  int get hashCode => Object.hashAllUnordered(
    _values.entries.map((e) => Object.hash(e.key, e.value)),
  );
}
