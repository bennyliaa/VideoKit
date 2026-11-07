import 'dart:async';

import 'package:flutter/foundation.dart';

/// Bridges [ValueListenable] (Kotlin `StateFlow`) to [Stream] (04 §12.1).
extension ValueListenableStream<T> on ValueListenable<T> {
  /// A broadcast-style single-subscription stream that first emits the
  /// current value and then every subsequent change.
  ///
  /// The listener is removed when the subscription is cancelled.
  Stream<T> asStream() {
    late final StreamController<T> controller;
    void onChange() => controller.add(value);
    controller = StreamController<T>(
      onListen: () {
        controller.add(value);
        addListener(onChange);
      },
      onCancel: () {
        removeListener(onChange);
        return controller.close();
      },
      sync: false,
    );
    return controller.stream;
  }
}
