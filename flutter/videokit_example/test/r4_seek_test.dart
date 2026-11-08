// TEST-R4 R4-01 / R3-04: the seek-bar gesture while the controls are hidden
// is a state machine — down shows the controls, past the touch slop it
// drags to the finger, up commits one seek, and a cancel or a hide during
// the drag also leaves the drag (the progress never freezes).
import 'package:flutter/gestures.dart' show kTouchSlop;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<PlayerRig> hiddenWhilePlaying(WidgetTester tester) async {
    setViewSize(tester, compactSize);
    final rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(testApp(demoPlayer(rig.session)));
    await rig.advance(tester, const Duration(seconds: 1));
    await tester.tap(find.bySemanticsLabel('播放'));
    await rig.advance(tester, const Duration(milliseconds: 500));
    await tester.pump(const Duration(seconds: 2));
    await tester.pump(const Duration(seconds: 2));
    expect(rig.session.controlsVisible.last, isFalse, reason: 'auto-hidden');
    return rig;
  }

  int shownUs(WidgetTester tester) =>
      tester.widget<VkSeekBar>(find.byType(VkSeekBar)).positionUs;

  Future<void> expectProgressMoves(WidgetTester tester, PlayerRig rig) async {
    final before = shownUs(tester);
    await rig.advance(tester, const Duration(seconds: 2));
    expect(
      shownUs(tester),
      greaterThan(before),
      reason: 'the progress follows playback again (not frozen)',
    );
    expect(find.byKey(const ValueKey('vk-seek-preview-frame')), findsNothing);
  }

  testWidgets('R3-04: a tap on the hidden bar shows the controls on the down '
      'and never seeks', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final seeks = rig.session.committedSeeks.length;
    final bar = tester.getRect(find.byType(VkSeekBar));
    for (final f in [0.1, 0.3, 0.5, 0.7, 0.9]) {
      tester
          .state<VideoKitPlayerState>(find.byType(VideoKitPlayer))
          .hideControls();
      await tester.pump();
      final g = await tester.startGesture(
        Offset(bar.left + bar.width * f, bar.center.dy),
      );
      await tester.pump();
      expect(
        rig.session.controlsVisible.last,
        isTrue,
        reason: 'shown when the finger goes down',
      );
      await tester.pump(const Duration(milliseconds: 30));
      await g.up();
      await rig.advance(tester, const Duration(milliseconds: 100));
    }
    expect(rig.session.committedSeeks, hasLength(seeks), reason: 'no seek');
  });

  testWidgets('R4-01: a fast drag on the hidden bar lands under the finger', (
    tester,
  ) async {
    final rig = await hiddenWhilePlaying(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.1));
    for (var i = 1; i <= 4; i++) {
      await g.moveTo(at(0.1 + 0.6 * i / 4));
      await tester.pump(const Duration(milliseconds: 16));
    }
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    final d = rig.session.state.value.durationUs!;
    expect(rig.session.committedSeeks.last.positionUs / d, closeTo(0.7, 0.01));
    await expectProgressMoves(tester, rig);
  });

  testWidgets('R4-01: a slow drag (1.5 s) on the hidden bar lands under the '
      'finger and the progress keeps moving', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.1));
    const steps = 50;
    for (var i = 1; i <= steps; i++) {
      await g.moveTo(at(0.1 + 0.5 * i / steps));
      // Preview seeks and the controls' fade-in run during the drag.
      await rig.advance(tester, const Duration(milliseconds: 30));
    }
    expect(rig.session.controlsVisible.last, isTrue);
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    final d = rig.session.state.value.durationUs!;
    expect(rig.session.committedSeeks.last.positionUs / d, closeTo(0.6, 0.01));
    await expectProgressMoves(tester, rig);
  });

  testWidgets('R4-01: a drag cancelled mid-way leaves the drag', (
    tester,
  ) async {
    final rig = await hiddenWhilePlaying(tester);
    final seeks = rig.session.committedSeeks.length;
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.2));
    for (var i = 1; i <= 10; i++) {
      await g.moveTo(at(0.2 + 0.2 * i / 10));
      await rig.advance(tester, const Duration(milliseconds: 30));
    }
    await g.cancel();
    await rig.advance(tester, const Duration(milliseconds: 300));
    expect(
      rig.session.committedSeeks.length,
      seeks + 1,
      reason: 'one seek where the preview was',
    );
    final d = rig.session.state.value.durationUs!;
    expect(rig.session.committedSeeks.last.positionUs / d, closeTo(0.4, 0.01));
    await expectProgressMoves(tester, rig);
    // The drag blocker is gone: the controls auto-hide again.
    await tester.pump(const Duration(seconds: 2));
    await tester.pump(const Duration(seconds: 2));
    expect(rig.session.controlsVisible.last, isFalse);
  });

  testWidgets('R4-01: the auto-hide delay passing during a drag keeps the '
      'controls and the drag; release then seeks', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.3));
    await tester.pump(const Duration(milliseconds: 16));
    await g.moveBy(Offset(kTouchSlop * 3, 0));
    await tester.pump(const Duration(milliseconds: 16));
    for (var i = 0; i < 10; i++) {
      await rig.advance(tester, const Duration(milliseconds: 500));
    }
    expect(rig.session.controlsVisible.last, isTrue, reason: 'drag blocker');
    await g.moveTo(at(0.8));
    await tester.pump(const Duration(milliseconds: 16));
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    final d = rig.session.state.value.durationUs!;
    expect(rig.session.committedSeeks.last.positionUs / d, closeTo(0.8, 0.01));
    await expectProgressMoves(tester, rig);
  });

  testWidgets('R4-01: the bar hidden or disabled mid-drag leaves the drag', (
    tester,
  ) async {
    for (final hide in [true, false]) {
      final ends = <int>[];
      Widget bar({VoidCallback? tapInstead, bool enabled = true}) => testApp(
        Center(
          child: SizedBox(
            width: 300,
            child: VkSeekBar(
              positionUs: 0,
              durationUs: 300000000,
              onDragUpdate: (_) {},
              onDragEnd: enabled ? ends.add : null,
              onTapInstead: tapInstead,
            ),
          ),
        ),
      );
      await tester.pumpWidget(bar());
      final g = await tester.startGesture(
        tester.getCenter(find.byType(VkSeekBar)),
      );
      for (var i = 0; i < 5; i++) {
        await g.moveBy(const Offset(10, 0));
        await tester.pump(const Duration(milliseconds: 16));
      }
      expect(find.textContaining(':'), findsWidgets, reason: 'bubble');
      await tester.pumpWidget(
        hide ? bar(tapInstead: () {}) : bar(enabled: false),
      );
      await tester.pump();
      expect(ends, hasLength(1), reason: hide ? 'hidden' : 'disabled');
      await g.moveBy(const Offset(10, 0));
      await g.up();
      await tester.pump();
      expect(ends, hasLength(1), reason: 'the rest of the gesture is ignored');
      await tester.pumpWidget(const SizedBox());
    }
  });
}
