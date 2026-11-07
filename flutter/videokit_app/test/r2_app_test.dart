// TEST-R2 regressions in the App: R2-01 back with a panel open, R2-02
// concurrent history writes, R2-03 opening never finishes / is released,
// R2-07 the floating button and the list end.
import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/history/history_store.dart';
import 'package:videokit_app/host/app_host.dart';
import 'package:videokit_app/pages/image_page.dart';
import 'package:videokit_app/pages/player_page.dart';
import 'package:videokit_app/picker/media_picker.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// Storage whose writes always fail.
final class FailingStorage implements AppStorage {
  final MemoryAppStorage _inner = MemoryAppStorage();

  @override
  Future<void> write(String name, String content) async =>
      throw const FileSystemException('disk full');

  @override
  dynamic noSuchMethod(Invocation i) => super.noSuchMethod(i);

  @override
  Future<String?> read(String name) => _inner.read(name);

  @override
  Future<void> deleteFile(String path) => _inner.deleteFile(path);
}

Future<void> openTile(WidgetTester tester, String name) async {
  await tapText(tester, name);
  await settle(tester, 8);
}

void main() {
  group('R2-01 back key with a panel open', () {
    testWidgets('player: 参数 panel closes, the page stays', (tester) async {
      final rig = AppRig.create(entries: sampleHistory());
      await rig.pump(tester);
      await openTile(tester, '山谷黄昏.mkv');
      final player = tester.state<VideoKitPlayerState>(
        find.byType(VideoKitPlayer),
      );
      player.openPanel(PlayerPanel.mediaInfo);
      await settle(tester, 2);
      expect(player.hasOpenPanel, isTrue);
      await tester.binding.handlePopRoute();
      await settle(tester, 15); // 3 s
      expect(find.byType(PlayerPage), findsOneWidget, reason: 'page stays');
      expect(find.byType(MediaInfoSheet), findsNothing, reason: 'panel shut');
      // The next back press leaves.
      await tester.binding.handlePopRoute();
      await settle(tester, 8);
      expect(find.byType(PlayerPage), findsNothing);
      await unmount(tester);
    });

    testWidgets('image: 图片信息 panel closes, the page stays', (tester) async {
      final rig = AppRig.create(entries: sampleHistory());
      await rig.pump(tester);
      await openTile(tester, '沙丘.heic');
      final viewer = tester.state<VideoKitImageViewerState>(
        find.byType(VideoKitImageViewer),
      );
      viewer.openInfo();
      await settle(tester, 2);
      expect(viewer.hasOpenPanel, isTrue);
      await tester.binding.handlePopRoute();
      await settle(tester, 15);
      expect(find.byType(ImagePage), findsOneWidget);
      expect(find.byType(ImageInfoSheet), findsNothing);
      await tester.binding.handlePopRoute();
      await settle(tester, 8);
      expect(find.byType(ImagePage), findsNothing);
      await unmount(tester);
    });
  });

  group('R2-02 history writes', () {
    test(
      'file storage: concurrent writes of one file all succeed, last wins',
      () async {
        final dir = await Directory.systemTemp.createTemp('vk_r2_02_');
        addTearDown(() => dir.delete(recursive: true));
        final storage = FileAppStorage(dir);
        await Future.wait([
          for (var i = 0; i < 25; i++) storage.write('history.json', 'v$i'),
        ]);
        expect(await storage.read('history.json'), 'v24');
        final leftovers = dir.listSync().whereType<File>().where(
          (f) => f.path.endsWith('.tmp'),
        );
        expect(leftovers, isEmpty, reason: 'no temporary files left');
      },
    );

    test(
      'a failing write is logged, opening still records the entry',
      () async {
        final store = HistoryStore(
          storage: FailingStorage(),
          picker: DemoMediaPicker(),
        );
        final e = await store.recordOpened(
          const PickedMedia(
            uri: 'demo:valley',
            displayName: '山谷黄昏.mkv',
            kind: MediaKind.video,
          ),
        );
        expect(e.uri, 'demo:valley');
        expect(store.entries, hasLength(1));
        await expectLater(
          writeQuietly(FailingStorage(), 'x.json', '{}'),
          completes,
        );
      },
    );
  });

  group('R2-03 opening reaches a final state', () {
    testWidgets('no answer within the timeout → error with 重试, which opens '
        'again', (tester) async {
      final hosts = AppHostCallbacks();
      final kit = FakeVideoKit(
        config: VideoKitConfig(hostCallbacks: hosts),
        scenarioOverrides: {
          'demo:valley': const Scenario.slowLoad(Duration(minutes: 5)),
        },
      );
      final rig = AppRig.create(
        entries: sampleHistory(),
        backend: DemoBackend(kit: kit, hosts: hosts),
      );
      await rig.pump(tester);
      await openTile(tester, '山谷黄昏.mkv');
      final page = tester.state<PlayerPageState>(find.byType(PlayerPage));
      expect(page.openFailed, isFalse);
      for (var i = 0; i < 50; i++) {
        await tester.pump(const Duration(seconds: 1));
      }
      expect(page.openFailed, isTrue, reason: '45 s without an answer');
      expect(find.text('没有打开成功'), findsOneWidget);
      expect(find.text('重试'), findsOneWidget);
      final first = page.session;
      await tester.tap(find.text('重试'));
      await settle(tester, 4);
      expect(page.openFailed, isFalse);
      expect(identical(page.session, first), isFalse, reason: 'new session');
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      await unmount(tester);
      // Let the second open's timeout timer run out.
      await tester.pump(const Duration(seconds: 50));
    });

    testWidgets('session released while opening → error, not "正在打开"', (
      tester,
    ) async {
      final hosts = AppHostCallbacks();
      final kit = FakeVideoKit(
        config: VideoKitConfig(hostCallbacks: hosts),
        scenarioOverrides: {
          'demo:valley': const Scenario.slowLoad(Duration(seconds: 20)),
        },
      );
      final rig = AppRig.create(
        entries: sampleHistory(),
        backend: DemoBackend(kit: kit, hosts: hosts),
      );
      await rig.pump(tester);
      await openTile(tester, '山谷黄昏.mkv');
      final page = tester.state<PlayerPageState>(find.byType(PlayerPage));
      // As the native side did in R2-03: the player goes away mid-open.
      unawaited(page.session!.release());
      await settle(tester, 4);
      expect(page.openFailed, isTrue);
      expect(find.text('没有打开成功'), findsOneWidget);
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      await unmount(tester);
      await tester.pump(const Duration(seconds: 50));
    });
  });

  for (final scale in [1.0, 2.0]) {
    testWidgets('R2-07: list end clears the floating button (text × $scale)', (
      tester,
    ) async {
      final rig = AppRig.create(entries: sampleHistory());
      await rig.pump(tester, textScale: scale);
      final list = find.byType(Scrollable).first;
      await tester.drag(list, const Offset(0, -20000));
      await settle(tester, 4);
      final footer = tester.getRect(find.textContaining('最多保存').last);
      final fab = tester.getRect(
        find.ancestor(of: find.text('打开文件'), matching: find.byType(VkButton)),
      );
      expect(footer.bottom, lessThanOrEqualTo(fab.top), reason: 'footer');
      await unmount(tester);
    });
  }
}
