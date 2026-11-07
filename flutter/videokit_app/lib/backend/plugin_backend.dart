import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/videokit_flutter.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/history_entry.dart';
import '../picker/channel_media_picker.dart';
import '../picker/media_picker.dart';
import '../startup/app_bootstrap.dart';
import 'app_backend.dart';

/// Release backend (04A P3): the `videokit_flutter` plugin over the native
/// Kit, with the system document picker (`ChannelMediaPicker`) and export
/// "另存为" (`ChannelExportTarget`). Never imports `videokit_fake`.
class PluginBackend implements AppBackend {
  PluginBackend._(this._kit, this._picker, this._exportTarget);

  final FlutterVideoKit _kit;
  final ChannelMediaPicker _picker;
  final ChannelExportTarget _exportTarget;
  int _exports = 0;

  /// Id of the precheck sink the native App registers at start-up.
  static const String precheckSinkId = 'app-export';

  /// Connects to the native Kit; throws [AppStartupException] when the
  /// channel or backend is unavailable or the protocol does not match.
  static Future<PluginBackend> connect([
    VideoKitConfig config = const VideoKitConfig(),
  ]) async {
    try {
      return PluginBackend._(
        await FlutterVideoKit.connect(config),
        const ChannelMediaPicker(),
        const ChannelExportTarget(),
      );
    } on VideoKitInitException catch (e) {
      throw AppStartupException(startupFailureOf(e.failure), e.diagnostic);
    }
  }

  /// Maps the plugin's init failure to the App's start-up failure.
  static StartupFailure startupFailureOf(VideoKitInitFailure f) => switch (f) {
    VideoKitInitFailure.protocolMismatch => StartupFailure.protocolMismatch,
    VideoKitInitFailure.noBackend => StartupFailure.noBackend,
    VideoKitInitFailure.channelUnavailable => StartupFailure.channelUnavailable,
  };

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
  VideoKitOutputSink get exportSink => const VideoKitOutputSink(
    sinkRef: 'registered:$precheckSinkId',
    capabilities: ChannelExportTarget.sinkCapabilities,
  );

  /// `ACTION_CREATE_DOCUMENT`, then a one-shot native sink for the chosen
  /// document (it unregisters itself after `markReady` or `abort`).
  @override
  Future<VideoKitOutputSink?> prepareExport({
    required String suggestedName,
    required String mimeType,
  }) => _exportTarget.prepare(
    '$precheckSinkId-${++_exports}',
    suggestedName: suggestedName,
    mimeType: mimeType,
  );

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
