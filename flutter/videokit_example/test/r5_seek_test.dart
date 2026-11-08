// TEST-R5 R5-01a: the release of a seek-bar drag commits one frame-exact
// seek at the release point (14 §5), never lost to the preview throttle.
// R5-01b: the auto-hide timer pauses while a finger is on the player and
// restarts on release, also when the controls tree changes mid-drag.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<PlayerRig> playing(WidgetTester tester, {Size? size}) async {
    setViewSize(tester, size ?? compactSize);
    final rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(testApp(demoPlayer(rig.session)));
    await rig.advance(tester, const Duration(seconds: 1));
    await tester.tap(find.bySemanticsLabel('播放'));
    await rig.advance(tester, const Duration(milliseconds: 500));
    return rig;
  }

  testWidgets('R5-01a: a slow drag ends with one EXACT seek at the release '
      'point; no preview after it', (tester) async {
    final rig = await playing(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final before = rig.session.commands.length;
    final g = await tester.startGesture(at(0.1));
    for (var i = 1; i <= 40; i++) {
      await g.moveTo(at(0.1 + 0.6 * i / 40));
      // Faster than the preview interval: previews are throttled.
      await rig.advance(tester, const Duration(milliseconds: 30));
    }
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 500));
    final seeks = rig.session.commands
        .skip(before)
        .whereType<SeekTo>()
        .toList();
    expect(seeks.where((s) => s.mode == SeekMode.preview), isNotEmpty);
    final committed = seeks.where((s) => s.mode != SeekMode.preview).toList();
    expect(committed, hasLength(1), reason: 'one final seek');
    expect(committed.single.mode, SeekMode.exact);
    expect(
      identical(seeks.last, committed.single),
      isTrue,
      reason: 'no trailing preview after the release',
    );
    final d = rig.session.state.value.durationUs!;
    expect(committed.single.positionUs / d, closeTo(0.7, 0.01));
  });

  testWidgets('R5-01a: a tap on the visible bar commits an EXACT seek', (
    tester,
  ) async {
    final rig = await playing(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    await tester.tapAt(Offset(bar.left + bar.width * 0.4, bar.center.dy));
    await rig.advance(tester, const Duration(milliseconds: 200));
    final last = rig.session.committedSeeks.last;
    expect(last.mode, SeekMode.exact);
    final d = rig.session.state.value.durationUs!;
    expect(last.positionUs / d, closeTo(0.4, 0.01));
  });

  testWidgets('R5-01b: holding a drag for 8 s keeps the controls; the hide '
      'timer restarts on release', (tester) async {
    final rig = await playing(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.2));
    for (var i = 1; i <= 16; i++) {
      await g.moveTo(at(0.2 + 0.01 * i));
      await rig.advance(tester, const Duration(milliseconds: 500));
    }
    expect(rig.session.controlsVisible.last, isTrue, reason: 'after 8 s');
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    await tester.pump(const Duration(seconds: 2));
    expect(rig.session.controlsVisible.last, isTrue, reason: 'full delay');
    await tester.pump(const Duration(seconds: 2));
    expect(rig.session.controlsVisible.last, isFalse, reason: 'hidden later');
  });

  testWidgets('R5-01b: the controls tree changing mid-drag (rotation) keeps '
      'the drag and the controls', (tester) async {
    final rig = await playing(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.2));
    for (var i = 1; i <= 4; i++) {
      await g.moveTo(at(0.2 + 0.05 * i));
      await tester.pump(const Duration(milliseconds: 16));
    }
    setViewSize(tester, const Size(780, 360));
    await tester.pump();
    for (var i = 0; i < 10; i++) {
      await rig.advance(tester, const Duration(milliseconds: 500));
    }
    expect(rig.session.controlsVisible.last, isTrue);
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    expect(tester.takeException(), isNull);
    expect(rig.session.committedSeeks.last.mode, SeekMode.exact);
  });
}
