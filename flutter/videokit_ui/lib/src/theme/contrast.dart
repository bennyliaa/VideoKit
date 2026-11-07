import 'dart:math' as math;

import 'package:flutter/painting.dart';

/// WCAG 2.x contrast helpers used to derive "on" colours (14 §7.1).
abstract final class VkContrast {
  /// WCAG AA threshold for normal text.
  static const double aaNormalText = 4.5;

  /// Pure black.
  static const Color black = Color(0xFF000000);

  /// Pure white.
  static const Color white = Color(0xFFFFFFFF);

  static double _channel(double c) =>
      c <= 0.03928 ? c / 12.92 : math.pow((c + 0.055) / 1.055, 2.4).toDouble();

  /// Relative luminance of [color] (alpha ignored).
  static double luminance(Color color) =>
      0.2126 * _channel(color.r) +
      0.7152 * _channel(color.g) +
      0.0722 * _channel(color.b);

  /// Contrast ratio between [a] and [b] (1–21).
  static double ratio(Color a, Color b) {
    final la = luminance(a);
    final lb = luminance(b);
    final hi = math.max(la, lb);
    final lo = math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  }

  /// Black or white, whichever contrasts more with [background].
  static Color bestOn(Color background) =>
      ratio(black, background) >= ratio(white, background) ? black : white;

  /// [preferred] if it meets [minimum] against [background], else [bestOn].
  static Color ensure(
    Color preferred,
    Color background, {
    double minimum = aaNormalText,
  }) =>
      ratio(preferred, background) >= minimum ? preferred : bestOn(background);

  /// [foreground] blended over [background] at [amount] (0–1), opaque.
  static Color blend(Color foreground, Color background, double amount) =>
      Color.alphaBlend(foreground.withValues(alpha: amount), background);
}
