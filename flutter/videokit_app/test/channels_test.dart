// M1-A1 item 2, Dart side: the documents / incoming channel contract with
// mocked platform channels (the Kotlin side is not run in this batch).
import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/picker/channel_media_picker.dart';
import 'package:videokit_app/picker/media_picker.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  const documents = MethodChannel(AppDocumentChannels.documents);
  const incoming = EventChannel(AppDocumentChannels.incoming);
  final calls = <MethodCall>[];

  void answer(Object? Function(MethodCall call) reply) {
    calls.clear();
    messenger.setMockMethodCallHandler(documents, (call) async {
      calls.add(call);
      return reply(call);
    });
  }

  tearDown(() {
    messenger.setMockMethodCallHandler(documents, null);
    messenger.setMockStreamHandler(incoming, null);
  });

  const picker = ChannelMediaPicker();
  final ctx = _NoContext();

  test(
    'openDocuments: video+image MIME filter, multi-select, parsing',
    () async {
      answer(
        (_) => [
          {
            'uri': 'content://media/v1',
            'displayName': '山谷黄昏.mkv',
            'mimeType': 'video/x-matroska',
            'sizeBytes': 1234,
            'persistable': true,
          },
          {
            'uri': 'content://media/i1',
            'displayName': '沙丘.heic',
            'mimeType': 'image/heic',
            'persistable': true,
          },
          {
            'uri': 'content://media/g1',
            'displayName': '烟花.gif',
            'mimeType': 'image/gif',
            'persistable': false,
          },
        ],
      );
      final r = await picker.pick(ctx);
      expect(calls.single.method, 'openDocuments');
      expect(calls.single.arguments, {
        'mimeTypes': ['video/*', 'image/*'],
        'multiple': true,
      });
      expect(r.map((m) => m.kind), [
        MediaKind.video,
        MediaKind.imageStatic,
        MediaKind.imageUnknown,
      ]);
      expect(r.first.sizeBytes, 1234);
      expect(r.first.persistable, isTrue);
      expect(r.last.persistable, isFalse);
    },
  );

  test('openDocuments single / video only; cancel → empty', () async {
    answer((_) => <Object?>[]);
    final r = await picker.pick(ctx, multiple: false, kinds: {MediaKind.video});
    expect(r, isEmpty);
    expect(calls.single.arguments, {
      'mimeTypes': ['video/*'],
      'multiple': false,
    });
  });

  test('reselect sends the old URI and its kind filter', () async {
    answer(
      (_) => {
        'uri': 'content://media/new',
        'displayName': '旅行合集.mp4',
        'mimeType': 'video/mp4',
        'persistable': true,
      },
    );
    final r = await picker.reselect(
      ctx,
      const PickedMedia(
        uri: 'content://media/old',
        displayName: '旅行合集.mp4',
        kind: MediaKind.video,
      ),
    );
    expect(calls.single.method, 'reselect');
    expect(calls.single.arguments, {
      'uri': 'content://media/old',
      'mimeTypes': ['video/*'],
    });
    expect(r?.uri, 'content://media/new');
    answer((_) => null);
    expect(
      await picker.reselect(
        ctx,
        const PickedMedia(uri: 'u', displayName: 'n', kind: MediaKind.video),
      ),
      isNull,
    );
  });

  test('checkAccess maps OK / MISSING / REVOKED; releaseAccess', () async {
    for (final (wire, access) in [
      ('OK', MediaAccess.ok),
      ('MISSING', MediaAccess.missing),
      ('REVOKED', MediaAccess.revoked),
    ]) {
      answer((_) => wire);
      expect(await picker.checkAccess('content://x'), access);
      expect(calls.single.arguments, {'uri': 'content://x'});
    }
    answer((_) => null);
    await picker.releaseAccess('content://x');
    expect(calls.single.method, 'releaseAccess');
    expect(calls.single.arguments, {'uri': 'content://x'});
  });

  test('incoming: one list per intent (cold + warm start)', () async {
    final events = StreamController<Object?>();
    messenger.setMockStreamHandler(
      incoming,
      MockStreamHandler.inline(
        onListen: (_, sink) => events.stream.listen(sink.success),
      ),
    );
    final got = <List<PickedMedia>>[];
    final sub = picker.incoming.listen(got.add);
    events
      ..add([
        {
          'uri': 'content://share/1',
          'displayName': 'a.mp4',
          'mimeType': 'video/mp4',
          'persistable': false,
        },
      ])
      ..add([
        {'uri': 'content://share/2', 'mimeType': 'image/png'},
        {'uri': 'content://share/3', 'mimeType': 'video/mp4'},
      ]);
    await pumpEventQueue();
    expect(got, hasLength(2));
    expect(got.first.single.persistable, isFalse);
    expect(got.last.map((m) => m.uri), [
      'content://share/2',
      'content://share/3',
    ]);
    // Missing names fall back to empty; the App shows the URI's name.
    expect(got.last.first.displayName, '');
    await sub.cancel();
    await events.close();
  });

  group('export 另存为', () {
    const target = ChannelExportTarget();

    test('cancelled dialog → null, no sink registered', () async {
      answer((_) => null);
      final s = await target.prepare(
        'app-export-1',
        suggestedName: 'VideoKit_20261107_200000.mp4',
        mimeType: 'video/mp4',
      );
      expect(s, isNull);
      expect(calls.map((c) => c.method), ['createDocument']);
      expect(calls.single.arguments, {
        'suggestedName': 'VideoKit_20261107_200000.mp4',
        'mimeType': 'video/mp4',
      });
    });

    test('chosen document → registered one-shot sink', () async {
      answer(
        (c) => c.method == 'createDocument' ? 'content://docs/out.mp4' : null,
      );
      final s = await target.prepare(
        'app-export-2',
        suggestedName: 'x.mp4',
        mimeType: 'video/mp4',
      );
      expect(calls.map((c) => c.method), [
        'createDocument',
        'registerExportSink',
      ]);
      expect(calls.last.arguments, {
        'sinkId': 'app-export-2',
        'uri': 'content://docs/out.mp4',
      });
      expect(s!.sinkRef, 'registered:app-export-2');
      expect(s.capabilities.fileDescriptor, isTrue);
      expect(s.capabilities.randomWrite, isTrue);
      answer((_) => null);
      await target.unregisterSink('app-export-2');
      expect(calls.single.arguments, {'sinkId': 'app-export-2'});
    });

    test('file type per container', () {
      expect(exportFileType('mp4'), ('mp4', 'video/mp4'));
      expect(exportFileType('WEBM'), ('webm', 'video/webm'));
      expect(exportFileType('mkv'), ('mkv', 'video/x-matroska'));
      expect(exportFileType(null), ('mp4', 'video/mp4'));
    });
  });
}

/// The channel picker never uses its context (the system UI is native).
final class _NoContext implements BuildContext {
  @override
  dynamic noSuchMethod(Invocation invocation) =>
      throw UnsupportedError('no context');
}
