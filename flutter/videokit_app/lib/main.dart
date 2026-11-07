import 'package:flutter/widgets.dart';

import 'app.dart';
import 'backend/backend_selector.dart';
import 'history/app_storage.dart';

/// VideoKit App entry point.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(VideoKitApp(backend: createBackend(), storage: FileAppStorage()));
}
