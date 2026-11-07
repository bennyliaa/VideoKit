import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

import '../gallery/gallery_text.dart';

/// Host side of the example: demo host actions (收藏 / 标签 / 删除 / 分享),
/// their ARB labels and the host callbacks answering them. Nothing here
/// touches real files; "删除" only answers the request.
abstract final class DemoHostActions {
  /// Action IDs. `delete` is the one [Scenario.hostActionTimeout] stalls.
  static const String favorite = 'favorite';

  /// Tag action.
  static const String tag = 'tag';

  /// Delete action (demo only).
  static const String delete = 'delete';

  /// Share action (always in the overflow menu).
  static const String share = 'share';

  /// Message key shown after a completed action.
  static const String doneMessage = 'demo.done';

  /// Screen reader description key: `demo.<id>.cd`, or `demo.<id>.image.cd`
  /// on image pages (R1-15: "这张图片", not "这个视频").
  static String _cd(String id, bool image) =>
      image ? 'demo.$id.image.cd' : 'demo.$id.cd';

  /// The action list of an image page.
  static List<VideoKitHostAction> image({bool favorited = false}) =>
      initial(favorited: favorited, image: true);

  /// The initial action list.
  static List<VideoKitHostAction> initial({
    bool favorited = false,
    bool image = false,
  }) => [
    favoriteAction(favorited, image: image),
    VideoKitHostAction(
      actionId: tag,
      labelKey: 'demo.tag',
      contentDescriptionKey: _cd(tag, image),
      icon: HostIcon.builtIn('tag'),
      placement: ActionPlacement.primaryBar,
      displayPriority: 2,
      badgeText: '3',
    ),
    VideoKitHostAction(
      actionId: delete,
      labelKey: 'demo.delete',
      contentDescriptionKey: _cd(delete, image),
      icon: HostIcon.builtIn('delete'),
      placement: ActionPlacement.secondaryBar,
      displayPriority: 1,
    ),
    VideoKitHostAction(
      actionId: share,
      labelKey: 'demo.share',
      contentDescriptionKey: _cd(share, image),
      icon: HostIcon.builtIn('share'),
      placement: ActionPlacement.overflow,
    ),
  ];

  /// The favourite action in the given state.
  static VideoKitHostAction favoriteAction(
    bool favorited, {
    bool image = false,
  }) => VideoKitHostAction(
    actionId: favorite,
    labelKey: favorited ? 'demo.favorited' : 'demo.favorite',
    contentDescriptionKey: _cd(favorited ? 'unfavorite' : favorite, image),
    icon: HostIcon.builtIn(favorited ? 'favorite' : 'favoriteborder'),
    placement: ActionPlacement.primaryBar,
    selected: favorited,
    displayPriority: 3,
  );

  /// Resolves the host string keys above from the example ARB.
  static String resolve(BuildContext context, String key) {
    final g = GalleryText.of(context);
    final l = g.l;
    return g(switch (key) {
      'demo.favorite' => l.hostFavorite,
      'demo.favorited' => l.hostFavorited,
      'demo.favorite.cd' => l.hostFavoriteCd,
      'demo.unfavorite.cd' => l.hostUnfavoriteCd,
      'demo.tag' => l.hostTag,
      'demo.tag.cd' => l.hostTagCd,
      'demo.delete' => l.hostDelete,
      'demo.delete.cd' => l.hostDeleteCd,
      'demo.share' => l.hostShare,
      'demo.share.cd' => l.hostShareCd,
      'demo.favorite.image.cd' => l.hostFavoriteImageCd,
      'demo.unfavorite.image.cd' => l.hostUnfavoriteImageCd,
      'demo.tag.image.cd' => l.hostTagImageCd,
      'demo.delete.image.cd' => l.hostDeleteImageCd,
      'demo.share.image.cd' => l.hostShareImageCd,
      doneMessage => l.hostDone,
      _ => key,
    });
  }
}

/// Host callbacks of the example: favourite toggles at once, the others
/// answer after a short (Fake clock) delay so the pending state is visible.
class DemoHostCallbacks extends NoopHostCallbacks {
  /// Creates the callbacks.
  DemoHostCallbacks();

  /// Clock of the owning Fake, set once the Fake exists.
  FakeClock? clock;

  bool _favorited = false;

  /// The host shows images (descriptions say "这张图片").
  bool image = false;

  /// Answer delay for the slow actions.
  static const Duration answerDelay = Duration(milliseconds: 800);

  @override
  Future<HostActionResult> onHostActionRequested(
    HostActionRequest request,
  ) async {
    switch (request.actionId) {
      case DemoHostActions.favorite:
        _favorited = !_favorited;
        return HostActionResult.completed(
          DemoHostActions.favoriteAction(_favorited, image: image),
        );
      case DemoHostActions.tag ||
          DemoHostActions.delete ||
          DemoHostActions.share:
        final c = clock;
        if (c != null) await c.delay(answerDelay);
        return const HostActionResult.completed(
          null,
          DemoHostActions.doneMessage,
        );
      default:
        return const HostActionResult.failed();
    }
  }
}
