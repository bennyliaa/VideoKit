import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/home/home_page.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/pages/image_page.dart';
import 'package:videokit_app/pages/multi_view_page.dart';
import 'package:videokit_app/pages/player_page.dart';
import 'package:videokit_app/picker/media_picker.dart';
import 'package:videokit_app/settings/settings_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

Future<void> pickDemo(WidgetTester tester, List<String> names) async {
  for (final n in names) {
    await tapText(tester, n);
    await tester.pump();
  }
  await tester.tap(find.textContaining('打开 ${names.length} 个'));
  await settle(tester);
}

void main() {
  testWidgets('first use: empty state with one action and the hint', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    expect(find.text('还没有播放记录'), findsOneWidget);
    expect(find.text('也可以从其他应用打开'), findsOneWidget);
    expect(find.text('打开文件'), findsOneWidget);
    expect(find.bySemanticsLabel('网格视图'), findsNothing);
    expect(find.byType(DemoBadge), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('open → play → back saves the snapshot; reopen resumes', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    expect(find.text('选择视频或图片'), findsOneWidget);
    await pickDemo(tester, ['山谷黄昏.mkv']);
    expect(find.byType(PlayerPage), findsOneWidget);
    // Play ~3 s of Fake time.
    await settle(tester, 15);
    final s = tester.state<PlayerPageState>(find.byType(PlayerPage)).session!;
    expect(s.state.value.phase, SessionPhase.playing);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(find.byType(HomePage), findsOneWidget);
    final saved = rig.savedEntries().single;
    expect(saved['displayName'], '山谷黄昏.mkv');
    expect(saved['playbackState'], isNotNull);
    final pos = (saved['lastPositionUs']! as num).toInt();
    expect(pos, greaterThan(1000000));
    expect(find.textContaining('看到 00:0'), findsOneWidget);
    expect(find.textContaining('刚刚'), findsOneWidget);
    // 04A P1/P2: thumbnail captured and media facts recorded.
    final thumb = saved['thumbnailPath']! as String;
    expect(rig.storage.thumbnails.containsKey(thumb), isTrue);
    expect(saved['videoCodec'], 'video/avc');
    expect(
      (saved['playbackState']! as Map<String, Object?>)['looping'],
      isFalse,
      reason: '04A L3: loop setting saved with the snapshot',
    );
    expect(find.text('1080p · H.264'), findsOneWidget);
    // Reopen: bound with the snapshot as initialState.
    await tapText(tester, '山谷黄昏.mkv');
    await settle(tester, 3);
    final s2 = tester.state<PlayerPageState>(find.byType(PlayerPage)).session!;
    expect(s2.state.value.positionUs, greaterThanOrEqualTo(pos));
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(
      rig.storage.deleted,
      contains(thumb),
      reason: 'old thumbnail replaced',
    );
    expect(rig.storage.thumbnails, hasLength(1));
    await unmount(tester);
  });

  testWidgets('image record: image viewer, "上次查看", "图片" badge', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['沙丘.heic']);
    expect(find.byType(ImagePage), findsOneWidget);
    expect(find.byType(VkSeekBar), findsNothing);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(find.text('上次查看 · 刚刚'), findsOneWidget);
    expect(find.text('图片'), findsWidgets);
    await unmount(tester);
  });

  testWidgets('multi-select: choose multi-view or concat; one record each', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '街头夜景 · 竖屏.mp4']);
    expect(find.text('已选择 2 个文件'), findsOneWidget);
    await tapText(tester, '在多画面中打开');
    await settle(tester, 6);
    expect(find.byType(MultiViewPage), findsOneWidget);
    expect(find.byType(VideoKitSlot), findsNWidgets(2));
    expect(find.text('发声'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(rig.savedEntries(), hasLength(2));
    // Concat from a new pick.
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
    await tapText(tester, '拼接为一个视频');
    await settle(tester, 8);
    expect(find.byType(ConcatPage), findsOneWidget);
    final editor = tester.state<VideoKitEditorState>(
      find.byType(VideoKitEditor),
    );
    expect(editor.controller.state.timeline.clips, hasLength(2));
    // Design page 16: phones title the editor "剪辑" (the project name is
    // on tablets: "拼接 2 个视频 · 剪辑").
    expect(find.text('剪辑'), findsWidgets);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(rig.savedEntries(), hasLength(3));
    await unmount(tester);
  });

  testWidgets('export 另存为: cancelled dialog starts nothing, then exports', (
    tester,
  ) async {
    final backend = _SaveAsBackend();
    final rig = AppRig.create(backend: backend);
    await rig.pump(tester, size: expandedSize);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
    await tapText(tester, '拼接为一个视频');
    await settle(tester, 8);
    final editor = tester.state<VideoKitEditorState>(
      find.byType(VideoKitEditor),
    );
    editor.openExport();
    await settle(tester);
    await tapText(tester, '开始导出');
    await settle(tester);
    expect(backend.requests.single, (
      'VideoKit_20261107_200000.mp4',
      'video/mp4',
    ));
    expect(editor.controller.state.phase, isNot(EditPhase.exporting));
    expect(find.text('开始导出'), findsOneWidget);
    await tapText(tester, '开始导出');
    await tester.pump(const Duration(milliseconds: 300));
    expect(backend.requests, hasLength(2));
    expect(editor.controller.state.phase, EditPhase.exporting);
    await unmount(tester);
  });

  testWidgets('moved file: marked 无法打开, 重新选择 relinks and opens', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['旅行合集.mp4']);
    expect(find.byType(PlayerPage), findsNothing);
    expect(find.text('无法打开“旅行合集.mp4”'), findsOneWidget);
    expect(find.text('无法打开'), findsOneWidget);
    expect(find.text('文件已移动或授权失效'), findsOneWidget);
    expect(rig.savedEntries().single['unavailable'], isTrue);
    await tapText(tester, '重新选择');
    await settle(tester, 2);
    await tapText(tester, '旅行合集.mp4');
    await tester.pump();
    await tapText(tester, '选择');
    await settle(tester, 4);
    expect(find.byType(PlayerPage), findsOneWidget);
    expect(rig.savedEntries().single['unavailable'], isFalse);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    await unmount(tester);
  });

  testWidgets('home: filters, grid toggle persisted, more menu', (
    tester,
  ) async {
    final rig = AppRig.create(entries: sampleHistory());
    await rig.pump(tester);
    expect(find.text('看到 01:41 · 2 小时前'), findsOneWidget);
    expect(find.text('看到 01:24 · 昨天'), findsOneWidget);
    expect(find.text('上次查看 · 昨天'), findsOneWidget);
    expect(find.text('看到 08:15 · 3 天前'), findsOneWidget);
    expect(find.text('1080p · H.264'), findsOneWidget);
    expect(find.text('1080×1920 · HEVC'), findsOneWidget);
    expect(find.text('图片 · 4032×3024'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('最多保存 200 条 · 只保存在本机'), 200);
    expect(find.text('最多保存 200 条 · 只保存在本机'), findsOneWidget);
    await tester.drag(find.byType(ListView).first, const Offset(0, 2000));
    await tester.pump();
    await tester.tap(find.widgetWithText(VkPressable, '图片'));
    await tester.pump();
    expect(find.text('沙丘.heic'), findsOneWidget);
    expect(find.text('山谷黄昏.mkv'), findsNothing);
    await tester.tap(find.widgetWithText(VkPressable, '视频'));
    await tester.pump();
    expect(find.text('沙丘.heic'), findsNothing);
    await tester.tap(find.widgetWithText(VkPressable, '全部'));
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('网格视图'));
    await settle(tester, 1);
    expect(find.bySemanticsLabel('列表视图'), findsOneWidget);
    expect(rig.storage.documents['settings.json'], contains('grid'));
    await tester.tap(find.bySemanticsLabel('列表视图'));
    await settle(tester, 1);
    // More → 从头播放 clears the position before opening.
    await tester.tap(find.bySemanticsLabel('更多').first);
    await settle(tester, 2);
    expect(find.text('在多画面中打开'), findsOneWidget);
    await tapText(tester, '从头播放');
    await settle(tester, 3);
    final s = tester.state<PlayerPageState>(find.byType(PlayerPage)).session!;
    expect(s.state.value.positionUs, lessThan(2000000));
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    // More → 删除 releases the permission.
    await tester.tap(find.bySemanticsLabel('更多').last);
    await settle(tester, 2);
    await tapText(tester, '从记录中删除');
    await settle(tester, 2);
    expect(rig.backend.picker.released, isNotEmpty);
    expect(rig.savedEntries(), hasLength(4));
    await unmount(tester);
  });

  testWidgets('settings: record switch, count, clear, theme, licenses', (
    tester,
  ) async {
    final rig = AppRig.create(entries: sampleHistory());
    await rig.pump(tester, size: const Size(360, 1600));
    await tester.tap(find.bySemanticsLabel('设置'));
    await settle(tester, 2);
    expect(find.byType(SettingsPage), findsOneWidget);
    expect(find.text('5 / 200 条'), findsOneWidget);
    expect(find.text('1.0.0'), findsOneWidget);
    expect(find.text('英文版本后续提供'), findsOneWidget);
    await tapText(tester, '浅色');
    await settle(tester, 2);
    expect(
      VkTheme.of(tester.element(find.byType(SettingsPage))).brightness,
      Brightness.light,
    );
    await tester.tap(find.bySemanticsLabel('减少动画'));
    await settle(tester, 1);
    expect(
      rig.storage.documents['settings.json'],
      contains('"reduceMotion":true'),
    );
    await tapText(tester, '清空播放记录');
    await settle(tester, 2);
    expect(find.text('清空播放记录？'), findsOneWidget);
    await tapText(tester, '清空');
    await settle(tester, 2);
    expect(find.text('0 / 200 条'), findsOneWidget);
    expect(rig.storage.deleted, contains('/thumbs/h5.png'));
    await tester.tap(find.bySemanticsLabel('记录播放历史'));
    await settle(tester, 1);
    expect(
      rig.storage.documents['settings.json'],
      contains('"recordHistory":false'),
    );
    await tapText(tester, '开源许可');
    await settle(tester, 4);
    expect(find.byType(LicensePage), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    // History off: opening a file records nothing.
    expect(find.text('播放历史记录已关闭，新的播放不会被记录'), findsOneWidget);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['沙丘.heic']);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(rig.savedEntries(), isEmpty);
    await unmount(tester);
  });

  testWidgets('"用 VideoKit 打开": opens directly, temporary grant noted', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    rig.backend.picker.simulateIncoming(const [
      PickedMedia(
        uri: 'demo:street',
        displayName: '街头夜景 · 竖屏.mp4',
        kind: MediaKind.video,
        persistable: false,
      ),
    ]);
    await settle(tester, 4);
    expect(find.byType(PlayerPage), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    expect(find.text('临时授权，下次可能需要重新选择'), findsOneWidget);
    expect(rig.savedEntries().single['persistable'], isFalse);
    await unmount(tester);
  });
}

/// Demo backend whose first "另存为" is cancelled.
final class _SaveAsBackend extends DemoBackend {
  final List<(String, String)> requests = [];

  @override
  Future<VideoKitOutputSink?> prepareExport({
    required String suggestedName,
    required String mimeType,
  }) async {
    requests.add((suggestedName, mimeType));
    return requests.length == 1 ? null : exportSink;
  }
}
