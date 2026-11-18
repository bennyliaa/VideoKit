import 'dart:typed_data';

/// Optional timeline media of an edit project (UI-AUDIT-A4, design pages
/// 15/16: thumbnail film and audio waveform on the clip blocks).
///
/// Dart-side addition, a separate interface like `VideoKitAvatarTools`, so
/// projects that do not have it (the plugin before native support) keep
/// compiling; the editor checks `project is VideoKitEditMediaPreview` and
/// otherwise draws plain blocks. The signatures match Kotlin (04A X2:
/// `sourceThumbnail(sourceId, atUs, maxWidth = 160, maxHeight = 90)`,
/// `sourceWaveform(sourceId, inUs, outUs, buckets)`); the native
/// implementation waits on real capabilities (thumbnail decode, audio
/// peaks). Timeline thumbnails are requested every 500 ms of source time
/// for local sources and every 2 s for slow ones (X2, frozen).
abstract interface class VideoKitEditMediaPreview {
  /// An encoded picture (PNG or JPEG) of source [sourceId] at source time
  /// [atUs], at most [maxWidth] × [maxHeight] px; null when the frame cannot
  /// be read (the block keeps its plain look there). Completes within a
  /// bounded time; the editor drops late answers.
  Future<Uint8List?> sourceThumbnail(
    String sourceId,
    int atUs, {
    int maxWidth = 160,
    int maxHeight = 90,
  });

  /// [buckets] audio peaks (0–1) of source [sourceId] over source time
  /// [inUs]–[outUs]; all zero for silence, empty when the source has no
  /// audio track.
  Future<List<double>> sourceWaveform(
    String sourceId,
    int inUs,
    int outUs,
    int buckets,
  );
}
