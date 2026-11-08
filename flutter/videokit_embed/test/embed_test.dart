import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_embed/main.dart';
import 'package:videokit_flutter/videokit_flutter.dart';
import 'package:videokit_flutter_platform_interface/videokit_embed_protocol.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

/// Simulated native side of the embed channel.
class _FakeEmbedHost implements VideoKitEmbedHostApi {
  _FakeEmbedHost(this.start);

  final EmbedStartMsg start;
  final List<String> calls = [];

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<EmbedStartMsg> attach(int dartProtocolVersion) async {
    calls.add('attach:$dartProtocolVersion');
    return start;
  }

  @override
  Future<void> onControlsVisibilityChanged(
    bool visible,
    int animationMs,
  ) async => calls.add('controls:$visible:$animationMs');

  @override
  Future<void> requestNavigation(int requestId, String direction) async =>
      calls.add('nav:$requestId:$direction');

  @override
  Future<void> onFullscreenRequested(bool fullscreen) async =>
      calls.add('fullscreen:$fullscreen');

  @override
  Future<void> onEditRequested(String sessionId) async =>
      calls.add('edit:$sessionId');

  @override
  Future<void> onContentDisplayed(EmbedSurfaceKind kind) async =>
      calls.add('displayed:${kind.name}');
}

/// Minimal plugin platform: handshake and adoption; every other call is recorded and answered with a neutral
/// value of its return type (the widgets attach textures, report visibility, send commands).
class _FakeHostApi implements VideoKitHostApi {
  final List<String> calls = [];

  @override
  dynamic noSuchMethod(Invocation invocation) {
    // Symbol("setActiveAudio") -> setActiveAudio
    final symbol = invocation.memberName.toString();
    final name = symbol.substring('Symbol("'.length, symbol.length - 2);
    final args = invocation.positionalArguments.skip(1).join(':');
    calls.add(args.isEmpty ? name : '$name:$args');
    return switch (name) {
      'createTexture' => Future<int>.value(1),
      'requestNavigation' => Future<String>.value('UNAVAILABLE'),
      'release' || 'captureState' => Future<PlaybackStateMsg?>.value(),
      'setControlsVisible' ||
      'updateHostActions' ||
      'resizeTexture' ||
      'disposeTexture' => Future<void>.value(),
      'captureThumbnail' => Future<ThumbnailResultMsg>.value(
        ThumbnailResultMsg(
          error: StableErrorMsg(
            code: 'INVALID_STATE',
            stage: 'PLAYBACK',
            retryable: false,
            suggestedAction: 'NONE',
            params: {},
          ),
        ),
      ),
      _ => Future<CommandResultMsg>.value(
        CommandResultMsg(kind: CommandResultKind.executed),
      ),
    };
  }

  @override
  Future<HandshakeResponse> handshake(HandshakeRequest request) async =>
      HandshakeResponse(
        protocolVersion: kChannelProtocolVersion,
        nativeKitVersion: 'test',
        apiVersion: '1.0.0',
        demoBackend: true,
      );

  @override
  Future<CreateResultMsg> adoptSession(String sessionId) async {
    calls.add('adopt:$sessionId');
    return CreateResultMsg(id: sessionId);
  }

  @override
  Future<void> closeAll() async => calls.add('closeAll');
}

class _FakePlatform extends VideoKitPlatform {
  _FakePlatform(this.api);

  final _FakeHostApi api;

  @override
  VideoKitHostApi get hostApi => api;

  // ignore: close_sinks, closed with the test isolate
  final StreamController<SessionUpdateMessage> sessions =
      StreamController.broadcast();

  @override
  Stream<SessionUpdateMessage> sessionUpdates() => sessions.stream;

  @override
  Stream<EditUpdateMessage> editUpdates() => const Stream.empty();

  @override
  void setCallbacks(VideoKitCallbacksApi? callbacks) {}
}

/// A bound video session as the host reports it (04A A1: silent until granted).
SessionStateMsg _ready({bool activeAudio = false}) => SessionStateMsg(
  phase: SessionPhaseMsg.ready,
  mediaKind: MediaKindMsg.video,
  positionUs: 0,
  durationUs: 120000000,
  playWhenReady: false,
  speed: 1,
  volume: 1,
  muted: false,
  audioTracks: [],
  subtitleTracks: [],
  transform: TransformMsg(
    scale: 1,
    panX: 0,
    panY: 0,
    rotationDeg: 0,
    fitMode: 'FIT',
  ),
  orientation: OrientationStateMsg(
    request: 'AUTO',
    contentOrientation: 'LANDSCAPE',
    fullscreen: false,
  ),
  visibility: 'VISIBLE',
  activeAudio: activeAudio,
  controlsVisible: true,
  resourcesHeld: true,
  hostActions: [],
  videoWidth: 1920,
  videoHeight: 1080,
  hiddenForLock: false,
  looping: false,
);

/// Pumps a few frames: the player shows an endless loading indicator, so `pumpAndSettle` never settles.
Future<void> _settle(WidgetTester tester) async {
  for (var i = 0; i < 10; i++) {
    await tester.pump(const Duration(milliseconds: 50));
  }
}

EmbedStartMsg _start({EmbedContentMsg? content}) => EmbedStartMsg(
  protocolVersion: 1,
  content: content,
  theme: EmbedThemeMsg(
    brightness: 'DARK',
    colors: {'color.primary': 0xFF2563EB},
  ),
  strings: {'player.play': '开始'},
);

void main() {
  group('EmbedChannel (14 §9.2)', () {
    test(
      'attach pulls content, theme and strings; pushes replace them',
      () async {
        final host = _FakeEmbedHost(
          _start(
            content: EmbedContentMsg(
              kind: EmbedSurfaceKind.player,
              sessionId: 's-1',
              sessionIds: [],
            ),
          ),
        );
        VideoKitEmbedFlutterApi? registered;
        final channel = EmbedChannel(
          hostApi: host,
          registerFlutterApi: (api) => registered = api,
        );
        await channel.start();
        expect(registered, same(channel));
        expect(host.calls, ['attach:$kEmbedProtocolVersion']);
        expect(channel.nativeProtocolVersion, 1);
        expect(channel.content.value?.sessionId, 's-1');
        expect(channel.theme.value?.brightness, 'DARK');
        expect(channel.strings.value['player.play'], '开始');

        channel.showContent(
          EmbedContentMsg(
            kind: EmbedSurfaceKind.multiView,
            sessionIds: ['a', 'b'],
          ),
        );
        expect(channel.content.value?.sessionIds, ['a', 'b']);
        channel.setStrings({});
        expect(channel.strings.value, isEmpty);
        channel.stop();
        expect(registered, isNull);
      },
    );

    test('navigation is a request id plus an answer; unknown answers map to failed', () async {
      final host = _FakeEmbedHost(_start());
      final channel = EmbedChannel(hostApi: host, registerFlutterApi: (_) {});
      final first = channel.requestNavigation(NavigationDirection.next);
      final second = channel.requestNavigation(NavigationDirection.previous);
      await Future<void>.delayed(Duration.zero);
      expect(host.calls, ['nav:1:NEXT', 'nav:2:PREVIOUS']);
      channel.navigationResult(2, 'ACCEPTED');
      channel.navigationResult(1, 'RESULT_FROM_THE_FUTURE');
      expect(await second, NavigationResult.accepted);
      expect(await first, NavigationResult.failed);
      // Pending requests answer unavailable when the channel stops.
      final pending = channel.requestNavigation(NavigationDirection.next);
      await Future<void>.delayed(Duration.zero);
      channel.stop();
      expect(await pending, NavigationResult.unavailable);
    });

    test('UI requests reach the native host', () {
      final host = _FakeEmbedHost(_start());
      final channel = EmbedChannel(hostApi: host, registerFlutterApi: (_) {})
        ..controlsVisibilityChanged(false, const Duration(milliseconds: 200))
        ..fullscreenRequested(true)
        ..editRequested('s-9')
        ..contentDisplayed(EmbedSurfaceKind.editor);
      expect(channel.content.value, isNull);
      expect(host.calls, [
        'controls:false:200',
        'fullscreen:true',
        'edit:s-9',
        'displayed:editor',
      ]);
    });
  });

  group('VideoKitEmbedApp', () {
    testWidgets(
      'waits for content, adopts nothing for the editor skeleton, reports the first frame',
      (tester) async {
        final host = _FakeEmbedHost(
          _start(
            content: EmbedContentMsg(
              kind: EmbedSurfaceKind.editor,
              sessionIds: [],
              projectId: 'p-1',
            ),
          ),
        );
        final plugin = _FakeHostApi();
        final channel = EmbedChannel(hostApi: host, registerFlutterApi: (_) {});
        await tester.pumpWidget(
          VideoKitEmbedApp(
            channel: channel,
            connect: () => FlutterVideoKit.connect(
              const VideoKitConfig(),
              platform: _FakePlatform(plugin),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(host.calls, contains('displayed:editor'));
        expect(plugin.calls.where((c) => c.startsWith('adopt')), isEmpty);
        await tester.pumpWidget(const SizedBox());
        await tester.pumpAndSettle();
        expect(plugin.calls, contains('closeAll'));
      },
    );

    Future<_FakePlatform> pumpEmbed(
      WidgetTester tester,
      EmbedContentMsg content,
    ) async {
      final platform = _FakePlatform(_FakeHostApi());
      final channel = EmbedChannel(
        hostApi: _FakeEmbedHost(_start(content: content)),
        registerFlutterApi: (_) {},
      );
      await tester.pumpWidget(
        VideoKitEmbedApp(
          channel: channel,
          connect: () => FlutterVideoKit.connect(
            const VideoKitConfig(),
            platform: platform,
          ),
        ),
      );
      await _settle(tester);
      return platform;
    }

    testWidgets(
      '04A A1: a single embedded player grants itself the audio once the adopted session is bound',
      (tester) async {
        final platform = await pumpEmbed(
          tester,
          EmbedContentMsg(
            kind: EmbedSurfaceKind.player,
            sessionId: 's-1',
            sessionIds: [],
          ),
        );
        final calls = platform.api.calls;
        expect(calls, contains('adopt:s-1'));
        platform.sessions.add(
          SessionUpdateMessage(sessionId: 's-1', seq: 1, state: _ready()),
        );
        await _settle(tester);
        final grants = calls.where((c) => c.startsWith('setActiveAudio:true'));
        expect(grants, hasLength(1), reason: '$calls');
        // Already audible (the host granted it): no second grant.
        platform.sessions.add(
          SessionUpdateMessage(
            sessionId: 's-1',
            seq: 2,
            state: _ready(activeAudio: true),
          ),
        );
        await _settle(tester);
        expect(
          calls.where((c) => c.startsWith('setActiveAudio:true')),
          hasLength(1),
        );
        await tester.pumpWidget(const SizedBox());
        await _settle(tester);
      },
    );

    testWidgets(
      '04A A1: a multi-view keeps every slot silent until the user picks the audio source',
      (tester) async {
        final platform = await pumpEmbed(
          tester,
          EmbedContentMsg(
            kind: EmbedSurfaceKind.multiView,
            sessionIds: ['a', 'b'],
          ),
        );
        for (final (i, id) in ['a', 'b'].indexed) {
          platform.sessions.add(
            SessionUpdateMessage(sessionId: id, seq: i + 1, state: _ready()),
          );
        }
        await _settle(tester);
        final calls = platform.api.calls;
        expect(calls, containsAll(['adopt:a', 'adopt:b']));
        expect(
          calls.where((c) => c.startsWith('setActiveAudio')),
          isEmpty,
          reason: 'multi-view sessions are never self-granted',
        );
        await tester.pumpWidget(const SizedBox());
        await _settle(tester);
      },
    );
  });
}
