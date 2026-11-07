// M3-A1: visibility classification (07 §5.3).
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

void main() {
  const viewport = Rect.fromLTWH(0, 0, 400, 800);
  SessionVisibility at(
    Rect r, {
    bool current = true,
    AppLifecycleState? life = AppLifecycleState.resumed,
  }) => VideoKitVisibilityReporter.classify(
    rect: r,
    viewport: viewport,
    routeCurrent: current,
    lifecycle: life,
  );

  test('inside or partly inside → visible; outside → offscreen', () {
    expect(at(const Rect.fromLTWH(0, 0, 200, 100)), SessionVisibility.visible);
    expect(
      at(const Rect.fromLTWH(0, 760, 200, 100)),
      SessionVisibility.visible,
      reason: 'partly visible has no API value yet → visible',
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
  });

  test('covered by a newer route → offscreen; app paused → background', () {
    const r = Rect.fromLTWH(0, 0, 200, 100);
    expect(at(r, current: false), SessionVisibility.offscreen);
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
}
