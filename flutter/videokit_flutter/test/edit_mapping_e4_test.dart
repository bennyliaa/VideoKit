// 04A E4 (M4-B2): the edit state from the channel matches the Kotlin model:
// an unprobed source has no probe, an unknown codec is null (not ''), and
// accepted ranges belong to the mask.
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/src/msg_mapping.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

EditStateMsg _state({
  required List<EditSourceMsg> sources,
  List<MaskTrackMsg> masks = const [],
  List<TrackingRunMsg> tracking = const [],
}) => EditStateMsg(
  phase: EditPhaseMsg.ready,
  revision: 3,
  sources: sources,
  clips: [],
  masks: masks,
  tracking: tracking,
  canUndo: false,
  canRedo: false,
  estimateDurationUs: 0,
);

void main() {
  test('an unprobed source maps to a null probe, not zeros', () {
    final state = editStateFromMsg(
      _state(
        sources: [
          EditSourceMsg(sourceId: 'src-1', mediaToken: 'm', mismatch: false),
        ],
      ),
    );
    expect(state.timeline.sources.single.probe, isNull);
  });

  test('unknown codecs map to null, known ones are kept', () {
    final state = editStateFromMsg(
      _state(
        sources: [
          EditSourceMsg(
            sourceId: 'src-1',
            mediaToken: 'm',
            mismatch: false,
            probe: SourceProbeMsg(
              durationUs: 5000000,
              width: 1280,
              height: 720,
              rotationDeg: 90,
              frameRate: 30,
              hasAudio: false,
            ),
          ),
          EditSourceMsg(
            sourceId: 'src-2',
            mediaToken: 'n',
            mismatch: true,
            probe: SourceProbeMsg(
              durationUs: 1,
              width: 2,
              height: 3,
              rotationDeg: 0,
              videoCodec: 'video/avc',
              audioCodec: '',
              hasAudio: true,
            ),
          ),
        ],
      ),
    );
    final first = state.timeline.sources[0].probe!;
    expect(first.videoCodec, isNull);
    expect(first.audioCodec, isNull);
    expect(first.durationUs, 5000000);
    expect(first.rotationDeg, 90);
    expect(first.fps, 30);
    final second = state.timeline.sources[1].probe!;
    expect(second.videoCodec, 'video/avc');
    expect(second.audioCodec, isNull);
    expect(second.hasAudio, isTrue);
    expect(state.timeline.sources[1].mismatch, isTrue);
  });

  test('accepted ranges belong to the mask; coverage flags follow them', () {
    final state = editStateFromMsg(
      _state(
        sources: [],
        masks: [
          MaskTrackMsg(
            maskId: 'mask-1',
            type: 'FACE',
            style: 'MOSAIC',
            strength: 0.5,
            enabled: true,
            range: TimeRangeMsg(startUs: 0, endUs: 2000000),
            keyframes: [],
            acceptedRanges: [TimeRangeMsg(startUs: 500000, endUs: 1000000)],
          ),
        ],
        tracking: [
          TrackingRunMsg(
            maskId: 'mask-1',
            status: 'COMPLETED',
            coverage: [
              CoverageRangeMsg(
                range: TimeRangeMsg(startUs: 0, endUs: 500000),
                quality: 'TRACKED',
              ),
              CoverageRangeMsg(
                range: TimeRangeMsg(startUs: 500000, endUs: 1000000),
                quality: 'LOST',
              ),
            ],
          ),
        ],
      ),
    );
    final mask = state.masks.single;
    expect(mask.acceptedRanges, [const TimeRangeUs(500000, 1000000)]);
    final segments = state.tracking['mask-1']!.coverage.segments;
    expect(segments.map((s) => s.accepted), [false, true]);
  });
}
