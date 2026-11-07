import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';

/// Checks value semantics: [a] equals an identical-content [same], differs
/// from [different], hash codes agree and toString is non-empty.
void expectValueSemantics(Object a, Object same, Object different) {
  expect(a, same);
  expect(a.hashCode, same.hashCode);
  expect(a, isNot(different));
  expect(a.toString(), isNotEmpty);
}

const _err = VideoKitStableError(
  code: ErrorCode.corruptMedia,
  stage: ErrorStage.decode,
);

const _action = VideoKitHostAction(
  actionId: 'fav',
  labelKey: 'favorite',
  contentDescriptionKey: 'favorite_cd',
  icon: HostIcon.builtin('favorite'),
  placement: ActionPlacement.primaryBar,
);

void main() {
  group('media', () {
    test('VideoSize', () {
      const s = VideoSize(1920, 1080);
      expectValueSemantics(
        s,
        const VideoSize(1920, 1080),
        s.copyWith(width: 1),
      );
      expect(s.aspectRatio, closeTo(16 / 9, 1e-9));
      expect(s.longEdge, 1920);
      expect(s.isPortrait, isFalse);
      expect(const VideoSize(1, 0).aspectRatio, 0);
    });

    test('TrackInfo copyWith can clear nullable fields', () {
      const t = TrackInfo(id: 'a1', language: 'en', label: 'English');
      expectValueSemantics(t, t.copyWith(), t.copyWith(id: 'a2'));
      expect(t.copyWith(language: null).language, isNull);
      expect(t.copyWith().language, 'en');
    });

    test('MediaTransform', () {
      const t = MediaTransform(scale: 2, rotationDeg: 90);
      expectValueSemantics(t, t.copyWith(), t.copyWith(panX: 0.1));
      expect(t.isZoomed, isTrue);
      expect(MediaTransform.identity.isZoomed, isFalse);
    });

    test('VideoKitMediaSource and source refs', () {
      const src = VideoKitMediaSource(
        mediaToken: 'm1',
        mediaKind: MediaKind.video,
        sourceRef: DemoSourceRef('normal'),
        displayName: 'clip',
      );
      expectValueSemantics(
        src,
        src.copyWith(),
        src.copyWith(sourceRef: const RegisteredSourceRef('r')),
      );
      expect(src.copyWith(displayName: null).displayName, isNull);
      expect(const UriSourceRef('content://x').wireRef, 'uri:content://x');
      expect(
        const UriSourceRef('content://x').toString(),
        isNot(contains('x')),
      );
      expect(const RegisteredSourceRef('r1').wireRef, 'registered:r1');
      expect(const DemoSourceRef('slow').wireRef, 'demo:slow');
    });
  });

  group('host', () {
    test('VideoKitHostAction / HostActionState', () {
      expectValueSemantics(
        _action,
        _action.copyWith(),
        _action.copyWith(selected: true),
      );
      expect(
        _action.copyWith(badgeText: '3').copyWith(badgeText: null).badgeText,
        isNull,
      );
      const st = HostActionState(action: _action);
      expect(st.isPending, isFalse);
      expect(st.copyWith(inFlight: true).isPending, isTrue);
      expect(
        st.copyWith(action: _action.copyWith(pending: true)).isPending,
        isTrue,
      );
      expectValueSemantics(st, st.copyWith(), st.copyWith(lastError: _err));
      expect(const HostIcon.hostResource(7), const HostResourceIcon(7));
    });

    test('requests and results', () {
      const r = HostActionRequest(
        actionId: 'a',
        sessionId: 's',
        mediaToken: 'm',
      );
      expectValueSemantics(r, r.copyWith(), r.copyWith(actionId: 'b'));
      const res = HostActionResult.pending(_action);
      expect(res.status, HostActionStatus.pending);
      expectValueSemantics(
        res,
        res.copyWith(),
        const HostActionResult.failed(_err),
      );
      const n = NavigationRequest(
        sessionId: 's',
        direction: NavigationDirection.next,
      );
      expectValueSemantics(
        n,
        n.copyWith(),
        n.copyWith(direction: NavigationDirection.previous),
      );
      const t = HostCallbackTimeouts();
      expect(t.hostAction, const Duration(seconds: 10));
      expect(t.navigation, const Duration(seconds: 3));
      expect(t.notification, const Duration(seconds: 2));
      expectValueSemantics(
        t,
        t.copyWith(),
        t.copyWith(navigation: Duration.zero),
      );
    });
  });

  group('session', () {
    test('VideoKitSessionState value semantics and immutable lists', () {
      final s = VideoKitSessionState(
        phase: SessionPhase.ready,
        mediaKind: MediaKind.video,
        durationUs: 1000,
        audioTracks: const [TrackInfo(id: 'a')],
        hostActions: const [HostActionState(action: _action)],
      );
      expectValueSemantics(
        s,
        s.copyWith(),
        s.copyWith(phase: SessionPhase.playing),
      );
      expect(s.copyWith(durationUs: null).durationUs, isNull);
      expect(s.copyWith(error: _err).error, _err);
      expect(
        () => s.audioTracks.add(const TrackInfo(id: 'b')),
        throwsUnsupportedError,
      );
      expect(VideoKitSessionState.initial().phase, SessionPhase.created);
      expect(VideoKitSessionState.initial().controlsVisible, isTrue);
    });

    test('commands have value semantics and stable kinds', () {
      final cmds = <VideoKitCommand>[
        const Play(),
        const Pause(),
        const SeekTo(5, mode: SeekMode.preview),
        const SetSpeed(1.5),
        const SetMuted(true),
        const SetVolume(0.3),
        const SelectAudioTrack('a'),
        const SelectSubtitleTrack(null),
        const SetTransform(MediaTransform(scale: 2)),
        const SetOrientation(OrientationRequest.landscape),
        const SetFullscreen(true),
        const SetVisibility(SessionVisibility.background),
        const SetActiveAudio(true, 3),
        const HideContentForLock(true),
        const InvokeHostAction('fav'),
        const Release(),
      ];
      final kinds = cmds.map((c) => c.kind).toSet();
      expect(kinds, hasLength(cmds.length));
      for (final c in cmds) {
        expect(c, c);
        expect(c.toString(), isNotEmpty);
      }
      expectValueSemantics(
        const SeekTo(5),
        const SeekTo(5).copyWith(),
        const SeekTo(5).copyWith(mode: SeekMode.exact),
      );
      expect(
        const SelectAudioTrack('a').copyWith(trackId: null).trackId,
        isNull,
      );
      expect(
        const SetActiveAudio(true, 3).copyWith(audioEpoch: 4).audioEpoch,
        4,
      );
    });

    test('command results', () {
      expect(const Executed(), const Executed());
      expect(const Superseded(), isNot(const Executed()));
      expectValueSemantics(
        const Rejected(_err),
        const Rejected(_err).copyWith(),
        Rejected(_err.copyWith(retryable: true)),
      );
      expectValueSemantics(
        const Unsupported(UnsupportedReason.trackNotFound),
        const Unsupported(UnsupportedReason.trackNotFound).copyWith(),
        const Unsupported(UnsupportedReason.valueOutOfRange),
      );
      expect(const SessionReleased(), const SessionReleased());
    });

    test('events', () {
      expect(const SourceReleased('m'), const SourceReleased('m'));
      expect(
        const HostActionFailed('a', _err),
        const HostActionFailed('a', _err),
      );
      expect(
        const TransientNotice(NoticeCodes.seekClamped),
        isNot(const TransientNotice(NoticeCodes.resourceDegraded)),
      );
      expect(const UserSeek('s', 1, 2), const UserSeek('s', 1, 2));
      expect(
        const WatchTimeAccumulated('s', 5).hashCode,
        const WatchTimeAccumulated('s', 5).hashCode,
      );
    });

    test('VideoKitPlaybackState JSON round trip and schema rules', () {
      final p = VideoKitPlaybackState(
        mediaToken: 'm1',
        zoom: 2,
        panX: 0.1,
        rotationDeg: 90,
        fitMode: FitMode.fill,
        preferredOrientation: OrientationRequest.landscape,
        fullscreen: true,
        positionUs: 123,
        speed: 1.5,
        volume: 0.5,
        muted: true,
        subtitleTrackId: 's1',
        audioTrackId: 'a1',
        lastViewedAt: DateTime.utc(2026, 11, 6, 12),
      );
      expect(VideoKitPlaybackState.fromJson(p.toJson()), p);
      expectValueSemantics(p, p.copyWith(), p.copyWith(zoom: 3));
      expect(p.copyWith(positionUs: null).positionUs, isNull);
      expect(p.transform.rotationDeg, 90);

      // Older/minimal snapshot: defaults fill missing optional fields.
      final minimal = VideoKitPlaybackState.fromJson({'schemaVersion': 1});
      expect(minimal, const VideoKitPlaybackState());

      // Unknown future major version is rejected safely.
      expect(
        () => VideoKitPlaybackState.fromJson({'schemaVersion': 99}),
        throwsA(isA<VideoKitException>()),
      );
      expect(
        () => VideoKitPlaybackState.fromJson(<String, Object?>{}),
        throwsA(isA<VideoKitException>()),
      );
    });

    test('session config', () {
      const c = VideoKitSessionConfig(debugLabel: 'x');
      expectValueSemantics(
        c,
        c.copyWith(),
        c.copyWith(priority: ResourcePriority.offscreen),
      );
    });

    test('asStream emits current value then changes', () async {
      final n = ValueNotifier<int>(1);
      final values = <int>[];
      final sub = n.asStream().listen(values.add);
      await Future<void>.delayed(Duration.zero);
      n.value = 2;
      n.value = 3;
      await Future<void>.delayed(Duration.zero);
      await sub.cancel();
      n.value = 4;
      await Future<void>.delayed(Duration.zero);
      expect(values, [1, 2, 3]);
      n.dispose();
    });
  });

  group('edit', () {
    test('Timeline durations and lookups', () {
      final tl = Timeline(
        sources: const [
          EditSource(
            sourceId: 's1',
            mediaToken: 'm1',
            probe: SourceProbe(
              durationUs: 10000000,
              width: 1920,
              height: 1080,
              videoCodec: 'video/avc',
            ),
          ),
        ],
        clips: const [
          EditClip(clipId: 'c1', sourceId: 's1', inUs: 0, outUs: 2000000),
          EditClip(clipId: 'c2', sourceId: 's1', inUs: 5000000, outUs: 6000000),
        ],
      );
      expect(tl.durationUs, 3000000);
      expect(tl.clipStartUs('c2'), 2000000);
      expect(tl.clipStartUs('nope'), isNull);
      expect(tl.sourceById('s1')?.mediaToken, 'm1');
      expectValueSemantics(tl, tl.copyWith(), tl.copyWith(clips: const []));
      expect(Timeline.empty().durationUs, 0);
    });

    test('MaskTrack.regionAt interpolates linearly and holds at ends', () {
      const a = NormalizedRect(left: 0, top: 0, width: 0.2, height: 0.2);
      const b = NormalizedRect(left: 0.4, top: 0.2, width: 0.4, height: 0.2);
      final m = MaskTrack(
        maskId: 'k',
        type: MaskType.manual,
        startUs: 0,
        endUs: 1000,
        keyframes: const [
          MaskKeyframe(atUs: 800, region: b),
          MaskKeyframe(atUs: 200, region: a),
        ],
      );
      expect(m.keyframes.first.atUs, 200, reason: 'sorted');
      expect(m.regionAt(100), a);
      expect(m.regionAt(900), b);
      final mid = m.regionAt(500)!;
      expect(mid.left, closeTo(0.2, 1e-9));
      expect(mid.width, closeTo(0.3, 1e-9));
      expect(m.regionAt(1000), isNull, reason: 'end exclusive');
      expect(m.regionAt(-1), isNull);
      expectValueSemantics(m, m.copyWith(), m.copyWith(enabled: false));
      expect(a.right, 0.2);
    });

    test('CoverageReport blocking segments', () {
      final r = CoverageReport(
        segments: const [
          CoverageSegment(startUs: 10, endUs: 20, state: TrackingState.lost),
          CoverageSegment(startUs: 0, endUs: 10, state: TrackingState.tracked),
          CoverageSegment(
            startUs: 20,
            endUs: 30,
            state: TrackingState.ambiguous,
            accepted: true,
          ),
        ],
      );
      expect(r.segments.first.startUs, 0);
      expect(r.blockingSegments, hasLength(1));
      expect(r.isComplete, isFalse);
      expect(r.stateAt(15), TrackingState.lost);
      expect(r.stateAt(99), isNull);
      expect(CoverageReport.empty().isComplete, isFalse);
      expectValueSemantics(r, r.copyWith(), CoverageReport.empty());
    });

    test('VideoKitEditState and commands', () {
      final s = VideoKitEditState(phase: EditPhase.ready, revision: 2);
      expectValueSemantics(s, s.copyWith(), s.copyWith(revision: 3));
      expect(s.copyWith(error: _err).copyWith(error: null).error, isNull);
      expect(s.maskById('x'), isNull);
      expect(
        const StartTracking(
          'm',
          TrackingKind.face,
          0,
          NormalizedRect(left: 0, top: 0, width: 1, height: 1),
        ).undoable,
        isFalse,
      );
      expect(const CancelTracking('m').undoable, isFalse);
      expect(const RemoveClip('c').undoable, isTrue);
      expectValueSemantics(
        const AddClip('s', 0, 10),
        const AddClip('s', 0, 10).copyWith(),
        const AddClip('s', 0, 10, index: 0),
      );
      expectValueSemantics(
        const EditApplied(3, createdId: 'x'),
        const EditApplied(3, createdId: 'x').copyWith(),
        const EditApplied(3),
      );
      expect(const EditProjectReleased(), const EditProjectReleased());
      expect(VideoKitEditState.initial().estimate, EditEstimate.unknown);
    });

    test('config, snapshot, token', () {
      final c = EditProjectConfig();
      expect(c.allowedPresetIds, ExportPresets.all);
      expectValueSemantics(c, c.copyWith(), c.copyWith(undoLimit: 1));
      const s = SerializedEditProject(schemaVersion: 1, json: '{}');
      expectValueSemantics(s, s.copyWith(), s.copyWith(json: '[]'));
      const t = SourceToken(sourceId: 's', mediaToken: 'm');
      expectValueSemantics(t, t.copyWith(), t.copyWith(sourceId: 'x'));
    });
  });

  group('export', () {
    test('precheck canExport depends on blocking issues', () {
      final ok = ExportPrecheck(estimatedDurationUs: 5);
      expect(ok.canExport, isTrue);
      final warn = ExportPrecheck(
        issues: const [
          PrecheckIssue(
            kind: PrecheckIssueKind.trackingCoverageIncomplete,
            blocking: false,
          ),
        ],
      );
      expect(warn.canExport, isTrue);
      final blocked = warn.copyWith(
        issues: const [PrecheckIssue(kind: PrecheckIssueKind.emptyTimeline)],
      );
      expect(blocked.canExport, isFalse);
      expectValueSemantics(ok, ok.copyWith(), blocked);
    });

    test('request, progress, results', () {
      const r = VideoKitExportRequest();
      expect(r.presetId, ExportPresets.original);
      expectValueSemantics(r, r.copyWith(), r.copyWith(presetId: 'P720'));
      const p = ExportProgress(exportId: 'e', stage: ExportStage.encoding);
      expect(p.fraction, isNull, reason: 'indeterminate by default');
      expectValueSemantics(p, p.copyWith(), p.copyWith(fraction: 0.5));
      final media = VideoKitExportedMedia(
        outputToken: 'o',
        container: 'mp4',
        extension: 'mp4',
        width: 1280,
        height: 720,
        durationUs: 1,
        sizeBytes: 2,
        createdAt: DateTime.utc(2026),
        editProjectId: 'p',
        exportPresetId: 'P720',
        warnings: const [ExportWarnings.demoNoRealFile],
        isDemo: true,
      );
      expectValueSemantics(media, media.copyWith(), media.copyWith(width: 1));
      expect(ExportSucceeded('e', media), ExportSucceeded('e', media));
      expect(
        const ExportFailed('e', _err, stage: ExportStage.encoding),
        isNot(const ExportFailed('e', _err)),
      );
      expect(const ExportCancelled('e'), const ExportCancelled('e'));
      const sink = VideoKitOutputSink(sinkRef: 'demo:tmp');
      expectValueSemantics(
        sink,
        sink.copyWith(),
        sink.copyWith(capabilities: const SinkCapabilities(randomWrite: true)),
      );
    });
  });

  group('capabilities and config', () {
    test('VideoKitCapabilities value semantics', () {
      final c = VideoKitCapabilities(
        suggestedHardwareVideoSessions: 4,
        outputFormats: const [
          OutputFormat(
            presetId: 'ORIGINAL',
            container: 'mp4',
            videoCodec: 'video/avc',
          ),
        ],
        unavailableReasons: const {
          FeatureKey.faceTracking: UnsupportedReason.moduleUnavailable,
        },
      );
      expectValueSemantics(c, c.copyWith(), c.copyWith(isDemo: true));
      expect(c.schemaVersion, VideoKitCapabilities.currentSchemaVersion);
      expect(c.playbackFeatures.speeds, [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]);
      expect(const CapabilityRequest(), CapabilityRequest.device);
    });

    test('VideoKitConfig and resource types', () {
      const c = VideoKitConfig();
      expect(c, c.copyWith());
      expect(c.logging, LoggingPolicy.releaseDefault);
      const req = ResourceRequest(
        sessionId: 's',
        kind: ResourceKind.videoDecoder,
        priority: ResourcePriority.visible,
      );
      expectValueSemantics(
        req,
        req.copyWith(),
        req.copyWith(kind: ResourceKind.encoder),
      );
      expect(
        const ReservationDenied('busy', DegradeSuggestion.pauseOffscreen),
        const ReservationDenied('busy', DegradeSuggestion.pauseOffscreen),
      );
      final u = ResourceUsage(kind: ResourceKind.encoder, held: 1);
      expectValueSemantics(u, u.copyWith(), u.copyWith(held: 2));
    });
  });
}
