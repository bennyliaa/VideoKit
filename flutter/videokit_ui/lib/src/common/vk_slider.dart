import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../theme/theme_scope.dart';

/// Horizontal value slider (volume, mask strength) drawn from the slider
/// tokens. Continuous drags only change the local value; [onChangeEnd]
/// fires once at the end (14 §6.3). Screen readers get increase/decrease
/// actions with [step].
class VkSlider extends StatefulWidget {
  /// Creates a slider for a value in 0–1.
  const VkSlider({
    super.key,
    required this.value,
    required this.semanticLabel,
    required this.semanticValue,
    this.onChanged,
    this.onChangeEnd,
    this.step = 0.1,
    this.onPicture = false,
  });

  /// Value 0–1.
  final double value;

  /// Screen-reader label.
  final String semanticLabel;

  /// Formats a value for screen readers.
  final String Function(double value) semanticValue;

  /// Every value change, including the final one (local visual state).
  final ValueChanged<double>? onChanged;

  /// Final value (commits a command).
  final ValueChanged<double>? onChangeEnd;

  /// Accessibility/keyboard step.
  final double step;

  /// Uses the seek bar style on the player picture; otherwise the
  /// `component.slider.surface` variant (14, M0-B2 review rule).
  final bool onPicture;

  @override
  State<VkSlider> createState() => _VkSliderState();
}

class _VkSliderState extends State<VkSlider> {
  double? _drag;

  double get _value => (_drag ?? widget.value).clamp(0.0, 1.0);

  /// Usable as soon as either callback is given (R1-01: a slider with only
  /// [VkSlider.onChanged] is not disabled).
  bool get _enabled => widget.onChanged != null || widget.onChangeEnd != null;

  void _set(double v, {required bool end}) {
    final c = v.clamp(0.0, 1.0);
    if (end) {
      setState(() => _drag = null);
      // The final value reaches both callbacks (taps, keys and screen
      // reader steps have no drag updates before it).
      widget.onChanged?.call(c);
      widget.onChangeEnd?.call(c);
    } else {
      setState(() => _drag = c);
      widget.onChanged?.call(c);
    }
  }

  double _fraction(Offset local, double width) {
    final dir = Directionality.of(context);
    final f = (local.dx / width).clamp(0.0, 1.0);
    return dir == TextDirection.rtl ? 1 - f : f;
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = widget.onPicture
        ? t.components.seekBar
        : t.components.sliderSurface;
    final v = _value;
    return Semantics(
      slider: true,
      label: widget.semanticLabel,
      value: widget.semanticValue(v),
      increasedValue: widget.semanticValue((v + widget.step).clamp(0, 1)),
      decreasedValue: widget.semanticValue((v - widget.step).clamp(0, 1)),
      onIncrease: _enabled ? () => _set(v + widget.step, end: true) : null,
      onDecrease: _enabled ? () => _set(v - widget.step, end: true) : null,
      child: Focus(
        canRequestFocus: _enabled,
        onKeyEvent: (node, e) {
          if (e is! KeyDownEvent || !_enabled) return KeyEventResult.ignored;
          if (e.logicalKey == LogicalKeyboardKey.arrowRight) {
            _set(v + widget.step, end: true);
            return KeyEventResult.handled;
          }
          if (e.logicalKey == LogicalKeyboardKey.arrowLeft) {
            _set(v - widget.step, end: true);
            return KeyEventResult.handled;
          }
          return KeyEventResult.ignored;
        },
        child: LayoutBuilder(
          builder: (context, c) {
            final width = c.maxWidth.isFinite
                ? c.maxWidth
                : t.dimensions.targetMin * 3;
            return GestureDetector(
              behavior: HitTestBehavior.opaque,
              onHorizontalDragUpdate: _enabled
                  ? (d) => _set(_fraction(d.localPosition, width), end: false)
                  : null,
              onHorizontalDragEnd: _enabled
                  ? (_) => _set(_value, end: true)
                  : null,
              onTapUp: _enabled
                  ? (d) => _set(_fraction(d.localPosition, width), end: true)
                  : null,
              child: SizedBox(
                width: width,
                height: t.dimensions.targetMin,
                child: CustomPaint(
                  painter: _SliderPainter(
                    value: v,
                    track: s.track,
                    active: _enabled ? s.played : t.colors.disabledContent,
                    thumb: _enabled ? s.thumb.normal : s.thumb.disabled,
                    height: _drag == null ? s.trackHeight : s.trackHeightActive,
                    thumbSize: s.thumbSize,
                    rtl: Directionality.of(context) == TextDirection.rtl,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _SliderPainter extends CustomPainter {
  _SliderPainter({
    required this.value,
    required this.track,
    required this.active,
    required this.thumb,
    required this.height,
    required this.thumbSize,
    required this.rtl,
  });

  final double value;
  final Color track;
  final Color active;
  final Color thumb;
  final double height;
  final double thumbSize;
  final bool rtl;

  @override
  void paint(Canvas canvas, Size size) {
    final y = size.height / 2;
    final r = Radius.circular(height / 2);
    final x = size.width * (rtl ? 1 - value : value);
    canvas.drawRRect(
      RRect.fromLTRBR(0, y - height / 2, size.width, y + height / 2, r),
      Paint()..color = track,
    );
    final (l, rr) = rtl ? (x, size.width) : (0.0, x);
    canvas
      ..drawRRect(
        RRect.fromLTRBR(l, y - height / 2, rr, y + height / 2, r),
        Paint()..color = active,
      )
      ..drawCircle(Offset(x, y), thumbSize / 2, Paint()..color = thumb);
  }

  @override
  bool shouldRepaint(_SliderPainter o) =>
      o.value != value ||
      o.track != track ||
      o.active != active ||
      o.thumb != thumb ||
      o.height != height ||
      o.rtl != rtl;
}
