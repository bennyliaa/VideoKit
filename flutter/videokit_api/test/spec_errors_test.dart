import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// Cross-checks `ErrorCode` against the shared registry `spec/errors.json`
/// (04A §1 rule 4). Codes are appended at the end, so the registry must be
/// an ordered prefix of the Dart enum; while the native side has not yet
/// added the 04A V7 codes the prefix check passes and the gap is printed.
/// Once the registry lists as many codes as Dart, they must match exactly.
void main() {
  final file = File('../../spec/errors.json');
  final skip = file.existsSync() ? false : 'spec/errors.json not present';

  Map<String, Object?> load() =>
      jsonDecode(file.readAsStringSync()) as Map<String, Object?>;

  List<Map<String, Object?>> codes() => [
    for (final e in load()['codes']! as List<Object?>)
      (e! as Map).cast<String, Object?>(),
  ];

  test('codes: ordered, registry is a prefix of ErrorCode', () {
    final spec = [for (final c in codes()) c['code']! as String];
    final dart = [for (final c in ErrorCode.values) c.wireName];
    expect(spec.toSet(), hasLength(spec.length), reason: 'duplicates');
    expect(dart.take(spec.length).toList(), spec);
    if (spec.length < dart.length) {
      // ignore: avoid_print
      print(
        'spec/errors.json lags Dart by: ${dart.skip(spec.length).toList()}',
      );
    } else {
      expect(spec, dart);
    }
  }, skip: skip);

  test('stages, actions and fallback parse to known values', () {
    final json = load();
    expect(
      ErrorCode.fromName(json['unknownCodeFallback'] as String?),
      ErrorCode.internalErrorRedacted,
    );
    for (final c in codes()) {
      final stage = c['stage'] as String;
      expect(ErrorStage.fromName(stage).wireName, stage, reason: '$c');
      final action = c['suggestedAction'] as String;
      expect(SuggestedAction.fromName(action).wireName, action, reason: '$c');
      expect(c['retryable'], isA<bool>());
    }
  }, skip: skip);
}
