import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

/// Host primary colour presets offered by the gallery (null = design
/// default). Host-side example values, not VideoKit tokens.
const List<Color?> galleryPrimaryPresets = [
  null,
  Color(0xFF1565C0),
  Color(0xFF2E7D32),
  Color(0xFFFFEB3B),
  Color(0xFF6A1B9A),
];

/// Text scale presets (03 §7.3: 100 % / 130 % / 200 %).
const List<double> galleryTextScales = [1.0, 1.3, 2.0];

/// Gallery languages: Chinese and pseudo-localization (13 §3.1).
const List<Locale> galleryLocales = [Locale('zh'), VkPseudo.locale];

/// Gallery settings (example-app state only).
@immutable
class GallerySettings {
  /// Creates settings.
  const GallerySettings({
    this.mode = VideoKitThemeMode.dark,
    this.primary,
    this.locale = const Locale('zh'),
    this.textScale = 1.0,
    this.reduceMotion = false,
  });

  /// Theme mode.
  final VideoKitThemeMode mode;

  /// Host primary override, null = default.
  final Color? primary;

  /// Locale (Chinese or pseudo).
  final Locale locale;

  /// Text scale.
  final double textScale;

  /// Reduced motion.
  final bool reduceMotion;

  /// Overrides for the theme scope.
  VideoKitThemeOverrides? get overrides =>
      primary == null ? null : VideoKitThemeOverrides.primary(primary!);

  /// Returns a copy with the given fields replaced.
  GallerySettings copyWith({
    VideoKitThemeMode? mode,
    Color? Function()? primary,
    Locale? locale,
    double? textScale,
    bool? reduceMotion,
  }) => GallerySettings(
    mode: mode ?? this.mode,
    primary: primary == null ? this.primary : primary(),
    locale: locale ?? this.locale,
    textScale: textScale ?? this.textScale,
    reduceMotion: reduceMotion ?? this.reduceMotion,
  );
}
