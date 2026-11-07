import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// Cross-checks `ErrorCode` against the shared registry `spec/errors.json`
/// (04A §1 rule 4). The registry and the Dart enum must list exactly the same
/// codes in the same order (TEST-R1 R1-08: a registry that lags behind Dart
/// is a failure, not a warning; spec and API change in the same batch).
void main() {
  final file = File('../../spec/errors.json');
  final skip = file.existsSync() ? false : 'spec/errors.json not present';

  Map<String, Object?> load() =>
      jsonDecode(file.readAsStringSync()) as Map<String, Object?>;

  List<Map<String, Object?>> codes() => [
    for (final e in load()['codes']! as List<Object?>)
      (e! as Map).cast<String, Object?>(),
  ];

  test('codes: registry equals ErrorCode, in order', () {
    final spec = [for (final c in codes()) c['code']! as String];
    final dart = [for (final c in ErrorCode.values) c.wireName];
    expect(spec.toSet(), hasLength(spec.length), reason: 'duplicates');
    expect(registryMismatch(spec, dart), isNull);
  }, skip: skip);

  test('R1-08: a lagging or reordered registry is a failure', () {
    expect(registryMismatch(['A', 'B'], ['A', 'B']), isNull);
    expect(registryMismatch(['A'], ['A', 'B']), contains('lags Dart by: [B]'));
    expect(registryMismatch(['B', 'A'], ['A', 'B']), contains('order'));
    expect(registryMismatch(['A', 'B', 'C'], ['A', 'B']), isNotNull);
  });

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

/// Why `spec/errors.json` and `ErrorCode` differ, or null when they match.
String? registryMismatch(List<String> spec, List<String> dart) {
  for (var i = 0; i < spec.length && i < dart.length; i++) {
    if (spec[i] != dart[i]) {
      return 'order differs at $i: ${spec[i]} vs ${dart[i]}';
    }
  }
  if (spec.length < dart.length) {
    return 'spec/errors.json lags Dart by: ${dart.skip(spec.length).toList()}';
  }
  if (spec.length > dart.length) {
    return 'spec/errors.json has codes Dart does not know: '
        '${spec.skip(dart.length).toList()}';
  }
  return null;
}
