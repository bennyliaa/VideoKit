// 04A E5/E6 (M4-B2): avatars on the channel. SetMaskAvatar carries the
// avatar; masks carry it back with style IMAGE; keyframes carry rollDeg;
// IMAGE without an avatar reads as MOSAIC (schema R7), as on the native side.
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter/src/msg_mapping.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

MaskTrackMsg _mask(String id, String style, {MaskAvatarMsg? avatar}) =>
    MaskTrackMsg(
      maskId: id,
      type: 'FACE',
      style: style,
      strength: 0.5,
      enabled: true,
      range: TimeRangeMsg(startUs: 0, endUs: 1000000),
      keyframes: [
        MaskKeyframeMsg(
          atUs: 0,
          region: MaskRegionMsg(
            x: 0.4,
            y: 0.3,
            width: 0.2,
            height: 0.25,
            rotationDeg: 0,
          ),
          source: 'TRACKER',
          quality: 'TRACKED',
          rollDeg: -12.5,
        ),
      ],
      acceptedRanges: [],
      avatar: avatar,
    );

VideoKitEditState _state(List<MaskTrackMsg> masks) => editStateFromMsg(
  EditStateMsg(
    phase: EditPhaseMsg.ready,
    revision: 1,
    sources: [],
    clips: [],
    masks: masks,
    tracking: [],
    canUndo: false,
    canRedo: false,
    estimateDurationUs: 0,
  ),
);

void main() {
  test('SetMaskAvatar carries the whole avatar', () {
    final msg = editCommandToMsg(
      const SetMaskAvatar(
        'mask-1',
        MaskAvatar(
          avatarToken: 'host:a-1',
          scale: 1.25,
          offsetX: 0.05,
          offsetY: -0.1,
          followRotation: false,
        ),
      ),
    );
    expect(msg.kind, 'SetMaskAvatar');
    expect(msg.maskId, 'mask-1');
    expect(msg.avatar!.avatarToken, 'host:a-1');
    expect(msg.avatar!.scale, 1.25);
    expect(msg.avatar!.offsetX, 0.05);
    expect(msg.avatar!.offsetY, -0.1);
    expect(msg.avatar!.followRotation, isFalse);
  });

  test('a mask with style IMAGE comes back with its avatar and roll', () {
    final mask = _state([
      _mask(
        'mask-1',
        'IMAGE',
        avatar: MaskAvatarMsg(
          avatarToken: 'builtin:3',
          scale: 1.5,
          offsetX: 0,
          offsetY: 0,
          followRotation: true,
        ),
      ),
    ]).masks.single;
    expect(mask.style, MaskStyle.image);
    expect(mask.avatar!.avatarToken, 'builtin:3');
    expect(mask.avatar!.scale, 1.5);
    expect(mask.keyframes.single.rollDeg, -12.5);
  });

  test('IMAGE without an avatar reads as MOSAIC (schema R7)', () {
    final mask = _state([_mask('mask-1', 'IMAGE')]).masks.single;
    expect(mask.style, MaskStyle.mosaic);
    expect(mask.avatar, isNull);
  });
}
