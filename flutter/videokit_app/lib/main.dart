import 'package:flutter/widgets.dart';

import 'backend/plugin_backend.dart';
import 'history/app_storage.dart';
import 'startup/app_bootstrap.dart';

/// VideoKit App release entry point (04A P3): the native Kit through the
/// `videokit_flutter` plugin. Never imports `videokit_fake`; the release
/// isolation check (`tool/release_isolation.dart`) enforces this.
///
/// Start-up (M1-A1): [AppBootstrap] shows a loading state while the
/// backend connects and an error page with retry when it cannot.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    AppBootstrap(connect: PluginBackend.connect, storage: FileAppStorage()),
  );
}
