import 'dart:ui' show Locale;

/// Pseudo-localization used instead of English for layout checks until the
/// English translation batch (13 §3.1): Chinese text lengthened by about
/// 40 % and bracketed so truncation is visible.
abstract final class VkPseudo {
  /// Pseudo locale (`zh-XA`). Resolves to Chinese resources, then every
  /// string is transformed by [transform].
  static const Locale locale = Locale('zh', 'XA');

  /// Lengthening ratio.
  static const double expansion = 0.4;

  /// Whether [l] is the pseudo locale.
  static bool isPseudo(Locale? l) =>
      l != null &&
      l.languageCode == locale.languageCode &&
      l.countryCode == locale.countryCode;

  /// Brackets [text] and pads it so it is ~40 % longer (at least the two
  /// brackets are added).
  static String transform(String text) {
    if (text.isEmpty) return text;
    final length = text.runes.length;
    final added = (length * expansion).ceil();
    final pad = added > 2 ? '～' * (added - 2) : '';
    return '［$text$pad］';
  }
}
