import 'package:flutter/foundation.dart';

import '../util/undefined.dart';
import 'error_code.dart';

/// Stable, redacted error passed across the API boundary (04 §9.1).
///
/// Carries only a code and parameters; user-facing text is resolved by
/// `videokit_ui` per locale. [diagnostic] is a redacted summary without
/// paths, credentials or media names.
@immutable
final class VideoKitStableError {
  /// Creates a stable error.
  const VideoKitStableError({
    required this.code,
    required this.stage,
    this.retryable = false,
    this.suggestedAction = SuggestedAction.none,
    this.diagnostic,
  });

  /// Shortcut for [ErrorCode.internalErrorRedacted].
  const VideoKitStableError.internal({
    this.stage = ErrorStage.unknown,
    this.diagnostic,
  }) : code = ErrorCode.internalErrorRedacted,
       retryable = false,
       suggestedAction = SuggestedAction.none;

  /// Stable code.
  final ErrorCode code;

  /// Stage where the error happened.
  final ErrorStage stage;

  /// Whether retrying the same operation may succeed.
  final bool retryable;

  /// Suggested next step.
  final SuggestedAction suggestedAction;

  /// Redacted diagnostic summary (debug only), or null.
  final String? diagnostic;

  /// Returns a copy with the given fields replaced.
  VideoKitStableError copyWith({
    ErrorCode? code,
    ErrorStage? stage,
    bool? retryable,
    SuggestedAction? suggestedAction,
    Object? diagnostic = undefined,
  }) => VideoKitStableError(
    code: code ?? this.code,
    stage: stage ?? this.stage,
    retryable: retryable ?? this.retryable,
    suggestedAction: suggestedAction ?? this.suggestedAction,
    diagnostic: pick<String?>(diagnostic, this.diagnostic),
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitStableError &&
      other.code == code &&
      other.stage == stage &&
      other.retryable == retryable &&
      other.suggestedAction == suggestedAction &&
      other.diagnostic == diagnostic;

  @override
  int get hashCode =>
      Object.hash(code, stage, retryable, suggestedAction, diagnostic);

  @override
  String toString() =>
      'VideoKitStableError(${code.wireName}, stage: ${stage.wireName}, '
      'retryable: $retryable, action: ${suggestedAction.wireName}'
      '${diagnostic == null ? '' : ', diagnostic: $diagnostic'})';
}

/// Exception wrapper for APIs that cannot return a result type
/// (e.g. `restoreEditProject` rejecting an unknown future schema).
final class VideoKitException implements Exception {
  /// Wraps [error].
  const VideoKitException(this.error);

  /// The stable error.
  final VideoKitStableError error;

  @override
  String toString() => 'VideoKitException($error)';
}
