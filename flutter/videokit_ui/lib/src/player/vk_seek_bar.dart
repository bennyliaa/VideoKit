import 'package:flutter/gestures.dart' show DragStartBehavior;
import 'package:flutter/material.dart';

import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';

/// Seek bar (14 §5.1, design pages 9–10): played, buffered and drag
/// preview layers, thumb, time bubble (and an optional preview frame) while
/// dragging. Drags only change
/// local state and report [onDragUpdate] (the owner throttles preview
/// seeks); release reports [onDragEnd] once. Screen readers get ±[stepUs]
/// increase/decrease and a spoken value ("1 分 5 秒，共 12 分 30 秒").
/// The time line always runs left to right (03 §7.4).
class VkSeekBar extends StatefulWidget {
  /// Creates a seek bar.
  const VkSeekBar({
    super.key,
    required this.positionUs,
    required this.durationUs,
    this.bufferedUs,
    this.onDragStart,
    this.onDragUpdate,
    this.onDragEnd,
    this.stepUs = 10000000,
    this.onPicture = true,
    this.previewFrame,
    this.onTapInstead,
  });

  /// Position (µs) to show when not dragging.
  final int positionUs;

  /// Duration (µs); 0 or less disables the bar.
  final int durationUs;

  /// Buffered position (µs).
  final int? bufferedUs;

  /// Drag started.
  final VoidCallback? onDragStart;

  /// Drag preview position.
  final ValueChanged<int>? onDragUpdate;

  /// Final position (one seek).
  final ValueChanged<int>? onDragEnd;

  /// Accessibility step (µs, default 10 s).
  final int stepUs;

  /// On the player picture (`apps.videokit.component.seekbar`) or on an
  /// ordinary surface (`component.slider.surface`, 14 §7.2).
  final bool onPicture;

  /// Preview frame shown above the time bubble while dragging (the player
  /// passes throttled `captureThumbnail` frames); decorative.
  final Widget? previewFrame;

  /// When set, a tap calls this instead of seeking (the player uses it while
  /// its controls are hidden: the tap shows them, TEST-R2 R2-05). Drags
  /// still seek.
  final VoidCallback? onTapInstead;

  @override
  State<VkSeekBar> createState() => _VkSeekBarState();
}

class _VkSeekBarState extends State<VkSeekBar> {
  int? _dragUs;

  /// [VkSeekBar.onTapInstead] as it was when the current tap went down.
  VoidCallback? _tapInstead;

  bool get _enabled => widget.durationUs > 0 && widget.onDragEnd != null;

  int _clamp(int us) =>
      us.clamp(0, widget.durationUs <= 0 ? 0 : widget.durationUs);

  int _atX(double x, double width) =>
      _clamp((widget.durationUs * (x / width).clamp(0.0, 1.0)).round());

  void _start(double x, double width) {
    widget.onDragStart?.call();
    setState(() => _dragUs = _atX(x, width));
    widget.onDragUpdate?.call(_dragUs!);
  }

  void _update(double x, double width) {
    setState(() => _dragUs = _atX(x, width));
    widget.onDragUpdate?.call(_dragUs!);
  }

  void _end() {
    final us = _dragUs;
    setState(() => _dragUs = null);
    if (us != null) widget.onDragEnd?.call(us);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final style = widget.onPicture
        ? t.components.seekBar
        : t.components.sliderSurface;
    final shown = _dragUs ?? _clamp(widget.positionUs);
    final duration = widget.durationUs;
    return Semantics(
      container: true,
      slider: true,
      label: s.text('playerSeekBar'),
      value: VkFormat.seekValue(s, shown, duration),
      increasedValue: VkFormat.seekValue(
        s,
        _clamp(shown + widget.stepUs),
        duration,
      ),
      decreasedValue: VkFormat.seekValue(
        s,
        _clamp(shown - widget.stepUs),
        duration,
      ),
      onIncrease: _enabled
          ? () => widget.onDragEnd!(_clamp(shown + widget.stepUs))
          : null,
      onDecrease: _enabled
          ? () => widget.onDragEnd!(_clamp(shown - widget.stepUs))
          : null,
      child: ExcludeSemantics(
        child: Directionality(
          textDirection: TextDirection.ltr,
          child: LayoutBuilder(
            builder: (context, c) {
              final width = c.maxWidth;
              return GestureDetector(
                behavior: HitTestBehavior.opaque,
                // Absolute positioning (R1-16): the drag starts where the
                // finger went down and the thumb follows the finger; screen
                // readers keep the ±step actions.
                dragStartBehavior: DragStartBehavior.down,
                onHorizontalDragStart: _enabled
                    ? (d) => _start(d.localPosition.dx, width)
                    : null,
                onHorizontalDragUpdate: _enabled
                    ? (d) => _update(d.localPosition.dx, width)
                    : null,
                onHorizontalDragEnd: _enabled ? (_) => _end() : null,
                onHorizontalDragCancel: _enabled ? _end : null,
                // TEST-R3 R3-04: whether this tap only shows the controls is
                // decided when the finger goes down. The controls appear
                // during the tap and the bar is rebuilt without
                // [onTapInstead]; the tap must still not seek. Only a drag
                // (past the touch slop) seeks while hidden.
                onTapDown: widget.onTapInstead != null || _enabled
                    ? (_) => _tapInstead = widget.onTapInstead
                    : null,
                onTapCancel: () => _tapInstead = null,
                onTapUp: widget.onTapInstead != null || _enabled
                    ? (d) {
                        final instead = _tapInstead ?? widget.onTapInstead;
                        _tapInstead = null;
                        if (instead != null) {
                          instead();
                        } else if (_enabled) {
                          widget.onDragEnd!(_atX(d.localPosition.dx, width));
                        }
                      }
                    : null,
                child: SizedBox(
                  height: t.dimensions.targetMin,
                  width: width,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Positioned.fill(
                        child: CustomPaint(
                          painter: _SeekPainter(
                            style: style,
                            played: duration <= 0
                                ? 0
                                : _clamp(widget.positionUs) / duration,
                            buffered: duration <= 0
                                ? 0
                                : _clamp(widget.bufferedUs ?? 0) / duration,
                            preview: _dragUs == null || duration <= 0
                                ? null
                                : _dragUs! / duration,
                            active: _dragUs != null,
                            enabled: _enabled,
                          ),
                        ),
                      ),
                      if (_dragUs != null && duration > 0)
                        Positioned(
                          bottom: t.dimensions.targetMin,
                          left: 0,
                          right: 0,
                          child: Align(
                            alignment: Alignment(
                              (_dragUs! / duration) * 2 - 1,
                              0,
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                if (widget.previewFrame != null) ...[
                                  widget.previewFrame!,
                                  SizedBox(height: t.dimensions.spacing4),
                                ],
                                _Bubble(
                                  style: style.bubble,
                                  text: VkFormat.timecode(_dragUs!),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _Bubble extends StatelessWidget {
  const _Bubble({required this.style, required this.text});

  final VkBoxStyle style;
  final String text;

  @override
  Widget build(BuildContext context) => Container(
    padding: style.padding,
    decoration: style.decoration,
    child: Text(text, style: style.textStyle),
  );
}

class _SeekPainter extends CustomPainter {
  _SeekPainter({
    required this.style,
    required this.played,
    required this.buffered,
    required this.preview,
    required this.active,
    required this.enabled,
  });

  final VkSeekBarStyle style;
  final double played;
  final double buffered;
  final double? preview;
  final bool active;
  final bool enabled;

  @override
  void paint(Canvas canvas, Size size) {
    final h = active ? style.trackHeightActive : style.trackHeight;
    final y = size.height / 2;
    final r = Radius.circular(h / 2);
    RRect bar(double to) => RRect.fromLTRBR(
      0,
      y - h / 2,
      size.width * to.clamp(0.0, 1.0),
      y + h / 2,
      r,
    );
    canvas
      ..drawRRect(bar(1), Paint()..color = style.track)
      ..drawRRect(bar(buffered), Paint()..color = style.buffered)
      ..drawRRect(bar(played), Paint()..color = style.played);
    final p = preview;
    if (p != null) {
      canvas.drawRRect(bar(p), Paint()..color = style.preview);
    }
    final thumbAt = (p ?? played).clamp(0.0, 1.0);
    canvas.drawCircle(
      Offset(size.width * thumbAt, y),
      style.thumbSize / 2,
      Paint()
        ..color = enabled
            ? (active ? style.thumb.pressed : style.thumb.normal)
            : style.thumb.disabled,
    );
  }

  @override
  bool shouldRepaint(_SeekPainter o) =>
      o.played != played ||
      o.buffered != buffered ||
      o.preview != preview ||
      o.active != active ||
      o.enabled != enabled ||
      o.style != style;
}
