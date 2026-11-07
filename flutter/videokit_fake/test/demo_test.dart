import 'dart:convert';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

void main() {
  test('demo data is deterministic for a fixed seed', () {
    final a = DemoDataGenerator(seed: 42);
    final b = DemoDataGenerator(seed: 42);
    final c = DemoDataGenerator(seed: 43);
    expect(a.manifestJson(), b.manifestJson());
    expect(a.manifest()['contentSha256'], isNot(c.manifest()['contentSha256']));
    final m = jsonDecode(a.manifestJson()) as Map<String, Object?>;
    expect(m['seed'], 42);
    expect(m['params'], {'mediaCount': 12});
    expect((m['contentSha256']! as String).length, 64);
    expect(m['generatorVersion'], DemoDataGenerator.generatorVersion);
  });

  test('media items cover video, static, animated and abnormal scenarios', () {
    final items = DemoDataGenerator().media();
    expect(items, hasLength(12));
    final kinds = items.map((i) => i.kind).toSet();
    expect(
      kinds,
      containsAll([
        MediaKind.video,
        MediaKind.imageStatic,
        MediaKind.imageAnimated,
      ]),
    );
    expect(
      items.map((i) => i.scenarioId).toSet(),
      containsAll(['normal', 'unsupported', 'corrupt', 'disconnect']),
    );
    for (final i in items) {
      final src = i.toMediaSource();
      expect(src.sourceRef, isA<DemoSourceRef>());
      expect(src.mediaToken, startsWith('demo-'));
      if (i.kind == MediaKind.video) {
        expect(i.durationUs, greaterThanOrEqualTo(60000000));
      }
    }
    expect(items.map((i) => i.mediaToken).toSet(), hasLength(12));
  });

  test('profileFor is stable per token', () {
    const src = VideoKitMediaSource(
      mediaToken: 'x',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('buffering'),
    );
    final p1 = DemoDataGenerator.profileFor(src);
    final p2 = DemoDataGenerator.profileFor(src);
    expect(p1.durationUs, p2.durationUs);
    expect(p1.scenarioId, 'buffering');
    expect(stableHash('abc'), stableHash('abc'));
    expect(DemoRandom(1).nextUint32(), DemoRandom(1).nextUint32());
  });

  testWidgets('DemoPicture paints timecode and watermark without errors', (
    tester,
  ) async {
    await tester.pumpWidget(
      const Directionality(
        textDirection: TextDirection.ltr,
        child: SizedBox(
          width: 320,
          height: 180,
          child: DemoPicture(
            seed: 7,
            semanticLabel: 'demo label',
            positionUs: 65000000,
            durationUs: 120000000,
          ),
        ),
      ),
    );
    expect(find.byType(CustomPaint), findsWidgets);
    expect(find.bySemanticsLabel('demo label'), findsOneWidget);
    final painter = DemoPicturePainter(seed: 7, positionUs: 1);
    expect(
      painter.shouldRepaint(DemoPicturePainter(seed: 7, positionUs: 2)),
      isTrue,
    );
    expect(
      painter.shouldRepaint(DemoPicturePainter(seed: 7, positionUs: 1)),
      isFalse,
    );
  });

  testWidgets('DemoSessionPicture follows a fake session', (tester) async {
    final kit = FakeVideoKit();
    final s = await kit.createSession(const VideoKitSessionConfig());
    await tester.pumpWidget(
      Directionality(
        textDirection: TextDirection.ltr,
        child: DemoSessionPicture(session: s),
      ),
    );
    expect(find.byType(DemoPicture), findsOneWidget);
    await tester.runAsync(s.release);
    await tester.pump();
  });
}
