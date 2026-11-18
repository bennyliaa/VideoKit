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
  icon: HostIcon.builtIn('favorite'),
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
      // 04A C1: channelCount.
      const a = TrackInfo(id: 'a', codec: 'audio/ac3', channelCount: 6);
      expectValueSemantics(a, a.copyWith(), a.copyWith(channelCount: 2));
      expect(a.copyWith(channelCount: null).channelCount, isNull);
      expect(a.copyWith().channelCount, 6);
      expect(const TrackInfo(id: 'x').channelCount, isNull);
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
      final st = HostActionState(action: _action);
      expect(st.isPending, isFalse);
      expect(st.copyWith(pending: true).isPending, isTrue);
      expect(
        HostActionState(action: _action.copyWith(pending: true)).pending,
        isTrue,
        reason: 'defaults to the host flag (04A S1)',
      );
      expect(
        st.copyWith(lastStatus: HostActionStatus.failed).lastStatus,
        HostActionStatus.failed,
      );
      expectValueSemantics(st, st.copyWith(), st.copyWith(lastError: _err));
      expect(const HostIcon.resource('7'), const HostIconResource('7'));
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
        const HostActionResult.failed('host.tag.failed'),
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
    test('04A L3: snapshot looping round-trips; old snapshots read null', () {
      const s = VideoKitPlaybackState(mediaToken: 't', looping: false);
      expect(VideoKitPlaybackState.fromJson(s.toJson()).looping, isFalse);
      final old = s.toJson()..remove('looping');
      expect(VideoKitPlaybackState.fromJson(old).looping, isNull);
      expect(s.copyWith(looping: null).looping, isNull);
      expect(s, isNot(s.copyWith(looping: true)));
    });

    test('04A P1/P2: MediaInfo, ThumbnailResult', () {
      const m = MediaInfo(
        container: 'video/mp4',
        videoCodec: 'video/avc',
        width: 1920,
        height: 1080,
        frameRate: 30,
      );
      expectValueSemantics(m, m.copyWith(), m.copyWith(width: 1280));
      expect(m.copyWith(videoCodec: null).videoCodec, isNull);
      final s = VideoKitSessionState(phase: SessionPhase.ready);
      expect(s.mediaInfo, isNull);
      expect(s.copyWith(mediaInfo: m).mediaInfo, m);
      expect(s.copyWith(mediaInfo: m), isNot(s));
      final a = ThumbnailCaptured(
        bytes: Uint8List.fromList(const [1, 2]),
        width: 2,
        height: 1,
      );
      expect(
        a,
        ThumbnailCaptured(
          bytes: Uint8List.fromList(const [1, 2]),
          width: 2,
          height: 1,
        ),
      );
      expect(a.mimeType, 'image/jpeg');
      const f = ThumbnailFailed(
        VideoKitStableError.invalidState(stage: ErrorStage.playback),
      );
      expect(f.error.code, ErrorCode.invalidState);
    });

    test('04A L1/L2: SetLooping, looping, ImageDetails', () {
      expect(const SetLooping(true), const SetLooping(true));
      expect(const SetLooping(true), isNot(const SetLooping(false)));
      expect(const SetLooping(false).kind, 'setLooping');
      const d = ImageDetails(frameCount: 48, decodedBytes: 10, sampleSize: 2);
      expectValueSemantics(d, d.copyWith(), d.copyWith(sampleSize: 4));
      expect(d.copyWith(frameCount: null).frameCount, isNull);
      final s = VideoKitSessionState(phase: SessionPhase.ready);
      expect(s.looping, isFalse);
      expect(s.imageDetails, isNull);
      final l = s.copyWith(looping: true, imageDetails: d);
      expect(l.looping, isTrue);
      expect(l.imageDetails, d);
      expect(l, isNot(s));
      expect(l.copyWith(imageDetails: null).imageDetails, isNull);
    });

    test('VideoKitSessionState value semantics and immutable lists', () {
      final s = VideoKitSessionState(
        phase: SessionPhase.ready,
        mediaKind: MediaKind.video,
        durationUs: 1000,
        audioTracks: const [TrackInfo(id: 'a')],
        hostActions: [HostActionState(action: _action)],
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
        lastViewedAtEpochMs: 1762430400000,
        sessionId: 's1',
        subtitlesEnabled: true,
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

    test('04A E4: TimeRangeUs, MaskTrack.acceptedRanges, nullable probe '
        'and video codec', () {
      const r = TimeRangeUs(500000, 1000000);
      expect(r.durationUs, 500000);
      expect(r.isValid, isTrue);
      expect(const TimeRangeUs(5, 5).isValid, isFalse);
      expect(r.contains(500000), isTrue);
      expect(r.contains(1000000), isFalse, reason: 'half open');
      expect(r.covers(600000, 900000), isTrue);
      expect(r.covers(400000, 900000), isFalse);
      expectValueSemantics(
        r,
        const TimeRangeUs(500000, 1000000),
        const TimeRangeUs(0, 1000000),
      );
      final m = MaskTrack(
        maskId: 'm',
        type: MaskType.face,
        startUs: 0,
        endUs: 2000000,
      );
      expect(m.acceptedRanges, isEmpty);
      final accepted = m.copyWith(acceptedRanges: const [r]);
      expect(accepted.isAccepted(600000, 900000), isTrue);
      expect(accepted.isAccepted(0, 900000), isFalse);
      expect(accepted == m, isFalse);
      expect(accepted.copyWith(), accepted);
      const p = SourceProbe(durationUs: 1, width: 2, height: 3);
      expect(p.videoCodec, isNull);
      expect(p.copyWith(videoCodec: 'video/avc').copyWith(videoCodec: null), p);
      const s = EditSource(sourceId: 's', mediaToken: 't');
      expect(s.probe, isNull);
      expect(s.copyWith(probe: p).copyWith(probe: null), s);
    });

    test('M5A-A1: MaskAvatar, MaskTrack.avatar, rollAt, SetMaskAvatar', () {
      const a = MaskAvatar(avatarToken: 'builtin:1');
      expect((a.scale, a.offsetX, a.offsetY, a.followRotation), (1.0, 0.0, 0.0, true));
      expect(a.isBuiltin, isTrue);
      expect(const MaskAvatar(avatarToken: 'app-avatar-1').isBuiltin, isFalse);
      expectValueSemantics(a, a.copyWith(), a.copyWith(scale: 2));
      expect(a.toString(), isNot(contains('builtin:1')), reason: 'redacted');
      expect(MaskStyle.image.wireName, 'IMAGE');
      expect(MaskStyle.fromName('IMAGE'), MaskStyle.image);
      final m = MaskTrack(
        maskId: 'm',
        type: MaskType.face,
        startUs: 0,
        endUs: 3000000,
        keyframes: const [
          MaskKeyframe(
            atUs: 0,
            region: MaskRegion(x: 0, y: 0, width: 0.1, height: 0.1),
            rollDeg: 0,
          ),
          MaskKeyframe(
            atUs: 1000000,
            region: MaskRegion(x: 0, y: 0, width: 0.1, height: 0.1),
          ),
          MaskKeyframe(
            atUs: 2000000,
            region: MaskRegion(x: 0, y: 0, width: 0.1, height: 0.1),
            rollDeg: 20,
          ),
        ],
      );
      expect(m.avatar, isNull);
      expect(m.rollAt(1000000), 10, reason: 'between keyframes with a roll');
      expect(m.rollAt(2500000), 20, reason: 'held after the last');
      expect(m.rollAt(3000000), isNull, reason: 'outside the range');
      // E7 Q2: no keyframe with a roll → 0 (not null) inside the range.
      expect(
        MaskTrack(maskId: 'n', type: MaskType.face, startUs: 0, endUs: 9)
            .rollAt(1),
        0,
      );
      final withAvatar = m.copyWith(avatar: a);
      expect(withAvatar.avatar, a);
      expect(withAvatar == m, isFalse);
      expect(withAvatar.copyWith(avatar: null), m);
      expectValueSemantics(
        SetMaskAvatar('m', a),
        SetMaskAvatar('m', a),
        SetMaskAvatar('m', a.copyWith(followRotation: false)),
      );
      expect(SetMaskAvatar('m', a).undoable, isTrue);
      const k = MaskKeyframe(
        atUs: 0,
        region: MaskRegion(x: 0, y: 0, width: 0.1, height: 0.1),
      );
      expect(k.copyWith(rollDeg: 5).copyWith(rollDeg: null), k);
    });

    test('M5A-A1: avatar value types', () {
      const r = AvatarRequest(projectId: 'p', maskId: 'm');
      expectValueSemantics(
        r,
        const AvatarRequest(projectId: 'p', maskId: 'm'),
        const AvatarRequest(projectId: 'p', maskId: 'm', currentToken: 't'),
      );
      const o = AvatarPrepareOptions();
      expect((o.cropToHead, o.feather, o.faceIndex), (true, 0.5, null));
      expectValueSemantics(o, o.copyWith(), o.copyWith(cropToHead: false));
      final s = AvatarStroke(
        brush: AvatarBrush.erase,
        points: const [(0.5, 0.5)],
        radius: 0.1,
      );
      expectValueSemantics(
        s,
        AvatarStroke(
          brush: AvatarBrush.erase,
          points: const [(0.5, 0.5)],
          radius: 0.1,
        ),
        AvatarStroke(
          brush: AvatarBrush.restore,
          points: const [(0.5, 0.5)],
          radius: 0.1,
        ),
      );
      final img = AvatarImage(
        avatarId: 'a',
        png: Uint8List.fromList([1, 2, 3]),
        width: 1,
        height: 1,
        headBox: const MaskRegion(x: 0, y: 0, width: 1, height: 1),
      );
      expectValueSemantics(
        img,
        img.copyWith(),
        img.copyWith(png: Uint8List.fromList([9])),
      );
      expect(AvatarSupport.fromName('MODEL_MISSING'), AvatarSupport.modelMissing);
      expect(AvatarSupport.fromName('???'), AvatarSupport.unsupported);
      expect(AvatarBrush.restore.wireName, 'RESTORE');
      expect(VideoKitCapabilities().avatar, AvatarSupport.unsupported);
    });

    test('MaskTrack.regionAt interpolates linearly and holds at ends', () {
      const a = MaskRegion(x: 0, y: 0, width: 0.2, height: 0.2);
      const b = MaskRegion(x: 0.4, y: 0.2, width: 0.4, height: 0.2);
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
      expect(mid.x, closeTo(0.2, 1e-9));
      expect(mid.width, closeTo(0.3, 1e-9));
      expect(m.regionAt(1000), isNull, reason: 'end exclusive');
      expect(m.regionAt(-1), isNull);
      expectValueSemantics(m, m.copyWith(), m.copyWith(enabled: false));
      expect(a.right, 0.2);
    });

    test('CoverageReport blocking segments', () {
      final r = CoverageReport(
        segments: const [
          CoverageRange(startUs: 10, endUs: 20, state: TrackingState.lost),
          CoverageRange(startUs: 0, endUs: 10, state: TrackingState.tracked),
          CoverageRange(
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
          seedRegion: MaskRegion(x: 0, y: 0, width: 1, height: 1),
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
    test('precheck: ok only without problems (04A S2)', () {
      final ok = ExportPrecheck(
        estimate: const EditEstimate(durationUs: 5),
        warnings: const [ExportWarnings.trackingCoverageAccepted],
        writeMode: SinkWriteMode.randomWrite,
      );
      expect(ok.ok, isTrue);
      expect(ok.canExport, isTrue);
      final blocked = ok.copyWith(problems: const [_err]);
      expect(blocked.ok, isFalse);
      expectValueSemantics(ok, ok.copyWith(), blocked);
      expect(SinkWriteMode.fromName('X'), SinkWriteMode.sequential);
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
          FeatureKey.faceTracking: UnsupportedReason.moduleNotInstalled,
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
