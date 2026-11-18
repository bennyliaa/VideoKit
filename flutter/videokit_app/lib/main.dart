import 'package:flutter/widgets.dart';

import 'backend/plugin_backend.dart';
import 'history/app_storage.dart';
import 'startup/app_bootstrap.dart';
import 'startup/privacy_consent.dart';

/// VideoKit App release entry point (04A P3): the native Kit through the
/// `videokit_flutter` plugin. Never imports `videokit_fake`; the release
/// isolation check (`tool/release_isolation.dart`) enforces this.
///
/// Start-up:
/// * VK-A2 / FT01B-05: [PrivacyGate] first — until the privacy policy is
///   agreed to, nothing connects and no SDK is created;
/// * M1-A1: [AppBootstrap] shows a loading state while the backend
///   connects and an error page with retry when it cannot.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = FileAppStorage();
  runApp(
    PrivacyGate(
      storage: storage,
      builder: () =>
          AppBootstrap(connect: PluginBackend.connect, storage: storage),
    ),
  );
}
