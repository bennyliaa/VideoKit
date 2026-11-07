// M1-A1 item 1: first-launch backend initialisation, start-up error page
// and retry (VideoKitStateView).
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_app/backend/app_backend.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/startup/app_bootstrap.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// Connector that fails with the queued failures, then succeeds.
final class ScriptedConnector {
  ScriptedConnector(this.failures);

  final List<Object> failures;
  int calls = 0;
  Completer<void>? gate;

  Future<AppBackend> call() async {
    calls++;
    final g = gate;
    if (g != null) await g.future;
    if (failures.isNotEmpty) throw failures.removeAt(0);
    return DemoBackend();
  }
}

Future<void> pumpBootstrap(
  WidgetTester tester,
  ScriptedConnector connect, {
  Size size = compactSize,
  Locale? locale,
  double textScale = 1.0,
}) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1;
  tester.platformDispatcher.textScaleFactorTestValue = textScale;
  addTearDown(tester.view.reset);
  addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
  await tester.pumpWidget(
    AppBootstrap(
      connect: connect.call,
      storage: MemoryAppStorage(),
      now: () => testNow,
      locale: locale,
    ),
  );
  await settle(tester);
}

void main() {
  testWidgets('loading state while the backend connects, then home', (
    tester,
  ) async {
    final c = ScriptedConnector([])..gate = Completer<void>();
    await pumpBootstrap(tester, c);
    expect(find.text('正在启动 VideoKit'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    c.gate!.complete();
    await settle(tester, 6);
    expect(find.text('正在启动 VideoKit'), findsNothing);
    expect(find.text('打开文件'), findsWidgets);
    expect(c.calls, 1);
    await unmount(tester);
  });

  testWidgets('channel unavailable → error page, retry connects', (
    tester,
  ) async {
    final c = ScriptedConnector([
      const AppStartupException(StartupFailure.channelUnavailable, 'x'),
    ]);
    await pumpBootstrap(tester, c);
    expect(find.text('无法连接播放组件'), findsOneWidget);
    expect(find.textContaining('播放组件没有响应'), findsOneWidget);
    expect(find.byType(VideoKitStateView), findsOneWidget);
    // Diagnostics are never shown.
    expect(find.textContaining('x)'), findsNothing);
    await tester.tap(find.text('重试'));
    await settle(tester, 6);
    expect(c.calls, 2);
    expect(find.text('无法连接播放组件'), findsNothing);
    expect(find.text('打开文件'), findsWidgets);
    await unmount(tester);
  });

  testWidgets('retry that fails again shows the error again', (tester) async {
    final c = ScriptedConnector([
      const AppStartupException(StartupFailure.channelUnavailable),
      StateError('boom'),
    ]);
    await pumpBootstrap(tester, c);
    await tester.tap(find.text('重试'));
    await settle(tester);
    expect(c.calls, 2);
    expect(find.text('VideoKit 启动失败'), findsOneWidget);
    expect(find.text('重试'), findsOneWidget);
    await unmount(tester);
  });

  for (final (failure, title) in [
    (StartupFailure.protocolMismatch, 'VideoKit 版本不匹配'),
    (StartupFailure.noBackend, '播放组件不可用'),
  ]) {
    testWidgets('${failure.name}: explanation only, no dead retry', (
      tester,
    ) async {
      final c = ScriptedConnector([AppStartupException(failure)]);
      await pumpBootstrap(tester, c);
      expect(find.text(title), findsOneWidget);
      expect(find.text('重试'), findsNothing);
      expect(find.byType(VkButton), findsNothing);
      await unmount(tester);
    });
  }

  testWidgets('unknown error → generic page with retry', (tester) async {
    final c = ScriptedConnector([Exception('?')]);
    await pumpBootstrap(tester, c);
    expect(find.text('VideoKit 启动失败'), findsOneWidget);
    expect(find.text('重试'), findsOneWidget);
    await unmount(tester);
  });

  testWidgets('error page: a11y, no overflow (zh-XA, 2.0×)', (tester) async {
    final handle = tester.ensureSemantics();
    for (final size in [compactSize, expandedSize]) {
      for (final scale in [1.0, 2.0]) {
        final c = ScriptedConnector([
          const AppStartupException(StartupFailure.channelUnavailable),
        ]);
        await pumpBootstrap(
          tester,
          c,
          size: size,
          textScale: scale,
          locale: VkPseudo.locale,
        );
        expect(tester.takeException(), isNull);
        await unmount(tester);
      }
    }
    final c = ScriptedConnector([
      const AppStartupException(StartupFailure.channelUnavailable),
    ]);
    await pumpBootstrap(tester, c);
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
    await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
    await expectLater(tester, meetsGuideline(textContrastGuideline));
    await unmount(tester);
    handle.dispose();
  });
}
