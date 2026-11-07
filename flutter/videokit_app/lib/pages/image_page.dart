import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import 'player_page.dart';

/// UI-03 image viewer for one record (images record the last viewed
/// time only).
class ImagePage extends StatefulWidget {
  /// Creates the page.
  const ImagePage({super.key, required this.entry});

  /// Record.
  final HistoryEntry entry;

  @override
  State<ImagePage> createState() => ImagePageState();
}

/// State (public for tests).
class ImagePageState extends State<ImagePage> {
  /// Session once created.
  VideoKitSession? session;
  late AppScope _scope;
  bool _started = false;
  bool _closing = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_open());
  }

  Future<void> _open() async {
    final s = await _scope.backend.videoKit.createSession(
      const VideoKitSessionConfig(debugLabel: 'app-image'),
    );
    if (!mounted) {
      await s.close();
      return;
    }
    setState(() => session = s);
    final r = await s.bind(_scope.backend.sourceFor(widget.entry));
    if (!mounted) return;
    if (r is Rejected && isAccessError(r.error.code)) {
      await _scope.history.markUnavailable(widget.entry.id);
      return;
    }
    if (r is Executed && s.state.value.mediaKind == MediaKind.imageAnimated) {
      await s.execute(const Play());
    }
  }

  /// Saves and leaves.
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
        if (!didPop) unawaited(close());
      },
      child: Scaffold(
        backgroundColor: t.colors.playerCanvas,
        body: s == null
            ? VideoKitStateView(
                model: mapSessionState(phase: SessionPhase.created)!,
              )
            : VideoKitImageViewer(
                session: s,
                title: widget.entry.displayName,
                source: _scope.backend.sourceFor(widget.entry),
                pictureBuilder: _scope.backend.pictureBuilder,
                onBack: () => unawaited(close()),
                options: const VideoKitImageViewerOptions(
                  showPageButtons: false,
                ),
              ),
      ),
    );
  }
}
