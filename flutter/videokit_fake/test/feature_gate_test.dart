// VK-A2 (REQ-API-10, FT01B-01/02): the Fake honours the static switches
// ("接口调用返回未开放") and asks the host's gate at the API entry points.
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

final class _Gate extends NoopHostCallbacks {
  _Gate(this.deny);

  final Set<VideoKitFeature> deny;

  @override
  Future<FeatureAccess> checkFeature(VideoKitFeature f, String? id) async =>
      deny.contains(f) ? const FeatureDenied() : FeatureAccess.allowed;
}

FakeVideoKit kitWith({
  Set<VideoKitFeature> hidden = const {},
  Set<VideoKitFeature> deny = const {},
}) => FakeVideoKit(
  config: VideoKitConfig(
    hostCallbacks: _Gate(deny),
    features: VideoKitFeatureConfig({
      for (final f in hidden) f: FeatureMode.hidden,
    }),
  ),
);

Future<FakeEditProject> projectOf(FakeVideoKit kit) async {
  final p = await kit.createEditProject(EditProjectConfig()) as FakeEditProject;
  final add = p.addSource(
    const VideoKitMediaSource(
      mediaToken: 'v',
      mediaKind: MediaKind.video,
      sourceRef: DemoSourceRef('normal'),
    ),
  );
  await kit.clock.advance(const Duration(milliseconds: 300));
  final src = await add;
  await p.apply(AddClip(src.sourceId, 0, 3000000));
  return p;
}

const _mask = AddMask(
  MaskType.manual,
  MaskRegion(x: 0.4, y: 0.4, width: 0.2, height: 0.2),
  0,
  1000000,
);

Matcher _throwsCode(ErrorCode code) => throwsA(
  isA<VideoKitException>().having((e) => e.error.code, 'code', code),
);

void main() {
  test('EDIT hidden: projects cannot be created or restored', () async {
    final kit = kitWith(hidden: {VideoKitFeature.edit});
    await expectLater(
      kit.createEditProject(EditProjectConfig()),
      _throwsCode(ErrorCode.featureDisabled),
    );
    await expectLater(
      kit.restoreEditProject(
        const SerializedEditProject(schemaVersion: 1, json: '{}'),
        EditProjectConfig(),
      ),
      _throwsCode(ErrorCode.featureDisabled),
    );
    // Playback is never switchable.
    expect(
      await kit.createSession(const VideoKitSessionConfig()),
      isA<VideoKitSession>(),
    );
  });

  test('EDIT denied by the gate: FEATURE_DENIED with the lock', () async {
    final kit = kitWith(deny: {VideoKitFeature.edit});
    await expectLater(
      kit.createEditProject(EditProjectConfig()),
      throwsA(
        isA<VideoKitException>()
            .having((e) => e.error.code, 'code', ErrorCode.featureDenied)
            .having((e) => e.error.params['badge'], 'badge', 'LOCK'),
      ),
    );
  });

  test('MASK_TRACKING hidden: mask and tracking commands are not '
      'available; clips still edit', () async {
    final p = await projectOf(kitWith(hidden: {VideoKitFeature.maskTracking}));
    expect(
      await p.apply(_mask),
      const EditUnsupported(UnsupportedReason.featureDisabled),
    );
    expect(
      await p.apply(SplitAt(p.state.value.timeline.clips.first.clipId, 1000000)),
      isA<EditApplied>(),
    );
  });

  test('AVATAR hidden: avatar commands and tools are not available; masks '
      'are', () async {
    final kit = kitWith(hidden: {VideoKitFeature.avatar});
    final p = await projectOf(kit);
    final id = (await p.apply(_mask) as EditApplied).createdId!;
    expect(
      await p.apply(
        SetMaskAvatar(id, const MaskAvatar(avatarToken: 'builtin:1')),
      ),
      const EditUnsupported(UnsupportedReason.featureDisabled),
    );
    expect(
      await p.apply(SetMaskStyle(id, MaskStyle.image, 0.5)),
      const EditUnsupported(UnsupportedReason.featureDisabled),
    );
    expect(
      await p.apply(SetMaskStyle(id, MaskStyle.blur, 0.5)),
      isA<EditApplied>(),
    );
    await expectLater(
      kit.prepareAvatar(
        const VideoKitMediaSource(
          mediaToken: 'img',
          mediaKind: MediaKind.imageStatic,
          sourceRef: DemoSourceRef('normal'),
        ),
      ),
      _throwsCode(ErrorCode.featureDisabled),
    );
  });

  test('EXPORT hidden or denied: the export does not start', () async {
    const request = VideoKitExportRequest(presetId: ExportPresets.p1080);
    const sink = VideoKitOutputSink(sinkRef: 'demo:none');
    var p = await projectOf(kitWith(hidden: {VideoKitFeature.export}));
    var r = await p.export(request, sink);
    expect((r as ExportFailed).error.code, ErrorCode.featureDisabled);
    expect(p.state.value.phase, isNot(EditPhase.exporting));
    p = await projectOf(kitWith(deny: {VideoKitFeature.export}));
    r = await p.export(request, sink);
    expect((r as ExportFailed).error.code, ErrorCode.featureDenied);
  });

  test('hiding EDIT also hides its dependants in the Fake project', () {
    expect(
      FakeEditProject.featureOf(_mask),
      VideoKitFeature.maskTracking,
    );
    expect(
      FakeEditProject.featureOf(
        const SetMaskAvatar('m', MaskAvatar(avatarToken: 'builtin:1')),
      ),
      VideoKitFeature.avatar,
    );
    expect(FakeEditProject.featureOf(const RemoveMask('m')), isNull);
  });
}
