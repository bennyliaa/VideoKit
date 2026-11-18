import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'app_scope.dart';
import 'avatar/avatar_store.dart';
import 'backend/app_backend.dart';
import 'history/app_storage.dart';
import 'history/history_store.dart';
import 'entitlement/entitlement_service.dart';
import 'home/home_page.dart';
import 'library/library_lock.dart';
import 'library/library_store.dart';
import 'l10n/gen/app_localizations.dart';
import 'pages/launcher.dart';
import 'picker/media_picker.dart';
import 'projects/export_journal.dart';
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
    this.libraryHashRounds = LibraryLock.defaultRounds,
    this.entitlements,
  });

  /// Entitlement service (REQ-APP-15); null = always subscribed (VK-A2).
  final EntitlementService? entitlements;

  /// PIN hash rounds of the media library (tests use fewer).
  final int libraryHashRounds;

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
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  /// Media library (REQ-APP-09–13).
  late final LibraryStore library = LibraryStore(
    storage: widget.storage,
    platform: widget.backend.library,
    now: widget.now,
  );

  /// Entitlements (REQ-APP-15).
  late final EntitlementService entitlements =
      widget.entitlements ?? AlwaysSubscribedEntitlements();

  /// Kit feature state for the module widgets (REQ-API-10): every feature
  /// enabled, the gate answered by [AppHostCallbacks.checkFeature].
  late final VideoKitFeatures kitFeatures = VideoKitFeatures(
    VideoKitFeatureGate(callbacks: widget.backend.hosts),
  );

  /// Locks on the Kit entries of paid features the user may not use
  /// (REQ-APP-15: entries stay, with a lock). A trial shows no lock; the
  /// home page says "试用中 · 剩 N 天" instead.
  void _syncBadges() {
    final e = entitlements.value;
    for (final f in VideoKitFeature.configurable) {
      final app = AppFeature.ofKit(f);
      kitFeatures.setBadge(
        f,
        app != null && !e.allows(app) ? FeatureBadge.lock : null,
      );
    }
  }

  /// Media library lock (REQ-APP-10).
  late final LibraryLock libraryLock = LibraryLock(
    storage: widget.storage,
    platform: widget.backend.library,
    now: widget.now,
    rounds: widget.libraryHashRounds,
  );

  /// REQ-APP-10: leaving the App (background, screen off) starts the
  /// auto-lock delay; coming back locks when it has passed.
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.paused || AppLifecycleState.hidden:
        libraryLock.appLeft();
      case AppLifecycleState.resumed:
        libraryLock.appReturned();
      case AppLifecycleState.inactive || AppLifecycleState.detached:
        break;
    }
  }

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

  /// The export in progress (M6-A1: a notice after the App was killed).
  late final ExportJournal exportJournal = ExportJournal(
    storage: widget.storage,
    now: widget.now,
  );

  /// The App's avatars (REQ-ED-07); the Kit reads them via `openAvatar`.
  late final AvatarStore avatars = AvatarStore(
    storage: widget.storage,
    now: widget.now,
    // 04A E7 Q4: avatars used by kept projects are never evicted.
    referenced: () => projects.referencedAvatars,
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
    await avatars.load();
    await exportJournal.load();
    await library.load();
    await libraryLock.load();
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    widget.backend.attach(this);
    widget.backend.hosts.avatars = avatars;
    // REQ-API-10 / REQ-APP-15: the App answers the Kit's feature gate from
    // its entitlements; the lock badges follow them.
    widget.backend.hosts
      ..entitlements = entitlements
      ..dialogContext = () => _navigator.currentContext;
    entitlements.addListener(_syncBadges);
    _syncBadges();
    _incoming = widget.backend.picker.incoming.listen(_onIncoming);
  }

  void _onIncoming(List<PickedMedia> media) {
    final ctx = _navigator.currentContext;
    if (ctx == null || media.isEmpty) return;
    unawaited(MediaLauncher.openPicked(ctx, media));
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    entitlements.removeListener(_syncBadges);
    kitFeatures.dispose();
    library.dispose();
    libraryLock.dispose();
    unawaited(_incoming?.cancel());
    widget.backend.detach();
    history.dispose();
    settings.dispose();
    projects.dispose();
    avatars.dispose();
    exportJournal.dispose();
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
      avatars: avatars,
      exportJournal: exportJournal,
      library: library,
      libraryLock: libraryLock,
      entitlements: entitlements,
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
            child: VideoKitFeatureScope(features: kitFeatures, child: child!),
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
