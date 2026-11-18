// M5A-A1 (REQ-ED-07, 04A E5/E6): Fake avatar tools, IMAGE masks and the
// snapshot 1.1 fields.
import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

VideoKitMediaSource _photo([String scenario = 'normal']) => VideoKitMediaSource(
  mediaToken: 'photo-$scenario',
  mediaKind: MediaKind.imageStatic,
  sourceRef: DemoSourceRef(scenario),
);

Future<T> _drive<T>(FakeVideoKit kit, Future<T> f) async {
  T? v;
  Object? error;
  var done = false;
  unawaited(
    f.then(
      (x) {
        v = x;
        done = true;
      },
      onError: (Object e) {
        error = e;
        done = true;
      },
    ),
  );
  for (var i = 0; !done && i < 100; i++) {
    await kit.clock.advance(const Duration(milliseconds: 100));
  }
  expect(done, isTrue, reason: 'did not complete');
  if (error != null) throw error!;
  return v as T;
}

int _alphaAt(AvatarImage a, double x, double y) {
  final rgba = FakeAvatarTools.decodePng(a.png, a.width, a.height)!;
  final px = (x * a.width).floor();
  final py = (y * a.height).floor();
  return rgba[(py * a.width + px) * 4 + 3];
}

void main() {
  group('avatar tools', () {
    test('the Fake reports avatar support and is VideoKitAvatarTools', () async {
      final kit = FakeVideoKit();
      expect(kit, isA<VideoKitAvatarTools>());
      final caps = await kit.capabilities(CapabilityRequest.device);
      expect(caps.avatar, AvatarSupport.available);
      expect(
        (await FakeVideoKit(editingAvailable: false).capabilities(
          CapabilityRequest.device,
        )).avatar,
        AvatarSupport.unsupported,
      );
    });

    test('prepareAvatar returns a transparent PNG with a head box', () async {
      final kit = FakeVideoKit();
      final a = await _drive(kit, kit.prepareAvatar(_photo()));
      expect(a.isDemo, isTrue);
      expect((a.width, a.height), (FakeAvatarTools.size, FakeAvatarTools.size));
      expect(a.png.sublist(1, 4), 'PNG'.codeUnits);
      expect(_alphaAt(a, 0.01, 0.99), 0, reason: 'corner is transparent');
      expect(_alphaAt(a, 0.5, 0.55), 255, reason: 'face is opaque');
      expect(a.headBox.width, greaterThan(0));
      expect(a.sourceFaceBox, isNotNull);
      expect(a.warnings, isEmpty);
    });

    test('scenarios: no face, unsupported, several faces, slow', () async {
      final kit = FakeVideoKit();
      for (final (scenario, code) in [
        (FakeAvatarTools.noFace, 'AVATAR_NO_FACE'),
        (FakeAvatarTools.unsupportedImage, 'AVATAR_IMAGE_UNSUPPORTED'),
      ]) {
        await expectLater(
          _drive(kit, kit.prepareAvatar(_photo(scenario))),
          throwsA(
            isA<VideoKitException>().having(
              (e) =>
                  e.error.code.wireName == code || e.error.diagnostic == code,
              'avatar error',
              isTrue,
            ),
          ),
        );
      }
      final many = await _drive(
        kit,
        kit.prepareAvatar(_photo(FakeAvatarTools.multipleFaces)),
      );
      expect(many.warnings, [AvatarImage.multipleFaces]);
      final slow = kit.prepareAvatar(_photo(FakeAvatarTools.slow));
      var done = false;
      unawaited(slow.then((_) => done = true));
      await kit.clock.advance(const Duration(seconds: 2));
      expect(done, isFalse, reason: 'still working after 2 s');
      await kit.clock.advance(const Duration(seconds: 2));
      expect(done, isTrue);
    });

    test('cropToHead off keeps the shoulders; feather is reported', () async {
      final kit = FakeVideoKit();
      final a = await _drive(
        kit,
        kit.prepareAvatar(
          _photo(),
          options: const AvatarPrepareOptions(cropToHead: false, feather: 0.2),
        ),
      );
      expect(a.cropToHead, isFalse);
      expect(a.feather, 0.2);
      expect(a.headBox, FakeAvatarTools.headBox(withShoulders: true));
    });

    test('refineAvatar erases and restores along a stroke', () async {
      final kit = FakeVideoKit();
      final a = await _drive(kit, kit.prepareAvatar(_photo()));
      final erased = await _drive(
        kit,
        kit.refineAvatar(a, [
          AvatarStroke(
            brush: AvatarBrush.erase,
            points: const [(0.5, 0.55)],
            radius: 0.1,
          ),
        ]),
      );
      expect(_alphaAt(erased, 0.5, 0.55), 0);
      expect(_alphaAt(erased, 0.5, 0.3), _alphaAt(a, 0.5, 0.3));
      final restored = await _drive(
        kit,
        kit.refineAvatar(erased, [
          AvatarStroke(
            brush: AvatarBrush.restore,
            points: const [(0.5, 0.55)],
            radius: 0.1,
          ),
        ], feather: 0.9),
      );
      expect(_alphaAt(restored, 0.5, 0.55), 255);
      expect(restored.feather, 0.9);
    });

    test('built-in avatars: count, PNG, tokens', () async {
      final kit = FakeVideoKit();
      expect(kit.builtinAvatarCount, 8);
      final png = await kit.builtinAvatar(3);
      expect(
        FakeAvatarTools.decodePng(
          png,
          FakeAvatarTools.size,
          FakeAvatarTools.size,
        ),
        isNotNull,
      );
      expect(FakeAvatarTools.builtinFor('builtin:3'), png);
      expect(FakeAvatarTools.builtinFor('builtin:9'), isNull);
      expect(FakeAvatarTools.builtinFor('app-avatar-1'), isNull);
      await expectLater(kit.builtinAvatar(0), throwsA(isA<VideoKitException>()));
    });

    test('PNG encode / decode round trip', () {
      final rgba = FakeAvatarTools.renderHead(seed: 42);
      final png = FakeAvatarTools.encodePng(
        rgba,
        FakeAvatarTools.size,
        FakeAvatarTools.size,
      );
      expect(
        FakeAvatarTools.decodePng(
          png,
          FakeAvatarTools.size,
          FakeAvatarTools.size,
        ),
        rgba,
      );
    });
  });

  group('IMAGE masks', () {
    Future<(FakeVideoKit, FakeEditProject, String)> project() async {
      final kit = FakeVideoKit();
      final p =
          await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
      final add = p.addSource(
        const VideoKitMediaSource(
          mediaToken: 'avatar-video',
          mediaKind: MediaKind.video,
          sourceRef: DemoSourceRef('normal'),
        ),
      );
      await kit.clock.advance(const Duration(milliseconds: 300));
      final src = await add;
      await p.apply(AddClip(src.sourceId, 0, 3000000));
      final mask =
          (await p.apply(
                    const AddMask(
                      MaskType.face,
                      MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2),
                      0,
                      2000000,
                    ),
                  )
                  as EditApplied)
              .createdId!;
      return (kit, p, mask);
    }

    test('IMAGE needs an avatar; SetMaskAvatar then IMAGE; undo', () async {
      final (_, p, mask) = await project();
      final noAvatar = await p.apply(SetMaskStyle(mask, MaskStyle.image, 0.5));
      expect(noAvatar, isA<EditRejected>());
      expect(
        (noAvatar as EditRejected).error.code,
        ErrorCode.invalidArgument,
      );
      const avatar = MaskAvatar(avatarToken: 'builtin:2', scale: 1.2);
      expect(await p.apply(const SetMaskAvatar('nope', avatar)), isA<EditRejected>());
      expect(await p.apply(SetMaskAvatar(mask, avatar)), isA<EditApplied>());
      expect(
        await p.apply(SetMaskStyle(mask, MaskStyle.image, 0.5)),
        isA<EditApplied>(),
      );
      var m = p.state.value.maskById(mask)!;
      expect((m.style, m.avatar), (MaskStyle.image, avatar));
      await p.undo();
      m = p.state.value.maskById(mask)!;
      expect(m.style, MaskStyle.mosaic);
      expect(m.avatar, avatar, reason: 'only the style was undone');
    });

    test('04A E7 Q7: switching the style keeps the avatar; back to IMAGE '
        'needs no new pick', () async {
      final (_, p, mask) = await project();
      const avatar = MaskAvatar(avatarToken: 'builtin:1', offsetX: 0.1);
      await p.apply(SetMaskAvatar(mask, avatar));
      await p.apply(SetMaskStyle(mask, MaskStyle.image, 0.5));
      for (final style in [MaskStyle.blur, MaskStyle.mosaic]) {
        expect(await p.apply(SetMaskStyle(mask, style, 0.5)), isA<EditApplied>());
        final m = p.state.value.maskById(mask)!;
        expect((m.style, m.avatar), (style, avatar));
      }
      expect(
        await p.apply(SetMaskStyle(mask, MaskStyle.image, 0.5)),
        isA<EditApplied>(),
      );
      expect(p.state.value.maskById(mask)!.avatar, avatar);
      // Kept through a snapshot round trip too.
      await p.apply(SetMaskStyle(mask, MaskStyle.blur, 0.5));
      final snap = await p.snapshot();
      expect(jsonDecode(snap.json).toString(), contains('builtin:1'));
    });

    test('invalid avatars are rejected', () async {
      final (_, p, mask) = await project();
      for (final bad in const [
        MaskAvatar(avatarToken: ''),
        MaskAvatar(avatarToken: 'x', scale: 0),
        MaskAvatar(avatarToken: '   '),
      ]) {
        expect(
          await p.apply(SetMaskAvatar(mask, bad)),
          isA<EditRejected>(),
          reason: '$bad',
        );
      }
      expect(
        await p.apply(
          const AddMask(
            MaskType.manual,
            MaskRegion(x: 0.1, y: 0.1, width: 0.2, height: 0.2),
            0,
            1000000,
            style: MaskStyle.image,
          ),
        ),
        isA<EditRejected>(),
      );
    });

    test('snapshot 1.1: avatar, IMAGE and rollDeg round trip', () async {
      final (kit, p, mask) = await project();
      await p.apply(
        SetMaskAvatar(
          mask,
          const MaskAvatar(
            avatarToken: 'app-avatar-3',
            scale: 1.5,
            offsetX: 0.1,
            offsetY: -0.05,
            followRotation: false,
          ),
        ),
      );
      await p.apply(SetMaskStyle(mask, MaskStyle.image, 0.5));
      await p.apply(
        StartTracking(
          mask,
          TrackingKind.face,
          seedRegion: const MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2),
        ),
      );
      await kit.clock.advance(const Duration(seconds: 3));
      final snap = await p.snapshot();
      final j = jsonDecode(snap.json) as Map<String, Object?>;
      expect(j['schemaMinor'], 1);
      final mj = (j['masks']! as List).single as Map<String, Object?>;
      expect(mj['style'], 'IMAGE');
      expect(mj['avatar'], {
        'avatarToken': 'app-avatar-3',
        'scale': 1.5,
        'offsetX': 0.1,
        'offsetY': -0.05,
        'followRotation': false,
      });
      final keys = mj['keyframes']! as List;
      expect(
        keys.whereType<Map<Object?, Object?>>().any((k) => k['rollDeg'] != null),
        isTrue,
        reason: 'tracker keyframes carry a head roll',
      );
      final restored = await FakeVideoKit().restoreEditProject(
        snap,
        EditProjectConfig(),
      );
      expect(restored.state.value.masks, p.state.value.masks);
      final m = restored.state.value.maskById(mask)!;
      expect(m.rollAt(500000), isNotNull);
    });

    test('IMAGE without an avatar reads as MOSAIC', () async {
      final restored = await FakeVideoKit().restoreEditProject(
        SerializedEditProject(
          schemaVersion: 1,
          json: jsonEncode({
            'schemaVersion': 1,
            'schemaMinor': 1,
            'projectId': 'p',
            'masks': [
              {
                'maskId': 'mask-1',
                'type': 'FACE',
                'style': 'IMAGE',
                'rangeUs': {'startUs': 0, 'endUs': 1000000},
                'avatar': null,
              },
            ],
          }),
        ),
        EditProjectConfig(),
      );
      expect(restored.state.value.masks.single.style, MaskStyle.mosaic);
    });
  });
}
