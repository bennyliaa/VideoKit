// 04A E7 (M5A follow-up, committed with M6-A1): the avatar on the preview.
// Q1: no avatar in a LOST / AMBIGUOUS / not-analysed range; a dashed box at
// the last trusted position says "目标丢失". Q9: a full-frame mosaic covers
// the whole picture, so no avatar is drawn over it.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
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

  Finder avatarImage() =>
      find.descendant(of: find.byType(MaskOverlay), matching: find.byType(Image));

  const avatar = MaskAvatar(avatarToken: 'builtin:1');

  testWidgets('Q1: lost range → no avatar, dashed "目标丢失" box', (tester) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      testApp(const EditDemoPage(initialScenario: EditDemoScenario.trackingLost)),
    );
    await frames(tester, 15);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    final c = e.controller;
    e.openMasks(MaskEditorTab.tracking);
    await frames(tester);
    await tester.tap(find.text('检测人脸'));
    await frames(tester);
    await tester.tap(find.bySemanticsLabel('人脸 1').first);
    for (var i = 0; i < 80; i++) {
      await tester.pump(const Duration(milliseconds: 250));
      if (c.state.tracking.values.firstOrNull?.status ==
          TrackingRunStatus.completed) {
        break;
      }
    }
    final maskId = c.state.tracking.keys.single;
    await c.apply(SetMaskAvatar(maskId, avatar));
    await c.apply(SetMaskStyle(maskId, MaskStyle.image, 0.5));
    await frames(tester);

    // Trusted range: the avatar is drawn.
    await c.seek(1000000);
    await frames(tester);
    expect(avatarImage(), findsOneWidget);
    expect(find.text('目标丢失'), findsNothing);

    // Lost range (4–6 s in this scenario): no avatar, dashed box.
    await c.seek(5000000);
    await frames(tester);
    expect(avatarImage(), findsNothing);
    expect(find.text('目标丢失'), findsOneWidget);
    final overlay = tester.widget<MaskOverlay>(find.byType(MaskOverlay));
    final box = overlay.boxes.firstWhere((b) => b.id == maskId);
    expect(box.dashed, isTrue);
    expect(box.content, isNull);
    expect(tester.takeException(), isNull);
    await unmount(tester);
  });

  testWidgets('Q9: under a full-frame mosaic no avatar is drawn', (
    tester,
  ) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(const EditDemoPage()));
    await frames(tester, 15);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    final c = e.controller;
    e.openMasks(MaskEditorTab.manual);
    await frames(tester);
    await e.maskEditor!.addManualMask();
    await frames(tester);
    final head = c.selectedMaskId!;
    await c.apply(SetMaskAvatar(head, avatar));
    await c.apply(SetMaskStyle(head, MaskStyle.image, 0.5));
    await frames(tester);
    expect(avatarImage(), findsOneWidget);

    await e.maskEditor!.addManualMask();
    await frames(tester);
    final whole = c.selectedMaskId!;
    expect(whole, isNot(head));
    await c.apply(
      UpdateMaskKeyframe(
        whole,
        c.playheadUs,
        const MaskRegion(x: 0, y: 0, width: 1, height: 1),
      ),
    );
    await frames(tester);
    expect(vkIsFullFrame(c.state.maskById(whole)!.regionAt(c.playheadUs)), isTrue);
    expect(avatarImage(), findsNothing);
    expect(c.state.maskById(head)!.avatar, avatar, reason: 'kept, only hidden');
    expect(tester.takeException(), isNull);
    await unmount(tester);
  });
}
