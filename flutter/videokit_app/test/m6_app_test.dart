// M6-A1 (VK-M8): camera permission only for "拍一张"; the licenses page
// lists components and marks undecided ones "待定".
import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/avatar/avatar_adjust_page.dart';
import 'package:videokit_app/avatar/avatar_pick_page.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/permissions/app_permissions.dart';
import 'package:videokit_app/projects/export_journal.dart';
import 'package:videokit_app/projects/project_store.dart';
import 'package:videokit_app/settings/licenses_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'm4_app_test.dart' show startConcat;
import 'support.dart';

void main() {
  Future<AppRig> pickPage(WidgetTester tester) async {
    final rig = AppRig.create();
    await rig.pump(tester, size: expandedSize);
    await startConcat(tester);
    final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
    e.openMasks(MaskEditorTab.manual);
    await settle(tester, 2);
    unawaited(e.maskEditor!.addManualMask());
    await settle(tester, 2);
    await tester.tap(find.text('头像'));
    await settle(tester, 4);
    expect(find.byType(AvatarPickPage), findsOneWidget);
    return rig;
  }

  testWidgets('nothing asks for a permission until 拍一张', (tester) async {
    final rig = await pickPage(tester);
    expect(rig.backend.permissions.requested, isEmpty);
    await tester.tap(find.text('拍一张'));
    await settle(tester, 8);
    expect(rig.backend.permissions.requested, [AppPermission.camera]);
    expect(find.byType(AvatarAdjustPage), findsOneWidget, reason: 'granted');
    await unmount(tester);
  });

  testWidgets('camera denied: a hint, no camera', (tester) async {
    final rig = await pickPage(tester);
    rig.backend.permissions.answers[AppPermission.camera] =
        PermissionState.denied;
    await tester.tap(find.text('拍一张'));
    await settle(tester, 2);
    expect(find.text('需要相机权限才能拍照，也可以从相册选择'), findsOneWidget);
    expect(find.byType(AvatarAdjustPage), findsNothing);
    await unmount(tester);
  });

  testWidgets('camera permanently denied: 去设置 opens the settings', (
    tester,
  ) async {
    final rig = await pickPage(tester);
    rig.backend.permissions.answers[AppPermission.camera] =
        PermissionState.permanentlyDenied;
    await tester.tap(find.text('拍一张'));
    await settle(tester, 2);
    expect(find.text('相机权限已关闭'), findsOneWidget);
    await tester.tap(find.text('去设置'));
    await settle(tester, 2);
    expect(rig.backend.permissions.settingsOpened, 1);
    expect(find.byType(AvatarAdjustPage), findsNothing);
    await unmount(tester);
  });

  testWidgets('an export interrupted last time shows a notice with '
      '重新导出; 知道了 clears it', (tester) async {
    final rig = AppRig.create();
    rig.storage.documents[ExportJournal.fileName] = jsonEncode({
      'projectId': 'project-1',
      'startedAtEpochMs': 0,
    });
    rig.storage.documents[ProjectStore.fileName] = jsonEncode({
      'schema': ProjectStore.fileSchema,
      'counter': 1,
      'projects': [
        RecentProject(
          id: 'project-1',
          savedAtEpochMs: 0,
          clipCount: 2,
          snapshot: SerializedEditProject(
            schemaVersion: 1,
            json: jsonEncode({'schemaVersion': 1, 'projectId': 'p'}),
          ),
        ).toJson(),
      ],
    });
    await rig.pump(tester);
    expect(find.text('上次导出没有完成'), findsOneWidget);
    expect(find.text('重新导出'), findsOneWidget);
    await tester.tap(find.text('知道了'));
    await settle(tester, 2);
    expect(find.text('上次导出没有完成'), findsNothing);
    expect(rig.storage.documents[ExportJournal.fileName], '{}');
    await unmount(tester);
  });

  test('ExportJournal: begin, end, and a stale entry after a kill', () async {
    final storage = MemoryAppStorage();
    final j = ExportJournal(storage: storage);
    await j.begin('project-7');
    // The App is killed here: a new run finds the entry.
    final next = ExportJournal(storage: storage);
    await next.load();
    expect(next.interrupted?.projectId, 'project-7');
    // A normal end clears it.
    await j.end('project-7');
    final clean = ExportJournal(storage: storage);
    await clean.load();
    expect(clean.interrupted, isNull);
    await j.end('other');
  });

  test('ChannelPermissions without a native handler is unavailable', () async {
    TestWidgetsFlutterBinding.ensureInitialized();
    const p = ChannelPermissions();
    expect(await p.request(AppPermission.camera), PermissionState.unavailable);
    await p.openSettings();
  });

  test('the component list marks undecided entries pending', () {
    expect(appComponents, isNotEmpty);
    expect(
      appComponents.where((c) => c.status == LicenseStatus.pending),
      isNotEmpty,
    );
    expect(
      appComponents.where((c) => c.status == LicenseStatus.adopted),
      isNotEmpty,
    );
  });

  testWidgets('licenses page: names, licenses, 待定, full text', (
    tester,
  ) async {
    final rig = AppRig.create();
    await rig.pump(tester);
    final nav = tester.state<NavigatorState>(find.byType(Navigator).first);
    unawaited(
      nav.push(
        MaterialPageRoute<void>(
          builder: (_) => const LicensesPage(version: '1'),
        ),
      ),
    );
    await settle(tester, 2);
    expect(find.text('AndroidX Media3'), findsOneWidget);
    expect(find.text('播放与导出 · Apache-2.0'), findsOneWidget);
    expect(find.text('待定'), findsWidgets);
    expect(find.textContaining('原生库的许可'), findsOneWidget);
    await unmount(tester);
  });
}
