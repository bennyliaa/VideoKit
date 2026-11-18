import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart' show VideoKitFeature;

/// Paid features of the VideoKit App (REQ-APP-15, final split 2026-11-08):
/// multi-view, editing and concatenation, masks and tracking, avatar
/// replacement, export. Free and never asked for: playback and image
/// viewing, the private media library, "最近播放", settings.
enum AppFeature {
  /// Multi-view (Kit `MULTI_VIEW`).
  multiView,

  /// Editing and concatenation (Kit `EDIT`).
  edit,

  /// Masks and tracking (Kit `MASK_TRACKING`).
  maskTracking,

  /// Avatar replacement (Kit `AVATAR`).
  avatar,

  /// Export (Kit `EXPORT`).
  export;

  /// The App feature behind a Kit feature, or null (unknown).
  static AppFeature? ofKit(VideoKitFeature f) => switch (f) {
    VideoKitFeature.multiView => multiView,
    VideoKitFeature.edit => edit,
    VideoKitFeature.maskTracking => maskTracking,
    VideoKitFeature.avatar => avatar,
    VideoKitFeature.export => export,
    VideoKitFeature.unknown => null,
  };
}

/// Subscription state.
enum EntitlementStatus {
  /// Subscribed (the default of [AlwaysSubscribedEntitlements]).
  subscribed,

  /// Free trial running: everything usable, no locks (VK-A3; VK-A2 only
  /// through the debug switch).
  trial,

  /// Not subscribed: paid entries show a lock and ask to subscribe.
  expired,
}

/// What the user may use now.
@immutable
final class Entitlement {
  /// Creates a value.
  const Entitlement({
    required this.status,
    this.trialEndsAtEpochMs,
    this.features = const {},
  });

  /// Everything (subscribed).
  static const Entitlement full = Entitlement(
    status: EntitlementStatus.subscribed,
  );

  /// State.
  final EntitlementStatus status;

  /// End of the trial ([EntitlementStatus.trial]).
  final int? trialEndsAtEpochMs;

  /// Paid features still allowed while [EntitlementStatus.expired] (none
  /// by default); ignored otherwise.
  final Set<AppFeature> features;

  /// Whether [feature] may be used.
  bool allows(AppFeature feature) => switch (status) {
    EntitlementStatus.subscribed || EntitlementStatus.trial => true,
    EntitlementStatus.expired => features.contains(feature),
  };

  /// Whole days of trial left at [now] (rounded up; 0 when over or not a
  /// trial).
  int trialDaysLeft(DateTime now) {
    final end = trialEndsAtEpochMs;
    if (status != EntitlementStatus.trial || end == null) return 0;
    final ms = end - now.millisecondsSinceEpoch;
    if (ms <= 0) return 0;
    return (ms / Duration.millisecondsPerDay).ceil();
  }

  @override
  bool operator ==(Object other) =>
      other is Entitlement &&
      other.status == status &&
      other.trialEndsAtEpochMs == trialEndsAtEpochMs &&
      setEquals(other.features, features);

  @override
  int get hashCode =>
      Object.hash(status, trialEndsAtEpochMs, Object.hashAll(features));
}

/// The App's entitlement service (REQ-APP-15, VK-A2). The App asks it
/// before its own paid entry points and answers the Kit's feature gate
/// (REQ-API-10) from it. VK-A3 replaces the implementation (trial, store
/// billing per channel); callers stay as they are.
abstract interface class EntitlementService
    implements ValueListenable<Entitlement> {
  /// Whether [feature] may be used now.
  bool allows(AppFeature feature);

  /// Re-reads the state (store, cache); VK-A2: nothing to do.
  Future<void> refresh();
}

/// VK-A2 implementation: always subscribed. Reads nothing and talks to no
/// store.
///
/// Debug builds only, for FT01B-07 and screenshots: [debugSimulate] puts it
/// in "not subscribed" or "trial" (settings shows the switches only when
/// `kDebugMode`; in a release build it does nothing).
final class AlwaysSubscribedEntitlements extends ValueNotifier<Entitlement>
    implements EntitlementService {
  /// Creates the service.
  AlwaysSubscribedEntitlements({DateTime Function()? now})
    : now = now ?? DateTime.now,
      super(Entitlement.full);

  /// Clock (trial end).
  final DateTime Function() now;

  /// Days of the simulated trial.
  static const int simulatedTrialDays = 5;

  /// "模拟未订阅" is on.
  bool get simulatingUnsubscribed =>
      value.status == EntitlementStatus.expired;

  /// "模拟试用中" is on.
  bool get simulatingTrial => value.status == EntitlementStatus.trial;

  /// Debug: simulate [status] (subscribed = back to normal). A trial ends
  /// [simulatedTrialDays] from now.
  void debugSimulate(EntitlementStatus status) {
    if (!kDebugMode) return;
    value = switch (status) {
      EntitlementStatus.subscribed => Entitlement.full,
      EntitlementStatus.expired => const Entitlement(
        status: EntitlementStatus.expired,
      ),
      EntitlementStatus.trial => Entitlement(
        status: EntitlementStatus.trial,
        trialEndsAtEpochMs: now()
            .add(const Duration(days: simulatedTrialDays))
            .millisecondsSinceEpoch,
      ),
    };
  }

  @override
  bool allows(AppFeature feature) => value.allows(feature);

  @override
  Future<void> refresh() async {}
}

/// A fixed entitlement (tests, demos of the expired state).
final class FixedEntitlements extends ValueNotifier<Entitlement>
    implements EntitlementService {
  /// Creates the service with [value].
  FixedEntitlements(super.value);

  @override
  bool allows(AppFeature feature) => value.allows(feature);

  @override
  Future<void> refresh() async {}
}
