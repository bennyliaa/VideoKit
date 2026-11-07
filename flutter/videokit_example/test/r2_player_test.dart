// TEST-R2 regressions on the player component: R2-05 (drag right after the
// controls appear), R2-04 (und track title).
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
