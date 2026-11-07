import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_badge.dart';
import '../common/vk_buttons.dart';
import '../common/vk_sheet_host.dart';
import '../foundation/auto_hide.dart';
import '../foundation/format.dart';
import '../foundation/selector.dart';
import '../host_action/host_action_bar.dart';
import '../l10n/vk_strings.dart';
import '../player/media_surface.dart';
import '../player/picture_style.dart';
import '../player/player_controller.dart';
import '../state_view/state_mapping.dart';
import '../state_view/state_view.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'image_info_sheet.dart';
import 'mini_map.dart';

/// Options of [VideoKitImageViewer].
@immutable
final class VideoKitImageViewerOptions {
  /// Creates options.
  const VideoKitImageViewerOptions({
    this.autoHideDelay = const Duration(seconds: 3),
    this.maxZoom = 8,
    this.doubleTapZoom = 2,
    this.zoomStep = 1.25,
    this.showPageButtons = true,
    this.swipeFraction = 0.18,
  });

  /// Auto-hide delay (only while an animated image plays).
  final Duration autoHideDelay;

  /// Maximum zoom relative to the fit size.
  final double maxZoom;

  /// Zoom level of a double tap from the fit size.
  final double doubleTapZoom;

  /// Keyboard zoom step factor.
  final double zoomStep;

  /// Show previous/next buttons (the host still decides, 14 §5.3).
  final bool showPageButtons;

  /// Horizontal swipe distance (fraction of the width) that requests a page.
  final double swipeFraction;
}

/// UI-03 image viewer (14 §5.3, design page 13): static and animated
/// images in the same session; zoom/pan/rotate, fit/original size, mini
/// map, animation play/pause/loop, page requests and the image info panel.
///
/// The control set is image-only: this widget has no seek bar, track,
/// speed or volume controls at all (guaranteed by the component type, not
/// by hiding).
class VideoKitImageViewer extends StatefulWidget {
  /// Creates a viewer.
  const VideoKitImageViewer({
    super.key,
    required this.session,
    this.title,
    this.source,
    this.hostActions,
    this.onBack,
    this.onStateAction,
    this.onControlsVisibilityChanged,
    this.pictureBuilder,
    this.resolveHostString,
    this.resolveHostIcon,
    this.options = const VideoKitImageViewerOptions(),
  });

  /// Session (owned by the host).
  final VideoKitSession session;

  /// Display name (display only).
  final String? title;

  /// Bound source, for the info panel (format, file size).
  final VideoKitMediaSource? source;

  /// Host actions; also settable through `session.updateHostActions`.
  final List<VideoKitHostAction>? hostActions;

  /// Back button; null hides it.
  final VoidCallback? onBack;

  /// State view actions (retry → host re-binds, other source …).
  final ValueChanged<StateAction>? onStateAction;

  /// Controls visibility changed.
  final ValueChanged<bool>? onControlsVisibilityChanged;

  /// Picture without texture (Dart Fake).
  final VideoKitPictureBuilder? pictureBuilder;

  /// Host string resolver.
  final HostStringResolver? resolveHostString;

  /// Host resource icon resolver.
  final HostIconResolver? resolveHostIcon;

  /// Options.
  final VideoKitImageViewerOptions options;

  @override
  State<VideoKitImageViewer> createState() => VideoKitImageViewerState();
}

/// State of [VideoKitImageViewer]; host handle through a `GlobalKey`.
class VideoKitImageViewerState extends State<VideoKitImageViewer> {
  late PlayerController _c;
  final FocusNode _focus = FocusNode(debugLabel: 'VideoKitImageViewer');
  MediaTransform? _gestureStart;
  Offset? _gestureFocal;
  double _swipeDx = 0;
  bool _swiping = false;

  /// Shows the controls.
  void showControls() => _c.autoHide.show();

  /// Opens the image info panel.
  void openInfo() {
    final s = VkStrings.of(context);
    _c.sheets.show(
      VkSheetEntry(
        id: 'info',
        title: s.text('viewerInfo'),
        builder: (context) =>
            ImageInfoSheet(session: widget.session, source: widget.source),
      ),
    );
  }

  /// Whether the media loops (04A L1, session state).
  bool get looping => widget.session.state.value.looping;

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
  void didUpdateWidget(VideoKitImageViewer oldWidget) {
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

  // ---------------------------------------------------------- transform --

  MediaTransform get _transform =>
      _c.gestureTransform ?? widget.session.state.value.transform;

  void _commit(MediaTransform t) => unawaited(_c.send(SetTransform(t)));

  static double _panLimit(double scale) => math.max(0, (scale - 1) / 2);

  MediaTransform _clampPan(MediaTransform t) {
    final limit = t.fitMode == FitMode.original ? 1.0 : _panLimit(t.scale);
    return t.copyWith(
      panX: t.panX.clamp(-limit, limit),
      panY: t.panY.clamp(-limit, limit),
    );
  }

  void _toggleFit() {
    final t = widget.session.state.value.transform;
    _commit(
      MediaTransform(
        fitMode: t.fitMode == FitMode.original ? FitMode.fit : FitMode.original,
        rotationDeg: t.rotationDeg,
      ),
    );
  }

  void _rotate() {
    final t = widget.session.state.value.transform;
    _commit(
      MediaTransform(
        fitMode: t.fitMode,
        rotationDeg: (t.rotationDeg + 90) % 360,
      ),
    );
  }

  void _zoomBy(double factor) {
    final t = widget.session.state.value.transform;
    final scale = (t.scale * factor).clamp(1.0, widget.options.maxZoom);
    _commit(_clampPan(t.copyWith(scale: scale)));
  }

  void _resetZoom() {
    final t = widget.session.state.value.transform;
    _commit(MediaTransform(fitMode: t.fitMode, rotationDeg: t.rotationDeg));
  }

  void _toggleZoom() {
    final t = widget.session.state.value.transform;
    if (t.isZoomed) {
      _resetZoom();
    } else {
      _commit(t.copyWith(scale: widget.options.doubleTapZoom));
    }
  }

  bool get _isAnimated =>
      widget.session.state.value.mediaKind == MediaKind.imageAnimated;

  void _togglePlay() {
    if (_isAnimated) _c.togglePlay();
  }

  void _toggleLoop() =>
      unawaited(_c.send(SetLooping(!widget.session.state.value.looping)));

  void _page(NavigationDirection direction) {
    _c.autoHide.kick();
    unawaited(_c.requestNavigation(direction));
  }

  /// Logical "forward" for a swipe: a leftward swipe in LTR means next.
  NavigationDirection _swipeDirection(double dx) {
    final rtl = Directionality.of(context) == TextDirection.rtl;
    final forward = rtl ? dx > 0 : dx < 0;
    return forward ? NavigationDirection.next : NavigationDirection.previous;
  }

  // ------------------------------------------------------------ gestures --

  void _scaleStart(ScaleStartDetails d) {
    _gestureStart = widget.session.state.value.transform;
    _gestureFocal = d.localFocalPoint;
    _swipeDx = 0;
  }

  void _scaleUpdate(ScaleUpdateDetails d, Size size) {
    final start = _gestureStart;
    final focal = _gestureFocal;
    if (start == null || focal == null || size.isEmpty) return;
    final delta = d.localFocalPoint - focal;
    if (d.pointerCount >= 2) {
      final scale = (start.scale * d.scale).clamp(1.0, widget.options.maxZoom);
      _c.setGestureTransform(
        _clampPan(
          start.copyWith(
            scale: scale,
            panX: start.panX + delta.dx / size.width,
            panY: start.panY + delta.dy / size.height,
          ),
        ),
      );
      return;
    }
    if (start.isZoomed || start.fitMode == FitMode.original) {
      // Pan first; what is left beyond the edge becomes a page swipe.
      final wanted = start.panX + delta.dx / size.width;
      final clamped = _clampPan(
        start.copyWith(panX: wanted, panY: start.panY + delta.dy / size.height),
      );
      _c.setGestureTransform(clamped);
      _swipeDx = (wanted - clamped.panX) * size.width;
      return;
    }
    setState(() {
      _swiping = true;
      _swipeDx = delta.dx;
    });
  }

  void _scaleEnd(ScaleEndDetails d, Size size) {
    final g = _c.gestureTransform;
    if (g != null) {
      unawaited(
        _c
            .send(SetTransform(g))
            .whenComplete(() => _c.setGestureTransform(null)),
      );
    }
    final dx = _swipeDx;
    final flick = d.velocity.pixelsPerSecond.dx;
    final far = dx.abs() > size.width * widget.options.swipeFraction;
    final fast = flick.abs() > 800 && flick.sign == dx.sign && dx != 0;
    if (d.pointerCount <= 1 && (far || fast)) {
      _page(_swipeDirection(dx));
    }
    setState(() {
      _swiping = false;
      _swipeDx = 0;
    });
    _gestureStart = null;
    _gestureFocal = null;
  }

  // -------------------------------------------------------------- build --

  Map<ShortcutActivator, VoidCallback> _shortcuts() {
    final rtl = Directionality.of(context) == TextDirection.rtl;
    void prev() => _page(NavigationDirection.previous);
    void next() => _page(NavigationDirection.next);
    return {
      const SingleActivator(LogicalKeyboardKey.arrowLeft): rtl ? next : prev,
      const SingleActivator(LogicalKeyboardKey.arrowRight): rtl ? prev : next,
      const SingleActivator(LogicalKeyboardKey.pageUp): prev,
      const SingleActivator(LogicalKeyboardKey.pageDown): next,
      const SingleActivator(LogicalKeyboardKey.equal): () =>
          _zoomBy(widget.options.zoomStep),
      const SingleActivator(LogicalKeyboardKey.add): () =>
          _zoomBy(widget.options.zoomStep),
      const SingleActivator(LogicalKeyboardKey.minus): () =>
          _zoomBy(1 / widget.options.zoomStep),
      const SingleActivator(LogicalKeyboardKey.digit0): _resetZoom,
      const SingleActivator(LogicalKeyboardKey.keyR): _rotate,
      const SingleActivator(LogicalKeyboardKey.keyI): openInfo,
      const SingleActivator(LogicalKeyboardKey.space): _togglePlay,
    };
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
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
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    return ListenableBuilder(
      listenable: _c,
      builder: (context, _) {
        final visible = _c.autoHide.visible;
        final motion = t.animations.normal;
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
              child: AnimatedSlide(
                offset: Offset(size.isEmpty ? 0 : _swipeDx / size.width, 0),
                duration: _swiping ? Duration.zero : motion.duration,
                curve: motion.curve,
                child: VkMediaSurface(
                  session: widget.session,
                  transformOverride: _c.gestureTransform,
                  builder: widget.pictureBuilder,
                ),
              ),
            ),
            Positioned.fill(
              child: Semantics(
                container: true,
                label: s.text('viewerPicture'),
                onTap: _c.autoHide.toggle,
                // The Semantics node above carries the tap for screen readers.
                child: GestureDetector(
                  excludeFromSemantics: true,
                  behavior: HitTestBehavior.opaque,
                  onTap: () {
                    _focus.requestFocus();
                    _c.autoHide.toggle();
                  },
                  onDoubleTap: _toggleZoom,
                  onScaleStart: _scaleStart,
                  onScaleUpdate: (d) => _scaleUpdate(d, size),
                  onScaleEnd: (d) => _scaleEnd(d, size),
                ),
              ),
            ),
            if (model != null)
              Positioned.fill(
                child: IgnorePointer(
                  ignoring: model.keepsPicture,
                  child: VideoKitStateView(
                    model: model,
                    onStateAction: widget.onStateAction,
                  ),
                ),
              ),
            // Zoom indicator and mini map stay while zoomed (design p. 13).
            if (_transform.isZoomed || _transform.fitMode == FitMode.original)
              ..._zoomIndicators(context, size, st),
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
            if (widget.session.isDemo)
              PositionedDirectional(
                top: 0,
                start: 0,
                end: 0,
                child: SafeArea(
                  child: Padding(
                    padding: EdgeInsetsDirectional.only(
                      top: t.dimensions.controlBarHeight,
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

  /// Zoom relative to the current fit mode, as on design page 13 (200 %
  /// after a double tap).
  double get _zoomFraction => _transform.scale;

  List<Widget> _zoomIndicators(
    BuildContext context,
    Size size,
    VideoKitSessionState st,
  ) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final percent = VkFormat.percent(s, _zoomFraction);
    return [
      PositionedDirectional(
        top: d.controlBarHeight + d.spacing32,
        start: 0,
        end: 0,
        child: SafeArea(
          child: Center(
            child: Semantics(
              container: true,
              label: s.text('viewerZoomLabel'),
              value: percent,
              liveRegion: true,
              child: ExcludeSemantics(
                child: Container(
                  padding: EdgeInsetsDirectional.symmetric(
                    horizontal: d.spacing12,
                    vertical: d.spacing4,
                  ),
                  decoration: BoxDecoration(
                    // Design p. 13: opaque dark capsule, visible over the black
                    // canvas and over bright pictures alike.
                    color: Color.alphaBlend(
                      t.colors.playerControlsContent.withValues(alpha: 0.12),
                      t.colors.playerCanvas,
                    ),
                    borderRadius: BorderRadius.circular(d.cornerFull),
                  ),
                  child: Text(
                    percent,
                    style: t.typography.label.copyWith(
                      color: t.colors.playerControlsContent,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
      if (_transform.isZoomed)
        PositionedDirectional(
          end: d.spacing16,
          bottom: d.controlBarHeight * 2,
          child: SafeArea(
            child: VkMiniMap(
              transform: _transform,
              mediaSize: widget.session.videoSize.value,
              label: s.text('viewerMiniMap'),
            ),
          ),
        ),
    ];
  }

  Widget _controls(BuildContext context, Size size, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final glass = t.drawables.glassPlayer;
    final pictureStyle = vkOnPictureIconStyle(context);
    final animated = st.mediaKind == MediaKind.imageAnimated;
    final white = t.colors.playerControlsContent;

    // Bottom toolbar: viewer tools, then host actions in priority order;
    // what does not fit goes to the single "more" panel (14 §7.2 rule).
    final tools = <_ToolItem>[
      _ToolItem(
        id: 'fit',
        icon: t.icons.resolve(
          st.transform.fitMode == FitMode.original ? 'fit' : 'originalsize',
        ),
        label: s.text(
          st.transform.fitMode == FitMode.original
              ? 'fitModeFit'
              : 'fitModeOriginal',
        ),
        onPressed: st.phase.isBound ? _toggleFit : null,
      ),
      _ToolItem(
        id: 'rotate',
        icon: t.icons.resolve('rotate'),
        label: s.text('playerRotate'),
        onPressed: st.phase.isBound ? _rotate : null,
      ),
    ];
    final toolbarWidth = size.width - d.spacing8 * 2;
    final itemExtent = d.targetMin * 1.25;
    final hostLayout = layoutHostActions(
      st.hostActions,
      available: math.max(0, toolbarWidth - tools.length * itemExtent),
      itemExtent: itemExtent,
      collapseSecondary: false,
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
                child: widget.title == null
                    ? const SizedBox.shrink()
                    : Semantics(
                        header: true,
                        child: Text(
                          widget.title!,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: t.typography.title.copyWith(color: white),
                        ),
                      ),
              ),
              VkIconButton(
                icon: t.icons.resolve('info'),
                semanticLabel: s.text('viewerInfo'),
                onPressed: openInfo,
                style: pictureStyle,
              ),
              VkIconButton(
                icon: t.icons.resolve('more'),
                semanticLabel: s.text('commonMore'),
                pending: hostLayout.overflow.any((a) => a.isPending),
                onPressed: () => _openMore(hostLayout.overflow),
                style: pictureStyle,
              ),
            ],
          ),
        ),
      ),
    );

    Widget toolButton(_ToolItem i) => _ToolButton(item: i, style: pictureStyle);
    Widget hostButton(HostActionState a) => _ToolButton(
      item: _ToolItem(
        id: a.action.actionId,
        icon: switch (a.action.icon) {
          HostIconBuiltIn(:final iconKey) => t.icons.resolve(iconKey),
          final HostIconResource r =>
            widget.resolveHostIcon?.call(r) ?? t.icons.resolve('unknown'),
        },
        label: _host(a.action.labelKey),
        semanticLabel: _host(a.action.contentDescriptionKey),
        selected: a.action.selected,
        pending: a.isPending,
        badgeText: a.action.badgeText,
        onPressed: a.action.enabled
            ? () => _c.requestHostAction(a.action.actionId)
            : null,
      ),
      style: pictureStyle,
    );

    final bottom = DecoratedBox(
      decoration: BoxDecoration(gradient: glass.gradient(fromTop: false)),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsetsDirectional.fromSTEB(
            d.spacing8,
            d.spacing24,
            d.spacing8,
            d.spacing8,
          ),
          child: Semantics(
            container: true,
            explicitChildNodes: true,
            child: Row(
              children: [
                for (final i in tools) Expanded(child: toolButton(i)),
                for (final a in hostLayout.visible)
                  Expanded(child: hostButton(a)),
              ],
            ),
          ),
        ),
      ),
    );

    final hostSecondary = widget.options.showPageButtons
        ? t.components.hostActionBar.item
        : null;

    return Stack(
      children: [
        PositionedDirectional(top: 0, start: 0, end: 0, child: topBar),
        if (animated)
          PositionedDirectional(
            top: d.controlBarHeight,
            start: d.spacing16,
            child: SafeArea(child: _AnimatedBadge(source: widget.source)),
          ),
        if (hostSecondary != null) ...[
          PositionedDirectional(
            start: d.spacing8,
            top: 0,
            bottom: 0,
            child: Center(
              child: VkIconButton(
                icon: t.icons.resolve('previous'),
                semanticLabel: s.text('viewerPrevious'),
                style: hostSecondary,
                onPressed: () => _page(NavigationDirection.previous),
              ),
            ),
          ),
          PositionedDirectional(
            end: d.spacing8,
            top: 0,
            bottom: 0,
            child: Center(
              child: VkIconButton(
                icon: t.icons.resolve('next'),
                semanticLabel: s.text('viewerNext'),
                style: hostSecondary,
                onPressed: () => _page(NavigationDirection.next),
              ),
            ),
          ),
        ],
        if (animated)
          PositionedDirectional(
            start: 0,
            end: 0,
            bottom: d.controlBarHeight * 2,
            child: Center(child: _animationStrip(context, st)),
          ),
        PositionedDirectional(bottom: 0, start: 0, end: 0, child: bottom),
      ],
    );
  }

  Widget _animationStrip(BuildContext context, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final style = vkOnPictureIconStyle(context);
    final playing = st.phase == SessionPhase.playing;
    return Container(
      padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing8),
      decoration: BoxDecoration(
        color: t.drawables.glassPlayer.color,
        borderRadius: BorderRadius.circular(d.cornerFull),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          VkIconButton(
            icon: playing ? t.icons.pause : t.icons.play,
            semanticLabel: s.text(playing ? 'playerPause' : 'playerPlay'),
            onPressed: st.phase.isBound ? _c.togglePlay : null,
            style: style,
          ),
          VkIconButton(
            icon: t.icons.resolve('loop'),
            semanticLabel: s.text('viewerLoop'),
            selected: st.looping,
            onPressed: _toggleLoop,
            style: style,
          ),
        ],
      ),
    );
  }

  void _openMore(List<HostActionState> hostOverflow) {
    final s = VkStrings.of(context);
    final t = VkTheme.of(context);
    final ids = [for (final a in hostOverflow) a.action.actionId];
    _c.sheets.show(
      VkSheetEntry(
        id: 'more',
        title: s.text('commonMore'),
        builder: (context) => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            VkSelector<VideoKitSessionState, List<HostActionState>>(
              listenable: widget.session.state,
              select: (x) => [
                for (final a in x.hostActions)
                  if (ids.contains(a.action.actionId)) a,
              ],
              builder: (context, host) => Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
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
                ],
              ),
            ),
            VkMenuItem(
              icon: t.icons.resolve('info'),
              label: s.text('viewerInfo'),
              onPressed: () {
                _c.sheets.close('more');
                openInfo();
              },
            ),
          ],
        ),
      ),
    );
  }
}

@immutable
final class _ToolItem {
  const _ToolItem({
    required this.id,
    required this.icon,
    required this.label,
    required this.onPressed,
    this.semanticLabel,
    this.selected = false,
    this.pending = false,
    this.badgeText,
  });

  final String id;
  final IconData icon;
  final String label;
  final String? semanticLabel;
  final bool selected;
  final bool pending;
  final String? badgeText;
  final VoidCallback? onPressed;
}

/// Toolbar item: icon button with its label underneath (design p. 13).
class _ToolButton extends StatelessWidget {
  const _ToolButton({required this.item, required this.style});

  final _ToolItem item;
  final VkStateStyle<VkBoxStyle> style;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final enabled = item.onPressed != null;
    final color = t.colors.playerControlsContent;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        VkIconButton(
          icon: item.icon,
          semanticLabel: item.semanticLabel ?? item.label,
          selected: item.selected,
          pending: item.pending,
          badgeText: item.badgeText,
          onPressed: item.onPressed,
          style: style,
        ),
        ExcludeSemantics(
          child: Text(
            item.label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
            style: t.typography.caption.copyWith(
              color: enabled ? color : color.withValues(alpha: 0.38),
            ),
          ),
        ),
      ],
    );
  }
}

/// "GIF · 动态" badge for animated images.
class _AnimatedBadge extends StatelessWidget {
  const _AnimatedBadge({required this.source});

  final VideoKitMediaSource? source;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final chip = t.components.chip.selected;
    final format = ImageInfoSheet.formatName(source);
    final text = format == null
        ? s.text('imageKindAnimated')
        : s.viewerAnimatedBadge(format);
    return Container(
      padding: chip.padding,
      decoration: BoxDecoration(
        color: t.colors.primary,
        borderRadius: BorderRadius.circular(t.dimensions.cornerFull),
      ),
      child: Text(
        text,
        style: t.typography.label.copyWith(color: t.colors.onPrimary),
      ),
    );
  }
}
