import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_info_rows.dart';
import '../export/export_panel.dart' show vkCodecName;
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';

/// Display name of a container MIME type, e.g. `video/x-matroska` → `MKV`
/// (technical names, not translated).
String vkContainerName(String mime) =>
    switch (mime.split(';').first.trim().toLowerCase()) {
      'video/mp4' => 'MP4',
      'video/x-matroska' => 'MKV',
      'video/webm' => 'WebM',
      'video/quicktime' => 'MOV',
      'video/x-msvideo' => 'AVI',
      'video/3gpp' => '3GP',
      'video/mp2t' => 'TS',
      'video/x-flv' => 'FLV',
      final m => (m.contains('/') ? m.split('/').last : m).toUpperCase(),
    };

/// Player "参数" panel (design page 9): container, video and audio codec,
/// resolution, frame rate, bit rate, rotation, duration and file size from
/// the session's `mediaInfo` (04A P2). Like the image info panel it shows
/// only what is reported: format, video codec, resolution, duration and
/// file size read "未知" when unknown; audio codec, frame rate, bit rate
/// and rotation are left out.
class MediaInfoSheet extends StatelessWidget {
  /// Creates the panel content.
  const MediaInfoSheet({super.key, required this.session});

  /// Session.
  final VideoKitSession session;

  /// Rows as (label, value) pairs, in display order.
  static List<(String, String)> rows(
    VkStrings s,
    VideoKitSessionState st,
    VideoSize? size,
  ) {
    final unknown = s.text('infoUnknown');
    final info = st.mediaInfo;
    final width = info?.width ?? size?.width;
    final height = info?.height ?? size?.height;
    final duration = info?.durationUs ?? st.durationUs;
    final container = info?.container;
    final video = info?.videoCodec;
    final bytes = info?.fileSizeBytes;
    return [
      (
        s.text('infoFormat'),
        container == null ? unknown : vkContainerName(container),
      ),
      (s.text('infoVideoCodec'), video == null ? unknown : vkCodecName(video)),
      if (info?.audioCodec case final audio?)
        (s.text('infoAudioCodec'), vkCodecName(audio)),
      (
        s.text('infoResolution'),
        width == null || height == null || width <= 0
            ? unknown
            : s.infoDimensionsValue(width, height),
      ),
      if (info?.frameRate case final fps? when fps > 0)
        (s.text('infoFrameRate'), VkFormat.frameRate(s, fps)),
      if (info?.bitrateBps case final bps? when bps > 0)
        (s.text('infoBitrate'), VkFormat.bitrate(s, bps)),
      if (info?.rotationDeg case final deg?)
        (s.text('infoRotation'), s.infoRotationValue(deg)),
      (
        s.text('infoDuration'),
        duration == null || duration <= 0
            ? unknown
            : VkFormat.timecode(duration),
      ),
      (
        s.text('infoFileSize'),
        bytes == null ? unknown : VkFormat.fileSize(s, bytes),
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
            builder: (context, st, _) => VkInfoRows(rows: rows(s, st, size)),
          ),
    );
  }
}
