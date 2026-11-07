import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter_platform_interface/videokit_embed_protocol.dart';

/// Embed protocol version of the Dart side (embed_messages.dart).
const int kEmbedProtocolVersion = 1;

/// Dart side of the embed channel of this engine (14 §9.2): pulls the native configuration with `attach`, then
/// follows `show*` / `setTheme` / `setStrings` pushes, and forwards UI-level requests to the native host.
class EmbedChannel implements VideoKitEmbedFlutterApi {
  /// Creates the channel; [hostApi] and [registerFlutterApi] are injectable for tests.
  EmbedChannel({
    VideoKitEmbedHostApi? hostApi,
    void Function(VideoKitEmbedFlutterApi? api)? registerFlutterApi,
  }) : _hostApi = hostApi ?? VideoKitEmbedHostApi(),
       _register = registerFlutterApi ?? VideoKitEmbedFlutterApi.setUp;

  final VideoKitEmbedHostApi _hostApi;
  final void Function(VideoKitEmbedFlutterApi? api) _register;
  final Map<int, Completer<NavigationResult>> _navigation = {};
  int _nextRequestId = 0;

  /// What to show; `null` until the native side says.
  final ValueNotifier<EmbedContentMsg?> content = ValueNotifier(null);

  /// Theme overrides from the native host.
  final ValueNotifier<EmbedThemeMsg?> theme = ValueNotifier(null);

  /// String overrides from the native host (ARB keys).
  final ValueNotifier<Map<String, String>> strings = ValueNotifier(const {});

  /// Native protocol version from `attach`, or `null` before it answered.
  int? nativeProtocolVersion;

  /// Registers the push handlers and pulls the current configuration.
  Future<void> start() async {
    _register(this);
    final start = await _hostApi.attach(kEmbedProtocolVersion);
    nativeProtocolVersion = start.protocolVersion;
    theme.value = start.theme;
    strings.value = Map.unmodifiable(start.strings);
    content.value = start.content;
  }

  /// Stops receiving pushes; pending navigation requests answer [NavigationResult.unavailable].
  void stop() {
    _register(null);
    for (final pending in _navigation.values) {
      if (!pending.isCompleted) pending.complete(NavigationResult.unavailable);
    }
    _navigation.clear();
  }

  // ---------------------------------------------------------------- Dart → native

  /// Controls shown / hidden, with the panel animation duration (host panel container sync).
  void controlsVisibilityChanged(bool visible, Duration animation) => unawaited(
    _hostApi
        .onControlsVisibilityChanged(visible, animation.inMilliseconds)
        .catchError((Object _) {}),
  );

  /// Fullscreen requested by the UI.
  void fullscreenRequested(bool fullscreen) => unawaited(
    _hostApi.onFullscreenRequested(fullscreen).catchError((Object _) {}),
  );

  /// Editor requested for [sessionId].
  void editRequested(String sessionId) =>
      unawaited(_hostApi.onEditRequested(sessionId).catchError((Object _) {}));

  /// First frame of [kind] (14 §9.3 metric).
  void contentDisplayed(EmbedSurfaceKind kind) =>
      unawaited(_hostApi.onContentDisplayed(kind).catchError((Object _) {}));

  /// Asks the native host for previous / next media; unknown or failed answers map to [NavigationResult.failed].
  Future<NavigationResult> requestNavigation(
    NavigationDirection direction,
  ) async {
    final id = ++_nextRequestId;
    final completer = Completer<NavigationResult>();
    _navigation[id] = completer;
    try {
      await _hostApi.requestNavigation(id, direction.wireName);
    } on Object {
      _navigation.remove(id);
      return NavigationResult.failed;
    }
    return completer.future;
  }

  // ---------------------------------------------------------------- native → Dart

  @override
  void showContent(EmbedContentMsg content) => this.content.value = content;

  @override
  void setTheme(EmbedThemeMsg? theme) => this.theme.value = theme;

  @override
  void setStrings(Map<String, String> strings) =>
      this.strings.value = Map.unmodifiable(strings);

  @override
  void navigationResult(int requestId, String result) => _navigation
      .remove(requestId)
      ?.complete(NavigationResult.fromName(result));
}
