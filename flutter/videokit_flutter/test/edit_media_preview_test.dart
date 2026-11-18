// 04A X2: the channel edit project offers VideoKitEditMediaPreview; while
// the native Kit does not answer (not implemented, failure) thumbnails are
// null and waveforms empty, so the editor keeps its plain blocks.
import 'dart:typed_data';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/src/channel_edit_project.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

import 'fake_platform.dart';

/// Native side with timeline media for one source.
class _PreviewHostApi extends FakeHostApi {
  final List<String> asked = [];

  @override
  Future<Uint8List?> sourceThumbnail(
    String projectId,
    String sourceId,
    int atUs,
    int maxWidth,
    int maxHeight,
  ) async {
    asked.add('thumb:$projectId:$sourceId:$atUs:${maxWidth}x$maxHeight');
    return sourceId == 'src-1' ? Uint8List.fromList([0x89, 0x50]) : null;
  }

  @override
  Future<List<double>> sourceWaveform(
    String projectId,
    String sourceId,
    int inUs,
    int outUs,
    int buckets,
  ) async {
    asked.add('wave:$projectId:$sourceId:$inUs-$outUs:$buckets');
    return List.filled(buckets, 0.5);
  }
}

ChannelEditProject _project(VideoKitHostApi api) => ChannelEditProject(
  projectId: 'p-1',
  api: api,
  isDemo: true,
  sessionFor: (_) => throw UnimplementedError('no preview session'),
);

void main() {
  test('the channel project is a media preview and forwards to native', () async {
    final api = _PreviewHostApi();
    final VideoKitEditProject project = _project(api);
    expect(project, isA<VideoKitEditMediaPreview>());
    final preview = project as VideoKitEditMediaPreview;
    expect(await preview.sourceThumbnail('src-1', 500000), [0x89, 0x50]);
    expect(await preview.sourceThumbnail('src-2', 0, maxWidth: 80, maxHeight: 45), isNull);
    expect(await preview.sourceWaveform('src-1', 0, 1000000, 4), [0.5, 0.5, 0.5, 0.5]);
    expect(api.asked, [
      'thumb:p-1:src-1:500000:160x90',
      'thumb:p-1:src-2:0:80x45',
      'wave:p-1:src-1:0-1000000:4',
    ]);
  });

  test('native failures give null thumbnails and empty waveforms', () async {
    // FakeHostApi does not implement the two calls: they throw (like an old native side).
    final VideoKitEditMediaPreview preview = _project(FakeHostApi());
    expect(await preview.sourceThumbnail('src-1', 0), isNull);
    expect(await preview.sourceWaveform('src-1', 0, 1000, 8), isEmpty);
  });
}
