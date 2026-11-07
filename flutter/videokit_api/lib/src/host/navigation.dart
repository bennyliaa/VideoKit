import 'package:flutter/foundation.dart';

import '../util/enum_codec.dart';
import '../util/undefined.dart';

/// Direction of a navigation request (05 §6, 06 §6.3).
enum NavigationDirection {
  previous,
  next;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [next].
  static NavigationDirection fromName(String? name) =>
      enumFromName(values, name, next);
}

/// Request to move to a neighbouring media item; the host decides (05 §6).
@immutable
final class NavigationRequest {
  /// Creates a request.
  const NavigationRequest({
    required this.sessionId,
    required this.direction,
    this.mediaToken,
  });

  /// Session ID.
  final String sessionId;

  /// Direction.
  final NavigationDirection direction;

  /// Currently bound media token, if any.
  final String? mediaToken;

  /// Returns a copy with the given fields replaced.
  NavigationRequest copyWith({
    String? sessionId,
    NavigationDirection? direction,
    Object? mediaToken = undefined,
  }) => NavigationRequest(
    sessionId: sessionId ?? this.sessionId,
    direction: direction ?? this.direction,
    mediaToken: pick<String?>(mediaToken, this.mediaToken),
  );

  @override
  bool operator ==(Object other) =>
      other is NavigationRequest &&
      other.sessionId == sessionId &&
      other.direction == direction &&
      other.mediaToken == mediaToken;

  @override
  int get hashCode => Object.hash(sessionId, direction, mediaToken);

  @override
  String toString() =>
      'NavigationRequest($sessionId, ${direction.name}, media: $mediaToken)';
}

/// Host answer to a navigation request (14 §5.3).
enum NavigationResult {
  /// Host navigates (typically re-binds the session).
  accepted,

  /// No item in that direction; the UI bounces back and shows a hint.
  unavailable,

  /// Host failed or timed out.
  failed;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [failed].
  static NavigationResult fromName(String? name) =>
      enumFromName(values, name, failed);
}
