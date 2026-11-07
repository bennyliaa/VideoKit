import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/history/history_entry.dart';
import 'package:videokit_app/history/history_store.dart';
import 'package:videokit_app/picker/channel_media_picker.dart';
import 'package:videokit_app/picker/media_picker.dart';
import 'package:videokit_app/settings/app_settings.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

PickedMedia _media(int i, {bool persistable = true}) => PickedMedia(
  uri: 'demo:file$i',
  displayName: 'file$i.mp4',
  kind: MediaKind.video,
  persistable: persistable,
);

void main() {
  late MemoryAppStorage storage;
  late DemoMediaPicker picker;
  late HistoryStore store;

  setUp(() {
    storage = MemoryAppStorage();
    picker = DemoMediaPicker();
    store = HistoryStore(storage: storage, picker: picker, now: () => testNow);
  });

  group('HistoryStore (REQ-APP-07/08)', () {
    test('one record per file, newest first, reopen moves to top', () async {
      await store.recordOpened(_media(1));
      await store.recordOpened(_media(2));
      await store.recordOpened(_media(1));
      expect(store.entries.map((e) => e.uri), ['demo:file1', 'demo:file2']);
      expect(storage.documents['history.json'], isNotNull);
    });

    test(
      '200 limit: oldest evicted, permission and thumbnail released',
      () async {
        for (var i = 0; i < 205; i++) {
          await store.recordOpened(_media(i));
        }
        expect(store.entries, hasLength(HistoryStore.limit));
        expect(store.entries.last.uri, 'demo:file5');
        expect(picker.released, [for (var i = 0; i < 5; i++) 'demo:file$i']);
      },
    );

    test('snapshot round-trips through JSON and reload', () async {
      final e = await store.recordOpened(_media(1));
      final snap = VideoKitPlaybackState(
        mediaToken: 'demo:file1',
        positionUs: 42000000,
        speed: 1.5,
      );
      await store.updatePlayback(
        e.id,
        snapshot: snap,
        durationUs: 120000000,
        width: 1920,
        height: 1080,
      );
      final again = HistoryStore(
        storage: storage,
        picker: picker,
        now: () => testNow,
      );
      await again.load();
      final r = again.entries.single;
      expect(r.lastPositionUs, 42000000);
      expect(r.playbackState?.speed, 1.5);
      expect(r.durationUs, 120000000);
      expect(r.width, 1920);
    });

    test('broken files start empty; broken snapshots are dropped', () async {
      storage.documents['history.json'] = '{not json';
      await store.load();
      expect(store.entries, isEmpty);
      final entry = HistoryEntry(
        id: 'x',
        uri: 'demo:x',
        displayName: 'x',
        kind: MediaKind.video,
        lastOpenedAtEpochMs: 1,
      ).toJson()..['playbackState'] = {'schemaVersion': 999};
      storage.documents['history.json'] = jsonEncode({
        'entries': [entry],
      });
      await store.load();
      expect(store.entries.single.playbackState, isNull);
    });

    test('remove/clear delete thumbnails and release permissions', () async {
      final a = await store.recordOpened(_media(1));
      await store.recordOpened(_media(2, persistable: false));
      storage.documents['history.json'] = jsonEncode({
        'entries': [
          a.copyWith(thumbnailPath: '/t/a.png').toJson(),
          ...[for (final e in store.entries.skip(1)) e.toJson()],
        ],
      });
      await store.load();
      await store.remove(a.id);
      expect(storage.deleted, ['/t/a.png']);
      expect(picker.released, ['demo:file1']);
      await store.clear();
      expect(store.entries, isEmpty);
      expect(picker.released, [
        'demo:file1',
      ], reason: 'temporary grants have nothing to release');
    });

    test('unavailable, relink, reset position', () async {
      final e = await store.recordOpened(_media(1));
      await store.updatePlayback(e.id, positionUs: 5000000);
      await store.markUnavailable(e.id);
      expect(store.byId(e.id)!.unavailable, isTrue);
      final r = await store.relink(e.id, _media(9));
      expect(r!.uri, 'demo:file9');
      expect(r.unavailable, isFalse);
      expect(r.lastPositionUs, 5000000, reason: 'position kept');
      expect(picker.released, ['demo:file1']);
      await store.resetPosition(e.id);
      expect(store.byId(e.id)!.lastPositionUs, isNull);
    });
  });

  group('AppSettings', () {
    test('defaults and JSON', () {
      const s = AppSettings();
      expect(s.recordHistory, isTrue);
      expect(s.reduceMotion, isNull, reason: 'follows the system');
      final t = s.copyWith(
        recordHistory: false,
        themeMode: VideoKitThemeMode.light,
        reduceMotion: () => true,
        layout: HomeLayout.grid,
      );
      expect(AppSettings.fromJson(t.toJson()), t);
      expect(AppSettings.fromJson(const {'themeMode': 'nope'}), s);
    });
  });

  group('ChannelMediaPicker (M2 contract)', () {
    TestWidgetsFlutterBinding.ensureInitialized();
    test('maps documents and access results', () async {
      final calls = <MethodCall>[];
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
          .setMockMethodCallHandler(
            const MethodChannel(AppDocumentChannels.documents),
            (call) async {
              calls.add(call);
              return switch (call.method) {
                'checkAccess' => 'MISSING',
                'releaseAccess' => null,
                _ => null,
              };
            },
          );
      const p = ChannelMediaPicker();
      expect(await p.checkAccess('content://x'), MediaAccess.missing);
      await p.releaseAccess('content://x');
      expect(calls.map((c) => c.method), ['checkAccess', 'releaseAccess']);
      final m = ChannelMediaPicker.fromMap({
        'uri': 'content://a',
        'displayName': 'a.mp4',
        'mimeType': 'video/mp4',
        'persistable': true,
      });
      expect(m.kind, MediaKind.video);
      expect(m.persistable, isTrue);
      expect(
        ChannelMediaPicker.fromMap({'uri': 'u', 'mimeType': 'image/gif'}).kind,
        MediaKind.imageUnknown,
      );
    });
  });
}
