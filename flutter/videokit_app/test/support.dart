import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/app.dart';
import 'package:videokit_app/backend/demo_backend.dart';
import 'package:videokit_app/entitlement/entitlement_service.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/history/history_entry.dart';

/// Phone and tablet sizes.
const Size compactSize = Size(360, 780);

/// Tablet landscape.
const Size expandedSize = Size(1280, 800);

/// Fixed "now" of the tests: 2026-11-07 20:00 local.
final DateTime testNow = DateTime(2026, 11, 7, 20);

/// App under test.
final class AppRig {
  AppRig._(this.backend, this.storage);

  /// Demo backend.
  final DemoBackend backend;

  /// In-memory storage.
  final MemoryAppStorage storage;

  /// Creates a rig, optionally with saved [entries] and [settings].
  static AppRig create({
    List<HistoryEntry> entries = const [],
    Map<String, Object?>? settings,
    DemoBackend? backend,
  }) {
    final storage = MemoryAppStorage();
    if (entries.isNotEmpty) {
      storage.documents['history.json'] = jsonEncode({
        'schema': 1,
        'counter': entries.length,
        'entries': [for (final e in entries) e.toJson()],
      });
    }
    // UI-AUDIT-A1: VK_SCREENS_MODE=light renders the light set.
    final light = Platform.environment['VK_SCREENS_MODE'] == 'light';
    final s = {if (light) 'themeMode': 'light', ...?settings};
    if (s.isNotEmpty) {
      storage.documents['settings.json'] = jsonEncode(s);
    }
    return AppRig._(backend ?? DemoBackend(), storage);
  }

  /// Pumps the app at [size].
  Future<void> pump(
    WidgetTester tester, {
    Size size = compactSize,
    Locale? locale,
    double textScale = 1.0,
    String? fontFamily,
    Widget Function(Widget app)? wrap,
    EntitlementService? entitlements,
  }) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = textScale;
    addTearDown(tester.view.reset);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    final app = VideoKitApp(
      backend: backend,
      storage: storage,
      now: () => testNow,
      locale: locale,
      fontFamily: fontFamily,
      // APP-LIB-A1: a cheap PIN hash keeps library tests fast.
      libraryHashRounds: 4,
      entitlements: entitlements,
    );
    await tester.pumpWidget(wrap == null ? app : wrap(app));
    await settle(tester);
  }

  /// Saved history JSON.
  List<Map<String, Object?>> savedEntries() {
    final raw = storage.documents['history.json'];
    if (raw == null) return const [];
    final json = jsonDecode(raw) as Map<String, Object?>;
    return (json['entries']! as List<Object?>).cast<Map<String, Object?>>();
  }
}

/// Pumps [frames] × 200 ms (Fake clock follows frames).
Future<void> settle(WidgetTester tester, [int frames = 4]) async {
  for (var i = 0; i < frames; i++) {
    await tester.pump(const Duration(milliseconds: 200));
  }
}

/// Unmounts the app and flushes zero timers.
Future<void> unmount(WidgetTester tester) async {
  await tester.pumpWidget(const SizedBox());
  await tester.pump(Duration.zero);
}

/// Taps the last widget showing [text] after scrolling it into view.
Future<void> tapText(WidgetTester tester, String text) async {
  final f = find.text(text).last;
  await tester.ensureVisible(f);
  await tester.pump();
  await tester.tap(f);
}

int _ago(Duration d) => testNow.subtract(d).millisecondsSinceEpoch;

/// The design page 7 history (5 records, one unavailable).
List<HistoryEntry> sampleHistory() => [
  HistoryEntry(
    id: 'h1',
    uri: 'demo:valley',
    displayName: '山谷黄昏.mkv',
    kind: MediaKind.video,
    mimeType: 'video/x-matroska',
    durationUs: 238000000,
    width: 1920,
    height: 1080,
    videoCodec: 'video/avc',
    lastPositionUs: 101000000,
    lastOpenedAtEpochMs: _ago(const Duration(hours: 2)),
  ),
  HistoryEntry(
    id: 'h2',
    uri: 'demo:street',
    displayName: '街头夜景 · 竖屏.mp4',
    kind: MediaKind.video,
    durationUs: 312000000,
    width: 1080,
    height: 1920,
    videoCodec: 'video/hevc',
    lastPositionUs: 84000000,
    lastOpenedAtEpochMs: _ago(const Duration(hours: 22)),
  ),
  HistoryEntry(
    id: 'h3',
    uri: 'demo:dune',
    displayName: '沙丘.heic',
    kind: MediaKind.imageStatic,
    width: 4032,
    height: 3024,
    lastOpenedAtEpochMs: _ago(const Duration(hours: 23)),
  ),
  HistoryEntry(
    id: 'h4',
    uri: 'demo:family',
    displayName: '家庭录像.avi',
    kind: MediaKind.video,
    durationUs: 750000000,
    width: 1280,
    height: 720,
    videoCodec: 'video/mp4v-es',
    lastPositionUs: 495000000,
    lastOpenedAtEpochMs: _ago(const Duration(days: 3)),
  ),
  HistoryEntry(
    id: 'h5',
    uri: 'demo:travel',
    displayName: '旅行合集.mp4',
    kind: MediaKind.video,
    unavailable: true,
    thumbnailPath: '/thumbs/h5.png',
    lastOpenedAtEpochMs: _ago(const Duration(days: 5)),
  ),
];
