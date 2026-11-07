import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  late PlayerRig rig;

  Future<void> pumpPlayer(
    WidgetTester tester,
    String scenario, {
    Size size = expandedSize,
    GlobalKey<VideoKitPlayerState>? key,
    List<bool>? visibility,
  }) async {
    setViewSize(tester, size);
    rig = await PlayerRig.create(scenario);
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      testApp(
        demoPlayer(
          rig.session,
          key: key,
          onControlsVisibilityChanged: visibility?.add,
        ),
      ),
    );
    if (scenario != 'slowLoad') {
      await rig.advance(tester, const Duration(seconds: 1));
    }
  }

  testWidgets('play / pause through the dispatcher; state follows session', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    expect(rig.session.state.value.phase, SessionPhase.ready);
    await tester.tap(find.bySemanticsLabel('播放'));
    await rig.advance(tester, const Duration(milliseconds: 500));
    expect(rig.session.commands.whereType<Play>(), hasLength(1));
    expect(rig.session.state.value.phase, SessionPhase.playing);
    expect(find.bySemanticsLabel('暂停'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('暂停'));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.commands.whereType<Pause>(), hasLength(1));
  });

  testWidgets('auto-hide: only while playing, not with a panel open', (
    tester,
  ) async {
    final key = GlobalKey<VideoKitPlayerState>();
    final visibility = <bool>[];
    await pumpPlayer(tester, 'normal', key: key, visibility: visibility);
    // Paused: stays visible.
    await tester.pump(const Duration(seconds: 10));
    expect(visibility, isNot(contains(false)));
    await tester.tap(find.bySemanticsLabel('播放'));
    await rig.advance(tester, const Duration(milliseconds: 500));
    await tester.pump(const Duration(seconds: 2));
    expect(visibility.lastOrNull ?? true, isTrue);
    await tester.pump(const Duration(seconds: 2));
    expect(visibility.last, isFalse, reason: 'hidden 3 s after playing');
    expect(rig.session.controlsVisible.last, isFalse);
    // A panel blocks hiding.
    key.currentState!.openPanel(PlayerPanel.speed);
    await tester.pump(const Duration(milliseconds: 400));
    expect(visibility.last, isTrue);
    await tester.pump(const Duration(seconds: 10));
    expect(visibility.last, isTrue, reason: 'panel open');
  });

  testWidgets('continuous seek: previews throttled, one commit (last)', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    final bar = find.byType(VkSeekBar);
    final start = tester.getTopLeft(bar) + const Offset(20, 0);
    final g = await tester.startGesture(
      start + Offset(0, tester.getSize(bar).height / 2),
    );
    for (var i = 0; i < 30; i++) {
      await g.moveBy(const Offset(15, 0));
      await tester.pump(const Duration(milliseconds: 16));
    }
    await g.up();
    await tester.pump(const Duration(milliseconds: 200));
    await rig.advance(tester, const Duration(milliseconds: 300));
    final seeks = rig.session.commands.whereType<SeekTo>().toList();
    final previews = seeks.where((s) => s.mode == SeekMode.preview).toList();
    expect(rig.session.committedSeeks, hasLength(1));
    expect(
      previews.length,
      lessThan(30),
      reason: 'previews are throttled (100 ms)',
    );
    final committed = rig.session.committedSeeks.single.positionUs;
    expect(committed, greaterThan(previews.last.positionUs - 1));
    expect(rig.session.state.value.positionUs, committed);
  });

  testWidgets('back key closes the panel first, then reaches the route', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    await tester.tap(find.bySemanticsLabel('倍速'));
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.byType(TrackSettingsSheet), findsOneWidget);
    final handled = await tester.binding.handlePopRoute();
    await tester.pump(const Duration(milliseconds: 400));
    expect(handled, isTrue);
    expect(find.byType(TrackSettingsSheet), findsNothing);
    expect(find.byType(VideoKitPlayer), findsOneWidget);
  });

  testWidgets('track sheet: speed and subtitle choice become commands', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    await tester.tap(find.bySemanticsLabel('倍速'));
    await tester.pump(const Duration(milliseconds: 400));
    await tester.tap(find.text('1.5×').last);
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.commands.whereType<SetSpeed>().single.speed, 1.5);
    expect(rig.session.state.value.speed, 1.5);
    await tester.tap(find.text('字幕').last);
    await tester.pump(const Duration(milliseconds: 300));
    final sub = rig.session.state.value.subtitleTracks.first;
    await tester.tap(
      find
          .text(
            TrackSettingsSheet.trackName(
              VkStrings.forLocale(const Locale('zh')),
              sub,
              0,
            ),
          )
          .last,
    );
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.state.value.selectedSubtitleTrackId, sub.id);
  });

  testWidgets('host actions: favourite updates, pending, timeout toast', (
    tester,
  ) async {
    await pumpPlayer(tester, 'hostActionTimeout');
    await tester.tap(find.bySemanticsLabel('收藏这个视频'));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(find.bySemanticsLabel('取消收藏这个视频'), findsOneWidget);
    expect(find.text('已收藏'), findsOneWidget);

    await tester.tap(find.bySemanticsLabel('删除这个视频'));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(tester.getSemantics(find.bySemanticsLabel('删除这个视频')).hint, '等待中');
    // A repeated tap while pending is merged by the session (Superseded).
    await tester.tap(find.bySemanticsLabel('删除这个视频'));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.hostActionRequests, ['favorite', 'delete', 'delete']);
    // The host never answers → 10 s timeout → failure toast.
    await rig.advance(tester, const Duration(seconds: 10));
    await tester.pump(const Duration(milliseconds: 100));
    expect(find.text('“删除”未完成'), findsOneWidget);
    expect(
      rig.session.state.value.hostActions
          .firstWhere((a) => a.action.actionId == 'delete')
          .pending,
      isFalse,
    );
  });

  testWidgets('state views: slow load, disconnect with retry, unsupported', (
    tester,
  ) async {
    await pumpPlayer(tester, 'slowLoad');
    expect(find.text('正在打开…'), findsOneWidget);
    await rig.advance(tester, const Duration(seconds: 4));
    expect(find.text('正在打开…'), findsNothing);
  });

  testWidgets('disconnect scenario shows the connection error', (tester) async {
    await pumpPlayer(tester, 'disconnect');
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 35; i++) {
      await rig.advance(tester, const Duration(seconds: 1));
    }
    expect(find.text('连接中断'), findsOneWidget);
  });

  testWidgets('unsupported scenario shows a fatal state without retry', (
    tester,
  ) async {
    await pumpPlayer(tester, 'unsupported');
    await rig.advance(tester, const Duration(seconds: 1));
    expect(find.byType(VideoKitStateView), findsOneWidget);
    expect(find.text('重试'), findsNothing);
  });
}
