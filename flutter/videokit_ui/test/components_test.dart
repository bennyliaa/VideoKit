import 'dart:io';
import 'dart:ui' show Tristate;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

Widget _app(Widget child, {Locale locale = const Locale('zh')}) => MaterialApp(
  locale: locale,
  localizationsDelegates: videoKitLocalizationsDelegates,
  supportedLocales: videoKitSupportedLocales,
  theme: ThemeData.dark(),
  home: VideoKitThemeScope(child: Scaffold(body: child)),
);

void main() {
  testWidgets(
    'VkButton / VkIconButton: semantics, disabled, selected, pending',
    (tester) async {
      var taps = 0;
      await tester.pumpWidget(
        _app(
          Column(
            children: [
              VkButton(label: '主要操作', onPressed: () => taps++),
              const VkButton(label: '禁用', onPressed: null),
              VkIconButton(
                icon: Icons.tag,
                semanticLabel: '标签',
                onPressed: () => taps++,
                pending: true,
                badgeText: '12345',
              ),
            ],
          ),
        ),
      );
      await tester.tap(find.text('主要操作'));
      await tester.tap(find.bySemanticsLabel('标签'));
      expect(taps, 2);
      final disabled = tester.getSemantics(find.bySemanticsLabel('禁用'));
      expect(disabled.flagsCollection.isEnabled, Tristate.isFalse);
      final pending = tester.getSemantics(find.bySemanticsLabel('标签'));
      expect(pending.hint, '等待中');
      expect(find.text('12…'), findsOneWidget, reason: 'badge ≤ 3 chars');
      expect(
        tester.getSize(find.byType(VkIconButton)).height,
        greaterThanOrEqualTo(48),
      );
      // Keyboard activation.
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.sendKeyEvent(LogicalKeyboardKey.enter);
      await tester.pump();
      expect(taps, 3);
    },
  );

  testWidgets(
    'VkSheetHost: panel opens, back and Esc close it, toast dismisses',
    (tester) async {
      final c = VkSheetController();
      await tester.pumpWidget(
        _app(VkSheetHost(controller: c, child: const SizedBox.expand())),
      );
      c.show(
        VkSheetEntry(id: 'p', title: '播放设置', builder: (_) => const Text('内容')),
      );
      await tester.pumpAndSettle();
      expect(find.text('播放设置'), findsOneWidget);
      final popped = await tester.binding.handlePopRoute();
      await tester.pumpAndSettle();
      expect(popped, isTrue);
      expect(
        c.hasPanel,
        isFalse,
        reason: 'back closes the panel, not the route',
      );
      c.show(
        VkSheetEntry(id: 'p', title: '播放设置', builder: (_) => const Text('内容')),
      );
      await tester.pumpAndSettle();
      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pumpAndSettle();
      expect(c.hasPanel, isFalse);
      c.showToast(const VkToastEntry(message: '提示'));
      await tester.pump();
      expect(find.text('提示'), findsOneWidget);
      await tester.pump(const Duration(seconds: 4));
      expect(find.text('提示'), findsNothing);
      c.dispose();
    },
  );

  testWidgets('VkSeekBar: drag previews locally and commits once', (
    tester,
  ) async {
    final updates = <int>[];
    final ends = <int>[];
    await tester.pumpWidget(
      _app(
        Center(
          child: SizedBox(
            width: 300,
            child: VkSeekBar(
              positionUs: 0,
              durationUs: 300000000,
              bufferedUs: 60000000,
              onDragUpdate: updates.add,
              onDragEnd: ends.add,
            ),
          ),
        ),
      ),
    );
    final bar = find.byType(VkSeekBar);
    final g = await tester.startGesture(
      tester.getCenter(bar) - const Offset(140, 0),
    );
    for (var i = 0; i < 20; i++) {
      await g.moveBy(const Offset(10, 0));
      await tester.pump(const Duration(milliseconds: 16));
    }
    expect(find.textContaining(':'), findsWidgets, reason: 'time bubble');
    await g.up();
    await tester.pump();
    expect(updates.length, greaterThan(5));
    expect(ends, hasLength(1));
    final sem = tester.getSemantics(bar);
    expect(sem.label, '播放进度');
    expect(sem.value, '0 秒，共 5 分 0 秒');
  });

  testWidgets('VkSlider commits on release and supports a11y steps', (
    tester,
  ) async {
    final ends = <double>[];
    await tester.pumpWidget(
      _app(
        Center(
          child: SizedBox(
            width: 200,
            child: VkSlider(
              value: 0.5,
              semanticLabel: '音量',
              semanticValue: (v) => '${(v * 100).round()}',
              onChangeEnd: ends.add,
            ),
          ),
        ),
      ),
    );
    await tester.drag(find.byType(VkSlider), const Offset(50, 0));
    await tester.pump();
    expect(ends, hasLength(1));
    final node = tester.getSemantics(find.byType(VkSlider));
    expect(node.label, '音量');
  });

  testWidgets('VideoKitStateView: title, detail, actions call back', (
    tester,
  ) async {
    final actions = <StateAction>[];
    await tester.pumpWidget(
      _app(
        VideoKitStateView(
          model: mapError(
            const VideoKitStableError(
              code: ErrorCode.sourceDisconnected,
              stage: ErrorStage.playback,
              retryable: true,
              suggestedAction: SuggestedAction.retry,
            ),
          ),
          onStateAction: actions.add,
        ),
      ),
    );
    expect(find.text('连接中断'), findsOneWidget);
    expect(find.text('请检查网络或存储连接后重试'), findsOneWidget);
    await tester.tap(find.text('重试'));
    expect(actions, [StateAction.retry]);
    await tester.pumpWidget(
      _app(
        VideoKitStateView.forSession(
          state: VideoKitSessionState(phase: SessionPhase.binding),
        ),
      ),
    );
    expect(find.text('正在打开…'), findsOneWidget);
    expect(find.text('读取媒体信息'), findsOneWidget);
  });

  testWidgets('HostActionBar: states, overflow menu, disabled semantics', (
    tester,
  ) async {
    final pressed = <String>[];
    VideoKitHostAction a(
      String id, {
      bool enabled = true,
      bool selected = false,
      ActionPlacement p = ActionPlacement.primaryBar,
      String? badge,
    }) => VideoKitHostAction(
      actionId: id,
      labelKey: 'label.$id',
      contentDescriptionKey: 'cd.$id',
      icon: HostIcon.builtIn(id),
      placement: p,
      enabled: enabled,
      selected: selected,
      badgeText: badge,
    );
    final c = VkSheetController();
    await tester.pumpWidget(
      _app(
        VkSheetHost(
          controller: c,
          child: Align(
            alignment: Alignment.topCenter,
            child: HostActionBar(
              actions: [
                HostActionState(action: a('favorite', selected: true)),
                HostActionState(action: a('tag'), pending: true),
                HostActionState(action: a('delete', enabled: false)),
                HostActionState(
                  action: a('share', p: ActionPlacement.overflow),
                ),
              ],
              resolveString: (k) => switch (k) {
                'label.favorite' => '已收藏',
                'label.tag' => '标签',
                'label.share' => '分享',
                _ => k,
              },
              onActionPressed: pressed.add,
            ),
          ),
        ),
      ),
    );
    expect(find.text('已收藏'), findsOneWidget);
    expect(tester.getSemantics(find.bySemanticsLabel('cd.delete')).hint, '不可用');
    expect(tester.getSemantics(find.bySemanticsLabel('cd.tag')).hint, '等待中');
    await tester.tap(find.bySemanticsLabel('cd.favorite'));
    await tester.tap(find.bySemanticsLabel('cd.delete'));
    expect(pressed, ['favorite']);
    await tester.tap(find.bySemanticsLabel('更多操作'));
    await tester.pump(const Duration(milliseconds: 500));
    await tester.tap(find.text('分享'));
    await tester.pump(const Duration(milliseconds: 500));
    expect(pressed, ['favorite', 'share']);
    expect(c.hasPanel, isFalse);
    c.dispose();
  });

  test('no hard-coded colours, font sizes or text literals in components', () {
    // 13 §3 / 14 §11.3 manual lint (custom_lint not yet in the toolchain).
    const dirs = [
      'common',
      'state_view',
      'player',
      'host_action',
      'foundation',
    ];
    final pattern = RegExp(
      r"Color\(0x|Colors\.|fontSize:|Text\(\s*'|label:\s*'",
    );
    final offenders = <String>[];
    for (final d in dirs) {
      for (final f in Directory('lib/src/$d').listSync().whereType<File>()) {
        final lines = f.readAsLinesSync();
        for (final (i, l) in lines.indexed) {
          if (pattern.hasMatch(l)) offenders.add('${f.path}:${i + 1}: $l');
        }
      }
    }
    expect(offenders, isEmpty);
  });
}
