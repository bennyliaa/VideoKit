import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

/// Small deterministic PRNG (SplitMix32-style) so demo data is identical on
/// every platform and Dart version (`dart:math` Random gives no such
/// guarantee).
final class DemoRandom {
  /// Seeds the generator.
  DemoRandom(int seed) : _state = seed & 0xFFFFFFFF;

  int _state;

  /// Next unsigned 32-bit value.
  int nextUint32() {
    _state = (_state + 0x9E3779B9) & 0xFFFFFFFF;
    var z = _state;
    z = ((z ^ (z >> 16)) * 0x85EBCA6B) & 0xFFFFFFFF;
    z = ((z ^ (z >> 13)) * 0xC2B2AE35) & 0xFFFFFFFF;
    return (z ^ (z >> 16)) & 0xFFFFFFFF;
  }

  /// Uniform int in `[min, max]`.
  int nextInt(int min, int max) => min + nextUint32() % (max - min + 1);

  /// Uniform double in `[0, 1)`.
  double nextDouble() => nextUint32() / 4294967296.0;
}

/// FNV-1a 32-bit hash of [text] (stable seed derivation from tokens).
int stableHash(String text) {
  var h = 0x811C9DC5;
  for (final unit in utf8.encode(text)) {
    h ^= unit;
    h = (h * 0x01000193) & 0xFFFFFFFF;
  }
  return h;
}

/// Synthetic description of a demo media item. Never refers to real files.
@immutable
final class DemoMediaItem {
  /// Creates an item.
  DemoMediaItem({
    required this.mediaToken,
    required this.kind,
    required this.displayName,
    required this.size,
    required this.seed,
    this.durationUs,
    List<TrackInfo> audioTracks = const [],
    List<TrackInfo> subtitleTracks = const [],
    this.scenarioId = 'normal',
  }) : audioTracks = List.unmodifiable(audioTracks),
       subtitleTracks = List.unmodifiable(subtitleTracks);

  /// Opaque token.
  final String mediaToken;

  /// Kind.
  final MediaKind kind;

  /// Display name.
  final String displayName;

  /// Picture size.
  final VideoSize size;

  /// Seed for the demo picture.
  final int seed;

  /// Duration (video / animated image).
  final int? durationUs;

  /// Audio tracks.
  final List<TrackInfo> audioTracks;

  /// Subtitle tracks.
  final List<TrackInfo> subtitleTracks;

  /// Fake scenario ID.
  final String scenarioId;

  /// Media source for binding to a Fake session.
  VideoKitMediaSource toMediaSource() => VideoKitMediaSource(
    mediaToken: mediaToken,
    mediaKind: kind,
    displayName: displayName,
    sourceRef: DemoSourceRef(scenarioId),
    mimeType: kind == MediaKind.video ? 'video/mp4' : 'image/png',
  );

  /// JSON form for the manifest.
  Map<String, Object?> toJson() => {
    'mediaToken': mediaToken,
    'kind': kind.wireName,
    'displayName': displayName,
    'width': size.width,
    'height': size.height,
    'seed': seed,
    'durationUs': durationUs,
    'audioTracks': [for (final t in audioTracks) t.id],
    'subtitleTracks': [for (final t in subtitleTracks) t.id],
    'scenarioId': scenarioId,
  };
}

/// Fixed-seed demo data generator with a manifest (14 §11.1, 03 §8.2).
///
/// Produces only original synthetic data: no `test_media`, personal photos
/// or credentials.
final class DemoDataGenerator {
  /// Creates a generator.
  DemoDataGenerator({this.seed = 20261106, this.mediaCount = 12});

  /// Generator version, recorded in the manifest.
  static const String generatorVersion = '1';

  /// Seed.
  final int seed;

  /// Number of media items.
  final int mediaCount;

  /// Kinds cycled through, with scenario IDs for the abnormal ones.
  static const List<(MediaKind, String)> _pattern = [
    (MediaKind.video, 'normal'),
    (MediaKind.video, 'normal'),
    (MediaKind.imageStatic, 'normal'),
    (MediaKind.imageAnimated, 'normal'),
    (MediaKind.video, 'buffering'),
    (MediaKind.video, 'slowLoad'),
    (MediaKind.video, 'unsupported'),
    (MediaKind.video, 'corrupt'),
    (MediaKind.imageStatic, 'normal'),
    (MediaKind.video, 'disconnect'),
    (MediaKind.video, 'resourceExhausted'),
    (MediaKind.video, 'normal'),
  ];

  /// Media items.
  List<DemoMediaItem> media() {
    final rnd = DemoRandom(seed);
    return List.unmodifiable([
      for (var i = 0; i < mediaCount; i++)
        _item(i, rnd, _pattern[i % _pattern.length]),
    ]);
  }

  DemoMediaItem _item(int i, DemoRandom rnd, (MediaKind, String) p) {
    final (kind, scenarioId) = p;
    final portrait = rnd.nextInt(0, 3) == 0;
    final size = portrait
        ? const VideoSize(1080, 1920)
        : const VideoSize(1920, 1080);
    final itemSeed = rnd.nextUint32();
    final index = (i + 1).toString().padLeft(2, '0');
    return switch (kind) {
      MediaKind.video => DemoMediaItem(
        mediaToken: 'demo-$seed-$index',
        kind: kind,
        displayName: 'Demo video $index',
        size: size,
        seed: itemSeed,
        durationUs: rnd.nextInt(60, 240) * 1000000,
        audioTracks: demoAudioTracks,
        subtitleTracks: demoSubtitleTracks,
        scenarioId: scenarioId,
      ),
      MediaKind.imageAnimated => DemoMediaItem(
        mediaToken: 'demo-$seed-$index',
        kind: kind,
        displayName: 'Demo animation $index',
        size: const VideoSize(480, 480),
        seed: itemSeed,
        durationUs: 2000000,
        scenarioId: scenarioId,
      ),
      _ => DemoMediaItem(
        mediaToken: 'demo-$seed-$index',
        kind: kind,
        displayName: 'Demo image $index',
        size: size,
        seed: itemSeed,
        scenarioId: scenarioId,
      ),
    };
  }

  /// Demo tracks shared by demo videos.
  static const List<TrackInfo> demoAudioTracks = [
    TrackInfo(
      id: 'audio-en',
      language: 'en',
      label: 'English',
      codec: 'audio/mp4a-latm',
    ),
    TrackInfo(
      id: 'audio-zh',
      language: 'zh',
      label: '中文',
      codec: 'audio/mp4a-latm',
    ),
    TrackInfo(
      id: 'audio-dts',
      language: 'en',
      label: 'DTS',
      codec: 'audio/vnd.dts',
      supported: false,
    ),
  ];

  /// Demo subtitle tracks.
  static const List<TrackInfo> demoSubtitleTracks = [
    TrackInfo(id: 'sub-en', language: 'en', label: 'English'),
    TrackInfo(id: 'sub-zh', language: 'zh', label: '简体中文'),
  ];

  /// Deterministic metadata for any source the Fake is asked to bind (demo
  /// items resolve to themselves; other tokens are derived from a hash).
  static DemoMediaItem profileFor(VideoKitMediaSource source) {
    final h = stableHash(source.mediaToken);
    final rnd = DemoRandom(h);
    final scenarioId = switch (source.sourceRef) {
      DemoSourceRef(:final scenarioId) => scenarioId,
      _ => 'normal',
    };
    final kind = source.mediaKind == MediaKind.imageUnknown
        ? MediaKind.imageStatic
        : source.mediaKind;
    return DemoMediaItem(
      mediaToken: source.mediaToken,
      kind: kind,
      displayName: source.displayName ?? 'Demo',
      size: kind == MediaKind.imageAnimated
          ? const VideoSize(480, 480)
          : const VideoSize(1920, 1080),
      seed: h,
      durationUs: switch (kind) {
        MediaKind.video => rnd.nextInt(60, 240) * 1000000,
        MediaKind.imageAnimated => 2000000,
        _ => null,
      },
      audioTracks: kind == MediaKind.video ? demoAudioTracks : const [],
      subtitleTracks: kind == MediaKind.video ? demoSubtitleTracks : const [],
      scenarioId: scenarioId,
    );
  }

  /// Demo tracking LOST ranges and clip layout for the editor demo.
  Map<String, Object?> editDemo() {
    final rnd = DemoRandom(seed ^ 0x5EED);
    final clips = [
      for (var i = 0; i < 3; i++)
        {
          'inUs': i * 10000000,
          'outUs': i * 10000000 + rnd.nextInt(4, 9) * 1000000,
        },
    ];
    final lostStart = rnd.nextInt(2, 5);
    return {
      'clips': clips,
      'mask': {'left': 0.3, 'top': 0.25, 'width': 0.2, 'height': 0.25},
      'trackingLostUs': [lostStart * 1000000, (lostStart + 2) * 1000000],
      'exportStages': [for (final s in ExportStage.values) s.wireName],
    };
  }

  /// Content (without hash) used for hashing.
  Map<String, Object?> _content() => {
    'generator': 'videokit_fake/DemoDataGenerator',
    'generatorVersion': generatorVersion,
    'seed': seed,
    'params': {'mediaCount': mediaCount},
    'media': [for (final m in media()) m.toJson()],
    'edit': editDemo(),
  };

  /// Manifest with seed, parameters and SHA-256 content hash.
  Map<String, Object?> manifest() {
    final content = _content();
    final hash = sha256.convert(utf8.encode(jsonEncode(content))).toString();
    return {...content, 'contentSha256': hash};
  }

  /// Manifest as pretty JSON (`manifest.json`).
  String manifestJson() =>
      const JsonEncoder.withIndent('  ').convert(manifest());
}
