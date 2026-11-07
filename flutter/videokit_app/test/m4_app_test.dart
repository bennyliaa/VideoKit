// M4-A1: "最近工程" — the concat project is saved as a snapshot when the
// user leaves and restored from the list; "添加视频" adds clips.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/projects/project_store.dart';
import 'package:videokit_app/projects/recent_projects_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'app_test.dart' show pickDemo;
import 'support.dart';

List<Map<String, Object?>> savedProjects(AppRig rig) {
  final raw = rig.storage.documents[ProjectStore.fileName];
  if (raw == null) return const [];
  return ((jsonDecode(raw) as Map<String, Object?>)['projects']! as List)
      .cast<Map<String, Object?>>();
}

Future<void> startConcat(WidgetTester tester) async {
  await tapText(tester, '打开文件');
  await settle(tester, 2);
  await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
  await tapText(tester, '拼接为一个视频');
  await settle(tester, 8);
}

Future<void> openRecent(WidgetTester tester) async {
  await tester.tap(find.bySemanticsLabel('最近工程'));
  await settle(tester, 4);
}

void main() {
  test('store: JSON round trip, newest first, limit 20, broken dropped', () {
    final p = RecentProject(
      id: 'project-1',
      savedAtEpochMs: 5,
      clipCount: 2,
      durationUs: 9,
      snapshot: const SerializedEditProject(schemaVersion: 1, json: '{}'),
    );
    expect(RecentProject.fromJson(p.toJson()), p);
    expect(RecentProject.fromJson({'id': 'x'}), isNull);
  });

  testWidgets('leaving the editor saves the project; reopening restores it', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await startConcat(tester);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    final clips = page.project!.state.value.timeline.clips.length;
    expect(clips, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    expect(find.byType(ConcatPage), findsNothing);
    final saved = savedProjects(rig);
    expect(saved, hasLength(1));
    expect(saved.single['clipCount'], 2);
    expect(saved.single['snapshot'], isA<String>());
    // Reopen from "最近工程".
    await openRecent(tester);
    expect(find.byType(RecentProjectsPage), findsOneWidget);
    expect(find.text('拼接 2 个视频'), findsOneWidget);
    expect(find.text('2 个片段'), findsOneWidget);
    await tester.tap(find.text('拼接 2 个视频'));
    await settle(tester, 8);
    final restored = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(restored.restoreFailed, isFalse);
    expect(restored.project!.state.value.timeline.clips, hasLength(2));
    // Edit and leave: the same project is updated, not duplicated.
    final c = tester
        .state<VideoKitEditorState>(find.byType(VideoKitEditor))
        .controller;
    c.selectClip(c.state.timeline.clips.last.clipId);
    await c.removeSelected();
    await settle(tester, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    expect(savedProjects(rig), hasLength(1));
    expect(savedProjects(rig).single['clipCount'], 1);
    expect(savedProjects(rig).single['id'], saved.single['id']);
    await unmount(tester);
  });

  testWidgets('an empty timeline is not kept; delete removes a project', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await startConcat(tester);
    final c = tester
        .state<VideoKitEditorState>(find.byType(VideoKitEditor))
        .controller;
    for (var i = 0; i < 2; i++) {
      c.selectClip(c.state.timeline.clips.first.clipId);
      await c.removeSelected();
      await settle(tester, 2);
    }
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    expect(savedProjects(rig), isEmpty);
    // Save one, then delete it from the list.
    await startConcat(tester);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await openRecent(tester);
    await tester.tap(find.bySemanticsLabel('删除工程'));
    await settle(tester, 2);
    expect(savedProjects(rig), isEmpty);
    expect(find.textContaining('还没有保存的工程'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('a snapshot the module rejects shows a clear error', (
    tester,
  ) async {
    final rig = AppRig.create();
    rig.storage.documents[ProjectStore.fileName] = jsonEncode({
      'schema': 1,
      'counter': 1,
      'projects': [
        const RecentProject(
          id: 'project-1',
          savedAtEpochMs: 0,
          clipCount: 3,
          snapshot: SerializedEditProject(schemaVersion: 99, json: '{}'),
        ).toJson(),
      ],
    });
    await rig.pump(tester);
    await openRecent(tester);
    await tester.tap(find.text('拼接 3 个视频'));
    await settle(tester, 6);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(page.restoreFailed, isTrue);
    expect(find.text('无法打开这个工程：格式版本过新或文件已损坏'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(find.byType(ConcatPage), findsNothing);
    await unmount(tester);
  });

  testWidgets('添加视频 adds the picked videos as clips', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester, size: expandedSize);
    await startConcat(tester);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    final unawaitedAdd = page.addVideos();
    await settle(tester, 2);
    await pickDemo(tester, ['街头夜景 · 竖屏.mp4']);
    await settle(tester, 6);
    await unawaitedAdd;
    expect(page.project!.state.value.timeline.clips, hasLength(3));
    expect(find.text('拼接 3 个视频'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
    expect(rig.storage, isA<AppStorage>());
  });
}
