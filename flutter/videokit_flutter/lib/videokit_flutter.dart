/// VideoKit Flutter plugin: `videokit_api` over the native Kit (14 §8.5).
///
/// ```dart
/// final kit = await FlutterVideoKit.connect(VideoKitConfig(hostCallbacks: myCallbacks));
/// final session = await kit.createSession(const VideoKitSessionConfig());
/// ```
library;

export 'src/channel_edit_project.dart' show ChannelEditProject;
export 'src/channel_session.dart' show ChannelSession;
export 'src/flutter_videokit.dart'
    show FlutterVideoKit, VideoKitInitException, VideoKitInitFailure;
export 'src/licenses.dart' show kVideoKitNoticeAsset, registerVideoKitLicenses;
