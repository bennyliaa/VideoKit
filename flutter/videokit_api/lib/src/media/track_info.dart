import 'package:flutter/foundation.dart';

import '../util/undefined.dart';

/// One audio or subtitle track (04 §3.1, 06 §4).
@immutable
final class TrackInfo {
  /// Creates a track description.
  const TrackInfo({
    required this.id,
    this.language,
    this.label,
    this.codec,
    this.supported = true,
  });

  /// Opaque track ID.
  final String id;

  /// BCP-47 language tag, if known.
  final String? language;

  /// Display label from the container, if any.
  final String? label;

  /// Codec MIME type or name, if known.
  final String? codec;

  /// Whether this device can decode/render the track.
  final bool supported;

  /// Returns a copy with the given fields replaced.
  TrackInfo copyWith({
    String? id,
    Object? language = undefined,
    Object? label = undefined,
    Object? codec = undefined,
    bool? supported,
  }) => TrackInfo(
    id: id ?? this.id,
    language: pick<String?>(language, this.language),
    label: pick<String?>(label, this.label),
    codec: pick<String?>(codec, this.codec),
    supported: supported ?? this.supported,
  );

  @override
  bool operator ==(Object other) =>
      other is TrackInfo &&
      other.id == id &&
      other.language == language &&
      other.label == label &&
      other.codec == codec &&
      other.supported == supported;

  @override
  int get hashCode => Object.hash(id, language, label, codec, supported);

  @override
  String toString() =>
      'TrackInfo($id, lang: $language, label: $label, codec: $codec, '
      'supported: $supported)';
}
