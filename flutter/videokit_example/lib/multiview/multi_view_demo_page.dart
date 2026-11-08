import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../gallery/gallery_text.dart';

/// Kind of a demo slot.
enum DemoSlotKind {
  /// Playing video.
  video,

  /// Static image.
  image,

  /// Animated image.
  animated,

  /// Unsupported source (single-slot error).
  unsupported,

  /// Video that buffers.
  buffering,
}

/// One slot of the demo (host side state).
final class DemoSlot {
  DemoSlot(this.number, this.kind, this.session);

  /// Stable 1-based number (title, media token).
  final int number;

  /// Kind.
  final DemoSlotKind kind;

  /// Session.
  final VideoKitSession session;

  /// Paused by the host to free a decoder.
  bool pausedForResources = false;

  /// Low resolution (host degradation).
  bool lowResolution = false;

  /// No decoder was available: static placeholder, no automatic retry
  /// (07 §3).
  bool placeholder = false;

  /// Session events (notices).
  StreamSubscription<VideoKitEvent>? events;

  /// Stops listening and closes the session.
  Future<void> close() async {
    // Close first: awaiting the cancel of a Fake event stream can wait for
    // the session, so it must not hold up the release.
    unawaited(events?.cancel());
    events = null;
    await session.close();
  }
}

/// Order in which "添加媒体" adds kinds (design page 14 mix).
const List<DemoSlotKind> demoSlotPattern = [
  DemoSlotKind.video,
  DemoSlotKind.video,
  DemoSlotKind.image,
  DemoSlotKind.unsupported,
  DemoSlotKind.video,
  DemoSlotKind.buffering,
  DemoSlotKind.video,
  DemoSlotKind.animated,
  DemoSlotKind.video,
  DemoSlotKind.video,
  DemoSlotKind.video,
  DemoSlotKind.video,
];

/// UI-05 `VideoKitSlotGrid` driven by the Dart Fake (M0-B3 item 4). The
/// page plays the host: it owns the audio epoch (07 §4), mutes all, and
/// applies degradation above [suggestedConcurrent] videos.
class MultiViewDemoPage extends StatefulWidget {
  /// Creates the page.
  const MultiViewDemoPage({super.key, this.initialCount});

  /// Initial slot count (default 4 on compact, 9 on wider screens).
  final int? initialCount;

  /// Concurrent videos the demo "device" suggests.
  static const int suggestedConcurrent = 6;

  /// Video decoders the demo "device" has (Fake budget, M3): binds beyond
  /// it are denied and the slot shows a placeholder.
  static const int decoderBudget = 7;

  @override
  State<MultiViewDemoPage> createState() => MultiViewDemoPageState();
}

/// State (public for tests).
class MultiViewDemoPageState extends State<MultiViewDemoPage>
    with SingleTickerProviderStateMixin {
  late final FakeVideoKit kit = FakeVideoKit(
    videoDecoderBudget: MultiViewDemoPage.decoderBudget,
  );

  /// Single audio source (07 §4 epoch rules).
  final VideoKitAudioCoordinator audio = VideoKitAudioCoordinator();

  /// Slots in grid order.
  final List<DemoSlot> slots = [];

  /// Slot grid layout.
  SlotGridLayout layout = SlotGridLayout.auto;

  /// Session ID with audio, if any.
  String? get activeAudio => audio.active;

  int _next = 1;
  bool _started = false;

  @override
  void initState() {
    super.initState();
    kit.clock.attachTicker(this);
    audio.addListener(_onAudio);
  }

  void _onAudio() {
    if (mounted) setState(() {});
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_started) return;
    _started = true;
    final compact =
        VkLayoutClass.fromWidth(MediaQuery.sizeOf(context).width) ==
        VkLayoutClass.compact;
    final count = widget.initialCount ?? (compact ? 4 : 9);
    unawaited(_addMany(count));
  }

  Future<void> _addMany(int count) async {
    for (var i = 0; i < count; i++) {
      await add();
    }
    if (slots.isNotEmpty && mounted) {
      await activateAudio(slots.first.session.sessionId);
    }
  }

  /// Adds one slot (up to 12).
  Future<void> add() async {
    if (slots.length >= VideoKitSlotGrid.maxSlots) return;
    final number = _next++;
    final kind = demoSlotPattern[(number - 1) % demoSlotPattern.length];
    final s = await kit.createSession(
      VideoKitSessionConfig(debugLabel: 'slot$number'),
    );
    if (!mounted) {
      await s.close();
      return;
    }
    final slot = DemoSlot(number, kind, s);
    slot.events = s.events.listen((e) => _onEvent(slot, e));
    setState(() => slots.add(slot));
    unawaited(_bind(slot));
    _applyBudget();
  }

  Future<void> _bind(DemoSlot slot) async {
    final (mediaKind, scenario) = switch (slot.kind) {
      DemoSlotKind.video => (MediaKind.video, 'normal'),
      DemoSlotKind.image => (MediaKind.imageStatic, 'normal'),
      DemoSlotKind.animated => (MediaKind.imageAnimated, 'normal'),
      DemoSlotKind.unsupported => (MediaKind.video, 'unsupported'),
      DemoSlotKind.buffering => (MediaKind.video, 'buffering'),
    };
    final r = await slot.session.bind(
      VideoKitMediaSource(
        mediaToken: 'slot-${slot.number}',
        mediaKind: mediaKind,
        sourceRef: DemoSourceRef(scenario),
      ),
    );
    if (!mounted) return;
    // 07 §3: no decoder left → placeholder; nothing retries by itself.
    final denied =
        r is Rejected && r.error.code == ErrorCode.decoderResourceExhausted;
    if (denied != slot.placeholder) setState(() => slot.placeholder = denied);
    if (denied || slot.pausedForResources) return;
    if (mediaKind != MediaKind.imageStatic) {
      await slot.session.execute(const SetMuted(true));
      await slot.session.execute(const Play());
    }
  }

  bool _isVideo(DemoSlot s) =>
      s.kind == DemoSlotKind.video || s.kind == DemoSlotKind.buffering;

  /// Host degradation: beyond the suggested count the oldest videos pause
  /// (07 §3); the audio slot is never the one paused.
  void _applyBudget() {
    final videos = slots.where(_isVideo).toList();
    final over = videos.length - MultiViewDemoPage.suggestedConcurrent;
    var paused = 0;
    for (final s in videos) {
      final pause = paused < over && s.session.sessionId != activeAudio;
      if (pause) paused++;
      if (pause != s.pausedForResources) {
        s.pausedForResources = pause;
        unawaited(s.session.execute(pause ? const Pause() : const Play()));
      }
      // One slot plays at low resolution once the grid is crowded.
      s.lowResolution = videos.length > 4 && identical(s, videos.last);
    }
    if (mounted) setState(() {});
  }

  /// Pausing count for the notice.
  int get pausedCount => slots.where((s) => s.pausedForResources).length;

  /// Makes [sessionId] the only audio source (07 §4, via [audio]).
  Future<void> activateAudio(String sessionId) async {
    final slot = slots
        .where((s) => s.session.sessionId == sessionId)
        .firstOrNull;
    if (slot == null) return;
    await audio.activate(slot.session);
    // The audio slot is never the paused one: re-run the budget.
    _applyBudget();
  }

  /// Mutes everything; the user picks a new audio source afterwards.
  Future<void> muteAll() => audio.muteAll([for (final s in slots) s.session]);

  void _onEvent(DemoSlot slot, VideoKitEvent e) {
    if (e is! TransientNotice || !mounted) return;
    final text = VkStrings.of(context).notice(e.code);
    if (text == null) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(text)));
  }

  void _onTap(DemoSlot slot) {
    if (slot.placeholder) {
      // The user asks once more (no automatic loop).
      unawaited(_bind(slot));
      return;
    }
    if (slot.pausedForResources) {
      // Resume this one; the budget pauses another instead.
      final other = slots.where(
        (s) =>
            _isVideo(s) &&
            !s.pausedForResources &&
            s.session.sessionId != activeAudio &&
            !identical(s, slot),
      );
      if (other.isNotEmpty) {
        other.first.pausedForResources = true;
        unawaited(other.first.session.execute(const Pause()));
      }
      slot.pausedForResources = false;
      unawaited(slot.session.execute(const Play()));
      setState(() {});
      return;
    }
    if (slot.kind == DemoSlotKind.video ||
        slot.kind == DemoSlotKind.buffering) {
      unawaited(activateAudio(slot.session.sessionId));
    }
  }

  /// Removes [slot] and closes its session.
  void remove(DemoSlot slot) {
    setState(() => slots.remove(slot));
    audio.onReleased(slot.session.sessionId);
    _applyBudget();
    unawaited(
      slot.close().then((_) {
        // Its decoder is free now: one placeholder gets one more try.
        final waiting = slots.where((s) => s.placeholder).firstOrNull;
        if (mounted && waiting != null) unawaited(_bind(waiting));
      }),
    );
  }

  @override
  void dispose() {
    audio
      ..removeListener(_onAudio)
      ..dispose();
    for (final s in slots) {
      unawaited(s.close());
    }
    kit.clock.detachTicker();
    unawaited(kit.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final g = GalleryText.of(context);
    final paused = pausedCount;
    // Design page 14 chrome is the shared `VideoKitMultiViewScaffold` (the
    // App uses the same one); this page only plays the host.
    return VideoKitMultiViewScaffold(
      count: slots.length,
      notice: paused > 0
          ? g(
              g.l.multiViewNotice(
                MultiViewDemoPage.suggestedConcurrent,
                paused,
              ),
            )
          : null,
      onMuteAll: activeAudio == null ? null : muteAll,
      onAdd: () => unawaited(add()),
      layout: layout,
      onLayoutChanged: (l) => setState(() => layout = l),
      grid: VideoKitSlotGrid(
        layout: layout,
        slots: [
          for (final (i, slot) in slots.indexed)
            VideoKitSlot(
              key: ValueKey(slot.session.sessionId),
              session: slot.session,
              index: i + 1,
              title: g(g.l.demoSlotTitle(slot.number)),
              degradation: slot.placeholder
                  ? SlotDegradation.placeholder
                  : slot.pausedForResources
                  ? SlotDegradation.pausedForResources
                  : (slot.lowResolution ? SlotDegradation.lowResolution : null),
              pictureBuilder: (context, session) =>
                  DemoSessionPicture(session: session),
              onActivateAudio: (id) => unawaited(activateAudio(id)),
              onTap: () => _onTap(slot),
              onRetry: () => unawaited(_bind(slot)),
              onRemove: () => remove(slot),
            ),
        ],
      ),
    );
  }
}
