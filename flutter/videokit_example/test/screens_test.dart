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
    VideoKitThemeMode mode = VideoKitThemeMode.dark,
  }) async {
    setViewSize(tester, size);
    final rig = await PlayerRig.create(scenario);
    addTearDown(rig.dispose);
    await tester.pumpWidget(
      _wrap(
        testApp(
          demoPlayer(rig.session, key: key),
          fontFamily: _family,
          mode: mode,
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
        testApp(const MultiViewDemoPage(initialCount: 10), fontFamily: _family),
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
    ]) async {
      setViewSize(tester, size);
      await tester.pumpWidget(
        _wrap(
          testApp(
            EditDemoPage(initialScenario: s, showScenarioPicker: false),
            fontFamily: _family,
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
      i < 40 && e.controller.state.phase != EditPhase.completed;
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
}
