import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import 'player_page.dart';

/// UI-05 multi-view for several records; the App keeps the single-audio
/// epoch (07 §4) and saves every session's snapshot on leave.
class MultiViewPage extends StatefulWidget {
  /// Creates the page.
  const MultiViewPage({super.key, required this.entries});

  /// Records (at most 12 are opened).
  final List<HistoryEntry> entries;

  @override
  State<MultiViewPage> createState() => MultiViewPageState();
}

/// State (public for tests).
class MultiViewPageState extends State<MultiViewPage> {
  /// Sessions by entry ID.
  final Map<String, VideoKitSession> sessions = {};
  late AppScope _scope;
  bool _started = false;
  bool _closing = false;
  int _epoch = 0;

  /// Session with audio.
  String? activeAudio;

  List<HistoryEntry> get _entries =>
      widget.entries.take(VideoKitSlotGrid.maxSlots).toList();

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_open());
  }

  Future<void> _open() async {
    for (final e in _entries) {
      final s = await _scope.backend.videoKit.createSession(
        VideoKitSessionConfig(debugLabel: 'app-multi-${e.id}'),
      );
      if (!mounted) {
        await s.close();
        return;
      }
      setState(() => sessions[e.id] = s);
      unawaited(_bind(e, s));
    }
  }

  Future<void> _bind(HistoryEntry e, VideoKitSession s) async {
    final r = await s.bind(
      _scope.backend.sourceFor(e),
      initialState: e.playbackState,
    );
    if (!mounted || r is! Executed) return;
    if (e.kind == MediaKind.imageStatic) return;
    await s.execute(const SetMuted(true));
    await s.execute(const Play());
    // TEST-R4 O-4: the first video in grid order starts with the audio,
    // not whichever slot finished opening first.
    final first = _entries.where((x) => x.kind == MediaKind.video).firstOrNull;
    if (activeAudio == null && e.id == first?.id) {
      await activateAudio(s.sessionId);
    } else {
      // R3-01: a slot that joins later is told it has no audio.
      await s.execute(SetActiveAudio(false, _epoch));
    }
  }

  /// Makes [sessionId] the only audio source.
  Future<void> activateAudio(String sessionId) async {
    final epoch = ++_epoch;
    setState(() => activeAudio = sessionId);
    // TEST-R3 R3-01: every other slot is told it has no audio, not only the
    // previous one (a session's default may differ per Kit).
    for (final s in sessions.values) {
      if (s.sessionId == sessionId) {
        await s.execute(SetActiveAudio(true, epoch));
        await s.execute(const SetMuted(false));
      } else {
        await s.execute(SetActiveAudio(false, epoch));
        await s.execute(const SetMuted(true));
      }
    }
  }

  /// Mutes all: `SetActiveAudio(false)` to every slot (R3-01).
  Future<void> muteAll() async {
    final epoch = ++_epoch;
    setState(() => activeAudio = null);
    for (final s in sessions.values) {
      await s.execute(SetActiveAudio(false, epoch));
      await s.execute(const SetMuted(true));
    }
  }

  /// Saves snapshots and leaves.
  Future<void> close() async {
    if (_closing) return;
    _closing = true;
    for (final e in _entries) {
      await saveAndClose(_scope, e, sessions[e.id]);
    }
    if (mounted) Navigator.of(context).pop();
  }

  /// Grid layout (design page 14 layout menu).
  SlotGridLayout layout = SlotGridLayout.auto;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) unawaited(close());
      },
      // TEST-R4 page 14: the same chrome as the example (count, layout,
      // hint, "全部静音"); the App does not add media from here.
      child: VideoKitMultiViewScaffold(
        title: a(a.l.multiViewTitle),
        count: _entries.length,
        leading: VkIconButton(
          icon: t.icons.resolve('back'),
          semanticLabel: s.text('playerBack'),
          onPressed: () => unawaited(close()),
        ),
        onMuteAll: activeAudio == null ? null : () => unawaited(muteAll()),
        layout: layout,
        onLayoutChanged: (l) => setState(() => layout = l),
        grid: VideoKitSlotGrid(
          layout: layout,
          slots: [
            for (final (i, e) in _entries.indexed)
              if (sessions[e.id] case final session?)
                VideoKitSlot(
                  key: ValueKey(e.id),
                  session: session,
                  index: i + 1,
                  title: e.displayName,
                  pictureBuilder: _scope.backend.pictureBuilder,
                  onActivateAudio: (id) => unawaited(activateAudio(id)),
                  onTap: e.kind == MediaKind.video
                      ? () => unawaited(activateAudio(session.sessionId))
                      : null,
                  onRetry: () => unawaited(_bind(e, session)),
                ),
          ],
        ),
      ),
    );
  }
}
