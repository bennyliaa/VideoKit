import 'package:flutter/services.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'gen/messages.g.dart';
import 'gen/messages.g.dart' as gen show editUpdates, sessionUpdates;

/// Channel protocol version spoken by this package (14 §8.3). A different native major version makes the
/// handshake fail with a clear error instead of continuing.
const int kChannelProtocolVersion = 1;

/// Version of the Dart plugin packages, sent in the handshake.
const String kVideoKitFlutterPackageVersion = '1.0.0-dev.1';

/// Abstraction over the native VideoKit channel (14 §8.1). Tests replace [instance] with a fake.
abstract class VideoKitPlatform extends PlatformInterface {
  /// Creates a platform implementation.
  VideoKitPlatform() : super(token: _token);

  static final Object _token = Object();

  static VideoKitPlatform _instance = PigeonVideoKitPlatform();

  /// The platform in use; defaults to the Pigeon channel.
  static VideoKitPlatform get instance => _instance;

  /// Replaces the platform; implementations must extend [VideoKitPlatform].
  static set instance(VideoKitPlatform instance) {
    PlatformInterface.verifyToken(instance, _token);
    _instance = instance;
  }

  /// Dart → native calls.
  VideoKitHostApi get hostApi;

  /// Session update stream of all sessions (dispatched by session id on the Dart side).
  Stream<SessionUpdateMessage> sessionUpdates();

  /// Edit update stream of all projects.
  Stream<EditUpdateMessage> editUpdates();

  /// Registers (or with `null` removes) the Dart side of the native → Dart host callbacks.
  void setCallbacks(VideoKitCallbacksApi? callbacks);
}

/// [VideoKitPlatform] over the Pigeon generated channels.
class PigeonVideoKitPlatform extends VideoKitPlatform {
  /// Creates the platform on [binaryMessenger] (default: the root isolate's messenger).
  PigeonVideoKitPlatform({BinaryMessenger? binaryMessenger})
    : _messenger = binaryMessenger,
      hostApi = VideoKitHostApi(binaryMessenger: binaryMessenger);

  final BinaryMessenger? _messenger;

  @override
  final VideoKitHostApi hostApi;

  @override
  Stream<SessionUpdateMessage> sessionUpdates() => gen.sessionUpdates();

  @override
  Stream<EditUpdateMessage> editUpdates() => gen.editUpdates();

  @override
  void setCallbacks(VideoKitCallbacksApi? callbacks) {
    VideoKitCallbacksApi.setUp(callbacks, binaryMessenger: _messenger);
  }
}
