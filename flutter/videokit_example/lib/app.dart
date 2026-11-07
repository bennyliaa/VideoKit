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
          data: mq.copyWith(textScaler: TextScaler.linear(_settings.textScale)),
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
