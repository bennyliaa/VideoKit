/// Sentinel used by `copyWith` to tell "argument omitted" apart from an
/// explicit `null` for nullable fields. Internal to `videokit_api`.
library;

/// Marker type for omitted `copyWith` arguments.
final class Undefined {
  const Undefined._();
}

/// The single sentinel instance; compare with [identical].
const Object undefined = Undefined._();

/// Returns [current] when [value] is the [undefined] sentinel, else [value]
/// cast to [T]. An `int` passed for a `double`/`double?` field is widened,
/// because nullable `copyWith` parameters are typed `Object?` and integer
/// literals would otherwise fail the cast.
T pick<T>(Object? value, T current) {
  if (identical(value, undefined)) return current;
  if (value is int && <T>[] is List<double?>) return value.toDouble() as T;
  return value as T;
}
