import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:flutter/painting.dart';
import 'package:videokit_api/videokit_api.dart';

import '../history/app_storage.dart';

/// One avatar the App saved (REQ-ED-07, App business, 04A E5 1 / E6).
@immutable
final class SavedAvatar {
  /// Creates an entry.
  const SavedAvatar({
    required this.token,
    required this.path,
    required this.savedAtEpochMs,
  });

  /// `avatarToken` handed to the Kit (opaque, never a path).
  final String token;

  /// App-private file.
  final String path;

  /// Last use.
  final int savedAtEpochMs;

  /// JSON form.
  Map<String, Object?> toJson() => {
    'token': token,
    'path': path,
    'savedAtEpochMs': savedAtEpochMs,
  };

  /// Parses [j]; null when broken.
  static SavedAvatar? fromJson(Map<String, Object?> j) {
    final token = j['token'];
    final path = j['path'];
    final at = j['savedAtEpochMs'];
    if (token is! String || path is! String || at is! num) return null;
    return SavedAvatar(token: token, path: path, savedAtEpochMs: at.toInt());
  }
}

/// The App's avatars (04A E5 1: the host stores the PNG and gives the Kit
/// only a token). Kept in the App-private directory, newest first, at most
/// [limit] ("最近使用"); built-in avatars come from the Kit.
class AvatarStore extends ChangeNotifier {
  /// Creates the store.
  AvatarStore({
    required this.storage,
    DateTime Function()? now,
    Set<String> Function()? referenced,
  }) : now = now ?? DateTime.now,
       referenced = referenced ?? _none;

  static Set<String> _none() => const {};

  /// 04A E7 Q4: tokens used by kept projects; these are never evicted.
  final Set<String> Function() referenced;

  /// Full: [limit] avatars kept and every one is used by a kept project, so
  /// a new one cannot be saved (the App says so instead of evicting).
  bool get isFull {
    if (_items.length < limit) return false;
    final used = referenced();
    return _items.every((a) => used.contains(a.token));
  }

  /// Storage.
  final AppStorage storage;

  /// Clock.
  final DateTime Function() now;

  /// File name of the index.
  static const String fileName = 'avatars.json';

  /// Kept avatars.
  static const int limit = 12;

  /// Token prefix of App avatars.
  static const String tokenPrefix = 'app-avatar-';

  List<SavedAvatar> _items = const [];
  int _counter = 0;
  final Map<String, Uint8List> _builtins = {};

  /// Saved avatars, newest first.
  List<SavedAvatar> get recent => _items;

  /// Loads the index (broken entries are dropped).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final j = jsonDecode(raw) as Map<String, Object?>;
      _counter = (j['counter'] as num?)?.toInt() ?? 0;
      _items = [
        for (final e in j['avatars'] as List<Object?>? ?? const [])
          if (e is Map<String, Object?>) ?SavedAvatar.fromJson(e),
      ];
    } on Object {
      _items = const [];
    }
    notifyListeners();
  }

  /// Saves [png] and returns its new token. Over [limit] the oldest avatar
  /// no kept project uses is dropped (04A E7 Q4); throws
  /// [AvatarStoreFullException] when [isFull].
  Future<String> save(Uint8List png) async {
    if (isFull) throw const AvatarStoreFullException();
    final token = '$tokenPrefix${++_counter}';
    final path = await storage.writeAvatar('$token.png', png);
    _items = [
      SavedAvatar(
        token: token,
        path: path,
        savedAtEpochMs: now().millisecondsSinceEpoch,
      ),
      ..._items,
    ];
    final used = referenced();
    final dropped = <SavedAvatar>[];
    while (_items.length > limit) {
      final victim = _items.lastWhere(
        (a) => a.token != token && !used.contains(a.token),
        orElse: () => _items.last,
      );
      dropped.add(victim);
      _items = [
        for (final a in _items)
          if (!identical(a, victim)) a,
      ];
    }
    for (final d in dropped) {
      await storage.deleteFile(d.path);
    }
    await _write();
    return token;
  }

  /// Moves [token] to the front of "最近使用".
  Future<void> touch(String token) async {
    final e = _items.where((x) => x.token == token).firstOrNull;
    if (e == null) return;
    _items = [
      SavedAvatar(
        token: e.token,
        path: e.path,
        savedAtEpochMs: now().millisecondsSinceEpoch,
      ),
      for (final x in _items)
        if (x.token != token) x,
    ];
    await _write();
  }

  /// PNG bytes of an App avatar, or null when unknown / gone.
  Future<Uint8List?> bytes(String token) async {
    final e = _items.where((x) => x.token == token).firstOrNull;
    return e == null ? null : storage.readBytes(e.path);
  }

  /// Remembers the Kit's built-in avatar picture for [token].
  void putBuiltin(String token, Uint8List png) {
    _builtins[token] = png;
    notifyListeners();
  }

  /// Image of [token]: an App avatar file or a cached built-in picture;
  /// null when not available.
  ImageProvider? image(String token) {
    final builtin = _builtins[token];
    if (builtin != null) return MemoryImage(builtin);
    final e = _items.where((x) => x.token == token).firstOrNull;
    return e == null ? null : storage.thumbnailImage(e.path);
  }

  /// Loads the built-in pictures from [tools] (once).
  Future<void> loadBuiltins(VideoKitAvatarTools tools) async {
    for (var n = 1; n <= tools.builtinAvatarCount; n++) {
      final token = '${MaskAvatar.builtinPrefix}$n';
      if (_builtins.containsKey(token)) continue;
      try {
        _builtins[token] = await tools.builtinAvatar(n);
      } on Object {
        // A missing built-in is simply not offered.
      }
    }
    notifyListeners();
  }

  Future<void> _write() async {
    notifyListeners();
    await writeQuietly(
      storage,
      fileName,
      jsonEncode({
        'schema': 1,
        'counter': _counter,
        'avatars': [for (final a in _items) a.toJson()],
      }),
    );
  }
}

/// The avatar store is full of avatars kept projects use (04A E7 Q4).
final class AvatarStoreFullException implements Exception {
  /// Creates the exception.
  const AvatarStoreFullException();

  @override
  String toString() => 'AvatarStoreFullException';
}

/// Read handle over bytes in memory (the Kit reads avatars through
/// `openAvatar`, 04A E6 2).
final class BytesSourceFactory implements VideoKitSourceFactory {
  /// Wraps [bytes].
  BytesSourceFactory(this.bytes);

  /// Content.
  final Uint8List bytes;

  @override
  Future<VideoKitReadHandle> open(OpenPurpose purpose) async =>
      _BytesHandle(bytes);
}

final class _BytesHandle implements VideoKitReadHandle {
  _BytesHandle(this._bytes);

  final Uint8List _bytes;
  bool _closed = false;

  @override
  int? get length => _bytes.length;

  @override
  Future<int> readAt(
    int offset,
    Uint8List target,
    int targetOffset,
    int length,
  ) async {
    if (_closed) throw StateError('closed');
    if (offset >= _bytes.length) return -1;
    final n = length.clamp(0, _bytes.length - offset);
    target.setRange(targetOffset, targetOffset + n, _bytes, offset);
    return n;
  }

  @override
  Future<void> close() async => _closed = true;
}
