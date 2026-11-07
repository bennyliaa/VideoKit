/// Platform interface of the VideoKit Flutter plugin (14 §8).
///
/// Contains the generated Pigeon protocol (`src/gen/messages.g.dart`) and [VideoKitPlatform], the
/// abstraction the `videokit_flutter` adapter talks to. Platform packages (Android today) implement the
/// native side of the same protocol.
library;

export 'src/gen/messages.g.dart';
export 'src/videokit_platform.dart';
