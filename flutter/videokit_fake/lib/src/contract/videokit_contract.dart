import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// Advances time for [kit] by [duration]. Fakes move their clock; real
/// implementations simply wait.
typedef ContractElapse = Future<void> Function(VideoKit kit, Duration duration);

Future<void> _realElapse(VideoKit kit, Duration d) => Future<void>.delayed(d);

/// Media/sink fixtures used by the suite. Defaults use `demo:` refs that
/// both the Dart Fake and the Kotlin Fake understand.
final class ContractFixtures {
  /// Creates fixtures.
  const ContractFixtures({
    this.video = const VideoKitMediaSource(
      mediaToken: 'contract-video-1',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('normal'),
    ),
    this.video2 = const VideoKitMediaSource(
      mediaToken: 'contract-video-2',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('normal'),
    ),
    this.image = const VideoKitMediaSource(
      mediaToken: 'contract-image-1',
      mediaKind: MediaKind.imageStatic,
      sourceRef: DemoSourceRef('normal'),
    ),
    this.unsupported = const VideoKitMediaSource(
      mediaToken: 'contract-unsupported-1',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('unsupported'),
    ),
    this.sink = const VideoKitOutputSink(
      sinkRef: 'demo:contract-sink',
      capabilities: SinkCapabilities(randomWrite: true, fileDescriptor: true),
    ),
  });

  /// A playable video.
  final VideoKitMediaSource video;

  /// Another playable video.
  final VideoKitMediaSource video2;

  /// A static image.
  final VideoKitMediaSource image;

  /// A video whose bind fails with `UNSUPPORTED_*`; null skips that case.
  final VideoKitMediaSource? unsupported;

  /// A capable output sink.
  final VideoKitOutputSink sink;
}

/// Host callbacks with switchable failure modes for the suite.
class ContractHostCallbacks extends NoopHostCallbacks {
  /// Every callback throws.
  bool throwAll = false;

  /// `onHostActionRequested` waits for [releaseHostAction].
  bool holdHostAction = false;

  /// Host action requests seen.
  final List<HostActionRequest> hostActionRequests = [];

  /// Controls visibility notifications seen.
  final List<bool> controlsVisibility = [];

  Completer<HostActionResult>? _held;

  /// Completes a held host action with [result].
  void releaseHostAction(HostActionResult result) {
    final held = _held;
    _held = null;
    if (held != null && !held.isCompleted) held.complete(result);
  }

  @override
  Future<HostActionResult> onHostActionRequested(
    HostActionRequest request,
  ) async {
    hostActionRequests.add(request);
    if (throwAll) throw StateError('host failure');
    if (holdHostAction) return (_held = Completer<HostActionResult>()).future;
    return const HostActionResult.completed();
  }

  @override
  Future<void> onControlsVisibilityChanged(
    String sessionId,
    bool visible,
  ) async {
    controlsVisibility.add(visible);
    if (throwAll) throw StateError('host failure');
  }

  @override
  Future<void> onPlaybackEvent(VideoKitPlaybackEvent event) async {
    if (throwAll) throw StateError('host failure');
  }

  @override
  Future<void> onPlaybackSnapshot(
    String sessionId,
    VideoKitPlaybackState snapshot,
  ) async {
    if (throwAll) throw StateError('host failure');
  }

  @override
  Future<void> onSourceReleased(String sessionId, String mediaToken) async {
    if (throwAll) throw StateError('host failure');
  }
}

/// Runs the Dart VideoKit contract suite (04 §11, 14 §11.1) against
/// implementations produced by [create].
///
/// [create] receives the config (with [ContractHostCallbacks]) so the suite
/// can inject host failures. [elapse] drives time (Fakes pass their clock).
void runVideoKitContractTests(
  VideoKit Function(VideoKitConfig config) create, {
  ContractFixtures fixtures = const ContractFixtures(),
  ContractElapse elapse = _realElapse,
  String description = 'VideoKit contract',
}) {
  group(description, () {
    late ContractHostCallbacks host;
    late VideoKit kit;

    setUp(() {
      host = ContractHostCallbacks();
      kit = create(
        VideoKitConfig(
          hostCallbacks: host,
          callbackTimeouts: const HostCallbackTimeouts(
            hostAction: Duration(seconds: 1),
            navigation: Duration(milliseconds: 500),
            notification: Duration(milliseconds: 500),
          ),
        ),
      );
    });

    tearDown(() async {
      host.releaseHostAction(const HostActionResult.completed());
      await kit.close();
    });

    /// Elapses time until [future] completes.
    Future<T> drive<T>(Future<T> future, {int maxSteps = 600}) async {
      var done = false;
      late T value;
      Object? error;
      StackTrace? stack;
      unawaited(
        future.then(
          (v) {
            value = v;
            done = true;
          },
          onError: (Object e, StackTrace s) {
            error = e;
            stack = s;
            done = true;
          },
        ),
      );
      await Future<void>.delayed(Duration.zero);
      for (var i = 0; !done && i < maxSteps; i++) {
        await elapse(kit, const Duration(milliseconds: 100));
      }
      if (!done) fail('operation did not complete');
      if (error != null) Error.throwWithStackTrace(error!, stack!);
      return value;
    }

    Future<VideoKitSession> boundVideo([VideoKitPlaybackState? initial]) async {
      final s = await kit.createSession(const VideoKitSessionConfig());
      final r = await drive(s.bind(fixtures.video, initialState: initial));
      expect(r, const Executed());
      return s;
    }

    group('version and capabilities', () {
      test('API major version is 1', () {
        expect(kit.apiVersion.major, 1);
        expect(
          kit.apiVersion.isCompatibleWith(const VideoKitApiVersion(1, 0, 0)),
          isTrue,
        );
      });

      test(
        'capability report has a schema version and per-media probe',
        () async {
          final c = await kit.capabilities(CapabilityRequest.device);
          expect(c.schemaVersion, greaterThanOrEqualTo(1));
          expect(c.isDemo, kit.isDemo);
          final probe = await kit.capabilities(
            CapabilityRequest(source: fixtures.video),
          );
          expect(probe.mediaProbe, isNotNull);
          expect(probe.mediaProbe!.playable, isTrue);
        },
      );
    });

    group('session state machine', () {
      test('new session is CREATED and rejects playback commands', () async {
        final s = await kit.createSession(const VideoKitSessionConfig());
        expect(s.state.value.phase, SessionPhase.created);
        expect(s.state.value.resourcesHeld, isFalse);
        expect(s.isDemo, kit.isDemo);
        expect(await s.execute(const Play()), isA<Rejected>());
        expect(await s.execute(const SeekTo(0)), isA<Rejected>());
        expect(await s.execute(const SetSpeed(1.5)), isA<Rejected>());
      });

      test('bind goes CREATED → BINDING → READY', () async {
        final s = await kit.createSession(const VideoKitSessionConfig());
        final phases = <SessionPhase>[];
        void listener() => phases.add(s.state.value.phase);
        s.state.addListener(listener);
        final r = await drive(s.bind(fixtures.video));
        s.state.removeListener(listener);
        expect(r, const Executed());
        expect(phases.first, SessionPhase.binding);
        expect(s.state.value.phase, SessionPhase.ready);
        expect(s.state.value.mediaKind, MediaKind.video);
        expect(s.state.value.durationUs, greaterThan(0));
        expect(s.state.value.resourcesHeld, isTrue);
        expect(s.videoSize.value, isNotNull);
      });

      test('play / pause transitions and position advances', () async {
        final s = await boundVideo();
        expect(await s.execute(const Play()), const Executed());
        expect(s.state.value.phase, SessionPhase.playing);
        final p0 = s.state.value.positionUs;
        await elapse(kit, const Duration(seconds: 1));
        expect(s.state.value.positionUs, greaterThan(p0));
        expect(await s.execute(const Pause()), const Executed());
        expect(s.state.value.phase, SessionPhase.paused);
        final p1 = s.state.value.positionUs;
        await elapse(kit, const Duration(seconds: 1));
        expect(s.state.value.positionUs, p1);
      });

      test(
        'rapid seeks: only the latest executes, earlier are Superseded',
        () async {
          final s = await boundVideo();
          final first = s.execute(
            const SeekTo(2000000, mode: SeekMode.preview),
          );
          final second = s.execute(
            const SeekTo(4000000, mode: SeekMode.preview),
          );
          final last = s.execute(const SeekTo(6000000));
          expect(await drive(first), const Superseded());
          expect(await drive(second), const Superseded());
          expect(await drive(last), const Executed());
          expect(s.state.value.positionUs, 6000000);
          expect(s.state.value.seekingToUs, isNull);
        },
      );

      test('seek beyond the end is clamped', () async {
        final s = await boundVideo();
        final d = s.state.value.durationUs!;
        expect(
          await drive(s.execute(SeekTo(d + 1000000000))),
          const Executed(),
        );
        expect(s.state.value.positionUs, d);
      });

      test('out-of-range values and unknown tracks are Unsupported', () async {
        final s = await boundVideo();
        expect(
          await s.execute(const SetSpeed(100)),
          const Unsupported(UnsupportedReason.valueOutOfRange),
        );
        expect(
          await s.execute(const SetVolume(-1)),
          const Unsupported(UnsupportedReason.valueOutOfRange),
        );
        expect(
          await s.execute(const SelectAudioTrack('no-such-track')),
          const Unsupported(UnsupportedReason.trackNotFound),
        );
        expect(
          await s.execute(const SelectSubtitleTrack(null)),
          const Executed(),
        );
        expect(s.state.value.selectedSubtitleTrackId, isNull);
        expect(await s.execute(const SetSpeed(1.5)), const Executed());
        expect(s.state.value.speed, 1.5);
      });

      test('image sessions refuse video-only commands', () async {
        final s = await kit.createSession(const VideoKitSessionConfig());
        expect(await drive(s.bind(fixtures.image)), const Executed());
        expect(s.state.value.phase, SessionPhase.ready);
        expect(s.state.value.mediaKind!.isImage, isTrue);
        expect(s.state.value.audioTracks, isEmpty);
        expect(
          await s.execute(const Play()),
          const Unsupported(UnsupportedReason.notApplicableToMediaKind),
        );
        expect(
          await s.execute(const SeekTo(0)),
          const Unsupported(UnsupportedReason.notApplicableToMediaKind),
        );
        expect(
          await s.execute(const SetTransform(MediaTransform(scale: 2))),
          const Executed(),
        );
      });

      test('stale audio epoch is Superseded', () async {
        final s = await boundVideo();
        expect(
          await s.execute(const SetActiveAudio(true, 5)),
          const Executed(),
        );
        expect(s.state.value.activeAudio, isTrue);
        expect(
          await s.execute(const SetActiveAudio(false, 4)),
          const Superseded(),
        );
        expect(s.state.value.activeAudio, isTrue);
      });

      test('content lock pauses and refuses play', () async {
        final s = await boundVideo();
        await s.execute(const Play());
        expect(
          await s.execute(const HideContentForLock(true)),
          const Executed(),
        );
        expect(s.state.value.contentHiddenForLock, isTrue);
        expect(s.state.value.phase, SessionPhase.paused);
        expect(
          await s.execute(const Play()),
          const Unsupported(UnsupportedReason.contentLocked),
        );
      });

      if (fixtures.unsupported != null) {
        test(
          'unsupported media maps to a stable UNSUPPORTED_* error',
          () async {
            final s = await kit.createSession(const VideoKitSessionConfig());
            final r = await drive(s.bind(fixtures.unsupported!));
            expect(r, isA<Rejected>());
            final code = (r as Rejected).error.code;
            expect(
              code,
              anyOf(
                ErrorCode.unsupportedContainer,
                ErrorCode.unsupportedVideoCodec,
                ErrorCode.unsupportedAudioCodec,
              ),
            );
            expect(s.state.value.phase, SessionPhase.errorFatal);
            expect(s.state.value.error?.code, code);
          },
        );
      }
    });

    group('snapshot and release', () {
      test('initial state is applied and captured back', () async {
        final s = await boundVideo(
          const VideoKitPlaybackState(
            positionUs: 5000000,
            speed: 1.5,
            zoom: 2,
            fitMode: FitMode.fill,
            muted: true,
          ),
        );
        final snap = await s.captureState();
        expect(snap.mediaToken, fixtures.video.mediaToken);
        expect(snap.positionUs, 5000000);
        expect(snap.speed, 1.5);
        expect(snap.zoom, 2);
        expect(snap.fitMode, FitMode.fill);
        expect(snap.muted, isTrue);
        expect(VideoKitPlaybackState.fromJson(snap.toJson()), snap);
      });

      test('release is idempotent and terminal', () async {
        final s = await boundVideo();
        final events = <VideoKitEvent>[];
        final sub = s.events.listen(events.add);
        final a = await drive(s.release());
        final b = await drive(s.release());
        expect(a, b);
        expect(s.state.value.phase, SessionPhase.released);
        expect(s.state.value.resourcesHeld, isFalse);
        expect(await s.execute(const Play()), const SessionReleased());
        expect(await s.bind(fixtures.video), const SessionReleased());
        await s.close();
        await sub.cancel();
        expect(events, contains(SourceReleased(fixtures.video.mediaToken)));
      });

      test('re-bind releases the previous source first', () async {
        final s = await boundVideo();
        final events = <VideoKitEvent>[];
        final sub = s.events.listen(events.add);
        expect(await drive(s.bind(fixtures.video2)), const Executed());
        await sub.cancel();
        expect(events.first, SourceReleased(fixtures.video.mediaToken));
        expect((await s.captureState()).mediaToken, fixtures.video2.mediaToken);
      });

      test(
        'closing VideoKit releases its sessions; close is idempotent',
        () async {
          final s = await boundVideo();
          await drive(kit.close());
          await drive(kit.close());
          expect(s.state.value.phase, SessionPhase.released);
        },
      );
    });

    group('host callbacks', () {
      const fav = VideoKitHostAction(
        actionId: 'fav',
        labelKey: 'favorite',
        contentDescriptionKey: 'favorite',
        icon: HostIcon.builtin('favorite'),
        placement: ActionPlacement.primaryBar,
      );

      test('duplicate clicks while pending are merged', () async {
        host.holdHostAction = true;
        final s = await kit.createSession(const VideoKitSessionConfig());
        await drive(s.bind(fixtures.video, hostActions: const [fav]));
        expect(
          await s.execute(const InvokeHostAction('fav')),
          const Executed(),
        );
        expect(
          await s.execute(const InvokeHostAction('fav')),
          const Executed(),
        );
        await elapse(kit, const Duration(milliseconds: 100));
        expect(host.hostActionRequests, hasLength(1));
        expect(s.state.value.hostActions.single.isPending, isTrue);
        host.releaseHostAction(
          HostActionResult.completed(fav.copyWith(selected: true)),
        );
        await elapse(kit, const Duration(milliseconds: 100));
        final st = s.state.value.hostActions.single;
        expect(st.inFlight, isFalse);
        expect(st.action.selected, isTrue);
        expect(
          await s.execute(const InvokeHostAction('nope')),
          const Unsupported(UnsupportedReason.hostActionUnavailable),
        );
      });

      test(
        'host action timeout → HOST_CALLBACK_FAILED, session unaffected',
        () async {
          host.holdHostAction = true;
          final s = await kit.createSession(const VideoKitSessionConfig());
          await drive(s.bind(fixtures.video, hostActions: const [fav]));
          final failed = s.events.firstWhere((e) => e is HostActionFailed);
          await s.execute(const InvokeHostAction('fav'));
          final e = await drive(failed) as HostActionFailed;
          expect(e.error.code, ErrorCode.hostCallbackFailed);
          expect(s.state.value.hostActions.single.inFlight, isFalse);
          expect(
            s.state.value.hostActions.single.lastError?.code,
            ErrorCode.hostCallbackFailed,
          );
          expect(await s.execute(const Play()), const Executed());
        },
      );

      test('throwing host callbacks never break the session', () async {
        host.throwAll = true;
        final s = await kit.createSession(const VideoKitSessionConfig());
        await drive(s.bind(fixtures.video, hostActions: const [fav]));
        expect(await s.execute(const Play()), const Executed());
        await s.execute(const InvokeHostAction('fav'));
        await s.reportControlsVisible(false);
        await elapse(kit, const Duration(seconds: 2));
        expect(s.state.value.phase, SessionPhase.playing);
        expect(s.state.value.controlsVisible, isFalse);
        expect(
          s.state.value.hostActions.single.lastError?.code,
          ErrorCode.hostCallbackFailed,
        );
        await drive(s.release());
        expect(s.state.value.phase, SessionPhase.released);
      });

      test('controls visibility is written to state and forwarded', () async {
        final s = await boundVideo();
        await s.reportControlsVisible(false);
        await elapse(kit, const Duration(milliseconds: 100));
        expect(s.state.value.controlsVisible, isFalse);
        expect(host.controlsVisibility, [false]);
      });
    });

    group('edit project', () {
      Future<(VideoKitEditProject, SourceToken)> readyProject() async {
        final p = await kit.createEditProject(EditProjectConfig());
        expect(p.state.value.phase, EditPhase.created);
        final token = await drive(p.addSource(fixtures.video));
        expect(p.state.value.phase, EditPhase.ready);
        return (p, token);
      }

      test('commands bump revision; invalid commands are Rejected', () async {
        final (p, src) = await readyProject();
        final r = await p.apply(AddClip(src.sourceId, 0, 4000000));
        expect(r, isA<EditApplied>());
        expect((r as EditApplied).revision, 1);
        expect(p.state.value.timeline.clips, hasLength(1));
        expect(p.state.value.estimate.durationUs, 4000000);
        final bad = await p.apply(TrimClip(r.createdId!, 5, 1));
        expect(bad, isA<EditRejected>());
        expect(p.state.value.revision, 1);
        expect(await p.apply(const RemoveClip('missing')), isA<EditRejected>());
      });

      test('undo / redo', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 4000000));
        final split = await p.apply(
          SplitAt(p.state.value.timeline.clips.single.clipId, 1000000),
        );
        expect(split, isA<EditApplied>());
        expect(p.state.value.timeline.clips, hasLength(2));
        expect(p.state.value.canUndo, isTrue);
        expect(await p.undo(), isA<EditApplied>());
        expect(p.state.value.timeline.clips, hasLength(1));
        expect(p.state.value.canRedo, isTrue);
        expect(await p.redo(), isA<EditApplied>());
        expect(p.state.value.timeline.clips, hasLength(2));
        expect(p.state.value.timeline.durationUs, 4000000);
      });

      test('snapshot round trip and future schema rejection', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 3000000));
        await p.apply(
          const AddMask(
            MaskType.manual,
            NormalizedRect(left: 0.1, top: 0.1, width: 0.2, height: 0.2),
            0,
            2000000,
          ),
        );
        final snap = await p.snapshot();
        expect(snap.schemaVersion, SerializedEditProject.currentSchemaVersion);
        final restored = await kit.restoreEditProject(
          snap,
          EditProjectConfig(),
        );
        expect(restored.state.value.timeline, p.state.value.timeline);
        expect(restored.state.value.masks, p.state.value.masks);
        await expectLater(
          kit.restoreEditProject(
            SerializedEditProject(schemaVersion: 99, json: snap.json),
            EditProjectConfig(),
          ),
          throwsA(isA<VideoKitException>()),
        );
      });

      test('precheck blocks empty timeline and incapable sink', () async {
        final (p, _) = await readyProject();
        final empty = await p.checkExport(
          const VideoKitExportRequest(),
          fixtures.sink,
        );
        expect(empty.canExport, isFalse);
        expect(
          empty.issues.map((i) => i.kind),
          contains(PrecheckIssueKind.emptyTimeline),
        );
        final noSink = await p.checkExport(
          const VideoKitExportRequest(),
          const VideoKitOutputSink(
            sinkRef: 'demo:none',
            capabilities: SinkCapabilities(sequentialWrite: false),
          ),
        );
        final issue = noSink.issues.firstWhere(
          (i) => i.kind == PrecheckIssueKind.sinkCapabilityUnsupported,
        );
        expect(issue.error?.code, ErrorCode.outputCapabilityUnsupported);
      });

      test('export succeeds through stages', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 2000000));
        final stages = <ExportStage>{};
        void listener() {
          final e = p.state.value.export;
          if (e != null) stages.add(e.stage);
        }

        p.state.addListener(listener);
        final result = await drive(
          p.export(const VideoKitExportRequest(), fixtures.sink),
        );
        p.state.removeListener(listener);
        expect(result, isA<ExportSucceeded>());
        final media = (result as ExportSucceeded).media;
        expect(media.editProjectId, p.projectId);
        expect(media.sourceTokens, [fixtures.video.mediaToken]);
        expect(media.isDemo, kit.isDemo);
        if (kit.isDemo) {
          expect(media.warnings, contains(ExportWarnings.demoNoRealFile));
        }
        expect(p.state.value.phase, EditPhase.completed);
        expect(
          stages,
          containsAll([ExportStage.preparing, ExportStage.encoding]),
        );
      });

      test('export cancel → CANCELLING → CANCELLED', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 8000000));
        final future = p.export(
          const VideoKitExportRequest(exportId: 'exp-1'),
          fixtures.sink,
        );
        await elapse(kit, const Duration(milliseconds: 600));
        expect(p.state.value.phase, EditPhase.exporting);
        await p.cancelExport('exp-1');
        expect(
          p.state.value.phase,
          anyOf(EditPhase.cancelling, EditPhase.cancelled),
        );
        final result = await drive(future);
        expect(result, isA<ExportCancelled>());
        expect(p.state.value.phase, EditPhase.cancelled);
        await p.cancelExport('unknown');
      });

      test('edits are rejected while exporting; close is idempotent', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 8000000));
        final future = p.export(
          const VideoKitExportRequest(exportId: 'exp-2'),
          fixtures.sink,
        );
        await elapse(kit, const Duration(milliseconds: 300));
        expect(await p.apply(const RemoveClip('x')), isA<EditRejected>());
        await p.cancelExport('exp-2');
        await drive(future);
        await drive(p.close());
        await drive(p.close());
        expect(p.state.value.phase, EditPhase.released);
        expect(
          await p.apply(const RemoveClip('x')),
          const EditProjectReleased(),
        );
      });

      test('preview session is shared and released with the project', () async {
        final (p, src) = await readyProject();
        await p.apply(AddClip(src.sourceId, 0, 3000000));
        final a = await drive(p.previewSession());
        final b = await drive(p.previewSession());
        expect(identical(a, b), isTrue);
        expect(a.state.value.durationUs, 3000000);
        await drive(p.close());
        expect(a.state.value.phase, SessionPhase.released);
      });
    });
  });
}
