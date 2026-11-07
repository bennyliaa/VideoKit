// M1-A1 item 4: player "参数" panel rows from `mediaInfo` (design page 9).
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

void main() {
  final s = VkStrings.forLocale(const Locale('zh'));

  test('all reported items, in design order', () {
    final rows = MediaInfoSheet.rows(
      s,
      VideoKitSessionState(
        phase: SessionPhase.ready,
        mediaKind: MediaKind.video,
        mediaInfo: const MediaInfo(
          container: 'video/x-matroska',
          videoCodec: 'video/hevc',
          audioCodec: 'audio/eac3',
          width: 3840,
          height: 2160,
          frameRate: 29.97,
          bitrateBps: 45200000,
          rotationDeg: 90,
          durationUs: 3725000000,
          fileSizeBytes: 21000000000,
        ),
      ),
      null,
    );
    expect(rows, [
      ('格式', 'MKV'),
      ('视频编码', 'HEVC'),
      ('音频编码', 'E-AC-3'),
      ('分辨率', '3840 × 2160'),
      ('帧率', '29.97 fps'),
      ('码率', '45.2 Mbps'),
      ('旋转', '90°'),
      ('时长', '1:02:05'),
      ('文件大小', '21 GB'),
    ]);
  });

  test('nothing reported: basic rows 未知, the others left out', () {
    final rows = MediaInfoSheet.rows(
      s,
      VideoKitSessionState(
        phase: SessionPhase.binding,
        mediaKind: MediaKind.video,
      ),
      null,
    );
    expect(rows, [
      ('格式', '未知'),
      ('视频编码', '未知'),
      ('分辨率', '未知'),
      ('时长', '未知'),
      ('文件大小', '未知'),
    ]);
  });

  test('falls back to video size and session duration', () {
    final rows = MediaInfoSheet.rows(
      s,
      VideoKitSessionState(
        phase: SessionPhase.ready,
        mediaKind: MediaKind.video,
        durationUs: 65000000,
        mediaInfo: const MediaInfo(bitrateBps: 850000),
      ),
      const VideoSize(1280, 720),
    );
    expect(rows.map((r) => r.$2), [
      '未知',
      '未知',
      '1280 × 720',
      '850 kbps',
      '01:05',
      '未知',
    ]);
  });

  test('container and codec names', () {
    expect(vkContainerName('video/mp4'), 'MP4');
    expect(vkContainerName('video/quicktime'), 'MOV');
    expect(vkContainerName('video/x-msvideo'), 'AVI');
    expect(vkContainerName('video/unknown-thing'), 'UNKNOWN-THING');
    expect(vkCodecName('video/avc'), 'H.264');
    expect(vkCodecName('video/mp4v-es'), 'MPEG-4');
    expect(vkCodecName('audio/mpeg'), 'MP3');
  });

  test('pseudo-locale transforms labels and values', () {
    final p = VkStrings.forLocale(VkPseudo.locale);
    final rows = MediaInfoSheet.rows(
      p,
      VideoKitSessionState(
        phase: SessionPhase.ready,
        mediaKind: MediaKind.video,
        mediaInfo: const MediaInfo(frameRate: 30),
      ),
      null,
    );
    expect(rows.first.$1, isNot('格式'));
  });
}
