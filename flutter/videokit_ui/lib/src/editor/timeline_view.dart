import 'dart:async';
import 'dart:math' as math;
import 'dart:ui' as ui;

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

  /// Source-time step of the thumbnails of a local source (X2, frozen).
  static const int thumbStepUs = 500000;

  /// Step for a [SourceLatency.slow] source (X2, frozen): fewer reads.
  static const int thumbStepSlowUs = 2000000;

  /// Thumbnail step for a source of [latency].
  static int thumbStepFor(SourceLatency latency) =>
      latency == SourceLatency.slow ? thumbStepSlowUs : thumbStepUs;

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

  // ------------------------------------- thumbnails / waveform (A4) --

  /// Most decoded thumbnails kept.
  static const int thumbCacheLimit = 160;

  final Map<String, ui.Image> _thumbs = {};
  final Map<String, List<double>> _waves = {};
  final Set<String> _requested = {};
  int _mediaRevision = 0;
  bool _disposed = false;

  VideoKitEditMediaPreview? get _media => switch (_c.project) {
    final VideoKitEditMediaPreview m => m,
    _ => null,
  };

  /// Thumbnail of [sourceId] near [sourceUs], or null (requested then;
  /// the timeline repaints when it arrives).
  ui.Image? _thumbFor(String sourceId, int sourceUs) {
    final media = _media;
    if (media == null) return null;
    final step = TimelineView.thumbStepFor(_c.latencyOf(sourceId));
    final at = sourceUs ~/ step * step;
    final key = '$sourceId@$at';
    final hit = _thumbs.remove(key);
    if (hit != null) {
      _thumbs[key] = hit; // most recent last
      return hit;
    }
    if (_requested.add(key)) {
      // Never inside paint: start after this frame.
      unawaited(
        Future(() async {
          final bytes = await media.sourceThumbnail(sourceId, at);
          if (bytes == null || _disposed) return;
          final codec = await ui.instantiateImageCodec(bytes);
          final frame = await codec.getNextFrame();
          codec.dispose();
          if (_disposed) {
            frame.image.dispose();
            return;
          }
          _thumbs[key] = frame.image;
          while (_thumbs.length > thumbCacheLimit) {
            final oldest = _thumbs.keys.first;
            _thumbs.remove(oldest)?.dispose();
            _requested.remove(oldest);
          }
          if (mounted) setState(() => _mediaRevision++);
        }).catchError((Object _) {}),
      );
    }
    return null;
  }

  /// Waveform peaks of [clip] (empty: no audio), or null while loading.
  List<double>? _waveFor(EditClip clip) {
    final media = _media;
    if (media == null) return null;
    final key = '${clip.sourceId}:${clip.inUs}:${clip.outUs}';
    final hit = _waves[key];
    if (hit != null) return hit;
    if (_requested.add(key)) {
      final buckets = (clip.durationUs / 1e5).round().clamp(16, 600);
      unawaited(
        Future(() async {
          final peaks = await media.sourceWaveform(
            clip.sourceId,
            clip.inUs,
            clip.outUs,
            buckets,
          );
          if (_disposed) return;
          _waves[key] = peaks;
          if (mounted) setState(() => _mediaRevision++);
        }).catchError((Object _) {}),
      );
    }
    return null;
  }

  @override
  void dispose() {
    _disposed = true;
    for (final i in _thumbs.values) {
      i.dispose();
    }
    _thumbs.clear();
    super.dispose();
  }

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
      final maxOut = src?.probe?.durationUs ?? clip.outUs;
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
            // Design page 15 item 5: the mask track is always there (one
            // empty lane before the first mask).
            math.max(1, masks.length) * (d.timelineMaskRow + d.spacing4) +
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
                                    maskTrackEmpty: s.text(
                                      'timelineMaskTrackEmpty',
                                    ),
                                    thumbFor: _media == null
                                        ? null
                                        : _thumbFor,
                                    waveFor: _media == null ? null : _waveFor,
                                    mediaRevision: _mediaRevision,
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
              VkFormat.timecodeTenths(clipStart),
              VkFormat.timecodeTenths(clipStart + clip.durationUs),
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
    required this.maskTrackEmpty,
    required this.textDirection,
    this.fontFamily,
    this.thumbFor,
    this.waveFor,
    this.mediaRevision = 0,
  });

  /// Thumbnail lookup (null: the project has no timeline media).
  final ui.Image? Function(String sourceId, int sourceUs)? thumbFor;

  /// Waveform lookup (null: the project has no timeline media).
  final List<double>? Function(EditClip clip)? waveFor;

  /// Bumped when a thumbnail or waveform arrives.
  final int mediaRevision;

  /// Text in the empty mask track.
  final String maskTrackEmpty;

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
      // Design pages 15/16: thumbnail film with the audio waveform along
      // the bottom (when the project offers timeline media), otherwise
      // placeholder frame lines.
      final inner = rect.deflate(d.borderWidth);
      final wave = waveFor?.call(clip);
      final waveH = wave == null ? 0.0 : inner.height * 0.3;
      final film = Rect.fromLTRB(
        inner.left,
        inner.top,
        inner.right,
        inner.bottom - waveH,
      );
      final probe = state.timeline.sourceById(clip.sourceId)?.probe;
      final aspect = probe != null && probe.height > 0
          ? probe.width / probe.height
          : 16 / 9;
      final tileW = math.max(d.spacing8, film.height * aspect);
      canvas
        ..save()
        ..clipRRect(RRect.fromRectAndRadius(inner, radius));
      var drewThumb = false;
      final lookup = thumbFor;
      if (lookup != null && w > 0) {
        for (var x = film.left; x < film.right; x += tileW) {
          if (x + tileW < 0 || x > size.width) continue;
          final frac = ((x - rect.left + tileW / 2) / w).clamp(0.0, 1.0);
          final srcUs = (inUs + frac * visualDuration).round().clamp(
            inUs,
            math.max(inUs, outUs - 1),
          );
          final img = lookup(clip.sourceId, srcUs);
          if (img == null) continue;
          drewThumb = true;
          final dst = Rect.fromLTWH(x, film.top, tileW, film.height);
          // Cover: crop the picture to the tile's aspect.
          final iw = img.width.toDouble();
          final ih = img.height.toDouble();
          final scaleCover = math.max(dst.width / iw, dst.height / ih);
          final sw = dst.width / scaleCover;
          final sh = dst.height / scaleCover;
          canvas.drawImageRect(
            img,
            Rect.fromLTWH((iw - sw) / 2, (ih - sh) / 2, sw, sh),
            dst,
            Paint()
              ..filterQuality = FilterQuality.low
              ..color = moving ? c.textPrimary.withValues(alpha: 0.5) : c.textPrimary,
          );
        }
      }
      if (!drewThumb) {
        final thumb = Paint()..color = c.border;
        for (var x = rect.left + clipH; x < rect.right; x += clipH) {
          canvas.drawLine(
            Offset(x, rect.top + d.spacing4),
            Offset(x, film.bottom - d.spacing4),
            thumb,
          );
        }
      }
      if (wave != null && waveH > 0) {
        final band = Rect.fromLTRB(inner.left, film.bottom, inner.right, inner.bottom);
        canvas.drawRect(band, Paint()..color = c.surface.withValues(alpha: 0.72));
        final wavePaint = Paint()..color = c.textSecondary;
        if (wave.isEmpty || wave.every((p) => p <= 0)) {
          // No audio or silence: a flat line.
          canvas.drawLine(
            Offset(band.left, band.center.dy),
            Offset(band.right, band.center.dy),
            wavePaint..strokeWidth = d.borderWidth,
          );
        } else {
          final barW = band.width / wave.length;
          for (final (j, p) in wave.indexed) {
            final hgt = math.max(d.borderWidth, p.clamp(0.0, 1.0) * band.height * 0.9);
            canvas.drawRect(
              Rect.fromCenter(
                center: Offset(band.left + barW * (j + 0.5), band.center.dy),
                width: math.max(d.borderWidth, barW * 0.6),
                height: hgt,
              ),
              wavePaint,
            );
          }
        }
      }
      // Clip label on a scrim so it stays readable over the film.
      final labelStyle = t.typography.label.copyWith(color: c.textPrimary);
      final label = TextPainter(
        text: TextSpan(
          text: clipLabel(i + 1),
          style: labelStyle.copyWith(fontFamily: fontFamily),
        ),
        textDirection: textDirection,
        maxLines: 1,
      )..layout();
      final labelAt = Offset(rect.left + d.spacing8, rect.top + d.spacing4);
      if (drewThumb) {
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(
              labelAt.dx - d.spacing4,
              labelAt.dy,
              label.width + d.spacing8,
              label.height,
            ),
            radius,
          ),
          Paint()..color = c.surface.withValues(alpha: 0.72),
        );
      }
      label.paint(canvas, labelAt);
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

    // Mask track (design page 15 item 5): one lane per mask over the whole
    // timeline; automatic masks are coloured by tracking state, manual
    // ones are one colour; diamonds are keyframes.
    final lanePaint = Paint()..color = c.surfaceVariant.withValues(alpha: 0.4);
    final laneR = Radius.circular(d.timelineMaskRow / 2);
    final laneL = scale.xForUs(0);
    final laneEnd = scale.xForUs(duration);
    for (var i = 0; i < math.max(1, state.masks.length); i++) {
      final top = maskTop + i * (d.timelineMaskRow + d.spacing4);
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTRB(laneL, top, laneEnd, top + d.timelineMaskRow),
          laneR,
        ),
        lanePaint,
      );
    }
    if (state.masks.isEmpty) {
      final style = t.typography.caption.copyWith(color: c.textSecondary);
      final lineH = (style.fontSize ?? d.spacing12) * (style.height ?? 1.3);
      _text(
        canvas,
        maskTrackEmpty,
        Offset(
          math.max(0, laneL) + d.spacing8,
          maskTop + (d.timelineMaskRow - lineH) / 2,
        ),
        style,
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
      old.maskTrackEmpty != maskTrackEmpty ||
      old.mediaRevision != mediaRevision ||
      (old.thumbFor == null) != (thumbFor == null) ||
      old.state != state ||
      old.scale != scale ||
      old.playheadUs != playheadUs ||
      old.selectedClipId != selectedClipId ||
      old.selectedMaskId != selectedMaskId ||
      old.trim != trim ||
      old.move != move ||
      old.theme != theme;
}
