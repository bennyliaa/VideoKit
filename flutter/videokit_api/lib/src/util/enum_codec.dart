/// Converts lowerCamelCase enum names to/from the SCREAMING_SNAKE_CASE wire
/// names used by the native API and the Pigeon channel.
library;

/// `sourceNotFound` → `SOURCE_NOT_FOUND`.
String toWireName(String camel) {
  final buffer = StringBuffer();
  for (var i = 0; i < camel.length; i++) {
    final ch = camel[i];
    final isUpper = ch.toUpperCase() == ch && ch.toLowerCase() != ch;
    final isDigit = ch.codeUnitAt(0) >= 0x30 && ch.codeUnitAt(0) <= 0x39;
    if (i > 0 && (isUpper || (isDigit && !_isDigitAt(camel, i - 1)))) {
      buffer.write('_');
    }
    buffer.write(ch.toUpperCase());
  }
  return buffer.toString();
}

bool _isDigitAt(String s, int i) {
  final c = s.codeUnitAt(i);
  return c >= 0x30 && c <= 0x39;
}

/// Looks up an enum value by its Dart name or wire name; returns [fallback]
/// for unknown or null names.
T enumFromName<T extends Enum>(List<T> values, String? name, T fallback) {
  if (name == null) return fallback;
  for (final v in values) {
    if (v.name == name || toWireName(v.name) == name) return v;
  }
  return fallback;
}
