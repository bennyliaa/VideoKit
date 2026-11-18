// UI-AUDIT-A4: the Fake's timeline media (thumbnails, waveform; design
// pages 15/16) and the mask effects its demo preview draws (page 17).
import 'package:flutter/painting.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

void main() {
  Future<(FakeVideoKit, FakeEditProject, String)> project() async {
    final kit = FakeVideoKit();
    final p =
        await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
    final add = p.addSource(
      const VideoKitMediaSource(
        mediaToken: 'clip-a',
        mediaKind: MediaKind.video,
        sourceRef: DemoSourceRef('normal'),
      ),
    );
    await kit.clock.advance(const Duration(milliseconds: 300));
    final src = await add;
    await p.apply(AddClip(src.sourceId, 0, 4000000));
    return (kit, p, src.sourceId);
  }

  test('the Fake project offers timeline media', () async {
    final (_, p, _) = await project();
    expect(p, isA<VideoKitEditMediaPreview>());
  });

  test('thumbnails: bounded size, aspect kept, frames differ', () async {
    final (_, p, src) = await project();
    final probe = p.state.value.timeline.sourceById(src)!.probe!;
    final a = await p.sourceThumbnail(src, 0, maxWidth: 160, maxHeight: 90);
    final b = await p.sourceThumbnail(src, 2000000, maxWidth: 160, maxHeight: 90);
    expect(a, isNotNull);
    expect(b, isNotNull);
    expect(a, isNot(equals(b)), reason: 'neighbouring frames differ');
    final w = 160;
    final h = (w * probe.height / probe.width).round().clamp(1, 90);
    expect(FakeAvatarTools.decodePng(a!, w, h), isNotNull);
    expect(await p.sourceThumbnail('nope', 0), isNull);
  });

  test('waveform: buckets in 0–1, deterministic; none after close', () async {
    final (_, p, src) = await project();
    final hasAudio = p.state.value.timeline.sourceById(src)!.probe!.hasAudio;
    final w1 = await p.sourceWaveform(src, 0, 4000000, 40);
    final w2 = await p.sourceWaveform(src, 0, 4000000, 40);
    if (hasAudio) {
      expect(w1, hasLength(40));
      expect(w1.every((v) => v >= 0 && v <= 1), isTrue);
      expect(w1, w2);
    } else {
      expect(w1, isEmpty);
    }
    expect(await p.sourceWaveform('nope', 0, 1, 4), isEmpty);
    await p.close();
    expect(await p.sourceWaveform(src, 0, 4000000, 40), isEmpty);
    expect(await p.sourceThumbnail(src, 0), isNull);
  });

  test('demo preview effects: mosaic / blur masks at the playhead', () async {
    final (_, p, _) = await project();
    const region = MaskRegion(x: 0.1, y: 0.1, width: 0.3, height: 0.3);
    final id =
        (await p.apply(const AddMask(MaskType.manual, region, 0, 2000000))
                as EditApplied)
            .createdId!;
    var fx = demoMaskEffects(p.state.value, 1000000);
    expect(fx, hasLength(1));
    expect(fx.single.style, MaskStyle.mosaic);
    expect(fx.single.region, region);
    await p.apply(SetMaskStyle(id, MaskStyle.blur, 0.8));
    fx = demoMaskEffects(p.state.value, 1000000);
    expect((fx.single.style, fx.single.strength), (MaskStyle.blur, 0.8));
    expect(demoMaskEffects(p.state.value, 3000000), isEmpty, reason: 'outside');
    final painter = DemoPicturePainter(seed: 1, positionUs: 0, effects: fx);
    expect(
      painter.shouldRepaint(DemoPicturePainter(seed: 1, positionUs: 0)),
      isTrue,
    );
    // A mosaic cell shows the scene colour (bars at the top).
    expect(
      painter.sceneColorAt(const Offset(1, 1), const Size(700, 400)),
      DemoPicturePainter.bars.first,
    );
  });

  test('the preview session carries the project state', () async {
    final (kit, p, _) = await project();
    final pending = p.previewSession();
    await kit.clock.advance(const Duration(seconds: 2));
    final s = await pending as FakeSession;
    expect(s.previewOf, isNotNull);
    expect(identical(s.previewOf!.value, p.state.value), isTrue);
  });
}
