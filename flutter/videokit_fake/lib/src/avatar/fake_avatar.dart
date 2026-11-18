import 'dart:math' as math;
import 'dart:typed_data';

import 'package:videokit_api/videokit_api.dart';

import '../clock/fake_clock.dart';

/// Fake avatar cut-out (REQ-ED-07, 04A E5/E6): returns a synthetic head
/// (round face with hair, transparent background, softened edge) as a real
/// PNG, and applies erase / restore strokes pixel by pixel. Never looks at
/// the picture's content.
///
/// Scenarios by `DemoSourceRef.scenarioId`: [noFace], [unsupportedImage],
/// [multipleFaces], [slow]; anything else succeeds after [delay].
final class FakeAvatarTools implements VideoKitAvatarTools {
  /// Creates the tools on [clock].
  FakeAvatarTools(this.clock);

  /// Clock of the owning Fake.
  final FakeClock clock;

  /// Normal processing time.
  static const Duration delay = Duration(milliseconds: 800);

  /// Scenario: no face found (`AVATAR_NO_FACE`).
  static const String noFace = 'avatarNoFace';

  /// Scenario: picture cannot be decoded (`AVATAR_IMAGE_UNSUPPORTED`).
  static const String unsupportedImage = 'avatarUnsupported';

  /// Scenario: several faces (warning only).
  static const String multipleFaces = 'avatarMultipleFaces';

  /// Scenario: 3 s processing.
  static const String slow = 'avatarSlow';

  /// Built-in avatars the Kit provides as `builtin:1` … `builtin:N`
  /// (04A E5 5).
  static const int builtinCount = 8;

  /// Side of the synthetic PNG.
  static const int size = 128;

  int _next = 0;
  final Map<String, Uint8List> _originals = {};

  /// Error by registered code name, or `INVALID_ARGUMENT` with the name as
  /// diagnostic until the code is in spec/errors.json (M5A-A1).
  static VideoKitException avatarError(String code) {
    final known = ErrorCode.fromName(code);
    return VideoKitException(
      VideoKitStableError(
        code: known == ErrorCode.internalErrorRedacted
            ? ErrorCode.invalidArgument
            : known,
        stage: ErrorStage.edit,
        diagnostic: code,
      ),
    );
  }

  @override
  Future<AvatarImage> prepareAvatar(
    VideoKitMediaSource image, {
    AvatarPrepareOptions options = const AvatarPrepareOptions(),
  }) async {
    final scenario = switch (image.sourceRef) {
      DemoSourceRef(:final scenarioId) => scenarioId,
      _ => '',
    };
    await clock.delay(
      scenario == slow ? const Duration(seconds: 3) : delay,
    );
    if (scenario == noFace) throw avatarError('AVATAR_NO_FACE');
    if (scenario == unsupportedImage) {
      throw avatarError('AVATAR_IMAGE_UNSUPPORTED');
    }
    final id = 'avatar-${++_next}';
    final seed = image.mediaToken.hashCode;
    final rgba = renderHead(
      seed: seed,
      feather: options.feather,
      withShoulders: !options.cropToHead,
    );
    _originals[id] = rgba;
    return AvatarImage(
      avatarId: id,
      png: encodePng(rgba, size, size),
      width: size,
      height: size,
      headBox: headBox(withShoulders: !options.cropToHead),
      sourceFaceBox: const MaskRegion(x: 0.3, y: 0.15, width: 0.4, height: 0.45),
      feather: options.feather,
      cropToHead: options.cropToHead,
      warnings: [if (scenario == multipleFaces) AvatarImage.multipleFaces],
      isDemo: true,
    );
  }

  @override
  Future<AvatarImage> refineAvatar(
    AvatarImage avatar,
    List<AvatarStroke> strokes, {
    double? feather,
  }) async {
    await clock.delay(const Duration(milliseconds: 100));
    final rgba =
        decodePng(avatar.png, avatar.width, avatar.height) ??
        (throw avatarError('AVATAR_IMAGE_UNSUPPORTED'));
    final original = _originals[avatar.avatarId];
    final w = avatar.width;
    final h = avatar.height;
    for (final s in strokes) {
      final r = s.radius * w;
      for (final (px, py) in s.points) {
        final cx = px * w;
        final cy = py * h;
        final x0 = math.max(0, (cx - r).floor());
        final x1 = math.min(w - 1, (cx + r).ceil());
        final y0 = math.max(0, (cy - r).floor());
        final y1 = math.min(h - 1, (cy + r).ceil());
        for (var y = y0; y <= y1; y++) {
          for (var x = x0; x <= x1; x++) {
            final dx = x + 0.5 - cx;
            final dy = y + 0.5 - cy;
            if (dx * dx + dy * dy > r * r) continue;
            final i = (y * w + x) * 4;
            if (s.brush == AvatarBrush.erase) {
              rgba[i + 3] = 0;
            } else if (original != null) {
              for (var k = 0; k < 4; k++) {
                rgba[i + k] = original[i + k];
              }
            }
          }
        }
      }
    }
    return avatar.copyWith(
      png: encodePng(rgba, w, h),
      feather: feather ?? avatar.feather,
    );
  }

  @override
  int get builtinAvatarCount => builtinCount;

  @override
  Future<Uint8List> builtinAvatar(int index) async {
    if (index < 1 || index > builtinCount) {
      throw avatarError('AVATAR_IMAGE_UNSUPPORTED');
    }
    return builtinPng(index);
  }

  /// The Kit's built-in avatar `n` (1-based) as a PNG (04A E5 5).
  static Uint8List builtinPng(int n) => encodePng(
    renderHead(seed: n * 7919, feather: 0.3, builtin: true),
    size,
    size,
  );

  /// PNG for [avatarToken] when it is `builtin:N`; null otherwise.
  static Uint8List? builtinFor(String avatarToken) {
    if (!avatarToken.startsWith(MaskAvatar.builtinPrefix)) return null;
    final n = int.tryParse(
      avatarToken.substring(MaskAvatar.builtinPrefix.length),
    );
    if (n == null || n < 1 || n > builtinCount) return null;
    return builtinPng(n);
  }

  /// Head box of the synthetic picture (normalized).
  static MaskRegion headBox({bool withShoulders = false}) => withShoulders
      ? const MaskRegion(x: 0.25, y: 0.05, width: 0.5, height: 0.55)
      : const MaskRegion(x: 0.12, y: 0.06, width: 0.76, height: 0.88);

  // ----------------------------------------------------------- drawing --

  static const List<(int, int, int)> _skins = [
    (0xE8, 0xBE, 0x96),
    (0xC6, 0x8A, 0x5A),
    (0xF0, 0xC4, 0x7E),
    (0x9C, 0x66, 0x44),
  ];

  static const List<(int, int, int)> _hairs = [
    (0x3A, 0x22, 0x14),
    (0x12, 0x18, 0x24),
    (0x93, 0x40, 0x10),
    (0x60, 0x40, 0x30),
  ];

  static const List<(int, int, int)> _builtinColors = [
    (0xF5, 0x9E, 0x0B),
    (0x10, 0xB9, 0x81),
    (0x63, 0x66, 0xF1),
    (0xEC, 0x48, 0x99),
    (0x0E, 0xA5, 0xE9),
    (0x84, 0xCC, 0x16),
    (0xF4, 0x3F, 0x5E),
    (0xA8, 0x55, 0xF7),
  ];

  /// RGBA pixels of a synthetic head ([size]²).
  static Uint8List renderHead({
    required int seed,
    double feather = 0.5,
    bool withShoulders = false,
    bool builtin = false,
  }) {
    const s = size;
    final out = Uint8List(s * s * 4);
    final rnd = seed.abs();
    final skin = builtin
        ? _builtinColors[(rnd ~/ 7919 - 1).clamp(0, 7)]
        : _skins[rnd % _skins.length];
    final hair = _hairs[(rnd ~/ 7) % _hairs.length];
    final faceR = withShoulders ? s * 0.22 : s * 0.38;
    final cx = s / 2;
    final cy = withShoulders ? s * 0.33 : s * 0.52;
    final soft = 1 + feather * 6;
    void put(int x, int y, (int, int, int) c, double a) {
      if (a <= 0) return;
      final i = (y * s + x) * 4;
      final old = out[i + 3] / 255;
      final na = a + old * (1 - a);
      for (var k = 0; k < 3; k++) {
        final cv = switch (k) {
          0 => c.$1,
          1 => c.$2,
          _ => c.$3,
        };
        out[i + k] = na == 0
            ? 0
            : ((cv * a + out[i + k] * old * (1 - a)) / na).round();
      }
      out[i + 3] = (na * 255).round().clamp(0, 255);
    }

    double edge(double dist, double r) =>
        ((r - dist) / soft + 0.5).clamp(0.0, 1.0);

    for (var y = 0; y < s; y++) {
      for (var x = 0; x < s; x++) {
        final px = x + 0.5;
        final py = y + 0.5;
        if (withShoulders && py > s * 0.62) {
          final w = s * 0.42 - (py - s * 0.62) * -0.4;
          put(x, y, hair, edge((px - cx).abs(), w));
        }
        final d = math.sqrt((px - cx) * (px - cx) + (py - cy) * (py - cy));
        if (!builtin && py < cy - faceR * 0.15) {
          put(x, y, hair, edge(d, faceR * 1.08));
        }
        put(x, y, skin, edge(d, faceR));
        if (!builtin && py < cy - faceR * 0.35 && d < faceR * 1.02) {
          put(x, y, hair, edge(d, faceR * 1.02));
        }
        final ex = faceR * 0.36;
        final ey = cy - faceR * 0.05;
        const eye = (0x1F, 0x29, 0x37);
        const white = (0xFF, 0xFF, 0xFF);
        for (final sx in [-1, 1]) {
          final de = math.sqrt(
            (px - (cx + sx * ex)) * (px - (cx + sx * ex)) +
                (py - ey) * (py - ey),
          );
          put(x, y, builtin ? white : eye, edge(de, faceR * 0.09));
        }
        if (!builtin) {
          final dm = math.sqrt(
            (px - cx) * (px - cx) + (py - (cy + faceR * 0.1)) * (py - (cy + faceR * 0.1)),
          );
          if (py > cy + faceR * 0.3) {
            put(
              x,
              y,
              (0xB0, 0x12, 0x3A),
              edge((dm - faceR * 0.45).abs(), faceR * 0.05),
            );
          }
        }
      }
    }
    return out;
  }

  // ------------------------------------------------------------- PNG --
  // Uncompressed ("stored" deflate) PNG: enough for a Fake, no package.

  static final List<int> _crcTable = List<int>.generate(256, (n) {
    var c = n;
    for (var k = 0; k < 8; k++) {
      c = (c & 1) != 0 ? 0xEDB88320 ^ (c >> 1) : c >> 1;
    }
    return c;
  });

  static int _crc(List<int> bytes) {
    var c = 0xFFFFFFFF;
    for (final b in bytes) {
      c = _crcTable[(c ^ b) & 0xFF] ^ (c >> 8);
    }
    return c ^ 0xFFFFFFFF;
  }

  static List<int> _u32(int v) => [
    (v >> 24) & 0xFF,
    (v >> 16) & 0xFF,
    (v >> 8) & 0xFF,
    v & 0xFF,
  ];

  static List<int> _chunk(String type, List<int> data) {
    final t = type.codeUnits;
    return [..._u32(data.length), ...t, ...data, ..._u32(_crc([...t, ...data]))];
  }

  /// Encodes RGBA pixels as an 8-bit RGBA PNG.
  static Uint8List encodePng(Uint8List rgba, int w, int h) {
    final raw = BytesBuilder(copy: false);
    for (var y = 0; y < h; y++) {
      raw
        ..addByte(0)
        ..add(Uint8List.sublistView(rgba, y * w * 4, (y + 1) * w * 4));
    }
    final data = raw.takeBytes();
    final z = BytesBuilder(copy: false)..add([0x78, 0x01]);
    var a = 1;
    var b = 0;
    for (final v in data) {
      a = (a + v) % 65521;
      b = (b + a) % 65521;
    }
    for (var off = 0; off < data.length || off == 0; off += 65535) {
      final end = math.min(data.length, off + 65535);
      final len = end - off;
      z
        ..addByte(end == data.length ? 1 : 0)
        ..add([len & 0xFF, len >> 8, (~len) & 0xFF, ((~len) >> 8) & 0xFF])
        ..add(Uint8List.sublistView(data, off, end));
      if (end == data.length) break;
    }
    z.add(_u32((b << 16) | a));
    return Uint8List.fromList([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
      ..._chunk('IHDR', [..._u32(w), ..._u32(h), 8, 6, 0, 0, 0]),
      ..._chunk('IDAT', z.takeBytes()),
      ..._chunk('IEND', const []),
    ]);
  }

  /// Decodes a PNG written by [encodePng] (stored deflate, filter 0);
  /// null for any other PNG.
  static Uint8List? decodePng(Uint8List png, int w, int h) {
    if (png.length < 8 || png[1] != 0x50) return null;
    final idat = BytesBuilder(copy: false);
    var p = 8;
    while (p + 8 <= png.length) {
      final len =
          (png[p] << 24) | (png[p + 1] << 16) | (png[p + 2] << 8) | png[p + 3];
      final type = String.fromCharCodes(png.sublist(p + 4, p + 8));
      if (type == 'IDAT') idat.add(png.sublist(p + 8, p + 8 + len));
      p += 12 + len;
    }
    final z = idat.takeBytes();
    if (z.length < 2) return null;
    final raw = BytesBuilder(copy: false);
    var q = 2;
    while (q < z.length - 4) {
      final header = z[q];
      if ((header & 0x06) != 0) return null; // not a stored block
      final len = z[q + 1] | (z[q + 2] << 8);
      raw.add(z.sublist(q + 5, q + 5 + len));
      q += 5 + len;
      if ((header & 1) == 1) break;
    }
    final data = raw.takeBytes();
    if (data.length != h * (w * 4 + 1)) return null;
    final out = Uint8List(w * h * 4);
    for (var y = 0; y < h; y++) {
      if (data[y * (w * 4 + 1)] != 0) return null;
      out.setRange(
        y * w * 4,
        (y + 1) * w * 4,
        data,
        y * (w * 4 + 1) + 1,
      );
    }
    return out;
  }
}
