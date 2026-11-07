import 'package:flutter/widgets.dart';

import 'app.dart';
import 'backend/plugin_backend.dart';
import 'history/app_storage.dart';

/// VideoKit App release entry point (04A P3): the native Kit through the
/// `videokit_flutter` plugin. Never imports `videokit_fake`; the release
/// isolation check (`tool/release_isolation.dart`) enforces this.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final backend = await PluginBackend.connect();
  runApp(VideoKitApp(backend: backend, storage: FileAppStorage()));
}
