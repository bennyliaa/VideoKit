import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/src/msg_mapping.dart';
import 'package:videokit_flutter/videokit_flutter.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

import 'fake_platform.dart';

class _Host extends NoopHostCallbacks {
  final List<String> calls = [];

  @override
  Future<RecoveryDecision> onRecoverableError(
    String sessionId,
    VideoKitStableError error,
  ) async {
    calls.add(
      'recoverable:$sessionId:${error.code.name}:${error.params['retryAfterMs']}',
    );
    return RecoveryDecision.retry;
  }

  @override
  Future<NavigationResult> onNavigationRequested(
    NavigationRequest request,
  ) async {
    calls.add('navigation:${request.direction.name}');
    return NavigationResult.accepted;
  }
}

void main() {
  late FakeHostApi api;
  late FakePlatform platform;

  setUp(() {
    api = FakeHostApi();
    platform = FakePlatform(api);
  });

  Future<FlutterVideoKit> connect([
    VideoKitConfig config = const VideoKitConfig(),
  ]) => FlutterVideoKit.connect(config, platform: platform);

  group('handshake (14 §8.3)', () {
    test(
      'sends protocol version and callback timeouts; demo flag from native',
      () async {
        final kit = await connect(
          const VideoKitConfig(
            callbackTimeouts: HostCallbackTimeouts(
              hostAction: Duration(seconds: 7),
            ),
          ),
        );
        expect(api.handshakeRequest!.protocolVersion, kChannelProtocolVersion);
        expect(api.handshakeRequest!.hostActionTimeoutMs, 7000);
        expect(api.handshakeRequest!.notificationTimeoutMs, 2000);
        expect(kit.isDemo, isTrue);
        expect(kit.apiVersion, VideoKitApiVersion.current);
      },
    );

    test('protocol mismatch fails with a clear error', () async {
      platform = FakePlatform(FakeHostApi(protocolVersion: 2));
      await expectLater(
        connect(),
        throwsA(
          isA<VideoKitInitException>().having(
            (e) => e.failure,
            'failure',
            VideoKitInitFailure.protocolMismatch,
          ),
        ),
      );
    });

    test('missing native backend is reported as noBackend', () async {
      platform = FakePlatform(
        FakeHostApi(
          handshakeError: Exception(
            'PlatformException(VIDEOKIT_NO_BACKEND, ...)',
          ),
        ),
      );
      await expectLater(
        connect(),
        throwsA(
          isA<VideoKitInitException>().having(
            (e) => e.failure,
            'failure',
            VideoKitInitFailure.noBackend,
          ),
        ),
      );
    });
  });

  group('session proxy (14 §8.5)', () {
    test('commands map to one host method each, with wire names', () async {
      final kit = await connect();
      final session = await kit.createSession(
        const VideoKitSessionConfig(
          initialVisibility: SessionVisibility.offscreen,
        ),
      );
      expect(api.calls.first, 'createSession:VISIBLE:OFFSCREEN');
      await session.bind(
        const VideoKitMediaSource(
          mediaToken: 'tok',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef('buffering'),
        ),
      );
      expect(api.lastBoundSource!.sourceRef, 'demo:buffering');
      await session.execute(const SeekTo(1500000, mode: SeekMode.exact));
      await session.execute(const SetVisibility(SessionVisibility.background));
      await session.execute(const SetOrientation(OrientationRequest.landscape));
      await session.execute(const SetActiveAudio(true, 9));
      await session.requestHostAction('tag');
      session.setControlsVisible(false);
      await Future<void>.delayed(Duration.zero);
      expect(
        api.calls,
        containsAll(<String>[
          'seekTo:1500000:exact',
          'setVisibility:BACKGROUND',
          'setOrientation:LANDSCAPE',
          'setActiveAudio:true:9',
          'requestHostAction:tag',
          'setControlsVisible:false',
        ]),
      );
    });

    test('unknown navigation result from native maps to failed', () async {
      final kit = await connect();
      final session = await kit.createSession(const VideoKitSessionConfig());
      expect(
        await session.requestNavigation(NavigationDirection.previous),
        NavigationResult.failed,
      );
      expect(api.calls.last, 'requestNavigation:PREVIOUS');
    });

    test('Dart readAt sources are not sent in protocol 1', () async {
      final kit = await connect();
      final session = await kit.createSession(const VideoKitSessionConfig());
      final result = await session.bind(
        VideoKitMediaSource(
          mediaToken: 't',
          mediaKind: MediaKind.video,
          sourceRef: DartSourceRef(_NoFactory()),
        ),
      );
      expect(result, const Unsupported(UnsupportedReason.notImplemented));
      expect(api.lastBoundSource, isNull);
    });

    test('rejections keep the stable error and its params', () async {
      api.nextResult = CommandResultMsg(
        kind: CommandResultKind.rejected,
        error: StableErrorMsg(
          code: 'INVALID_ARGUMENT',
          stage: 'PLAYBACK',
          retryable: false,
          suggestedAction: 'NONE',
          diagnostic: 'INVALID_ARGUMENT:SPEED',
          params: {'max': '4'},
        ),
      );
      final kit = await connect();
      final session = await kit.createSession(const VideoKitSessionConfig());
      final result = await session.execute(const Play()) as Rejected;
      expect(result.error.code, ErrorCode.invalidArgument);
      expect(result.error.params, {'max': '4'});
    });

    test('state is replaced from updates; stale and duplicate seq are dropped (14 §8.3)', () async {
      final kit = await connect();
      final session = await kit.createSession(
        const VideoKitSessionConfig(),
      ) as ChannelSession;
      final id = session.sessionId;
      platform.sessions.add(
        SessionUpdateMessage(
          sessionId: id,
          seq: 2,
          state: stateMsg(positionUs: 2000),
        ),
      );
      platform.sessions.add(
        SessionUpdateMessage(
          sessionId: id,
          seq: 1,
          state: stateMsg(positionUs: 1000),
        ),
      );
      platform.sessions.add(
        SessionUpdateMessage(
          sessionId: id,
          seq: 2,
          state: stateMsg(positionUs: 999),
        ),
      );
      platform.sessions.add(
        SessionUpdateMessage(
          sessionId: 'someone-else',
          seq: 9,
          state: stateMsg(positionUs: 7),
        ),
      );
      await Future<void>.delayed(Duration.zero);
      expect(session.state.value.positionUs, 2000);
      expect(session.state.value.phase, SessionPhase.ready);
      expect(session.videoSize.value, const VideoSize(1920, 1080));
      expect(session.lastSeq, 2);
      // No texture without a lease (04A S7).
      expect(api.calls.where((c) => c.startsWith('createTexture')), isEmpty);
    });

    test('texture leases: lazy creation, ref counting, delayed disposal (04A S7, 14 §8.5)', () {
      fakeAsync((async) {
        late ChannelSession session;
        connect()
            .then((kit) => kit.createSession(const VideoKitSessionConfig()))
            .then((s) => session = s as ChannelSession);
        async.flushMicrotasks();
        platform.sessions.add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 1,
            state: stateMsg(),
          ),
        );
        async.flushMicrotasks();
        final first = session.acquireTexture();
        final second = session.acquireTexture();
        async.flushMicrotasks();
        expect(first.textureId.value, 42);
        expect(api.calls.where((c) => c.startsWith('createTexture')), [
          'createTexture:1920 x 1080',
        ]);
        first.release();
        first.release(); // idempotent
        expect(session.textureLeaseCount, 1);
        second.release();
        async.elapse(const Duration(milliseconds: 1500));
        // Re-acquired within the delay: the texture is reused.
        final third = session.acquireTexture();
        async.elapse(const Duration(seconds: 3));
        expect(api.calls.where((c) => c == 'disposeTexture'), isEmpty);
        expect(third.textureId.value, 42);
        third.release();
        async.elapse(const Duration(milliseconds: 1999));
        expect(api.calls.where((c) => c == 'disposeTexture'), isEmpty);
        async.elapse(const Duration(milliseconds: 2));
        expect(api.calls.where((c) => c == 'disposeTexture').length, 1);
        expect(session.textureId.value, isNull);
        // Surface recycled by the native side while no texture is requested: ignored.
        platform.callbacks!.onTextureChanged(session.sessionId, 7);
        expect(session.textureId.value, isNull);
      });
    });

    test('events are forwarded; unknown event types are dropped', () async {
      final kit = await connect();
      final session = await kit.createSession(
        const VideoKitSessionConfig(),
      ) as ChannelSession;
      final events = <VideoKitEvent>[];
      session.events.listen(events.add);
      platform.sessions
        ..add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 1,
            event: EventMsg(type: 'SOURCE_RELEASED', mediaToken: 'm'),
          ),
        )
        ..add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 2,
            event: EventMsg(type: 'FROM_THE_FUTURE'),
          ),
        )
        ..add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 3,
            event: EventMsg(type: 'PLAYBACK_ENDED'),
          ),
        );
      await Future<void>.delayed(Duration.zero);
      expect(events, [const SourceReleased('m'), const PlaybackEnded()]);
    });

    test('release returns the final snapshot, is idempotent and disposes the texture', () async {
      final kit = await connect();
      final session = await kit.createSession(const VideoKitSessionConfig());
      final first = await session.release();
      final second = await session.release();
      expect(first, second);
      expect(first.fitMode, FitMode.original);
      expect(first.subtitlesEnabled, isFalse);
      expect(api.calls.where((c) => c.startsWith('release:')).length, 1);
    });
  });

  group('looping and image details (04A L1, L2)', () {
    test(
      'SetLooping is one host method; state carries looping and image details',
      () async {
        final kit = await connect();
        final session = await kit.createSession(
          const VideoKitSessionConfig(),
        ) as ChannelSession;
        expect(await session.execute(const SetLooping(true)), const Executed());
        expect(api.calls.last, 'setLooping:true');
        platform.sessions.add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 1,
            state: stateMsg(
              looping: true,
              imageDetails: ImageDetailsMsg(frameCount: 20, sampleSize: 2),
            ),
          ),
        );
        await Future<void>.delayed(Duration.zero);
        expect(session.state.value.looping, isTrue);
        expect(
          session.state.value.imageDetails,
          const ImageDetails(frameCount: 20, sampleSize: 2),
        );
        platform.sessions.add(
          SessionUpdateMessage(
            sessionId: session.sessionId,
            seq: 2,
            state: stateMsg(),
          ),
        );
        await Future<void>.delayed(Duration.zero);
        expect(session.state.value.looping, isFalse);
        expect(session.state.value.imageDetails, isNull);
      },
    );
  });

  group('track channels (04A C1)', () {
    test('channelCount is mapped, null stays null', () {
      final six = trackFromMsg(
        TrackInfoMsg(
          id: 'a1',
          codec: 'audio/ac3',
          supported: true,
          channelCount: 6,
        ),
      );
      expect(six.channelCount, 6);
      expect(
        trackFromMsg(TrackInfoMsg(id: 's1', supported: true)).channelCount,
        isNull,
      );
    });
  });

  group('thumbnails and media info (04A P1, P2)', () {
    test(
      'captureThumbnail returns the native JPEG or the stable error',
      () async {
        final kit = await connect();
        final session = await kit.createSession(
          const VideoKitSessionConfig(),
        ) as ChannelSession;
        final captured = await session.captureThumbnail(
          1500000,
          320,
          180,
        ) as ThumbnailCaptured;
        expect(captured.width, 160);
        expect(captured.bytes.first, 0xFF);
        expect(api.calls.last, 'captureThumbnail:1500000:320 x 180');
        final failed =
            await session.captureThumbnail(-1, 320, 180) as ThumbnailFailed;
        expect(failed.error.code, ErrorCode.invalidArgument);
        await session.release();
        expect(
          (await session.captureThumbnail(
            0,
            1,
            1,
          ) as ThumbnailFailed).error.code,
          ErrorCode.sessionReleased,
        );
      },
    );

    test('media info is mapped from the session state', () async {
      final kit = await connect();
      final session = await kit.createSession(
        const VideoKitSessionConfig(),
      ) as ChannelSession;
      platform.sessions.add(
        SessionUpdateMessage(
          sessionId: session.sessionId,
          seq: 1,
          state: stateMsg(
            mediaInfo: MediaInfoMsg(
              container: 'mkv',
              videoCodec: 'video/hevc',
              width: 3840,
              frameRate: 23.976,
            ),
          ),
        ),
      );
      await Future<void>.delayed(Duration.zero);
      final info = session.state.value.mediaInfo!;
      expect(info.container, 'mkv');
      expect(info.width, 3840);
      expect(info.frameRate, closeTo(23.976, 1e-6));
      expect(info.audioCodec, isNull);
    });
  });

  group('add-to-app (14 §9.1)', () {
    test(
      'adopts a host-shared session; unknown ids fail with SESSION_RELEASED',
      () async {
        final kit = await connect();
        await expectLater(
          kit.adoptSession('host-1'),
          throwsA(
            isA<VideoKitException>().having(
              (e) => e.error.code,
              'code',
              ErrorCode.sessionReleased,
            ),
          ),
        );
        api.sharedSessions.add('host-1');
        final session = await kit.adoptSession('host-1');
        expect(session.sessionId, 'host-1');
        expect(identical(await kit.adoptSession('host-1'), session), isTrue);
        expect(api.calls.where((c) => c.startsWith('adoptSession')).length, 3);
      },
    );
  });

  group('host callbacks bridge', () {
    test('native callbacks reach the Dart host with mapped types', () async {
      final host = _Host();
      await connect(VideoKitConfig(hostCallbacks: host));
      final callbacks = platform.callbacks!;
      final decision = await callbacks.onRecoverableError(
        'native-session-1',
        StableErrorMsg(
          code: 'SOURCE_DISCONNECTED',
          stage: 'PLAYBACK',
          retryable: true,
          suggestedAction: 'RECONNECT_SOURCE',
          params: {'retryAfterMs': '500'},
        ),
      );
      expect(decision, 'RETRY');
      expect(
        await callbacks.onNavigationRequested(
          NavigationRequestMsg(sessionId: 's', direction: 'NEXT'),
        ),
        'ACCEPTED',
      );
      expect(host.calls, [
        'recoverable:native-session-1:sourceDisconnected:500',
        'navigation:next',
      ]);
    });
  });

  group('edit project proxy', () {
    test(
      'commands, created ids and sealed export results (04A I5, N12)',
      () async {
        final kit = await connect();
        final project = await kit.createEditProject(EditProjectConfig());
        final token = await project.addSource(
          const VideoKitMediaSource(
            mediaToken: 'tok',
            mediaKind: MediaKind.video,
            sourceRef: DemoSourceRef('normal'),
          ),
        );
        expect(token.sourceId, 'src-1');
        final applied = await project.apply(
          const AcceptTrackingRange('mask-1', 10, 20),
        ) as EditApplied;
        expect(applied.createdId, 'clip-2');
        expect(api.lastEdit!.kind, 'AcceptTrackingRange');
        expect(api.lastEdit!.startUs, 10);
        final result = await project.export(
          const VideoKitExportRequest(presetId: ExportPresets.p720),
          const VideoKitOutputSink(sinkRef: 'demo:memory'),
        );
        final failed = result as ExportFailed;
        expect(failed.error.code, ErrorCode.outputSpaceInsufficient);
        expect(failed.error.params['requiredBytes'], '1000');
        expect(failed.stage, ExportStage.encoding);
        expect(api.calls.last, 'export:P720:demo:memory');
      },
    );
  });

  group('wire names', () {
    test(
      'enum wire names follow the Kotlin UPPER_SNAKE spelling (04A §1.3)',
      () {
        expect(
          wireOf(ErrorCode.unsupportedSnapshotVersion),
          'UNSUPPORTED_SNAPSHOT_VERSION',
        );
        expect(wireOf(SessionVisibility.offscreen), 'OFFSCREEN');
        expect(
          enumOf(
            ErrorCode.values,
            'CODE_FROM_THE_FUTURE',
            ErrorCode.internalErrorRedacted,
          ),
          ErrorCode.internalErrorRedacted,
        );
        expect(exportStageFromWire('WRITING'), ExportStage.writing);
        expect(
          exportStageFromWire('STAGE_FROM_THE_FUTURE'),
          ExportStage.preparing,
        );
        final tracking = editCommandToMsg(
          const StartTracking(
            'mask-1',
            TrackingKind.object,
            seedRegion: MaskRegion(x: 0.1, y: 0.2, width: 0.3, height: 0.4),
            targetId: 'c-1',
          ),
        );
        expect(tracking.trackingKind, 'OBJECT');
        expect(tracking.region!.width, 0.3);
        expect(tracking.targetId, 'c-1');
      },
    );
  });
}

class _NoFactory implements VideoKitSourceFactory {
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
