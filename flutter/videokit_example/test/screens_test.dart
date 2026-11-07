// PNG screenshots of the main component states for comparison with the
// design deck. Runs only when VK_SCREENS_DIR is set, for example:
//   VK_SCREENS_DIR=<dir> flutter test test/screens_test.dart
// Uses the Windows DengXian font and the SDK's Material icon font; the
// images are review material only, not goldens.
import 'dart:async';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_example/gallery/components_page.dart';
import 'package:videokit_example/image/image_demo_page.dart';
import 'package:videokit_example/multiview/multi_view_demo_page.dart';
import 'package:videokit_example/player/player_demo_page.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

final String? _dir = Platform.environment['VK_SCREENS_DIR'];
const _family = 'VkScreenshotSans';

Future<void> _loadFonts() async {
  Future<ByteData> read(String path) async =>
      ByteData.sublistView(await File(path).readAsBytes());
  final sans = FontLoader(_family)
    ..addFont(read(r'C:\Windows\Fonts\Deng.ttf'))
    ..addFont(read(r'C:\Windows\Fonts\Dengb.ttf'));
  await sans.load();
  final sdk = File(Platform.resolvedExecutable).parent.parent.parent.parent;
  final icons = FontLoader('MaterialIcons')
    ..addFont(
      read('${sdk.path}/artifacts/material_fonts/materialicons-regular.otf'),
    );
  await icons.load();
}

final _boundary = GlobalKey();

Future<void> _shot(WidgetTester tester, String name) async {
  await tester.pump(const Duration(milliseconds: 400));
  final ro =
      _boundary.currentContext!.findRenderObject()! as RenderRepaintBoundary;
  await tester.runAsync(() async {
    final image = await ro.toImage();
    final png = await image.toByteData(format: ui.ImageByteFormat.png);
    image.dispose();
    final f = File('$_dir/$name.png');
    await f.parent.create(recursive: true);
    await f.writeAsBytes(png!.buffer.asUint8List());
  });
}

Widget _wrap(Widget app) => RepaintBoundary(key: _boundary, child: app);

void main() {
  setUpAll(() async {
    if (_dir != null) await _loadFonts();
  });

  Future<PlayerRig> player(
    WidgetTester tester,
    String scenario,
    Size size, {
    GlobalKey<VideoKitPlayerState>? key,
    VideoKitThemeMode? mode,
    double textScale = 1.0,
  }) async {
    setViewSize(tester, size);
    final rig = await PlayerRig.create(scenario);
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      _wrap(
        testApp(
          // A handler, so unsupported media offers the capability page (J4).
          demoPlayer(rig.session, key: key, onStateAction: (_) {}),
          fontFamily: _family,
          mode: mode,
          textScale: textScale,
        ),
      ),
    );
    if (scenario != 'slowLoad') {
      await rig.advance(tester, const Duration(seconds: 1));
    }
    return rig;
  }

  testWidgets('player screens', (tester) async {
    final key = GlobalKey<VideoKitPlayerState>();
    var rig = await player(tester, 'normal', compactSize, key: key);
    await rig.advance(tester, const Duration(seconds: 42));
    await _shot(tester, 'ui01_player_portrait');
    key.currentState!.openPanel(PlayerPanel.speed);
    await _shot(tester, 'ui02_track_sheet_speed_portrait');
    key.currentState!.openPanel(PlayerPanel.subtitles);
    await _shot(tester, 'ui02_track_sheet_subtitles_portrait');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    rig = await player(tester, 'hostActionTimeout', expandedSize, key: key);
    await tester.tap(find.bySemanticsLabel('收藏这个视频'));
    await tester.tap(find.bySemanticsLabel('删除这个视频'));
    await rig.advance(tester, const Duration(milliseconds: 300));
    await _shot(tester, 'ui01_player_landscape_host_pending');
    key.currentState!.openPanel(PlayerPanel.audio);
    await _shot(tester, 'ui02_track_sheet_audio_landscape');
    await tester.binding.handlePopRoute();
    await rig.advance(tester, const Duration(seconds: 10));
    await tester.pump(const Duration(milliseconds: 100));
    await _shot(tester, 'ui04_host_action_timeout_toast');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    rig = await player(tester, 'slowLoad', compactSize);
    await rig.advance(tester, const Duration(milliseconds: 500));
    await _shot(tester, 'ui09_state_loading');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    rig = await player(tester, 'unsupported', compactSize);
    await _shot(tester, 'ui09_state_unsupported');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    rig = await player(tester, 'disconnect', expandedSize);
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 32; i++) {
      await rig.advance(tester, const Duration(seconds: 1));
    }
    await _shot(tester, 'ui09_state_disconnect');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);
  }, skip: _dir == null);

  testWidgets('component library screens', (tester) async {
    for (final mode in [VideoKitThemeMode.dark, VideoKitThemeMode.light]) {
      setViewSize(tester, const Size(1280, 2600));
      await tester.pumpWidget(
        _wrap(testApp(const ComponentsPage(), fontFamily: _family, mode: mode)),
      );
      await tester.pump(const Duration(milliseconds: 100));
      await _shot(tester, 'common_components_${mode.name}');
      await tester.pumpWidget(const SizedBox());
      await tester.pump(Duration.zero);
    }
  }, skip: _dir == null);

  Future<void> frames(WidgetTester tester, int n) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  testWidgets('M0-B3 image viewer screens', (tester) async {
    final key = GlobalKey<ImageDemoPageState>();
    setViewSize(tester, compactSize);
    await tester.pumpWidget(
      _wrap(testApp(ImageDemoPage(key: key), fontFamily: _family)),
    );
    await frames(tester, 6);
    await _shot(tester, 'ui03_image_static');
    final c = tester.getCenter(find.byType(VideoKitImageViewer));
    await tester.tapAt(c);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tapAt(c);
    await frames(tester, 3);
    key.currentState!.session!.setControlsVisible(true);
    await _shot(tester, 'ui03_image_zoomed_minimap');
    await unmount(tester);

    await tester.pumpWidget(
      _wrap(
        testApp(ImageDemoPage(key: key, initialIndex: 1), fontFamily: _family),
      ),
    );
    await frames(tester, 6);
    await _shot(tester, 'ui03_image_animated');
    await tester.tap(find.bySemanticsLabel('图片信息'));
    await frames(tester, 3);
    await _shot(tester, 'ui03_image_info_sheet');
    await unmount(tester);

    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      _wrap(testApp(ImageDemoPage(key: key), fontFamily: _family)),
    );
    await frames(tester, 6);
    await tester.fling(
      find.byType(VideoKitImageViewer),
      const Offset(300, 0),
      1500,
    );
    await frames(tester, 2);
    await _shot(tester, 'ui03_image_landscape_page_bounce_toast');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M0-B3 multi-view screens', (tester) async {
    setViewSize(tester, compactSize);
    await tester.pumpWidget(
      _wrap(testApp(const MultiViewDemoPage(), fontFamily: _family)),
    );
    await frames(tester, 12);
    await _shot(tester, 'ui05_multiview_phone_2x2');
    await unmount(tester);

    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      _wrap(
        testApp(const MultiViewDemoPage(initialCount: 9), fontFamily: _family),
      ),
    );
    await frames(tester, 14);
    await _shot(tester, 'ui05_multiview_tablet_degraded');
    await unmount(tester);

    await tester.pumpWidget(
      _wrap(
        testApp(const MultiViewDemoPage(initialCount: 12), fontFamily: _family),
      ),
    );
    await frames(tester, 16);
    await _shot(tester, 'ui05_multiview_tablet_12');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M0-B3 review fixes: single more panel', (tester) async {
    final key = GlobalKey<VideoKitPlayerState>();
    setViewSize(tester, compactSize);
    final rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      _wrap(testApp(demoPlayer(rig.session, key: key), fontFamily: _family)),
    );
    await rig.advance(tester, const Duration(seconds: 1));
    await tester.pump();
    await _shot(tester, 'fix1_player_portrait_single_more');
    key.currentState!.openPanel(PlayerPanel.more);
    await _shot(tester, 'fix1_more_panel_two_groups');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M0-B4 editor screens', (tester) async {
    Future<VideoKitEditorState> editor(
      Size size, [
      EditDemoScenario s = EditDemoScenario.normal,
      VideoKitThemeOverrides? overrides,
    ]) async {
      setViewSize(tester, size);
      await tester.pumpWidget(
        _wrap(
          testApp(
            EditDemoPage(initialScenario: s, showScenarioPicker: false),
            fontFamily: _family,
            overrides: overrides,
          ),
        ),
      );
      await frames(tester, 15);
      return tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    }

    var e = await editor(expandedSize);
    e.controller.selectClip(e.controller.state.timeline.clips[1].clipId);
    unawaited(e.controller.seek(26000000));
    await frames(tester, 3);
    await _shot(tester, 'ui06_editor_expanded');
    await tester.tap(find.text('排序'));
    await frames(tester, 3);
    await _shot(tester, 'ui06_clip_order_sheet');
    await unmount(tester);

    e = await editor(compactSize);
    e.controller.selectClip(e.controller.state.timeline.clips[1].clipId);
    await frames(tester, 3);
    await _shot(tester, 'ui06_editor_compact');
    await unmount(tester);
    // Design page 22, third column: a host primary override.
    e = await editor(
      compactSize,
      EditDemoScenario.normal,
      VideoKitThemeOverrides.primary(const Color(0xFF14B8A6)),
    );
    e.controller.selectClip(e.controller.state.timeline.clips[1].clipId);
    await frames(tester, 3);
    await _shot(tester, 'theme_host_primary_override');
    await unmount(tester);
    e = await editor(compactSize);
    e.controller.selectClip(e.controller.state.timeline.clips[1].clipId);
    await frames(tester, 3);
    e.openExport();
    await frames(tester, 4);
    await _shot(tester, 'ui08_export_presets_checks');
    await tester.ensureVisible(find.text('开始导出'));
    await tester.pump();
    await tester.tap(find.text('开始导出'));
    await frames(tester, 6);
    await _shot(tester, 'ui08_export_progress');
    for (
      var i = 0;
      i < 200 && e.controller.state.phase != EditPhase.completed;
      i++
    ) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await frames(tester, 2);
    await _shot(tester, 'ui08_export_success');
    await unmount(tester);

    e = await editor(compactSize, EditDemoScenario.exportFails);
    e.openExport();
    await frames(tester, 4);
    await tester.ensureVisible(find.text('开始导出'));
    await tester.pump();
    await tester.tap(find.text('开始导出'));
    for (
      var i = 0;
      i < 40 && e.controller.state.phase != EditPhase.failed;
      i++
    ) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await frames(tester, 2);
    await _shot(tester, 'ui08_export_failed');
    await unmount(tester);

    e = await editor(compactSize, EditDemoScenario.cancelSlow);
    e.openExport();
    await frames(tester, 4);
    await tester.ensureVisible(find.text('开始导出'));
    await tester.pump();
    await tester.tap(find.text('开始导出'));
    await frames(tester, 3);
    await tester.ensureVisible(find.text('取消导出'));
    await tester.pump();
    await tester.tap(find.text('取消导出'));
    await frames(tester, 1);
    await _shot(tester, 'ui08_export_cancelling');
    for (
      var i = 0;
      i < 20 && e.controller.state.phase != EditPhase.cancelled;
      i++
    ) {
      await tester.pump(const Duration(milliseconds: 250));
    }
    await frames(tester, 2);
    await _shot(tester, 'ui08_export_cancelled');
    await unmount(tester);

    e = await editor(expandedSize);
    e.openMasks(MaskEditorTab.manual);
    await frames(tester, 2);
    unawaited(e.maskEditor!.addManualMask());
    await frames(tester, 3);
    unawaited(e.controller.seek(2000000));
    await frames(tester, 3);
    await _shot(tester, 'ui07_mask_manual');
    await unmount(tester);

    e = await editor(expandedSize, EditDemoScenario.trackingLost);
    e.openMasks(MaskEditorTab.tracking);
    await frames(tester, 2);
    unawaited(e.maskEditor!.detectFaces());
    await frames(tester, 3);
    await _shot(tester, 'ui07_track_candidates');
    final cand = e.maskEditor!.candidates!.first;
    unawaited(e.maskEditor!.chooseCandidate(cand));
    await frames(tester, 6);
    await _shot(tester, 'ui07_track_running');
    for (var i = 0; i < 80; i++) {
      await tester.pump(const Duration(milliseconds: 250));
      if (e.controller.state.tracking.values.firstOrNull?.status ==
          TrackingRunStatus.completed) {
        break;
      }
    }
    await frames(tester, 2);
    await _shot(tester, 'ui07_track_coverage_lost');
    await tester.tap(find.text('纠正').first);
    await frames(tester, 3);
    await _shot(tester, 'ui07_track_correction');
    await unmount(tester);

    e = await editor(compactSize, EditDemoScenario.trackingLost);
    e.openMasks(MaskEditorTab.tracking);
    await frames(tester, 2);
    unawaited(e.maskEditor!.detectFaces());
    await frames(tester, 3);
    unawaited(e.maskEditor!.chooseCandidate(e.maskEditor!.candidates!.first));
    for (var i = 0; i < 80; i++) {
      await tester.pump(const Duration(milliseconds: 250));
      if (e.controller.state.tracking.values.firstOrNull?.status ==
          TrackingRunStatus.completed) {
        break;
      }
    }
    e.openExport();
    await frames(tester, 4);
    await tester.ensureVisible(find.text('查看未覆盖区间'));
    await tester.pump();
    await tester.tap(find.text('查看未覆盖区间'));
    await frames(tester, 3);
    await _shot(tester, 'ui07_coverage_check_sheet');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M0-B4 fix: zoom capsule', (tester) async {
    final key = GlobalKey<ImageDemoPageState>();
    setViewSize(tester, compactSize);
    await tester.pumpWidget(
      _wrap(testApp(ImageDemoPage(key: key), fontFamily: _family)),
    );
    await frames(tester, 6);
    final c = tester.getCenter(find.byType(VideoKitImageViewer));
    await tester.tapAt(c);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tapAt(c);
    await frames(tester, 3);
    await _shot(tester, 'fix_ui03_zoom_capsule');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M1-A1 seek preview frame and 参数 panel', (tester) async {
    final key = GlobalKey<VideoKitPlayerState>();
    final rig = await player(tester, 'normal', compactSize, key: key);
    await rig.advance(tester, const Duration(seconds: 20));
    final bar = find.byType(VkSeekBar);
    final start = tester.getTopLeft(bar) + const Offset(40, 0);
    final g = await tester.startGesture(
      start + Offset(0, tester.getSize(bar).height / 2),
    );
    for (var i = 0; i < 12; i++) {
      await g.moveBy(const Offset(12, 0));
      await tester.pump(const Duration(milliseconds: 40));
    }
    // Let the demo PNG decode (real async).
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 300)),
    );
    await tester.pump();
    await _shot(tester, 'm1_seek_preview_frame');
    await g.up();
    await tester.pump(const Duration(milliseconds: 400));
    key.currentState!.openPanel(PlayerPanel.more);
    await _shot(tester, 'm1_more_panel_media_info_entry');
    await tester.binding.handlePopRoute();
    await tester.pump(const Duration(milliseconds: 400));
    key.currentState!.openPanel(PlayerPanel.mediaInfo);
    await _shot(tester, 'm1_media_info_sheet');
    await unmount(tester);
    await player(tester, 'normal', expandedSize, key: key);
    key.currentState!.openPanel(PlayerPanel.mediaInfo);
    await _shot(tester, 'm1_media_info_sheet_landscape');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('TEST-R1 fix screens', (tester) async {
    setViewSize(tester, const Size(392, 520));
    final rig = await PlayerRig.create('normal');
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      _wrap(
        testApp(
          demoPlayer(rig.session),
          fontFamily: _family,
          locale: VkPseudo.locale,
          textScale: 2,
        ),
      ),
    );
    await rig.advance(tester, const Duration(seconds: 1));
    await _shot(tester, 'r1_12_player_pseudo_200');
    await unmount(tester);

    // R1-02 / R1-09: error state, controls disabled, 重试 reachable.
    setViewSize(tester, compactSize);
    final dis = await PlayerRig.create('disconnect');
    addTearDown(dis.dispose);
    await tester.pumpWidget(
      _wrap(testApp(demoPlayer(dis.session), fontFamily: _family)),
    );
    await dis.advance(tester, const Duration(seconds: 1));
    await tester.tap(find.bySemanticsLabel('播放'));
    for (var i = 0; i < 35; i++) {
      await dis.advance(tester, const Duration(seconds: 1));
    }
    await _shot(tester, 'r1_02_disconnect_disabled_controls');
    await unmount(tester);

    // R1-03 / R1-06: audio names, filled speed chips at 360 dp.
    final key = GlobalKey<VideoKitPlayerState>();
    setViewSize(tester, const Size(360, 780));
    final tr = await PlayerRig.create('normal');
    addTearDown(tr.dispose);
    await tester.pumpWidget(
      _wrap(testApp(demoPlayer(tr.session, key: key), fontFamily: _family)),
    );
    await tr.advance(tester, const Duration(seconds: 1));
    key.currentState!.openPanel(PlayerPanel.audio);
    await _shot(tester, 'r1_03_audio_tracks');
    await tester.binding.handlePopRoute();
    await tester.pump(const Duration(milliseconds: 400));
    key.currentState!.openPanel(PlayerPanel.speed);
    await _shot(tester, 'r1_06_speed_chips_360');
    await unmount(tester);

    // R1-05: nearby media in the landscape host panel slot.
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      _wrap(testApp(const PlayerDemoPage(), fontFamily: _family)),
    );
    await frames(tester, 10);
    await _shot(tester, 'r1_05_host_panel_nearby_media');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);

    // R1-12b: phone 3×3 with paused slots.
    setViewSize(tester, const Size(392, 780));
    final mv = GlobalKey<MultiViewDemoPageState>();
    await tester.pumpWidget(
      _wrap(
        testApp(
          MultiViewDemoPage(key: mv, initialCount: 12),
          fontFamily: _family,
        ),
      ),
    );
    await frames(tester, 10);
    await tester.tap(find.bySemanticsLabel('布局'));
    await frames(tester, 4);
    await tester.tap(find.text('3×3'));
    await frames(tester, 4);
    await _shot(tester, 'r1_12b_multiview_3x3_phone');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);

    // R1-01 / R1-04 / R1-13: light component page.
    setViewSize(tester, const Size(392, 1600));
    await tester.pumpWidget(
      _wrap(
        testApp(
          const ComponentsPage(),
          fontFamily: _family,
          mode: VideoKitThemeMode.light,
        ),
      ),
    );
    await frames(tester, 4);
    await _shot(tester, 'r1_13_components_light');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);

    // R1-10 / R1-10b: back from the unsupported page, fitted.
    setViewSize(tester, compactSize);
    final img = GlobalKey<ImageDemoPageState>();
    await tester.pumpWidget(
      _wrap(
        testApp(ImageDemoPage(key: img, initialIndex: 3), fontFamily: _family),
      ),
    );
    await frames(tester, 6);
    await _shot(tester, 'r1_10_unsupported_page');
    img.currentState!.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('上一张'));
    await frames(tester, 6);
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 200)),
    );
    await _shot(tester, 'r1_10_previous_page_after_unsupported');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);
  }, skip: _dir == null);

  testWidgets('M2-A1 screens', (tester) async {
    // 04A U1: unsupported video keeps only back and title.
    setViewSize(tester, compactSize);
    final un = await PlayerRig.create('unsupported');
    addTearDown(un.dispose);
    await tester.pumpWidget(
      _wrap(testApp(demoPlayer(un.session), fontFamily: _family)),
    );
    await un.advance(tester, const Duration(seconds: 1));
    await _shot(tester, 'm2_u1_player_unsupported');
    await unmount(tester);
    // 04A U1 on the image viewer (paging stays).
    final img = GlobalKey<ImageDemoPageState>();
    await tester.pumpWidget(
      _wrap(
        testApp(ImageDemoPage(key: img, initialIndex: 3), fontFamily: _family),
      ),
    );
    await frames(tester, 6);
    img.currentState!.session!.setControlsVisible(true);
    await _shot(tester, 'm2_u1_image_unsupported');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);
    // Track subtitles with channel layouts (04A C1).
    final key = GlobalKey<VideoKitPlayerState>();
    final tr = await PlayerRig.create('normal');
    addTearDown(tr.dispose);
    await tester.pumpWidget(
      _wrap(testApp(demoPlayer(tr.session, key: key), fontFamily: _family)),
    );
    await tr.advance(tester, const Duration(seconds: 1));
    key.currentState!.openPanel(PlayerPanel.audio);
    await _shot(tester, 'm2_c1_audio_channels');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M3-A1 screens', (tester) async {
    final mv = GlobalKey<MultiViewDemoPageState>();
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      _wrap(
        testApp(
          MultiViewDemoPage(key: mv, initialCount: 12),
          fontFamily: _family,
        ),
      ),
    );
    await frames(tester, 12);
    await _shot(tester, 'm3_multiview_12_placeholders');
    await tester.tap(find.byType(VideoKitSlot).at(4));
    await frames(tester, 4);
    await _shot(tester, 'm3_audio_moved_to_slot5');
    mv.currentState!.kit.preemptAudio();
    await frames(tester, 2);
    await _shot(tester, 'm3_audio_preempted_notice');
    final s = mv.currentState!.kit.sessions.firstWhere(
      (x) => x.sessionId == mv.currentState!.slots[1].session.sessionId,
    );
    s.injectFault(
      const VideoKitStableError(
        code: ErrorCode.decoderUnavailable,
        stage: ErrorStage.playback,
      ),
    );
    await frames(tester, 4);
    await _shot(tester, 'm3_single_slot_fault');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);
  }, skip: _dir == null);

  testWidgets('M4-A1 screens', (tester) async {
    setViewSize(tester, expandedSize);
    await tester.pumpWidget(
      _wrap(
        testApp(
          const EditDemoPage(
            initialScenario: EditDemoScenario.fastConcatRejected,
            showScenarioPicker: false,
          ),
          fontFamily: _family,
        ),
      ),
    );
    await frames(tester, 15);
    tester.state<VideoKitEditorState>(find.byType(VideoKitEditor)).openExport();
    await frames(tester, 4);
    await _shot(tester, 'm4_export_fast_concat_rejected');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);
  }, skip: _dir == null);

  testWidgets('UI-AUDIT-A2 screens', (tester) async {
    // 04A B1: opened, still buffering the first frame.
    var rig = await player(tester, 'openBuffering', compactSize);
    await _shot(tester, 'a2_open_buffering');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    // J9: system text at 200 %, portrait list rows.
    rig = await player(tester, 'normal', compactSize, textScale: 2.0);
    await _shot(tester, 'a2_player_text_200');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    // Design page 10: landscape, floating lock, mute by the slider.
    rig = await player(tester, 'normal', expandedSize);
    await _shot(tester, 'a2_player_landscape');
    await tester.pumpWidget(const SizedBox());
    rig.dispose();
    await tester.pump(Duration.zero);

    // J4: read-only capability page.
    setViewSize(tester, compactSize);
    await tester.pumpWidget(
      _wrap(
        testApp(
          VideoKitCapabilitiesPage(
            capabilities: Future.value(FakeVideoKit.demoCapabilities()),
          ),
          fontFamily: _family,
        ),
      ),
    );
    await frames(tester, 4);
    await _shot(tester, 'a2_capabilities_page');
    await tester.pumpWidget(const SizedBox());
    await frames(tester, 5);
  }, skip: _dir == null);
}
