import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app.dart';
import '../backend/app_backend.dart';
import '../history/app_storage.dart';
import '../l10n/app_text.dart';
import '../l10n/gen/app_localizations.dart';

/// Why the backend could not start (M1-A1 item 1).
enum StartupFailure {
  /// Native protocol version differs from the Dart side.
  protocolMismatch,

  /// The native side has no backend (release build without a backend).
  noBackend,

  /// The plugin channel is missing or failed.
  channelUnavailable,

  /// Anything else.
  unknown,
}

/// Thrown by backend connectors; carries no media data.
final class AppStartupException implements Exception {
  /// Creates the exception.
  const AppStartupException(this.failure, [this.diagnostic]);

  /// Classified reason.
  final StartupFailure failure;

  /// English, redacted diagnostic (never shown to users).
  final String? diagnostic;

  @override
  String toString() => 'AppStartupException(${failure.name}, $diagnostic)';
}

/// Connects the backend.
typedef BackendConnector = Future<AppBackend> Function();

/// First launch / start-up (M1-A1 item 1): connects the backend while a
/// loading state is shown; on failure shows a `VideoKitStateView` with the
/// reason and "重试". Once connected the App proper starts.
class AppBootstrap extends StatefulWidget {
  /// Creates the bootstrap.
  const AppBootstrap({
    super.key,
    required this.connect,
    required this.storage,
    this.now,
    this.locale,
    this.fontFamily,
  });

  /// Backend connector (`PluginBackend.connect` in release).
  final BackendConnector connect;

  /// App-private storage.
  final AppStorage storage;

  /// Clock (tests).
  final DateTime Function()? now;

  /// Forced locale (tests).
  final Locale? locale;

  /// Font family for review screenshots; null uses the platform font.
  final String? fontFamily;

  @override
  State<AppBootstrap> createState() => AppBootstrapState();
}

/// State (public for tests).
class AppBootstrapState extends State<AppBootstrap> {
  /// Connected backend.
  AppBackend? backend;

  /// Last failure, if any.
  StartupFailure? failure;

  bool _connecting = false;

  /// Whether a connection attempt is running.
  bool get connecting => _connecting;

  @override
  void initState() {
    super.initState();
    unawaited(retry());
  }

  /// (Re)connects the backend.
  Future<void> retry() async {
    if (_connecting) return;
    setState(() {
      _connecting = true;
      failure = null;
    });
    try {
      final b = await widget.connect();
      if (!mounted) {
        await b.close();
        return;
      }
      setState(() => backend = b);
    } on AppStartupException catch (e) {
      if (mounted) setState(() => failure = e.failure);
    } on Object {
      if (mounted) setState(() => failure = StartupFailure.unknown);
    } finally {
      if (mounted) setState(() => _connecting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final b = backend;
    if (b != null) {
      return VideoKitApp(
        backend: b,
        storage: widget.storage,
        now: widget.now,
        locale: widget.locale,
        fontFamily: widget.fontFamily,
      );
    }
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      locale: widget.locale ?? const Locale('zh'),
      localizationsDelegates: [
        AppLocalizations.delegate,
        ...videoKitLocalizationsDelegates,
      ],
      supportedLocales: videoKitSupportedLocales,
      localeResolutionCallback: videoKitResolveLocale,
      theme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: widget.fontFamily,
      ),
      builder: (context, child) =>
          VideoKitThemeScope(mode: VideoKitThemeMode.dark, child: child!),
      home: StartupPage(
        failure: failure,
        connecting: _connecting,
        onRetry: () => unawaited(retry()),
      ),
    );
  }
}

/// Start-up loading / error page.
class StartupPage extends StatelessWidget {
  /// Creates the page.
  const StartupPage({
    super.key,
    required this.failure,
    required this.connecting,
    required this.onRetry,
  });

  /// Failure to show, or null while connecting.
  final StartupFailure? failure;

  /// A connection attempt is running.
  final bool connecting;

  /// Retry.
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final f = failure;
    final StateViewModel model;
    if (f == null || connecting) {
      model = StateViewModel(
        kind: StateViewKind.loading,
        iconName: 'movie',
        titleText: a(a.l.startupConnecting),
      );
    } else {
      final (title, detail) = switch (f) {
        StartupFailure.protocolMismatch => (
          a.l.startupProtocolTitle,
          a.l.startupProtocolDetail,
        ),
        StartupFailure.noBackend => (
          a.l.startupNoBackendTitle,
          a.l.startupNoBackendDetail,
        ),
        StartupFailure.channelUnavailable => (
          a.l.startupChannelTitle,
          a.l.startupChannelDetail,
        ),
        StartupFailure.unknown => (
          a.l.startupUnknownTitle,
          a.l.startupUnknownDetail,
        ),
      };
      model = StateViewModel(
        kind: StateViewKind.error,
        iconName: 'warning',
        titleText: a(title),
        detailText: a(detail),
        // A protocol mismatch or a missing backend does not go away by
        // retrying; only offer it where it can help.
        actions:
            f == StartupFailure.channelUnavailable ||
                f == StartupFailure.unknown
            ? const [StateAction.retry]
            : const [],
      );
    }
    return Scaffold(
      backgroundColor: t.colors.playerCanvas,
      body: SafeArea(
        child: VideoKitStateView(model: model, onStateAction: (_) => onRetry()),
      ),
    );
  }
}
