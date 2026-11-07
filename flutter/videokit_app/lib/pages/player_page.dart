import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../host/entry_host.dart';
import '../l10n/app_text.dart';

/// Errors that mean "file moved / permission lost" (REQ-APP-07).
bool isAccessError(ErrorCode code) =>
    code == ErrorCode.sourceNotFound ||
    code == ErrorCode.sourcePermissionDenied;

/// Saves the session's playback snapshot into the history (01 §4.13:
/// `captureState()` → stored → next `bind(initialState: …)`), then closes
/// the session.
Future<void> saveAndClose(
  AppScope scope,
  HistoryEntry entry,
  VideoKitSession? session,
) async {
  if (session == null) return;
  final st = session.state.value;
  if (st.phase.isBound || st.phase == SessionPhase.ended) {
    final snap = await session.captureState();
    final size = session.videoSize.value;
    final info = st.mediaInfo;
    // Small thumbnail only for recorded entries (REQ-APP-08).
    String? thumb;
    if (scope.history.byId(entry.id) != null) {
      final t = await session.captureThumbnail(st.positionUs, 320, 180);
      if (t is ThumbnailCaptured) {
        final ext = t.mimeType == 'image/png' ? 'png' : 'jpg';
        thumb = await scope.storage.writeThumbnail(
          '${entry.id}-${DateTime.now().millisecondsSinceEpoch}.$ext',
          t.bytes,
        );
      }
    }
    await scope.history.updatePlayback(
      entry.id,
      // Images keep a snapshot only when animated (04A L3: looping).
      snapshot: !entry.isImage || st.mediaKind == MediaKind.imageAnimated
          ? snap
          : null,
      positionUs: entry.isImage ? null : st.positionUs,
      durationUs: info?.durationUs ?? st.durationUs,
      width: info?.width ?? size?.width,
      height: info?.height ?? size?.height,
      kind: st.mediaKind,
      videoCodec: info?.videoCodec,
      mimeType: info?.container,
      thumbnailPath: thumb,
    );
  } else if (st.error case final e? when isAccessError(e.code)) {
    await scope.history.markUnavailable(entry.id);
  }
  await session.close();
}

/// "没有打开成功" with "重试" (TEST-R2 R2-03), shared by player and image
/// pages.
Widget openFailedView(
  BuildContext context, {
  required Future<void> Function() onRetry,
}) {
  final a = AppText.of(context);
  return VideoKitStateView(
    model: StateViewModel(
      kind: StateViewKind.error,
      iconName: 'warning',
      titleText: a(a.l.openFailedTitle),
      detailText: a(a.l.openFailedDetail),
      actions: const [StateAction.retry],
    ),
    onStateAction: (_) => unawaited(onRetry()),
  );
}

/// UI-01 player for one record; resumes from the saved snapshot.
class PlayerPage extends StatefulWidget {
  /// Creates the page.
  const PlayerPage({
    super.key,
    required this.entry,
    this.fromStart = false,
    this.openTimeout = defaultOpenTimeout,
  });

  /// How long "正在打开" may last before the page offers a retry (TEST-R2
  /// R2-03: an open that never finishes must reach a final state).
  static const Duration defaultOpenTimeout = Duration(seconds: 45);

  /// See [defaultOpenTimeout].
  final Duration openTimeout;

  /// Record.
  final HistoryEntry entry;

  /// Ignore the saved position ("从头播放").
  final bool fromStart;

  @override
  State<PlayerPage> createState() => PlayerPageState();
}

/// State (public for tests).
class PlayerPageState extends State<PlayerPage> {
  /// Session once created.
  VideoKitSession? session;
  late AppScope _scope;
  bool _started = false;
  bool _closing = false;
  EntryHost? _host;
  final GlobalKey<VideoKitPlayerState> _player = GlobalKey();

  /// Opening did not finish (timed out, or the session was released while
  /// opening): an error with "重试" is shown instead of "正在打开".
  bool openFailed = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_open());
  }

  @override
  void dispose() {
    _unregister();
    super.dispose();
  }

  void _unregister() {
    final s = session;
    final h = _host;
    if (s != null && h != null) _scope.backend.hosts.unregister(s.sessionId, h);
    _host = null;
  }

  /// "重试" after a failed open: a fresh session, bound again.
  Future<void> retryOpen() async {
    final old = session;
    _unregister();
    setState(() {
      openFailed = false;
      session = null;
    });
    if (old != null) unawaited(old.close());
    await _open();
  }

  Future<void> _open() async {
    final s = await _scope.backend.videoKit.createSession(
      const VideoKitSessionConfig(debugLabel: 'app-player'),
    );
    if (!mounted) {
      await s.close();
      return;
    }
    // M2: "收藏" / "标签" are App business (history), routed by session.
    final host = EntryHost(
      scope: _scope,
      context: () => context,
      entryId: widget.entry.id,
    )..session = s;
    _scope.backend.hosts.register(s.sessionId, host);
    _host = host;
    setState(() => session = s);
    // R2-03: released underneath while opening → final state at once.
    void watch() {
      if (s.state.value.phase.isReleasingOrReleased &&
          !_closing &&
          mounted &&
          identical(s, session)) {
        setState(() => openFailed = true);
      }
    }

    s.state.addListener(watch);
    final r = await s
        .bind(
          _scope.backend.sourceFor(widget.entry),
          initialState: widget.fromStart ? null : widget.entry.playbackState,
          hostActions: EntryHost.actionsFor(_scope, widget.entry),
        )
        .then<VideoKitCommandResult?>((r) => r)
        .timeout(widget.openTimeout, onTimeout: () => null);
    s.state.removeListener(watch);
    if (!mounted || _closing || !identical(s, session) || openFailed) return;
    // R2-03: no answer in time, or released underneath (e.g. the native
    // player went away during a configuration change) → final state.
    if (r == null ||
        r is SessionReleased ||
        s.state.value.phase.isReleasingOrReleased) {
      setState(() => openFailed = true);
      return;
    }
    if (r is Rejected && isAccessError(r.error.code)) {
      await _scope.history.markUnavailable(widget.entry.id);
      return;
    }
    if (r is Executed) await s.execute(const Play());
  }

  /// Saves the snapshot and leaves.
  Future<void> close() async {
    if (_closing) return;
    _closing = true;
    await saveAndClose(_scope, widget.entry, session);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = session;
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        // R2-01: with a panel open the back press only closes the panel.
        if (didPop || (_player.currentState?.hasOpenPanel ?? false)) return;
        unawaited(close());
      },
      child: Scaffold(
        backgroundColor: t.colors.playerCanvas,
        body: openFailed
            ? SafeArea(child: openFailedView(context, onRetry: retryOpen))
            : s == null
            ? VideoKitStateView(
                model: mapSessionState(phase: SessionPhase.created)!,
              )
            : VideoKitPlayer(
                key: _player,
                session: s,
                title: widget.entry.displayName,
                pictureBuilder: _scope.backend.pictureBuilder,
                resolveHostString: (k) => resolveAppHostString(context, k),
                onBack: () => unawaited(close()),
                onStateAction: (a) {
                  if (a == StateAction.retry ||
                      a == StateAction.reconnectSource) {
                    unawaited(
                      s.bind(
                        _scope.backend.sourceFor(widget.entry),
                        initialState: widget.entry.playbackState,
                        hostActions: EntryHost.actionsFor(_scope, widget.entry),
                      ),
                    );
                  }
                },
              ),
      ),
    );
  }
}
