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
import '../export/export_panel.dart' show vkCodecName;
import '../foundation/audio_grant.dart';
import '../foundation/auto_hide.dart';
import '../foundation/controls_policy.dart';
import '../foundation/format.dart';
import '../foundation/layout_class.dart';
import '../foundation/selector.dart';
import '../host_action/host_action_bar.dart';
import '../l10n/vk_strings.dart';
import '../state_view/state_mapping.dart';
import '../state_view/state_view.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'media_info_sheet.dart';
import 'media_surface.dart';
import 'picture_style.dart';
import 'player_controller.dart';
import 'seek_preview.dart';
import 'track_settings_sheet.dart';
import 'vk_seek_bar.dart';

/// Panels the host can open through [VideoKitPlayerState.openPanel].
enum PlayerPanel { subtitles, audio, speed, more, mediaInfo }

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
    this.grantAudio = true,
  });

  /// TEST-R3 R3-01 (04A A1): after a successful bind the player grants
  /// itself the audio (`SetActiveAudio(true, epoch)`). Hosts that coordinate
  /// audio across several sessions turn this off.
  final bool grantAudio;

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
  /// Whether a panel (settings, more, 参数 …) is open. Hosts with their own
  /// back handling check it first: the back press then only closes the
  /// panel (TEST-R2 R2-01).
  bool get hasOpenPanel => _c.sheets.hasPanel;

  late PlayerController _c;
  VkSingleAudioGrant? _audio;
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
    PlayerPanel.mediaInfo => _openMediaInfo(),
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
    _audio = widget.options.grantAudio
        ? VkSingleAudioGrant(widget.session)
        : null;
    final actions = widget.hostActions;
    if (actions != null) unawaited(widget.session.updateHostActions(actions));
  }

  @override
  void didUpdateWidget(VideoKitPlayer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.session, widget.session)) {
      _c.dispose();
      _c = _create();
      _audio?.dispose();
      _audio = widget.options.grantAudio
          ? VkSingleAudioGrant(widget.session)
          : null;
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
    _audio?.dispose();
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

  /// "参数" (design page 9): the session's `mediaInfo`.
  void _openMediaInfo() {
    final s = VkStrings.of(context);
    _c.sheets.show(
      VkSheetEntry(
        id: 'mediaInfo',
        title: s.text('playerMediaInfo'),
        builder: (context) => MediaInfoSheet(session: widget.session),
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
            VkMenuItem(
              icon: t.icons.resolve('info'),
              label: s.text('playerMediaInfo'),
              onPressed: () {
                _c.sheets.close('more');
                _openMediaInfo();
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
          capabilityHelp: widget.onStateAction != null,
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
              // TEST-R2 R2-05: hidden controls ignore taps except the seek bar,
              // which stays hit-testable at its final position (see _controls).
              child: IgnorePointer(
                ignoring: false,
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
                        child: _controls(
                          context,
                          size,
                          st,
                          blocked:
                              vkControlsMode(model, st) !=
                              VkControlsMode.normal,
                          minimal:
                              vkControlsMode(model, st) ==
                              VkControlsMode.minimal,
                          hidden: !visible,
                        ),
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
          text: VkFormat.speed(s, st.speed),
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

  /// Portrait big play key: light disc with dark icon; disabled is a faint
  /// disc with a faint icon (R1-02: errors must not look playable).
  static VkStateStyleBox _bigPlayStyle(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final light = t.colors.playerControlsContent;
    final all = t.components.buttonIcon.copyWithAll(
      (b) => b.copyWith(
        background: light.withValues(alpha: 0.92),
        content: t.colors.playerCanvas,
        minSize: d.targetMin * 1.5,
      ),
    );
    return VkStateStyleBox(
      normal: all.normal,
      pressed: all.pressed,
      focused: all.focused,
      disabled: all.disabled.copyWith(
        background: light.withValues(alpha: 0.16),
        content: light.withValues(alpha: 0.38),
      ),
      selected: all.selected,
      hovered: all.hovered,
    );
  }

  Widget _controlButton(
    BuildContext context,
    _ControlItem i, {
    bool enabled = true,
  }) {
    final t = VkTheme.of(context);
    final style = t.components.buttonIcon;
    final onPressed = enabled ? i.onPressed : null;
    final content = t.colors.playerControlsContent;
    if (i.text != null) {
      return VkPressable(
        style: style,
        semanticLabel: i.label,
        semanticValue: i.text,
        onPressed: onPressed,
        builder: (context, box) => Text(
          i.text!,
          style: t.typography.label.copyWith(
            color: onPressed == null
                ? content.withValues(alpha: 0.38)
                : content,
          ),
        ),
      );
    }
    return VkIconButton(
      icon: i.icon,
      semanticLabel: i.label,
      selected: i.selected,
      onPressed: onPressed,
      style: _onPictureStyle(context),
    );
  }

  VkStateStyleBox _onPictureStyle(BuildContext context) =>
      vkOnPictureIconStyle(context);

  /// "1920 × 1080 · H.264" from the media info (design page 10), or null.
  static String? _mediaSummary(VkStrings s, VideoKitSessionState st) {
    final info = st.mediaInfo;
    final w = info?.width;
    final h = info?.height;
    final codec = info?.videoCodec;
    if (w == null || h == null || w <= 0 || codec == null) return null;
    return s.playerMediaSummary(
      s.infoDimensionsValue(w, h),
      vkCodecName(codec),
    );
  }

  Widget _controls(
    BuildContext context,
    Size size,
    VideoKitSessionState st, {
    bool blocked = false,
    bool minimal = false,
    bool hidden = false,
  }) {
    // While hidden only the seek bar takes pointers (R2-05): dragging it
    // shows the controls at once and lands under the finger.
    Widget hid(Widget w) => IgnorePointer(ignoring: hidden, child: w);
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
    // Design page 9: the position is bold white, the duration regular and
    // dimmed.
    final positionStyle = t.typography.timecode.copyWith(
      fontWeight: FontWeight.w700,
      color: t.colors.playerControlsContent,
    );
    final durationStyle = t.typography.timecode.copyWith(
      fontWeight: FontWeight.w400,
      color: t.colors.playerControlsContent.withValues(alpha: 0.72),
    );
    final all = _secondary(context, st);
    final pictureStyle = _onPictureStyle(context);
    final volumeSlider =
        isVideo && layout != VkLayoutClass.compact && landscape;
    // Design page 10: in landscape the orientation lock floats at the start
    // edge and mute sits next to the volume slider.
    final lockItem = landscape
        ? all.where((i) => i.id == 'lock').firstOrNull
        : null;
    final muteItem = volumeSlider
        ? all.where((i) => i.id == 'volume').firstOrNull
        : null;
    // J9 (design page 23): at large text the portrait row becomes two list
    // rows, "字幕：…" and "更多控制"; everything else is in "more".
    final listRows = collapse && !landscape && isVideo;
    final secondary = [
      for (final i in all)
        if (i != lockItem &&
            i != muteItem &&
            !(listRows && i.id == 'subtitles'))
          i,
    ];

    // Fit secondary controls into the row (fullscreen always stays; "more"
    // lives in the top bar, so it takes no slot); the rest goes to "more".
    final rowWidth = size.width - d.spacing16 * 2;
    var slots = (rowWidth / (d.targetMin + d.spacing4)).floor();
    if (landscape) slots = (slots / 2).floor();
    if (collapse) slots = math.min(slots, 3);
    if (listRows) slots = 0;
    final fits = secondary.length <= slots;
    final shown = fits
        ? secondary
        : [
            if (!listRows) ...secondary.where((i) => i.id == 'fullscreen'),
            ...secondary
                .where((i) => i.id != 'fullscreen')
                .take(math.max(0, slots - 1)),
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

    final topBar = vkGlassBehind(
      glass.gradient(fromTop: true),
      SafeArea(
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
                    // Design page 10: in landscape the media summary follows
                    // the title on the same line.
                    Row(
                      children: [
                        if (widget.title != null)
                          Flexible(
                            child: Text(
                              widget.title!,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: t.typography.title.copyWith(
                                color: t.colors.playerControlsContent,
                              ),
                            ),
                          ),
                        if (landscape)
                          if (widget.subtitle ?? _mediaSummary(s, st)
                              case final summary?) ...[
                            SizedBox(width: d.spacing12),
                            Flexible(
                              child: Text(
                                summary,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: t.typography.caption.copyWith(
                                  color: t.colors.playerControlsContent
                                      .withValues(alpha: 0.72),
                                ),
                              ),
                            ),
                          ],
                      ],
                    ),
                  ],
                ),
              ),
              if (landscape && !minimal)
                ConstrainedBox(
                  constraints: BoxConstraints(maxWidth: size.width * 0.45),
                  child: hostBar,
                ),
              if (!minimal)
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
        !blocked &&
        st.phase.isBound &&
        (isVideo || st.mediaKind == MediaKind.imageAnimated);
    final step = widget.options.seekStepUs ~/ 1000000;
    final playButton = VkIconButton(
      icon: playing ? t.icons.pause : t.icons.play,
      semanticLabel: s.text(playing ? 'playerPause' : 'playerPlay'),
      onPressed: canPlay ? _c.togglePlay : null,
      iconSize: landscape ? d.icon24 : d.targetMin * 0.75,
      style: landscape ? pictureStyle : _bigPlayStyle(context),
    );
    final rewind = VkIconButton(
      icon: t.icons.resolve('seekback'),
      semanticLabel: s.rewind(step),
      onPressed: !blocked && isVideo && st.phase.isBound
          ? () => _c.seekBy(-widget.options.seekStepUs)
          : null,
      style: pictureStyle,
    );
    final forward = VkIconButton(
      icon: t.icons.resolve('seekforward'),
      semanticLabel: s.forward(step),
      onPressed: !blocked && isVideo && st.phase.isBound
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
            onDragEnd: !blocked && st.phase.isBound ? _c.dragEnd : null,
            onTapInstead: hidden ? _c.autoHide.show : null,
            previewFrame: VkSeekPreviewFrame(frames: _c.seekPreview),
          )
        : const SizedBox.shrink();
    final volume = volumeSlider
        ? Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (muteItem != null)
                _controlButton(context, muteItem, enabled: !blocked),
              SizedBox(
                width: d.targetMin * 2.5,
                child: VkSlider(
                  onPicture: true,
                  value: st.muted ? 0 : st.volume,
                  semanticLabel: s.text('playerVolume'),
                  semanticValue: (v) => VkFormat.percent(s, v),
                  onChangeEnd: !blocked && st.phase.isBound
                      ? (v) => unawaited(_c.send(SetVolume(v)))
                      : null,
                ),
              ),
            ],
          )
        : null;
    // J9 list rows (portrait, large text).
    final subtitleIndex = st.subtitleTracks.indexWhere(
      (x) => x.id == st.selectedSubtitleTrackId,
    );
    final subtitleName = subtitleIndex < 0
        ? s.text('tracksSubtitlesOff')
        : TrackSettingsSheet.trackName(
            s,
            st.subtitleTracks[subtitleIndex],
            subtitleIndex,
          );
    final listRowsWidget = listRows
        ? Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _ListRow(
                icon: t.icons.resolve('subtitles'),
                label: s.playerSubtitlesRow(subtitleName),
                onPressed: !blocked && st.phase.isBound
                    ? () => _openTracks(TrackSettingsTab.subtitles)
                    : null,
              ),
              SizedBox(height: d.spacing8),
              _ListRow(
                icon: t.icons.resolve('more'),
                label: s.text('playerMoreControls'),
                onPressed: blocked ? null : _openMore,
              ),
            ],
          )
        : null;
    final bottom = vkGlassBehind(
      glass.gradient(fromTop: false),
      SafeArea(
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
                hid(
                  Row(
                    children: [
                      Text(VkFormat.timecode(position), style: positionStyle),
                      const Spacer(),
                      Text(VkFormat.timecode(duration), style: durationStyle),
                    ],
                  ),
                ),
              if (landscape && isVideo)
                Row(
                  children: [
                    hid(
                      Text(VkFormat.timecode(position), style: positionStyle),
                    ),
                    SizedBox(width: d.spacing12),
                    Expanded(child: seekBar),
                    SizedBox(width: d.spacing12),
                    hid(
                      Text(VkFormat.timecode(duration), style: durationStyle),
                    ),
                  ],
                )
              else
                seekBar,
              if (!landscape)
                hid(
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
                ),
              if (listRowsWidget != null) ...[
                SizedBox(height: d.spacing12),
                hid(listRowsWidget),
              ],
              hid(
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
                          ? _controlButton(context, i, enabled: !blocked)
                          : Expanded(
                              child: Center(
                                child: _controlButton(
                                  context,
                                  i,
                                  enabled: !blocked,
                                ),
                              ),
                            ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );

    if (minimal) {
      return Stack(
        children: [
          PositionedDirectional(top: 0, start: 0, end: 0, child: hid(topBar)),
        ],
      );
    }
    final bottomBar = IgnorePointer(ignoring: blocked, child: bottom);
    if (landscape) {
      return Stack(
        children: [
          PositionedDirectional(top: 0, start: 0, end: 0, child: hid(topBar)),
          PositionedDirectional(start: 0, end: 0, bottom: 0, child: bottomBar),
          // Design page 10: floating orientation lock at the start edge.
          if (lockItem != null)
            PositionedDirectional(
              start: d.spacing16,
              top: 0,
              bottom: 0,
              child: Center(
                child: hid(
                  IgnorePointer(
                    ignoring: blocked,
                    child: VkIconButton(
                      icon: lockItem.icon,
                      semanticLabel: lockItem.label,
                      selected: lockItem.selected,
                      onPressed: lockItem.onPressed,
                      style: t.components.hostActionBar.item,
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    }
    // Portrait: the host action column gets exactly the space between the
    // two bars, so at large text it moves actions to "more" instead of
    // overlapping the time row (R1-12).
    return CustomMultiChildLayout(
      delegate: _PortraitControlsLayout(
        margin: d.spacing12,
        gap: d.spacing8,
        rtl: Directionality.of(context) == TextDirection.rtl,
      ),
      children: [
        LayoutId(id: _PortraitSlot.top, child: hid(topBar)),
        LayoutId(id: _PortraitSlot.bottom, child: bottomBar),
        LayoutId(
          id: _PortraitSlot.host,
          child: IgnorePointer(ignoring: blocked || hidden, child: hostBar),
        ),
      ],
    );
  }
}

enum _PortraitSlot { top, bottom, host }

/// Top bar at the top, bottom bar at the bottom, host actions at the end
/// edge just above the bottom bar, limited to the space left between them.
class _PortraitControlsLayout extends MultiChildLayoutDelegate {
  _PortraitControlsLayout({
    required this.margin,
    required this.gap,
    required this.rtl,
  });

  final double margin;
  final double gap;
  final bool rtl;

  @override
  void performLayout(Size size) {
    final width = BoxConstraints.tightFor(width: size.width);
    final top = layoutChild(
      _PortraitSlot.top,
      width.copyWith(maxHeight: size.height),
    );
    positionChild(_PortraitSlot.top, Offset.zero);
    final bottom = layoutChild(
      _PortraitSlot.bottom,
      width.copyWith(maxHeight: size.height),
    );
    positionChild(_PortraitSlot.bottom, Offset(0, size.height - bottom.height));
    final room = math.max(
      0.0,
      size.height - top.height - bottom.height - gap * 2,
    );
    final host = layoutChild(
      _PortraitSlot.host,
      BoxConstraints(
        maxWidth: math.max(0, size.width - margin * 2),
        maxHeight: room,
      ),
    );
    final x = rtl ? margin : size.width - margin - host.width;
    positionChild(
      _PortraitSlot.host,
      Offset(x, size.height - bottom.height - gap - host.height),
    );
  }

  @override
  bool shouldRelayout(_PortraitControlsLayout old) =>
      old.margin != margin || old.gap != gap || old.rtl != rtl;
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

/// Full-width control row used at large text (J9, design page 23): icon and
/// label on a raised surface, one touch target high at least.
class _ListRow extends StatelessWidget {
  const _ListRow({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  final IconData icon;
  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final style = t.components.menu.copyWithAll(
      (b) => b.copyWith(
        background: t.colors.surface,
        content: t.colors.textPrimary,
        radius: d.cornerLarge,
      ),
    );
    return VkPressable(
      style: style,
      semanticLabel: label,
      onPressed: onPressed,
      builder: (context, box) => Row(
        children: [
          Icon(
            icon,
            size: d.icon24 * VkLayoutClass.iconScale(context),
            color: box.content,
          ),
          SizedBox(width: d.spacing16),
          Expanded(
            child: Text(
              label,
              style: t.typography.body.copyWith(color: box.content),
            ),
          ),
        ],
      ),
    );
  }
}
