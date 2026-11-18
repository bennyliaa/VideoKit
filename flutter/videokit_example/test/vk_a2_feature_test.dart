// VK-A2 (REQ-API-10, 16 FT01B-01/02/03): the example host's "功能开关"
// panel; videokit_ui hides entries of hidden features, asks the gate
// before an entry opens, shows the host's marker and stays put when
// denied; without a gate nothing changes.
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_example/features/feature_switch_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

void main() {
  Future<void> frames(WidgetTester tester, [int n = 4]) async {
    for (var i = 0; i < n; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }
  }

  Future<void> unmount(WidgetTester tester) async {
    await tester.pumpWidget(const SizedBox());
    await tester.pump(Duration.zero);
  }

  Future<VideoKitEditorState?> editor(
    WidgetTester tester, {
    Set<VideoKitFeature> hidden = const {},
    Map<VideoKitFeature, GateAnswer> answers = const {},
    bool gate = true,
    Size size = expandedSize,
  }) async {
    setViewSize(tester, size);
    final host = gate
        ? GateDemoHost(answers: answers)
        : const NoopHostCallbacks();
    await tester.pumpWidget(
      testApp(
        EditDemoPage(
          showScenarioPicker: false,
          features: VideoKitFeatureConfig({
            for (final f in hidden) f: FeatureMode.hidden,
          }),
          hostCallbacks: host,
        ),
      ),
    );
    await frames(tester, 15);
    final e = find.byType(VideoKitEditor);
    return e.evaluate().isEmpty
        ? null
        : tester.state<VideoKitEditorState>(e);
  }

  group('FT01B-01 hidden features', () {
    testWidgets('EDIT hidden: no editor, "这个功能未开放"', (tester) async {
      final e = await editor(tester, hidden: {VideoKitFeature.edit});
      expect(e, isNull);
      expect(find.text('这个功能未开放'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('MASK_TRACKING hidden: no 打码 / 跟踪; export stays', (
      tester,
    ) async {
      await editor(tester, hidden: {VideoKitFeature.maskTracking});
      expect(find.text('打码'), findsNothing);
      expect(find.text('跟踪'), findsNothing);
      expect(find.text('导出'), findsOneWidget);
      await unmount(tester);
    });

    testWidgets('EXPORT hidden: no 导出 (phone tab bar too)', (tester) async {
      await editor(tester, hidden: {VideoKitFeature.export});
      expect(find.text('导出'), findsNothing);
      expect(find.text('打码'), findsOneWidget);
      await unmount(tester);
      await editor(
        tester,
        hidden: {VideoKitFeature.export},
        size: compactSize,
      );
      expect(find.text('导出'), findsNothing);
      await unmount(tester);
    });

    testWidgets('AVATAR hidden: no "头像" style; mosaic and blur stay', (
      tester,
    ) async {
      final e = (await editor(tester, hidden: {VideoKitFeature.avatar}))!;
      e.openMasks(MaskEditorTab.manual);
      await frames(tester);
      unawaited(e.maskEditor!.addManualMask());
      await frames(tester);
      expect(find.text('马赛克'), findsWidgets);
      expect(find.text('头像'), findsNothing);
      await unmount(tester);
    });

    testWidgets('player: no 编辑 entry when EDIT is hidden', (tester) async {
      setViewSize(tester, expandedSize);
      final rig = await PlayerRig.create('normal');
      addTearDown(rig.dispose);
      final features = VideoKitFeatures(
        const VideoKitFeatureGate(
          config: VideoKitFeatureConfig({
            VideoKitFeature.edit: FeatureMode.hidden,
          }),
        ),
      );
      await tester.pumpWidget(
        testApp(
          VideoKitFeatureScope(
            features: features,
            child: demoPlayer(rig.session),
          ),
        ),
      );
      await rig.advance(tester, const Duration(seconds: 1));
      expect(find.bySemanticsLabel('编辑'), findsNothing);
      await unmount(tester);
    });
  });

  group('FT01B-02 denied', () {
    testWidgets('打码 denied: the host\'s page, the lock, no mask editor', (
      tester,
    ) async {
      setViewSize(tester, expandedSize);
      await tester.pumpWidget(testApp(const FeatureSwitchPage()));
      await frames(tester);
      final page = tester.state<FeatureSwitchPageState>(
        find.byType(FeatureSwitchPage),
      );
      page.answers[VideoKitFeature.maskTracking] = GateAnswer.deny;
      page.openEditor();
      await frames(tester, 15);
      final e = tester.state<VideoKitEditorState>(find.byType(VideoKitEditor));
      await tester.tap(find.text('打码'));
      await frames(tester, 2);
      expect(find.text('示例宿主的付费页'), findsOneWidget);
      await tester.tap(find.text('关闭'));
      await frames(tester, 2);
      expect(e.controller.mode, EditorMode.clips, reason: 'not entered');
      expect(find.bySemanticsLabel('需解锁'), findsWidgets, reason: 'lock');
      await unmount(tester);
    });

    testWidgets('trial: entered, with the "试用中" marker', (tester) async {
      final e = (await editor(
        tester,
        answers: {VideoKitFeature.maskTracking: GateAnswer.trial},
      ))!;
      await tester.tap(find.text('打码'));
      await frames(tester, 3);
      expect(e.controller.mode, EditorMode.mask);
      final demo = tester.state<EditDemoPageState>(find.byType(EditDemoPage));
      expect(
        demo.features.badgeOf(VideoKitFeature.maskTracking),
        FeatureBadge.trial,
      );
      e.controller.mode = EditorMode.clips;
      await frames(tester, 2);
      expect(find.text('试用中'), findsWidgets, reason: 'on the entries');
      await unmount(tester);
    });

    testWidgets('direct API calls return the codes', (tester) async {
      setViewSize(tester, expandedSize);
      await tester.pumpWidget(testApp(const FeatureSwitchPage()));
      await frames(tester);
      final page = tester.state<FeatureSwitchPageState>(
        find.byType(FeatureSwitchPage),
      );
      page.hidden.add(VideoKitFeature.maskTracking);
      page.answers[VideoKitFeature.export] = GateAnswer.trial;
      await tester.runAsync(page.callApi);
      await frames(tester);
      expect(page.apiResult, 'AddMask: FEATURE_DISABLED · export: OK');
      page.hidden
        ..clear()
        ..add(VideoKitFeature.edit);
      await tester.runAsync(page.callApi);
      expect(page.apiResult, 'createEditProject: FEATURE_DISABLED');
      await unmount(tester);
    });
  });

  testWidgets('FT01B-03 no gate: everything as before', (tester) async {
    final e = (await editor(tester, gate: false))!;
    expect(find.text('打码'), findsOneWidget);
    expect(find.text('导出'), findsOneWidget);
    await tester.tap(find.text('打码'));
    await frames(tester, 2);
    expect(e.controller.mode, EditorMode.mask);
    expect(find.bySemanticsLabel('需解锁'), findsNothing);
    await unmount(tester);
  });
}
