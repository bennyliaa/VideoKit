import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';

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
    await scope.history.updatePlayback(
      entry.id,
      snapshot: entry.isImage ? null : snap,
      positionUs: entry.isImage ? null : st.positionUs,
      durationUs: st.durationUs,
      width: size?.width,
      height: size?.height,
      kind: st.mediaKind,
    );
  } else if (st.error case final e? when isAccessError(e.code)) {
    await scope.history.markUnavailable(entry.id);
  }
  await session.close();
}

/// UI-01 player for one record; resumes from the saved snapshot.
class PlayerPage extends StatefulWidget {
  /// Creates the page.
  const PlayerPage({super.key, required this.entry, this.fromStart = false});

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
      const VideoKitSessionConfig(debugLabel: 'app-player'),
    );
    if (!mounted) {
      await s.close();
      return;
    }
    setState(() => session = s);
    final r = await s.bind(
      _scope.backend.sourceFor(widget.entry),
      initialState: widget.fromStart ? null : widget.entry.playbackState,
    );
    if (!mounted) return;
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
        if (!didPop) unawaited(close());
      },
      child: Scaffold(
        backgroundColor: t.colors.playerCanvas,
        body: s == null
            ? VideoKitStateView(
                model: mapSessionState(phase: SessionPhase.created)!,
              )
            : VideoKitPlayer(
                session: s,
                title: widget.entry.displayName,
                pictureBuilder: _scope.backend.pictureBuilder,
                onBack: () => unawaited(close()),
                onStateAction: (a) {
                  if (a == StateAction.retry ||
                      a == StateAction.reconnectSource) {
                    unawaited(
                      s.bind(
                        _scope.backend.sourceFor(widget.entry),
                        initialState: widget.entry.playbackState,
                      ),
                    );
                  }
                },
              ),
      ),
    );
  }
}
