import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'dart:async';

import 'package:videokit_example/editor/edit_demo_page.dart';
import 'package:videokit_example/gallery/components_page.dart';
import 'package:videokit_example/image/image_demo_page.dart';
import 'package:videokit_example/multiview/multi_view_demo_page.dart';
import 'package:videokit_example/player/player_demo_page.dart';
import 'package:videokit_ui/videokit_ui.dart';

import 'support.dart';

/// {中文, 伪本地化} × {1.0, 1.3, 2.0} × {compact, expanded} (M0-B2 item 5).
const _locales = [Locale('zh'), VkPseudo.locale];
const _scales = [1.0, 1.3, 2.0];
const _sizes = {'compact': compactSize, 'expanded': expandedSize};

void main() {
  for (final locale in _locales) {
    for (final scale in _scales) {
      for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
        final tag = '${locale.toLanguageTag()} × $scale × $sizeName';

        testWidgets('player + panels without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          final rig = await PlayerRig.create('normal');
          addTearDown(rig.dispose);
          final key = GlobalKey<VideoKitPlayerState>();
          await tester.pumpWidget(
            testApp(
              demoPlayer(rig.session, key: key),
              locale: locale,
              textScale: scale,
            ),
          );
          await rig.advance(tester, const Duration(seconds: 1));
          expect(tester.takeException(), isNull);
          for (final panel in [
            PlayerPanel.speed,
            PlayerPanel.subtitles,
            PlayerPanel.audio,
            PlayerPanel.more,
            PlayerPanel.mediaInfo,
          ]) {
            key.currentState!.openPanel(panel);
            await tester.pump(const Duration(milliseconds: 400));
            expect(tester.takeException(), isNull, reason: panel.name);
            await tester.binding.handlePopRoute();
            await tester.pump(const Duration(milliseconds: 400));
          }
          expect(tester.takeException(), isNull);
        });

        testWidgets('player state views without overflow: $tag', (
          tester,
        ) async {
          setViewSize(tester, size);
          for (final scenario in ['slowLoad', 'unsupported']) {
            final rig = await PlayerRig.create(scenario);
            await tester.pumpWidget(
              testApp(
                demoPlayer(rig.session),
                locale: locale,
                textScale: scale,
              ),
            );
            await rig.advance(tester, const Duration(milliseconds: 500));
            expect(tester.takeException(), isNull, reason: scenario);
            await tester.pumpWidget(const SizedBox());
            rig.dispose();
            await tester.pump(Duration.zero);
          }
        });

        testWidgets('components page without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(const ComponentsPage(), locale: locale, textScale: scale),
          );
          await tester.pump(const Duration(milliseconds: 100));
          expect(tester.takeException(), isNull);
          for (var i = 0; i < 20; i++) {
            await tester.drag(
              find.byType(ListView).first,
              Offset(0, -size.height * 0.8),
            );
            await tester.pump(const Duration(milliseconds: 200));
            expect(tester.takeException(), isNull);
          }
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
        });

        testWidgets('player demo page without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(const PlayerDemoPage(), locale: locale, textScale: scale),
          );
          for (var i = 0; i < 10; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          expect(tester.takeException(), isNull);
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
        });

        testWidgets('image viewer pages without overflow: $tag', (
          tester,
        ) async {
          setViewSize(tester, size);
          for (final index in [0, 1, 3]) {
            final key = GlobalKey<ImageDemoPageState>();
            await tester.pumpWidget(
              testApp(
                ImageDemoPage(key: key, initialIndex: index),
                locale: locale,
                textScale: scale,
              ),
            );
            for (var i = 0; i < 8; i++) {
              await tester.pump(const Duration(milliseconds: 200));
            }
            expect(tester.takeException(), isNull, reason: 'page $index');
            // 04A U1: the unsupported page keeps only back, title, paging.
            if (index == 3) {
              await tester.pumpWidget(const SizedBox());
              await tester.pump(Duration.zero);
              continue;
            }
            key.currentState!.session!.setControlsVisible(true);
            await tester.tap(
              find
                  .bySemanticsLabel(
                    VkPseudo.isPseudo(locale)
                        ? VkPseudo.transform('图片信息')
                        : '图片信息',
                  )
                  .first,
            );
            for (var i = 0; i < 3; i++) {
              await tester.pump(const Duration(milliseconds: 200));
            }
            expect(tester.takeException(), isNull, reason: 'info $index');
            await tester.pumpWidget(const SizedBox());
            await tester.pump(Duration.zero);
          }
        });

        testWidgets('editor modes without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(
              const EditDemoPage(showScenarioPicker: false),
              locale: locale,
              textScale: scale,
            ),
          );
          for (var i = 0; i < 15; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          expect(tester.takeException(), isNull, reason: 'clips');
          final e = tester.state<VideoKitEditorState>(
            find.byType(VideoKitEditor),
          );
          e.controller.selectClip(e.controller.state.timeline.clips[1].clipId);
          await tester.pump(const Duration(milliseconds: 200));
          expect(tester.takeException(), isNull, reason: 'selected');
          e.openMasks(MaskEditorTab.manual);
          await tester.pump(const Duration(milliseconds: 200));
          unawaited(e.maskEditor!.addManualMask());
          await tester.pump(const Duration(milliseconds: 400));
          expect(tester.takeException(), isNull, reason: 'mask');
          e.openMasks(MaskEditorTab.tracking);
          await tester.pump(const Duration(milliseconds: 200));
          unawaited(e.maskEditor!.detectFaces());
          for (var i = 0; i < 3; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          expect(tester.takeException(), isNull, reason: 'tracking');
          e.openExport();
          for (var i = 0; i < 3; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          expect(tester.takeException(), isNull, reason: 'export');
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
        });
        testWidgets('multi-view page without overflow: $tag', (tester) async {
          setViewSize(tester, size);
          for (final count in [4, 12]) {
            await tester.pumpWidget(
              testApp(
                MultiViewDemoPage(initialCount: count),
                locale: locale,
                textScale: scale,
              ),
            );
            for (var i = 0; i < 12; i++) {
              await tester.pump(const Duration(milliseconds: 200));
            }
            expect(tester.takeException(), isNull, reason: '$count slots');
            await tester.pumpWidget(const SizedBox());
            await tester.pump(Duration.zero);
          }
        });
      }
    }
  }

  group('accessibility guidelines', () {
    for (final MapEntry(key: sizeName, value: size) in _sizes.entries) {
      for (final mode in ['clips', 'mask', 'tracking', 'export']) {
        testWidgets('editor $mode: tap targets, labels, contrast ($sizeName)', (
          tester,
        ) async {
          final handle = tester.ensureSemantics();
          setViewSize(tester, size);
          await tester.pumpWidget(
            testApp(const EditDemoPage(showScenarioPicker: false)),
          );
          for (var i = 0; i < 15; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          final e = tester.state<VideoKitEditorState>(
            find.byType(VideoKitEditor),
          );
          e.controller.selectClip(e.controller.state.timeline.clips[0].clipId);
          switch (mode) {
            case 'mask':
              e.openMasks(MaskEditorTab.manual);
              await tester.pump(const Duration(milliseconds: 200));
              unawaited(e.maskEditor!.addManualMask());
            case 'tracking':
              e.openMasks(MaskEditorTab.tracking);
              await tester.pump(const Duration(milliseconds: 200));
              unawaited(e.maskEditor!.detectFaces());
            case 'export':
              e.openExport();
          }
          for (var i = 0; i < 4; i++) {
            await tester.pump(const Duration(milliseconds: 200));
          }
          await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
          await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
          await expectLater(tester, meetsGuideline(textContrastGuideline));
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
          handle.dispose();
        });
      }

      testWidgets('image viewer: tap targets, labels, contrast ($sizeName)', (
        tester,
      ) async {
        final handle = tester.ensureSemantics();
        setViewSize(tester, size);
        await tester.pumpWidget(testApp(const ImageDemoPage(initialIndex: 1)));
        for (var i = 0; i < 6; i++) {
          await tester.pump(const Duration(milliseconds: 200));
        }
        await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        await tester.pumpWidget(const SizedBox());
        await tester.pump(Duration.zero);
        handle.dispose();
      });

      testWidgets('multi-view: tap targets, labels, contrast ($sizeName)', (
        tester,
      ) async {
        final handle = tester.ensureSemantics();
        setViewSize(tester, size);
        await tester.pumpWidget(
          testApp(
            MultiViewDemoPage(initialCount: size == compactSize ? 4 : 10),
          ),
        );
        for (var i = 0; i < 10; i++) {
          await tester.pump(const Duration(milliseconds: 200));
        }
        await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        await tester.pumpWidget(const SizedBox());
        await tester.pump(Duration.zero);
        handle.dispose();
      });

      testWidgets('player: tap targets, labels, contrast ($sizeName)', (
        tester,
      ) async {
        final handle = tester.ensureSemantics();
        setViewSize(tester, size);
        final rig = await PlayerRig.create('normal');
        addTearDown(rig.dispose);
        await tester.pumpWidget(testApp(demoPlayer(rig.session)));
        await rig.advance(tester, const Duration(seconds: 1));
        await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        handle.dispose();
      });

      for (final mode in [VideoKitThemeMode.dark, VideoKitThemeMode.light]) {
        testWidgets('components page: tap targets, labels, contrast '
            '($sizeName, ${mode.name})', (tester) async {
          final handle = tester.ensureSemantics();
          setViewSize(tester, size);
          await tester.pumpWidget(testApp(const ComponentsPage(), mode: mode));
          await tester.pump(const Duration(milliseconds: 100));
          await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
          await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
          await expectLater(tester, meetsGuideline(textContrastGuideline));
          await tester.pumpWidget(const SizedBox());
          await tester.pump(Duration.zero);
          handle.dispose();
        });
      }
    }
  });
}
