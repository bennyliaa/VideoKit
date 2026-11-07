// UI-AUDIT-A2: 04A B1 opening then buffering, J4 unsupported state and
// capability page, J9 large-text list rows, J6 timecodes, J5 image info.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  late PlayerRig rig;

  Future<void> pump(
    WidgetTester tester,
    String scenario, {
    Size size = compactSize,
    double textScale = 1.0,
    ValueChanged<StateAction>? onStateAction,
  }) async {
    setViewSize(tester, size);
    rig = await PlayerRig.create(scenario);
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      testApp(
        demoPlayer(rig.session, onStateAction: onStateAction),
        textScale: textScale,
      ),
    );
    await rig.advance(tester, const Duration(seconds: 1));
  }

  testWidgets('04A B1: opened then buffering shows the spinner, not '
      '"正在打开"', (tester) async {
    await pump(tester, 'openBuffering');
    expect(rig.session.state.value.phase, SessionPhase.buffering);
    expect(find.text('正在缓冲…'), findsOneWidget);
    expect(find.text('正在打开…'), findsNothing);
    expect(find.byType(CircularProgressIndicator), findsWidgets);
    await rig.advance(tester, const Duration(seconds: 3));
    expect(rig.session.state.value.phase, isNot(SessionPhase.buffering));
    expect(find.text('正在缓冲…'), findsNothing);
  });

  testWidgets('J4: unsupported → short title, detail, error code and '
      '"查看能力说明" for the host', (tester) async {
    final actions = <StateAction>[];
    await pump(tester, 'unsupported', onStateAction: actions.add);
    expect(find.text('格式不支持'), findsOneWidget);
    expect(find.text('本设备不支持此视频编码'), findsOneWidget);
    expect(find.text('错误代码 UNSUPPORTED_VIDEO_CODEC'), findsOneWidget);
    await tester.tap(find.text('查看能力说明'));
    await tester.pump();
    expect(actions, contains(StateAction.showCapabilities));
  });

  testWidgets('J4: without a host handler there is no capability button', (
    tester,
  ) async {
    await pump(tester, 'unsupported');
    expect(find.text('格式不支持'), findsOneWidget);
    expect(find.text('查看能力说明'), findsNothing);
  });

  testWidgets('J4: capability page lists decoders, formats and limits', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    await tester.pumpWidget(
      testApp(
        VideoKitCapabilitiesPage(
          capabilities: Future.value(FakeVideoKit.demoCapabilities()),
        ),
      ),
    );
    await tester.pump();
    await tester.pump();
    expect(find.text('能力说明'), findsOneWidget);
    expect(find.text('视频解码'), findsOneWidget);
    expect(find.text('H.264'), findsWidgets);
    await tester.scrollUntilVisible(find.text('设备建议'), 200);
    expect(find.text('设备建议'), findsOneWidget);
  });

  testWidgets('J9: at 200 % the portrait row becomes "字幕：…" and '
      '"更多控制" rows', (tester) async {
    await pump(tester, 'normal', textScale: 2.0);
    expect(find.text('更多控制'), findsOneWidget);
    expect(find.textContaining('字幕：'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('R3-01: the single player grants itself the audio once bound', (
    tester,
  ) async {
    await pump(tester, 'normal');
    await tester.pump();
    expect(rig.session.commands.whereType<SetActiveAudio>(), hasLength(1));
    expect(
      rig.session.commands.whereType<SetActiveAudio>().single.active,
      isTrue,
    );
    expect(rig.session.state.value.activeAudio, isTrue);
  });

  test('J6: editing timecodes carry tenths; playback ones do not', () {
    expect(VkFormat.timecodeTenths(31000000), '00:31.0');
    expect(VkFormat.timecodeTenths(102600000), '01:42.6');
    expect(VkFormat.timecodeTenths(-5), '00:00.0');
    expect(VkFormat.timecode(102600000), '01:42');
  });

  testWidgets('J9: icon scale follows text up to 1.5', (tester) async {
    final seen = <double>[];
    for (final scale in [1.0, 1.3, 2.0]) {
      await tester.pumpWidget(
        MediaQuery(
          data: MediaQueryData(textScaler: TextScaler.linear(scale)),
          child: Builder(
            builder: (context) {
              seen.add(VkLayoutClass.iconScale(context));
              return const SizedBox();
            },
          ),
        ),
      );
    }
    expect(seen, [1.0, 1.3, 1.5]);
  });
}
