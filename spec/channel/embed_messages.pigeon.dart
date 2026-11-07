// Pigeon definition of the add-to-app embed channel (14 §9.2): one channel per embedded Flutter engine
// between `videokit-ui-android` (native) and the embed entry point `videokitEmbedMain` (Dart).
//
// Regenerate (from flutter/videokit_flutter_platform_interface):
//   dart run pigeon --input pigeons/embed_messages.dart
// Generated files are committed (13 §2.1): lib/src/gen/embed_messages.g.dart and
// ../../kit/android/videokit-ui-android/src/main/kotlin/com/videokit/ui/android/gen/EmbedMessages.g.kt.
//
// The media itself does not travel here: the embedded UI reaches the host-owned session through the plugin
// channel (`adoptSession`, videokit_messages.dart). This channel only says what to show and carries UI-level
// requests back to the native host. Enum-like values travel as UPPER_SNAKE wire names (04A §1.3).
// ignore_for_file: one_member_abstracts

import 'package:pigeon/pigeon.dart';

@ConfigurePigeon(
  PigeonOptions(
    dartOut: 'lib/src/gen/embed_messages.g.dart',
    dartPackageName: 'videokit_flutter_platform_interface',
    kotlinOut: '../../kit/android/videokit-ui-android/src/main/kotlin/com/videokit/ui/android/gen/EmbedMessages.g.kt',
    kotlinOptions: KotlinOptions(package: 'com.videokit.ui.android.gen'),
    copyrightHeader: 'pigeons/copyright_header.txt',
  ),
)
/// What the embedded engine shows.
enum EmbedSurfaceKind { player, imageViewer, editor, multiView }

/// Player embed options (`PlayerEmbedOptions` on the native side).
class PlayerEmbedOptionsMsg {
  PlayerEmbedOptionsMsg({
    required this.autoHideControlsMs,
    required this.allowFullscreen,
    required this.showNavigation,
    required this.startFullscreen,
  });

  int autoHideControlsMs;
  bool allowFullscreen;
  bool showNavigation;
  bool startFullscreen;
}

/// Content of one embedded engine; replaced as a whole by `show*` calls.
class EmbedContentMsg {
  EmbedContentMsg({required this.kind, this.sessionId, required this.sessionIds, this.projectId, this.playerOptions});

  EmbedSurfaceKind kind;

  /// Host-owned session (player, image viewer); adopted through the plugin channel.
  String? sessionId;

  /// Host-owned sessions of a multi-view grid (one engine, `VideoKitSlotGrid`; 14 §9.3 multi-instance comparison).
  List<String> sessionIds;

  /// Edit project (editor).
  String? projectId;
  PlayerEmbedOptionsMsg? playerOptions;
}

/// Token overrides from the native host (14 §9.1 `VideoKitThemeOverrides`): colors as ARGB ints keyed by the
/// Dart token key (`VkTokenKeys`), `brightness` LIGHT / DARK / null (follow the system).
class EmbedThemeMsg {
  EmbedThemeMsg({this.brightness, required this.colors});

  String? brightness;
  Map<String, int> colors;
}

/// Everything the Dart side needs when it starts (it may start before or after the native side configured it).
class EmbedStartMsg {
  EmbedStartMsg({required this.protocolVersion, this.content, this.theme, required this.strings});

  /// Embed protocol version of the native side (1).
  int protocolVersion;
  EmbedContentMsg? content;
  EmbedThemeMsg? theme;

  /// String overrides, keys as in the ARB file (14 §9.1).
  Map<String, String> strings;
}

/// Dart → native.
@HostApi()
abstract class VideoKitEmbedHostApi {
  /// First call of the embed entry point; returns the current configuration.
  EmbedStartMsg attach(int dartProtocolVersion);

  /// Controls became visible or hidden; the native bridge animates the host panel container with the
  /// theme's motion duration (14 §9.2).
  void onControlsVisibilityChanged(bool visible, int animationMs);

  /// The UI asks for previous / next media. Not `@async` (generated async handlers need the Android main
  /// dispatcher library): the answer comes back as `VideoKitEmbedFlutterApi.navigationResult(requestId, …)`.
  void requestNavigation(int requestId, String direction);

  /// The UI asks to enter or leave fullscreen; the host decides (orientation, system bars).
  void onFullscreenRequested(bool fullscreen);

  /// The UI asks to open the editor for the session's media.
  void onEditRequested(String sessionId);

  /// First Flutter frame of the current content (14 §9.3 first-frame metric).
  void onContentDisplayed(EmbedSurfaceKind kind);
}

/// Native → Dart.
@FlutterApi()
abstract class VideoKitEmbedFlutterApi {
  void showContent(EmbedContentMsg content);

  void setTheme(EmbedThemeMsg? theme);

  void setStrings(Map<String, String> strings);

  /// Answer to [VideoKitEmbedHostApi.requestNavigation]: a `NavigationResult` wire name.
  void navigationResult(int requestId, String result);
}
