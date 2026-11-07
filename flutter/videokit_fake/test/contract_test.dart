import 'package:videokit_fake/videokit_fake.dart';

/// The Dart Fake must pass the shared contract suite (14 §11.2).
void main() {
  runVideoKitContractTests(
    (config) => FakeVideoKit(config: config),
    elapse: (kit, d) => (kit as FakeVideoKit).clock.advance(d),
    description: 'FakeVideoKit contract',
  );
}
