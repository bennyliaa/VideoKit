// M4-A2: "最近工程" keeps the module snapshot with its schemaVersion;
// restore goes through `restoreEditProject` (which migrates), a newer
// schema is told apart from a damaged file, and a migrated project is
// saved back in the current schema.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/projects/project_store.dart';

import 'm4_app_test.dart' show openRecent, startConcat;
import 'support.dart';

void main() {
  test('an entry without schemaVersion takes it from the snapshot', () {
    final e = RecentProject.fromJson({
      'id': 'project-1',
      'savedAtEpochMs': 0,
      'clipCount': 1,
      'snapshot': jsonEncode({'schemaVersion': 1, 'projectId': 'p'}),
    });
    expect(e, isNotNull);
    expect(e!.snapshot.schemaVersion, 1);
    expect(e.needsMigration, isFalse);
    // Re-written with the version beside the snapshot.
    expect(e.toJson()['schemaVersion'], 1);
  });

  test('no version anywhere: the entry is dropped, never fatal', () {
    expect(
      RecentProject.fromJson({
        'id': 'project-1',
        'savedAtEpochMs': 0,
        'clipCount': 1,
        'snapshot': '{}',
      }),
      isNull,
    );
  });

  test('an older schema needs migration', () {
    const e = RecentProject(
      id: 'p',
      savedAtEpochMs: 0,
      clipCount: 1,
      snapshot: SerializedEditProject(schemaVersion: 0, json: '{}'),
    );
    expect(e.needsMigration, SerializedEditProject.currentSchemaVersion > 0);
  });

  testWidgets('a damaged snapshot says "文件已损坏", not "更新版本"', (tester) async {
    final rig = AppRig.create();
    rig.storage.documents[ProjectStore.fileName] = jsonEncode({
      'schema': ProjectStore.fileSchema,
      'counter': 1,
      'projects': [
        RecentProject(
          id: 'project-1',
          savedAtEpochMs: 0,
          clipCount: 2,
          snapshot: SerializedEditProject(
            schemaVersion: SerializedEditProject.currentSchemaVersion,
            json: 'not json',
          ),
        ).toJson(),
      ],
    });
    await rig.pump(tester);
    await openRecent(tester);
    await tester.tap(find.text('拼接 2 个视频'));
    await settle(tester, 6);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(page.restoreFailed, isTrue);
    expect(page.restoreTooNew, isFalse);
    expect(find.text('无法打开这个工程：文件已损坏'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    await unmount(tester);
  });

  testWidgets('an older schema is migrated on restore and saved back as '
      'the current one', (tester) async {
    final v0 = jsonEncode({
      'schemaVersion': 0,
      'projectId': 'old',
      'revision': 2,
      'sources': [
        {
          'sourceId': 'src-1',
          'mediaToken': 't',
          'probe': {'durationUs': 3000000, 'width': 1920, 'height': 1080},
        },
      ],
      'timeline': {
        'clips': [
          {
            'clipId': 'clip-2',
            'sourceId': 'src-1',
            'inUs': 0,
            'outUs': 3000000,
          },
        ],
      },
    });
    final rig = AppRig.create();
    rig.storage.documents[ProjectStore.fileName] = jsonEncode({
      'schema': ProjectStore.fileSchema,
      'counter': 1,
      'projects': [
        RecentProject(
          id: 'project-1',
          savedAtEpochMs: 0,
          clipCount: 1,
          snapshot: SerializedEditProject(schemaVersion: 0, json: v0),
        ).toJson(),
      ],
    });
    await rig.pump(tester);
    await openRecent(tester);
    await tester.tap(find.text('拼接 1 个视频'));
    await settle(tester, 8);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(page.restoreFailed, isFalse);
    final raw = jsonDecode(
      rig.storage.documents[ProjectStore.fileName]!,
    ) as Map<String, Object?>;
    final entry = (raw['projects']! as List).single as Map<String, Object?>;
    expect(entry['schemaVersion'], SerializedEditProject.currentSchemaVersion);
    final inner = jsonDecode(entry['snapshot']! as String) as Map;
    expect(inner['schemaVersion'], SerializedEditProject.currentSchemaVersion);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });

  testWidgets('a project saved and restored keeps its schemaVersion', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await startConcat(tester);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    final raw = jsonDecode(
      rig.storage.documents[ProjectStore.fileName]!,
    ) as Map<String, Object?>;
    expect(raw['schema'], ProjectStore.fileSchema);
    final entry = (raw['projects']! as List).single as Map<String, Object?>;
    expect(entry['schemaVersion'], SerializedEditProject.currentSchemaVersion);
    final inner = jsonDecode(entry['snapshot']! as String) as Map;
    expect(inner['schemaVersion'], entry['schemaVersion']);
    await openRecent(tester);
    await tester.tap(find.text('拼接 2 个视频'));
    await settle(tester, 8);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(page.restoreFailed, isFalse);
    expect(page.project!.state.value.timeline.clips, hasLength(2));
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });
}
