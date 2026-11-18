import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import '../avatar/avatar_store.dart';
import '../entitlement/entitlement_gate.dart';
import '../entitlement/entitlement_service.dart';
import '../history/history_entry.dart';

/// Host side of one open session (a player or image page).
abstract interface class AppSessionHost {
  /// A host action of the page's session ("收藏", "标签").
  Future<HostActionResult> onHostAction(HostActionRequest request);

  /// "上一张 / 下一张" of the page's session.
  Future<NavigationResult> onNavigation(NavigationRequest request);
}

/// The App's [VideoKitHostCallbacks] (M2): routes host action and
/// navigation requests to the page that owns the session. Pages register
/// themselves for their session ID while open. The Kit applies the
/// timeouts (14 §12: actions 10 s, navigation 3 s); requests for sessions
/// without a page are answered at once.
final class AppHostCallbacks extends NoopHostCallbacks {
  /// Creates the router.
  AppHostCallbacks();

  final Map<String, AppSessionHost> _hosts = {};

  /// Routes requests of [sessionId] to [host].
  void register(String sessionId, AppSessionHost host) =>
      _hosts[sessionId] = host;

  /// Stops routing [sessionId] (only if still routed to [host]).
  void unregister(String sessionId, AppSessionHost host) {
    if (identical(_hosts[sessionId], host)) _hosts.remove(sessionId);
  }

  /// Whether [sessionId] has a page (tests).
  bool routes(String sessionId) => _hosts.containsKey(sessionId);

  @override
  Future<HostActionResult> onHostActionRequested(HostActionRequest request) =>
      _hosts[request.sessionId]?.onHostAction(request) ??
      Future.value(const HostActionResult.failed());

  @override
  Future<NavigationResult> onNavigationRequested(NavigationRequest request) =>
      _hosts[request.sessionId]?.onNavigation(request) ??
      Future.value(NavigationResult.unavailable);

  /// The App's avatars (set when the App starts).
  AvatarStore? avatars;

  /// Entitlements (set when the App starts; REQ-APP-15).
  EntitlementService? entitlements;

  /// Context for the App's paywall placeholder (the navigator's).
  BuildContext? Function()? dialogContext;

  /// REQ-API-10 / REQ-APP-15: the App answers the Kit's feature gate from
  /// its entitlements (multi-view, edit, masks and tracking, avatar,
  /// export are paid). A paid feature the user may not use shows the
  /// App's paywall placeholder, then is denied with a lock; a trial is
  /// allowed without a marker.
  @override
  Future<FeatureAccess> checkFeature(
    VideoKitFeature feature,
    String? sessionId,
  ) async {
    final app = AppFeature.ofKit(feature);
    final service = entitlements;
    if (app == null || service == null || service.allows(app)) {
      return FeatureAccess.allowed;
    }
    final ctx = dialogContext?.call();
    if (ctx != null && ctx.mounted) await showEntitlementDenied(ctx, app);
    return const FeatureDenied();
  }

  /// REQ-ED-07 (04A E6 2): the Kit reads an App avatar for preview /
  /// export; null when it is gone (the Kit then falls back to mosaic).
  @override
  Future<VideoKitSourceFactory?> openAvatar(String avatarToken) async {
    final png = await avatars?.bytes(avatarToken);
    return png == null ? null : BytesSourceFactory(png);
  }
}

/// The App's own host actions (M2, App business, not in the module):
/// "收藏" and "标签" on the player and the image viewer. Labels are App
/// string keys resolved by `AppHostStrings`.
abstract final class AppHostActions {
  /// Favourite action ID.
  static const String favorite = 'favorite';

  /// Tag action ID.
  static const String tag = 'tag';

  /// Actions for [entry] in its current state.
  static List<VideoKitHostAction> forEntry(HistoryEntry entry) => [
    favoriteAction(entry),
    tagAction(entry),
  ];

  static String _kind(HistoryEntry e) => e.isImage ? 'image' : 'video';

  /// "收藏" / "已收藏".
  static VideoKitHostAction favoriteAction(HistoryEntry e) =>
      VideoKitHostAction(
        actionId: favorite,
        labelKey: e.favorite ? 'app.favorited' : 'app.favorite',
        contentDescriptionKey:
            'app.${e.favorite ? 'unfavorite' : 'favorite'}.${_kind(e)}.cd',
        icon: HostIcon.builtIn(e.favorite ? 'favorite' : 'favoriteborder'),
        placement: ActionPlacement.primaryBar,
        selected: e.favorite,
        displayPriority: 3,
      );

  /// "标签" with the tag count as badge.
  static VideoKitHostAction tagAction(HistoryEntry e) => VideoKitHostAction(
    actionId: tag,
    labelKey: 'app.tag',
    contentDescriptionKey: 'app.tag.${_kind(e)}.cd',
    icon: HostIcon.builtIn('tag'),
    placement: ActionPlacement.primaryBar,
    displayPriority: 2,
    badgeText: e.tags.isEmpty ? null : '${e.tags.length}',
  );
}
