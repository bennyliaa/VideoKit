import 'app_backend.dart';
import 'demo_backend.dart';

/// Backend selection point (M0-B5 item 1). `--dart-define=VIDEOKIT_BACKEND=`
/// chooses the implementation; M0 has only `demo` (Dart Fake). M1 adds
/// `plugin` (`videokit_flutter` + `ChannelMediaPicker`) and moves the demo
/// backend behind a separate entry point so release builds do not contain
/// the Fake (REQ-APP-06, report §3).
AppBackend createBackend() {
  const name = String.fromEnvironment('VIDEOKIT_BACKEND', defaultValue: 'demo');
  return switch (name) {
    _ => DemoBackend(),
  };
}
