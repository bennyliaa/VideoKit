// TEST-R4 layout: R4-03 / R3-05 (200 % matrix of the multi-view: the
// actions stay reachable, badges never overlap the audio control), R4-04
// (export success page as design page 21), J8 (space to free rounded up to
// 10 MB).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_example/multiview/multi_view_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<void> frames(WidgetTester tester, [int n = 12]) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  group('R4-03: multi-view at 200 %', () {
    for (final (name, size) in [
      ('compact', compactSize),
      ('expanded', expandedSize),
    ]) {
      for (final count in [4, 9, 12]) {
        testWidgets('$name, $count slots: "更多" holds the actions, nothing '
            'overlaps', (tester) async {
          setViewSize(tester, size);
          final key = GlobalKey<MultiViewDemoPageState>();
          await tester.pumpWidget(
            testApp(
              MultiViewDemoPage(key: key, initialCount: count),
              textScale: 2,
            ),
          );
          await frames(tester);
          expect(tester.takeException(), isNull);
          // Bottom bar actions moved to the top bar's "更多".
          expect(find.widgetWithText(VkButton, '添加媒体'), findsNothing);
          final more = find.bySemanticsLabel('更多');
          expect(more, findsOneWidget);
          final screen = Offset.zero & size;
          expect(screen.contains(tester.getCenter(more)), isTrue);
          // Badges: never over the audio control of the same slot.
          for (final slot in tester.widgetList<VideoKitSlot>(
            find.byType(VideoKitSlot),
          )) {
            final inSlot = find.byWidget(slot);
            final audio = find.descendant(
              of: inSlot,
              matching: find.byType(VkIconButton),
            );
            final badges = find.descendant(
              of: inSlot,
              matching: find.textContaining(RegExp('低清|图片|动图')),
            );
            for (final a in audio.evaluate()) {
              final ar = tester.getRect(find.byWidget(a.widget));
              for (final b in badges.evaluate()) {
                final br = tester.getRect(find.byWidget(b.widget));
                expect(
                  ar.overlaps(br),
                  isFalse,
                  reason: 'slot ${slot.index}: badge over the audio control',
                );
              }
            }
          }
          // 9 slots: the last video plays at low resolution (at 12 it is
          // over the demo decoder budget and shows a placeholder instead).
          if (count == 9) {
            // R5-03: the text shows where it fits (tablet); a cell too
            // narrow for it (360 px phone at 200 %) keeps the icon, and the
            // slot's spoken value still says "已降为低分辨率".
            if (size == expandedSize) {
              expect(find.text('低清'), findsWidgets, reason: 'R5-03 text');
            } else {
              expect(
                find.text('低清').evaluate().isNotEmpty ||
                    find
                        .byIcon(Icons.warning_amber_rounded)
                        .evaluate()
                        .isNotEmpty,
                isTrue,
                reason: 'R5-03 text or icon',
              );
            }
            expect(find.text('已降为低分辨率'), findsNothing);
          }
          // TEST-R5 R5-02: the unsupported slot's "移除" is a labelled icon
          // button inside its slot, never cut off.
          if (count >= 4) {
            final remove = find.bySemanticsLabel('移除');
            expect(remove, findsOneWidget);
            final slotRect = tester.getRect(
              find
                  .ancestor(of: remove, matching: find.byType(VideoKitSlot))
                  .first,
            );
            final r = tester.getRect(remove);
            expect(
              slotRect.contains(r.topLeft) && slotRect.contains(r.bottomRight),
              isTrue,
              reason: 'remove inside its slot',
            );
          }
          // "添加媒体" is reachable from "更多".
          await tester.tap(more);
          await frames(tester, 2);
          final add = find.text('添加媒体');
          expect(add, findsOneWidget);
          final before = key.currentState!.slots.length;
          await tester.tap(add);
          await frames(tester, 4);
          expect(
            key.currentState!.slots.length,
            count < VideoKitSlotGrid.maxSlots ? before + 1 : before,
          );
          expect(tester.takeException(), isNull);
          await unmount(tester);
        });
      }
    }

    testWidgets('normal text keeps the bottom bar (design page 14)', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      await tester.pumpWidget(testApp(const MultiViewDemoPage()));
      await frames(tester);
      expect(find.widgetWithText(VkButton, '添加媒体'), findsOneWidget);
      expect(find.text('点按画面切换声音来源，同一时间只有一路发声'), findsOneWidget);
      expect(find.text('4 / 12'), findsOneWidget);
      await unmount(tester);
    });
  });

  testWidgets('R4-04: the export success page follows design page 21', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    await tester.pumpWidget(testApp(const EditDemoPage()));
    await frames(tester, 15);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    final c = e.controller;
    e.openExport();
    await frames(tester, 4);
    // Scroll the presets view down first: the result must not inherit it.
    await tester.drag(
      find.byType(SingleChildScrollView).last,
      const Offset(0, -400),
    );
    await frames(tester, 2);
    await tester.tap(find.text('开始导出'), warnIfMissed: false);
    for (var i = 0; i < 120 && c.state.phase != EditPhase.completed; i++) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await frames(tester, 2);
    expect(find.text('导出完成'), findsOneWidget);
    for (final label in ['容器 / 编码', '分辨率', '时长', '大小', '来源', '警告']) {
      expect(find.text(label), findsOneWidget, reason: label);
    }
    expect(find.textContaining('· 横屏'), findsOneWidget);
    expect(find.textContaining(RegExp(r'^\d+ 个视频$')), findsOneWidget);
    expect(find.widgetWithText(VkButton, '完成'), findsOneWidget);
    expect(find.widgetWithText(VkButton, '返回编辑'), findsNothing);
    // The success icon is on the first screen (scroll reset, R4-04).
    final icon = find.byIcon(
      VkTheme.of(tester.element(find.text('导出完成'))).icons.check,
    );
    expect(icon, findsWidgets);
    expect(tester.getRect(icon.first).top, greaterThanOrEqualTo(0));
    expect(
      tester.getRect(icon.first).top,
      lessThan(tester.getRect(find.text('导出完成')).top),
    );
    await tester.tap(find.widgetWithText(VkButton, '完成'));
    await frames(tester, 2);
    expect(e.controller.mode, isNot(EditorMode.export));
    await unmount(tester);
  });

  test('J8: the space to free rounds up to 10 MB', () {
    VideoKitStableError err(String? bytes) => VideoKitStableError(
      code: ErrorCode.outputSpaceInsufficient,
      stage: ErrorStage.sink,
      params: {requiredBytesParam: ?bytes},
    );
    expect(vkSpaceToFree(err('1')), 10000000);
    expect(vkSpaceToFree(err('10000000')), 10000000);
    expect(vkSpaceToFree(err('10000001')), 20000000);
    expect(vkSpaceToFree(err('0')), isNull);
    expect(vkSpaceToFree(err('x')), isNull);
    expect(vkSpaceToFree(err(null)), isNull);
    expect(
      vkSpaceToFree(
        const VideoKitStableError(
          code: ErrorCode.exportFailed,
          stage: ErrorStage.export,
          params: {'requiredBytes': '5'},
        ),
      ),
      isNull,
    );
  });
}
