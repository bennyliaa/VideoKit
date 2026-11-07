import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/image/image_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  final key = GlobalKey<ImageDemoPageState>();

  Future<void> pumpPage(
    WidgetTester tester, {
    int index = 0,
    Size size = compactSize,
  }) async {
    setViewSize(tester, size);
    await tester.pumpWidget(
      testApp(ImageDemoPage(key: key, initialIndex: index)),
    );
    for (var i = 0; i < 6; i++) {
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

  VideoKitSessionState state() => key.currentState!.session!.state.value;

  testWidgets('static image: image tools only, no video controls', (
    tester,
  ) async {
    await pumpPage(tester);
    expect(state().mediaKind, MediaKind.imageStatic);
    expect(find.byType(VkSeekBar), findsNothing);
    for (final label in ['倍速', '字幕', '音轨', '静音', '后退 10 秒', '播放']) {
      expect(find.bySemanticsLabel(label), findsNothing, reason: label);
    }
    expect(find.bySemanticsLabel('原尺寸'), findsOneWidget);
    expect(find.bySemanticsLabel('旋转画面'), findsOneWidget);
    expect(find.bySemanticsLabel('收藏这张图片'), findsOneWidget);
    expect(find.bySemanticsLabel('图片信息'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('info panel shows only reported facts; back closes it', (
    tester,
  ) async {
    await pumpPage(tester);
    await tester.tap(find.bySemanticsLabel('图片信息'));
    await settle(tester);
    expect(find.text('HEIC（静态）'), findsOneWidget);
    expect(find.text('1920 × 1080'), findsOneWidget);
    expect(find.text('3.2 MB'), findsOneWidget);
    // 04A L2 details reported by the Fake.
    expect(find.text('1 帧'), findsOneWidget);
    expect(find.text('8.3 MB'), findsOneWidget);
    expect(find.text('原始分辨率'), findsOneWidget);
    final handled = await tester.binding.handlePopRoute();
    await settle(tester);
    expect(handled, isTrue);
    expect(find.byType(ImageInfoSheet), findsNothing);
    expect(find.byType(VideoKitImageViewer), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('double tap zooms with indicator and mini map; fit/rotate', (
    tester,
  ) async {
    await pumpPage(tester);
    final center = tester.getCenter(find.byType(VideoKitImageViewer));
    await tester.tapAt(center);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tapAt(center);
    await settle(tester);
    expect(state().transform.scale, 2);
    expect(find.bySemanticsLabel('可见区域'), findsOneWidget);
    expect(find.bySemanticsLabel('缩放比例'), findsOneWidget);
    await tester.tapAt(center);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tapAt(center);
    await settle(tester);
    expect(state().transform.scale, 1);
    expect(find.bySemanticsLabel('可见区域'), findsNothing);

    key.currentState!.session!.setControlsVisible(true);
    await tester.tap(find.bySemanticsLabel('原尺寸'));
    await settle(tester);
    expect(state().transform.fitMode, FitMode.original);
    expect(find.bySemanticsLabel('适应'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('旋转画面'));
    await settle(tester);
    expect(state().transform.rotationDeg, 90);
    await unmount(tester);
  });

  testWidgets('swipe pages through the host; past the end bounces back', (
    tester,
  ) async {
    await pumpPage(tester);
    final viewer = find.byType(VideoKitImageViewer);
    await tester.fling(viewer, const Offset(-200, 0), 1500);
    await settle(tester);
    expect(key.currentState!.index, 1);
    expect(state().mediaKind, MediaKind.imageAnimated);
    expect(find.text('GIF · 动态'), findsOneWidget);
    await tester.fling(viewer, const Offset(200, 0), 1500);
    await settle(tester);
    expect(key.currentState!.index, 0);
    await tester.fling(viewer, const Offset(200, 0), 1500);
    await settle(tester);
    expect(key.currentState!.index, 0);
    expect(find.text('没有更多内容了'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester);
    expect(key.currentState!.index, 1);
    await unmount(tester);
  });

  testWidgets('animated image: pause/play and loop off stops at the end', (
    tester,
  ) async {
    await pumpPage(tester, index: 1);
    expect(state().phase, SessionPhase.playing);
    await tester.tap(find.bySemanticsLabel('暂停'));
    await settle(tester);
    expect(state().phase, SessionPhase.paused);
    await tester.tap(find.bySemanticsLabel('播放'));
    await settle(tester);
    expect(state().phase, SessionPhase.playing);
    final loop = find.bySemanticsLabel('循环播放');
    expect(
      tester.getSemantics(loop).flagsCollection.isSelected.toString(),
      contains('isTrue'),
    );
    expect(state().looping, isTrue, reason: '04A L1 default for animations');
    await tester.tap(loop);
    await settle(tester);
    expect(state().looping, isFalse, reason: 'SetLooping(false) sent');
    // The demo animation lasts 2 s; without looping it stops on the last
    // frame (ENDED) instead of wrapping.
    for (var i = 0; i < 15; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
    expect(state().phase, SessionPhase.ended);
    expect(state().positionUs, state().durationUs);
    expect(find.bySemanticsLabel('播放'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('corrupt image shows the state view', (tester) async {
    await pumpPage(tester, index: 3);
    for (var i = 0; i < 10; i++) {
      await tester.pump(const Duration(milliseconds: 300));
    }
    expect(find.byType(VideoKitStateView), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('R1-10: pages after the unsupported one show their own image', (
    tester,
  ) async {
    await pumpPage(tester, index: 2);
    final first = key.currentState!.session;
    key.currentState!.session!.setControlsVisible(true);
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester);
    expect(key.currentState!.index, 3);
    expect(state().phase, SessionPhase.errorFatal);
    expect(find.byType(VideoKitStateView), findsOneWidget);
    expect(identical(key.currentState!.session, first), isFalse);
    key.currentState!.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('上一张'));
    await settle(tester);
    expect(key.currentState!.index, 2);
    expect(state().phase, SessionPhase.ready);
    expect(state().error, isNull);
    expect(find.byType(VideoKitStateView), findsNothing);
    await tester.tap(find.bySemanticsLabel('上一张'));
    await settle(tester);
    expect(state().mediaKind, MediaKind.imageAnimated);
    expect(state().error, isNull);
    await unmount(tester);
  });

  testWidgets('R1-10b: the next page starts at 适应', (tester) async {
    await pumpPage(tester);
    final viewer = find.byType(VideoKitImageViewer);
    final center = tester.getCenter(viewer);
    await tester.tapAt(center);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tapAt(center);
    await settle(tester);
    expect(state().transform.scale, 2);
    key.currentState!.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester);
    expect(key.currentState!.index, 1);
    expect(state().transform, const MediaTransform());
    expect(find.bySemanticsLabel('可见区域'), findsNothing);
    await unmount(tester);
  });

  testWidgets('R1-15: image page host actions describe the image', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    await pumpPage(tester);
    key.currentState!.session!.setControlsVisible(true);
    await tester.pump();
    expect(find.bySemanticsLabel(RegExp('收藏这张图片')), findsOneWidget);
    expect(find.bySemanticsLabel(RegExp('这个视频')), findsNothing);
    await unmount(tester);
    handle.dispose();
  });

  testWidgets('R1-10b: same session re-bound to a new image resets to 适应', (
    tester,
  ) async {
    setViewSize(tester, compactSize);
    final kit = FakeVideoKit();
    final s = await kit.createSession(const VideoKitSessionConfig());
    Future<void> advance([int ms = 500]) async {
      var done = false;
      unawaited(
        kit.clock
            .advance(Duration(milliseconds: ms))
            .whenComplete(() => done = true),
      );
      while (!done) {
        await tester.pump(Duration.zero);
      }
      await tester.pump();
    }

    Future<void> run(Future<Object?> f) async {
      unawaited(f);
      await advance();
    }

    VideoKitMediaSource src(String id) => VideoKitMediaSource(
      mediaToken: id,
      mediaKind: MediaKind.imageStatic,
      sourceRef: const DemoSourceRef('normal'),
    );
    Widget viewer(VideoKitMediaSource source) => testApp(
      VideoKitImageViewer(
        session: s,
        source: source,
        pictureBuilder: (context, session) =>
            DemoSessionPicture(session: session),
      ),
    );
    await run(s.bind(src('a')));
    await tester.pumpWidget(viewer(src('a')));
    await run(
      s.execute(const SetTransform(MediaTransform(scale: 2, panX: 0.4))),
    );
    await tester.pump();
    expect(s.state.value.transform.scale, 2);
    await run(s.bind(src('b')));
    await tester.pumpWidget(viewer(src('b')));
    await tester.pump();
    await advance();
    expect(s.state.value.transform, const MediaTransform());
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
    unawaited(s.close());
    await advance();
    unawaited(kit.close());
    await advance();
  });
}
