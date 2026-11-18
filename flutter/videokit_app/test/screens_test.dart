// PNG screenshots for comparison with design pages 7, 8 (and the editor
// top-bar fix). Runs only when VK_SCREENS_DIR is set.
import 'dart:async';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

import 'package:videokit_app/app_scope.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/history/history_entry.dart';
import 'package:videokit_app/library/library_gate.dart';
import 'package:videokit_app/pages/image_page.dart';
import 'package:videokit_app/startup/app_bootstrap.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'library_page_test.dart' show libraryRig, openLibrary;
import 'startup_test.dart' show ScriptedConnector;

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

  Future<AppRig> app(
    WidgetTester tester, {
    bool history = true,
    Map<String, Object?>? settings,
    Size size = compactSize,
  }) async {
    final rig = AppRig.create(
      entries: history ? sampleHistory() : const [],
      settings: settings,
    );
    await rig.pump(tester, size: size, fontFamily: _family, wrap: _wrap);
    return rig;
  }

  testWidgets('M0-B5 app screens', (tester) async {
    await app(tester, history: false);
    await _shot(tester, 'app_home_empty');
    await tapText(tester, '打开文件');
    await settle(tester, 4);
    await _shot(tester, 'app_picker_demo');
    await unmount(tester);

    await app(tester);
    await _shot(tester, 'app_home_list');
    await tester.tap(find.bySemanticsLabel('更多').first);
    await settle(tester, 4);
    await _shot(tester, 'app_home_menu');
    await unmount(tester);

    await app(tester, settings: {'layout': 'grid'});
    await _shot(tester, 'app_home_grid');
    await unmount(tester);

    await app(tester, size: expandedSize);
    await _shot(tester, 'app_home_list_tablet');
    await unmount(tester);

    await app(tester);
    await tester.tap(find.bySemanticsLabel('设置'));
    await settle(tester, 6);
    await _shot(tester, 'app_settings');
    await unmount(tester);

    await app(tester, settings: {'themeMode': 'light'});
    await _shot(tester, 'app_home_list_light');
    await unmount(tester);

    // Multi-select choice and the editor top bar (fix from M0-B4 review).
    await app(tester, history: false, size: expandedSize);
    await tapText(tester, '打开文件');
    await settle(tester, 4);
    await tapText(tester, '山谷黄昏.mkv');
    await tapText(tester, '家庭录像.avi');
    await tester.pump();
    await tester.tap(find.textContaining('打开 2 个'));
    await settle(tester, 4);
    await _shot(tester, 'app_open_choice');
    await tapText(tester, '拼接为一个视频');
    await settle(tester, 10);
    await _shot(tester, 'fix_editor_topbar_export');
    await unmount(tester);
    // 04A P1/P2: a played record gets a captured thumbnail and codec.
    await app(tester, history: false);
    await tapText(tester, '打开文件');
    await settle(tester, 4);
    await tapText(tester, '山谷黄昏.mkv');
    await tester.pump();
    await tester.tap(find.textContaining('打开 1 个'));
    await settle(tester, 20);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    // Let the PNG decode (real async; fake time does not decode images).
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 300)),
    );
    await tester.pump();
    await _shot(tester, 'app_home_captured_thumbnail');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M1-A1 start-up screens', (tester) async {
    tester.view.physicalSize = compactSize;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);
    Future<void> boot(ScriptedConnector c) async {
      await tester.pumpWidget(
        _wrap(
          AppBootstrap(
            connect: c.call,
            storage: MemoryAppStorage(),
            now: () => testNow,
            fontFamily: _family,
          ),
        ),
      );
      await settle(tester);
    }

    final loading = ScriptedConnector([])..gate = Completer<void>();
    await boot(loading);
    await _shot(tester, 'app_startup_loading');
    loading.gate!.complete();
    await settle(tester);
    await unmount(tester);
    for (final (failure, name) in [
      (StartupFailure.channelUnavailable, 'app_startup_channel_unavailable'),
      (StartupFailure.protocolMismatch, 'app_startup_protocol_mismatch'),
      (StartupFailure.noBackend, 'app_startup_no_backend'),
    ]) {
      await boot(ScriptedConnector([AppStartupException(failure)]));
      await _shot(tester, name);
      await unmount(tester);
    }
  }, skip: _dir == null);

  testWidgets('M2-A1 screens', (tester) async {
    final rig = AppRig.create(
      entries: [
        ...sampleHistory(),
        HistoryEntry(
          id: 'h6',
          uri: 'demo:fireworks',
          displayName: '烟花.gif',
          kind: MediaKind.imageAnimated,
          lastOpenedAtEpochMs: testNow
              .subtract(const Duration(days: 6))
              .millisecondsSinceEpoch,
        ),
      ],
    );
    await rig.pump(tester, fontFamily: _family, wrap: _wrap);
    await tapText(tester, '沙丘.heic');
    await settle(tester, 8);
    final page = tester.state<ImagePageState>(find.byType(ImagePage));
    page.session!.setControlsVisible(true);
    await tester.tap(find.bySemanticsLabel('收藏这张图片'));
    await settle(tester, 4);
    await _shot(tester, 'm2_app_image_favorited');
    await tester.tap(find.bySemanticsLabel('为这张图片添加标签'));
    await settle(tester, 4);
    await tester.enterText(find.byType(TextField), '沙漠');
    await tester.tap(find.text('添加'));
    await tester.pump();
    await _shot(tester, 'm2_app_tag_editor');
    await tester.tap(find.text('完成'));
    await settle(tester, 4);
    page.session!.setControlsVisible(true);
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester, 8);
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 200)),
    );
    await _shot(tester, 'm2_app_image_next_animated');
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await _shot(tester, 'm2_app_home_favorite_tags');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M4-A1 screens', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester, fontFamily: _family, wrap: _wrap);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    for (final n in ['山谷黄昏.mkv', '家庭录像.avi']) {
      await tapText(tester, n);
      await tester.pump();
    }
    await tester.tap(find.textContaining('打开 2 个'));
    await settle(tester, 4);
    await tapText(tester, '拼接为一个视频');
    await settle(tester, 8);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await tester.tap(find.bySemanticsLabel('最近工程'));
    await settle(tester, 4);
    await _shot(tester, 'm4_app_recent_projects');
    await unmount(tester);
  }, skip: _dir == null);

  testWidgets('M5A-A1 screens (design page 25)', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester, fontFamily: _family, wrap: _wrap);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    for (final n in ['山谷黄昏.mkv', '家庭录像.avi']) {
      await tapText(tester, n);
      await tester.pump();
    }
    await tester.tap(find.textContaining('打开 2 个'));
    await settle(tester, 4);
    await tapText(tester, '拼接为一个视频');
    await settle(tester, 8);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await settle(tester, 2);
    unawaited(e.maskEditor!.addManualMask());
    await settle(tester, 2);
    await tapText(tester, '头像');
    await settle(tester, 4);
    await _shot(tester, 'm5a_app_avatar_pick');
    await tapText(tester, '拍一张');
    await settle(tester, 8);
    await _shot(tester, 'm5a_app_avatar_adjust');
    await tapText(tester, '使用此头像');
    await settle(tester, 4);
    await _shot(tester, 'm5a_app_editor_avatar_style');
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  }, skip: _dir == null);

  // APP-LIB-A1: design pages 26 (tablet library) and 27 (PIN, phone list,
  // drawer, import, settings).
  testWidgets('APP-LIB-A1 screens', (tester) async {
    Future<AppRig> library(Size size, {bool pin = false}) async {
      final rig = libraryRig(
        videos: 30,
        images: 12,
        folders: const ['旅行', '家人', '宠物', '工作'],
        inFirst: 42,
        settings: {'setUpDone': true},
      );
      await rig.pump(tester, size: size, fontFamily: _family, wrap: _wrap);
      await openLibrary(tester);
      if (pin) {
        await AppScope.of(
          tester.element(find.byType(LibraryGate)),
        ).libraryLock.setPin('123456');
        await settle(tester, 2);
      }
      return rig;
    }

    // Page 26: tablet, folder "旅行" selected.
    await library(expandedSize, pin: true);
    await tester.tap(find.text('旅行'));
    await settle(tester, 2);
    await _shot(tester, 'applib_p26_tablet');
    await tester.tap(find.bySemanticsLabel('收起文件夹栏'));
    await settle(tester, 2);
    await _shot(tester, 'applib_p26_tablet_bar_hidden');
    await unmount(tester);

    // Page 27: PIN, phone list (page 2, videos), drawer, settings.
    await library(compactSize, pin: true);
    await tester.tap(find.bySemanticsLabel('立即上锁'));
    await settle(tester, 2);
    for (final c in ['1', '2', '3']) {
      await tester.tap(find.bySemanticsLabel('数字 $c'));
      await tester.pump();
    }
    await settle(tester, 1);
    await _shot(tester, 'applib_p27_pin');
    for (final c in ['4', '5', '6']) {
      await tester.tap(find.bySemanticsLabel('数字 $c'));
      await tester.pump();
    }
    await settle(tester, 2);
    await tester.tap(find.text('视频'));
    await settle(tester, 2);
    await tester.tap(find.bySemanticsLabel('下一页'));
    await settle(tester, 2);
    await _shot(tester, 'applib_p27_phone_list');
    await tester.tap(find.bySemanticsLabel('显示文件夹栏').first);
    await settle(tester, 3);
    await tester.longPress(find.text('旅行').last);
    await settle(tester, 3);
    await _shot(tester, 'applib_p27_drawer_folder_menu');
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    await tester.tap(find.bySemanticsLabel('媒体库设置'));
    await settle(tester, 3);
    await _shot(tester, 'applib_p27_settings');
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    await tester.tap(find.text('导入'));
    await settle(tester, 2);
    await _shot(tester, 'applib_p27_import_picker');
    await unmount(tester);
  }, skip: _dir == null);
}
