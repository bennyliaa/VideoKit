import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// 04A K1: `TransientNotice` codes are upper snake case and registered in
/// `spec/notices.json` (created by Coder B, format like errors.json). The
/// registry comparison is skipped until the file exists.
void main() {
  final file = File('../../spec/notices.json');

  test('Dart codes are upper snake case and unique', () {
    final upper = RegExp(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$');
    for (final c in NoticeCodes.all) {
      expect(upper.hasMatch(c), isTrue, reason: c);
    }
    expect(NoticeCodes.all.toSet(), hasLength(NoticeCodes.all.length));
  });

  test('spec/notices.json lists exactly the Dart codes', () {
    final json = jsonDecode(file.readAsStringSync()) as Map<String, Object?>;
    final raw = (json['notices'] ?? json['codes'])! as List<Object?>;
    final spec = {for (final e in raw) (e is Map ? e['code'] : e)! as String};
    expect(spec, NoticeCodes.all.toSet());
  }, skip: file.existsSync() ? false : 'spec/notices.json not present yet');

  test('K3: export warning codes are upper snake case; CODE:argument', () {
    final upper = RegExp(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$');
    for (final c in ExportWarnings.all) {
      expect(upper.hasMatch(c), isTrue, reason: c);
    }
    expect(ExportWarnings.all.toSet(), hasLength(ExportWarnings.all.length));
    expect(
      ExportWarnings.codeOf('TRACKING_COVERAGE_ACCEPTED:mask-1'),
      ExportWarnings.trackingCoverageAccepted,
    );
    expect(ExportWarnings.codeOf('SILENCE_INSERTED'), 'SILENCE_INSERTED');
    expect(
      ExportWarnings.has([
        'TRACKING_COVERAGE_ACCEPTED:m2',
      ], ExportWarnings.trackingCoverageAccepted),
      isTrue,
    );
    expect(
      ExportWarnings.has(const [], ExportWarnings.silenceInserted),
      isFalse,
    );
  });

  test('spec/notices.json exportWarnings lists exactly the Dart codes', () {
    final json = jsonDecode(file.readAsStringSync()) as Map<String, Object?>;
    final group = json['exportWarnings'] as List<Object?>?;
    if (group == null) {
      markTestSkipped('exportWarnings group not present yet');
      return;
    }
    final spec = {for (final e in group) (e! as Map)['code']! as String};
    expect(spec, ExportWarnings.all.toSet());
  }, skip: file.existsSync() ? false : 'spec/notices.json not present yet');
}
