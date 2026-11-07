// Visibility classification (07 §5.3; 04A V1 PARTIALLY_VISIBLE, V2 opaque
// routes only).
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

void main() {
  const viewport = Rect.fromLTWH(0, 0, 400, 800);
  SessionVisibility at(
    Rect r, {
    bool occluded = false,
    AppLifecycleState? life = AppLifecycleState.resumed,
  }) => VideoKitVisibilityReporter.classify(
    rect: r,
    viewport: viewport,
    occluded: occluded,
    lifecycle: life,
  );

  test(
    'fully inside → visible; partly → partiallyVisible; out → offscreen',
    () {
      expect(
        at(const Rect.fromLTWH(0, 0, 200, 100)),
        SessionVisibility.visible,
      );
      expect(
        at(const Rect.fromLTWH(0, 710, 200, 100)),
        SessionVisibility.partiallyVisible,
      );
      expect(
        at(const Rect.fromLTWH(0, 700.2, 200, 99.9)),
        SessionVisibility.visible,
        reason: 'sub-pixel slack at the edge',
      );
      expect(
        at(const Rect.fromLTWH(-50, 0, 200, 100)),
        SessionVisibility.partiallyVisible,
      );
      expect(
        at(const Rect.fromLTWH(0, 900, 200, 100)),
        SessionVisibility.offscreen,
      );
      expect(
        at(const Rect.fromLTWH(0, 800, 200, 100)),
        SessionVisibility.offscreen,
        reason: 'touching the edge is not visible',
      );
    },
  );

  test('opaque route on top → offscreen; app paused → background', () {
    const r = Rect.fromLTWH(0, 0, 200, 100);
    expect(at(r, occluded: true), SessionVisibility.offscreen);
    for (final s in [
      AppLifecycleState.paused,
      AppLifecycleState.hidden,
      AppLifecycleState.detached,
    ]) {
      expect(at(r, life: s), SessionVisibility.background, reason: s.name);
    }
    expect(
      at(r, life: AppLifecycleState.inactive),
      SessionVisibility.visible,
      reason: 'inactive (e.g. notification shade) keeps playing',
    );
    expect(at(r, life: null), SessionVisibility.visible);
  });

  test('wire name and on-screen helper', () {
    expect(SessionVisibility.partiallyVisible.wireName, 'PARTIALLY_VISIBLE');
    expect(
      SessionVisibility.fromName('PARTIALLY_VISIBLE'),
      SessionVisibility.partiallyVisible,
    );
    expect(SessionVisibility.partiallyVisible.isOnScreen, isTrue);
    expect(SessionVisibility.offscreen.isOnScreen, isFalse);
  });
}
