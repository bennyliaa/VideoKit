import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import '../../tools/vk_lints/vk_literal_lint.dart';
import '../tool/release_isolation.dart';

void main() {
  test('vk_literal_lint: App text from ARB, colours/sizes from tokens', () {
    // 14 §11.3 via tools/vk_lints (M0-B6 report §2.4).
    final findings = lintDirectories(['lib']);
    expect(findings.map((f) => '$f'), isEmpty);
  });

  group('release isolation (14 §11.4, 04A P3)', () {
    final root = Directory('.');

    test('lib/main.dart cannot reach videokit_fake or demo code', () {
      final r = checkIsolation(root, 'main.dart');
      expect(r.violations, isEmpty);
      expect(
        r.reachable.any((u) => u.startsWith('package:videokit_ui/')),
        isTrue,
        reason: 'the walk follows workspace packages',
      );
      expect(demoAssets(root), isEmpty, reason: 'no demo assets bundled');
    });

    test('lib/main_demo.dart does reach the Fake (control)', () {
      final r = checkIsolation(root, 'main_demo.dart');
      expect(
        r.violations.any(
          (v) => v.contains('videokit_fake') || v.contains('/backend/demo_'),
        ),
        isTrue,
        reason: 'the walk must detect the demo backend',
      );
    });
  });
}
