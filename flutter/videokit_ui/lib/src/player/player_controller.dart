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
      case ErrorRaised() ||
          PlaybackEnded() ||
          SourceReleased() ||
          TransientNotice():
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
    dragUs = us;
    dispatcher.seekDrag(us);
    seekPreview.request(us);
    notifyListeners();
  }

  /// Seek bar released: one final seek.
  void dragEnd(int us) {
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

  /// Requests navigation and shows a notice when unavailable.
  Future<void> requestNavigation(NavigationDirection direction) async {
    final r = await session.requestNavigation(direction);
    if (_disposed) return;
    if (r == NavigationResult.unavailable) {
      sheets.showToast(
        VkToastEntry(message: strings().text('navigationUnavailable')),
      );
    }
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
