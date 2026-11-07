import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

const _video = VideoKitMediaSource(
  mediaToken: 'scenario-video',
  mediaKind: MediaKind.video,
  sourceRef: DemoSourceRef('normal'),
);

class _RetryHost extends NoopHostCallbacks {
  @override
  Future<RecoveryDecision> onRecoverableError(
    String sessionId,
    VideoKitStableError error,
  ) async => RecoveryDecision.retry;
}

Future<(FakeVideoKit, FakeSession)> _bound(
  Scenario scenario, {
  VideoKitConfig config = const VideoKitConfig(),
  VideoKitMediaSource source = _video,
  bool expectOk = true,
}) async {
  final kit = FakeVideoKit(config: config, defaultScenario: scenario);
  final s =
      await kit.createSession(const VideoKitSessionConfig()) as FakeSession;
  final f = s.bind(source);
  await kit.clock.advance(scenario.loadDelay + const Duration(milliseconds: 1));
  final r = await f;
  if (expectOk) expect(r, const Executed());
  return (kit, s);
}

Future<void> _playTo(FakeVideoKit kit, FakeSession s, Duration at) async {
  await s.execute(const Play());
  await kit.clock.advance(at);
}

void main() {
  test('04A B1: openBuffering — bind succeeds with the tracks, then the '
      'session buffers before the first frame', () async {
    const scenario = Scenario.openBuffering(Duration(seconds: 3));
    final (kit, s) = await _bound(scenario);
    expect(s.state.value.phase, SessionPhase.buffering);
    expect(s.state.value.durationUs, isNotNull, reason: 'tracks known');
    expect(s.state.value.audioTracks, isNotEmpty);
    await kit.clock.advance(const Duration(seconds: 2));
    expect(s.state.value.phase, SessionPhase.buffering);
    await kit.clock.advance(const Duration(seconds: 2));
    expect(s.state.value.phase, SessionPhase.ready);
    expect(Scenarios.catalog['openBuffering'], isNotNull);
    await s.close();
    await kit.close();
  });

  test('TEST-R3 R3-01 (04A A1): a bound session has no audio until the '
      'host grants it', () async {
    final (kit, s) = await _bound(const Scenario.normal());
    expect(s.state.value.activeAudio, isFalse);
    expect(await s.execute(const SetActiveAudio(true, 1)), const Executed());
    expect(s.state.value.activeAudio, isTrue);
    expect(await s.execute(const SetActiveAudio(false, 2)), const Executed());
    expect(s.state.value.activeAudio, isFalse);
    await s.close();
    await kit.close();
  });

  test('catalog covers every 14 §11.1 scenario and combines', () {
    expect(
      Scenarios.catalog.keys,
      containsAll([
        'normal',
        'slowLoad',
        'buffering',
        'unsupported',
        'corrupt',
        'disconnect',
        'resourceExhausted',
        'hostActionTimeout',
        'trackingLost',
        'exportFails',
        'exportCancelSlow',
      ]),
    );
    final combo =
        const Scenario.slowLoad(Duration(seconds: 3)) +
        Scenario.buffering() +
        Scenario.hostActionTimeout('delete');
    expect(combo.loadDelay, const Duration(seconds: 3));
    expect(combo.bufferingWindows, hasLength(1));
    expect(combo.hostActionTimeouts, {'delete'});
    expect(combo.name, 'slowLoad+buffering+hostActionTimeout');
    expect(Scenarios.byId('nope'), const Scenario.normal());
    expect(
      combo,
      combo.and(const Scenario.normal()).and(const Scenario.normal()),
    );
  });

  test('slowLoad keeps BINDING for the delay', () async {
    final kit = FakeVideoKit(defaultScenario: const Scenario.slowLoad());
    final s = await kit.createSession(const VideoKitSessionConfig());
    final f = s.bind(_video);
    await kit.clock.advance(const Duration(milliseconds: 2900));
    expect(s.state.value.phase, SessionPhase.binding);
    await kit.clock.advance(const Duration(milliseconds: 200));
    expect(await f, const Executed());
    expect(s.state.value.phase, SessionPhase.ready);
  });

  test('play requested during BINDING starts playback when ready', () async {
    final kit = FakeVideoKit();
    final s = await kit.createSession(const VideoKitSessionConfig());
    final f = s.bind(_video);
    expect(await s.execute(const Play()), const Executed());
    await kit.clock.advance(const Duration(seconds: 1));
    await f;
    expect(s.state.value.phase, SessionPhase.playing);
  });

  test('buffering window', () async {
    final (kit, s) = await _bound(
      Scenario.buffering(
        at: const Duration(seconds: 2),
        duration: const Duration(seconds: 1),
      ),
    );
    await _playTo(kit, s, const Duration(milliseconds: 2100));
    expect(s.state.value.phase, SessionPhase.buffering);
    expect(s.state.value.positionUs, 2000000);
    await kit.clock.advance(const Duration(milliseconds: 1000));
    expect(s.state.value.phase, SessionPhase.playing);
  });

  test('unsupported and resource exhausted at bind', () async {
    final (_, s) = await _bound(
      const Scenario.unsupported(UnsupportedPart.audioCodec),
      expectOk: false,
    );
    expect(s.state.value.phase, SessionPhase.errorFatal);
    expect(s.state.value.error?.code, ErrorCode.unsupportedAudioCodec);
    expect(
      s.state.value.error?.suggestedAction,
      SuggestedAction.chooseOtherTrack,
    );

    final (kit2, s2) = await _bound(
      const Scenario.resourceExhausted(),
      expectOk: false,
    );
    expect(s2.state.value.phase, SessionPhase.errorRecoverable);
    expect(s2.state.value.error?.code, ErrorCode.decoderResourceExhausted);
    // Retry (re-bind) succeeds: recoverable errors fire once.
    final retry = s2.bind(_video);
    await kit2.clock.advance(const Duration(seconds: 1));
    expect(await retry, const Executed());
  });

  test('corrupt at 45 s is fatal', () async {
    final (kit, s) = await _bound(const Scenario.corrupt());
    await _playTo(kit, s, const Duration(seconds: 46));
    expect(s.state.value.phase, SessionPhase.errorFatal);
    expect(s.state.value.error?.code, ErrorCode.corruptMedia);
    expect(s.state.value.positionUs, 45000000);
  });

  test('disconnect is recoverable and host retry resumes position', () async {
    final (kit, s) = await _bound(
      const Scenario.disconnect(at: Duration(seconds: 3)),
      config: VideoKitConfig(hostCallbacks: _RetryHost()),
    );
    final events = <VideoKitEvent>[];
    final sub = s.events.listen(events.add);
    await _playTo(kit, s, const Duration(milliseconds: 3100));
    expect(
      s.state.value.phase,
      anyOf(SessionPhase.errorRecoverable, SessionPhase.binding),
    );
    expect(
      events.whereType<ErrorRaised>().single.error.code,
      ErrorCode.sourceDisconnected,
    );
    await kit.clock.advance(const Duration(seconds: 1));
    expect(s.state.value.phase, SessionPhase.ready);
    expect(s.state.value.positionUs, 3000000);
    await s.execute(const Play());
    await kit.clock.advance(const Duration(seconds: 2));
    expect(s.state.value.phase, SessionPhase.playing, reason: 'fires once');
    await sub.cancel();
  });

  test('host action timeout uses the 10 s default', () async {
    const del = VideoKitHostAction(
      actionId: 'delete',
      labelKey: 'delete',
      contentDescriptionKey: 'delete',
      icon: HostIcon.builtIn('delete'),
      placement: ActionPlacement.overflow,
    );
    final kit = FakeVideoKit(
      defaultScenario: Scenario.hostActionTimeout('delete'),
    );
    final s = await kit.createSession(const VideoKitSessionConfig());
    final b = s.bind(_video, hostActions: const [del]);
    await kit.clock.advance(const Duration(seconds: 1));
    await b;
    final failed = s.events.firstWhere((e) => e is HostActionFailed);
    await s.requestHostAction('delete');
    await kit.clock.advance(const Duration(seconds: 9));
    expect(s.state.value.hostActions.single.isPending, isTrue);
    await kit.clock.advance(const Duration(seconds: 1, milliseconds: 1));
    final e = await failed as HostActionFailed;
    expect(e.error.code, ErrorCode.hostCallbackFailed);
    expect(kit.hostBridge.failureCount, greaterThanOrEqualTo(1));
  });

  test('ended → play restarts; animated image loops; demo flags', () async {
    final (kit, s) = await _bound(const Scenario.normal());
    final d = s.state.value.durationUs!;
    final seek = s.execute(SeekTo(d - 500000));
    await kit.clock.advance(const Duration(seconds: 1));
    await seek;
    await _playTo(kit, s, const Duration(seconds: 1));
    expect(s.state.value.phase, SessionPhase.ended);
    await s.execute(const Play());
    expect(s.state.value.positionUs, 0);
    expect(s.isDemo, isTrue);
    expect(s.textureId.value, isNull);
    expect(kit.isDemo, isTrue);

    final img = await kit.createSession(const VideoKitSessionConfig());
    final b = img.bind(
      const VideoKitMediaSource(
        mediaToken: 'gif',
        mediaKind: MediaKind.imageAnimated,
        sourceRef: DemoSourceRef('normal'),
      ),
    );
    await kit.clock.advance(const Duration(seconds: 1));
    await b;
    expect(await img.execute(const Play()), const Executed());
    await kit.clock.advance(const Duration(seconds: 5));
    expect(img.state.value.phase, SessionPhase.playing);
    expect(img.state.value.positionUs, lessThan(2000000));
    expect(
      await img.execute(const SetSpeed(2)),
      const Unsupported(UnsupportedReason.mediaKind),
    );
  });

  test('session limit of 12', () async {
    final kit = FakeVideoKit();
    for (var i = 0; i < 12; i++) {
      await kit.createSession(const VideoKitSessionConfig());
    }
    await expectLater(
      kit.createSession(const VideoKitSessionConfig()),
      throwsA(isA<VideoKitException>()),
    );
    await kit.sessions.first.release();
    await kit.createSession(const VideoKitSessionConfig());
  });

  group('edit project scenarios', () {
    Future<(FakeVideoKit, FakeEditProject, String)> project(Scenario sc) async {
      final kit = FakeVideoKit(defaultScenario: sc);
      final p =
          await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
      final add = p.addSource(_video);
      await kit.clock.advance(const Duration(milliseconds: 300));
      final src = await add;
      await p.apply(AddClip(src.sourceId, 0, 10000000));
      return (kit, p, src.sourceId);
    }

    Future<String> faceMask(FakeVideoKit kit, FakeEditProject p) async {
      final r = await p.apply(
        const AddMask(
          MaskType.face,
          MaskRegion(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
          0,
          10000000,
        ),
      ) as EditApplied;
      return r.createdId!;
    }

    test('tracking LOST coverage, precheck, correction and accept', () async {
      final (kit, p, _) = await project(const Scenario.trackingLost());
      final maskId = await faceMask(kit, p);
      final candidates = p.detectCandidates(0);
      await kit.clock.advance(const Duration(milliseconds: 400));
      expect((await candidates).candidates, hasLength(2));

      // Uncovered before tracking.
      var pre = await p.checkExport(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      expect(pre.canExport, isFalse);
      expect(pre.uncoveredRanges.single.state, TrackingState.notAnalyzed);

      final start = await p.apply(
        StartTracking(
          maskId,
          TrackingKind.face,
          seedRegion: const MaskRegion(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
        ),
      );
      expect(start, isA<EditApplied>());
      expect(p.state.value.phase, EditPhase.tracking);
      expect(await p.apply(const RemoveClip('x')), isA<EditRejected>());
      await kit.clock.advance(const Duration(seconds: 1));
      expect(p.state.value.tracking[maskId]!.progress, greaterThan(0));
      await kit.clock.advance(const Duration(seconds: 3));
      final run = p.state.value.tracking[maskId]!;
      expect(run.status, TrackingRunStatus.completed);
      expect(p.state.value.phase, EditPhase.ready);
      expect(run.coverage.stateAt(5000000), TrackingState.lost);
      expect(run.coverage.blockingSegments.single.startUs, 4000000);

      pre = await p.checkExport(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      expect(pre.canExport, isFalse);
      expect(pre.uncoveredRanges.single.state, TrackingState.lost);
      final accepted = await p.checkExport(
        const VideoKitExportRequest(acceptUncoveredTracking: true),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      expect(accepted.canExport, isTrue);

      // Correction from 4 s recomputes and resolves the LOST range.
      await p.apply(
        CorrectTracking(
          maskId,
          4000000,
          const MaskRegion(x: 0.4, y: 0.3, width: 0.2, height: 0.2),
        ),
      );
      expect(p.state.value.phase, EditPhase.tracking);
      expect(
        p.state.value.tracking[maskId]!.coverage.stateAt(5000000),
        TrackingState.notAnalyzed,
      );
      await kit.clock.advance(const Duration(seconds: 3));
      expect(p.state.value.tracking[maskId]!.coverage.isComplete, isTrue);
      expect(
        p.state.value.masks.single.keyframes.any(
          (k) => k.source == KeyframeSource.tracker,
        ),
        isTrue,
      );
    });

    test('accept range and cancel tracking', () async {
      final (kit, p, _) = await project(const Scenario.trackingLost());
      final maskId = await faceMask(kit, p);
      await p.apply(
        StartTracking(
          maskId,
          TrackingKind.face,
          seedRegion: const MaskRegion(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
        ),
      );
      await kit.clock.advance(const Duration(seconds: 4));
      expect(
        await p.apply(AcceptTrackingRange(maskId, 4000000, 6000000)),
        isA<EditApplied>(),
      );
      expect(p.state.value.tracking[maskId]!.coverage.isComplete, isTrue);
      expect(await p.apply(CancelTracking(maskId)), isA<EditRejected>());

      final (kit2, p2, _) = await project(const Scenario.normal());
      final m2 = await faceMask(kit2, p2);
      await p2.apply(
        StartTracking(
          m2,
          TrackingKind.face,
          seedRegion: const MaskRegion(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
        ),
      );
      await kit2.clock.advance(const Duration(milliseconds: 500));
      expect(await p2.apply(CancelTracking(m2)), isA<EditApplied>());
      expect(p2.state.value.phase, EditPhase.ready);
      expect(p2.state.value.tracking[m2]!.status, TrackingRunStatus.cancelled);
      await kit2.clock.advance(const Duration(seconds: 5));
      expect(
        p2.state.value.tracking[m2]!.status,
        TrackingRunStatus.cancelled,
        reason: 'stale results are dropped',
      );
    });

    test('exportFails at encode with OUTPUT_SPACE_INSUFFICIENT', () async {
      final (kit, p, _) = await project(Scenario.exportFails());
      final events = <VideoKitEditEvent>[];
      final sub = p.events.listen(events.add);
      final f = p.export(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      await kit.clock.advance(const Duration(seconds: 5));
      final r = await f;
      expect(r, isA<ExportFailed>());
      expect((r as ExportFailed).error.code, ErrorCode.outputSpaceInsufficient);
      expect(r.error.suggestedAction, SuggestedAction.freeSpace);
      expect(r.stage, ExportStage.encoding);
      expect(p.state.value.phase, EditPhase.failed);
      await Future<void>.delayed(Duration.zero);
      expect(events.whereType<ExportFinished>(), hasLength(1));
      await sub.cancel();
      // Editing after a failed export returns to READY.
      await p.apply(const SetMaskEnabled('none', true));
      final again = await p.apply(
        const AddMask(
          MaskType.manual,
          MaskRegion(x: 0, y: 0, width: 0.1, height: 0.1),
          0,
          1000000,
        ),
      );
      expect(again, isA<EditApplied>());
      expect(p.state.value.phase, EditPhase.ready);
    });

    test('exportCancelSlow stays CANCELLING for 2 s', () async {
      final (kit, p, _) = await project(const Scenario.exportCancelSlow());
      final f = p.export(
        const VideoKitExportRequest(exportId: 'e1'),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      await kit.clock.advance(const Duration(milliseconds: 800));
      expect(p.state.value.export?.stage, ExportStage.encoding);
      expect(p.state.value.export?.fraction, isNotNull);
      await p.cancelExport('e1');
      expect(p.state.value.export?.cancellable, isFalse);
      await kit.clock.advance(const Duration(milliseconds: 1500));
      expect(p.state.value.phase, EditPhase.cancelling);
      await kit.clock.advance(const Duration(seconds: 1));
      expect(await f, const ExportCancelled('e1'));
      expect(p.state.value.phase, EditPhase.cancelled);
    });

    test('space precheck and undo limit', () async {
      final (kit, p, src) = await project(const Scenario.normal());
      final pre = await p.checkExport(
        const VideoKitExportRequest(),
        const VideoKitOutputSink(
          sinkRef: 'demo:t',
          capabilities: SinkCapabilities(knownFreeSpaceBytes: 10),
        ),
      );
      expect(pre.problems.single.code, ErrorCode.outputSpaceInsufficient);
      expect(pre.estimate.sizeBytes, greaterThan(0));
      final bad = await p.checkExport(
        const VideoKitExportRequest(presetId: 'NOPE'),
        const VideoKitOutputSink(sinkRef: 'demo:t'),
      );
      expect(bad.problems.single.code, ErrorCode.encoderUnavailable);

      final small = await kit.createEditProject(
        EditProjectConfig(undoLimit: 2),
      );
      final add = small.addSource(_video);
      await kit.clock.advance(const Duration(milliseconds: 300));
      final s2 = await add;
      for (var i = 0; i < 4; i++) {
        await small.apply(AddClip(s2.sourceId, 0, 1000000));
      }
      expect(await small.undo(), isA<EditApplied>());
      expect(await small.undo(), isA<EditApplied>());
      expect(await small.undo(), isA<EditRejected>());
      expect(small.state.value.timeline.clips, hasLength(2));
      expect(src, isNotEmpty);
    });

    test('restored snapshot keeps coverage and ids stay unique', () async {
      final (kit, p, src) = await project(const Scenario.trackingLost());
      final maskId = await faceMask(kit, p);
      await p.apply(
        StartTracking(
          maskId,
          TrackingKind.face,
          seedRegion: const MaskRegion(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
        ),
      );
      await kit.clock.advance(const Duration(seconds: 4));
      final restored = await kit.restoreEditProject(
        await p.snapshot(),
        EditProjectConfig(),
      );
      expect(restored.state.value.tracking, p.state.value.tracking);
      final r = await restored.apply(AddClip(src, 0, 1000000)) as EditApplied;
      expect(
        p.state.value.timeline.clips.map((c) => c.clipId),
        isNot(contains(r.createdId)),
      );
      await expectLater(
        kit.restoreEditProject(
          const SerializedEditProject(schemaVersion: 1, json: 'not json'),
          EditProjectConfig(),
        ),
        throwsA(isA<VideoKitException>()),
      );
      unawaited(kit.close());
    });
  });
}
