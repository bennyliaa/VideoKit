import 'package:flutter/widgets.dart';

import 'app.dart';
import 'backend/demo_backend.dart';
import 'history/app_storage.dart';
import 'startup/privacy_consent.dart';

/// Demo entry point (04A P3, debug/development only):
/// `flutter run -t lib/main_demo.dart`. Runs on the Dart Fake with demo
/// documents; never used for release builds. Same first launch as release
/// (privacy consent before anything starts, VK-A2).
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final storage = FileAppStorage();
  runApp(
    PrivacyGate(
      storage: storage,
      // The demo backend (and its Fake) is created only after consent.
      builder: () => VideoKitApp(backend: DemoBackend(), storage: storage),
    ),
  );
}
