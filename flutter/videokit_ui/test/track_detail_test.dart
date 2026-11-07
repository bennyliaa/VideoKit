// 04A C1: track subtitle = codec name + channel layout.
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

void main() {
  final s = VkStrings.forLocale(const Locale('zh'));

  String? detail(String? codec, int? channels) => vkTrackDetail(
    s,
    TrackInfo(id: 't', codec: codec, channelCount: channels),
  );

  test('layouts: 1 → 单声道, 2 → 2.0, 6 → 5.1, 8 → 7.1, others N 声道', () {
    expect(detail('audio/mp4a-latm', 1), 'AAC 单声道');
    expect(detail('audio/mp4a-latm', 2), 'AAC 2.0');
    expect(detail('audio/vnd.dts', 6), 'DTS 5.1');
    expect(detail('audio/eac3', 8), 'E-AC-3 7.1');
    expect(detail('audio/opus', 4), 'Opus 4 声道');
    expect(detail('audio/opus', 3), 'Opus 3 声道');
  });

  test('unknown channels: codec only; unknown codec: layout only', () {
    expect(detail('audio/mp4a-latm', null), 'AAC');
    expect(detail('audio/mp4a-latm', 0), 'AAC');
    expect(detail(null, 6), '5.1');
    expect(detail(null, null), isNull);
    expect(detail('text/vtt', null), 'WebVTT');
    expect(detail('audio/x-new', 2), 'audio/x-new 2.0', reason: 'raw codec');
  });

  test('pseudo-locale transforms the composed text', () {
    final p = VkStrings.forLocale(VkPseudo.locale);
    final v = vkTrackDetail(
      p,
      const TrackInfo(id: 't', codec: 'audio/mp4a-latm', channelCount: 1),
    );
    expect(v, isNot('AAC 单声道'));
    expect(v, contains('AAC'));
  });
}
