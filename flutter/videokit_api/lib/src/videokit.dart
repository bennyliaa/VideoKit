import 'package:flutter/foundation.dart';

import 'capability/capabilities.dart';
import 'edit/edit_project.dart';
import 'feature/feature.dart';
import 'feature/feature_gate.dart';
import 'host/host_callbacks.dart';
import 'resource/resource_budget.dart';
import 'session/session.dart';
import 'util/enum_codec.dart';
import 'util/undefined.dart';

/// Semantic API version `major.minor.patch` (04 §10).
@immutable
final class VideoKitApiVersion implements Comparable<VideoKitApiVersion> {
  /// Creates a version.
  const VideoKitApiVersion(this.major, this.minor, this.patch)
    : assert(major >= 0),
      assert(minor >= 0),
      assert(patch >= 0);

  /// Version implemented by this Dart package.
  static const VideoKitApiVersion current = VideoKitApiVersion(1, 0, 0);

  /// Parses `major.minor.patch`; throws [FormatException] otherwise.
  factory VideoKitApiVersion.parse(String text) {
    final parts = text.trim().split('.');
    if (parts.length != 3) {
      throw FormatException('Expected major.minor.patch', text);
    }
    final nums = parts.map(int.tryParse).toList();
    if (nums.any((n) => n == null || n < 0)) {
      throw FormatException('Expected non-negative integers', text);
    }
    return VideoKitApiVersion(nums[0]!, nums[1]!, nums[2]!);
  }

  /// Major.
  final int major;

  /// Minor.
  final int minor;

  /// Patch.
  final int patch;

  /// Whether a host built against [required] can use this version (same
  /// major, minor/patch not lower).
  bool isCompatibleWith(VideoKitApiVersion required) =>
      major == required.major && compareTo(required) >= 0;

  /// Returns a copy with the given fields replaced.
  VideoKitApiVersion copyWith({int? major, int? minor, int? patch}) =>
      VideoKitApiVersion(
        major ?? this.major,
        minor ?? this.minor,
        patch ?? this.patch,
      );

  @override
  int compareTo(VideoKitApiVersion other) {
    if (major != other.major) return major.compareTo(other.major);
    if (minor != other.minor) return minor.compareTo(other.minor);
    return patch.compareTo(other.patch);
  }

  @override
  bool operator ==(Object other) =>
      other is VideoKitApiVersion &&
      other.major == major &&
      other.minor == minor &&
      other.patch == patch;

  @override
  int get hashCode => Object.hash(major, minor, patch);

  @override
  String toString() => '$major.$minor.$patch';
}

/// Log level of [VideoKitLogger].
enum LogLevel {
  debug,
  info,
  warn,
  error;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a Dart or wire name; unknown or null → [debug].
  static LogLevel fromName(String? name) => enumFromName(values, name, debug);
}

/// Replaceable logger (13 §4). Messages are redacted: no credentials, full
/// paths, media names, media content or face data.
abstract interface class VideoKitLogger {
  /// Logs one redacted message.
  void log(LogLevel level, String tag, String message);
}

/// Logging policy (13 §4, 04A N10).
@immutable
sealed class LoggingPolicy {
  const LoggingPolicy();

  /// Release default: no logs.
  static const LoggingPolicy releaseDefault = LoggingPolicyReleaseDefault();
}

/// No logs are written (Kotlin `LoggingPolicy.ReleaseDefault`).
final class LoggingPolicyReleaseDefault extends LoggingPolicy {
  /// Creates the policy.
  const LoggingPolicyReleaseDefault();

  @override
  bool operator ==(Object other) => other is LoggingPolicyReleaseDefault;

  @override
  int get hashCode => (LoggingPolicyReleaseDefault).hashCode;

  @override
  String toString() => 'LoggingPolicy.releaseDefault';
}

/// Redacted debug diagnostics written to [logger] (Kotlin
/// `LoggingPolicy.Diagnostics`).
final class LoggingPolicyDiagnostics extends LoggingPolicy {
  /// Creates the policy.
  const LoggingPolicyDiagnostics(this.logger, {this.minLevel = LogLevel.debug});

  /// Logger.
  final VideoKitLogger logger;

  /// Minimum level.
  final LogLevel minLevel;

  @override
  bool operator ==(Object other) =>
      other is LoggingPolicyDiagnostics &&
      identical(other.logger, logger) &&
      other.minLevel == minLevel;

  @override
  int get hashCode =>
      Object.hash(LoggingPolicyDiagnostics, identityHashCode(logger), minLevel);

  @override
  String toString() => 'LoggingPolicy.diagnostics(${minLevel.name})';
}

/// VideoKit configuration (04 §2). The Android `Context` of the Kotlin
/// config has no Dart counterpart.
@immutable
final class VideoKitConfig {
  /// Creates a config.
  const VideoKitConfig({
    this.hostCallbacks = const NoopHostCallbacks(),
    this.callbackTimeouts = const HostCallbackTimeouts(),
    this.resourceBudget,
    this.logging = LoggingPolicy.releaseDefault,
    this.features = VideoKitFeatureConfig.allEnabled,
  });

  /// Static feature switches (REQ-API-10 ①); unlisted features are
  /// enabled.
  final VideoKitFeatureConfig features;

  /// The switches with the host's gate ([VideoKitHostCallbacks.checkFeature]).
  VideoKitFeatureGate get featureGate => VideoKitFeatureGate(
    config: features,
    callbacks: hostCallbacks,
    timeout: callbackTimeouts.featureGate,
  );

  /// Host callbacks.
  final VideoKitHostCallbacks hostCallbacks;

  /// Callback timeouts.
  final HostCallbackTimeouts callbackTimeouts;

  /// Host-scope budget; null = VideoKit default.
  final ResourceBudget? resourceBudget;

  /// Logging policy.
  final LoggingPolicy logging;

  /// Returns a copy with the given fields replaced.
  VideoKitConfig copyWith({
    VideoKitHostCallbacks? hostCallbacks,
    HostCallbackTimeouts? callbackTimeouts,
    Object? resourceBudget = undefined,
    LoggingPolicy? logging,
    VideoKitFeatureConfig? features,
  }) => VideoKitConfig(
    hostCallbacks: hostCallbacks ?? this.hostCallbacks,
    callbackTimeouts: callbackTimeouts ?? this.callbackTimeouts,
    resourceBudget: pick<ResourceBudget?>(resourceBudget, this.resourceBudget),
    logging: logging ?? this.logging,
    features: features ?? this.features,
  );

  @override
  bool operator ==(Object other) =>
      other is VideoKitConfig &&
      identical(other.hostCallbacks, hostCallbacks) &&
      other.callbackTimeouts == callbackTimeouts &&
      identical(other.resourceBudget, resourceBudget) &&
      other.logging == logging &&
      other.features == features;

  @override
  int get hashCode => Object.hash(
    identityHashCode(hostCallbacks),
    callbackTimeouts,
    identityHashCode(resourceBudget),
    logging,
    features,
  );

  @override
  String toString() =>
      'VideoKitConfig(${hostCallbacks.runtimeType}, $callbackTimeouts, '
      'budget: ${resourceBudget?.runtimeType}, $logging)';
}

/// VideoKit entry point (04 §2, §12.2).
abstract interface class VideoKit {
  /// Runtime API version.
  VideoKitApiVersion get apiVersion;

  /// Whether this instance is a demo/fake backend.
  bool get isDemo;

  /// Capability report.
  Future<VideoKitCapabilities> capabilities(CapabilityRequest request);

  /// Creates a session.
  Future<VideoKitSession> createSession(VideoKitSessionConfig config);

  /// Creates an edit project.
  Future<VideoKitEditProject> createEditProject(EditProjectConfig config);

  /// Restores an edit project; throws `VideoKitException` for an unknown
  /// future schema major version.
  Future<VideoKitEditProject> restoreEditProject(
    SerializedEditProject serialized,
    EditProjectConfig config,
  );

  /// Releases all sessions and projects. Idempotent.
  Future<void> close();
}
