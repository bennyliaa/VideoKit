import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';

/// Feature switches and gate for the Kit widgets below (REQ-API-10, VK-A2).
///
/// * A hidden feature has no entry ([isEnabled]).
/// * Before an entry opens, [enter] asks the host's gate; a denied entry
///   does not open (the host handles the user side, e.g. its paywall).
/// * The host's marker of the last answer (lock, trial) is kept per feature
///   ([badgeOf]) and drawn on the entry; hosts can also set it up front
///   ([setBadge], e.g. from their entitlements) so the lock shows before
///   the first tap.
///
/// Without a scope everything is enabled and allowed, exactly as before
/// (FT01B-03).
class VideoKitFeatures extends ChangeNotifier {
  /// Creates the state for [gate].
  VideoKitFeatures(this.gate, {Map<VideoKitFeature, FeatureBadge?> badges = const {}})
    : _badges = Map.of(badges);

  /// Switches and the host's gate.
  VideoKitFeatureGate gate;

  final Map<VideoKitFeature, FeatureBadge?> _badges;

  /// Shared default: everything enabled and allowed, no markers.
  static final VideoKitFeatures open = VideoKitFeatures(
    VideoKitFeatureGate.open,
  );

  /// Whether [feature] has an entry.
  bool isEnabled(VideoKitFeature feature) => gate.isEnabled(feature);

  /// Marker on the entry of [feature], or null.
  FeatureBadge? badgeOf(VideoKitFeature feature) =>
      _badges[feature] == FeatureBadge.unknown ? null : _badges[feature];

  /// Sets the marker of [feature] (null removes it).
  void setBadge(VideoKitFeature feature, FeatureBadge? badge) {
    if (_badges[feature] == badge) return;
    _badges[feature] = badge;
    notifyListeners();
  }

  /// Asks the gate before entering [feature]; remembers the marker of the
  /// answer. True when the entry may open.
  Future<bool> enter(VideoKitFeature feature, {String? sessionId}) async {
    if (!isEnabled(feature)) return false;
    final access = await gate.check(feature, sessionId: sessionId);
    setBadge(feature, access.badge);
    return access.isAllowed;
  }

  /// The nearest features state, or [open].
  static VideoKitFeatures of(BuildContext context) =>
      context
          .dependOnInheritedWidgetOfExactType<_FeatureInherited>()
          ?.notifier ??
      open;
}

/// Puts [features] above the Kit widgets in [child].
class VideoKitFeatureScope extends StatelessWidget {
  /// Creates the scope.
  const VideoKitFeatureScope({
    super.key,
    required this.features,
    required this.child,
  });

  /// State.
  final VideoKitFeatures features;

  /// Subtree.
  final Widget child;

  @override
  Widget build(BuildContext context) =>
      _FeatureInherited(notifier: features, child: child);
}

class _FeatureInherited extends InheritedNotifier<VideoKitFeatures> {
  const _FeatureInherited({required super.notifier, required super.child});
}

/// The host's marker on an entry: a small lock, or "试用中" (REQ-API-10 ②).
class VkFeatureBadge extends StatelessWidget {
  /// Creates the marker for [badge] (nothing for null / unknown).
  const VkFeatureBadge({super.key, required this.badge});

  /// Marker.
  final FeatureBadge? badge;

  /// Screen-reader text of [badge], or null.
  static String? label(VkStrings s, FeatureBadge? badge) => switch (badge) {
    FeatureBadge.lock => s.text('featureBadgeLock'),
    FeatureBadge.trial => s.text('featureBadgeTrial'),
    _ => null,
  };

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final b = badge;
    if (b == null || b == FeatureBadge.unknown) return const SizedBox.shrink();
    final lock = b == FeatureBadge.lock;
    return Semantics(
      label: label(s, b),
      child: ExcludeSemantics(
        child: Container(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing4,
            vertical: d.spacing4 / 2,
          ),
          decoration: BoxDecoration(
            color: lock ? t.colors.surfaceHigh : t.colors.primaryContainer,
            borderRadius: BorderRadius.circular(d.cornerFull),
          ),
          child: lock
              ? Icon(
                  t.icons.resolve('lock'),
                  size: d.icon16,
                  color: t.colors.textSecondary,
                )
              : Text(
                  s.text('featureBadgeTrial'),
                  style: t.typography.caption.copyWith(
                    color: t.colors.primary,
                  ),
                ),
        ),
      ),
    );
  }
}

/// [child] with the marker of [feature] at its top end corner.
class VkFeatureBadged extends StatelessWidget {
  /// Creates the wrapper.
  const VkFeatureBadged({super.key, required this.feature, required this.child});

  /// Feature whose marker is drawn.
  final VideoKitFeature feature;

  /// The entry.
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final badge = VideoKitFeatures.of(context).badgeOf(feature);
    if (badge == null) return child;
    return Stack(
      clipBehavior: Clip.none,
      children: [
        child,
        PositionedDirectional(
          top: 0,
          end: 0,
          child: IgnorePointer(child: VkFeatureBadge(badge: badge)),
        ),
      ],
    );
  }
}
