// M4-A2: the edit project snapshot, schema v1 as frozen by 04A E2.
// Checked against spec/schema/edit-project.v1.json once Coder B adds it
// (M4-B1); until then these tests pin the E2 rules.
import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

const _video = VideoKitMediaSource(
  mediaToken: 'schema-video',
  mediaKind: MediaKind.video,
  sourceRef: DemoSourceRef('normal'),
);

const _region = MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2);

void main() {
  Future<(FakeVideoKit, FakeEditProject)> project() async {
    final kit = FakeVideoKit();
    final p =
        await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
    final add = p.addSource(_video);
    await kit.clock.advance(const Duration(milliseconds: 300));
    final src = await add;
    await p.apply(AddClip(src.sourceId, 0, 3000000));
    return (kit, p);
  }

  Future<Map<String, Object?>> json(VideoKitEditProject p) async =>
      jsonDecode((await p.snapshot()).json) as Map<String, Object?>;

  Future<FakeEditProject> withAcceptedRangeAndExport() async {
    final (kit, p) = await project();
    final mask = (await p.apply(
      const AddMask(MaskType.face, _region, 0, 2000000),
    ) as EditApplied).createdId!;
    await p.apply(AcceptTrackingRange(mask, 0, 2000000));
    final done = p.export(
      const VideoKitExportRequest(presetId: ExportPresets.p720),
      const VideoKitOutputSink(sinkRef: 'demo:t'),
    );
    VideoKitExportResult? r;
    unawaited(done.then((x) => r = x));
    for (var i = 0; i < 200 && r == null; i++) {
      await kit.clock.advance(const Duration(milliseconds: 250));
    }
    expect(r, isA<ExportSucceeded>());
    return p;
  }

  test('E2 1-4: top level, ranges as objects, accepted ranges on the mask, '
      'tracking without runtime fields', () async {
    final p = await withAcceptedRangeAndExport();
    final j = await json(p);
    expect(j['schemaVersion'], 1);
    expect(j['createdAt'], isA<int>());
    expect(j['updatedAt'], isA<int>());
    expect(
      j['updatedAt']! as int,
      greaterThanOrEqualTo(j['createdAt']! as int),
    );
    expect(j['exportPresetId'], ExportPresets.p720);
    final mask = (j['masks']! as List).single as Map<String, Object?>;
    expect(mask['rangeUs'], {'startUs': 0, 'endUs': 2000000});
    expect(mask['acceptedRanges'], [
      {'startUs': 0, 'endUs': 2000000},
    ]);
    final run = (j['tracking']! as List).single as Map<String, Object?>;
    expect(run.keys.toSet(), {'maskId', 'status', 'coverage'});
    for (final c in run['coverage']! as List) {
      expect((c as Map).keys.toSet(), {'startUs', 'endUs', 'quality'});
    }
    expect(jsonEncode(j).contains('"accepted"'), isFalse);
    expect(jsonEncode(j).contains('requestId'), isFalse);
  });

  test('round trip: restore, snapshot again, same JSON; accepted ranges '
      'come back', () async {
    final p = await withAcceptedRangeAndExport();
    final first = await p.snapshot();
    final kit = FakeVideoKit();
    final restored = await kit.restoreEditProject(first, EditProjectConfig());
    final again = await restored.snapshot();
    expect(jsonDecode(again.json), jsonDecode(first.json));
    final segments = restored
        .state
        .value
        .tracking
        .values
        .single
        .coverage
        .segments
        .where((s) => s.accepted);
    expect(segments.map((s) => (s.startUs, s.endUs)), [(0, 2000000)]);
    // 04A E4: the range lives on the mask; coverage `accepted` derives it.
    expect(restored.state.value.masks.single.acceptedRanges, const [
      TimeRangeUs(0, 2000000),
    ]);
  });

  test('E2 6: missing optional fields read as defaults', () async {
    final kit = FakeVideoKit();
    final p = await kit.restoreEditProject(
      SerializedEditProject(
        schemaVersion: 1,
        json: jsonEncode({
          'schemaVersion': 1,
          'projectId': 'minimal',
          'sources': [
            {
              'sourceId': 'src-1',
              'mediaToken': 't',
              'probe': {'durationUs': 3000000, 'width': 1920, 'height': 1080},
            },
          ],
          'timeline': {
            'clips': [
              {
                'clipId': 'clip-2',
                'sourceId': 'src-1',
                'inUs': 0,
                'outUs': 1000000,
              },
            ],
          },
        }),
      ),
      EditProjectConfig(),
    );
    final st = p.state.value;
    expect(st.timeline.clips.single.durationUs, 1000000);
    expect(st.masks, isEmpty);
    expect(st.tracking, isEmpty);
    final j = await json(p);
    expect(j['exportPresetId'], isNull);
    expect(j['createdAt'], 0);
  });

  test('E2 6: a higher major version is rejected (outer or inner)', () async {
    final kit = FakeVideoKit();
    for (final s in [
      const SerializedEditProject(schemaVersion: 2, json: '{}'),
      SerializedEditProject(
        schemaVersion: 1,
        json: jsonEncode({'schemaVersion': 2}),
      ),
    ]) {
      await expectLater(
        kit.restoreEditProject(s, EditProjectConfig()),
        throwsA(
          isA<VideoKitException>().having(
            (e) => e.error.code,
            'code',
            ErrorCode.unsupportedSnapshotVersion,
          ),
        ),
      );
    }
  });

  test('E2 6: the migration framework upgrades synthetic v0 data', () async {
    // The pre-freeze Dart form: ranges as arrays, `accepted` on coverage,
    // coverage `state`, runtime fields in tracking, no timestamps.
    final v0 = {
      'schemaVersion': 0,
      'projectId': 'old',
      'revision': 4,
      'sources': [
        {
          'sourceId': 'src-1',
          'mediaToken': 't',
          'probe': {'durationUs': 3000000, 'width': 1920, 'height': 1080},
        },
      ],
      'timeline': {
        'clips': [
          {
            'clipId': 'clip-2',
            'sourceId': 'src-1',
            'inUs': 0,
            'outUs': 3000000,
          },
        ],
      },
      'masks': [
        {
          'maskId': 'mask-3',
          'type': 'FACE',
          'style': 'MOSAIC',
          'strength': 0.5,
          'enabled': true,
          'rangeUs': [0, 2000000],
          'keyframes': <Object?>[],
        },
      ],
      'tracking': [
        {
          'maskId': 'mask-3',
          'requestId': 'track-4',
          'projectRevision': 3,
          'kind': 'FACE',
          'progress': 1.0,
          'status': 'CANCELLED',
          'coverage': [
            {
              'startUs': 0,
              'endUs': 500000,
              'state': 'NOT_ANALYZED',
              'accepted': false,
            },
            {
              'startUs': 500000,
              'endUs': 1000000,
              'state': 'NOT_ANALYZED',
              'accepted': true,
            },
          ],
        },
      ],
    };
    expect(FakeEditProjectCodec.migrations.keys, contains(0));
    final kit = FakeVideoKit();
    final p = await kit.restoreEditProject(
      SerializedEditProject(schemaVersion: 0, json: jsonEncode(v0)),
      EditProjectConfig(),
    );
    final st = p.state.value;
    expect(st.masks.single.startUs, 0);
    expect(st.masks.single.endUs, 2000000);
    final segs = st.tracking['mask-3']!.coverage.segments;
    expect(segs.map((s) => s.accepted), [false, true]);
    final j = await json(p);
    expect(j['schemaVersion'], 1);
    final mask = (j['masks']! as List).single as Map<String, Object?>;
    expect(mask['acceptedRanges'], [
      {'startUs': 500000, 'endUs': 1000000},
    ]);
  });

  test('E2 (b): the current schemaMinor (1) is written; a higher minor of the same '
      'major reads, unknown fields ignored', () async {
    final (_, p) = await project();
    final j = await json(p);
    expect(j['schemaVersion'], 1);
    expect(j['schemaMinor'], FakeEditProjectCodec.currentSchemaMinor);
    final newer = {
      ...j,
      'schemaMinor': 7,
      'someFutureField': {'x': 1},
    };
    final kit = FakeVideoKit();
    final restored = await kit.restoreEditProject(
      SerializedEditProject(schemaVersion: 1, json: jsonEncode(newer)),
      EditProjectConfig(),
    );
    expect(restored.state.value.timeline.clips, p.state.value.timeline.clips);
    expect((await json(restored))['schemaMinor'], 1);
  });

  test('E2 6: a version with no migration step is rejected', () async {
    final kit = FakeVideoKit();
    await expectLater(
      kit.restoreEditProject(
        SerializedEditProject(
          schemaVersion: -1,
          json: jsonEncode({'schemaVersion': -1}),
        ),
        EditProjectConfig(),
      ),
      throwsA(isA<VideoKitException>()),
    );
  });

  test('E2 7: the undo stack holds at most 100 steps', () async {
    expect(EditProjectConfig().undoLimit, 100);
    final (_, p) = await project();
    final clip = p.state.value.timeline.clips.single.clipId;
    for (var i = 0; i < 105; i++) {
      await p.apply(TrimClip(clip, 0, 3000000 - (i + 1) * 1000));
    }
    var undone = 0;
    while (p.state.value.canUndo) {
      await p.undo();
      undone++;
    }
    expect(undone, 100);
  });

  test('createdAt stays, updatedAt follows edits', () async {
    final (kit, p) = await project();
    final before = await json(p);
    await kit.clock.advance(const Duration(seconds: 5));
    final clip = p.state.value.timeline.clips.single.clipId;
    await p.apply(SplitAt(clip, 1000000));
    final after = await json(p);
    expect(after['createdAt'], before['createdAt']);
    expect(
      after['updatedAt']! as int,
      greaterThanOrEqualTo((before['updatedAt']! as int) + 5000),
    );
  });
}
