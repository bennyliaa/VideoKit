// 04A X1: the plugin registers the open source notices of the Kit with
// Flutter's LicenseRegistry, so the host's licence page lists them.
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_flutter/src/licenses.dart';

class _FileBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async {
    expect(key, kVideoKitNoticeAsset);
    final bytes = File('assets/NOTICE').readAsBytesSync();
    return ByteData.sublistView(Uint8List.fromList(bytes));
  }
}

void main() {
  test('the notice asset lists the Kit dependencies with the Apache text', () {
    final text = File('assets/NOTICE').readAsStringSync();
    for (final name in [
      'AndroidX Media3',
      'kotlinx.coroutines',
      'Kotlin Standard Library',
      'Guava',
    ]) {
      expect(text, contains(name));
    }
    expect(text, contains('Apache License'));
    expect(text, contains('END OF TERMS AND CONDITIONS'));
    // Models not adopted yet are not listed (04A X1).
    expect(text.toLowerCase(), isNot(contains('opencv')));
    expect(text.toLowerCase(), isNot(contains('onnx')));
  });

  test('registration adds one VideoKit entry, once', () async {
    resetVideoKitLicensesForTest();
    final bundle = _FileBundle();
    registerVideoKitLicenses(bundle: bundle);
    registerVideoKitLicenses(bundle: bundle);
    final entries = await LicenseRegistry.licenses
        .where((e) => e.packages.contains(kVideoKitNoticePackages.single))
        .toList();
    expect(entries, hasLength(1));
    final text = entries.single.paragraphs.map((p) => p.text).join('\n');
    expect(text, contains('AndroidX Media3'));
    expect(utf8.encode(text), isNotEmpty);
  });
}
