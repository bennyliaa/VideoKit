import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// 03 §5.5 / 14 §7.1: every registered token has a value in light and dark.
void main() {
  test('registry keys are unique, lower-case and dot separated', () {
    final keys = VkTokenKeys.all.map((k) => k.key).toList();
    expect(keys.toSet(), hasLength(keys.length));
    final pattern = RegExp(r'^[a-z0-9]+(\.[a-z0-9]+)+$');
    for (final k in keys) {
      expect(pattern.hasMatch(k), isTrue, reason: k);
    }
    for (final k in VkTokenKeys.all.where((k) => k.isVideoKitSpecific)) {
      expect(k.key, startsWith('apps.videokit.'));
    }
    expect(
      VkTokenType.values.every((t) => VkTokenKeys.ofType(t).isNotEmpty),
      isTrue,
      reason: 'all seven categories registered',
    );
    expect(
      VkTokenKeys.byKey('color.surfacevariant'),
      VkTokenKeys.surfaceVariant,
    );
    expect(VkTokenKeys.byKey('nope'), isNull);
    expect(themeSchemaVersion, 1);
    expect(const DefaultThemeSource().themeSchemaVersion, 1);
  });

  for (final b in Brightness.values) {
    test('every key has a ${b.name} value', () {
      final t = const DefaultThemeSource().resolve(b, null);
      for (final k in VkTokenKeys.all) {
        expect(t.valueOf(k), isNotNull, reason: '${k.key} (${b.name})');
      }
      for (final name in VkTokenKeys.iconNames.where((n) => n != 'unknown')) {
        expect(
          t.icons.resolve(name),
          isNot(t.icons.resolve('unknown')),
          reason: 'icon.$name has its own glyph',
        );
      }
    });
  }
}
