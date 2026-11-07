import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'app_scope.dart';
import 'backend/app_backend.dart';
import 'history/app_storage.dart';
import 'history/history_store.dart';
import 'home/home_page.dart';
import 'l10n/gen/app_localizations.dart';
import 'pages/launcher.dart';
import 'picker/media_picker.dart';
import 'projects/project_store.dart';
import 'settings/app_settings.dart';

/// VideoKit App (01 §1, §4.13): the stand-alone player built on the
/// VideoKit module, which it uses only through `videokit_api` /
/// `videokit_ui` (REQ-APP-05).
class VideoKitApp extends StatefulWidget {
  /// Creates the app.
  const VideoKitApp({
    super.key,
    required this.backend,
    required this.storage,
    this.now,
    this.locale,
    this.fontFamily,
  });

  /// VideoKit backend (M0: Dart Fake).
  final AppBackend backend;

  /// App-private storage.
  final AppStorage storage;

  /// Clock for relative times (tests).
  final DateTime Function()? now;

  /// Forced locale (tests: pseudo-localization); null = Chinese.
  final Locale? locale;

  /// Font family for review screenshots; null uses the platform font.
  final String? fontFamily;

  @override
  State<VideoKitApp> createState() => VideoKitAppState();
}

/// State of [VideoKitApp] (public for tests).
class VideoKitAppState extends State<VideoKitApp>
    with SingleTickerProviderStateMixin {
  late final HistoryStore history = HistoryStore(
    storage: widget.storage,
    picker: widget.backend.picker,
    now: widget.now,
  );
  late final SettingsStore settings = SettingsStore(widget.storage);
  late final ProjectStore projects = ProjectStore(
    storage: widget.storage,
    now: widget.now,
  );
  final GlobalKey<NavigatorState> _navigator = GlobalKey();
  StreamSubscription<List<PickedMedia>>? _incoming;
  late final Future<void> _ready = _load();

  /// Navigator (tests).
  NavigatorState? get navigator => _navigator.currentState;

  Future<void> _load() async {
    await settings.load();
    await history.load();
    await projects.load();
  }

  @override
  void initState() {
    super.initState();
    widget.backend.attach(this);
    _incoming = widget.backend.picker.incoming.listen(_onIncoming);
  }

  void _onIncoming(List<PickedMedia> media) {
    final ctx = _navigator.currentContext;
    if (ctx == null || media.isEmpty) return;
    unawaited(MediaLauncher.openPicked(ctx, media));
  }

  @override
  void dispose() {
    unawaited(_incoming?.cancel());
    widget.backend.detach();
    history.dispose();
    settings.dispose();
    projects.dispose();
    super.dispose();
  }

  ThemeMode _hostMode(VideoKitThemeMode m) => switch (m) {
    VideoKitThemeMode.dark => ThemeMode.dark,
    VideoKitThemeMode.light => ThemeMode.light,
    VideoKitThemeMode.system ||
    VideoKitThemeMode.followHost => ThemeMode.system,
  };

  @override
  Widget build(BuildContext context) {
    return AppScope(
      backend: widget.backend,
      storage: widget.storage,
      history: history,
      settings: settings,
      projects: projects,
      child: ValueListenableBuilder<AppSettings>(
        valueListenable: settings,
        builder: (context, s, _) => MaterialApp(
          navigatorKey: _navigator,
          debugShowCheckedModeBanner: false,
          onGenerateTitle: (context) => AppLocalizations.of(context).appTitle,
          locale: widget.locale ?? const Locale('zh'),
          localizationsDelegates: [
            AppLocalizations.delegate,
            ...videoKitLocalizationsDelegates,
          ],
          supportedLocales: videoKitSupportedLocales,
          localeResolutionCallback: videoKitResolveLocale,
          theme: ThemeData(
            brightness: Brightness.light,
            fontFamily: widget.fontFamily,
          ),
          darkTheme: ThemeData(
            brightness: Brightness.dark,
            fontFamily: widget.fontFamily,
          ),
          themeMode: _hostMode(s.themeMode),
          builder: (context, child) => VideoKitThemeScope(
            mode: s.themeMode,
            reduceMotion: s.reduceMotion,
            child: child!,
          ),
          home: FutureBuilder<void>(
            future: _ready,
            builder: (context, snap) =>
                snap.connectionState == ConnectionState.done
                ? const HomePage()
                : const SizedBox.shrink(),
          ),
        ),
      ),
    );
  }
}
