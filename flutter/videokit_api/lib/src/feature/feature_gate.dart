import 'dart:async';

import 'package:flutter/foundation.dart';

import '../error/error_code.dart';
import '../error/stable_error.dart';
import '../host/host_callbacks.dart';
import 'feature.dart';

/// Static switches plus the host's dynamic gate, as one helper (REQ-API-10)
/// shared by the Fake, the plugin and `videokit_ui`: [isEnabled] for
/// entries and API checks, [check] before entering a feature.
@immutable
final class VideoKitFeatureGate {
  /// Creates the gate.
  const VideoKitFeatureGate({
    this.config = VideoKitFeatureConfig.allEnabled,
    this.callbacks = const NoopHostCallbacks(),
    this.timeout = const Duration(seconds: 30),
  });

  /// Everything enabled and allowed (a host that configures nothing).
  static const VideoKitFeatureGate open = VideoKitFeatureGate();

  /// Static switches.
  final VideoKitFeatureConfig config;

  /// Host callbacks (`checkFeature`).
  final VideoKitHostCallbacks callbacks;

  /// `checkFeature` timeout.
  final Duration timeout;

  /// Whether [feature] is enabled (dependencies included).
  bool isEnabled(VideoKitFeature feature) => config.isEnabled(feature);

  /// Asks the host whether [feature] may be entered now. A hidden feature
  /// throws `FEATURE_DISABLED` (as in Kotlin) and the host is not asked; a
  /// throw or a timeout of the host counts as denied without a marker;
  /// [VideoKitFeature.unknown] is always allowed. Callers check
  /// [isEnabled] first where hiding is a normal case (UI entries).
  Future<FeatureAccess> check(
    VideoKitFeature feature, {
    String? sessionId,
    ErrorStage stage = ErrorStage.edit,
  }) async {
    if (feature == VideoKitFeature.unknown) return FeatureAccess.allowed;
    if (!isEnabled(feature)) {
      throw VideoKitException(disabledError(feature, stage: stage));
    }
    // A host without a gate: no callback, no timer (FT01B-03).
    if (callbacks.runtimeType == NoopHostCallbacks) {
      return FeatureAccess.allowed;
    }
    try {
      return await callbacks
          .checkFeature(feature, sessionId)
          .timeout(timeout);
    } on Object {
      return const FeatureDenied(null);
    }
  }

  /// `FEATURE_DISABLED` for [feature] at [stage].
  static VideoKitStableError disabledError(
    VideoKitFeature feature, {
    ErrorStage stage = ErrorStage.edit,
  }) => VideoKitStableError(
    code: ErrorCode.featureDisabled,
    stage: stage,
    params: {'feature': feature.wireName},
  );

  /// `FEATURE_DENIED` for [feature] (with the host's [badge]) at [stage].
  static VideoKitStableError deniedError(
    VideoKitFeature feature, {
    FeatureBadge? badge,
    ErrorStage stage = ErrorStage.edit,
  }) => VideoKitStableError(
    code: ErrorCode.featureDenied,
    stage: stage,
    retryable: true,
    params: {'feature': feature.wireName, 'badge': ?badge?.wireName},
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitFeatureGate &&
      other.config == config &&
      identical(other.callbacks, callbacks) &&
      other.timeout == timeout;

  @override
  int get hashCode =>
      Object.hash(config, identityHashCode(callbacks), timeout);
}
