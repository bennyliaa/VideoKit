// 04A E7 (M5A follow-up, committed with M6-A1): Q3 / R8 a project written
// by a newer schema minor is never overwritten (saves go to a copy), and
// Q4 avatars used by kept projects are never evicted from the avatar store.
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/avatar/avatar_store.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/projects/project_store.dart';

import 'm4_app_test.dart' show openRecent, startConcat;
import 'support.dart';

Map<String, Object?> _file(AppRig rig) =>
    jsonDecode(rig.storage.documents[ProjectStore.fileName]!)
        as Map<String, Object?>;

List<Map<String, Object?>> _entries(AppRig rig) => [
  for (final e in _file(rig)['projects']! as List) e as Map<String, Object?>,
];

void main() {
  group('Q3 / R8', () {
    test('schemaMinor: beside the snapshot, else inside it, else 0', () {
      Map<String, Object?> entry(Map<String, Object?> extra, String snap) => {
        'id': 'p',
        'savedAtEpochMs': 0,
        'clipCount': 1,
        'snapshot': snap,
        ...extra,
      };
      final inner = jsonEncode({'schemaVersion': 1, 'schemaMinor': 3});
      expect(RecentProject.fromJson(entry({}, inner))!.schemaMinor, 3);
      expect(
        RecentProject.fromJson(entry({'schemaMinor': 2}, inner))!.schemaMinor,
        2,
      );
      final bare = jsonEncode({'schemaVersion': 1});
      final e = RecentProject.fromJson(entry({}, bare))!;
      expect(e.schemaMinor, 0);
      expect(e.isNewerMinor, isFalse);
      final newer = RecentProject.fromJson(
        entry({}, jsonEncode({
          'schemaVersion': SerializedEditProject.currentSchemaVersion,
          'schemaMinor': SerializedEditProject.currentSchemaMinor + 1,
        })),
      )!;
      expect(newer.isNewerMinor, isTrue);
      final copy = RecentProject(
        id: 'c',
        savedAtEpochMs: 1,
        clipCount: 1,
        snapshot: const SerializedEditProject(schemaVersion: 1, json: '{}'),
        schemaMinor: 1,
        copyOf: 'p',
        avatarTokens: const ['app-avatar-1'],
      );
      expect(RecentProject.fromJson(copy.toJson()), copy);
    });

    testWidgets('a newer-minor project is kept; edits go to a copy, once '
        'noticed, and later saves follow the copy', (tester) async {
      // A project saved by this App, then marked as written by a newer one.
      final first = AppRig.create();
      await first.pump(tester);
      await startConcat(tester);
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      await unmount(tester);
      final newer = SerializedEditProject.currentSchemaMinor + 1;
      final saved = _entries(first).single;
      final inner = jsonDecode(saved['snapshot']! as String) as Map;
      inner['schemaMinor'] = newer;
      final original = {
        ...saved,
        'schemaMinor': newer,
        'snapshot': jsonEncode(inner),
      };
      final rig = AppRig.create();
      rig.storage.documents[ProjectStore.fileName] = jsonEncode({
        ..._file(first),
        'projects': [original],
      });

      await rig.pump(tester);
      await openRecent(tester);
      await tester.tap(find.text('拼接 2 个视频'));
      await settle(tester, 8);
      final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
      expect(page.restoreFailed, isFalse, reason: 'R2: minor is readable');
      await tester.binding.handlePopRoute();
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));
      expect(page.savedAsCopyNoticed, isTrue);
      expect(
        find.text('这个工程由更新版本的应用保存，修改已另存为副本，原工程保持不变'),
        findsOneWidget,
      );
      await settle(tester, 6);
      final entries = _entries(rig);
      expect(entries, hasLength(2));
      final kept = entries.firstWhere((e) => e['id'] == original['id']);
      expect(kept, original, reason: 'never overwritten');
      final copy = entries.firstWhere((e) => e['id'] != original['id']);
      expect(copy['copyOf'], original['id']);
      expect(copy['schemaMinor'], SerializedEditProject.currentSchemaMinor);
      expect(_file(rig)['copies'], {original['id']: copy['id']});
      expect(find.text('副本：原工程由更新版本的应用保存'), findsOneWidget);

      // Opening the original again: still the same copy, no third entry.
      await tester.tap(find.text('拼接 2 个视频').last);
      await settle(tester, 8);
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      expect(_entries(rig), hasLength(2));
      expect(
        _entries(rig).firstWhere((e) => e['id'] == original['id']),
        original,
      );
      await tester.binding.handlePopRoute();
      await settle(tester, 4);
      await unmount(tester);
    });
  });

  group('Q4', () {
    test('referenced avatars are never evicted; full when all are used', () async {
      final storage = MemoryAppStorage();
      final used = <String>{};
      final store = AvatarStore(storage: storage, referenced: () => used);
      final tokens = [
        for (var i = 0; i < AvatarStore.limit; i++)
          await store.save(Uint8List.fromList([i])),
      ];
      // The oldest two are used by kept projects.
      used.addAll(tokens.take(2));
      final next = await store.save(Uint8List.fromList([99]));
      expect(store.recent, hasLength(AvatarStore.limit));
      expect(store.recent.first.token, next);
      expect(await store.bytes(tokens[0]), isNotNull, reason: 'used');
      expect(await store.bytes(tokens[1]), isNotNull, reason: 'used');
      expect(await store.bytes(tokens[2]), isNull, reason: 'oldest unused');
      expect(store.isFull, isFalse);

      used.addAll(store.recent.map((a) => a.token));
      expect(store.isFull, isTrue);
      await expectLater(
        store.save(Uint8List.fromList([100])),
        throwsA(isA<AvatarStoreFullException>()),
      );
      expect(store.recent, hasLength(AvatarStore.limit));
    });

    test('ProjectStore reports the avatar tokens of its kept projects', () async {
      final storage = MemoryAppStorage();
      RecentProject p(String id, List<String> tokens) => RecentProject(
        id: id,
        savedAtEpochMs: 0,
        clipCount: 1,
        snapshot: const SerializedEditProject(schemaVersion: 1, json: '{}'),
        avatarTokens: tokens,
      );
      storage.documents[ProjectStore.fileName] = jsonEncode({
        'schema': ProjectStore.fileSchema,
        'counter': 2,
        'projects': [
          p('project-1', ['app-avatar-1', 'app-avatar-2']).toJson(),
          p('project-2', ['app-avatar-2', 'app-avatar-5']).toJson(),
        ],
      });
      final store = ProjectStore(storage: storage);
      await store.load();
      expect(store.referencedAvatars, {
        'app-avatar-1',
        'app-avatar-2',
        'app-avatar-5',
      });
      await store.remove('project-1');
      expect(store.referencedAvatars, {'app-avatar-2', 'app-avatar-5'});
    });
  });
}
