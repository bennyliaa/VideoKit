import 'dart:async';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_fake/videokit_fake.dart';

void main() {
  test('advance runs tasks in order and ticks in ≤ 250 ms steps', () async {
    final clock = FakeClock();
    final log = <String>[];
    final deltas = <Duration>[];
    clock.addTickListener(deltas.add);
    clock.schedule(const Duration(milliseconds: 600), () => log.add('b'));
    clock.schedule(const Duration(milliseconds: 100), () => log.add('a'));
    final cancelled = clock.schedule(
      const Duration(milliseconds: 300),
      () => log.add('x'),
    );
    cancelled.cancel();
    await clock.advance(const Duration(seconds: 1));
    expect(log, ['a', 'b']);
    expect(clock.now, const Duration(seconds: 1));
    expect(deltas.every((d) => d <= const Duration(milliseconds: 250)), isTrue);
    expect(deltas.fold(Duration.zero, (a, b) => a + b), clock.now);
    expect(clock.pendingTaskCount, 0);
  });

  test('delay completes only when clock time passes', () async {
    final clock = FakeClock();
    var done = false;
    unawaited(clock.delay(const Duration(seconds: 2)).then((_) => done = true));
    await clock.advance(const Duration(seconds: 1));
    expect(done, isFalse);
    await clock.advance(const Duration(seconds: 1));
    expect(done, isTrue);
  });

  test('advanceSync and dispose', () {
    final clock = FakeClock();
    var ran = 0;
    clock.schedule(const Duration(milliseconds: 10), () => ran++);
    clock.advanceSync(const Duration(milliseconds: 20));
    expect(ran, 1);
    clock.schedule(const Duration(milliseconds: 10), () => ran++);
    clock.dispose();
    clock.advanceSync(const Duration(milliseconds: 20));
    expect(ran, 1);
  });

  testWidgets('ticker mode follows frames scaled by speed and pauses', (
    tester,
  ) async {
    final clock = FakeClock()..speed = 2;
    clock.attachTicker(tester);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));
    expect(clock.now, const Duration(milliseconds: 200));
    clock.pause();
    await tester.pump(const Duration(milliseconds: 100));
    expect(clock.now, const Duration(milliseconds: 200));
    clock.resume();
    await tester.pump(const Duration(milliseconds: 100));
    expect(clock.now, const Duration(milliseconds: 400));
    clock.dispose();
  });
}
