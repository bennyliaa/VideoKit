// M1-A1 item 3: throttled seek-drag preview frames.
import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/src/player/seek_preview.dart';

final class _Capture {
  final List<int> positions = [];
  final List<Completer<ThumbnailResult>> pending = [];

  Future<ThumbnailResult> call(int us) {
    positions.add(us);
    final c = Completer<ThumbnailResult>();
    pending.add(c);
    return c.future;
  }

  void completeLast([ThumbnailResult? r]) =>
      pending.last.complete(r ?? frame(positions.last));
}

ThumbnailCaptured frame(int us) => ThumbnailCaptured(
  bytes: Uint8List.fromList([us % 256]),
  width: 16,
  height: 9,
);

void main() {
  testWidgets('≥ 100 ms between requests, latest position wins', (
    tester,
  ) async {
    final cap = _Capture();
    final f = SeekPreviewFrames(capture: cap.call);
    f.request(1);
    expect(cap.positions, [1]);
    cap.completeLast();
    await tester.pump();
    expect(f.value!.bytes.single, 1);
    for (var i = 2; i <= 9; i++) {
      await tester.pump(const Duration(milliseconds: 10));
      f.request(i);
    }
    expect(cap.positions, [1], reason: 'inside the 100 ms window');
    await tester.pump(const Duration(milliseconds: 20));
    expect(cap.positions, [1, 9], reason: 'one request for the latest');
    cap.completeLast();
    await tester.pump();
    expect(f.value!.bytes.single, 9);
    // Idle: nothing more is requested.
    await tester.pump(const Duration(milliseconds: 500));
    expect(cap.positions, [1, 9]);
    f.dispose();
  });

  testWidgets('never two requests at once', (tester) async {
    final cap = _Capture();
    final f = SeekPreviewFrames(capture: cap.call);
    f.request(1);
    await tester.pump(const Duration(milliseconds: 150));
    f.request(2);
    await tester.pump(const Duration(milliseconds: 300));
    expect(cap.positions, [1], reason: 'first still in flight');
    cap.completeLast();
    await tester.pump();
    expect(cap.positions, [1, 2]);
    cap.completeLast();
    await tester.pump();
    expect(f.value!.bytes.single, 2);
    f.dispose();
  });

  testWidgets('release cancels: late result dropped, frame cleared', (
    tester,
  ) async {
    final cap = _Capture();
    final f = SeekPreviewFrames(capture: cap.call);
    f.request(1);
    cap.completeLast();
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    f.request(2);
    expect(cap.positions, [1, 2]);
    f.request(3);
    f.cancel();
    expect(f.value, isNull);
    cap.completeLast();
    await tester.pump(const Duration(milliseconds: 300));
    expect(f.value, isNull, reason: 'in-flight result after release');
    expect(cap.positions, [1, 2], reason: 'pending position dropped');
    // A new drag starts fresh.
    f.request(4);
    expect(cap.positions, [1, 2, 4]);
    f.dispose();
  });

  testWidgets('failed or throwing capture keeps the previous frame', (
    tester,
  ) async {
    final cap = _Capture();
    final f = SeekPreviewFrames(capture: cap.call);
    f.request(1);
    cap.completeLast();
    await tester.pump(const Duration(milliseconds: 100));
    f.request(2);
    cap.completeLast(const ThumbnailFailed(VideoKitStableError.internal()));
    await tester.pump(const Duration(milliseconds: 100));
    expect(f.value!.bytes.single, 1);
    f.request(3);
    cap.pending.last.completeError(StateError('channel'));
    await tester.pump(const Duration(milliseconds: 100));
    expect(f.value!.bytes.single, 1);
    f.request(4);
    expect(cap.positions, [1, 2, 3, 4], reason: 'errors do not stall');
    f.dispose();
  });

  testWidgets('VkSeekPreviewFrame shows nothing until a frame arrives', (
    tester,
  ) async {
    final f = SeekPreviewFrames(
      capture: (_) async =>
          ThumbnailCaptured(bytes: _png1x1, width: 1, height: 1),
    );
    await tester.pumpWidget(
      Directionality(
        textDirection: TextDirection.ltr,
        child: VkSeekPreviewFrame(frames: f),
      ),
    );
    expect(find.byKey(const ValueKey('vk-seek-preview-frame')), findsNothing);
    f.request(0);
    await tester.pump();
    await tester.pump();
    expect(find.byKey(const ValueKey('vk-seek-preview-frame')), findsOneWidget);
    f.cancel();
    await tester.pump();
    expect(find.byKey(const ValueKey('vk-seek-preview-frame')), findsNothing);
    await tester.pumpWidget(const SizedBox());
    f.dispose();
  });
}

/// A valid 1×1 PNG.
final Uint8List _png1x1 = Uint8List.fromList(const [
  0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D, //
  0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
  0x0D, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
  0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
  0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82,
]);
