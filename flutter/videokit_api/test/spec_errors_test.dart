import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// Cross-checks `ErrorCode` against the shared registry `spec/errors.json`
/// (owned by the native side, 13 §3.2). Skipped while the file does not
/// exist. Accepted shapes: `["CODE", …]`, `[{"code": "CODE"}, …]`,
/// `{"codes": [...]}` or `{"errors": [...]}`.
void main() {
  final file = File('../../spec/errors.json');
  test('ErrorCode matches spec/errors.json', () {
    final Object? raw = jsonDecode(file.readAsStringSync());
    Object? list = raw;
    if (raw is Map) list = raw['codes'] ?? raw['errors'];
    expect(
      list,
      isA<List<Object?>>(),
      reason: 'unrecognised errors.json shape',
    );
    final codes = <String>{
      for (final e in list! as List<Object?>)
        if (e is String)
          e
        else if (e is Map && e['code'] is String)
          e['code']! as String,
    };
    expect(codes, ErrorCode.values.map((c) => c.wireName).toSet());
  }, skip: file.existsSync() ? false : 'spec/errors.json not present yet');
}
