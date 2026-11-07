import 'package:flutter/scheduler.dart';
import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

/// Tells [session] whether its picture can be seen (07 §5.3, UI-05):
///
/// * **visible**: [child] is fully inside the nearest scroll viewport and the
///   screen;
/// * **partiallyVisible**: only part of it is (04A V1);
/// * **offscreen**: scrolled out, or fully covered by an opaque route (04A
///   V2: a translucent dialog or a bottom sheet on top changes nothing);
/// * **background**: the app is paused or hidden.
///
/// Only changes are sent (`SetVisibility`), and nothing is sent to a
/// released session. The session decides what to do (pause offscreen,
/// release decoders later); hosts use [onChanged] for their own policy.
class VideoKitVisibilityReporter extends StatefulWidget {
  /// Creates the reporter.
  const VideoKitVisibilityReporter({
    super.key,
    required this.session,
    required this.child,
    this.enabled = true,
    this.onChanged,
  });

  /// Session to inform.
  final VideoKitSession session;

  /// The picture (slot, player).
  final Widget child;

  /// Off = report nothing.
  final bool enabled;

  /// Called after each reported change.
  final ValueChanged<SessionVisibility>? onChanged;

  /// Visibility for [rect] inside [viewport] (both global), app [lifecycle]
  /// and whether an opaque route fully covers the page ([occluded]). Pure;
  /// used by the widget.
  static SessionVisibility classify({
    required Rect rect,
    required Rect viewport,
    bool occluded = false,
    AppLifecycleState? lifecycle,
  }) {
    if (lifecycle == AppLifecycleState.paused ||
        lifecycle == AppLifecycleState.hidden ||
        lifecycle == AppLifecycleState.detached) {
      return SessionVisibility.background;
    }
    if (occluded) return SessionVisibility.offscreen;
    final seen = rect.intersect(viewport);
    if (seen.width <= 0 || seen.height <= 0) return SessionVisibility.offscreen;
    // Allow sub-pixel rounding at the edges.
    const slack = 0.5;
    final full =
        seen.width >= rect.width - slack && seen.height >= rect.height - slack;
    return full
        ? SessionVisibility.visible
        : SessionVisibility.partiallyVisible;
  }

  @override
  State<VideoKitVisibilityReporter> createState() =>
      _VideoKitVisibilityReporterState();
}

class _VideoKitVisibilityReporterState extends State<VideoKitVisibilityReporter>
    with WidgetsBindingObserver {
  SessionVisibility? _sent;
  ScrollPosition? _position;
  bool _scheduled = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final p = Scrollable.maybeOf(context)?.position;
    if (!identical(p, _position)) {
      _position?.removeListener(_schedule);
      _position = p?..addListener(_schedule);
    }
    _schedule();
  }

  @override
  void didUpdateWidget(VideoKitVisibilityReporter old) {
    super.didUpdateWidget(old);
    if (!identical(old.session, widget.session)) _sent = null;
    _schedule();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) => _schedule();

  @override
  void didChangeMetrics() => _schedule();

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _position?.removeListener(_schedule);
    super.dispose();
  }

  void _schedule() {
    if (_scheduled || !widget.enabled) return;
    _scheduled = true;
    SchedulerBinding.instance
      ..addPostFrameCallback((_) {
        _scheduled = false;
        if (mounted) _check();
      })
      ..ensureVisualUpdate();
  }

  void _check() {
    final box = context.findRenderObject();
    if (box is! RenderBox || !box.hasSize || !box.attached) return;
    final rect = box.localToGlobal(Offset.zero) & box.size;
    final view = View.of(context);
    var viewport = Offset.zero & (view.physicalSize / view.devicePixelRatio);
    final scrollBox = Scrollable.maybeOf(context)?.context.findRenderObject();
    if (scrollBox is RenderBox && scrollBox.hasSize) {
      viewport = viewport.intersect(
        scrollBox.localToGlobal(Offset.zero) & scrollBox.size,
      );
    }
    final v = VideoKitVisibilityReporter.classify(
      rect: rect,
      viewport: viewport,
      // Routes fully covered by an opaque route are kept offstage with
      // their tickers disabled; translucent routes leave them onstage.
      occluded: !TickerMode.valuesOf(context).enabled,
      lifecycle: WidgetsBinding.instance.lifecycleState,
    );
    if (v == _sent) return;
    _sent = v;
    final s = widget.session;
    final st = s.state.value;
    if (st.phase == SessionPhase.released) return;
    if (st.visibility != v) s.execute(SetVisibility(v)).ignore();
    widget.onChanged?.call(v);
  }

  @override
  Widget build(BuildContext context) {
    _schedule();
    return widget.child;
  }
}
