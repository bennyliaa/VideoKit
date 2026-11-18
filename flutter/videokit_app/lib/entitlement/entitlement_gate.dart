import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart' show FeatureBadge;
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'entitlement_service.dart';

/// Name of [f] in messages.
String appFeatureName(AppText a, AppFeature f) => a(switch (f) {
  AppFeature.multiView => a.l.featureMultiView,
  AppFeature.edit => a.l.featureEdit,
  AppFeature.maskTracking => a.l.featureMaskTracking,
  AppFeature.avatar => a.l.featureAvatar,
  AppFeature.export => a.l.featureExport,
});

/// What the user picked in the paywall placeholder.
enum PaywallChoice {
  /// "订阅".
  subscribe,

  /// "恢复购买".
  restore,

  /// "取消".
  cancel,
}

/// The App's paywall placeholder for [feature] (REQ-APP-15; VK-A3 replaces
/// it with the subscription page): "订阅 / 恢复购买 / 取消". In VK-A2 the
/// first two only say that subscriptions come with the release version.
/// Shown by [ensureEntitled] and by the App's answer to the Kit's gate.
Future<PaywallChoice> showEntitlementDenied(
  BuildContext context,
  AppFeature feature,
) async {
  final a = AppText.of(context);
  final choice = await showDialog<PaywallChoice>(
    context: context,
    builder: (context) {
      final t = VkTheme.of(context);
      final d = t.dimensions;
      return AlertDialog(
        backgroundColor: t.colors.surfaceHigh,
        icon: Icon(t.icons.resolve('lock'), color: t.colors.primary),
        title: Text(
          a(a.l.entitlementDeniedTitle(appFeatureName(a, feature))),
          style: t.typography.title.copyWith(color: t.colors.textPrimary),
        ),
        content: Text(
          a(a.l.entitlementDeniedBody),
          style: t.typography.body.copyWith(color: t.colors.textSecondary),
        ),
        actions: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              VkButton(
                label: a(a.l.paywallSubscribe),
                onPressed: () =>
                    Navigator.of(context).pop(PaywallChoice.subscribe),
              ),
              SizedBox(height: d.spacing8),
              VkButton(
                label: a(a.l.paywallRestore),
                variant: VkButtonVariant.secondary,
                onPressed: () =>
                    Navigator.of(context).pop(PaywallChoice.restore),
              ),
              SizedBox(height: d.spacing8),
              VkButton(
                label: a(a.l.paywallCancel),
                variant: VkButtonVariant.text,
                onPressed: () =>
                    Navigator.of(context).pop(PaywallChoice.cancel),
              ),
            ],
          ),
        ],
      );
    },
  );
  final picked = choice ?? PaywallChoice.cancel;
  if (picked != PaywallChoice.cancel && context.mounted) {
    ScaffoldMessenger.maybeOf(context)
      ?..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(a(a.l.paywallComingSoon))));
  }
  return picked;
}

/// Checks [feature] before an App entry point (REQ-APP-15): true when it
/// may be used; otherwise shows the paywall placeholder and returns false.
/// Never blocks free features.
Future<bool> ensureEntitled(BuildContext context, AppFeature feature) async {
  final service = AppScope.of(context).entitlements;
  if (service.allows(feature)) return true;
  await showEntitlementDenied(context, feature);
  return false;
}

/// [child] with a lock at its top end corner while [feature] is not part
/// of the user's plan (REQ-APP-15: the entry stays, with a lock).
class EntitlementLock extends StatelessWidget {
  /// Creates the wrapper.
  const EntitlementLock({
    super.key,
    required this.feature,
    required this.child,
  });

  /// Paid feature.
  final AppFeature feature;

  /// The entry.
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final service = AppScope.of(context).entitlements;
    return ValueListenableBuilder<Entitlement>(
      valueListenable: service,
      builder: (context, e, _) => e.allows(feature)
          ? child
          : Stack(
              clipBehavior: Clip.none,
              children: [
                child,
                const PositionedDirectional(
                  top: 0,
                  end: 0,
                  child: IgnorePointer(
                    child: VkFeatureBadge(badge: FeatureBadge.lock),
                  ),
                ),
              ],
            ),
    );
  }
}
