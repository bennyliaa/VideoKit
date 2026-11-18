// APP-LIB-A1 (16 FT-01A, design pages 26–27): the media library pages in
// the App — first entry, PIN, FLAG_SECURE, folder bar / drawer, filters,
// paging, folder rules, import, opening without "最近播放".
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/app_scope.dart';
import 'package:videokit_app/library/library_gate.dart';
import 'package:videokit_app/library/library_lock.dart';
import 'package:videokit_app/library/library_models.dart';
import 'package:videokit_app/library/library_page.dart';
import 'package:videokit_app/library/library_platform.dart';
import 'package:videokit_app/library/library_store.dart';
import 'package:videokit_app/pages/player_page.dart';

import 'app_test.dart' show pickDemo;
import 'support.dart';

/// A rig with a library of [videos] + [images] items, [folders] (the
/// first [inFirst] items go to the first folder) and no PIN (set up done).
AppRig libraryRig({
  int videos = 0,
  int images = 0,
  List<String> folders = const [],
  int inFirst = 0,
  Map<String, Object?> settings = const {'setUpDone': true},
}) {
  final rig = AppRig.create();
  final items = [
    for (var i = 0; i < videos + images; i++)
      LibraryItem(
        id: 'item-$i',
        path: 'memory:library/item-$i',
        displayName: '${i < videos ? 'video' : 'photo'}-$i.${i < videos ? 'mp4' : 'jpg'}',
        kind: i < videos ? MediaKind.video : MediaKind.imageStatic,
        importedAtEpochMs: 1000 - i,
        durationUs: i < videos ? 134000000 : null,
        folderId: folders.isNotEmpty && i < inFirst ? 'folder-0' : null,
      ),
  ];
  rig.storage.documents[LibraryStore.fileName] = jsonEncode({
    'schema': 1,
    'counter': 100,
    'folders': [
      for (final (i, f) in folders.indexed)
        LibraryFolder(id: 'folder-$i', name: f, createdAtEpochMs: i).toJson(),
    ],
    'items': [for (final i in items) i.toJson()],
  });
  rig.storage.documents[LibraryLock.fileName] = jsonEncode(settings);
  for (final i in items) {
    rig.backend.library.files[i.path] = 1;
  }
  return rig;
}

Future<void> openLibrary(WidgetTester tester) async {
  await tester.tap(find.bySemanticsLabel('媒体库'));
  await settle(tester, 4);
}

Future<void> typePin(WidgetTester tester, String pin) async {
  for (final c in pin.split('')) {
    await tester.tap(find.bySemanticsLabel('数字 $c'));
    await tester.pump();
  }
  await settle(tester, 2);
}

void main() {
  testWidgets('FT01A-01/02: first entry offers a PIN; FLAG_SECURE only '
      'while the library is open', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    expect(rig.backend.library.secure, isFalse);
    await openLibrary(tester);
    expect(find.text('保护你的私密媒体'), findsOneWidget);
    expect(rig.backend.library.secure, isTrue);
    await tester.tap(find.text('暂不设置'));
    await settle(tester, 2);
    expect(find.byType(LibraryPage), findsOneWidget);
    expect(find.text('这里还没有媒体'), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 2);
    expect(rig.backend.library.secure, isFalse);
    await unmount(tester);
  });

  testWidgets('FT01A-01: set a PIN, lock, wrong PIN, unlock', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('设置密码'));
    await settle(tester, 2);
    expect(find.text('设置 6 位数字密码'), findsOneWidget);
    await typePin(tester, '123456');
    expect(find.text('再次输入密码'), findsOneWidget);
    await typePin(tester, '123456');
    expect(find.byType(LibraryPage), findsOneWidget);
    expect(find.bySemanticsLabel('立即上锁'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('立即上锁'));
    await settle(tester, 2);
    expect(find.text('私密媒体库'), findsOneWidget);
    expect(find.byType(LibraryPage), findsNothing, reason: 'nothing shown');
    await typePin(tester, '000000');
    expect(find.text('密码错误，还可尝试 4 次'), findsOneWidget);
    await typePin(tester, '123456');
    expect(find.byType(LibraryPage), findsOneWidget);
    final saved = rig.storage.documents[LibraryLock.fileName]!;
    expect(saved, isNot(contains('123456')));
    await unmount(tester);
  });

  testWidgets('FT01A-02: auto-lock while inside closes the player and asks '
      'for the PIN', (tester) async {
    final rig = libraryRig(videos: 1);
    await rig.pump(tester);
    await openLibrary(tester);
    final lock = AppScope.of(
      tester.element(find.byType(LibraryGate)),
    ).libraryLock;
    await tester.tap(find.text('video-0.mp4'));
    await settle(tester, 6);
    expect(find.byType(PlayerPage), findsOneWidget);
    // A PIN, then the lock the lifecycle would apply after the delay.
    await lock.setPin('123456');
    lock.lock();
    await settle(tester, 4);
    expect(find.byType(PlayerPage), findsNothing);
    expect(find.text('私密媒体库'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-13: opening from the library never records "最近播放"', (
    tester,
  ) async {
    final rig = libraryRig(videos: 2);
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('video-0.mp4'));
    await settle(tester, 6);
    expect(find.byType(PlayerPage), findsOneWidget);
    await tester.binding.handlePopRoute();
    await settle(tester, 6);
    expect(rig.savedEntries(), isEmpty);
    await unmount(tester);
  });

  testWidgets('FT01A-08/12 tablet: folder bar beside the list, range with '
      'page size, pages, filters, collapse', (tester) async {
    final rig = libraryRig(
      videos: 15,
      images: 6,
      folders: ['旅行', '家人'],
      inFirst: 3,
    );
    await rig.pump(tester, size: expandedSize);
    await openLibrary(tester);
    expect(find.text('文件夹'), findsOneWidget);
    expect(find.text('全部媒体'), findsWidgets);
    expect(find.text('旅行'), findsOneWidget);
    expect(find.text('未分类'), findsOneWidget);
    expect(find.text('长按文件夹：改名 · 删除'), findsOneWidget);
    expect(find.text('第 1–20 项，共 21 项 · 每页 20 项'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('下一页'));
    await settle(tester, 2);
    expect(find.text('第 21–21 项，共 21 项 · 每页 20 项'), findsOneWidget);
    await tester.tap(find.text('图片').first);
    await settle(tester, 2);
    expect(find.text('第 1–6 项，共 6 项 · 每页 20 项'), findsOneWidget);
    await tester.tap(find.text('旅行'));
    await settle(tester, 2);
    expect(find.text('3 项'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('收起文件夹栏'));
    await settle(tester, 2);
    expect(find.text('长按文件夹：改名 · 删除'), findsNothing);
    await tester.tap(find.bySemanticsLabel('显示文件夹栏'));
    await settle(tester, 2);
    expect(find.text('长按文件夹：改名 · 删除'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-12 phone: folder bar is a drawer from the start edge', (
    tester,
  ) async {
    final rig = libraryRig(videos: 3, folders: ['旅行']);
    await rig.pump(tester);
    await openLibrary(tester);
    expect(find.text('长按文件夹：改名 · 删除'), findsNothing);
    expect(find.text('第 1–3 项，共 3 项'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('显示文件夹栏').first);
    await settle(tester, 3);
    expect(find.text('文件夹'), findsOneWidget);
    await tester.tap(find.text('旅行'));
    await settle(tester, 3);
    expect(find.text('文件夹'), findsNothing, reason: 'drawer closed');
    expect(find.text('这里还没有媒体'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-10: new folder; duplicate and empty names refused', (
    tester,
  ) async {
    final rig = libraryRig(folders: ['旅行']);
    await rig.pump(tester, size: expandedSize);
    await openLibrary(tester);
    await tester.tap(find.bySemanticsLabel('新建文件夹'));
    await settle(tester, 2);
    await tester.enterText(find.byType(TextField), '旅行');
    await tester.pump();
    expect(find.text('已有同名文件夹'), findsOneWidget);
    await tester.tap(find.text('创建'));
    await tester.pump();
    expect(find.byType(TextField), findsOneWidget, reason: 'still open');
    await tester.enterText(find.byType(TextField), '   ');
    await tester.pump();
    expect(find.text('名称不能为空'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '宠物');
    await tester.tap(find.text('创建'));
    await settle(tester, 2);
    expect(find.text('宠物'), findsWidgets);
    final saved = rig.storage.documents[LibraryStore.fileName]!;
    expect(saved, contains('宠物'));
    await unmount(tester);
  });

  testWidgets('FT01A-19: select one, select all across pages, delete with '
      'confirmation', (tester) async {
    final rig = libraryRig(videos: 21);
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('选择'));
    await settle(tester, 2);
    expect(find.text('已选 0 项'), findsOneWidget);
    await tester.tap(find.text('video-0.mp4'));
    await settle(tester, 1);
    expect(find.text('已选 1 项'), findsOneWidget);
    await tester.tap(find.text('全选'));
    await settle(tester, 1);
    expect(find.text('已选文件夹全部 21 项'), findsOneWidget);
    // Leaving "全选" by one item keeps the other 20 (also on page 2).
    await tester.tap(find.text('video-1.mp4'));
    await settle(tester, 1);
    expect(find.text('已选 20 项'), findsOneWidget);
    await tester.tap(find.text('删除'));
    await settle(tester, 2);
    expect(find.text('删除已选的 20 项？'), findsOneWidget);
    await tester.tap(find.text('删除').last);
    await settle(tester, 3);
    expect(find.text('第 1–1 项，共 1 项'), findsOneWidget);
    expect(find.text('video-1.mp4'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-17/19: export the selection to the gallery after the '
      'warning; the library keeps it', (tester) async {
    final rig = libraryRig(videos: 2, images: 1);
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('选择'));
    await settle(tester, 2);
    await tester.tap(find.text('全选'));
    await settle(tester, 1);
    await tester.tap(find.text('导出到相册'));
    await settle(tester, 2);
    expect(find.text('导出后不再私密'), findsOneWidget);
    await tester.tap(find.text('导出'));
    await settle(tester, 3);
    expect(find.text('导出完成：3 项成功，0 项失败'), findsOneWidget);
    await tester.tap(find.text('完成'));
    await settle(tester, 2);
    expect(rig.backend.library.gallery, hasLength(3));
    expect(find.text('第 1–3 项，共 3 项'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-20: move out asks first, then removes verified items', (
    tester,
  ) async {
    final rig = libraryRig(videos: 2, folders: ['旅行'], inFirst: 1);
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('选择'));
    await settle(tester, 2);
    await tester.tap(find.text('全选'));
    await settle(tester, 1);
    await tester.tap(find.text('移动到文件夹'));
    await settle(tester, 2);
    expect(find.text('移出后不再私密'), findsOneWidget);
    await tester.tap(find.text('选择目标文件夹'));
    await settle(tester, 3);
    expect(find.text('完成：2 项已移出，0 项仍在媒体库'), findsOneWidget);
    expect(rig.backend.library.directories['tree:demo'], {'旅行', '未分类'});
    await tester.tap(find.text('完成'));
    await settle(tester, 2);
    expect(find.text('这里还没有媒体'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-19: folders can be selected, all, and deleted', (
    tester,
  ) async {
    final rig = libraryRig(
      videos: 3,
      folders: ['旅行', '家人'],
      inFirst: 2,
    );
    await rig.pump(tester, size: expandedSize);
    await openLibrary(tester);
    // The folder bar's "选择" (the top bar has one for media too).
    await tester.tap(find.text('选择').last);
    await settle(tester, 2);
    expect(find.text('已选 0 个文件夹，共 0 项'), findsOneWidget);
    await tester.tap(find.text('全选'));
    await settle(tester, 1);
    expect(find.text('已选 2 个文件夹，共 2 项'), findsOneWidget);
    await tester.tap(find.text('删除').first);
    await settle(tester, 2);
    expect(find.text('删除已选的 2 个文件夹？'), findsOneWidget);
    await tester.tap(find.text('媒体移到“未分类”'));
    await settle(tester, 3);
    expect(find.text('旅行'), findsNothing);
    expect(find.text('第 1–3 项，共 3 项 · 每页 20 项'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('REQ-APP-14: data warning on first use and in settings; '
      'settings rows lead to choosing media', (tester) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    await openLibrary(tester);
    expect(
      find.text('卸载 App 或清除数据会删除媒体库中的所有文件。'),
      findsOneWidget,
    );
    await tester.tap(find.text('暂不设置'));
    await settle(tester, 2);
    await tester.tap(find.bySemanticsLabel('媒体库设置'));
    await settle(tester, 3);
    await tester.scrollUntilVisible(find.text('移出媒体库'), 200);
    expect(find.text('数据'), findsOneWidget);
    expect(
      find.text('卸载 App 或清除数据会删除媒体库中的所有文件。'),
      findsOneWidget,
    );
    await tester.tap(find.text('选择媒体'));
    await settle(tester, 3);
    expect(find.text('已选 0 项'), findsOneWidget, reason: 'selection mode');
    await unmount(tester);
  });

  testWidgets('FT01A-21: import a whole folder through the import menu', (
    tester,
  ) async {
    final rig = libraryRig();
    rig.backend.library.listing = const TreeListing(
      name: '相机',
      entries: [
        TreeEntry(dir: '', uri: 'u:1', name: 'a.mp4', mimeType: 'video/mp4'),
        TreeEntry(dir: '', uri: 'u:2', name: 'b.txt', mimeType: 'text/plain'),
      ],
    );
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('导入'));
    await settle(tester, 2);
    await tester.tap(find.text('导入整个文件夹'));
    await settle(tester, 4);
    expect(find.text('导入到“相机”'), findsOneWidget);
    expect(find.text('已跳过 1 个不是视频或图片的文件'), findsOneWidget);
    expect(find.text('导入后删除手机里的原文件'), findsNothing);
    await tester.tap(find.text('完成'));
    await settle(tester, 2);
    expect(find.text('第 1–1 项，共 1 项'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('FT01A-04: import through the picker into the folder', (
    tester,
  ) async {
    final rig = libraryRig();
    await rig.pump(tester);
    await openLibrary(tester);
    await tester.tap(find.text('导入'));
    await settle(tester, 2);
    await tester.tap(find.text('选择视频和图片'));
    await settle(tester, 2);
    await pickDemo(tester, ['山谷黄昏.mkv', '沙丘.heic']);
    await settle(tester, 4);
    expect(find.text('导入到“未分类”'), findsOneWidget);
    expect(find.text('文件复制到 App 内，相册和其他 App 看不到'), findsOneWidget);
    expect(find.text('导入完成：2 项成功，0 项失败'), findsOneWidget);
    await tester.tap(find.text('完成'));
    await settle(tester, 2);
    expect(find.text('第 1–2 项，共 2 项'), findsOneWidget);
    expect(rig.savedEntries(), isEmpty, reason: 'imports are not history');
    await unmount(tester);
  });
}
