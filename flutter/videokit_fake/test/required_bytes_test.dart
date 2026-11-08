// J8 (UI-AUDIT-A1, TEST-R4): OUTPUT_SPACE_INSUFFICIENT carries
// `requiredBytes` = the bytes still to free (spec/errors.json).
import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

const _video = VideoKitMediaSource(
  mediaToken: 'j8-video',
  mediaKind: MediaKind.video,
  sourceRef: DemoSourceRef('normal'),
);

void main() {
  Future<(FakeVideoKit, FakeEditProject)> project([Scenario? sc]) async {
    final kit = FakeVideoKit(defaultScenario: sc ?? const Scenario.normal());
    final p =
        await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
    final add = p.addSource(_video);
    await kit.clock.advance(const Duration(milliseconds: 300));
    final src = await add;
    await p.apply(AddClip(src.sourceId, 0, 10000000));
    return (kit, p);
  }

  test(
    'precheck: requiredBytes is the estimate minus the free space',
    () async {
      final (_, p) = await project();
      const free = 1000;
      final pre = await p.checkExport(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(
          sinkRef: 'demo:t',
          capabilities: SinkCapabilities(knownFreeSpaceBytes: free),
        ),
      );
      final e = pre.problems.singleWhere(
        (e) => e.code == ErrorCode.outputSpaceInsufficient,
      );
      final size = pre.estimate.sizeBytes!;
      expect(int.parse(e.params['requiredBytes']!), size - free);
      expect(e.suggestedAction, SuggestedAction.freeSpace);
    },
  );

  test('enough space: no problem, no requiredBytes', () async {
    final (_, p) = await project();
    final pre = await p.checkExport(
      const VideoKitExportRequest(),
      const VideoKitOutputSink(
        sinkRef: 'demo:t',
        capabilities: SinkCapabilities(knownFreeSpaceBytes: 1 << 50),
      ),
    );
    expect(
      pre.problems.where((e) => e.code == ErrorCode.outputSpaceInsufficient),
      isEmpty,
    );
  });

  test(
    'a sink running out of space mid-export reports requiredBytes',
    () async {
      final (kit, p) = await project(Scenario.exportFails());
      final done = p.export(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      VideoKitExportResult? r;
      unawaited(done.then((x) => r = x));
      for (var i = 0; i < 200 && r == null; i++) {
        await kit.clock.advance(const Duration(milliseconds: 250));
      }
      final failed = r! as ExportFailed;
      expect(failed.error.code, ErrorCode.outputSpaceInsufficient);
      expect(int.parse(failed.error.params['requiredBytes']!), greaterThan(0));
    },
  );
}
