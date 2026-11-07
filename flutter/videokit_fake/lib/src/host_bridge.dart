import 'dart:async';

import 'package:videokit_api/videokit_api.dart';

import 'clock/fake_clock.dart';

/// Calls host callbacks with clock-based timeouts and full failure
/// isolation (04 §8): a throwing or hanging host never affects the session.
final class FakeHostBridge {
  /// Creates a bridge.
  FakeHostBridge({
    required this.callbacks,
    required this.timeouts,
    required this.clock,
  });

  /// Host callbacks.
  final VideoKitHostCallbacks callbacks;

  /// Timeouts.
  final HostCallbackTimeouts timeouts;

  /// Clock used for timeouts.
  final FakeClock clock;

  /// Number of failed or timed-out callback invocations (diagnostics/tests).
  int failureCount = 0;

  /// Calls [call]; completes with null on exception or after [timeout].
  Future<T?> guarded<T>(Future<T> Function() call, Duration timeout) {
    final completer = Completer<T?>();
    final task = clock.schedule(timeout, () {
      if (!completer.isCompleted) {
        failureCount++;
        completer.complete(null);
      }
    });
    void fail() {
      if (!completer.isCompleted) {
        task.cancel();
        failureCount++;
        completer.complete(null);
      }
    }

    try {
      call().then((value) {
        if (!completer.isCompleted) {
          task.cancel();
          completer.complete(value);
        }
      }, onError: (Object _, StackTrace _) => fail());
    } catch (_) {
      fail();
    }
    return completer.future;
  }

  /// Fire-and-forget notification with the notification timeout.
  void notify(Future<void> Function(VideoKitHostCallbacks c) call) {
    unawaited(guarded(() => call(callbacks), timeouts.notification));
  }

  /// `HOST_CALLBACK_FAILED` error.
  static const VideoKitStableError callbackFailed = VideoKitStableError(
    code: ErrorCode.hostCallbackFailed,
    stage: ErrorStage.callback,
    retryable: true,
    suggestedAction: SuggestedAction.retry,
  );
}
