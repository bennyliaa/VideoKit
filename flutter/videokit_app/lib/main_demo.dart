import 'package:flutter/widgets.dart';

import 'app.dart';
import 'backend/demo_backend.dart';
import 'history/app_storage.dart';

/// Demo entry point (04A P3, debug/development only):
/// `flutter run -t lib/main_demo.dart`. Runs on the Dart Fake with demo
/// documents; never used for release builds.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(VideoKitApp(backend: DemoBackend(), storage: FileAppStorage()));
}
