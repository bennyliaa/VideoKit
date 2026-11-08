import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_sheet_host.dart';
import '../foundation/auto_hide.dart';
import '../foundation/command_dispatcher.dart';
import '../l10n/vk_strings.dart';
import 'seek_preview.dart';

/// Internal controller of `VideoKitPlayer` (14 §4.1): combines the session
/// state (single source of truth) with UI-local visual state (drag preview,
/// gesture zoom, panels, controls visibility). Not exported.
class PlayerController extends ChangeNotifier {
  /// Creates a controller for [session].
  PlayerController({
    required this.session,
    required Duration autoHideDelay,
    required this.strings,
    required this.hostLabel,
    this.onControlsVisibilityChanged,
    this.previewFrames = true,
  }) : autoHide = AutoHidePolicy(delay: autoHideDelay) {
    dispatcher = CommandDispatcher(
      execute: session.execute,
      onFeedback: _onFeedback,
      requestHostAction: session.requestHostAction,
    );
    session.state.addListener(_onState);
    autoHide.addListener(_onVisibility);
    sheets.addListener(_onSheets);
    _events = session.events.listen(_onEvent);
    _onState();
    session.setControlsVisible(autoHide.visible);
  }

  /// Session.
  final VideoKitSession session;

  /// Whether a seek drag asks for preview frames (`captureThumbnail`);
  /// false for slow sources (04A P6), set by the widget.
  bool previewFrames;

  /// Strings resolver (refreshed by the widget when the locale changes).
  VkStrings Function() strings;

  /// Host label resolver for host action names.
  String Function(String key) hostLabel;

  /// Host callback for visibility changes.
  ValueChanged<bool>? onControlsVisibilityChanged;

  /// Auto-hide policy.
  final AutoHidePolicy autoHide;

  /// Panels and toasts.
  final VkSheetController sheets = VkSheetController();

  /// Command dispatch (14 §4.3).
  late final CommandDispatcher dispatcher;

  StreamSubscription<VideoKitEvent>? _events;
  bool _disposed = false;

  /// Local seek-bar drag position, while dragging.
  int? dragUs;

  /// Largest preview frame requested while dragging (px).
  static const int previewMaxWidth = 320;

  /// See [previewMaxWidth].
  static const int previewMaxHeight = 180;

  /// Preview frames while dragging (throttled `captureThumbnail`).
  late final SeekPreviewFrames seekPreview = SeekPreviewFrames(
    capture: (us) =>
        session.captureThumbnail(us, previewMaxWidth, previewMaxHeight),
  );

  /// Gesture zoom in progress (applied before `SetTransform` commits).
  MediaTransform? gestureTransform;

  void _onState() {
    final st = session.state.value;
    autoHide
      ..setBlocker(AutoHideBlocker.notPlaying, st.phase != SessionPhase.playing)
      ..setBlocker(
        AutoHideBlocker.hostActionPending,
        st.hostActions.any((a) => a.isPending),
      );
  }

  void _onVisibility() {
    final v = autoHide.visible;
    // R4-01: controls hidden while a drag is open (a host hide) end the
    // drag, so the progress display never stays frozen on it.
    final drag = dragUs;
    if (!v && drag != null) dragEnd(drag);
    session.setControlsVisible(v);
    onControlsVisibilityChanged?.call(v);
    notifyListeners();
  }

  void _onSheets() {
    autoHide.setBlocker(AutoHideBlocker.panelOpen, sheets.hasPanel);
  }

  void _onEvent(VideoKitEvent e) {
    if (_disposed) return;
    final s = strings();
    switch (e) {
      case HostActionFailed(:final actionId, :final messageKey):
        final action = session.state.value.hostActions
            .where((a) => a.action.actionId == actionId)
            .map((a) => hostLabel(a.action.labelKey))
            .firstOrNull;
        sheets.showToast(
          VkToastEntry(
            message: messageKey != null
                ? hostLabel(messageKey)
                : s.hostActionFailed(action ?? actionId),
            actionLabel: s.text('commonRetry'),
            onAction: () => requestHostAction(actionId),
          ),
        );
      case TransientNotice(:final code):
        final message = s.notice(code);
        if (message != null) sheets.showToast(VkToastEntry(message: message));
      case ErrorRaised() || PlaybackEnded() || SourceReleased():
        break;
    }
  }

  void _onFeedback(DispatchFeedback f) {
    if (_disposed) return;
    final s = strings();
    switch (f) {
      case RejectedFeedback(:final error):
        sheets.showToast(VkToastEntry(message: s.error(error.code)));
      case UnsupportedFeedback():
        sheets.showToast(VkToastEntry(message: s.text('commandUnavailable')));
      case SessionReleasedFeedback():
        notifyListeners();
    }
  }

  /// Sets a blocker from widget-level input (focus, hover, a11y, drag).
  void setBlocker(AutoHideBlocker b, bool active) =>
      autoHide.setBlocker(b, active);

  /// Sends [command] through the dispatcher and restarts the auto-hide timer.
  Future<VideoKitCommandResult?> send(VideoKitCommand command) {
    autoHide.kick();
    return dispatcher.dispatch(command);
  }

  /// Play/pause toggle with last-intent merging.
  void togglePlay() {
    autoHide.kick();
    final st = session.state.value;
    final playing = st.phase == SessionPhase.playing || st.playWhenReady;
    unawaited(dispatcher.setPlaying(!playing));
  }

  /// Relative seek clamped to the media.
  void seekBy(int deltaUs) {
    final st = session.state.value;
    final d = st.durationUs ?? 0;
    final base = st.seekingToUs ?? st.positionUs;
    autoHide.kick();
    unawaited(dispatcher.seekEnd((base + deltaUs).clamp(0, d)));
  }

  /// Seek bar drag started.
  void dragStart() {
    autoHide.setBlocker(AutoHideBlocker.dragging, true);
  }

  /// Seek bar drag preview (throttled preview seeks).
  void dragUpdate(int us) {
    if (_disposed) return;
    dragUs = us;
    dispatcher.seekDrag(us);
    // 04A P6: slow sources show only the time bubble while dragging.
    if (previewFrames) seekPreview.request(us);
    notifyListeners();
  }

  /// Seek bar released: one final seek.
  void dragEnd(int us) {
    if (_disposed) return;
    dragUs = null;
    seekPreview.cancel();
    autoHide.setBlocker(AutoHideBlocker.dragging, false);
    unawaited(dispatcher.seekEnd(us));
    notifyListeners();
  }

  /// Requests a host action.
  void requestHostAction(String actionId) {
    autoHide.kick();
    unawaited(dispatcher.requestHostAction(actionId));
  }

  bool _navigating = false;

  /// Whether a navigation request is waiting for the host.
  bool get navigating => _navigating;

  /// Requests navigation (M2: one request at a time; repeated swipes or
  /// taps while the host decides are dropped) and shows a notice when the
  /// host has nothing more or failed (the Kit applies the 3 s timeout, 14
  /// §12, and reports it as `failed`).
  Future<NavigationResult?> requestNavigation(
    NavigationDirection direction,
  ) async {
    if (_navigating || _disposed) return null;
    _navigating = true;
    NavigationResult r;
    try {
      r = await session.requestNavigation(direction);
    } on Object {
      r = NavigationResult.failed;
    } finally {
      _navigating = false;
    }
    if (_disposed) return r;
    final key = switch (r) {
      NavigationResult.unavailable => 'navigationUnavailable',
      NavigationResult.failed => 'navigationFailed',
      NavigationResult.accepted => null,
    };
    if (key != null) {
      sheets.showToast(VkToastEntry(message: strings().text(key)));
    }
    return r;
  }

  /// Local gesture transform (scale/pan) while pinching.
  void setGestureTransform(MediaTransform? t) {
    gestureTransform = t;
    notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    session.state.removeListener(_onState);
    unawaited(_events?.cancel());
    seekPreview.dispose();
    autoHide.dispose();
    sheets.dispose();
    dispatcher.dispose();
    super.dispose();
  }
}
