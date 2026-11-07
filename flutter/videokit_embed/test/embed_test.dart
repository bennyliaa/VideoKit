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
  Future<void> onControlsVisibilityChanged(bool visible, int animationMs) async =>
      calls.add('controls:$visible:$animationMs');

  @override
  Future<void> requestNavigation(int requestId, String direction) async => calls.add('nav:$requestId:$direction');

  @override
  Future<void> onFullscreenRequested(bool fullscreen) async => calls.add('fullscreen:$fullscreen');

  @override
  Future<void> onEditRequested(String sessionId) async => calls.add('edit:$sessionId');

  @override
  Future<void> onContentDisplayed(EmbedSurfaceKind kind) async => calls.add('displayed:${kind.name}');
}

/// Minimal plugin platform: handshake and adoption only.
class _FakeHostApi implements VideoKitHostApi {
  final List<String> calls = [];

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);

  @override
  Future<HandshakeResponse> handshake(HandshakeRequest request) async =>
      HandshakeResponse(protocolVersion: kChannelProtocolVersion, nativeKitVersion: 'test', apiVersion: '1.0.0', demoBackend: true);

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

  @override
  Stream<SessionUpdateMessage> sessionUpdates() => const Stream.empty();

  @override
  Stream<EditUpdateMessage> editUpdates() => const Stream.empty();

  @override
  void setCallbacks(VideoKitCallbacksApi? callbacks) {}
}

EmbedStartMsg _start({EmbedContentMsg? content}) => EmbedStartMsg(
  protocolVersion: 1,
  content: content,
  theme: EmbedThemeMsg(brightness: 'DARK', colors: {'color.primary': 0xFF2563EB}),
  strings: {'player.play': '开始'},
);

void main() {
  group('EmbedChannel (14 §9.2)', () {
    test('attach pulls content, theme and strings; pushes replace them', () async {
      final host = _FakeEmbedHost(_start(content: EmbedContentMsg(kind: EmbedSurfaceKind.player, sessionId: 's-1', sessionIds: [])));
      VideoKitEmbedFlutterApi? registered;
      final channel = EmbedChannel(hostApi: host, registerFlutterApi: (api) => registered = api);
      await channel.start();
      expect(registered, same(channel));
      expect(host.calls, ['attach:$kEmbedProtocolVersion']);
      expect(channel.nativeProtocolVersion, 1);
      expect(channel.content.value?.sessionId, 's-1');
      expect(channel.theme.value?.brightness, 'DARK');
      expect(channel.strings.value['player.play'], '开始');

      channel.showContent(EmbedContentMsg(kind: EmbedSurfaceKind.multiView, sessionIds: ['a', 'b']));
      expect(channel.content.value?.sessionIds, ['a', 'b']);
      channel.setStrings({});
      expect(channel.strings.value, isEmpty);
      channel.stop();
      expect(registered, isNull);
    });

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
      expect(host.calls, ['controls:false:200', 'fullscreen:true', 'edit:s-9', 'displayed:editor']);
    });
  });

  group('VideoKitEmbedApp', () {
    testWidgets('waits for content, adopts nothing for the editor skeleton, reports the first frame', (tester) async {
      final host = _FakeEmbedHost(_start(content: EmbedContentMsg(kind: EmbedSurfaceKind.editor, sessionIds: [], projectId: 'p-1')));
      final plugin = _FakeHostApi();
      final channel = EmbedChannel(hostApi: host, registerFlutterApi: (_) {});
      await tester.pumpWidget(
        VideoKitEmbedApp(
          channel: channel,
          connect: () => FlutterVideoKit.connect(const VideoKitConfig(), platform: _FakePlatform(plugin)),
        ),
      );
      await tester.pumpAndSettle();
      expect(host.calls, contains('displayed:editor'));
      expect(plugin.calls.where((c) => c.startsWith('adopt')), isEmpty);
      await tester.pumpWidget(const SizedBox());
      await tester.pumpAndSettle();
      expect(plugin.calls, contains('closeAll'));
    });
  });
}
