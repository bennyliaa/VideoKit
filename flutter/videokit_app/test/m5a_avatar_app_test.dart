// M5A-A1 (REQ-ED-07, 04A E5/E6): the App's own avatar pages ("选择头像",
// "调整头像") as the host of the editor's "头像" style; avatars stored in
// the App and read by the Kit through openAvatar.
import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/app_scope.dart';
import 'package:videokit_app/avatar/avatar_adjust_page.dart';
import 'package:videokit_app/avatar/avatar_pick_page.dart';
import 'package:videokit_app/avatar/avatar_store.dart';
import 'package:videokit_app/history/history_entry.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'm4_app_test.dart' show startConcat;
import 'support.dart';

void main() {
  Future<(AppRig, VideoKitEditorState)> editorWithMask(
    WidgetTester tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester, size: expandedSize);
    await startConcat(tester);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await settle(tester, 2);
    unawaited(e.maskEditor!.addManualMask());
    await settle(tester, 2);
    return (rig, e);
  }

  testWidgets('"头像" opens 选择头像; a built-in avatar is applied', (
    tester,
  ) async {
    final (_, e) = await editorWithMask(tester);
    await tester.tap(find.text('头像'));
    await settle(tester, 4);
    expect(find.byType(AvatarPickPage), findsOneWidget);
    expect(find.text('选择头像'), findsOneWidget);
    expect(find.text('用你的照片'), findsOneWidget);
    expect(find.text('从相册选择'), findsOneWidget);
    expect(find.text('拍一张'), findsOneWidget, reason: 'demo picker');
    expect(find.text('内置头像'), findsOneWidget);
    expect(find.textContaining('照片只在本机处理，不会上传。'), findsOneWidget);
    expect(find.text('最近使用'), findsNothing, reason: 'nothing saved yet');
    await tester.tap(find.bySemanticsLabel('内置头像 3'));
    await settle(tester, 4);
    expect(find.byType(AvatarPickPage), findsNothing);
    final m = e.controller.state.maskById(e.controller.selectedMaskId!)!;
    expect((m.style, m.avatar?.avatarToken), (MaskStyle.image, 'builtin:3'));
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });

  testWidgets('拍一张 → 调整头像 → erase → 使用此头像: saved in the App, '
      'readable through openAvatar, listed under 最近使用', (tester) async {
    final (rig, e) = await editorWithMask(tester);
    await tester.tap(find.text('头像'));
    await settle(tester, 4);
    await tester.tap(find.text('拍一张'));
    await settle(tester, 8); // the Fake cut-out takes 0.8 s
    final adjust = tester.state<AvatarAdjustPageState>(
      find.byType(AvatarAdjustPage),
    );
    expect(adjust.avatar, isNotNull);
    expect(find.text('调整头像'), findsOneWidget);
    expect(find.text('已自动去除背景'), findsOneWidget);
    expect(find.text('原图'), findsOneWidget);
    for (final label in ['缩放', '移动', '擦除', '恢复', '笔刷大小', '边缘柔化']) {
      expect(find.text(label), findsWidgets, reason: label);
    }
    expect(find.text('裁到头部（含头发）'), findsOneWidget);
    expect(find.text('重新识别'), findsOneWidget);
    final before = adjust.avatar!.png;
    await tester.drag(
      find.bySemanticsLabel('抠图结果'),
      const Offset(40, 0),
    );
    await settle(tester, 2);
    expect(adjust.avatar!.png, isNot(before), reason: 'erased');
    // "移动" changes the offset kept with the mask.
    await tester.tap(find.text('移动'));
    await tester.pump();
    await tester.drag(find.bySemanticsLabel('抠图结果'), const Offset(20, 0));
    await tester.pump();
    expect(adjust.offset.dx, greaterThan(0));
    await tester.tap(find.text('使用此头像'));
    await settle(tester, 4);
    expect(find.byType(AvatarAdjustPage), findsNothing);
    expect(find.byType(AvatarPickPage), findsNothing);
    final m = e.controller.state.maskById(e.controller.selectedMaskId!)!;
    expect(m.style, MaskStyle.image);
    expect(m.avatar!.avatarToken, startsWith(AvatarStore.tokenPrefix));
    expect(m.avatar!.offsetX, greaterThan(0));
    // Stored in the App (04A E5 1) and read back by the Kit (E6 2).
    final index =
        jsonDecode(rig.storage.documents[AvatarStore.fileName]!)
            as Map<String, Object?>;
    expect((index['avatars']! as List), hasLength(1));
    final factory = await rig.backend.hosts.openAvatar(m.avatar!.avatarToken);
    expect(factory, isNotNull);
    final handle = await factory!.open(OpenPurpose.probe);
    final buf = Uint8List(4);
    expect(await handle.readAt(0, buf, 0, 4), 4);
    expect(buf.sublist(1, 4), 'PNG'.codeUnits);
    await handle.close();
    expect(await rig.backend.hosts.openAvatar('app-avatar-404'), isNull);
    // Next time it is under "最近使用".
    await tester.tap(find.text('我的头像'));
    await settle(tester, 4);
    expect(find.text('最近使用'), findsOneWidget);
    expect(find.bySemanticsLabel('最近使用的头像 1'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });

  testWidgets('no face: the adjust page explains and offers another photo', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester, size: expandedSize);
    final nav = tester.state<NavigatorState>(find.byType(Navigator).first);
    final ctx = tester.element(find.byType(Navigator).first);
    final scope = AppScope.of(ctx);
    const entry = HistoryEntry(
      id: 'avatar-source',
      uri: 'demo:face',
      displayName: 'face.jpg',
      kind: MediaKind.imageStatic,
      lastOpenedAtEpochMs: 0,
    );
    unawaited(
      nav.push(
        MaterialPageRoute<void>(
          builder: (_) => AvatarAdjustPage(
            tools: scope.backend.videoKit as VideoKitAvatarTools,
            entry: entry,
            source: const VideoKitMediaSource(
              mediaToken: 'face',
              mediaKind: MediaKind.imageStatic,
              sourceRef: DemoSourceRef(FakeAvatarTools.noFace),
            ),
          ),
        ),
      ),
    );
    await settle(tester, 8);
    expect(find.text('没有识别到人脸，请换一张照片'), findsOneWidget);
    expect(find.text('换一张照片'), findsOneWidget);
    expect(
      tester.widget<VkButton>(find.widgetWithText(VkButton, '使用此头像')).onPressed,
      isNull,
    );
    await tester.tap(find.text('换一张照片'));
    await settle(tester, 2);
    expect(find.byType(AvatarAdjustPage), findsNothing);
    await unmount(tester);
  });

  test('AvatarStore keeps at most 12 and drops the oldest file', () async {
    final storage = MemoryAppStorage();
    final store = AvatarStore(storage: storage);
    final tokens = [
      for (var i = 0; i < 13; i++) await store.save(Uint8List.fromList([i])),
    ];
    expect(store.recent, hasLength(AvatarStore.limit));
    expect(store.recent.first.token, tokens.last);
    expect(await store.bytes(tokens.first), isNull, reason: 'dropped');
    expect(storage.deleted, hasLength(1));
    final again = AvatarStore(storage: storage);
    await again.load();
    expect(again.recent.map((a) => a.token), store.recent.map((a) => a.token));
    await again.touch(tokens[5]);
    expect(again.recent.first.token, tokens[5]);
  });
}
