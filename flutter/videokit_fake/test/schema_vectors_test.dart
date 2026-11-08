// M4-A2 (04A E2): the Dart codec against the single source of the edit
// project snapshot, spec/schema/edit-project.v1.json (Coder B, M4-B1):
// * spec/vectors/timeline/schema-migration.json (R1-R6, M0);
// * W1 conformance: written snapshots carry every schema property (null
//   where nullable) and nothing else, with the schema's types and enums.
import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

Map<String, Object?> _load(String path) =>
    jsonDecode(File(path).readAsStringSync()) as Map<String, Object?>;

/// Accepted ranges of [m] as `{startUs, endUs}` (04A E4: on the mask).
List<Map<String, Object?>> _accepted(MaskTrack m) => [
  for (final r in m.acceptedRanges) {'startUs': r.startUs, 'endUs': r.endUs},
];

void main() {
  const schemaPath = '../../spec/schema/edit-project.v1.json';
  const vectorsPath = '../../spec/vectors/timeline/schema-migration.json';
  if (!File(schemaPath).existsSync() || !File(vectorsPath).existsSync()) {
    test('schema vectors', () {}, skip: 'spec/schema not present');
    return;
  }
  final schema = _load(schemaPath);

  group('schema-migration vectors', () {
    final json = _load(vectorsPath);
    test('kind', () => expect(json['kind'], 'timeline-schema-migration'));
    for (final raw in json['cases']! as List<Object?>) {
      final c = (raw! as Map).cast<String, Object?>();
      test(c['id']! as String, () async {
        final e = (c['expect']! as Map).cast<String, Object?>();
        final text = c['json'] as String? ?? jsonEncode(c['payload']);
        final kit = FakeVideoKit();
        addTearDown(kit.close);
        VideoKitEditProject? p;
        String? code;
        try {
          p = await kit.restoreEditProject(
            SerializedEditProject(
              schemaVersion: c['envelopeVersion']! as int,
              json: text,
            ),
            EditProjectConfig(),
          );
        } on VideoKitException catch (x) {
          code = x.error.code.wireName;
        }
        if (e['result'] == 'REJECTED') {
          expect(p, isNull, reason: 'restored');
          expect(code, e['code']);
          return;
        }
        expect(code, isNull, reason: 'rejected with $code');
        final st = p!.state.value;
        final written =
            jsonDecode((await p.snapshot()).json) as Map<String, Object?>;
        if (e.containsKey('projectId')) {
          expect(p.projectId, e['projectId']);
        }
        for (final k in ['revision', 'createdAt', 'updatedAt']) {
          if (e.containsKey(k)) expect(written[k], e[k], reason: k);
        }
        if (e.containsKey('exportPresetId')) {
          expect(written['exportPresetId'], e['exportPresetId']);
        }
        if (e['sources'] case final List<Object?> sources) {
          expect(st.timeline.sources, hasLength(sources.length));
          for (final (i, x) in sources.indexed) {
            final want = (x! as Map).cast<String, Object?>();
            final s = st.timeline.sources[i];
            final got = <String, Object?>{
              'sourceId': s.sourceId,
              'mediaToken': s.mediaToken,
              'rotation': s.probe?.rotationDeg ?? 0,
              'fps': s.probe?.fps,
              'videoCodec': s.probe?.videoCodec,
            };
            for (final k in want.keys) {
              expect(got[k], want[k], reason: 'source $i $k');
            }
          }
        }
        if (e['clips'] case final List<Object?> clips) {
          expect([
            for (final c in st.timeline.clips)
              {'clipId': c.clipId, 'inUs': c.inUs, 'outUs': c.outUs},
          ], clips);
        }
        if (e['masks'] case final List<Object?> masks) {
          expect(st.masks, hasLength(masks.length));
          for (final (i, x) in masks.indexed) {
            final want = (x! as Map).cast<String, Object?>();
            final m = st.masks[i];
            final got = <String, Object?>{
              'maskId': m.maskId,
              'style': m.style.wireName,
              'strength': m.strength,
              'enabled': m.enabled,
              'rangeUs': {'startUs': m.startUs, 'endUs': m.endUs},
              'keyframes': [for (final k in m.keyframes) k.atUs],
              'keyframeStates': [
                for (final k in m.keyframes) k.state?.wireName,
              ],
              'acceptedRanges': _accepted(m),
            };
            for (final k in want.keys) {
              expect(got[k], want[k], reason: 'mask $i $k');
            }
          }
        }
        if (e['tracking'] case final List<Object?> runs) {
          expect(st.tracking, hasLength(runs.length));
          for (final x in runs) {
            final want = (x! as Map).cast<String, Object?>();
            final r = st.tracking[want['maskId']]!;
            expect(r.status.wireName, want['status'], reason: 'status');
            if (want.containsKey('qualities')) {
              expect([
                for (final s in r.coverage.segments) s.state.wireName,
              ], want['qualities']);
            }
          }
        }
        // Written again and read back: unchanged.
        final again = await FakeVideoKit().restoreEditProject(
          await p.snapshot(),
          EditProjectConfig(),
        );
        final st2 = again.state.value;
        expect(st2.timeline, st.timeline);
        expect(st2.masks, st.masks);
        expect(st2.revision, st.revision);
        expect(
          {
            for (final e in st2.tracking.entries)
              e.key: (e.value.status, e.value.coverage),
          },
          {
            for (final e in st.tracking.entries)
              e.key: (e.value.status, e.value.coverage),
          },
        );
      });
    }
  });

  group('W1 conformance', () {
    test('schema version is 1.0', () {
      expect(schema['x-version'], {'major': 1, 'minor': 0});
      expect(SerializedEditProject.currentSchemaVersion, 1);
      expect(FakeEditProjectCodec.currentSchemaMinor, 0);
    });

    Future<VideoKitEditProject> rich() async {
      final kit = FakeVideoKit();
      final p =
          await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
      final add = p.addSource(
        const VideoKitMediaSource(
          mediaToken: 'w1',
          mediaKind: MediaKind.video,
          displayName: 'w1.mp4',
          sourceRef: DemoSourceRef('normal'),
        ),
      );
      await kit.clock.advance(const Duration(milliseconds: 300));
      final src = await add;
      await p.apply(AddClip(src.sourceId, 0, 3000000));
      final mask = (await p.apply(
        const AddMask(
          MaskType.face,
          MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2),
          0,
          2000000,
        ),
      ) as EditApplied).createdId!;
      await p.apply(AcceptTrackingRange(mask, 0, 2000000));
      final done = p.export(
        const VideoKitExportRequest(presetId: ExportPresets.p1080),
        const VideoKitOutputSink(sinkRef: 'demo:w1'),
      );
      VideoKitExportResult? r;
      unawaited(done.then((x) => r = x));
      for (var i = 0; i < 200 && r == null; i++) {
        await kit.clock.advance(const Duration(milliseconds: 250));
      }
      return p;
    }

    test('a rich project conforms', () async {
      final p = await rich();
      final j = jsonDecode((await p.snapshot()).json);
      final errors = _SchemaCheck(schema).check(j);
      expect(errors, isEmpty);
      // The rich project exercises masks, keyframes, tracking, preset.
      expect(((j as Map)['masks']! as List), isNotEmpty);
      expect((j['tracking']! as List), isNotEmpty);
      expect(j['exportPresetId'], ExportPresets.p1080);
    });

    test('an empty project conforms', () async {
      final kit = FakeVideoKit();
      final p = await kit.createEditProject(EditProjectConfig());
      final j = jsonDecode((await p.snapshot()).json);
      expect(_SchemaCheck(schema).check(j), isEmpty);
    });

    test('the checker itself rejects extra and missing properties', () {
      final check = _SchemaCheck(schema);
      expect(
        check.check({'schemaVersion': 1, 'projectId': 'p', 'extra': true}),
        isNotEmpty,
      );
      expect(check.check({'schemaVersion': 'x', 'projectId': 'p'}), isNotEmpty);
    });
  });
}

/// A small checker for the JSON Schema subset used by
/// edit-project.v1.json: type, const, enum, required, properties, items,
/// oneOf, $ref. W1 adds: an object with `properties` must carry exactly
/// those properties (every one written, nothing else).
final class _SchemaCheck {
  _SchemaCheck(this.root);

  final Map<String, Object?> root;

  List<String> check(Object? value) {
    final errors = <String>[];
    _check(root, value, r'$', errors);
    return errors;
  }

  Map<String, Object?> _resolve(Map<String, Object?> s) {
    final ref = s[r'$ref'] as String?;
    if (ref == null) return s;
    final name = ref.split('/').last;
    final defs = (root[r'$defs']! as Map).cast<String, Object?>();
    return _resolve((defs[name]! as Map).cast<String, Object?>());
  }

  bool _isType(String t, Object? v) => switch (t) {
    'null' => v == null,
    'integer' => v is int,
    'number' => v is num,
    'string' => v is String,
    'boolean' => v is bool,
    'array' => v is List,
    'object' => v is Map,
    _ => false,
  };

  void _check(
    Map<String, Object?> schemaIn,
    Object? v,
    String at,
    List<String> errors,
  ) {
    final s = _resolve(schemaIn);
    if (s['oneOf'] case final List<Object?> options) {
      final matches = options.where((o) {
        final e = <String>[];
        _check((o! as Map).cast<String, Object?>(), v, at, e);
        return e.isEmpty;
      }).length;
      if (matches != 1) errors.add('$at: oneOf matched $matches');
      return;
    }
    final type = s['type'];
    if (type != null) {
      final types = type is List ? type.cast<String>() : [type as String];
      if (!types.any((t) => _isType(t, v))) {
        errors.add('$at: type $types');
        return;
      }
    }
    if (s.containsKey('const') && s['const'] != v) {
      errors.add('$at: const ${s['const']}');
    }
    if (s['enum'] case final List<Object?> values) {
      if (!values.contains(v)) errors.add('$at: enum');
    }
    if (v is Map && s['properties'] is Map) {
      final props = (s['properties']! as Map).cast<String, Object?>();
      final keys = v.keys.cast<String>().toSet();
      for (final k in keys.difference(props.keys.toSet())) {
        errors.add('$at.$k: not in schema (W1)');
      }
      for (final k in props.keys.toSet().difference(keys)) {
        errors.add('$at.$k: not written (W1)');
      }
      for (final k in keys.intersection(props.keys.toSet())) {
        _check(
          (props[k]! as Map).cast<String, Object?>(),
          v[k],
          '$at.$k',
          errors,
        );
      }
    }
    final required = s['required'];
    if (v is Map && required is List) {
      for (final k in required) {
        if (!v.containsKey(k)) errors.add('$at.$k: required');
      }
    }
    if (v is List && s['items'] is Map) {
      final items = (s['items']! as Map).cast<String, Object?>();
      for (final (i, x) in v.indexed) {
        _check(items, x, '$at[$i]', errors);
      }
    }
  }
}
