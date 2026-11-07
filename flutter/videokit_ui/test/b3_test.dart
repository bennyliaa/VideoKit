import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/src/image_viewer/mini_map.dart';
import 'package:videokit_ui/videokit_ui.dart';

Widget _app(Widget child, {VideoKitThemeMode mode = VideoKitThemeMode.dark}) =>
    MaterialApp(
      locale: const Locale('zh'),
      localizationsDelegates: videoKitLocalizationsDelegates,
      supportedLocales: videoKitSupportedLocales,
      home: VideoKitThemeScope(
        mode: mode,
        child: Scaffold(body: child),
      ),
    );

void main() {
  group('VideoKitSlotGrid (14 §5.5)', () {
    test('auto columns: phone 2, tablet 2/3/4 by count; fixed shapes', () {
      const c = VkLayoutClass.compact;
      const e = VkLayoutClass.expanded;
      expect(VideoKitSlotGrid.columnsFor(4, SlotGridLayout.auto, c), 2);
      expect(VideoKitSlotGrid.columnsFor(9, SlotGridLayout.auto, c), 2);
      expect(VideoKitSlotGrid.columnsFor(1, SlotGridLayout.auto, e), 1);
      expect(VideoKitSlotGrid.columnsFor(4, SlotGridLayout.auto, e), 2);
      expect(VideoKitSlotGrid.columnsFor(9, SlotGridLayout.auto, e), 3);
      expect(VideoKitSlotGrid.columnsFor(12, SlotGridLayout.auto, e), 4);
      expect(VideoKitSlotGrid.columnsFor(2, SlotGridLayout.grid3x3, c), 3);
      expect(VideoKitSlotGrid.columnsFor(2, SlotGridLayout.grid3x4, c), 4);
      expect(VideoKitSlotGrid.rowsFor(4, 2, SlotGridLayout.grid2x2), 2);
      expect(VideoKitSlotGrid.rowsFor(12, 4, SlotGridLayout.grid3x4), 3);
      expect(VideoKitSlotGrid.rowsFor(5, 2, SlotGridLayout.auto), 3);
    });

    testWidgets('shows at most 12 slots, no overflow at 2.0 text scale', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(360, 780);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.reset);
      await tester.pumpWidget(
        MediaQuery(
          data: const MediaQueryData(
            size: Size(360, 780),
            textScaler: TextScaler.linear(2),
          ),
          child: _app(
            VideoKitSlotGrid(
              slots: [
                for (var i = 0; i < 14; i++)
                  ColoredBox(key: ValueKey(i), color: const Color(0xFF000000)),
              ],
            ),
          ),
        ),
      );
      expect(
        find.byType(ColoredBox).evaluate().where((e) {
          return e.widget.key is ValueKey<int>;
        }),
        hasLength(12),
      );
      expect(tester.takeException(), isNull);
    });
  });

  group('image viewer helpers (14 §5.3)', () {
    test('mini map visible rect follows zoom and pan', () {
      expect(
        VkMiniMap.visibleRect(MediaTransform.identity),
        const Rect.fromLTWH(0, 0, 1, 1),
      );
      final r = VkMiniMap.visibleRect(const MediaTransform(scale: 2));
      expect(r, const Rect.fromLTWH(0.25, 0.25, 0.5, 0.5));
      final panned = VkMiniMap.visibleRect(
        const MediaTransform(scale: 2, panX: 0.5),
      );
      expect(panned.left, 0, reason: 'panning right shows the left part');
    });

    test('info rows: only what the API reports, unknown otherwise', () {
      final s = VkStrings.forLocale(const Locale('zh'));
      const src = VideoKitMediaSource(
        mediaToken: 't',
        mediaKind: MediaKind.imageAnimated,
        sourceRef: DemoSourceRef('normal'),
        mimeType: 'image/gif',
        knownLength: 4600000,
      );
      final rows = ImageInfoSheet.rows(
        s,
        VideoKitSessionState(
          phase: SessionPhase.ready,
          mediaKind: MediaKind.imageAnimated,
        ),
        const VideoSize(1280, 1152),
        src,
      );
      // J5: no rotation metadata reported → no "方向" row (not the shape).
      expect(rows.map((r) => r.$2), ['GIF（动态）', '1280 × 1152', '4.6 MB']);
      final none = ImageInfoSheet.rows(
        s,
        VideoKitSessionState(phase: SessionPhase.ready),
        null,
        null,
      );
      expect(none.map((r) => r.$2).toSet(), {'未知'});
      expect(ImageInfoSheet.formatName(src), 'GIF');
      // 04A L2: detail rows appear only with values.
      final detailed = ImageInfoSheet.rows(
        s,
        VideoKitSessionState(
          phase: SessionPhase.ready,
          mediaKind: MediaKind.imageAnimated,
          imageDetails: const ImageDetails(
            frameCount: 48,
            decodedBytes: 18000000,
            sampleSize: 2,
          ),
        ),
        const VideoSize(1280, 1152),
        src,
      );
      expect(detailed.skip(3).map((r) => r.$2), ['48 帧', '18 MB', '按 1/2 采样']);
      final partial = ImageInfoSheet.rows(
        s,
        VideoKitSessionState(
          phase: SessionPhase.ready,
          imageDetails: const ImageDetails(sampleSize: 1),
        ),
        null,
        null,
      );
      expect(partial.skip(3).map((r) => r.$2), ['原始分辨率']);
    });
  });

  group('M0-B2 review tokens (14 §7.2)', () {
    testWidgets('badge/pending ring dimensions and slider surface variant', (
      tester,
    ) async {
      late VideoKitThemeData t;
      await tester.pumpWidget(
        _app(
          Builder(
            builder: (context) {
              t = VkTheme.of(context);
              return const SizedBox();
            },
          ),
          mode: VideoKitThemeMode.light,
        ),
      );
      expect(t.dimensions.badgeSize, 16);
      expect(t.dimensions.badgeInset, 4);
      expect(t.dimensions.pendingRingSize, 40);
      expect(t.dimensions.pendingRingStroke, 2);
      final slider = t.components.sliderSurface;
      expect(slider.track, t.colors.borderStrong);
      expect(slider.buffered, t.colors.textTertiary);
      expect(slider.played, t.colors.primary);
      expect(slider.thumb.normal, t.colors.primary);
      for (final bg in [t.colors.surface, t.colors.background]) {
        expect(VkContrast.ratio(slider.track, bg), greaterThanOrEqualTo(3));
      }
      expect(
        VkTokenKeys.byKey('component.slider.surface'),
        VkTokenKeys.sliderSurface,
      );
    });

    testWidgets('icon button: badge in the target corner, ring around icon', (
      tester,
    ) async {
      await tester.pumpWidget(
        _app(
          Center(
            child: VkIconButton(
              icon: Icons.tag,
              semanticLabel: '标签',
              onPressed: () {},
              pending: true,
              badgeText: '3',
            ),
          ),
        ),
      );
      final button = tester.getRect(find.byType(VkIconButton));
      final badge = tester.getRect(find.byType(VkBadge));
      final icon = tester.getRect(find.byIcon(Icons.tag));
      final ring = tester.getRect(find.byType(CircularProgressIndicator));
      expect(badge.top, closeTo(button.top + 4, 0.5));
      expect(badge.right, closeTo(button.right - 4, 0.5));
      expect(badge.height, greaterThanOrEqualTo(16));
      expect(ring.size, const Size(40, 40));
      expect(ring.center, icon.center);
      expect(ring.left, greaterThanOrEqualTo(button.left));
    });
  });
}
