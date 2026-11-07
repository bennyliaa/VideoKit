// TEST-R3 regressions in the App: R3-01 audio in the multi-view, R3-02 a
// Kit without the edit engine (EDITING_NOT_AVAILABLE).
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/host/app_host.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/pages/multi_view_page.dart';
import 'package:videokit_fake/videokit_fake.dart';

import 'app_test.dart' show pickDemo;
import 'support.dart';

DemoBackend noEditing() {
  final hosts = AppHostCallbacks();
  return DemoBackend(
    kit: FakeVideoKit(
      config: VideoKitConfig(hostCallbacks: hosts),
      editingAvailable: false,
    ),
    hosts: hosts,
  );
}

void main() {
  testWidgets('R3-02: without an edit engine "拼接" is disabled and says '
      'it is coming', (tester) async {
    final rig = AppRig.create(backend: noEditing());
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
    expect(find.text('功能即将提供'), findsOneWidget);
    await tester.tap(find.text('拼接为一个视频'));
    await settle(tester, 4);
    expect(find.byType(ConcatPage), findsNothing, reason: 'disabled');
    await unmount(tester);
  });

  testWidgets('R3-02: the concat page shows "暂不支持" with a way back, '
      'never an endless spinner', (tester) async {
    final rig = AppRig.create(entries: sampleHistory(), backend: noEditing());
    await rig.pump(tester);
    final videos = [
      for (final e in sampleHistory())
        if (e.kind == MediaKind.video) e,
    ].take(2).toList();
    final nav = tester.state<NavigatorState>(find.byType(Navigator).first);
    unawaited(
      nav.push(
        MaterialPageRoute<void>(builder: (_) => ConcatPage(entries: videos)),
      ),
    );
    await settle(tester, 8);
    final page = tester.state<ConcatPageState>(find.byType(ConcatPage));
    expect(page.notAvailable, isTrue);
    expect(find.text('暂不支持'), findsOneWidget);
    expect(find.text('剪辑与拼接功能即将提供'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
    await tester.tap(find.bySemanticsLabel('返回'));
    await settle(tester, 4);
    expect(find.byType(ConcatPage), findsNothing);
    await unmount(tester);
  });

  testWidgets('R3-01: one slot has the audio; "全部静音" clears every slot', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
    await tapText(tester, '在多画面中打开');
    await settle(tester, 8);
    final page = tester.state<MultiViewPageState>(find.byType(MultiViewPage));
    bool audible(VideoKitSession s) => s.state.value.activeAudio;
    expect(page.sessions.values.where(audible), hasLength(1));
    final other = page.sessions.values.firstWhere((s) => !audible(s));
    await page.activateAudio(other.sessionId);
    await settle(tester, 2);
    expect(page.sessions.values.where(audible).single, same(other));
    await page.muteAll();
    await settle(tester, 2);
    expect(page.sessions.values.where(audible), isEmpty);
    expect(find.text('发声'), findsNothing);
    await tester.binding.handlePopRoute();
    await settle(tester, 4);
    await unmount(tester);
  });
}
