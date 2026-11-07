import 'package:flutter/foundation.dart';

import 'theme_data.dart';

/// Source of VideoKit theme values (03 §5.1, 14 §7.1). V1.0 ships
/// `DefaultThemeSource`; SkinKit will be another implementation later
/// (03 §5.5) without component changes.
abstract interface class VideoKitThemeSource {
  /// Token schema version this source produces (currently 1).
  int get themeSchemaVersion;

  /// Resolves the theme for [brightness] with optional host [overrides].
  VideoKitThemeData resolve(
    Brightness brightness,
    VideoKitThemeOverrides? overrides,
  );

  /// Notifies when the source changes (host re-skin, SkinKit); null if
  /// static.
  Listenable? get changes;
}
