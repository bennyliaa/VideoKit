import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/videokit_flutter.dart';
import 'package:videokit_flutter_platform_interface/videokit_embed_protocol.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'embed_channel.dart';

/// Motion duration of the host panel container sync (`anim.normal`, 14 §7.2); 0 with reduced motion.
const Duration _panelAnimation = Duration(milliseconds: 200);

/// Connects a VideoKit for the embed engine; replaceable in tests.
typedef EmbedKitConnector = Future<FlutterVideoKit> Function();

/// Root widget of an embedded engine (14 §9.2): waits for the native side to say what to show, adopts the
/// host-owned session(s) through the plugin channel and shows the VideoKit component. Never releases host
/// sessions: switching content or disposing only stops observing them.
class VideoKitEmbedApp extends StatefulWidget {
  /// Creates the app; [channel] and [connect] are injectable for tests.
  const VideoKitEmbedApp({super.key, this.channel, this.connect});

  /// Embed channel of this engine.
  final EmbedChannel? channel;

  /// Plugin connection.
  final EmbedKitConnector? connect;

  @override
  State<VideoKitEmbedApp> createState() => _VideoKitEmbedAppState();
}

class _VideoKitEmbedAppState extends State<VideoKitEmbedApp> {
  late final EmbedChannel _channel = widget.channel ?? EmbedChannel();
  late final Future<FlutterVideoKit> _kit = (widget.connect ?? () => FlutterVideoKit.connect(const VideoKitConfig()))();

  @override
  void initState() {
    super.initState();
    unawaited(_channel.start().catchError((Object _) {}));
  }

  @override
  void dispose() {
    _channel.stop();
    unawaited(_kit.then((kit) => kit.close()).catchError((Object _) {}));
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => ValueListenableBuilder<EmbedThemeMsg?>(
    valueListenable: _channel.theme,
    builder: (context, theme, _) => MaterialApp(
      debugShowCheckedModeBanner: false,
      localizationsDelegates: videoKitLocalizationsDelegates,
      supportedLocales: videoKitSupportedLocales,
      localeResolutionCallback: videoKitResolveLocale,
      themeMode: _themeMode(theme),
      theme: ThemeData(brightness: Brightness.light),
      darkTheme: ThemeData(brightness: Brightness.dark),
      home: VideoKitThemeScope(
        overrides: _overrides(theme),
        child: ValueListenableBuilder<Map<String, String>>(
          valueListenable: _channel.strings,
          builder: (context, strings, _) => VideoKitStrings(
            overrides: strings,
            child: ColoredBox(
              color: Colors.black,
              child: ValueListenableBuilder<EmbedContentMsg?>(
                valueListenable: _channel.content,
                builder: (context, content, _) => content == null
                    ? const SizedBox.expand()
                    : _EmbedContentView(
                        key: ValueKey(_contentKey(content)),
                        content: content,
                        kit: _kit,
                        channel: _channel,
                      ),
              ),
            ),
          ),
        ),
      ),
    ),
  );

  static String _contentKey(EmbedContentMsg c) => '${c.kind.name}:${c.sessionId}:${c.sessionIds.join(',')}:${c.projectId}';

  static ThemeMode _themeMode(EmbedThemeMsg? theme) => switch (theme?.brightness) {
    'LIGHT' => ThemeMode.light,
    'DARK' => ThemeMode.dark,
    _ => ThemeMode.system,
  };

  static VideoKitThemeOverrides? _overrides(EmbedThemeMsg? theme) {
    if (theme == null || theme.colors.isEmpty) return null;
    // Unknown keys and non-colour categories are ignored and reported by VideoKitThemeData.diagnostics.
    return VideoKitThemeOverrides(values: {for (final e in theme.colors.entries) e.key: Color(e.value)});
  }
}

/// One content of the embed: adopts its sessions, shows the component, reports the first frame.
class _EmbedContentView extends StatefulWidget {
  const _EmbedContentView({super.key, required this.content, required this.kit, required this.channel});

  final EmbedContentMsg content;
  final Future<FlutterVideoKit> kit;
  final EmbedChannel channel;

  @override
  State<_EmbedContentView> createState() => _EmbedContentViewState();
}

class _EmbedContentViewState extends State<_EmbedContentView> {
  late final Future<List<VideoKitSession>> _sessions = _adopt();
  bool _displayedReported = false;

  Future<List<VideoKitSession>> _adopt() async {
    final kit = await widget.kit;
    final c = widget.content;
    final ids = switch (c.kind) {
      EmbedSurfaceKind.player || EmbedSurfaceKind.imageViewer => [?c.sessionId],
      EmbedSurfaceKind.multiView => c.sessionIds,
      EmbedSurfaceKind.editor => const <String>[],
    };
    return [for (final id in ids) await kit.adoptSession(id)];
  }

  @override
  void dispose() {
    // Adopted host sessions: release() only stops observing them (the host owns them).
    unawaited(_sessions.then((list) => Future.wait(list.map((s) => s.release()))).catchError((Object _) => const <VideoKitPlaybackState>[]));
    super.dispose();
  }

  void _reportDisplayed() {
    if (_displayedReported) return;
    _displayedReported = true;
    WidgetsBinding.instance.addPostFrameCallback((_) => widget.channel.contentDisplayed(widget.content.kind));
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<List<VideoKitSession>>(
    future: _sessions,
    builder: (context, snapshot) {
      final sessions = snapshot.data;
      if (sessions == null) return const SizedBox.expand();
      _reportDisplayed();
      return switch (widget.content.kind) {
        EmbedSurfaceKind.player => _player(context, sessions.single),
        EmbedSurfaceKind.multiView => _grid(sessions),
        EmbedSurfaceKind.imageViewer => _imageViewer(context, sessions.single),
        // Protocol 1 does not share native edit projects; the editor embed stays a skeleton (M0-B3-B §4).
        EmbedSurfaceKind.editor => const SizedBox.expand(),
      };
    },
  );

  Widget _player(BuildContext context, VideoKitSession session) {
    final options = widget.content.playerOptions;
    final reduceMotion = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return VideoKitPlayer(
      session: session,
      options: VideoKitPlayerOptions(
        autoHideDelay: Duration(milliseconds: options?.autoHideControlsMs ?? 3000),
      ),
      onControlsVisibilityChanged: (visible) =>
          widget.channel.controlsVisibilityChanged(visible, reduceMotion ? Duration.zero : _panelAnimation),
      onFullscreenRequested: (options?.allowFullscreen ?? true) ? widget.channel.fullscreenRequested : null,
      onEditRequested: (_) => widget.channel.editRequested(session.sessionId),
    );
  }

  Widget _imageViewer(BuildContext context, VideoKitSession session) {
    final reduceMotion = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return VideoKitImageViewer(
      session: session,
      onControlsVisibilityChanged: (visible) =>
          widget.channel.controlsVisibilityChanged(visible, reduceMotion ? Duration.zero : _panelAnimation),
    );
  }

  // Single-engine multi-view (UI-05), the one-engine side of the 14 §9.3 memory comparison.
  Widget _grid(List<VideoKitSession> sessions) => VideoKitSlotGrid(
    slots: [for (var i = 0; i < sessions.length; i++) VideoKitSlot(session: sessions[i], index: i)],
  );
}
