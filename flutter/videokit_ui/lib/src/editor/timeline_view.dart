import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter/services.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../mask/coverage_strip.dart';
import '../theme/theme_data.dart';
import '../theme/theme_scope.dart';
import 'editor_controller.dart';
import 'timeline_scale.dart';

/// Trim drag in progress (local visual state, 14 §6.3).
@immutable
final class _Trim {
  const _Trim(this.clipId, this.start, this.inUs, this.outUs);

  final String clipId;
  final bool start;
  final int inUs;
  final int outUs;
}

/// Reorder drag in progress.
@immutable
final class _Move {
  const _Move(this.clipId, this.x, this.insertAt);

  final String clipId;
  final double x;
  final int insertAt;
}

/// UI-06 timeline (14 §5.6): ruler, clip blocks, mask rows with keyframe
/// diamonds and coverage, playhead. Zoom 10–400 px/s around the focus
/// (pinch or Ctrl+wheel), snapping within 8 dp to the playhead, clip
/// boundaries and keyframes; trim by dragging the selected clip's edges,
/// reorder by long-press drag. Every gesture commits one command at its
/// end.
class TimelineView extends StatefulWidget {
  /// Creates a timeline.
  const TimelineView({super.key, required this.controller});

  /// Editor controller.
  final EditorController controller;

  @override
  State<TimelineView> createState() => _TimelineViewState();
}

class _TimelineViewState extends State<TimelineView> {
  _Trim? _trim;
  _Move? _move;
  double _width = 0;
  bool _fitted = false;
  TimelineScale? _zoomStart;
  Offset? _panStart;
  double _panScrollStart = 0;
  int? _lastSnap;
  Offset? _down;

  EditorController get _c => widget.controller;

  /// Snap threshold (14 §5.6: 8 dp).
  double get _snapPx => VkTheme.of(context).dimensions.spacing8;

  double get _handleWidth => VkTheme.of(context).dimensions.spacing16;

  double _rulerHeight(VideoKitThemeData t) => t.dimensions.spacing24;

  double _clipTop(VideoKitThemeData t) =>
      _rulerHeight(t) + t.dimensions.spacing4;

  double _maskTop(VideoKitThemeData t) =>
      _clipTop(t) + t.dimensions.timelineClipRow + t.dimensions.spacing8;

  void _fitIfNeeded(double width) {
    final d = _c.state.timeline.durationUs;
    if (_fitted || d <= 0 || width <= 0) return;
    _fitted = true;
    final pps = ((width - _handleWidth * 2) / (d / 1e6)).clamp(
      TimelineScale.minPxPerSecond,
      TimelineScale.maxPxPerSecond,
    );
    _c.scale = TimelineScale(pxPerSecond: pps, scrollX: -_handleWidth);
  }

  // ----------------------------------------------------------- geometry --

  ({int index, EditClip clip, int start})? _hitClip(double x) {
    final us = _c.scale.usForX(x);
    var start = 0;
    for (final (i, clip) in _c.state.timeline.clips.indexed) {
      if (us >= start && us < start + clip.durationUs) {
        return (index: i, clip: clip, start: start);
      }
      start += clip.durationUs;
    }
    return null;
  }

  /// Edge of the selected clip under [x], if within the handle width.
  bool? _hitHandle(double x) {
    final id = _c.selectedClipId;
    if (id == null) return null;
    final tl = _c.state.timeline;
    final start = tl.clipStartUs(id);
    final clip = tl.clips.where((c) => c.clipId == id).firstOrNull;
    if (start == null || clip == null) return null;
    final l = _c.scale.xForUs(start);
    final r = _c.scale.xForUs(start + clip.durationUs);
    if ((x - l).abs() <= _handleWidth) return true;
    if ((x - r).abs() <= _handleWidth) return false;
    return null;
  }

  Iterable<int> _snapTargets(String exceptClipId) sync* {
    yield _c.playheadUs;
    final starts = _c.clipStarts();
    final clips = _c.state.timeline.clips;
    for (final (i, s) in starts.indexed) {
      if (clips[i].clipId == exceptClipId) continue;
      yield s;
      yield s + clips[i].durationUs;
    }
    for (final m in _c.state.masks) {
      for (final k in m.keyframes) {
        yield k.atUs;
      }
    }
  }

  // ----------------------------------------------------------- gestures --

  void _onTapUp(TapUpDetails d) {
    final t = VkTheme.of(context);
    if (d.localPosition.dy < _clipTop(t)) {
      unawaited(_c.seek(_c.scale.usForX(d.localPosition.dx)));
      return;
    }
    final hit = _hitClip(d.localPosition.dx);
    _c.selectClip(hit?.clip.clipId);
    if (hit != null) unawaited(_c.seek(_c.scale.usForX(d.localPosition.dx)));
  }

  void _onScaleStart(ScaleStartDetails d) {
    _zoomStart = _c.scale;
    _panStart = _down ?? d.localFocalPoint;
    _panScrollStart = _c.scale.scrollX;
    _lastSnap = null;
    if (d.pointerCount == 1) {
      // Hit-test where the finger went down: the recognizer reports the
      // focal point only after the touch slop.
      final edge = _hitHandle((_down ?? d.localFocalPoint).dx);
      final id = _c.selectedClipId;
      if (edge != null && id != null) {
        final clip = _c.state.timeline.clips.firstWhere((c) => c.clipId == id);
        setState(() => _trim = _Trim(id, edge, clip.inUs, clip.outUs));
      }
    }
  }

  void _onScaleUpdate(ScaleUpdateDetails d) {
    final start = _zoomStart;
    final panStart = _panStart;
    if (start == null || panStart == null) return;
    final duration = _c.state.timeline.durationUs;
    if (d.pointerCount >= 2) {
      _c.scale = start
          .zoomAround(d.localFocalPoint.dx, d.horizontalScale)
          .scrolledTo(
            start.zoomAround(d.localFocalPoint.dx, d.horizontalScale).scrollX,
            duration,
            _width,
          );
      return;
    }
    final dx = d.localFocalPoint.dx - panStart.dx;
    final trim = _trim;
    if (trim != null) {
      _updateTrim(trim, dx);
      return;
    }
    _c.scale = _c.scale.scrolledTo(_panScrollStart - dx, duration, _width);
  }

  void _updateTrim(_Trim trim, double dx) {
    final tl = _c.state.timeline;
    final clip = tl.clips.firstWhere((c) => c.clipId == trim.clipId);
    final src = tl.sourceById(clip.sourceId);
    final clipStart = tl.clipStartUs(clip.clipId) ?? 0;
    final deltaUs = (dx / _c.scale.pxPerSecond * 1e6).round();
    const minUs = 500000;
    var inUs = clip.inUs;
    var outUs = clip.outUs;
    if (trim.start) {
      inUs = (clip.inUs + deltaUs).clamp(0, clip.outUs - minUs);
      final edge = clipStart + (inUs - clip.inUs);
      final snapped = _c.scale.snap(edge, _snapTargets(clip.clipId), _snapPx);
      if (snapped != null) {
        inUs = (clip.inUs + snapped - clipStart).clamp(0, clip.outUs - minUs);
      }
      _haptic(snapped);
    } else {
      final maxOut = src?.probe.durationUs ?? clip.outUs;
      outUs = (clip.outUs + deltaUs).clamp(clip.inUs + minUs, maxOut);
      final edge = clipStart + (outUs - clip.inUs);
      final snapped = _c.scale.snap(edge, _snapTargets(clip.clipId), _snapPx);
      if (snapped != null) {
        outUs = (clip.inUs + snapped - clipStart).clamp(
          clip.inUs + minUs,
          maxOut,
        );
      }
      _haptic(snapped);
    }
    setState(() => _trim = _Trim(trim.clipId, trim.start, inUs, outUs));
  }

  void _haptic(int? snapped) {
    if (snapped != null && snapped != _lastSnap) {
      unawaited(HapticFeedback.selectionClick());
    }
    _lastSnap = snapped;
  }

  void _onScaleEnd(ScaleEndDetails d) {
    final trim = _trim;
    if (trim != null) {
      final clip = _c.state.timeline.clips
          .where((c) => c.clipId == trim.clipId)
          .firstOrNull;
      if (clip != null &&
          (clip.inUs != trim.inUs || clip.outUs != trim.outUs)) {
        unawaited(_c.apply(TrimClip(trim.clipId, trim.inUs, trim.outUs)));
      }
    }
    setState(() => _trim = null);
    _zoomStart = null;
    _panStart = null;
  }

  int _insertionIndex(double x) {
    final starts = _c.clipStarts();
    final clips = _c.state.timeline.clips;
    final us = _c.scale.usForX(x);
    var i = 0;
    for (; i < clips.length; i++) {
      if (us < starts[i] + clips[i].durationUs / 2) break;
    }
    return i;
  }

  void _onLongPressStart(LongPressStartDetails d) {
    final hit = _hitClip(d.localPosition.dx);
    if (hit == null) return;
    _c.selectClip(hit.clip.clipId);
    unawaited(HapticFeedback.selectionClick());
    setState(
      () => _move = _Move(
        hit.clip.clipId,
        d.localPosition.dx,
        _insertionIndex(d.localPosition.dx),
      ),
    );
  }

  void _onLongPressMove(LongPressMoveUpdateDetails d) {
    final m = _move;
    if (m == null) return;
    setState(
      () => _move = _Move(
        m.clipId,
        d.localPosition.dx,
        _insertionIndex(d.localPosition.dx),
      ),
    );
  }

  void _onLongPressEnd(LongPressEndDetails d) {
    final m = _move;
    setState(() => _move = null);
    if (m == null) return;
    final clips = _c.state.timeline.clips;
    final from = clips.indexWhere((c) => c.clipId == m.clipId);
    if (from < 0) return;
    final to = m.insertAt > from ? m.insertAt - 1 : m.insertAt;
    if (to != from) unawaited(_c.apply(MoveClip(m.clipId, to)));
  }

  void _onPointerSignal(PointerSignalEvent e) {
    if (e is! PointerScrollEvent) return;
    final duration = _c.state.timeline.durationUs;
    final ctrl =
        HardwareKeyboard.instance.isControlPressed ||
        HardwareKeyboard.instance.isMetaPressed;
    if (ctrl) {
      final factor = e.scrollDelta.dy < 0 ? 1.2 : 1 / 1.2;
      final z = _c.scale.zoomAround(e.localPosition.dx, factor);
      _c.scale = z.scrolledTo(z.scrollX, duration, _width);
    } else {
      final delta = e.scrollDelta.dx != 0 ? e.scrollDelta.dx : e.scrollDelta.dy;
      _c.scale = _c.scale.scrolledTo(
        _c.scale.scrollX + delta,
        duration,
        _width,
      );
    }
  }

  void _zoomButton(double factor) {
    final duration = _c.state.timeline.durationUs;
    final z = _c.scale.zoomAround(_width / 2, factor);
    _c.scale = z.scrolledTo(z.scrollX, duration, _width);
  }

  // -------------------------------------------------------------- build --

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return ListenableBuilder(
      listenable: _c,
      builder: (context, _) {
        final st = _c.state;
        final masks = st.masks;
        final height =
            _maskTop(t) +
            masks.length * (d.timelineMaskRow + d.spacing4) +
            d.spacing8;
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            LayoutBuilder(
              builder: (context, c) {
                _width = c.maxWidth;
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  if (mounted) _fitIfNeeded(c.maxWidth);
                });
                return SizedBox(
                  height: height,
                  child: Semantics(
                    container: true,
                    label: s.text('timelineLabel'),
                    explicitChildNodes: true,
                    child: ClipRect(
                      child: Stack(
                        children: [
                          Positioned.fill(
                            child: Listener(
                              onPointerSignal: _onPointerSignal,
                              onPointerDown: (e) => _down = e.localPosition,
                              child: GestureDetector(
                                excludeFromSemantics: true,
                                behavior: HitTestBehavior.opaque,
                                onTapUp: _onTapUp,
                                onScaleStart: _onScaleStart,
                                onScaleUpdate: _onScaleUpdate,
                                onScaleEnd: _onScaleEnd,
                                onLongPressStart: _onLongPressStart,
                                onLongPressMoveUpdate: _onLongPressMove,
                                onLongPressEnd: _onLongPressEnd,
                                child: CustomPaint(
                                  painter: _TimelinePainter(
                                    state: st,
                                    scale: _c.scale,
                                    playheadUs: _c.playheadUs,
                                    selectedClipId: _c.selectedClipId,
                                    selectedMaskId: _c.selectedMaskId,
                                    trim: _trim,
                                    move: _move,
                                    theme: t,
                                    clipLabel: s.editorClip,
                                    textDirection: Directionality.of(context),
                                    fontFamily: DefaultTextStyle.of(context)
                                        .style
                                        .fontFamily,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          ..._clipSemantics(context, st),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                VkIconButton(
                  icon: VkTheme.of(context).icons.resolve('zoomout'),
                  semanticLabel: s.text('timelineZoomOut'),
                  onPressed: () => _zoomButton(1 / 1.5),
                ),
                VkIconButton(
                  icon: VkTheme.of(context).icons.resolve('zoomin'),
                  semanticLabel: s.text('timelineZoomIn'),
                  onPressed: () => _zoomButton(1.5),
                ),
              ],
            ),
          ],
        );
      },
    );
  }

  /// Invisible semantics nodes over each clip: select, move earlier/later,
  /// and (selected clip) trim handles with increase/decrease.
  List<Widget> _clipSemantics(BuildContext context, VideoKitEditState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final out = <Widget>[];
    var start = 0;
    final clips = st.timeline.clips;
    for (final (i, clip) in clips.indexed) {
      final l = _c.scale.xForUs(start);
      final w = _c.scale.widthForUs(clip.durationUs);
      final clipStart = start;
      start += clip.durationUs;
      if (l + w < 0 || l > _width) continue;
      final selected = clip.clipId == _c.selectedClipId;
      out.add(
        Positioned(
          left: math.max(0, l),
          top: _clipTop(t),
          width: math.max(d.targetMin, math.min(w, _width - math.max(0, l))),
          height: d.timelineClipRow,
          child: Semantics(
            button: true,
            selected: selected,
            label: s.clipSemantic(
              i + 1,
              VkFormat.timecode(clipStart),
              VkFormat.timecode(clipStart + clip.durationUs),
              VkFormat.durationSpoken(s, clip.durationUs),
            ),
            onTap: () => _c.selectClip(clip.clipId),
            customSemanticsActions: {
              if (i > 0)
                CustomSemanticsAction(label: s.text('clipMoveEarlier')): () =>
                    unawaited(_c.moveBy(clip.clipId, -1)),
              if (i < clips.length - 1)
                CustomSemanticsAction(label: s.text('clipMoveLater')): () =>
                    unawaited(_c.moveBy(clip.clipId, 1)),
            },
            child: const SizedBox.expand(),
          ),
        ),
      );
    }
    return out;
  }
}

class _TimelinePainter extends CustomPainter {
  _TimelinePainter({
    required this.state,
    required this.scale,
    required this.playheadUs,
    required this.selectedClipId,
    required this.selectedMaskId,
    required this.trim,
    required this.move,
    required this.theme,
    required this.clipLabel,
    required this.textDirection,
    this.fontFamily,
  });

  final VideoKitEditState state;
  final TimelineScale scale;
  final int playheadUs;
  final String? selectedClipId;
  final String? selectedMaskId;
  final _Trim? trim;
  final _Move? move;
  final VideoKitThemeData theme;
  final String Function(int index) clipLabel;
  final TextDirection textDirection;

  /// Family of the surrounding text (host or theme font), so painted labels
  /// match the rest of the screen.
  final String? fontFamily;

  void _text(Canvas canvas, String text, Offset at, TextStyle style) {
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: style.copyWith(fontFamily: fontFamily),
      ),
      textDirection: textDirection,
      maxLines: 1,
    )..layout();
    tp.paint(canvas, at);
  }

  @override
  void paint(Canvas canvas, Size size) {
    final t = theme;
    final d = t.dimensions;
    final c = t.colors;
    final ruler = d.spacing24;
    final clipTop = ruler + d.spacing4;
    final clipH = d.timelineClipRow;
    final maskTop = clipTop + clipH + d.spacing8;
    final duration = state.timeline.durationUs;

    // Ruler.
    final tickPaint = Paint()
      ..color = c.borderStrong
      ..strokeWidth = d.borderWidth;
    final step = scale.tickStepUs();
    final first = math.max(0, scale.usForX(0) ~/ step * step);
    for (var us = first; us <= duration; us += step) {
      final x = scale.xForUs(us);
      if (x > size.width) break;
      canvas.drawLine(Offset(x, ruler * 0.4), Offset(x, ruler), tickPaint);
      _text(
        canvas,
        VkFormat.timecode(us),
        Offset(x + d.spacing4, 0),
        t.typography.caption.copyWith(color: c.textSecondary),
      );
    }

    // Clips.
    var start = 0;
    final radius = Radius.circular(d.cornerSmall);
    for (final (i, clip) in state.timeline.clips.indexed) {
      var inUs = clip.inUs;
      var outUs = clip.outUs;
      final tr = trim;
      if (tr != null && tr.clipId == clip.clipId) {
        inUs = tr.inUs;
        outUs = tr.outUs;
      }
      final visualDuration = outUs - inUs;
      final shift = tr != null && tr.clipId == clip.clipId && tr.start
          ? inUs - clip.inUs
          : 0;
      final l = scale.xForUs(start + shift);
      final w = scale.widthForUs(visualDuration);
      final rect = Rect.fromLTWH(l, clipTop, w, clipH);
      final moving = move?.clipId == clip.clipId;
      final fill = i.isEven ? c.surfaceHigh : c.surfaceVariant;
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect.deflate(d.borderWidth), radius),
        Paint()..color = moving ? fill.withValues(alpha: 0.5) : fill,
      );
      // Thumbnail placeholders.
      final thumb = Paint()..color = c.border;
      for (var x = rect.left + clipH; x < rect.right; x += clipH) {
        canvas.drawLine(
          Offset(x, rect.top + d.spacing4),
          Offset(x, rect.bottom - d.spacing4),
          thumb,
        );
      }
      canvas
        ..save()
        ..clipRect(rect);
      _text(
        canvas,
        clipLabel(i + 1),
        Offset(rect.left + d.spacing8, rect.top + d.spacing4),
        t.typography.label.copyWith(color: c.textPrimary),
      );
      canvas.restore();
      if (clip.clipId == selectedClipId) {
        final sel = Paint()
          ..color = c.selection
          ..style = PaintingStyle.stroke
          ..strokeWidth = d.focusRingWidth * 1.5;
        canvas.drawRRect(RRect.fromRectAndRadius(rect, radius), sel);
        final handle = Paint()..color = c.selection;
        final hw = d.spacing8;
        canvas
          ..drawRRect(
            RRect.fromRectAndRadius(
              Rect.fromLTWH(rect.left - hw / 2, rect.top, hw, clipH),
              radius,
            ),
            handle,
          )
          ..drawRRect(
            RRect.fromRectAndRadius(
              Rect.fromLTWH(rect.right - hw / 2, rect.top, hw, clipH),
              radius,
            ),
            handle,
          );
      }
      start += clip.durationUs;
    }

    // Reorder insertion line.
    final m = move;
    if (m != null) {
      final starts = <int>[];
      var s = 0;
      for (final clip in state.timeline.clips) {
        starts.add(s);
        s += clip.durationUs;
      }
      starts.add(s);
      final x = scale.xForUs(starts[m.insertAt.clamp(0, starts.length - 1)]);
      canvas.drawLine(
        Offset(x, clipTop - d.spacing4),
        Offset(x, clipTop + clipH + d.spacing4),
        Paint()
          ..color = c.primary
          ..strokeWidth = d.focusRingWidth * 1.5,
      );
    }

    // Mask rows: band, keyframe diamonds, coverage.
    for (final (i, mask) in state.masks.indexed) {
      final top = maskTop + i * (d.timelineMaskRow + d.spacing4);
      final l = scale.xForUs(mask.startUs);
      final r = scale.xForUs(mask.endUs);
      final band = Rect.fromLTRB(l, top, r, top + d.timelineMaskRow);
      final run = state.tracking[mask.maskId];
      if (mask.type.isAutomatic && run != null) {
        final strip = Rect.fromLTRB(
          l,
          band.center.dy - d.timelineCoverageStrip / 2,
          r,
          band.center.dy + d.timelineCoverageStrip / 2,
        );
        for (final seg in run.coverage.segments) {
          final sl = scale.xForUs(seg.startUs);
          final sr = scale.xForUs(seg.endUs);
          if (sr <= sl) continue;
          CoveragePainter.paintState(
            canvas,
            Rect.fromLTRB(sl, strip.top, sr, strip.bottom),
            seg.state,
            t,
          );
        }
      } else {
        canvas.drawRRect(
          RRect.fromRectAndRadius(band, Radius.circular(band.height / 2)),
          Paint()
            ..color = mask.maskId == selectedMaskId
                ? c.primaryContainer
                : c.surfaceVariant,
        );
      }
      final diamond = Paint()..color = c.textPrimary;
      final k = d.timelineMaskRow * 0.3;
      // Diamonds mark user keyframes and correction points (design pages
      // 15, 19); per-frame tracker keyframes are not drawn.
      for (final kf in mask.keyframes) {
        if (kf.source == KeyframeSource.tracker) continue;
        final x = scale.xForUs(kf.atUs);
        final cy = band.center.dy;
        canvas.drawPath(
          Path()
            ..moveTo(x, cy - k)
            ..lineTo(x + k, cy)
            ..lineTo(x, cy + k)
            ..lineTo(x - k, cy)
            ..close(),
          diamond,
        );
      }
    }

    // Playhead.
    final px = scale.xForUs(playheadUs);
    final ph = Paint()
      ..color = c.primary
      ..strokeWidth = d.focusRingWidth;
    canvas
      ..drawLine(Offset(px, ruler * 0.5), Offset(px, size.height), ph)
      ..drawCircle(Offset(px, ruler * 0.5), d.spacing4 * 1.5, ph);
  }

  @override
  bool shouldRepaint(_TimelinePainter old) =>
      old.fontFamily != fontFamily ||
      old.state != state ||
      old.scale != scale ||
      old.playheadUs != playheadUs ||
      old.selectedClipId != selectedClipId ||
      old.selectedMaskId != selectedMaskId ||
      old.trim != trim ||
      old.move != move ||
      old.theme != theme;
}
