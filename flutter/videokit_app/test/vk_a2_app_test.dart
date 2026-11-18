// VK-A2 App side (REQ-APP-15 prerequisites, 16 FT-01B): entitlement
// service (always subscribed now), App entry points behind it, privacy
// consent before anything starts, permission purpose before each request.
// The Kit feature gate (REQ-API-10) follows once the feature list is
// confirmed.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/avatar/avatar_adjust_page.dart';
import 'package:videokit_app/entitlement/entitlement_service.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/library/library_page.dart';
import 'package:videokit_app/pages/concat_page.dart';
import 'package:videokit_app/pages/multi_view_page.dart';
import 'package:videokit_app/permissions/app_permissions.dart';
import 'package:videokit_app/startup/privacy_consent.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'app_test.dart' show pickDemo;
import 'library_page_test.dart' show libraryRig, openLibrary;
import 'm4_app_test.dart' show startConcat;
import 'support.dart';

void main() {
  group('FT01B-04 entitlements', () {
    test('always subscribed: every paid feature allowed', () async {
      final s = AlwaysSubscribedEntitlements();
      expect(s.value.status, EntitlementStatus.subscribed);
      for (final f in AppFeature.values) {
        expect(s.allows(f), isTrue, reason: f.name);
      }
      await s.refresh();
      expect(s.value, Entitlement.full);
    });

    test('final split: 5 paid features = the 5 Kit features; the library '
        'is free', () {
      expect(AppFeature.values, [
        AppFeature.multiView,
        AppFeature.edit,
        AppFeature.maskTracking,
        AppFeature.avatar,
        AppFeature.export,
      ]);
      expect(
        VideoKitFeature.configurable.map(AppFeature.ofKit).toList(),
        AppFeature.values,
      );
      expect(AppFeature.ofKit(VideoKitFeature.unknown), isNull);
      const expired = Entitlement(
        status: EntitlementStatus.expired,
        features: {AppFeature.export},
      );
      expect(expired.allows(AppFeature.export), isTrue);
      expect(expired.allows(AppFeature.multiView), isFalse);
    });

    test('trial: everything allowed; days left rounded up', () {
      final now = DateTime(2026, 11, 8, 12);
      final trial = Entitlement(
        status: EntitlementStatus.trial,
        trialEndsAtEpochMs: now
            .add(const Duration(days: 4, hours: 1))
            .millisecondsSinceEpoch,
      );
      expect(AppFeature.values.every(trial.allows), isTrue);
      expect(trial.trialDaysLeft(now), 5);
      expect(Entitlement.full.trialDaysLeft(now), 0);
    });

    testWidgets('default App: concat opens (no gate in the way)', (
      tester,
    ) async {
      final rig = AppRig.create();
      await rig.pump(tester, size: expandedSize);
      await startConcat(tester);
      expect(find.byType(VideoKitEditor), findsOneWidget);
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      await unmount(tester);
    });
  });

  group('FT01B-07 not subscribed', () {
    const expired = Entitlement(status: EntitlementStatus.expired);

    testWidgets('multi-select: both choices show a lock; each asks to '
        'subscribe (订阅 / 恢复购买 / 取消) and nothing opens', (tester) async {
      final rig = AppRig.create();
      await rig.pump(tester, entitlements: FixedEntitlements(expired));
      await tapText(tester, '打开文件');
      await settle(tester, 2);
      await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
      expect(find.bySemanticsLabel('需解锁'), findsNWidgets(2));
      await tapText(tester, '在多画面中打开');
      await settle(tester, 4);
      expect(find.text('多画面需要订阅'), findsOneWidget);
      expect(find.text('订阅'), findsOneWidget);
      expect(find.text('恢复购买'), findsOneWidget);
      await tester.tap(find.text('订阅'));
      await settle(tester, 2);
      expect(find.text('订阅将在正式版本中提供'), findsOneWidget);
      expect(find.byType(MultiViewPage), findsNothing);
      await unmount(tester);
    });

    testWidgets('concat refused; recent projects stay listed and ask on '
        'open', (tester) async {
      final rig = AppRig.create();
      await rig.pump(tester, entitlements: FixedEntitlements(expired));
      await tapText(tester, '打开文件');
      await settle(tester, 2);
      await pickDemo(tester, ['山谷黄昏.mkv', '家庭录像.avi']);
      await tapText(tester, '拼接为一个视频');
      await settle(tester, 4);
      expect(find.text('编辑与拼接需要订阅'), findsOneWidget);
      await tester.tap(find.text('取消'));
      await settle(tester, 2);
      expect(find.byType(ConcatPage), findsNothing);
      await unmount(tester);
    });

    testWidgets('the library is free: opens, imports', (tester) async {
      final rig = libraryRig(videos: 2);
      await rig.pump(tester, entitlements: FixedEntitlements(expired));
      expect(find.bySemanticsLabel('需解锁'), findsNothing, reason: 'free');
      await openLibrary(tester);
      expect(find.byType(LibraryPage), findsOneWidget);
      await tester.tap(find.text('导入'));
      await settle(tester, 2);
      expect(find.text('选择视频和图片'), findsOneWidget, reason: 'no prompt');
      await unmount(tester);
    });

    testWidgets('editor: locked Kit entries; the App answers the gate with '
        'its prompt and the Kit does not enter', (tester) async {
      final rig = AppRig.create();
      final service = AlwaysSubscribedEntitlements();
      await rig.pump(tester, size: expandedSize, entitlements: service);
      await startConcat(tester);
      final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
      service.debugSimulate(EntitlementStatus.expired);
      await settle(tester, 2);
      expect(find.bySemanticsLabel('需解锁'), findsWidgets, reason: 'locks');
      await tester.tap(find.text('打码'));
      await settle(tester, 2);
      expect(find.text('打码与跟踪需要订阅'), findsOneWidget);
      await tester.tap(find.text('取消'));
      await settle(tester, 2);
      expect(e.controller.mode, EditorMode.clips, reason: 'not entered');
      await tester.tap(find.text('导出'));
      await settle(tester, 2);
      expect(find.text('导出需要订阅'), findsOneWidget);
      await tester.tap(find.text('取消'));
      await settle(tester, 2);
      await tester.binding.handlePopRoute();
      await settle(tester, 6);
      await unmount(tester);
    });
  });

  group('debug switches (default: subscribed)', () {
    test('simulate not subscribed / trial / back', () {
      final now = DateTime(2026, 11, 8);
      final s = AlwaysSubscribedEntitlements(now: () => now);
      s.debugSimulate(EntitlementStatus.expired);
      expect(s.simulatingUnsubscribed, isTrue, reason: 'tests run in debug');
      expect(s.allows(AppFeature.multiView), isFalse);
      s.debugSimulate(EntitlementStatus.trial);
      expect((s.simulatingTrial, s.allows(AppFeature.edit)), (true, true));
      expect(s.value.trialDaysLeft(now), 5);
      s.debugSimulate(EntitlementStatus.subscribed);
      expect(s.value, Entitlement.full);
    });

    testWidgets('settings has both switches; trial shows "试用中 · 剩 5 天" '
        'and no locks', (tester) async {
      final rig = AppRig.create();
      final service = AlwaysSubscribedEntitlements(now: () => testNow);
      await rig.pump(tester, entitlements: service);
      expect(find.textContaining('试用中'), findsNothing);
      await tester.tap(find.bySemanticsLabel('设置'));
      await settle(tester, 3);
      await tester.scrollUntilVisible(find.text('模拟试用中（调试）'), 200);
      expect(find.text('模拟未订阅（调试）'), findsOneWidget);
      await tester.tap(find.bySemanticsLabel('模拟试用中（调试）'));
      await settle(tester, 2);
      expect(service.simulatingTrial, isTrue);
      await tester.binding.handlePopRoute();
      await settle(tester, 2);
      expect(find.text('试用中 · 剩 5 天'), findsOneWidget);
      expect(find.bySemanticsLabel('需解锁'), findsNothing);
      await unmount(tester);
    });
  });

  group('FT01B-05 privacy first launch', () {
    Future<(MemoryAppStorage, List<String>)> pumpGate(
      WidgetTester tester, {
      MemoryAppStorage? storage,
      VoidCallback? onExit,
    }) async {
      final s = storage ?? MemoryAppStorage();
      final built = <String>[];
      await tester.pumpWidget(
        PrivacyGate(
          storage: s,
          onExit: onExit,
          builder: () {
            built.add('app');
            return const Directionality(
              textDirection: TextDirection.ltr,
              child: Text('APP STARTED'),
            );
          },
        ),
      );
      await tester.pump();
      await tester.pump();
      return (s, built);
    }

    testWidgets('nothing starts before consent; agreeing starts it and is '
        'remembered', (tester) async {
      final (storage, built) = await pumpGate(tester);
      expect(find.text('隐私政策与用户协议'), findsOneWidget);
      expect(built, isEmpty, reason: 'no backend, no SDK before consent');
      expect(storage.documents.keys, isEmpty, reason: 'nothing written');
      await tester.tap(find.text('同意并继续'));
      await tester.pump();
      await tester.pump();
      expect(find.text('APP STARTED'), findsOneWidget);
      expect(built, ['app']);
      expect(storage.documents, contains(PrivacyConsentStore.fileName));
      await unmount(tester);
      final (_, again) = await pumpGate(tester, storage: storage);
      expect(find.text('隐私政策与用户协议'), findsNothing);
      expect(again, ['app'], reason: 'asked once');
      await unmount(tester);
    });

    testWidgets('refusing: only the policy, agreeing again, or exit', (
      tester,
    ) async {
      var exited = 0;
      final (_, built) = await pumpGate(tester, onExit: () => exited++);
      await tester.tap(find.text('不同意'));
      await tester.pump();
      expect(find.text('需要你的同意才能使用'), findsOneWidget);
      expect(find.text('同意并继续'), findsNothing);
      await tester.tap(find.text('查看《隐私政策》'));
      await tester.pumpAndSettle();
      expect(find.text('隐私政策'), findsOneWidget);
      await tester.binding.handlePopRoute();
      await tester.pumpAndSettle();
      await tester.tap(find.text('退出'));
      expect(exited, 1);
      await tester.tap(find.text('再次查看并同意'));
      await tester.pump();
      expect(find.text('同意并继续'), findsOneWidget);
      expect(built, isEmpty);
      await unmount(tester);
    });

    testWidgets('a newer policy version asks again', (tester) async {
      final storage = MemoryAppStorage()
        ..documents[PrivacyConsentStore.fileName] =
            '{"version":0,"acceptedAtEpochMs":1}';
      final (_, built) = await pumpGate(tester, storage: storage);
      expect(find.text('隐私政策与用户协议'), findsOneWidget);
      expect(built, isEmpty);
      await unmount(tester);
    });
  });

  group('FT01B-06 permission purpose first', () {
    Future<AppRig> pickPage(WidgetTester tester) async {
      final rig = AppRig.create();
      rig.backend.permissions.setStatus(
        AppPermission.camera,
        PermissionState.denied,
      );
      await rig.pump(tester, size: expandedSize);
      await startConcat(tester);
      final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
      e.openMasks(MaskEditorTab.manual);
      await settle(tester, 2);
      unawaited(e.maskEditor!.addManualMask());
      await settle(tester, 2);
      await tester.tap(find.text('头像'));
      await settle(tester, 4);
      return rig;
    }

    testWidgets('the purpose shows before the system asks; cancel asks '
        'nothing; continue asks', (tester) async {
      final rig = await pickPage(tester);
      await tester.tap(find.text('拍一张'));
      await settle(tester, 2);
      expect(find.text('需要相机权限'), findsOneWidget);
      expect(
        find.text('相机用于拍一张照片作为头像。只在你点“拍一张”时使用，照片只保存在本机。'),
        findsOneWidget,
      );
      expect(rig.backend.permissions.requested, isEmpty);
      await tester.tap(find.text('取消'));
      await settle(tester, 2);
      expect(rig.backend.permissions.requested, isEmpty);
      expect(find.byType(AvatarAdjustPage), findsNothing, reason: 'degraded');
      // Again: this time continue.
      await tester.tap(find.text('拍一张'));
      await settle(tester, 2);
      await tester.tap(find.text('继续'));
      await settle(tester, 8);
      expect(rig.backend.permissions.requested, [AppPermission.camera]);
      expect(find.byType(AvatarAdjustPage), findsOneWidget);
      await unmount(tester);
    });
  });
}
