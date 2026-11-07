// M2-A1 item 3: image records open in UI-03, page through the image
// records, and "收藏" / "标签" are App host actions stored in the history.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/history/history_entry.dart';
import 'package:videokit_app/host/app_host.dart';
import 'package:videokit_app/host/entry_host.dart';
import 'package:videokit_app/pages/image_page.dart';
import 'package:videokit_app/pages/player_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

List<HistoryEntry> withAnimated({VideoKitPlaybackState? snapshot}) => [
  ...sampleHistory(),
  HistoryEntry(
    id: 'h6',
    uri: 'demo:fireworks',
    displayName: '烟花.gif',
    kind: MediaKind.imageAnimated,
    playbackState: snapshot,
    lastOpenedAtEpochMs: testNow
        .subtract(const Duration(days: 6))
        .millisecondsSinceEpoch,
  ),
];

/// Tall enough that every sample record is on screen.
const Size tall = Size(400, 1800);

Future<void> openTile(WidgetTester tester, String name) async {
  await tapText(tester, name);
  await settle(tester, 8);
}

void main() {
  test('history keeps favourite and tags (JSON), old records read as none', () {
    final e = sampleHistory().first.copyWith(favorite: true, tags: ['海', '夏天']);
    final back = HistoryEntry.fromJson(e.toJson());
    expect(back, e);
    expect(back.favorite, isTrue);
    expect(back.tags, ['海', '夏天']);
    final old = HistoryEntry.fromJson(sampleHistory().first.toJson());
    expect(old.favorite, isFalse);
    expect(old.tags, isEmpty);
    expect(sampleHistory().first.toJson().containsKey('favorite'), isFalse);
  });

  test('host router: unknown sessions answer at once', () async {
    final hosts = AppHostCallbacks();
    expect(
      (await hosts.onHostActionRequested(
        const HostActionRequest(
          actionId: 'favorite',
          sessionId: 'x',
          mediaToken: 't',
        ),
      )).status,
      HostActionStatus.failed,
    );
    expect(
      await hosts.onNavigationRequested(
        const NavigationRequest(
          sessionId: 'x',
          direction: NavigationDirection.next,
        ),
      ),
      NavigationResult.unavailable,
    );
  });

  testWidgets('image record opens UI-03: no video controls; pages to the '
      'next image record', (tester) async {
    final rig = AppRig.create(entries: withAnimated());
    await rig.pump(tester, size: tall);
    await openTile(tester, '沙丘.heic');
    final page = tester.state<ImagePageState>(find.byType(ImagePage));
    expect(find.byType(VideoKitImageViewer), findsOneWidget);
    expect(find.byType(VideoKitPlayer), findsNothing);
    expect(find.byType(VkSeekBar), findsNothing);
    expect(page.pages.map((e) => e.id), ['h3', 'h6']);
    final first = page.session;
    expect(rig.backend.hosts.routes(first!.sessionId), isTrue);
    page.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester, 8);
    expect(page.current.id, 'h6');
    expect(identical(page.session, first), isFalse, reason: 'new session');
    expect(rig.backend.hosts.routes(first.sessionId), isFalse);
    expect(page.session!.state.value.mediaKind, MediaKind.imageAnimated);
    expect(find.text('烟花.gif'), findsWidgets);
    // Past the last image the host answers "没有更多内容了".
    page.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('下一张'));
    await settle(tester, 4);
    expect(page.current.id, 'h6');
    expect(find.text('没有更多内容了'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });

  testWidgets('收藏 on an image: stored in the history, shown selected', (
    tester,
  ) async {
    final rig = AppRig.create(entries: withAnimated());
    await rig.pump(tester, size: tall);
    await openTile(tester, '沙丘.heic');
    final page = tester.state<ImagePageState>(find.byType(ImagePage));
    page.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('收藏这张图片'));
    await settle(tester, 4);
    final h3 = rig.savedEntries().firstWhere((e) => e['id'] == 'h3');
    expect(h3['favorite'], isTrue);
    final fav = page.session!.state.value.hostActions.firstWhere(
      (a) => a.action.actionId == AppHostActions.favorite,
    );
    expect(fav.action.selected, isTrue);
    expect(find.text('已收藏'), findsWidgets);
    expect(find.bySemanticsLabel('取消收藏这张图片'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    // Home shows the favourite mark.
    expect(find.byIcon(Icons.favorite_rounded), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('标签 on a video: editor adds tags, badge shows the count', (
    tester,
  ) async {
    final rig = AppRig.create(entries: sampleHistory());
    await rig.pump(tester, size: tall);
    await openTile(tester, '山谷黄昏.mkv');
    final page = tester.state<PlayerPageState>(find.byType(PlayerPage));
    page.session!.setControlsVisible(true);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel('为这个视频添加标签'));
    await settle(tester, 4);
    expect(find.byType(TagEditor), findsOneWidget);
    expect(find.text('还没有标签'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '风景');
    await tester.tap(find.text('添加'));
    await tester.pump();
    await tester.enterText(find.byType(TextField), '黄昏');
    await tester.tap(find.text('完成'));
    await settle(tester, 4);
    expect(find.byType(TagEditor), findsNothing);
    final h1 = rig.savedEntries().firstWhere((e) => e['id'] == 'h1');
    expect(h1['tags'], ['风景', '黄昏']);
    final tag = page.session!.state.value.hostActions.firstWhere(
      (a) => a.action.actionId == AppHostActions.tag,
    );
    expect(tag.action.badgeText, '2');
    expect(tag.isPending, isFalse);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    expect(find.text('2 个标签'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('animated image: looping off is saved and restored (L3)', (
    tester,
  ) async {
    final rig = AppRig.create(entries: withAnimated());
    await rig.pump(tester, size: tall);
    await openTile(tester, '烟花.gif');
    var page = tester.state<ImagePageState>(find.byType(ImagePage));
    expect(page.session!.state.value.looping, isTrue, reason: 'GIF default');
    await page.session!.execute(const SetLooping(false));
    await settle(tester, 2);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    final h6 = rig.savedEntries().firstWhere((e) => e['id'] == 'h6');
    expect((h6['playbackState']! as Map)['looping'], isFalse);
    expect(h6.containsKey('lastPositionUs'), isFalse, reason: 'no resume');
    await openTile(tester, '烟花.gif');
    page = tester.state<ImagePageState>(find.byType(ImagePage));
    expect(page.session!.state.value.looping, isFalse, reason: 'restored');
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });

  testWidgets('history off: no App host actions (nothing to store them in)', (
    tester,
  ) async {
    final rig = AppRig.create(settings: {'recordHistory': false});
    await rig.pump(tester, size: tall);
    await tapText(tester, '打开文件');
    await settle(tester, 2);
    await tapText(tester, '沙丘.heic');
    await tester.pump();
    await tester.tap(find.textContaining('打开 1 个'));
    await settle(tester, 8);
    final page = tester.state<ImagePageState>(find.byType(ImagePage));
    expect(page.session!.state.value.hostActions, isEmpty);
    expect(EntryHost.actionsFor, isNotNull);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    await unmount(tester);
  });
}
