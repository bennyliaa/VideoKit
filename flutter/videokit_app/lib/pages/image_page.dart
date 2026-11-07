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
    final r = await s.bind(
      _scope.backend.sourceFor(entry),
      initialState: restore,
      hostActions: EntryHost.actionsFor(_scope, entry),
    );
    if (!mounted || generation != _generation) return;
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
        if (!didPop) unawaited(close());
      },
      child: Scaffold(
        backgroundColor: t.colors.playerCanvas,
        body: s == null
            ? VideoKitStateView(
                model: mapSessionState(phase: SessionPhase.created)!,
              )
            : VideoKitImageViewer(
                key: ObjectKey(s),
                session: s,
                title: current.displayName,
                source: _scope.backend.sourceFor(current),
                pictureBuilder: _scope.backend.pictureBuilder,
                resolveHostString: (k) => resolveAppHostString(context, k),
                onBack: () => unawaited(close()),
                options: VideoKitImageViewerOptions(
                  showPageButtons: pages.length > 1,
                ),
              ),
      ),
    );
  }
}
