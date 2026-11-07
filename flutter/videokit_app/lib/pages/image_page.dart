import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../host/entry_host.dart';
import 'player_page.dart';

/// UI-03 image viewer (M2): opens a record and pages through the other
/// image records of the history ("上一张 / 下一张" go to the App as
/// navigation requests). Each page gets its own session (a page that fails
/// fatally is never re-bound, TEST-R1 R1-10). "收藏" / "标签" are App host
/// actions; an animated image restores its looping setting (04A L3).
class ImagePage extends StatefulWidget {
  /// Creates the page.
  const ImagePage({super.key, required this.entry});

  /// Record opened first.
  final HistoryEntry entry;

  @override
  State<ImagePage> createState() => ImagePageState();
}

/// State (public for tests).
class ImagePageState extends State<ImagePage> {
  /// Session of the current page.
  VideoKitSession? session;

  /// Record shown now.
  late HistoryEntry current = widget.entry;

  late AppScope _scope;
  bool _started = false;
  bool _closing = false;
  EntryHost? _host;
  int _generation = 0;

  /// Opening did not finish (R2-03): error with "重试".
  bool openFailed = false;

  /// Image records the viewer pages through, in the home list's order.
  List<HistoryEntry> get pages => [
    for (final e in _scope.history.entries)
      if (e.isImage && !e.unavailable) e,
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_open(widget.entry));
  }

  @override
  void dispose() {
    _generation++;
    _unregister();
    super.dispose();
  }

  void _unregister() {
    final s = session;
    final h = _host;
    if (s != null && h != null) _scope.backend.hosts.unregister(s.sessionId, h);
    _host = null;
  }

  Future<void> _open(HistoryEntry entry) async {
    final generation = ++_generation;
    final s = await _scope.backend.videoKit.createSession(
      const VideoKitSessionConfig(debugLabel: 'app-image'),
    );
    if (!mounted || generation != _generation) {
      await s.close();
      return;
    }
    final host = EntryHost(
      scope: _scope,
      context: () => context,
      entryId: entry.id,
      onNavigate: _navigate,
    )..session = s;
    _scope.backend.hosts.register(s.sessionId, host);
    _host = host;
    setState(() {
      session = s;
      current = entry;
    });
    // 04A L3: an animated image comes back with its looping setting, from
    // the first frame.
    final restore = entry.kind == MediaKind.imageAnimated
        ? entry.playbackState?.copyWith(positionUs: 0)
        : null;
    void watch() {
      if (s.state.value.phase.isReleasingOrReleased &&
          !_closing &&
          mounted &&
          generation == _generation) {
        setState(() => openFailed = true);
      }
    }

    s.state.addListener(watch);
    final r = await s
        .bind(
          _scope.backend.sourceFor(entry),
          initialState: restore,
          hostActions: EntryHost.actionsFor(_scope, entry),
        )
        .then<VideoKitCommandResult?>((r) => r)
        .timeout(PlayerPage.defaultOpenTimeout, onTimeout: () => null);
    s.state.removeListener(watch);
    if (!mounted || generation != _generation || _closing || openFailed) {
      return;
    }
    // R2-03: never left on "正在打开".
    if (r == null ||
        r is SessionReleased ||
        s.state.value.phase.isReleasingOrReleased) {
      setState(() => openFailed = true);
      return;
    }
    if (r is Rejected && isAccessError(r.error.code)) {
      await _scope.history.markUnavailable(entry.id);
      return;
    }
    if (r is Executed && s.state.value.mediaKind == MediaKind.imageAnimated) {
      await s.execute(const Play());
    }
  }

  /// Host side of "上一张 / 下一张": answers at once, then switches pages.
  Future<NavigationResult> _navigate(NavigationDirection direction) async {
    final list = pages;
    final at = list.indexWhere((e) => e.id == current.id);
    final next = at + (direction == NavigationDirection.next ? 1 : -1);
    if (at < 0 || next < 0 || next >= list.length) {
      return NavigationResult.unavailable;
    }
    scheduleMicrotask(() => unawaited(_switchTo(list[next])));
    return NavigationResult.accepted;
  }

  Future<void> _switchTo(HistoryEntry next) async {
    if (!mounted || _closing) return;
    final old = session;
    final oldEntry = current;
    _unregister();
    unawaited(saveAndClose(_scope, oldEntry, old));
    await _open(_scope.history.byId(next.id) ?? next);
  }

  /// Saves and leaves.
  Future<void> close() async {
    if (_closing) return;
    _closing = true;
    _unregister();
    await saveAndClose(_scope, current, session);
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
        final viewer = s == null
            ? null
            : GlobalObjectKey<VideoKitImageViewerState>(s).currentState;
        if (didPop || (viewer?.hasOpenPanel ?? false)) return;
        unawaited(close());
      },
      child: Scaffold(
        backgroundColor: t.colors.playerCanvas,
        body: openFailed
            ? SafeArea(
                child: openFailedView(
                  context,
                  onRetry: () async {
                    setState(() => openFailed = false);
                    _unregister();
                    final old = session;
                    if (old != null) unawaited(old.close());
                    await _open(current);
                  },
                ),
              )
            : s == null
            ? VideoKitStateView(
                model: mapSessionState(phase: SessionPhase.created)!,
              )
            : VideoKitImageViewer(
                key: GlobalObjectKey<VideoKitImageViewerState>(s),
                session: s,
                title: current.displayName,
                source: _scope.backend.sourceFor(current),
                pictureBuilder: _scope.backend.pictureBuilder,
                resolveHostString: (k) => resolveAppHostString(context, k),
                onBack: () => unawaited(close()),
                onStateAction: (a) {
                  if (a != StateAction.showCapabilities) return;
                  // J4: read-only capability page.
                  unawaited(
                    Navigator.of(context).push(
                      MaterialPageRoute<void>(
                        builder: (_) => VideoKitCapabilitiesPage(
                          capabilities: _scope.backend.videoKit.capabilities(
                            const CapabilityRequest(),
                          ),
                        ),
                      ),
                    ),
                  );
                },
                options: VideoKitImageViewerOptions(
                  showPageButtons: pages.length > 1,
                ),
              ),
      ),
    );
  }
}
