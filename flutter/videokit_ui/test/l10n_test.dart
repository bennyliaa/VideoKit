import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

Map<String, Object?> _zhArb() =>
    jsonDecode(File('lib/l10n/app_zh.arb').readAsStringSync())
        as Map<String, Object?>;

Set<String> _keys(Map<String, Object?> arb) =>
    arb.keys.where((k) => !k.startsWith('@')).toSet();

void main() {
  group('ARB (13 §3.1)', () {
    test('template is app_zh.arb; only Chinese is maintained', () {
      final files = Directory('lib/l10n')
          .listSync()
          .whereType<File>()
          .map((f) => f.uri.pathSegments.last)
          .toList();
      expect(files, ['app_zh.arb']);
      expect(
        File('l10n.yaml').readAsStringSync(),
        contains('template-arb-file: app_zh.arb'),
      );
      expect(VideoKitLocalizations.supportedLocales, [const Locale('zh')]);
    });

    test('keys are English semantic names, documented and non-empty', () {
      final arb = _zhArb();
      for (final k in _keys(arb)) {
        expect(RegExp(r'^[a-z][a-zA-Z0-9]+$').hasMatch(k), isTrue, reason: k);
        expect((arb[k]! as String).trim(), isNotEmpty, reason: k);
        expect(arb['@$k'], isNotNull, reason: 'missing @$k description');
      }
    });

    test('every key referenced by components exists in app_zh.arb', () {
      final arb = _keys(_zhArb());
      final s = VkStrings.forLocale(const Locale('zh'));
      final referenced = {...s.defaults.keys, ...VkStrings.placeholderKeys};
      expect(
        arb.containsAll(referenced),
        isTrue,
        reason: 'missing: ${referenced.difference(arb)}',
      );
      expect(
        referenced,
        arb,
        reason: 'unused ARB keys: ${arb.difference(referenced)}',
      );
      for (final v in s.defaults.values) {
        expect(v.trim(), isNotEmpty);
      }
    });
  });

  group('VkStrings', () {
    test('every ErrorCode and SuggestedAction has text', () {
      final s = VkStrings.forLocale(const Locale('zh'));
      for (final code in ErrorCode.values) {
        expect(s.error(code), isNotEmpty);
        expect(VkStrings.errorKey(code), startsWith('error'));
      }
      expect(s.error(ErrorCode.sourceDisconnected), '连接中断');
      expect(
        s.error(ErrorCode.fromName('FUTURE_CODE')),
        s.error(ErrorCode.internalErrorRedacted),
      );
      for (final a in SuggestedAction.values) {
        a == SuggestedAction.none
            ? expect(s.action(a), isNull)
            : expect(s.action(a), isNotEmpty);
      }
    });

    test('fallback is Chinese for any language (first version)', () {
      for (final l in const [Locale('en'), Locale('fr'), Locale('ja')]) {
        expect(VkStrings.forLocale(l).demoBadge, '演示模式 · 模拟数据');
        expect(
          videoKitResolveLocale(l, videoKitSupportedLocales),
          const Locale('zh'),
        );
      }
      expect(
        videoKitResolveLocale(VkPseudo.locale, videoKitSupportedLocales),
        VkPseudo.locale,
      );
    });

    test('pseudo-localization lengthens ~40 % and brackets', () {
      expect(VkPseudo.transform('连接中断'), '［连接中断］');
      final long = VkPseudo.transform('此视频没有可选音轨');
      expect(long.runes.length, greaterThanOrEqualTo((9 * 1.4).ceil()));
      expect(long, startsWith('［'));
      final p = VkStrings.forLocale(VkPseudo.locale);
      expect(p.pseudo, isTrue);
      expect(p.error(ErrorCode.corruptMedia), startsWith('［文件已损坏'));
      expect(p.demoBadge, endsWith('］'));
      expect(VkPseudo.transform(''), '');
    });

    test('ICU plural durations, locale formatting, file sizes', () {
      final s = VkStrings.forLocale(const Locale('zh'));
      expect(VkFormat.durationSpoken(s, 65000000), '1 分 5 秒');
      expect(VkFormat.durationSpoken(s, 5000000), '5 秒');
      expect(VkFormat.durationSpoken(s, 3725000000), '1 小时 2 分 5 秒');
      expect(VkFormat.seekValue(s, 65000000, 750000000), '1 分 5 秒，共 12 分 30 秒');
      expect(VkFormat.timecode(65000000), '01:05');
      expect(VkFormat.timecode(3725000000), '1:02:05');
      expect(VkFormat.timecode(-1), '00:00');
      expect(VkFormat.number(s, 12345.67), '12,345.7');
      expect(VkFormat.percent(s, 0.5), '50%');
      expect(VkFormat.fileSize(s, 512), '512 字节');
      expect(VkFormat.fileSize(s, 1500), '1.5 KB');
      expect(VkFormat.fileSize(s, 999), '999 字节');
      expect(VkFormat.fileSize(s, 5000000), '5 MB');
      expect(VkFormat.fileSize(s, 3000000000), '3 GB');
      final p = VkStrings.forLocale(VkPseudo.locale);
      expect(
        VkFormat.percent(p, 0.5),
        '50%',
        reason: 'pseudo uses zh number rules',
      );
    });
  });

  testWidgets('host overrides, pseudo locale and missing delegate', (
    tester,
  ) async {
    late VkStrings s;
    Widget probe() => Builder(
      builder: (context) {
        s = VkStrings.of(context);
        return const SizedBox();
      },
    );
    await tester.pumpWidget(
      MaterialApp(
        locale: const Locale('zh'),
        localizationsDelegates: videoKitLocalizationsDelegates,
        supportedLocales: videoKitSupportedLocales,
        home: VideoKitStrings(
          overrides: const {
            'errorSourceDisconnected': 'NAS 已断开',
            'commonRetry': '再试一次',
          },
          child: probe(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(s.error(ErrorCode.sourceDisconnected), 'NAS 已断开');
    expect(s.text('commonRetry'), '再试一次');
    expect(s.error(ErrorCode.corruptMedia), '文件已损坏或不完整');

    await tester.pumpWidget(
      MaterialApp(
        locale: VkPseudo.locale,
        localizationsDelegates: videoKitLocalizationsDelegates,
        supportedLocales: videoKitSupportedLocales,
        home: probe(),
      ),
    );
    await tester.pumpAndSettle();
    expect(s.pseudo, isTrue);
    expect(s.text('commonRetry'), '［重试］');

    await tester.pumpWidget(
      Localizations(
        locale: const Locale('en'),
        delegates: const [DefaultWidgetsLocalizations.delegate],
        child: probe(),
      ),
    );
    expect(s.text('commonRetry'), '重试');
  });
}
