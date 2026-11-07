import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

/// Runs the shared state-machine vectors (`spec/vectors/state-machine`,
/// 04A §1 rule 4) against the Dart Fake. Vectors win over Fake behaviour.
/// Host for vectors: counts host action calls and answers as configured.
class _VectorHost extends NoopHostCallbacks {
  _VectorHost(this.answer);

  final HostActionStatus answer;
  int calls = 0;

  @override
  Future<HostActionResult> onHostActionRequested(HostActionRequest r) async {
    calls++;
    return HostActionResult(status: answer);
  }
}

void main() {
  final dir = Directory('../../spec/vectors/state-machine');
  if (!dir.existsSync()) {
    test('spec vectors', () {}, skip: 'spec/vectors not present');
    return;
  }
  Map<String, Object?> load(String name) =>
      jsonDecode(File('${dir.path}/$name').readAsStringSync())
          as Map<String, Object?>;

  List<Map<String, Object?>> cases(Map<String, Object?> j) => [
    for (final c in j['cases']! as List<Object?>)
      (c! as Map).cast<String, Object?>(),
  ];

  List<Map<String, Object?>> steps(Map<String, Object?> c) => [
    for (final s in c['steps']! as List<Object?>)
      (s! as Map).cast<String, Object?>(),
  ];

  Map<String, Object?> expectOf(Map<String, Object?> step) =>
      (step['expect']! as Map).cast<String, Object?>();

  Future<T> drive<T>(FakeClock clock, Future<T> f) async {
    var done = false;
    late T v;
    Object? error;
    unawaited(
      f.then(
        (x) {
          v = x;
          done = true;
        },
        onError: (Object e) {
          error = e;
          done = true;
        },
      ),
    );
    for (var i = 0; !done && i < 200; i++) {
      await clock.advance(const Duration(milliseconds: 100));
    }
    expect(done, isTrue, reason: 'step did not complete');
    if (error != null) throw error!;
    return v;
  }

  group('session vectors', () {
    final json = load('session.json');
    test('kind', () => expect(json['kind'], 'session-state-machine'));
    for (final c in cases(json)) {
      test(c['id']! as String, () async {
        final from = c['from']! as String;
        final media = switch (c['media']) {
          'IMAGE_STATIC' => MediaKind.imageStatic,
          'IMAGE_ANIMATED' => MediaKind.imageAnimated,
          _ => MediaKind.video,
        };
        final source = VideoKitMediaSource(
          mediaToken: 'vector-${c['id']}',
          mediaKind: media,
          sourceRef: DemoSourceRef(switch (from) {
            'ERROR_RECOVERABLE' => 'resourceExhausted',
            'ERROR_FATAL' => 'unsupported',
            _ => 'normal',
          }),
        );
        final host = _VectorHost(
          HostActionStatus.fromName(
            c['hostActionAnswer'] as String? ?? 'COMPLETED',
          ),
        );
        final actions = [
          for (final id in (c['hostActions'] as List<Object?>? ?? const []))
            VideoKitHostAction(
              actionId: id! as String,
              labelKey: id as String,
              contentDescriptionKey: id,
              icon: HostIcon.builtIn(id),
              placement: ActionPlacement.primaryBar,
            ),
        ];
        final kit = FakeVideoKit(config: VideoKitConfig(hostCallbacks: host));
        final clock = kit.clock;
        final s = await kit.createSession(const VideoKitSessionConfig());
        // Reach `from`.
        if (from != 'CREATED') {
          final initialLooping = c['initialLooping'] as bool?;
          await drive(
            clock,
            s.bind(
              source,
              hostActions: actions,
              // 04A L3: a saved snapshot carrying the loop setting.
              initialState: initialLooping == null
                  ? null
                  : VideoKitPlaybackState(looping: initialLooping),
            ),
          );
        }
        switch (from) {
          case 'PLAYING':
            await s.execute(const Play());
          case 'PAUSED':
            await s.execute(const Play());
            await s.execute(const Pause());
          case 'ENDED':
            final d = s.state.value.durationUs!;
            await drive(clock, s.execute(SeekTo(d - 200000)));
            await s.execute(const Play());
            await clock.advance(const Duration(seconds: 1));
          case 'RELEASED':
            await drive(clock, s.release());
        }
        expect(s.state.value.phase.wireName, from, reason: 'setup');
        var ended = 0;
        final sub = s.events.listen((e) {
          if (e is PlaybackEnded) ended++;
        });

        for (final step in steps(c)) {
          final cmd = step['command']! as String;
          final Future<VideoKitCommandResult> f = switch (cmd) {
            'PLAY' => s.execute(const Play()),
            'PAUSE' => s.execute(const Pause()),
            'SEEK_TO' => s.execute(SeekTo(step['positionUs']! as int)),
            'SET_SPEED' => s.execute(
              SetSpeed((step['speed']! as num).toDouble()),
            ),
            'SET_VOLUME' => s.execute(
              SetVolume((step['volume']! as num).toDouble()),
            ),
            'SELECT_AUDIO_TRACK' => s.execute(
              SelectAudioTrack(step['trackId'] as String?),
            ),
            'SELECT_SUBTITLE_TRACK' => s.execute(
              SelectSubtitleTrack(step['trackId'] as String?),
            ),
            'SET_VISIBILITY' => s.execute(
              SetVisibility(
                SessionVisibility.fromName(step['visibility'] as String?),
              ),
            ),
            'SET_FULLSCREEN' => s.execute(
              SetFullscreen(step['fullscreen']! as bool),
            ),
            'SET_ACTIVE_AUDIO' => s.execute(
              SetActiveAudio(
                step['active']! as bool,
                step['audioEpoch']! as int,
              ),
            ),
            'HIDE_CONTENT_FOR_LOCK' => s.execute(
              HideContentForLock(step['hidden']! as bool),
            ),
            'BIND' => s.bind(source, hostActions: actions),
            'REQUEST_HOST_ACTION' => s.requestHostAction(
              step['actionId']! as String,
            ),
            // The host reports its pending actions finished (as the Kotlin
            // runner does).
            'HOST_ACTIONS_SETTLED' =>
              s
                  .updateHostActions([
                    for (final a in actions) a.copyWith(pending: false),
                  ])
                  .then((_) => const Executed()),
            'RELEASE' => s.execute(const Release()),
            // 04A L1 looping steps.
            'SET_LOOPING' => s.execute(SetLooping(step['looping']! as bool)),
            'SEEK_NEAR_END' => s.execute(
              SeekTo(s.state.value.durationUs! - 500000),
            ),
            'ADVANCE' =>
              clock
                  .advance(Duration(microseconds: step['us']! as int))
                  .then((_) => const Executed()),
            _ => throw StateError('unknown vector command $cmd'),
          };
          final r = await drive(clock, f);
          final e = expectOf(step);
          final kind = switch (r) {
            Executed() => 'EXECUTED',
            Rejected() => 'REJECTED',
            Superseded() => 'SUPERSEDED',
            Unsupported() => 'UNSUPPORTED',
            SessionReleased() => 'SESSION_RELEASED',
          };
          expect(kind, e['result'], reason: '$cmd → $r');
          if (e['phase'] != null) {
            expect(s.state.value.phase.wireName, e['phase'], reason: cmd);
          }
          if (e['reason'] != null) {
            expect((r as Unsupported).reason.wireName, e['reason']);
          }
          if (e['code'] != null) {
            expect((r as Rejected).error.code.wireName, e['code'], reason: cmd);
          }
          if (e['hostCalls'] != null) {
            await clock.flush();
            expect(host.calls, e['hostCalls'], reason: cmd);
          }
          final st = s.state.value;
          if (e['looping'] != null) {
            expect(st.looping, e['looping'], reason: cmd);
          }
          if (e['atEnd'] != null) {
            expect(st.positionUs == st.durationUs, e['atEnd'], reason: cmd);
          }
          if (e['snapshotLooping'] != null) {
            final snap = await drive(clock, s.captureState());
            expect(snap.looping, e['snapshotLooping'], reason: cmd);
          }
          if (e['playbackEnded'] != null) {
            await clock.flush();
            expect(ended, e['playbackEnded'], reason: cmd);
          }
        }
        await sub.cancel();
        await kit.close();
      });
    }
  });

  group('edit project vectors', () {
    final json = load('edit-project.json');
    test('kind', () => expect(json['kind'], 'edit-state-machine'));
    const video = VideoKitMediaSource(
      mediaToken: 'vector-edit',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('normal'),
    );
    for (final c in cases(json)) {
      test(c['id']! as String, () async {
        final from = c['from']! as String;
        final kit = FakeVideoKit();
        final clock = kit.clock;
        final p = await kit.createEditProject(EditProjectConfig());
        String? sourceId;
        if (from != 'EMPTY') {
          sourceId = (await drive(clock, p.addSource(video))).sourceId;
        }
        if (from == 'READY_WITH_CLIP' || from == 'RELEASED') {
          await p.apply(AddClip(sourceId!, 0, 3000000));
        }
        if (from == 'RELEASED') await drive(clock, p.close());

        String firstClip() {
          final clips = p.state.value.timeline.clips;
          return clips.isEmpty ? 'missing' : clips.first.clipId;
        }

        MaskTrack? firstMask() {
          final m = p.state.value.masks;
          return m.isEmpty ? null : m.first;
        }

        for (final step in steps(c)) {
          final cmd = step['command']! as String;
          int us(String k) => step[k]! as int;
          double d(String k) => (step[k]! as num).toDouble();
          String kind;
          String? rejectedCode;
          if (cmd == 'ADD_SOURCE') {
            try {
              await drive(clock, p.addSource(video));
              kind = 'APPLIED';
            } on VideoKitException catch (x) {
              kind = 'REJECTED';
              rejectedCode = x.error.code.wireName;
            }
          } else if (cmd == 'EXPORT') {
            final r = await drive(
              clock,
              p.export(
                const VideoKitExportRequest(),
                const VideoKitOutputSink(
                  sinkRef: 'demo:vector',
                  capabilities: SinkCapabilities(randomWrite: true),
                ),
              ),
            );
            kind = switch (r) {
              ExportSucceeded() => 'SUCCEEDED',
              ExportFailed() => 'FAILED',
              ExportCancelled() => 'CANCELLED',
            };
            if (r is ExportFailed) rejectedCode = r.error.code.wireName;
          } else if (cmd == 'RESTORE_FUTURE_SNAPSHOT') {
            final snap = await p.snapshot();
            try {
              await kit.restoreEditProject(
                snap.copyWith(schemaVersion: snap.schemaVersion + 1),
                EditProjectConfig(),
              );
              kind = 'APPLIED';
            } on VideoKitException catch (x) {
              kind = 'REJECTED';
              rejectedCode = x.error.code.wireName;
            }
          } else if (cmd == 'DETECT_CANDIDATES') {
            final r = await drive(clock, p.detectCandidates(us('atUs')));
            kind = r.error == null && r.candidates.isNotEmpty
                ? 'APPLIED'
                : 'REJECTED';
            rejectedCode = r.error?.code.wireName;
          } else if (cmd == 'CLOSE') {
            await drive(clock, p.close());
            kind = 'APPLIED';
          } else {
            final mask = firstMask();
            final Future<EditCommandResult> f = switch (cmd) {
              'UNDO' => p.undo(),
              'REDO' => p.redo(),
              'ADD_CLIP' => p.apply(
                AddClip(
                  step['source'] == 'first'
                      ? (sourceId ?? 'missing')
                      : 'unknown',
                  us('inUs'),
                  us('outUs'),
                  index: step['index'] as int?,
                ),
              ),
              'ADD_MASK' => p.apply(
                AddMask(
                  MaskType.fromName(step['type'] as String?),
                  MaskRegion(
                    x: d('x'),
                    y: d('y'),
                    width: d('width'),
                    height: d('height'),
                  ),
                  us('startUs'),
                  us('endUs'),
                ),
              ),
              'SPLIT_FIRST' => p.apply(SplitAt(firstClip(), us('atUs'))),
              'TRIM_FIRST' => p.apply(
                TrimClip(firstClip(), us('inUs'), us('outUs')),
              ),
              'MOVE_FIRST' => p.apply(MoveClip(firstClip(), us('toIndex'))),
              'REMOVE_FIRST' => p.apply(RemoveClip(firstClip())),
              'START_TRACKING_FIRST_MASK' => p.apply(
                StartTracking(
                  mask?.maskId ?? 'missing',
                  mask?.type == MaskType.object
                      ? TrackingKind.object
                      : TrackingKind.face,
                  seedRegion: mask?.keyframes.first.region,
                ),
              ),
              'CANCEL_TRACKING_FIRST_MASK' => p.apply(
                CancelTracking(mask?.maskId ?? 'missing'),
              ),
              'ACCEPT_TRACKING_RANGE_FIRST_MASK' => p.apply(
                AcceptTrackingRange(
                  mask?.maskId ?? 'missing',
                  us('startUs'),
                  us('endUs'),
                ),
              ),
              _ => throw StateError('unknown vector command $cmd'),
            };
            final r = await f;
            if (r is EditRejected) rejectedCode = r.error.code.wireName;
            kind = switch (r) {
              EditApplied() => 'APPLIED',
              EditRejected() => 'REJECTED',
              EditUnsupported() => 'UNSUPPORTED',
              EditProjectReleased() => 'PROJECT_RELEASED',
            };
          }
          final e = expectOf(step);
          expect(kind, e['result'], reason: cmd);
          if (e['phase'] != null) {
            expect(p.state.value.phase.wireName, e['phase'], reason: cmd);
          }
          if (e['code'] != null) {
            expect(rejectedCode, e['code'], reason: cmd);
          }
        }
        await kit.close();
      });
    }
  });
}
