// TEST-R2 regressions on the player component: R2-05 (drag right after the
// controls appear), R2-04 (und track title).
import 'package:flutter/gestures.dart' show kTouchSlop;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
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

  testWidgets('R2-05: dragging the bar while the controls are hidden lands '
      'under the finger and shows them', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    Offset at(double f) => Offset(bar.left + bar.width * f, bar.center.dy);
    final g = await tester.startGesture(at(0.10));
    for (var i = 1; i <= 16; i++) {
      await g.moveTo(at(0.10 + 0.40 * i / 16));
      await tester.pump(const Duration(milliseconds: 16));
    }
    expect(rig.session.controlsVisible.last, isTrue, reason: 'shown on drag');
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    final d = rig.session.state.value.durationUs!;
    expect(rig.session.committedSeeks.last.positionUs / d, closeTo(0.5, 0.01));
  });

  testWidgets('R2-05: a tap on the hidden bar only shows the controls', (
    tester,
  ) async {
    final rig = await hiddenWhilePlaying(tester);
    final seeks = rig.session.committedSeeks.length;
    final bar = tester.getRect(find.byType(VkSeekBar));
    await tester.tapAt(Offset(bar.left + bar.width * 0.8, bar.center.dy));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.controlsVisible.last, isTrue);
    expect(rig.session.committedSeeks, hasLength(seeks), reason: 'no seek');
    // Other hidden controls stay untouchable: the play key is not hit.
    expect(rig.session.commands.whereType<Pause>(), isEmpty);
  });

  testWidgets('R3-04: a slow tap with a little jitter on the hidden bar '
      'still only shows the controls', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final seeks = rig.session.committedSeeks.length;
    final bar = tester.getRect(find.byType(VkSeekBar));
    for (final f in [0.2, 0.5, 0.8]) {
      // Hidden again before each tap.
      tester
          .state<VideoKitPlayerState>(find.byType(VideoKitPlayer))
          .hideControls();
      await tester.pump();
      final at = Offset(bar.left + bar.width * f, bar.center.dy);
      final g = await tester.startGesture(at);
      await tester.pump(const Duration(milliseconds: 80));
      await g.moveBy(const Offset(3, 1)); // below the touch slop
      await tester.pump(const Duration(milliseconds: 80));
      await g.up();
      await rig.advance(tester, const Duration(milliseconds: 100));
      expect(rig.session.controlsVisible.last, isTrue);
    }
    expect(rig.session.committedSeeks, hasLength(seeks), reason: 'no seek');
  });

  testWidgets('R3-04: a drag past the touch slop on the hidden bar seeks to '
      'the finger', (tester) async {
    final rig = await hiddenWhilePlaying(tester);
    final bar = tester.getRect(find.byType(VkSeekBar));
    final g = await tester.startGesture(
      Offset(bar.left + bar.width * 0.3, bar.center.dy),
    );
    await tester.pump(const Duration(milliseconds: 16));
    await g.moveBy(Offset(kTouchSlop * 3, 0));
    await tester.pump(const Duration(milliseconds: 16));
    await g.up();
    await rig.advance(tester, const Duration(milliseconds: 300));
    final d = rig.session.state.value.durationUs!;
    final expected = (bar.width * 0.3 + kTouchSlop * 3) / bar.width;
    expect(
      rig.session.committedSeeks.last.positionUs / d,
      closeTo(expected, 0.02),
    );
  });

  test('R2-04: und / empty / mul titles become "音轨 N"', () {
    final s = VkStrings.forLocale(const Locale('zh'));
    String name(String? lang, {String? label, bool audio = true}) =>
        TrackSettingsSheet.trackName(
          s,
          TrackInfo(id: 't', language: lang, label: label),
          0,
          audio: audio,
        );
    expect(name('und'), '音轨 1');
    expect(name('UND'), '音轨 1');
    expect(name(''), '音轨 1');
    expect(name(null), '音轨 1');
    expect(name('mul'), '音轨 1');
    expect(name('und', label: 'und'), '音轨 1');
    expect(name('en'), 'en');
    expect(name('und', label: 'Director'), 'Director');
    expect(name('und', audio: false), '轨道 1', reason: 'subtitles');
    final detail = vkTrackDetail(
      s,
      const TrackInfo(id: 't', language: 'und', codec: 'audio/mp4a-latm'),
    );
    expect(detail, 'AAC', reason: 'codec stays as the subtitle');
  });
}
