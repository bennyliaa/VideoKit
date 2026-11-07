import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/player/player_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  singleMoreTests();
  r1PlayerTests();
  r1HostLayoutTests();
  r1SeekTests();
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

  testWidgets('seek drag: preview frames ≥ 100 ms apart, gone on release', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    final frame = find.byKey(const ValueKey('vk-seek-preview-frame'));
    final bar = find.byType(VkSeekBar);
    final start = tester.getTopLeft(bar) + const Offset(20, 0);
    final g = await tester.startGesture(
      start + Offset(0, tester.getSize(bar).height / 2),
    );
    // 30 moves over ~480 ms.
    for (var i = 0; i < 30; i++) {
      await g.moveBy(const Offset(15, 0));
      await tester.pump(const Duration(milliseconds: 16));
    }
    final during = rig.session.thumbnailRequests.length;
    expect(during, inInclusiveRange(2, 6), reason: '≥ 100 ms apart');
    expect(frame, findsOneWidget, reason: 'Fake demo frame shown');
    // The frame sits above the time bubble.
    expect(
      tester.getBottomLeft(frame).dy,
      lessThan(tester.getTopLeft(find.textContaining(':').last).dy + 1),
    );
    await g.up();
    await tester.pump(const Duration(milliseconds: 16));
    expect(frame, findsNothing);
    await tester.pump(const Duration(milliseconds: 500));
    expect(
      rig.session.thumbnailRequests,
      hasLength(during),
      reason: 'cancelled',
    );
  });

  testWidgets('更多 → 参数 shows the session mediaInfo (design page 9)', (
    tester,
  ) async {
    await pumpPlayer(tester, 'normal');
    await tester.tap(find.bySemanticsLabel('更多'));
    await tester.pump(const Duration(milliseconds: 400));
    await tester.tap(find.text('参数'));
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.byType(MediaInfoSheet), findsOneWidget);
    final info = rig.session.state.value.mediaInfo!;
    for (final (label, value) in [
      ('视频编码', 'H.264'),
      ('音频编码', 'AAC'),
      ('分辨率', '${info.width} × ${info.height}'),
      ('帧率', '30 fps'),
      ('码率', '8 Mbps'),
      ('旋转', '0°'),
    ]) {
      expect(find.text(label), findsOneWidget, reason: label);
      expect(find.text(value), findsOneWidget, reason: label);
    }
    expect(find.text('时长'), findsOneWidget);
    expect(find.text('文件大小'), findsOneWidget);
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

void singleMoreTests() {
  late PlayerRig rig;
  testWidgets('one "more" only: host overflow is the first panel group', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(testApp(demoPlayer(rig.session)));
    await rig.advance(tester, const Duration(seconds: 1));
    await tester.pump();
    expect(find.bySemanticsLabel('更多操作'), findsNothing);
    expect(find.bySemanticsLabel('更多'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('更多'));
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.text('更多操作'), findsOneWidget, reason: 'group 1 title');
    expect(find.text('播放控制'), findsOneWidget, reason: 'group 2 title');
    expect(find.text('分享'), findsOneWidget);
    expect(
      tester.getTopLeft(find.text('分享')).dy,
      lessThan(tester.getTopLeft(find.text('播放控制')).dy),
    );
    await tester.tap(find.text('分享'));
    await rig.advance(tester, const Duration(milliseconds: 100));
    expect(rig.session.hostActionRequests, ['share']);
  });
}

/// TEST-R1 regressions for the player (R1-09, R1-02).
void r1PlayerTests() {
  testWidgets('R1-03 / R1-06: readable codecs, filled speed chips, 1.0×', (
    tester,
  ) async {
    final key = GlobalKey<VideoKitPlayerState>();
    setViewSize(tester, const Size(360, 780));
    final rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(testApp(demoPlayer(rig.session, key: key)));
    await rig.advance(tester, const Duration(seconds: 1));
    key.currentState!.openPanel(PlayerPanel.audio);
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.textContaining('audio/'), findsNothing, reason: 'no MIME');
    expect(find.text('AAC'), findsWidgets);
    await tester.binding.handlePopRoute();
    await tester.pump(const Duration(milliseconds: 400));
    key.currentState!.openPanel(PlayerPanel.speed);
    await tester.pump(const Duration(milliseconds: 400));
    for (final l in ['0.5×', '0.75×', '1.0×', '1.25×', '1.5×', '2.0×']) {
      expect(
        find.descendant(
          of: find.byType(TrackSettingsSheet),
          matching: find.text(l),
        ),
        findsOneWidget,
        reason: l,
      );
    }
    // One row at 360 dp.
    final ys = {
      for (final l in ['0.5×', '2.0×']) tester.getCenter(find.text(l)).dy,
    };
    expect(ys, hasLength(1));
    // Selected chip filled with the primary colour (design page 11).
    final one = find.descendant(
      of: find.byType(TrackSettingsSheet),
      matching: find.text('1.0×'),
    );
    final t = VkTheme.of(tester.element(one));
    final selected = tester.widget<VkPressable>(
      find.ancestor(of: one, matching: find.byType(VkPressable)).first,
    );
    expect(find.text('1.0×'), findsNWidgets(2), reason: 'player button too');
    expect(selected.selected, isTrue);
    expect(t.components.chip.selected.background, t.colors.primary);
    expect(t.components.chip.normal.borderWidth, 0, reason: 'no outline');
  });

  testWidgets('R1-05: landscape host panel shows nearby media', (tester) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(testApp(const PlayerDemoPage()));
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    expect(find.text('邻近媒体'), findsOneWidget);
    for (final name in ['海边.mp4', '山谷黄昏.mkv', '城市夜景.mov']) {
      expect(find.text(name), findsOneWidget, reason: name);
    }
    expect(find.byType(DemoPicture), findsNWidgets(4), reason: 'picture + 3');
    expect(find.bySemanticsLabel(RegExp('^海边.mp4，')), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(seconds: 1));
  });

  testWidgets('R1-09: 重试 on a phone reaches the host (not the bars)', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    final rig = await PlayerRig.create('disconnect');
    addTearDown(rig.dispose);
    final actions = <StateAction>[];
    await tester.pumpWidget(
      testApp(demoPlayer(rig.session, onStateAction: actions.add)),
    );
    await rig.advance(tester, const Duration(seconds: 1));
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 35; i++) {
      await rig.advance(tester, const Duration(seconds: 1));
    }
    expect(find.text('连接中断'), findsOneWidget);
    // R1-02: the primary controls look and act disabled.
    final play = tester.widget<VkIconButton>(
      find
          .ancestor(
            of: find.byIcon(Icons.play_arrow_rounded),
            matching: find.byType(VkIconButton),
          )
          .first,
    );
    expect(play.onPressed, isNull);
    await tester.tap(find.text('重试'));
    await tester.pump();
    expect(actions, [StateAction.retry]);
  });

  testWidgets('R1-09: demo page retry re-binds and playback resumes', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    final key = GlobalKey<PlayerDemoPageState>();
    await tester.pumpWidget(
      testApp(
        PlayerDemoPage(
          key: key,
          initialScenario: PlayerDemoScenario.disconnect,
        ),
      ),
    );
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 70; i++) {
      await tester.pump(const Duration(milliseconds: 500));
    }
    final s = key.currentState!.session!;
    expect(s.state.value.phase, SessionPhase.errorRecoverable);
    await tester.tap(find.text('重试'));
    for (var i = 0; i < 20; i++) {
      await tester.pump(const Duration(milliseconds: 100));
    }
    expect(identical(key.currentState!.session, s), isTrue, reason: 'rebind');
    expect(s.state.value.phase, SessionPhase.ready);
    expect(s.state.value.positionUs, 30000000, reason: 'resumes there');
    expect(find.text('连接中断'), findsNothing);
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 500));
    }
    expect(s.state.value.phase, SessionPhase.playing);
    expect(s.state.value.positionUs, greaterThan(30000000));
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(seconds: 1));
  });
}

/// R1-12: host action column never overlaps itself or the time row.
void r1HostLayoutTests() {
  for (final locale in [const Locale('zh'), VkPseudo.locale]) {
    for (final scale in [1.0, 1.3, 2.0]) {
      testWidgets('R1-12: no overlap, ${locale.toLanguageTag()} × $scale', (
        tester,
      ) async {
        setViewSize(tester, const Size(392, 520));
        final rig = await PlayerRig.create('normal');
        addTearDown(rig.dispose);
        await tester.pumpWidget(
          testApp(demoPlayer(rig.session), locale: locale, textScale: scale),
        );
        await rig.advance(tester, const Duration(seconds: 1));
        final bar = find.byType(HostActionBar);
        Rect rectOf(Element e) {
          final box = e.renderObject! as RenderBox;
          return box.localToGlobal(Offset.zero) & box.size;
        }

        // Buttons, and labels outside them (a badge belongs to its button).
        final labels = find
            .descendant(of: bar, matching: find.byType(Text))
            .evaluate()
            .where(
              (e) => e.findAncestorWidgetOfExactType<VkIconButton>() == null,
            )
            .toList();
        final rects = [
          for (final e
              in find
                  .descendant(of: bar, matching: find.byType(VkIconButton))
                  .evaluate())
            rectOf(e),
          for (final e in labels) rectOf(e),
        ];
        for (var i = 0; i < rects.length; i++) {
          for (var j = i + 1; j < rects.length; j++) {
            final o = rects[i].intersect(rects[j]);
            expect(
              o.width > 0.5 && o.height > 0.5,
              isFalse,
              reason: 'host items overlap: ${rects[i]} / ${rects[j]}',
            );
          }
        }
        final time = tester.getRect(find.text('2:36'));
        expect(tester.getRect(bar).bottom, lessThanOrEqualTo(time.top + 0.5));
        if (scale > 1.3) {
          expect(labels, isEmpty, reason: 'icons only at large text');
        }
      });
    }
  }
}

/// R1-16①: seeking by drag is absolute — the result is under the finger.
void r1SeekTests() {
  for (final (from, to) in [(0.10, 0.26), (0.0, 0.26), (0.60, 0.20)]) {
    testWidgets('R1-16: drag ${from * 100}% → ${to * 100}% lands under the '
        'finger', (tester) async {
      setViewSize(tester, compactSize);
      final rig = await PlayerRig.create('normal');
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(demoPlayer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      final bar = tester.getRect(find.byType(VkSeekBar));
      final y = bar.center.dy;
      Offset at(double f) => Offset(bar.left + bar.width * f, y);
      final g = await tester.startGesture(at(from));
      const steps = 16;
      for (var i = 1; i <= steps; i++) {
        await g.moveTo(at(from + (to - from) * i / steps));
        await tester.pump(const Duration(milliseconds: 16));
      }
      await g.up();
      await rig.advance(tester, const Duration(milliseconds: 300));
      final d = rig.session.state.value.durationUs!;
      expect(rig.session.committedSeeks.last.positionUs / d, closeTo(to, 0.01));
    });
  }
}
