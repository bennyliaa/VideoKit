// M2-A1: UI-03 / UI-04 through the session contract (the path a real
// `ChannelSession` takes), plus 04A U1 for the player and the viewer.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/demo/demo_host.dart';
import 'package:videokit_example/image/image_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// Host whose answers the test controls.
final class ScriptedHost extends NoopHostCallbacks {
  int navigationCalls = 0;
  int actionCalls = 0;
  Completer<NavigationResult>? navigation;
  HostActionResult Function(HostActionRequest r)? action;
  Completer<void>? actionGate;

  @override
  Future<NavigationResult> onNavigationRequested(NavigationRequest r) {
    navigationCalls++;
    return (navigation ??= Completer()).future;
  }

  @override
  Future<HostActionResult> onHostActionRequested(HostActionRequest r) async {
    actionCalls++;
    final g = actionGate;
    if (g != null) await g.future;
    return action?.call(r) ?? const HostActionResult.completed();
  }
}

/// Fake session bound to one image, with a scripted host.
final class ImageRig {
  ImageRig._(this.kit, this.session, this.host);

  final FakeVideoKit kit;
  final VideoKitSession session;
  final ScriptedHost host;

  static Future<ImageRig> create({
    MediaKind kind = MediaKind.imageAnimated,
    String scenario = 'normal',
  }) async {
    final host = ScriptedHost();
    final kit = FakeVideoKit(config: VideoKitConfig(hostCallbacks: host));
    final s = await kit.createSession(const VideoKitSessionConfig());
    unawaited(
      s.bind(
        VideoKitMediaSource(
          mediaToken: 'img-$scenario',
          mediaKind: kind,
          sourceRef: DemoSourceRef(scenario),
        ),
        hostActions: DemoHostActions.image(),
      ),
    );
    return ImageRig._(kit, s, host);
  }

  Future<void> advance(WidgetTester tester, Duration d) async {
    var done = false;
    unawaited(kit.clock.advance(d).whenComplete(() => done = true));
    while (!done) {
      await tester.pump(Duration.zero);
    }
    await tester.pump();
  }

  void dispose() {
    unawaited(session.close());
    unawaited(kit.close());
    kit.clock.dispose();
  }
}

Widget viewer(
  VideoKitSession s, {
  Widget Function(BuildContext, bool)? hostPanel,
  ValueChanged<bool>? onVisibility,
}) => Builder(
  builder: (context) => VideoKitImageViewer(
    session: s,
    title: '演示图片',
    pictureBuilder: (context, session) => DemoSessionPicture(session: session),
    resolveHostString: (k) => DemoHostActions.resolve(context, k),
    onBack: () {},
    hostPanel: hostPanel,
    onControlsVisibilityChanged: onVisibility,
  ),
);

void main() {
  group('04A U1', () {
    testWidgets('player: unsupported keeps only back and title', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await PlayerRig.create('unsupported');
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(demoPlayer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      expect(rig.session.state.value.phase, SessionPhase.errorFatal);
      expect(find.bySemanticsLabel('返回'), findsOneWidget);
      expect(find.text('演示视频'), findsOneWidget);
      for (final gone in ['播放', '更多', '收藏这个视频', '倍速', '播放进度']) {
        expect(find.bySemanticsLabel(gone), findsNothing, reason: gone);
      }
      expect(find.byType(VkSeekBar), findsNothing);
      expect(find.byType(HostActionBar), findsNothing);
    });

    testWidgets('player: recoverable error keeps controls, disabled', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await PlayerRig.create('disconnect');
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(demoPlayer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      await tester.tap(find.bySemanticsLabel('播放'));
      for (var i = 0; i < 35; i++) {
        await rig.advance(tester, const Duration(seconds: 1));
      }
      expect(rig.session.state.value.phase, SessionPhase.errorRecoverable);
      expect(find.byType(VkSeekBar), findsOneWidget);
      expect(find.byType(HostActionBar), findsOneWidget);
      expect(find.text('重试'), findsOneWidget);
      expect(
        tester.widget<VkSeekBar>(find.byType(VkSeekBar)).onDragEnd,
        isNull,
      );
    });

    testWidgets('viewer: unsupported image keeps back, title, paging', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final key = GlobalKey<ImageDemoPageState>();
      await tester.pumpWidget(
        testApp(ImageDemoPage(key: key, initialIndex: 3)),
      );
      for (var i = 0; i < 6; i++) {
        await tester.pump(const Duration(milliseconds: 200));
      }
      key.currentState!.session!.setControlsVisible(true);
      await tester.pump();
      expect(
        key.currentState!.session!.state.value.phase,
        SessionPhase.errorFatal,
      );
      expect(find.bySemanticsLabel('返回'), findsOneWidget);
      for (final gone in ['原尺寸', '旋转画面', '图片信息', '更多']) {
        expect(find.bySemanticsLabel(gone), findsNothing, reason: gone);
      }
      // Paging stays: the user must be able to leave the broken page.
      expect(find.bySemanticsLabel('上一张'), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      await tester.pump(const Duration(seconds: 1));
    });
  });

  group('UI-03 / UI-04 over the session contract', () {
    testWidgets('no video controls on images (static and animated)', (
      tester,
    ) async {
      for (final kind in [MediaKind.imageStatic, MediaKind.imageAnimated]) {
        setViewSize(tester, compactSize);
        final rig = await ImageRig.create(kind: kind);
        await tester.pumpWidget(testApp(viewer(rig.session)));
        await rig.advance(tester, const Duration(seconds: 1));
        rig.session.setControlsVisible(true);
        await tester.pump();
        expect(find.byType(VkSeekBar), findsNothing, reason: kind.name);
        for (final video in ['倍速', '字幕', '音轨', '快进 10 秒', '后退 10 秒']) {
          expect(find.bySemanticsLabel(video), findsNothing, reason: video);
        }
        await tester.pumpWidget(const SizedBox());
        rig.dispose();
        await tester.pump(Duration.zero);
      }
    });

    testWidgets('info panel: mediaInfo items with values (animated)', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create();
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(viewer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      final info = rig.session.state.value.mediaInfo!;
      final rows = ImageInfoSheet.rows(
        VkStrings.forLocale(const Locale('zh')),
        rig.session.state.value,
        null,
        null,
      );
      final map = {for (final (k, v) in rows) k: v};
      expect(map['尺寸'], '${info.width} × ${info.height}');
      expect(map['格式'], contains('GIF'));
      expect(map['帧率'], '24 fps');
      expect(map.containsKey('时长'), info.durationUs != null);
      expect(map['文件大小'], isNot('未知'));
    });

    testWidgets('navigation: one request at a time; failure is shown', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create(kind: MediaKind.imageStatic);
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(viewer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      rig.session.setControlsVisible(true);
      await tester.pump();
      await tester.tap(find.bySemanticsLabel('下一张'));
      await tester.pump();
      await tester.tap(find.bySemanticsLabel('下一张'));
      await tester.pump();
      await tester.fling(
        find.byType(VideoKitImageViewer),
        const Offset(-200, 0),
        1500,
      );
      await tester.pump();
      expect(rig.host.navigationCalls, 1, reason: 'deduplicated');
      rig.host.navigation!.complete(NavigationResult.failed);
      await rig.advance(tester, const Duration(milliseconds: 100));
      expect(find.text('无法切换到下一项，请重试'), findsOneWidget);
    });

    testWidgets('navigation: host never answers → 3 s timeout → failed', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create(kind: MediaKind.imageStatic);
      addTearDown(rig.dispose);
      await tester.pumpWidget(testApp(viewer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      rig.session.setControlsVisible(true);
      await tester.pump();
      await tester.tap(find.bySemanticsLabel('下一张'));
      await rig.advance(tester, const Duration(seconds: 2));
      expect(find.text('无法切换到下一项，请重试'), findsNothing);
      await rig.advance(tester, const Duration(milliseconds: 1100));
      expect(find.text('无法切换到下一项，请重试'), findsOneWidget);
      // After the timeout a new request goes out.
      await tester.tap(find.bySemanticsLabel('下一张'));
      await tester.pump();
      expect(rig.host.navigationCalls, 2);
    });

    testWidgets('host action: dedup while pending; failure toast + 重试', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create(kind: MediaKind.imageStatic);
      addTearDown(rig.dispose);
      rig.host
        ..actionGate = Completer<void>()
        ..action = (_) => const HostActionResult.failed();
      await tester.pumpWidget(testApp(viewer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      rig.session.setControlsVisible(true);
      await tester.pump();
      final fav = find.bySemanticsLabel('收藏这张图片');
      await tester.tap(fav);
      await rig.advance(tester, const Duration(milliseconds: 100));
      expect(
        rig.session.state.value.hostActions
            .firstWhere((a) => a.action.actionId == 'favorite')
            .isPending,
        isTrue,
      );
      await tester.tap(fav);
      await rig.advance(tester, const Duration(milliseconds: 100));
      expect(rig.host.actionCalls, 1, reason: 'pending action not resent');
      rig.host.actionGate!.complete();
      await rig.advance(tester, const Duration(milliseconds: 100));
      expect(find.text('“收藏”未完成'), findsOneWidget);
      expect(find.text('重试'), findsOneWidget);
    });

    testWidgets('host action: 10 s timeout ends pending with a toast', (
      tester,
    ) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create(kind: MediaKind.imageStatic);
      addTearDown(rig.dispose);
      rig.host.actionGate = Completer<void>(); // never completes
      await tester.pumpWidget(testApp(viewer(rig.session)));
      await rig.advance(tester, const Duration(seconds: 1));
      rig.session.setControlsVisible(true);
      await tester.pump();
      await tester.tap(find.bySemanticsLabel('为这张图片添加标签'));
      await rig.advance(tester, const Duration(seconds: 9));
      expect(find.text('“标签”未完成'), findsNothing);
      await rig.advance(tester, const Duration(milliseconds: 1100));
      expect(find.text('“标签”未完成'), findsOneWidget);
      expect(
        rig.session.state.value.hostActions
            .firstWhere((a) => a.action.actionId == 'tag')
            .isPending,
        isFalse,
      );
    });

    testWidgets('host panel follows controls visibility', (tester) async {
      setViewSize(tester, compactSize);
      final rig = await ImageRig.create(kind: MediaKind.imageStatic);
      addTearDown(rig.dispose);
      final shown = <bool>[];
      final reported = <bool>[];
      await tester.pumpWidget(
        testApp(
          viewer(
            rig.session,
            onVisibility: reported.add,
            hostPanel: (context, visible) {
              shown.add(visible);
              return const Text('宿主面板');
            },
          ),
        ),
      );
      await rig.advance(tester, const Duration(seconds: 1));
      rig.session.setControlsVisible(true);
      await tester.pump();
      expect(shown.last, isTrue);
      expect(find.text('宿主面板'), findsOneWidget);
      await tester.tapAt(tester.getCenter(find.byType(VideoKitImageViewer)));
      await tester.pump(const Duration(milliseconds: 400));
      await tester.pump(const Duration(milliseconds: 400));
      expect(shown.last, isFalse, reason: 'hidden with the controls');
      expect(reported.last, isFalse);
      expect(rig.session.state.value.controlsVisible, isFalse);
      await tester.tapAt(tester.getCenter(find.byType(VideoKitImageViewer)));
      await tester.pump(const Duration(milliseconds: 400));
      await tester.pump(const Duration(milliseconds: 400));
      expect(shown.last, isTrue);
    });
  });
}
