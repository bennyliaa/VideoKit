import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../theme/theme_scope.dart';

/// Preview frames while the seek bar is dragged (M1-A1, design page 9):
/// `captureThumbnail` at the drag position, at most one request every
/// [interval] (≥ 100 ms) and never two at once; the latest position wins.
/// [cancel] (release) drops pending and in-flight results and clears the
/// frame. Failed captures keep the previous frame (no error UI: the time
/// bubble still shows the position).
class SeekPreviewFrames extends ValueNotifier<ThumbnailCaptured?> {
  /// Creates the fetcher; [capture] is usually `session.captureThumbnail`.
  SeekPreviewFrames({required this.capture, this.interval = minInterval})
    : assert(interval >= minInterval, 'throttle must be ≥ 100 ms'),
      super(null);

  /// Smallest allowed request spacing.
  static const Duration minInterval = Duration(milliseconds: 100);

  /// Captures a frame at a position (µs).
  final Future<ThumbnailResult> Function(int atUs) capture;

  /// Spacing between request starts.
  final Duration interval;

  int? _pendingUs;
  bool _inFlight = false;

  /// Runs for [interval] after each request start.
  Timer? _cooldown;
  int _generation = 0;
  bool _disposed = false;

  /// Requests issued so far (tests, diagnostics).
  int requests = 0;

  /// Drag moved to [us].
  void request(int us) {
    if (_disposed) return;
    _pendingUs = us;
    _pump();
  }

  /// Drag released or cancelled.
  void cancel() {
    _generation++;
    _cooldown?.cancel();
    _cooldown = null;
    _pendingUs = null;
    _inFlight = false;
    if (!_disposed) value = null;
  }

  void _pump() {
    if (_inFlight || _cooldown != null || _pendingUs == null) return;
    _fire();
  }

  void _fire() {
    final us = _pendingUs!;
    _pendingUs = null;
    _inFlight = true;
    _cooldown = Timer(interval, () {
      _cooldown = null;
      _pump();
    });
    requests++;
    final gen = _generation;
    unawaited(
      capture(us)
          .then<void>((r) {
            if (gen != _generation || _disposed) return;
            if (r is ThumbnailCaptured) value = r;
          }, onError: (Object _) {})
          .whenComplete(() {
            if (gen != _generation || _disposed) return;
            _inFlight = false;
            _pump();
          }),
    );
  }

  @override
  void dispose() {
    cancel();
    _disposed = true;
    super.dispose();
  }
}

/// The current preview frame above the seek bar's time bubble; nothing
/// until the first frame arrives. 16:9 box, frame letterboxed inside.
class VkSeekPreviewFrame extends StatelessWidget {
  /// Creates the frame view.
  const VkSeekPreviewFrame({super.key, required this.frames});

  /// Frames.
  final SeekPreviewFrames frames;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final bubble = t.components.seekBar.bubble;
    final width = d.targetMin * 3;
    return ValueListenableBuilder<ThumbnailCaptured?>(
      valueListenable: frames,
      builder: (context, frame, _) => frame == null
          ? const SizedBox.shrink()
          : DecoratedBox(
              key: const ValueKey('vk-seek-preview-frame'),
              decoration: bubble.decoration,
              child: Padding(
                padding: EdgeInsetsDirectional.all(d.spacing4),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(d.spacing4),
                  child: ColoredBox(
                    color: t.colors.playerCanvas,
                    child: SizedBox(
                      width: width,
                      height: width * 9 / 16,
                      child: Image.memory(
                        frame.bytes,
                        fit: BoxFit.contain,
                        gaplessPlayback: true,
                        excludeFromSemantics: true,
                        // Undecodable bytes: no frame, the time bubble remains.
                        errorBuilder: (_, _, _) => const SizedBox.shrink(),
                      ),
                    ),
                  ),
                ),
              ),
            ),
    );
  }
}
