import 'dart:async';
import 'dart:ui' as ui;

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

Future<T> _drive<T>(FakeClock clock, Future<T> f) async {
  var done = false;
  late T v;
  unawaited(
    f.then((x) {
      v = x;
      done = true;
    }),
  );
  for (var i = 0; !done && i < 100; i++) {
    await clock.advance(const Duration(milliseconds: 100));
  }
  return v;
}

void main() {
  loopingSnapshotTests();
  test('04A P2: mediaInfo filled after bind (video and image)', () async {
    final kit = FakeVideoKit();
    final s = await kit.createSession(const VideoKitSessionConfig());
    expect(s.state.value.mediaInfo, isNull);
    await _drive(
      kit.clock,
      s.bind(
        const VideoKitMediaSource(
          mediaToken: 'm1',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef('normal'),
          mimeType: 'video/mp4',
        ),
      ),
    );
    final info = s.state.value.mediaInfo!;
    expect(info.container, 'video/mp4');
    expect(info.videoCodec, 'video/avc');
    expect(info.width, 1920);
    expect(info.durationUs, s.state.value.durationUs);
    expect(info.fileSizeBytes, greaterThan(0));
    final img = await kit.createSession(const VideoKitSessionConfig());
    await _drive(
      kit.clock,
      img.bind(
        const VideoKitMediaSource(
          mediaToken: 'm2',
          mediaKind: MediaKind.imageStatic,
          sourceRef: DemoSourceRef('normal'),
          mimeType: 'image/heic',
        ),
      ),
    );
    expect(img.state.value.mediaInfo!.videoCodec, isNull);
    expect(img.state.value.mediaInfo!.container, 'image/heic');
    await kit.close();
  });

  testWidgets('04A P1: captureThumbnail fits the box, decodes, errors', (
    tester,
  ) async {
    final kit = FakeVideoKit();
    late FakeSession s;
    await tester.runAsync(() async {
      s = (await kit.createSession(
        const VideoKitSessionConfig(),
      )) as FakeSession;
    });
    final before = await s.captureThumbnail(0, 320, 180);
    expect(
      (before as ThumbnailFailed).error.code,
      ErrorCode.invalidState,
      reason: 'not bound',
    );
    await tester.runAsync(
      () => _drive(
        kit.clock,
        s.bind(
          const VideoKitMediaSource(
            mediaToken: 't1',
            mediaKind: MediaKind.video,
            sourceRef: DemoSourceRef('normal'),
          ),
        ),
      ),
    );
    final r = await s.captureThumbnail(1000000, 320, 320);
    final ok = r as ThumbnailCaptured;
    expect((ok.width, ok.height), (320, 180), reason: '16:9 inside 320×320');
    expect(ok.mimeType, 'image/png');
    expect(ok.bytes.sublist(0, 4), [0x89, 0x50, 0x4E, 0x47]);
    await tester.runAsync(() async {
      final codec = await ui.instantiateImageCodec(ok.bytes);
      final frame = await codec.getNextFrame();
      expect(frame.image.width, 320);
      expect(frame.image.height, 180);
    });
    final bad = await s.captureThumbnail(0, 0, 10);
    expect((bad as ThumbnailFailed).error.code, ErrorCode.invalidArgument);
    await tester.runAsync(() => _drive(kit.clock, s.release()));
    final gone = await s.captureThumbnail(0, 320, 180);
    expect((gone as ThumbnailFailed).error.code, ErrorCode.sessionReleased);
    await tester.runAsync(kit.close);
  });

  test('fitThumbnail never upscales and keeps the aspect', () {
    expect(fitThumbnail(1920, 1080, 320, 180), (320, 180));
    expect(fitThumbnail(1080, 1920, 320, 180), (101, 180));
    expect(fitThumbnail(100, 50, 320, 180), (100, 50));
  });
}

void loopingSnapshotTests() {
  test(
    '04A L3: initialState.looping overrides the default; captured back',
    () async {
      final kit = FakeVideoKit();
      final s = await kit.createSession(const VideoKitSessionConfig());
      await _drive(
        kit.clock,
        s.bind(
          const VideoKitMediaSource(
            mediaToken: 'l1',
            mediaKind: MediaKind.video,
            sourceRef: DemoSourceRef('normal'),
          ),
          initialState: const VideoKitPlaybackState(looping: true),
        ),
      );
      expect(s.state.value.looping, isTrue, reason: 'video default is false');
      expect((await s.captureState()).looping, isTrue);
      final img = await kit.createSession(const VideoKitSessionConfig());
      await _drive(
        kit.clock,
        img.bind(
          const VideoKitMediaSource(
            mediaToken: 'l2',
            mediaKind: MediaKind.imageStatic,
            sourceRef: DemoSourceRef('normal'),
          ),
          initialState: const VideoKitPlaybackState(looping: true),
        ),
      );
      expect(
        img.state.value.looping,
        isFalse,
        reason: 'still images never loop',
      );
      expect((await img.captureState()).looping, isNull);
      await kit.close();
    },
  );
}
