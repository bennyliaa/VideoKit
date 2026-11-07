// M3-A1: multi-instance scenarios of the Dart Fake — decoder budget,
// single-slot fault injection, audio preemption, offscreen pause/release,
// stale audio epochs (07 §3–§5).
import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';

VideoKitMediaSource _video(String token, [MediaKind kind = MediaKind.video]) =>
    VideoKitMediaSource(
      mediaToken: token,
      mediaKind: kind,
      sourceRef: const DemoSourceRef('normal'),
    );

Future<(FakeSession, VideoKitCommandResult)> _open(
  FakeVideoKit kit,
  String token, [
  MediaKind kind = MediaKind.video,
]) async {
  final s =
      await kit.createSession(const VideoKitSessionConfig()) as FakeSession;
  final f = s.bind(_video(token, kind));
  await kit.clock.advance(const Duration(seconds: 1));
  return (s, await f);
}

void main() {
  test('decoder budget: the extra video is denied, images are not; freed '
      'decoders are reused', () async {
    final kit = FakeVideoKit(videoDecoderBudget: 2);
    final (a, ra) = await _open(kit, 'a');
    final (b, rb) = await _open(kit, 'b');
    expect(ra, const Executed());
    expect(rb, const Executed());
    final (c, rc) = await _open(kit, 'c');
    expect(rc, isA<Rejected>());
    expect((rc as Rejected).error.code, ErrorCode.decoderResourceExhausted);
    expect(rc.error.retryable, isTrue);
    expect(c.state.value.phase, SessionPhase.errorRecoverable);
    expect(c.holdsDecoder, isFalse);
    // Images do not take a video decoder.
    final (_, ri) = await _open(kit, 'img', MediaKind.imageStatic);
    expect(ri, const Executed());
    // Others are untouched.
    expect(a.state.value.phase, SessionPhase.ready);
    expect(b.state.value.phase, SessionPhase.ready);
    // Releasing one frees a decoder for the next bind.
    await a.release();
    final f = c.bind(_video('c'));
    await kit.clock.advance(const Duration(seconds: 1));
    expect(await f, const Executed());
    await kit.close();
  });

  test('fault injection fails one session only', () async {
    final kit = FakeVideoKit();
    final (a, _) = await _open(kit, 'a');
    final (b, _) = await _open(kit, 'b');
    await b.execute(const Play());
    final events = <VideoKitEvent>[];
    a.events.listen(events.add);
    a.injectFault(
      const VideoKitStableError(
        code: ErrorCode.decoderUnavailable,
        stage: ErrorStage.playback,
      ),
    );
    await kit.clock.advance(const Duration(seconds: 1));
    expect(a.state.value.phase, SessionPhase.errorFatal);
    expect(a.holdsDecoder, isFalse);
    expect(events.whereType<ErrorRaised>(), hasLength(1));
    expect(b.state.value.phase, SessionPhase.playing);
    expect(b.state.value.error, isNull);
    await kit.close();
  });

  test('K2: audio focus lost for good pauses the source and says so', () async {
    final kit = FakeVideoKit();
    final (a, _) = await _open(kit, 'a');
    final (b, _) = await _open(kit, 'b');
    expect(await a.execute(const SetActiveAudio(true, 1)), const Executed());
    await a.execute(const Play());
    final notices = <VideoKitEvent>[];
    a.events.listen(notices.add);
    kit.preemptAudio();
    await kit.clock.advance(const Duration(milliseconds: 100));
    expect(a.state.value.phase, SessionPhase.paused);
    expect(a.state.value.activeAudio, isTrue, reason: 'still the source');
    expect(a.state.value.muted, isFalse, reason: 'paused, not muted');
    expect(
      notices,
      contains(const TransientNotice(NoticeCodes.audioFocusLost)),
    );
    expect(b.state.value.activeAudio, isFalse, reason: 'untouched');
    await kit.close();
  });

  test('K2: a transient focus loss pauses silently and resumes', () async {
    final kit = FakeVideoKit();
    final (a, _) = await _open(kit, 'a');
    await a.execute(const SetActiveAudio(true, 1));
    await a.execute(const Play());
    final notices = <VideoKitEvent>[];
    a.events.listen(notices.add);
    kit.preemptAudio(transient: true);
    await kit.clock.advance(const Duration(milliseconds: 100));
    expect(a.state.value.phase, SessionPhase.paused);
    expect(notices.whereType<TransientNotice>(), isEmpty, reason: 'no notice');
    kit.regainAudioFocus();
    await kit.clock.advance(const Duration(milliseconds: 100));
    expect(a.state.value.phase, SessionPhase.playing);
    await kit.close();
  });

  test('stale audio epochs are rejected', () async {
    final kit = FakeVideoKit();
    final (a, _) = await _open(kit, 'a');
    expect(await a.execute(const SetActiveAudio(true, 5)), const Executed());
    final late = await a.execute(const SetActiveAudio(false, 4));
    expect(late, isA<Rejected>());
    expect(a.state.value.activeAudio, isTrue);
    await kit.close();
  });

  test(
    'offscreen pauses, releases the decoder later, resumes on visible',
    () async {
      final kit = FakeVideoKit(videoDecoderBudget: 1);
      final (a, _) = await _open(kit, 'a');
      await a.execute(const Play());
      await a.execute(const SetVisibility(SessionVisibility.offscreen));
      await kit.clock.advance(const Duration(milliseconds: 100));
      expect(a.state.value.phase, SessionPhase.paused);
      expect(a.holdsDecoder, isTrue, reason: 'kept for a while');
      await kit.clock.advance(const Duration(seconds: 5));
      expect(a.holdsDecoder, isFalse, reason: 'released after the delay');
      final pos = a.state.value.positionUs;
      // The freed decoder can serve another slot.
      final (_, rb) = await _open(kit, 'b');
      expect(rb, const Executed());
      await a.execute(const SetVisibility(SessionVisibility.visible));
      await kit.clock.advance(const Duration(milliseconds: 100));
      expect(a.state.value.phase, SessionPhase.playing);
      expect(a.state.value.positionUs, greaterThanOrEqualTo(pos));
      await kit.close();
    },
  );

  test('visible again before the delay keeps the decoder', () async {
    final kit = FakeVideoKit();
    final (a, _) = await _open(kit, 'a');
    await a.execute(const Play());
    await a.execute(const SetVisibility(SessionVisibility.background));
    await kit.clock.advance(const Duration(seconds: 2));
    await a.execute(const SetVisibility(SessionVisibility.visible));
    await kit.clock.advance(const Duration(seconds: 10));
    expect(a.holdsDecoder, isTrue);
    expect(a.state.value.phase, SessionPhase.playing);
    await kit.close();
  });
}
