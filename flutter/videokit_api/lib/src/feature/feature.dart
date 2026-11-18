import 'package:flutter/foundation.dart';

import '../util/enum_codec.dart';

/// A feature the host can hide or gate (REQ-API-10, VK-A2; confirmed list
/// 2026-11-08). Playback and image viewing are not features in this sense:
/// they can never be hidden or gated.
///
/// [maskTracking] and [avatar] depend on [edit]: hiding [edit] hides them
/// too ([requires]). The dynamic gate is asked only for the feature named;
/// the host encodes any dependency in its own answers. No quotas.
///
/// Kotlin naming is aligned by B (`VideoKitFeature`, wire names below).
enum VideoKitFeature {
  /// Multi-view grids.
  multiView,

  /// Editing and concatenation, including saving and restoring projects.
  edit,

  /// Manual masks and automatic tracking.
  maskTracking,

  /// Avatar replacement, including the avatar tools (cut-out).
  avatar,

  /// Export of edit projects.
  export,

  /// A feature this version does not know (wire fallback); never hidden
  /// and never gated.
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// The feature this one needs, or null.
  VideoKitFeature? get requires => switch (this) {
    maskTracking || avatar => edit,
    _ => null,
  };

  /// The features a host can configure (without [unknown]).
  static const List<VideoKitFeature> configurable = [
    multiView,
    edit,
    maskTracking,
    avatar,
    export,
  ];

  /// Parses a Dart or wire name; unknown → [unknown].
  static VideoKitFeature fromName(String? name) =>
      enumFromName(values, name, unknown);
}

/// Static switch of a feature in [VideoKitFeatureConfig] (REQ-API-10 ①).
enum FeatureMode {
  /// Available (default).
  enabled,

  /// Hidden: no entry in the UI; API calls answer `FEATURE_DISABLED`.
  hidden;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a name; unknown → [enabled] (an unknown switch never hides).
  static FeatureMode fromName(String? name) =>
      enumFromName(values, name, enabled);
}

/// The static switches of a VideoKit instance (`VideoKitConfig.features`).
@immutable
final class VideoKitFeatureConfig {
  /// Creates switches; features not in [modes] are enabled.
  const VideoKitFeatureConfig([this.modes = const {}]);

  /// Everything enabled.
  static const VideoKitFeatureConfig allEnabled = VideoKitFeatureConfig();

  /// Switches as configured.
  final Map<VideoKitFeature, FeatureMode> modes;

  /// Effective mode: hidden when the feature or what it [requires] is
  /// hidden; [VideoKitFeature.unknown] is always enabled.
  FeatureMode modeOf(VideoKitFeature feature) {
    if (feature == VideoKitFeature.unknown) return FeatureMode.enabled;
    if (modes[feature] == FeatureMode.hidden) return FeatureMode.hidden;
    final parent = feature.requires;
    return parent == null ? FeatureMode.enabled : modeOf(parent);
  }

  /// Whether [feature] is enabled (shown, callable).
  bool isEnabled(VideoKitFeature feature) =>
      modeOf(feature) == FeatureMode.enabled;

  /// Returns a copy with [feature] set to [mode].
  VideoKitFeatureConfig withMode(VideoKitFeature feature, FeatureMode mode) =>
      VideoKitFeatureConfig({...modes, feature: mode});

  @override
  bool operator ==(Object other) =>
      other is VideoKitFeatureConfig && mapEquals(other.modes, modes);

  @override
  int get hashCode => Object.hashAllUnordered(
    modes.entries.map((e) => Object.hash(e.key, e.value)),
  );

  @override
  String toString() => 'VideoKitFeatureConfig($modes)';
}

/// Marker the host wants on the entry of a feature (REQ-API-10 ②). The Kit
/// shows no text of its own; `videokit_ui` draws the marker and its label.
enum FeatureBadge {
  /// Locked: the host will ask the user to subscribe or buy.
  lock,

  /// Available during a trial.
  trial,

  /// Unknown marker (wire fallback); drawn as no marker.
  unknown;

  /// SCREAMING_SNAKE_CASE wire name.
  String get wireName => toWireName(name);

  /// Parses a name; null stays null; unknown → [unknown].
  static FeatureBadge? fromName(String? name) =>
      name == null ? null : enumFromName(values, name, unknown);
}

/// Answer of the dynamic feature gate `VideoKitHostCallbacks.checkFeature`
/// (REQ-API-10 ②).
@immutable
sealed class FeatureAccess {
  const FeatureAccess(this.badge);

  /// Allowed without a marker: the answer of a host without a gate.
  static const FeatureAccess allowed = FeatureAllowed();

  /// Marker for the entry, or null.
  final FeatureBadge? badge;

  /// Whether the feature may be used.
  bool get isAllowed;
}

/// The feature may be used, optionally with a marker (e.g. trial).
final class FeatureAllowed extends FeatureAccess {
  /// Creates the answer.
  const FeatureAllowed([super.badge]);

  @override
  bool get isAllowed => true;

  @override
  bool operator ==(Object other) =>
      other is FeatureAllowed && other.badge == badge;

  @override
  int get hashCode => Object.hash(FeatureAllowed, badge);

  @override
  String toString() => 'FeatureAllowed(${badge?.name})';
}

/// The feature may not be used now. The host handles the user side (for
/// example its paywall, before answering); the Kit does not enter it and
/// reports `FEATURE_DENIED`.
final class FeatureDenied extends FeatureAccess {
  /// Creates the answer (marker: lock unless given).
  const FeatureDenied([FeatureBadge? badge = FeatureBadge.lock])
    : super(badge);

  @override
  bool get isAllowed => false;

  @override
  bool operator ==(Object other) =>
      other is FeatureDenied && other.badge == badge;

  @override
  int get hashCode => Object.hash(FeatureDenied, badge);

  @override
  String toString() => 'FeatureDenied(${badge?.name})';
}
