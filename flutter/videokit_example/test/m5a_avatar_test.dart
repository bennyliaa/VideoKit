// M5A-A1 (REQ-ED-07, 04A E6 5): the "头像" style in the mask panel. The
// host's onRequestAvatar opens its own pages (here: the demo host's
// built-in sheet); without it the entry is hidden.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<void> frames(WidgetTester tester, [int n = 4]) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  testWidgets('choose "头像": the host sheet, then size and rotation', (
    tester,
  ) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(const EditDemoPage()));
    await frames(tester, 15);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await frames(tester);
    unawaited(e.maskEditor!.addManualMask());
    await frames(tester);
    final c = e.controller;
    final maskId = c.selectedMaskId!;
    expect(find.text('头像'), findsOneWidget, reason: 'third style');
    await tester.tap(find.text('头像'));
    await frames(tester);
    expect(find.text('选择内置头像（示例宿主）'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('内置头像 2'));
    await frames(tester);
    var m = c.state.maskById(maskId)!;
    expect(m.style, MaskStyle.image);
    expect(m.avatar?.avatarToken, 'builtin:2');
    expect(find.text('我的头像'), findsOneWidget);
    expect(find.text('点按更换'), findsOneWidget);
    expect(find.text('大小'), findsOneWidget);
    expect(find.text('随头部转动'), findsOneWidget);
    expect(find.text('强度'), findsNothing, reason: 'replaced by 大小');
    // The avatar is drawn in the box on the preview.
    expect(
      find.descendant(
        of: find.byType(MaskOverlay),
        matching: find.byType(Image),
      ),
      findsOneWidget,
    );
    await tester.tap(find.bySemanticsLabel('随头部转动'));
    await frames(tester);
    m = c.state.maskById(maskId)!;
    expect(m.avatar?.followRotation, isFalse);
    // "更换头像" keeps the rotation setting.
    await tester.tap(find.text('我的头像'));
    await frames(tester);
    await tester.tap(find.bySemanticsLabel('内置头像 5'));
    await frames(tester);
    m = c.state.maskById(maskId)!;
    expect(m.avatar?.avatarToken, 'builtin:5');
    expect(m.avatar?.followRotation, isFalse);
    expect(tester.takeException(), isNull);
    await unmount(tester);
  });

  testWidgets('cancelling the host sheet leaves the style as it was', (
    tester,
  ) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(const EditDemoPage()));
    await frames(tester, 15);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await frames(tester);
    unawaited(e.maskEditor!.addManualMask());
    await frames(tester);
    await tester.tap(find.text('头像'));
    await frames(tester);
    await tester.tapAt(const Offset(10, 10)); // outside the sheet
    await frames(tester);
    final m = e.controller.state.maskById(e.controller.selectedMaskId!)!;
    expect(m.style, MaskStyle.mosaic);
    expect(m.avatar, isNull);
    await unmount(tester);
  });

  testWidgets('without onRequestAvatar the "头像" entry is hidden', (
    tester,
  ) async {
    setViewSize(tester, expandedSize);
    final kit = FakeVideoKit();
    final p = (await tester.runAsync(() async {
      final p = await kit.createEditProject(EditProjectConfig());
      final add = p.addSource(
        const VideoKitMediaSource(
          mediaToken: 'v',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef('normal'),
        ),
      );
      await kit.clock.advance(const Duration(seconds: 1));
      final src = await add;
      await p.apply(AddClip(src.sourceId, 0, 10000000));
      return p;
    }))!;
    await tester.pumpWidget(
      testApp(
        VideoKitEditor(
          project: p,
          sink: const VideoKitOutputSink(sinkRef: 'demo:none'),
          pictureBuilder: (context, session) =>
              DemoSessionPicture(session: session),
        ),
      ),
    );
    await frames(tester, 6);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await frames(tester);
    unawaited(e.maskEditor!.addManualMask());
    await frames(tester);
    expect(find.text('马赛克'), findsWidgets);
    expect(find.text('头像'), findsNothing);
    await unmount(tester);
  });
}
