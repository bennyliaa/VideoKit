import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/foundation.dart' show listEquals;
import 'package:flutter/gestures.dart' show kTouchSlop;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_badge.dart';
import '../common/vk_buttons.dart';
import '../common/vk_pressable.dart';
import '../common/vk_sheet_host.dart';
import '../common/vk_slider.dart';
import '../foundation/auto_hide.dart';
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
import '../foundation/selector.dart';
import '../host_action/host_action_bar.dart';
import '../l10n/vk_strings.dart';
import '../state_view/state_mapping.dart';
import '../state_view/state_view.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'media_surface.dart';
import 'picture_style.dart';
import 'player_controller.dart';
import 'track_settings_sheet.dart';
import 'vk_seek_bar.dart';

/// Panels the host can open through [VideoKitPlayerState.openPanel].
enum PlayerPanel { subtitles, audio, speed, more }

/// Player options (14 §5.1, §12 defaults).
@immutable
final class VideoKitPlayerOptions {
  /// Creates options.
  const VideoKitPlayerOptions({
    this.autoHideDelay = const Duration(seconds: 3),
    this.seekStepUs = 10000000,
    this.keyboardSeekStepUs = 5000000,
    this.keyboardLargeSeekStepUs = 30000000,
    this.seekGesture = true,
    this.zoomGesture = true,
    this.speeds = vkDefaultSpeeds,
    this.maxZoom = 8,
  });

  /// Controls auto-hide delay (3 s).
  final Duration autoHideDelay;

  /// Rewind/forward step (10 s).
  final int seekStepUs;

  /// Arrow-key seek (5 s).
  final int keyboardSeekStepUs;

  /// Shift+arrow seek (30 s).
  final int keyboardLargeSeekStepUs;

  /// Horizontal drag on the picture seeks when not zoomed.
  final bool seekGesture;

  /// Pinch zoom / pan.
  final bool zoomGesture;

  /// Offered speeds.
  final List<double> speeds;

  /// Maximum zoom factor.
  final double maxZoom;
}

/// UI-01 video player (14 §5.1, design pages 9–10).
///
/// Layers, bottom to top: picture (texture or [pictureBuilder]), gestures,
/// state view (UI-09), controls (top bar, host actions, seek bar, main and
/// secondary controls), host panel slot, panels/toasts, demo badge. The
/// session is the only state authority; the widget keeps only visual state.
class VideoKitPlayer extends StatefulWidget {
  /// Creates a player.
  const VideoKitPlayer({
    super.key,
    required this.session,
    this.title,
    this.subtitle,
    this.hostActions,
    this.hostPanel,
    this.onControlsVisibilityChanged,
    this.onFullscreenRequested,
    this.onEditRequested,
    this.onBack,
    this.onStateAction,
    this.pictureBuilder,
    this.resolveHostString,
    this.resolveHostIcon,
    this.options = const VideoKitPlayerOptions(),
  });

  /// Session (owned by the host).
  final VideoKitSession session;

  /// Display name from the host (display only).
  final String? title;

  /// Secondary info line (landscape top bar).
  final String? subtitle;

  /// Host actions; also settable through `session.updateHostActions`.
  final List<VideoKitHostAction>? hostActions;

  /// Host panel slot (03 §6), shown and hidden with the controls.
  final Widget Function(BuildContext context, bool controlsVisible)? hostPanel;

  /// Controls visibility changed.
  final ValueChanged<bool>? onControlsVisibilityChanged;

  /// Fullscreen toggled (the host performs the window change).
  final ValueChanged<bool>? onFullscreenRequested;

  /// Edit entry with the current position (µs); null hides the button.
  final ValueChanged<int>? onEditRequested;

  /// Back button; null hides it.
  final VoidCallback? onBack;

  /// State view actions the player cannot handle itself (retry → host
  /// re-binds, permission, other source).
  final ValueChanged<StateAction>? onStateAction;

  /// Picture without texture.
  final VideoKitPictureBuilder? pictureBuilder;

  /// Host string resolver (host action labels).
  final HostStringResolver? resolveHostString;

  /// Host resource icon resolver.
  final HostIconResolver? resolveHostIcon;

  /// Options.
  final VideoKitPlayerOptions options;

  @override
  State<VideoKitPlayer> createState() => VideoKitPlayerState();
}

/// State of [VideoKitPlayer]; doubles as the host handle (14 §4.1
/// `VideoKitPlayerHandle`) through a `GlobalKey<VideoKitPlayerState>`.
class VideoKitPlayerState extends State<VideoKitPlayer> {
  late PlayerController _c;
  final FocusNode _focus = FocusNode(debugLabel: 'VideoKitPlayer');
  MediaTransform? _gestureStart;
  Offset? _gestureFocal;
  int? _seekGestureBase;

  /// Shows the controls.
  void showControls() => _c.autoHide.show();

  /// Hides the controls (refused while a blocker is active).
  bool hideControls() => _c.autoHide.hide();

  /// Opens a panel.
  void openPanel(PlayerPanel panel) => switch (panel) {
    PlayerPanel.subtitles => _openTracks(TrackSettingsTab.subtitles),
    PlayerPanel.audio => _openTracks(TrackSettingsTab.audio),
    PlayerPanel.speed => _openTracks(TrackSettingsTab.speed),
    PlayerPanel.more => _openMore(),
  };

  String _host(String key) => widget.resolveHostString?.call(key) ?? key;

  PlayerController _create() => PlayerController(
    session: widget.session,
    autoHideDelay: widget.options.autoHideDelay,
    strings: () => VkStrings.of(context),
    hostLabel: _host,
    onControlsVisibilityChanged: widget.onControlsVisibilityChanged,
  );

  @override
  void initState() {
    super.initState();
    _c = _create();
    final actions = widget.hostActions;
    if (actions != null) unawaited(widget.session.updateHostActions(actions));
  }

  @override
  void didUpdateWidget(VideoKitPlayer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.session, widget.session)) {
      _c.dispose();
      _c = _create();
    } else {
      _c
        ..hostLabel = _host
        ..onControlsVisibilityChanged = widget.onControlsVisibilityChanged;
    }
    final actions = widget.hostActions;
    if (actions != null && actions != oldWidget.hostActions) {
      unawaited(widget.session.updateHostActions(actions));
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final a11y = MediaQuery.maybeAccessibleNavigationOf(context) ?? false;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _c.setBlocker(AutoHideBlocker.accessibleNavigation, a11y);
    });
  }

  @override
  void dispose() {
    _c.dispose();
    _focus.dispose();
    super.dispose();
  }

  // ------------------------------------------------------------- panels --

  void _openTracks(TrackSettingsTab tab) {
    final s = VkStrings.of(context);
    _c.sheets.show(
      VkSheetEntry(
        id: 'tracks',
        title: s.text('settingsTitle'),
        builder: (context) => TrackSettingsSheet(
          session: widget.session,
          initialTab: tab,
          speeds: widget.options.speeds,
          onCommand: (c) => unawaited(_c.send(c)),
        ),
      ),
    );
  }

  /// Host actions the host action bar could not show (reported after
  /// layout); they form the first group of the single "more" panel.
  List<String> _hostOverflowIds = const [];

  /// Player controls that did not fit in the bottom row.
  List<_ControlItem> _playerOverflow = const [];

  void _onHostOverflow(List<HostActionState> overflow) {
    final ids = [for (final a in overflow) a.action.actionId];
    if (listEquals(ids, _hostOverflowIds) || !mounted) return;
    setState(() => _hostOverflowIds = ids);
  }

  void _openMore() {
    final s = VkStrings.of(context);
    final t = VkTheme.of(context);
    final st = widget.session.state.value;
    final overflow = _playerOverflow;
    _c.sheets.show(
      VkSheetEntry(
        id: 'more',
        title: s.text('commonMore'),
        builder: (context) => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Group 1: host actions (14 §7.2 M0-B2 rule: one "more" only).
            VkSelector<VideoKitSessionState, List<HostActionState>>(
              listenable: widget.session.state,
              select: (x) => [
                for (final a in x.hostActions)
                  if (_hostOverflowIds.contains(a.action.actionId)) a,
              ],
              builder: (context, host) => host.isEmpty
                  ? const SizedBox.shrink()
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _MenuGroupHeader(s.text('hostActionMore')),
                        for (final a in host)
                          HostActionMenuItem(
                            state: a,
                            resolveString: widget.resolveHostString,
                            resolveIcon: widget.resolveHostIcon,
                            onPressed: (id) {
                              _c.sheets.close('more');
                              _c.requestHostAction(id);
                            },
                          ),
                        _MenuGroupHeader(s.text('moreGroupPlayer')),
                      ],
                    ),
            ),
            // Group 2: player secondary controls.
            for (final i in overflow)
              VkMenuItem(
                icon: i.icon,
                label: i.label,
                selected: i.selected,
                onPressed: i.onPressed == null
                    ? null
                    : () {
                        _c.sheets.close('more');
                        i.onPressed!();
                      },
              ),
            VkMenuItem(
              icon: t.icons.resolve('fit'),
              label: s.fitModeNotice(_fitLabel(s, st.transform.fitMode)),
              onPressed: () {
                _c.sheets.close('more');
                _cycleFit();
              },
            ),
          ],
        ),
      ),
    );
  }

  // ----------------------------------------------------------- commands --

  static String _fitLabel(VkStrings s, FitMode m) => switch (m) {
    FitMode.fit => s.text('fitModeFit'),
    FitMode.fill => s.text('fitModeFill'),
    FitMode.original => s.text('fitModeOriginal'),
  };

  void _cycleFit() {
    final st = widget.session.state.value;
    final next = FitMode
        .values[(st.transform.fitMode.index + 1) % FitMode.values.length];
    unawaited(
      _c.send(
        SetTransform(
          MediaTransform(fitMode: next, rotationDeg: st.transform.rotationDeg),
        ),
      ),
    );
    final s = VkStrings.of(context);
    _c.sheets.showToast(
      VkToastEntry(message: s.fitModeNotice(_fitLabel(s, next))),
    );
  }

  void _toggleFullscreen() {
    final fs = !widget.session.state.value.orientation.fullscreen;
    unawaited(_c.send(SetFullscreen(fs)));
    widget.onFullscreenRequested?.call(fs);
  }

  void _toggleMute() {
    unawaited(_c.send(SetMuted(!widget.session.state.value.muted)));
  }

  void _toggleOrientationLock() {
    final locked =
        widget.session.state.value.orientation.request ==
        OrientationRequest.locked;
    unawaited(
      _c.send(
        SetOrientation(
          locked ? OrientationRequest.auto : OrientationRequest.locked,
        ),
      ),
    );
  }

  void _rotate() {
    final t = widget.session.state.value.transform;
    unawaited(
      _c.send(
        SetTransform(t.copyWith(rotationDeg: (t.rotationDeg + 90) % 360)),
      ),
    );
  }

  void _onStateAction(StateAction a) {
    switch (a) {
      case StateAction.replay:
        unawaited(_c.send(const Play()));
      default:
        widget.onStateAction?.call(a);
    }
  }

  // ------------------------------------------------------------ gestures --

  void _scaleStart(ScaleStartDetails d) {
    final st = widget.session.state.value;
    _gestureStart = st.transform;
    _gestureFocal = d.localFocalPoint;
    _seekGestureBase = null;
  }

  void _scaleUpdate(ScaleUpdateDetails d, Size size) {
    final start = _gestureStart;
    final focal = _gestureFocal;
    if (start == null || focal == null || size.isEmpty) return;
    final delta = d.localFocalPoint - focal;
    if (d.pointerCount >= 2 && widget.options.zoomGesture) {
      final scale = (start.scale * d.scale).clamp(1.0, widget.options.maxZoom);
      _c.setGestureTransform(
        start.copyWith(
          scale: scale,
          panX: (start.panX + delta.dx / size.width).clamp(-1.0, 1.0),
          panY: (start.panY + delta.dy / size.height).clamp(-1.0, 1.0),
        ),
      );
    } else if (start.isZoomed && widget.options.zoomGesture) {
      _c.setGestureTransform(
        start.copyWith(
          panX: (start.panX + delta.dx / size.width).clamp(-1.0, 1.0),
          panY: (start.panY + delta.dy / size.height).clamp(-1.0, 1.0),
        ),
      );
    } else if (widget.options.seekGesture) {
      final st = widget.session.state.value;
      final duration = st.durationUs ?? 0;
      if (duration <= 0 || st.mediaKind != MediaKind.video) return;
      if (_seekGestureBase == null) {
        if (delta.dx.abs() < kTouchSlop || delta.dx.abs() < delta.dy.abs()) {
          return;
        }
        _seekGestureBase = st.seekingToUs ?? st.positionUs;
        _c.dragStart();
      }
      // Full width ≈ 90 s, at most the whole media.
      final span = math.min(duration, 90000000);
      final target = (_seekGestureBase! + delta.dx / size.width * span)
          .round()
          .clamp(0, duration);
      _c.dragUpdate(target);
    }
  }

  void _scaleEnd(ScaleEndDetails d) {
    final g = _c.gestureTransform;
    if (g != null) {
      unawaited(
        _c
            .send(SetTransform(g))
            .whenComplete(() => _c.setGestureTransform(null)),
      );
    }
    if (_seekGestureBase != null) {
      _c.dragEnd(_c.dragUs ?? _seekGestureBase!);
    }
    _gestureStart = null;
    _gestureFocal = null;
    _seekGestureBase = null;
  }

  // -------------------------------------------------------------- build --

  Map<ShortcutActivator, VoidCallback> _shortcuts() {
    final o = widget.options;
    final st = widget.session.state.value;
    return {
      const SingleActivator(LogicalKeyboardKey.space): _c.togglePlay,
      const SingleActivator(LogicalKeyboardKey.arrowLeft): () =>
          _c.seekBy(-o.keyboardSeekStepUs),
      const SingleActivator(LogicalKeyboardKey.arrowRight): () =>
          _c.seekBy(o.keyboardSeekStepUs),
      const SingleActivator(LogicalKeyboardKey.arrowLeft, shift: true): () =>
          _c.seekBy(-o.keyboardLargeSeekStepUs),
      const SingleActivator(LogicalKeyboardKey.arrowRight, shift: true): () =>
          _c.seekBy(o.keyboardLargeSeekStepUs),
      const SingleActivator(LogicalKeyboardKey.arrowUp): () =>
          unawaited(_c.send(SetVolume((st.volume + 0.1).clamp(0.0, 1.0)))),
      const SingleActivator(LogicalKeyboardKey.arrowDown): () =>
          unawaited(_c.send(SetVolume((st.volume - 0.1).clamp(0.0, 1.0)))),
      const SingleActivator(LogicalKeyboardKey.keyM): _toggleMute,
      const SingleActivator(LogicalKeyboardKey.keyF): _toggleFullscreen,
      const SingleActivator(LogicalKeyboardKey.escape): () {
        if (!_c.sheets.closeTop() && st.orientation.fullscreen) {
          _toggleFullscreen();
        }
      },
    };
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    _c.strings = () => VkStrings.of(context);
    return ValueListenableBuilder<VideoKitSessionState>(
      valueListenable: widget.session.state,
      builder: (context, st, _) => CallbackShortcuts(
        bindings: _shortcuts(),
        child: Focus(
          focusNode: _focus,
          child: VkSheetHost(
            controller: _c.sheets,
            child: ColoredBox(
              color: t.colors.playerCanvas,
              child: LayoutBuilder(
                builder: (context, c) =>
                    _layers(context, Size(c.maxWidth, c.maxHeight)),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _layers(BuildContext context, Size size) {
    final s = VkStrings.of(context);
    return ListenableBuilder(
      listenable: _c,
      builder: (context, _) {
        final visible = _c.autoHide.visible;
        final motion = VkTheme.of(context).animations.normal;
        final st = widget.session.state.value;
        final model = mapSessionState(
          phase: st.phase,
          error: st.error,
          mediaKind: st.mediaKind,
          hiddenForLock: st.hiddenForLock,
        );
        return Stack(
          children: [
            Positioned.fill(
              child: VkMediaSurface(
                session: widget.session,
                transformOverride: _c.gestureTransform,
                builder: widget.pictureBuilder,
              ),
            ),
            Positioned.fill(
              child: Semantics(
                container: true,
                label: s.text('playerPicture'),
                onTap: _c.autoHide.toggle,
                // The Semantics node above carries the tap for screen readers.
                child: GestureDetector(
                  excludeFromSemantics: true,
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    _focus.requestFocus();
                    _c.autoHide.toggle();
                  },
                  onDoubleTap: _cycleFit,
                  onScaleStart: _scaleStart,
                  onScaleUpdate: (d) => _scaleUpdate(d, size),
                  onScaleEnd: _scaleEnd,
                ),
              ),
            ),
            if (model != null)
              Positioned.fill(
                child: IgnorePointer(
                  ignoring: model.keepsPicture,
                  child: VideoKitStateView(
                    model: model,
                    onStateAction: _onStateAction,
                  ),
                ),
              ),
            Positioned.fill(
              child: IgnorePointer(
                ignoring: !visible,
                child: AnimatedOpacity(
                  opacity: visible ? 1 : 0,
                  duration: motion.duration,
                  curve: motion.curve,
                  child: ExcludeSemantics(
                    excluding: !visible,
                    child: MouseRegion(
                      onEnter: (_) =>
                          _c.setBlocker(AutoHideBlocker.hovered, true),
                      onExit: (_) =>
                          _c.setBlocker(AutoHideBlocker.hovered, false),
                      hitTestBehavior: HitTestBehavior.translucent,
                      child: Focus(
                        canRequestFocus: false,
                        skipTraversal: true,
                        onFocusChange: (f) =>
                            _c.setBlocker(AutoHideBlocker.focusInControls, f),
                        child: _controls(context, size, st),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            if (widget.hostPanel != null) _hostPanel(context, size, visible),
            if (widget.session.isDemo)
              PositionedDirectional(
                top: 0,
                start: 0,
                end: 0,
                child: SafeArea(
                  child: Padding(
                    padding: EdgeInsetsDirectional.only(
                      top: VkTheme.of(context).dimensions.controlBarHeight,
                    ),
                    child: const Center(child: DemoBadge()),
                  ),
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _hostPanel(BuildContext context, Size size, bool visible) {
    final t = VkTheme.of(context);
    final landscape = size.width > size.height;
    final motion = t.animations.normal;
    final child = AnimatedOpacity(
      opacity: visible ? 1 : 0,
      duration: motion.duration,
      curve: motion.curve,
      child: IgnorePointer(
        ignoring: !visible,
        child: widget.hostPanel!(context, visible),
      ),
    );
    return landscape
        ? PositionedDirectional(
            top: t.dimensions.controlBarHeight + t.dimensions.spacing16,
            bottom: t.dimensions.controlBarHeight * 2 + t.dimensions.spacing16,
            end: t.dimensions.spacing16,
            child: SafeArea(left: false, right: false, child: child),
          )
        : PositionedDirectional(
            start: 0,
            end: 0,
            bottom: t.dimensions.controlBarHeight * 4,
            child: child,
          );
  }

  // ----------------------------------------------------------- controls --

  List<_ControlItem> _secondary(BuildContext context, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final isVideo = st.mediaKind == MediaKind.video;
    final bound = st.phase.isBound;
    final locked = st.orientation.request == OrientationRequest.locked;
    final fs = st.orientation.fullscreen;
    return [
      if (isVideo)
        _ControlItem(
          id: 'speed',
          icon: t.icons.resolve('speed'),
          label: s.text('playerSpeed'),
          text: s.speedValue(
            VkFormat.number(s, st.speed, maxFractionDigits: 2),
          ),
          onPressed: bound ? () => _openTracks(TrackSettingsTab.speed) : null,
        ),
      if (isVideo)
        _ControlItem(
          id: 'subtitles',
          icon: t.icons.resolve('subtitles'),
          label: s.text('playerSubtitles'),
          selected: st.selectedSubtitleTrackId != null,
          onPressed: bound
              ? () => _openTracks(TrackSettingsTab.subtitles)
              : null,
        ),
      if (isVideo)
        _ControlItem(
          id: 'audio',
          icon: t.icons.resolve('audiotrack'),
          label: s.text('playerAudioTrack'),
          onPressed: bound ? () => _openTracks(TrackSettingsTab.audio) : null,
        ),
      if (isVideo)
        _ControlItem(
          id: 'volume',
          icon: t.icons.resolve(st.muted ? 'mute' : 'volume'),
          label: s.text(st.muted ? 'playerUnmute' : 'playerMute'),
          onPressed: bound ? _toggleMute : null,
        ),
      _ControlItem(
        id: 'lock',
        icon: t.icons.resolve('orientationlock'),
        label: s.text(
          locked ? 'playerUnlockOrientation' : 'playerLockOrientation',
        ),
        selected: locked,
        onPressed: _toggleOrientationLock,
      ),
      _ControlItem(
        id: 'rotate',
        icon: t.icons.resolve('rotate'),
        label: s.text('playerRotate'),
        onPressed: bound ? _rotate : null,
      ),
      if (widget.onEditRequested != null && isVideo)
        _ControlItem(
          id: 'edit',
          icon: t.icons.resolve('edit'),
          label: s.text('playerEdit'),
          onPressed: bound
              ? () => widget.onEditRequested!(st.positionUs)
              : null,
        ),
      _ControlItem(
        id: 'fullscreen',
        icon: t.icons.resolve(fs ? 'exitfullscreen' : 'fullscreen'),
        label: s.text(fs ? 'playerExitFullscreen' : 'playerFullscreen'),
        onPressed: _toggleFullscreen,
      ),
    ];
  }

  Widget _controlButton(BuildContext context, _ControlItem i) {
    final t = VkTheme.of(context);
    final style = t.components.buttonIcon;
    if (i.text != null) {
      return VkPressable(
        style: style,
        semanticLabel: i.label,
        semanticValue: i.text,
        onPressed: i.onPressed,
        builder: (context, box) => Text(
          i.text!,
          style: t.typography.label.copyWith(
            color: t.colors.playerControlsContent,
          ),
        ),
      );
    }
    return VkIconButton(
      icon: i.icon,
      semanticLabel: i.label,
      selected: i.selected,
      onPressed: i.onPressed,
      style: _onPictureStyle(context),
    );
  }

  VkStateStyleBox _onPictureStyle(BuildContext context) =>
      vkOnPictureIconStyle(context);

  Widget _controls(BuildContext context, Size size, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final layout = VkLayoutClass.fromWidth(size.width);
    final landscape = size.width > size.height;
    final collapse = VkLayoutClass.collapseSecondary(
      MediaQuery.textScalerOf(context),
    );
    final glass = t.drawables.glassPlayer;
    final isVideo = st.mediaKind == MediaKind.video;
    final duration = st.durationUs ?? 0;
    final position = _c.dragUs ?? st.seekingToUs ?? st.positionUs;
    final white = t.typography.timecode.copyWith(
      color: t.colors.playerControlsContent,
    );
    final secondary = _secondary(context, st);
    final pictureStyle = _onPictureStyle(context);

    // Fit secondary controls into the row; the rest goes to "more".
    final rowWidth = size.width - d.spacing16 * 2;
    var slots = (rowWidth / (d.targetMin + d.spacing4)).floor();
    if (landscape) slots = (slots / 2).floor();
    if (collapse) slots = math.min(slots, 3);
    final fits = secondary.length <= slots;
    final shown = fits
        ? secondary
        : [
            ...secondary.where((i) => i.id == 'fullscreen'),
            ...secondary
                .where((i) => i.id != 'fullscreen')
                .take(math.max(0, slots - 2)),
          ];
    final overflow = secondary.where((i) => !shown.contains(i)).toList();
    _playerOverflow = overflow;
    final shownOrdered = secondary.where(shown.contains).toList();

    final hostBar = VkSelector<VideoKitSessionState, List<HostActionState>>(
      listenable: widget.session.state,
      select: (x) => x.hostActions,
      builder: (context, actions) => actions.isEmpty
          ? const SizedBox.shrink()
          : HostActionBar(
              actions: actions,
              axis: landscape ? Axis.horizontal : Axis.vertical,
              showLabels: true,
              resolveString: widget.resolveHostString,
              resolveIcon: widget.resolveHostIcon,
              onActionPressed: _c.requestHostAction,
              showOverflowButton: false,
              onOverflowChanged: _onHostOverflow,
            ),
    );

    final topBar = DecoratedBox(
      decoration: BoxDecoration(gradient: glass.gradient(fromTop: true)),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4,
          ),
          child: Row(
            children: [
              if (widget.onBack != null)
                VkIconButton(
                  icon: t.icons.resolve('back'),
                  semanticLabel: s.text('playerBack'),
                  onPressed: widget.onBack,
                  style: pictureStyle,
                ),
              SizedBox(width: d.spacing8),
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (widget.title != null)
                      Text(
                        widget.title!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: t.typography.title.copyWith(
                          color: t.colors.playerControlsContent,
                        ),
                      ),
                    if (widget.subtitle != null && landscape)
                      Text(
                        widget.subtitle!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: t.typography.caption.copyWith(
                          color: t.colors.playerControlsContent.withValues(
                            alpha: 0.72,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              if (landscape)
                ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: size.width * 0.45),
                  child: hostBar,
                ),
              VkIconButton(
                icon: t.icons.resolve('more'),
                semanticLabel: s.text('commonMore'),
                pending: st.hostActions.any(
                  (a) =>
                      a.isPending &&
                      _hostOverflowIds.contains(a.action.actionId),
                ),
                onPressed: _openMore,
                style: pictureStyle,
              ),
            ],
          ),
        ),
      ),
    );

    final playing =
        st.phase == SessionPhase.playing ||
        (st.playWhenReady && st.phase == SessionPhase.buffering);
    final canPlay =
        st.phase.isBound &&
        (isVideo || st.mediaKind == MediaKind.imageAnimated);
    final step = widget.options.seekStepUs ~/ 1000000;
    final playButton = VkIconButton(
      icon: playing ? t.icons.pause : t.icons.play,
      semanticLabel: s.text(playing ? 'playerPause' : 'playerPlay'),
      onPressed: canPlay ? _c.togglePlay : null,
      iconSize: landscape ? d.icon24 : d.targetMin * 0.75,
      style: landscape
          ? pictureStyle
          : t.components.buttonIcon.copyWithAll(
              (b) => b.copyWith(
                background: t.colors.playerControlsContent.withValues(
                  alpha: 0.92,
                ),
                content: t.colors.playerCanvas,
                minSize: d.targetMin * 1.5,
              ),
            ),
    );
    final rewind = VkIconButton(
      icon: t.icons.resolve('seekback'),
      semanticLabel: s.rewind(step),
      onPressed: isVideo && st.phase.isBound
          ? () => _c.seekBy(-widget.options.seekStepUs)
          : null,
      style: pictureStyle,
    );
    final forward = VkIconButton(
      icon: t.icons.resolve('seekforward'),
      semanticLabel: s.forward(step),
      onPressed: isVideo && st.phase.isBound
          ? () => _c.seekBy(widget.options.seekStepUs)
          : null,
      style: pictureStyle,
    );
    final seekBar = isVideo
        ? VkSeekBar(
            positionUs: position,
            durationUs: duration,
            bufferedUs: st.bufferedUs,
            stepUs: widget.options.seekStepUs,
            onDragStart: _c.dragStart,
            onDragUpdate: _c.dragUpdate,
            onDragEnd: st.phase.isBound ? _c.dragEnd : null,
          )
        : const SizedBox.shrink();
    final volume = isVideo && layout != VkLayoutClass.compact && landscape
        ? SizedBox(
            width: d.targetMin * 2.5,
            child: VkSlider(
              onPicture: true,
              value: st.muted ? 0 : st.volume,
              semanticLabel: s.text('playerVolume'),
              semanticValue: (v) => VkFormat.percent(s, v),
              onChangeEnd: st.phase.isBound
                  ? (v) => unawaited(_c.send(SetVolume(v)))
                  : null,
            ),
          )
        : null;
    final bottom = DecoratedBox(
      decoration: BoxDecoration(gradient: glass.gradient(fromTop: false)),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsetsDirectional.fromSTEB(
            d.spacing16,
            d.spacing24,
            d.spacing16,
            d.spacing8,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (!landscape && isVideo)
                Row(
                  children: [
                    Text(VkFormat.timecode(position), style: white),
                    const Spacer(),
                    Text(VkFormat.timecode(duration), style: white),
                  ],
                ),
              if (landscape && isVideo)
                Row(
                  children: [
                    Text(VkFormat.timecode(position), style: white),
                    SizedBox(width: d.spacing12),
                    Expanded(child: seekBar),
                    SizedBox(width: d.spacing12),
                    Text(VkFormat.timecode(duration), style: white),
                  ],
                )
              else
                seekBar,
              if (!landscape)
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    rewind,
                    SizedBox(width: d.spacing24),
                    playButton,
                    SizedBox(width: d.spacing24),
                    forward,
                  ],
                ),
              Row(
                children: [
                  if (landscape) ...[
                    playButton,
                    rewind,
                    forward,
                    ?volume,
                    const Spacer(),
                  ],
                  for (final i in shownOrdered)
                    landscape
                        ? _controlButton(context, i)
                        : Expanded(
                            child: Center(child: _controlButton(context, i)),
                          ),
                ],
              ),
            ],
          ),
        ),
      ),
    );

    return Stack(
      children: [
        PositionedDirectional(top: 0, start: 0, end: 0, child: topBar),
        if (!landscape)
          PositionedDirectional(
            end: d.spacing12,
            bottom: d.controlBarHeight * 3.6,
            child: hostBar,
          ),
        PositionedDirectional(start: 0, end: 0, bottom: 0, child: bottom),
      ],
    );
  }
}

/// `VkStateStyle<VkBoxStyle>` alias used by the player.
typedef VkStateStyleBox = VkStateStyle<VkBoxStyle>;

@immutable
final class _ControlItem {
  const _ControlItem({
    required this.id,
    required this.icon,
    required this.label,
    required this.onPressed,
    this.text,
    this.selected = false,
  });

  final String id;
  final IconData icon;
  final String label;
  final String? text;
  final bool selected;
  final VoidCallback? onPressed;
}

/// Group title inside the "more" panel.
class _MenuGroupHeader extends StatelessWidget {
  const _MenuGroupHeader(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.fromSTEB(
        d.spacing16,
        d.spacing12,
        d.spacing16,
        d.spacing4,
      ),
      child: Semantics(
        header: true,
        child: Text(
          text,
          style: t.typography.label.copyWith(color: t.colors.textSecondary),
        ),
      ),
    );
  }
}
