import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/history_entry.dart';
import '../picker/media_picker.dart';

/// What the App needs from a VideoKit backend (REQ-APP-05: public API
/// only). M0: `DemoBackend` (Dart Fake); M1: the `videokit_flutter`
/// plugin with `ChannelMediaPicker`. Chosen in `backend_selector.dart`.
abstract interface class AppBackend {
  /// Demo data (shows the demo badge, export creates no real file).
  bool get isDemo;

  /// Media picker.
  MediaPickerService get picker;

  /// The VideoKit entry point.
  VideoKit get videoKit;

  /// Source for a recorded entry.
  VideoKitMediaSource sourceFor(HistoryEntry entry);

  /// Picture builder for sessions without a texture (Fake only).
  VideoKitPictureBuilder? get pictureBuilder;

  /// Thumbnail of a record (small file, or a demo picture).
  Widget thumbnail(BuildContext context, HistoryEntry entry);

  /// Output sink for exports (M2: `ACTION_CREATE_DOCUMENT` "另存为").
  VideoKitOutputSink get exportSink;

  /// Export presets (`capabilities().outputFormats`).
  Future<List<OutputFormat>> presets();

  /// Starts backend timing (the Fake clock follows frames).
  void attach(TickerProvider vsync);

  /// Stops backend timing.
  void detach();

  /// Releases the backend.
  Future<void> close();
}
