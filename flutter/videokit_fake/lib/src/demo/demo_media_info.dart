import 'dart:math' as math;
import 'dart:typed_data';

import 'package:videokit_api/videokit_api.dart';

import 'demo_data.dart';

/// Demo [MediaInfo] for a profile (04A P2): plausible values, flagged as
/// demo data through the Fake's `isDemo`.
MediaInfo demoMediaInfo(DemoMediaItem p, String? mimeType) {
  final video = p.kind == MediaKind.video;
  final animated = p.kind == MediaKind.imageAnimated;
  final duration = p.durationUs;
  final bitrate = video ? 8000000 : null;
  final container =
      mimeType ??
      (video ? 'video/mp4' : (animated ? 'image/gif' : 'image/jpeg'));
  return MediaInfo(
    container: container,
    videoCodec: video ? 'video/avc' : null,
    audioCodec: video ? 'audio/mp4a-latm' : null,
    width: p.size.width,
    height: p.size.height,
    frameRate: video ? 30 : (animated ? 24 : null),
    bitrateBps: bitrate,
    rotationDeg: 0,
    durationUs: duration,
    fileSizeBytes: video && duration != null
        ? bitrate! ~/ 8 * duration ~/ 1000000
        : p.size.width * p.size.height ~/ 4,
  );
}

/// Size fitting [w]×[h] into [maxW]×[maxH] (aspect kept, never upscaled).
(int, int) fitThumbnail(int w, int h, int maxW, int maxH) {
  if (w <= 0 || h <= 0) return (maxW, maxH);
  final s = math.min(1.0, math.min(maxW / w, maxH / h));
  return (math.max(1, (w * s).round()), math.max(1, (h * s).round()));
}

/// Encodes a small demo picture (diagonal gradient from [seed], darker
/// band at the playhead fraction [at]) as PNG — pure Dart, no `dart:io`
/// (stored deflate blocks).
Uint8List demoThumbnailPng(int width, int height, int seed, double at) {
  final hue = (seed % 360) / 360;
  (int, int, int) rgb(double h, double s, double v) {
    final i = (h * 6).floor() % 6;
    final f = h * 6 - (h * 6).floor();
    final p = v * (1 - s), q = v * (1 - f * s), t = v * (1 - (1 - f) * s);
    final (r, g, b) = switch (i) {
      0 => (v, t, p),
      1 => (q, v, p),
      2 => (p, v, t),
      3 => (p, q, v),
      4 => (t, p, v),
      _ => (v, p, q),
    };
    return ((r * 255).round(), (g * 255).round(), (b * 255).round());
  }

  final raw = BytesBuilder();
  final band = (at.clamp(0.0, 1.0) * width).round();
  for (var y = 0; y < height; y++) {
    raw.addByte(0); // filter: none
    for (var x = 0; x < width; x++) {
      final d = (x / width + y / height) / 2;
      final v = (x - band).abs() < math.max(1, width ~/ 40) ? 0.35 : 0.85;
      final (r, g, b) = rgb((hue + d * 0.25) % 1.0, 0.55, v);
      raw
        ..addByte(r)
        ..addByte(g)
        ..addByte(b);
    }
  }
  return _png(width, height, raw.takeBytes());
}

Uint8List _png(int w, int h, Uint8List scanlines) {
  final out = BytesBuilder()
    ..add(const [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
  void chunk(String type, List<int> data) {
    final t = type.codeUnits;
    out
      ..add(_u32(data.length))
      ..add(t)
      ..add(data)
      ..add(_u32(_crc32([...t, ...data])));
  }

  chunk('IHDR', [..._u32(w), ..._u32(h), 8, 2, 0, 0, 0]);
  chunk('IDAT', _zlibStored(scanlines));
  chunk('IEND', const []);
  return out.takeBytes();
}

List<int> _zlibStored(Uint8List data) {
  final out = BytesBuilder()..add(const [0x78, 0x01]);
  const max = 65535;
  for (var off = 0; off < data.length || off == 0; off += max) {
    final len = math.min(max, data.length - off);
    final last = off + len >= data.length;
    out
      ..addByte(last ? 1 : 0)
      ..add([len & 0xFF, len >> 8, ~len & 0xFF, (~len >> 8) & 0xFF])
      ..add(Uint8List.sublistView(data, off, off + len));
    if (last) break;
  }
  var a = 1, b = 0;
  for (final x in data) {
    a = (a + x) % 65521;
    b = (b + a) % 65521;
  }
  out.add(_u32((b << 16) | a));
  return out.takeBytes();
}

List<int> _u32(int v) => [
  (v >> 24) & 0xFF,
  (v >> 16) & 0xFF,
  (v >> 8) & 0xFF,
  v & 0xFF,
];

final List<int> _crcTable = List.generate(256, (n) {
  var c = n;
  for (var k = 0; k < 8; k++) {
    c = (c & 1) != 0 ? 0xEDB88320 ^ (c >> 1) : c >> 1;
  }
  return c;
});

int _crc32(List<int> bytes) {
  var c = 0xFFFFFFFF;
  for (final b in bytes) {
    c = _crcTable[(c ^ b) & 0xFF] ^ (c >> 8);
  }
  return c ^ 0xFFFFFFFF;
}
