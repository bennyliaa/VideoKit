import 'dart:async';

import 'package:flutter/scheduler.dart';

/// Handle of a task scheduled on a [FakeClock].
final class FakeClockTask {
  FakeClockTask._(this.dueAt, this._callback, this._seq);

  /// Clock time at which the task runs.
  final Duration dueAt;
  final VoidCallback _callback;
  final int _seq;
  bool _cancelled = false;
  bool _done = false;

  /// Whether the task is still waiting.
  bool get isPending => !_cancelled && !_done;

  /// Cancels the task; no-op if already run.
  void cancel() => _cancelled = true;
}

/// Controllable clock driving every Fake (14 §11.1).
///
/// * Tests call [advance] (async: flushes microtasks between steps, works
///   under `fakeAsync`/`testWidgets` and plain `test`).
/// * The example app calls [attachTicker] so the clock follows real frames,
///   scaled by [speed] and stoppable with [pause]/[resume].
///
/// Time advances in steps of at most [tickStep] (4 Hz = the native snapshot
/// sampling rate, 14 §12) so tick listeners see realistic increments and
/// scheduled tasks fire in order.
class FakeClock {
  /// Creates a clock at time zero.
  FakeClock({this.tickStep = const Duration(milliseconds: 250)});

  /// Maximum step per tick.
  final Duration tickStep;

  Duration _now = Duration.zero;
  final List<FakeClockTask> _tasks = [];
  final List<void Function(Duration delta)> _tickListeners = [];
  int _seq = 0;
  Ticker? _ticker;
  Duration _lastElapsed = Duration.zero;
  bool _paused = false;

  /// Wall-clock multiplier in ticker mode (e.g. 10 for ×10).
  double speed = 1.0;

  /// Current clock time.
  Duration get now => _now;

  /// Whether ticker-driven time is paused.
  bool get isPaused => _paused;

  /// Number of tasks still pending.
  int get pendingTaskCount => _tasks.where((t) => t.isPending).length;

  /// Registers [listener] called with the elapsed delta on every step.
  void addTickListener(void Function(Duration delta) listener) =>
      _tickListeners.add(listener);

  /// Removes a tick listener.
  void removeTickListener(void Function(Duration delta) listener) =>
      _tickListeners.remove(listener);

  /// Runs [callback] after [delay] of clock time.
  FakeClockTask schedule(Duration delay, VoidCallback callback) {
    final task = FakeClockTask._(
      _now + (delay.isNegative ? Duration.zero : delay),
      callback,
      _seq++,
    );
    _tasks.add(task);
    return task;
  }

  /// Completes after [delay] of clock time.
  Future<void> delay(Duration delay) {
    final completer = Completer<void>();
    schedule(delay, completer.complete);
    return completer.future;
  }

  /// Advances by [duration], flushing microtasks after each step so awaited
  /// futures resolve in order.
  Future<void> advance(Duration duration) async {
    final target = _now + duration;
    do {
      _step(target);
      await Future<void>.delayed(Duration.zero);
    } while (_now < target);
    // Run tasks scheduled for exactly `target` by the last flush.
    _runDue();
    await Future<void>.delayed(Duration.zero);
  }

  /// Advances synchronously (ticker mode); futures resolve afterwards.
  void advanceSync(Duration duration) {
    final target = _now + duration;
    do {
      _step(target);
    } while (_now < target);
  }

  /// Lets awaited futures settle without moving time.
  Future<void> flush() async {
    _runDue();
    await Future<void>.delayed(Duration.zero);
  }

  void _step(Duration target) {
    var next = _now + tickStep;
    if (next > target) next = target;
    for (final t in _tasks) {
      if (t.isPending && t.dueAt < next && t.dueAt >= _now) next = t.dueAt;
    }
    final delta = next - _now;
    _now = next;
    if (delta > Duration.zero) {
      for (final l in List.of(_tickListeners)) {
        l(delta);
      }
    }
    _runDue();
  }

  void _runDue() {
    while (true) {
      final due = _tasks.where((t) => t.isPending && t.dueAt <= _now).toList()
        ..sort((a, b) {
          final c = a.dueAt.compareTo(b.dueAt);
          return c != 0 ? c : a._seq.compareTo(b._seq);
        });
      if (due.isEmpty) break;
      for (final t in due) {
        if (!t.isPending) continue;
        t._done = true;
        t._callback();
      }
    }
    _tasks.removeWhere((t) => !t.isPending);
  }

  /// Follows real frames from [vsync] (example app).
  void attachTicker(TickerProvider vsync) {
    detachTicker();
    _lastElapsed = Duration.zero;
    _ticker = vsync.createTicker((elapsed) {
      final delta = elapsed - _lastElapsed;
      _lastElapsed = elapsed;
      if (_paused || delta <= Duration.zero) return;
      advanceSync(delta * speed);
    })..start();
  }

  /// Stops following frames.
  void detachTicker() {
    _ticker?.dispose();
    _ticker = null;
  }

  /// Pauses ticker-driven time ([advance] still works).
  void pause() => _paused = true;

  /// Resumes ticker-driven time.
  void resume() => _paused = false;

  /// Cancels all tasks and listeners and detaches the ticker.
  void dispose() {
    detachTicker();
    for (final t in _tasks) {
      t.cancel();
    }
    _tasks.clear();
    _tickListeners.clear();
  }
}
