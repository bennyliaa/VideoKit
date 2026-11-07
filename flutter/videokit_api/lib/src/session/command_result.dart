import 'package:flutter/foundation.dart';

import '../error/stable_error.dart';
import '../error/unsupported_reason.dart';

/// Result of a session command (04 §4.2).
@immutable
sealed class VideoKitCommandResult {
  const VideoKitCommandResult();
}

/// The command was executed.
final class Executed extends VideoKitCommandResult {
  /// Creates the result.
  const Executed();

  @override
  bool operator ==(Object other) => other is Executed;

  @override
  int get hashCode => (Executed).hashCode;

  @override
  String toString() => 'Executed()';
}

/// Refused, e.g. illegal state transition.
final class Rejected extends VideoKitCommandResult {
  /// Creates the result.
  const Rejected(this.error);

  /// Why.
  final VideoKitStableError error;

  /// Returns a copy with the given fields replaced.
  Rejected copyWith({VideoKitStableError? error}) =>
      Rejected(error ?? this.error);

  @override
  bool operator ==(Object other) => other is Rejected && other.error == error;

  @override
  int get hashCode => Object.hash(Rejected, error);

  @override
  String toString() => 'Rejected($error)';
}

/// Replaced by a later command of the same kind (e.g. rapid seeks).
final class Superseded extends VideoKitCommandResult {
  /// Creates the result.
  const Superseded();

  @override
  bool operator ==(Object other) => other is Superseded;

  @override
  int get hashCode => (Superseded).hashCode;

  @override
  String toString() => 'Superseded()';
}

/// Not supported by capability.
final class Unsupported extends VideoKitCommandResult {
  /// Creates the result.
  const Unsupported(this.reason);

  /// Why.
  final UnsupportedReason reason;

  /// Returns a copy with the given fields replaced.
  Unsupported copyWith({UnsupportedReason? reason}) =>
      Unsupported(reason ?? this.reason);

  @override
  bool operator ==(Object other) =>
      other is Unsupported && other.reason == reason;

  @override
  int get hashCode => Object.hash(Unsupported, reason);

  @override
  String toString() => 'Unsupported(${reason.name})';
}

/// The session is already released.
final class SessionReleased extends VideoKitCommandResult {
  /// Creates the result.
  const SessionReleased();

  @override
  bool operator ==(Object other) => other is SessionReleased;

  @override
  int get hashCode => (SessionReleased).hashCode;

  @override
  String toString() => 'SessionReleased()';
}
