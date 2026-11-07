import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'gallery/gallery_page.dart';
import 'gallery/gallery_settings.dart';
import 'gallery/gallery_text.dart';
import 'l10n/gen/example_localizations.dart';

/// VideoKit module example app (M0-B1: theme gallery only). Not the
/// VideoKit App (01 §1).
class VideoKitExampleApp extends StatefulWidget {
  /// Creates the app.
  const VideoKitExampleApp({super.key, this.initial = const GallerySettings()});

  /// Initial settings.
  final GallerySettings initial;

  @override
  State<VideoKitExampleApp> createState() => _VideoKitExampleAppState();
}

class _VideoKitExampleAppState extends State<VideoKitExampleApp> {
  late GallerySettings _settings = widget.initial;

  ThemeMode get _hostMode => switch (_settings.mode) {
    VideoKitThemeMode.dark => ThemeMode.dark,
    VideoKitThemeMode.light => ThemeMode.light,
    VideoKitThemeMode.system ||
    VideoKitThemeMode.followHost => ThemeMode.system,
  };

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      onGenerateTitle: (context) {
        final t = GalleryText.of(context);
        return t(t.l.appTitle);
      },
      debugShowCheckedModeBanner: false,
      locale: _settings.locale,
      localizationsDelegates: [
        ExampleLocalizations.delegate,
        ...videoKitLocalizationsDelegates,
      ],
      supportedLocales: videoKitSupportedLocales,
      localeResolutionCallback: videoKitResolveLocale,
      theme: ThemeData(brightness: Brightness.light),
      darkTheme: ThemeData(brightness: Brightness.dark),
      themeMode: _hostMode,
      builder: (context, child) {
        final mq = MediaQuery.of(context);
        return MediaQuery(
          // R1-11: the gallery factor is a debug multiplier on top of the
          // system font scale, never a replacement for it.
          data: mq.copyWith(
            textScaler: DebugTextScaler.on(mq.textScaler, _settings.textScale),
          ),
          child: VideoKitThemeScope(
            mode: _settings.mode,
            overrides: _settings.overrides,
            reduceMotion: _settings.reduceMotion ? true : null,
            child: child!,
          ),
        );
      },
      home: GalleryPage(
        settings: _settings,
        onChanged: (s) => setState(() => _settings = s),
      ),
    );
  }
}

/// System text scaling times a debug factor (gallery "额外字体倍数").
final class DebugTextScaler extends TextScaler {
  const DebugTextScaler._(this.base, this.factor);

  /// [base] unchanged when [factor] is 1.
  static TextScaler on(TextScaler base, double factor) =>
      factor == 1 ? base : DebugTextScaler._(base, factor);

  /// System (or host) scaler.
  final TextScaler base;

  /// Debug factor.
  final double factor;

  @override
  double scale(double fontSize) => base.scale(fontSize) * factor;

  @override
  // ignore: deprecated_member_use
  double get textScaleFactor => base.textScaleFactor * factor;

  @override
  bool operator ==(Object other) =>
      other is DebugTextScaler && other.base == base && other.factor == factor;

  @override
  int get hashCode => Object.hash(base, factor);
}
