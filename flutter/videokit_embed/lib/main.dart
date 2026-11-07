/// VideoKit add-to-app Flutter module (14 §9.2).
///
/// Native hosts never call Dart directly: `videokit-ui-android` runs [videokitEmbedMain] in each embed engine and
/// talks to it over the embed channel; media goes through the VideoKit plugin channel.
library;

import 'package:flutter/widgets.dart';

import 'src/embed_app.dart';

export 'src/embed_app.dart' show EmbedKitConnector, VideoKitEmbedApp;
export 'src/embed_channel.dart' show EmbedChannel, kEmbedProtocolVersion;

/// Default entry point, so `flutter run` on the module starts the same UI.
void main() => videokitEmbedMain(const []);

/// Entry point of every embed engine (`VideoKitFlutterConfig.dartEntrypoint`).
@pragma('vm:entry-point')
void videokitEmbedMain(List<String> args) => runApp(const VideoKitEmbedApp());
