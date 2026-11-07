import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/demo/demo_host.dart';
import 'package:videokit_example/l10n/gen/example_localizations.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// Phone portrait (compact) and tablet landscape (expanded) test sizes.
const Size compactSize = Size(360, 780);

/// Expanded landscape size.
const Size expandedSize = Size(1280, 800);

/// Session proxy recording every command the UI sends.
class RecordingSession implements VideoKitSession {
  /// Wraps [inner].
  RecordingSession(this.inner);

  /// Wrapped Fake session.
  final VideoKitSession inner;

  /// Commands in order.
  final List<VideoKitCommand> commands = [];

  /// Host action requests in order.
  final List<String> hostActionRequests = [];

  /// `setControlsVisible` calls in order.
  final List<bool> controlsVisible = [];

  /// Committed (non-preview) seeks.
  Iterable<SeekTo> get committedSeeks =>
      commands.whereType<SeekTo>().where((c) => c.mode != SeekMode.preview);

  @override
  String get sessionId => inner.sessionId;
  @override
  ValueListenable<VideoKitSessionState> get state => inner.state;
  @override
  Stream<VideoKitEvent> get events => inner.events;
  @override
  ValueListenable<int?> get textureId => inner.textureId;
  @override
  VideoKitTextureLease acquireTexture() => inner.acquireTexture();
  @override
  ValueListenable<VideoSize?> get videoSize => inner.videoSize;
  @override
  bool get isDemo => inner.isDemo;
  @override
  Future<VideoKitCommandResult> bind(
    VideoKitMediaSource source, {
    VideoKitPlaybackState? initialState,
    List<VideoKitHostAction> hostActions = const [],
  }) =>
      inner.bind(source, initialState: initialState, hostActions: hostActions);
  @override
  Future<VideoKitCommandResult> execute(VideoKitCommand command) {
    commands.add(command);
    return inner.execute(command);
  }

  @override
  Future<void> updateHostActions(List<VideoKitHostAction> actions) =>
      inner.updateHostActions(actions);
  @override
  Future<VideoKitCommandResult> requestHostAction(String actionId) {
    hostActionRequests.add(actionId);
    return inner.requestHostAction(actionId);
  }

  @override
  Future<NavigationResult> requestNavigation(NavigationDirection direction) =>
      inner.requestNavigation(direction);
  @override
  void setControlsVisible(bool visible) {
    controlsVisible.add(visible);
    inner.setControlsVisible(visible);
  }

  @override
  Future<VideoKitPlaybackState> captureState() => inner.captureState();
  @override
  Future<ThumbnailResult> captureThumbnail(int atUs, int w, int h) {
    thumbnailRequests.add(atUs);
    return inner.captureThumbnail(atUs, w, h);
  }

  /// Positions of `captureThumbnail` calls.
  final List<int> thumbnailRequests = [];
  @override
  Future<VideoKitPlaybackState> release() => inner.release();
  @override
  Future<void> close() => inner.close();
}

/// A Fake with demo host callbacks and a bound, recorded session.
class PlayerRig {
  PlayerRig._(this.kit, this.session);

  /// Fake (manual clock).
  final FakeVideoKit kit;

  /// Recorded session.
  final RecordingSession session;

  /// Fake clock.
  FakeClock get clock => kit.clock;

  /// Creates a rig and starts binding [scenarioId]; opening completes on
  /// the Fake clock ([advance]).
  static Future<PlayerRig> create(String scenarioId) async {
    final callbacks = DemoHostCallbacks();
    final kit = FakeVideoKit(config: VideoKitConfig(hostCallbacks: callbacks));
    callbacks.clock = kit.clock;
    final s = RecordingSession(
      await kit.createSession(const VideoKitSessionConfig()),
    );
    unawaited(
      s.bind(
        VideoKitMediaSource(
          mediaToken: 'test-$scenarioId',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef(scenarioId),
        ),
        hostActions: DemoHostActions.initial(),
      ),
    );
    return PlayerRig._(kit, s);
  }

  /// Advances the Fake clock and pumps a frame.
  /// (The clock awaits zero timers, which only run when the test pumps.)
  Future<void> advance(WidgetTester tester, Duration d) async {
    var done = false;
    unawaited(clock.advance(d).whenComplete(() => done = true));
    while (!done) {
      await tester.pump(Duration.zero);
    }
    await tester.pump();
  }

  /// Disposes the Fake.
  void dispose() {
    unawaited(session.close());
    unawaited(kit.close());
    kit.clock.dispose();
  }
}

/// Test app: example + VideoKit localizations, theme scope, text scale.
Widget testApp(
  Widget home, {
  Locale locale = const Locale('zh'),
  double textScale = 1.0,
  VideoKitThemeMode mode = VideoKitThemeMode.dark,
  String? fontFamily,
}) => MaterialApp(
  locale: locale,
  debugShowCheckedModeBanner: false,
  localizationsDelegates: [
    ExampleLocalizations.delegate,
    ...videoKitLocalizationsDelegates,
  ],
  supportedLocales: videoKitSupportedLocales,
  localeResolutionCallback: videoKitResolveLocale,
  theme: ThemeData(brightness: Brightness.dark, fontFamily: fontFamily),
  builder: (context, child) => MediaQuery(
    data: MediaQuery.of(context)
        .copyWith(textScaler: TextScaler.linear(textScale)),
    child: VideoKitThemeScope(mode: mode, child: child!),
  ),
  home: home,
);

/// The player as the example wires it.
Widget demoPlayer(
  VideoKitSession session, {
  GlobalKey<VideoKitPlayerState>? key,
  ValueChanged<bool>? onControlsVisibilityChanged,
  ValueChanged<StateAction>? onStateAction,
}) => Builder(
  builder: (context) => Scaffold(
    body: VideoKitPlayer(
      key: key,
      session: session,
      title: '演示视频',
      pictureBuilder: (context, s) => DemoSessionPicture(session: s),
      resolveHostString: (k) => DemoHostActions.resolve(context, k),
      onControlsVisibilityChanged: onControlsVisibilityChanged,
      onStateAction: onStateAction,
      onEditRequested: (_) {},
      onBack: () {},
    ),
  ),
);

/// Sets the test view to [size] at DPR 1.
void setViewSize(WidgetTester tester, Size size) {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  addTearDown(tester.view.reset);
}
