import 'package:intl/intl.dart' as intl;

import '../l10n/vk_strings.dart';

/// Locale-aware formatting (13 §3.1): numbers, percentages, file sizes and
/// spoken durations follow the current locale via `intl`; timecodes use
/// ASCII digits (rendered with the tabular-figures timecode style).
abstract final class VkFormat {
  static String _locale(VkStrings s) =>
      intl.Intl.verifiedLocale(
        s.intlLocale,
        intl.NumberFormat.localeExists,
        onFailure: (_) => 'zh',
      ) ??
      'zh';

  /// Timecode `mm:ss` / `h:mm:ss` (design pages 5 and 9: "01:24 / 05:12";
  /// locale independent, for tabular display).
  static String timecode(int us) {
    final total = us < 0 ? 0 : us ~/ 1000000;
    final h = total ~/ 3600;
    final m = ((total % 3600) ~/ 60).toString().padLeft(2, '0');
    final sec = (total % 60).toString().padLeft(2, '0');
    return h > 0 ? '$h:$m:$sec' : '$m:$sec';
  }

  /// Spoken duration for screen readers, e.g. "1 分 5 秒".
  static String durationSpoken(VkStrings s, int us) {
    final total = us < 0 ? 0 : us ~/ 1000000;
    return s.durationSpoken(total ~/ 3600, (total % 3600) ~/ 60, total % 60);
  }

  /// Seek bar semantics value "position，共 duration".
  static String seekValue(VkStrings s, int positionUs, int durationUs) =>
      s.seekValue(durationSpoken(s, positionUs), durationSpoken(s, durationUs));

  /// Decimal number in the current locale.
  static String number(
    VkStrings s,
    num value, {
    int maxFractionDigits = 1,
    int minFractionDigits = 0,
  }) =>
      (intl.NumberFormat.decimalPattern(_locale(s))
            ..minimumFractionDigits = minFractionDigits
            ..maximumFractionDigits = maxFractionDigits)
          .format(value);

  /// Playback speed "1.0×", "0.75×" (design page 11: at least one decimal).
  static String speed(VkStrings s, double value) => s.speedValue(
    number(s, value, minFractionDigits: 1, maxFractionDigits: 2),
  );

  /// Percentage (0–1) in the current locale.
  static String percent(VkStrings s, double fraction) =>
      intl.NumberFormat.percentPattern(_locale(s)).format(fraction);

  /// File size with decimal units (1 KB = 1000 B, as Android `Formatter`;
  /// 04A B8).
  /// Bit rate with decimal units (kbps below 1 Mbps).
  static String bitrate(VkStrings s, int bitsPerSecond) {
    final mega = bitsPerSecond >= 1000000;
    return s.infoBitrateValue(
      number(
        s,
        bitsPerSecond / (mega ? 1000000 : 1000),
        maxFractionDigits: mega ? 1 : 0,
      ),
      mega: mega,
    );
  }

  /// Frame rate, up to two decimals (29.97).
  static String frameRate(VkStrings s, double fps) =>
      s.infoFrameRateValue(number(s, fps, maxFractionDigits: 2));

  static String fileSize(VkStrings s, int bytes) {
    var value = bytes.toDouble();
    var unit = 0;
    while (value >= 1000 && unit < 3) {
      value /= 1000;
      unit++;
    }
    return s.fileSize(
      number(s, value, maxFractionDigits: unit == 0 ? 0 : 1),
      unit,
    );
  }
}
