import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_info_rows.dart';
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';

/// Image info panel (design page 13): format, pixel size, file size and
/// orientation, plus frame count, decoded memory and decode sampling when
/// the engine reports `ImageDetails` (04A L2). Shows only what the session
/// and source actually report: the four basic rows read "未知" when
/// unknown, the detail rows are left out.
class ImageInfoSheet extends StatelessWidget {
  /// Creates the panel content.
  const ImageInfoSheet({super.key, required this.session, this.source});

  /// Session (pixel size, kind, orientation).
  final VideoKitSession session;

  /// Bound source (MIME type / extension, known length).
  final VideoKitMediaSource? source;

  /// Upper-case format name from the MIME type or extension, e.g. `GIF`;
  /// [container] (`mediaInfo.container`, 04A P2) is used when the source
  /// does not say.
  static String? formatName(VideoKitMediaSource? source, [String? container]) {
    final mime = source?.mimeType ?? container;
    if (mime != null && mime.contains('/')) {
      final sub = mime.split('/').last.split(';').first.trim();
      if (sub.isNotEmpty) return sub.toUpperCase();
    }
    final ext = source?.extension;
    if (ext != null && ext.isNotEmpty) {
      return (ext.startsWith('.') ? ext.substring(1) : ext).toUpperCase();
    }
    return null;
  }

  /// Rows as (label, value) pairs, in display order.
  static List<(String, String)> rows(
    VkStrings s,
    VideoKitSessionState st,
    VideoSize? size,
    VideoKitMediaSource? source,
  ) {
    final unknown = s.text('infoUnknown');
    final kind = switch (st.mediaKind) {
      MediaKind.imageAnimated => s.text('imageKindAnimated'),
      MediaKind.imageStatic => s.text('imageKindStatic'),
      _ => null,
    };
    final info = st.mediaInfo;
    final format = formatName(source, info?.container);
    final formatValue = format == null
        ? (kind ?? unknown)
        : (kind == null ? format : s.infoFormatValue(format, kind));
    final length = source?.knownLength ?? info?.fileSizeBytes;
    final details = st.imageDetails;
    final width = size?.width ?? info?.width;
    final height = size?.height ?? info?.height;
    final animated = st.mediaKind == MediaKind.imageAnimated;
    return [
      (s.text('infoFormat'), formatValue),
      (
        s.text('infoDimensions'),
        width == null || height == null || width == 0
            ? unknown
            : s.infoDimensionsValue(width, height),
      ),
      (
        s.text('infoFileSize'),
        length == null ? unknown : VkFormat.fileSize(s, length),
      ),
      // J5: the rotation metadata (EXIF orientation), not the shape; left
      // out when the engine does not report it.
      if (info?.rotationDeg case final deg?)
        (
          s.text('infoOrientation'),
          deg % 360 == 0
              ? s.text('orientationNoRotation')
              : s.orientationRotated(deg % 360),
        ),
      // 04A L2: shown only when the engine reports them.
      if (details?.frameCount case final frames?)
        (s.text('infoFrameCount'), s.infoFrameCountValue(frames)),
      // M2: animated images also show what mediaInfo reports.
      if (animated)
        if (info?.frameRate case final fps? when fps > 0)
          (s.text('infoFrameRate'), VkFormat.frameRate(s, fps)),
      if (animated)
        if (info?.durationUs case final us? when us > 0)
          (s.text('infoDuration'), VkFormat.timecode(us)),
      if (details?.decodedBytes case final bytes?)
        (s.text('infoDecodedMemory'), VkFormat.fileSize(s, bytes)),
      if (details?.sampleSize case final sample?)
        (
          s.text('infoSampleSize'),
          sample <= 1
              ? s.text('infoSampleFull')
              : s.infoSampleSizeValue(sample),
        ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final s = VkStrings.of(context);
    return ValueListenableBuilder<VideoSize?>(
      valueListenable: session.videoSize,
      builder: (context, size, _) =>
          ValueListenableBuilder<VideoKitSessionState>(
            valueListenable: session.state,
            builder: (context, st, _) =>
                VkInfoRows(rows: rows(s, st, size, source)),
          ),
    );
  }
}
