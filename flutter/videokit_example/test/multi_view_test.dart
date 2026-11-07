import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/multiview/multi_view_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  final key = GlobalKey<MultiViewDemoPageState>();

  Future<void> pumpPage(
    WidgetTester tester, {
    Size size = compactSize,
    int? count,
  }) async {
    setViewSize(tester, size);
    await tester.pumpWidget(
      testApp(MultiViewDemoPage(key: key, initialCount: count)),
    );
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> settle(WidgetTester tester) async {
    for (var i = 0; i < 4; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  List<bool> audio() => [
    for (final s in key.currentState!.slots) s.session.state.value.activeAudio,
  ];

  testWidgets('phone: 4 slots, single audio source moves; mute all', (
    tester,
  ) async {
    await pumpPage(tester);
    expect(find.byType(VideoKitSlot), findsNWidgets(4));
    expect(audio(), [true, false, false, false]);
    expect(find.text('发声'), findsOneWidget);
    // Slot 2 (video) asks for audio through its muted badge.
    await tester.tap(find.bySemanticsLabel('设为发声画面').first);
    await settle(tester);
    expect(audio(), [false, true, false, false]);
    expect(audio().where((a) => a), hasLength(1), reason: 'only one');
    await tester.tap(find.text('全部静音'));
    await settle(tester);
    expect(audio(), everyElement(isFalse));
    expect(find.text('发声'), findsNothing);
    await unmount(tester);
  });

  testWidgets('single-slot error: only that slot; remove it', (tester) async {
    await pumpPage(tester);
    expect(find.text('仅此格受影响'), findsOneWidget);
    expect(find.text('图片'), findsOneWidget, reason: 'image slot badge');
    final others = [
      for (final s in key.currentState!.slots)
        if (s.kind != DemoSlotKind.unsupported) s.session.state.value.phase,
    ];
    expect(others, isNot(contains(SessionPhase.errorFatal)));
    await tester.tap(find.text('移除'));
    await settle(tester);
    expect(find.byType(VideoKitSlot), findsNWidgets(3));
    expect(find.text('仅此格受影响'), findsNothing);
    await unmount(tester);
  });

  testWidgets('tablet: 3×3 by default; over budget pauses with a notice', (
    tester,
  ) async {
    await pumpPage(tester, size: expandedSize);
    final state = key.currentState!;
    expect(state.slots, hasLength(9));
    final first = tester.getTopLeft(find.byType(VideoKitSlot).at(0));
    final fourth = tester.getTopLeft(find.byType(VideoKitSlot).at(3));
    expect(fourth.dx, first.dx, reason: '3 columns: slot 4 starts row 2');
    // 9 slots hold 6 videos (= the suggested count); a 10th slot adds a
    // 7th video, so the host pauses the oldest one.
    expect(state.pausedCount, 0);
    expect(find.textContaining('当前设备建议'), findsNothing);
    await tester.tap(find.text('添加媒体'));
    await settle(tester);
    expect(state.pausedCount, 1);
    expect(find.text('已暂停 · 资源不足'), findsOneWidget);
    expect(
      state.slots.where(
        (s) => s.pausedForResources && s.session.sessionId == state.activeAudio,
      ),
      isEmpty,
      reason: 'the audio slot is never paused',
    );
    expect(find.textContaining('当前设备建议同时播放 6 路视频'), findsOneWidget);
    expect(find.text('已降为低分辨率'), findsOneWidget);
    // Tapping the paused slot resumes it and pauses another instead.
    final paused = state.slots.firstWhere((s) => s.pausedForResources);
    await tester.tap(find.text('已暂停 · 资源不足'));
    await settle(tester);
    expect(paused.pausedForResources, isFalse);
    expect(paused.session.state.value.phase, SessionPhase.playing);
    expect(state.pausedCount, 1);
    // Fill to 12: the add button disables.
    for (var i = 0; i < 2; i++) {
      await tester.tap(find.text('添加媒体'));
      await settle(tester);
    }
    expect(state.slots, hasLength(12));
    expect(find.byType(VideoKitSlot), findsNWidgets(12));
    await tester.tap(find.text('添加媒体'));
    await settle(tester);
    expect(state.slots, hasLength(12));
    await unmount(tester);
  });

  testWidgets('layout picker switches the grid shape', (tester) async {
    await pumpPage(tester, size: expandedSize, count: 4);
    final a = tester.getTopLeft(find.byType(VideoKitSlot).at(0));
    final c = tester.getTopLeft(find.byType(VideoKitSlot).at(2));
    expect(c.dx, a.dx, reason: 'auto, 4 slots → 2 columns');
    await tester.tap(find.text('4×3'));
    await settle(tester);
    final c2 = tester.getTopLeft(find.byType(VideoKitSlot).at(2));
    expect(c2.dy, a.dy, reason: '4 columns: slot 3 on the first row');
    await unmount(tester);
  });

  testWidgets('R1-12b: phone 3×3 paused slots show icon + short text', (
    tester,
  ) async {
    await pumpPage(tester, size: const Size(392, 780), count: 12);
    await tester.tap(find.text('3×3'));
    await settle(tester);
    expect(key.currentState!.pausedCount, greaterThan(0));
    expect(find.text('已暂停 · 资源不足'), findsNothing);
    final short = find.text('已暂停');
    expect(short, findsWidgets);
    for (final e in short.evaluate()) {
      final text = e.renderObject! as RenderBox;
      final textRect = text.localToGlobal(Offset.zero) & text.size;
      final slot = find.ancestor(
        of: find.byWidget(e.widget),
        matching: find.byType(VideoKitSlot),
      );
      final icon = find.descendant(
        of: slot,
        matching: find.byIcon(Icons.pause_rounded),
      );
      final iconRect = tester.getRect(icon.first);
      expect(textRect.overlaps(iconRect), isFalse);
      expect((e.widget as Text).maxLines, 1);
      expect(
        tester
            .getRect(slot)
            .contains(textRect.bottomRight - const Offset(1, 1)),
        isTrue,
      );
    }
    await unmount(tester);
  });
}
