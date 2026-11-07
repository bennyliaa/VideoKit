import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/videokit_flutter.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/history_entry.dart';
import '../picker/channel_media_picker.dart';
import '../picker/media_picker.dart';
import 'app_backend.dart';

/// Release backend (04A P3): the `videokit_flutter` plugin over the native
/// Kit, with the system document picker (`ChannelMediaPicker`, native side
/// M2). Never imports `videokit_fake`.
class PluginBackend implements AppBackend {
  PluginBackend._(this._kit, this._picker);

  final FlutterVideoKit _kit;
  final ChannelMediaPicker _picker;

  /// Connects to the native Kit; throws `VideoKitInitException` when the
  /// channel or backend is unavailable.
  static Future<PluginBackend> connect([
    VideoKitConfig config = const VideoKitConfig(),
  ]) async => PluginBackend._(
    await FlutterVideoKit.connect(config),
    const ChannelMediaPicker(),
  );

  @override
  bool get isDemo => _kit.isDemo;

  @override
  MediaPickerService get picker => _picker;

  @override
  VideoKit get videoKit => _kit;

  @override
  VideoKitMediaSource sourceFor(HistoryEntry entry) => VideoKitMediaSource(
    mediaToken: entry.uri,
    mediaKind: entry.kind,
    displayName: entry.displayName,
    sourceRef: UriSourceRef(entry.uri),
    mimeType: entry.mimeType,
  );

  @override
  VideoKitPictureBuilder? get pictureBuilder => null;

  @override
  Widget thumbnail(BuildContext context, HistoryEntry entry) {
    final t = VkTheme.of(context);
    return ColoredBox(
      color: t.colors.surfaceVariant,
      child: Center(
        child: Icon(
          t.icons.resolve(entry.isImage ? 'fit' : 'movie'),
          color: t.colors.textSecondary,
        ),
      ),
    );
  }

  @override
  VideoKitOutputSink get exportSink =>
      // M2: ACTION_CREATE_DOCUMENT "另存为" registers the real sink.
      const VideoKitOutputSink(sinkRef: 'registered:app-export');

  @override
  Future<List<OutputFormat>> presets() async =>
      (await _kit.capabilities(CapabilityRequest.device)).outputFormats;

  @override
  void attach(TickerProvider vsync) {}

  @override
  void detach() {}

  @override
  Future<void> close() => _kit.close();
}
