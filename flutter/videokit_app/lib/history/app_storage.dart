import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/foundation.dart' show debugPrint;
import 'package:flutter/painting.dart';
import 'package:path_provider/path_provider.dart';

/// App-private persistence (REQ-APP-08): small JSON documents and
/// thumbnail files. Nothing leaves the device.
abstract interface class AppStorage {
  /// Reads document [name] or null.
  Future<String?> read(String name);

  /// Writes document [name] atomically.
  Future<void> write(String name, String content);

  /// Deletes file [path] if it exists (thumbnails).
  Future<void> deleteFile(String path);

  /// Directory for thumbnails, or null when unavailable.
  Future<String?> thumbnailDirectory();

  /// Saves a small thumbnail [name] and returns its path.
  Future<String> writeThumbnail(String name, Uint8List bytes);

  /// Image for a stored thumbnail [path].
  ImageProvider thumbnailImage(String path);

  /// Saves avatar PNG [name] (REQ-ED-07, 04A E5 1: the host keeps the
  /// avatars) and returns its path.
  Future<String> writeAvatar(String name, Uint8List bytes);

  /// Bytes of a stored file [path] (avatars), or null when it is gone.
  Future<Uint8List?> readBytes(String path);
}

/// Files under the application support directory (path_provider).
final class FileAppStorage implements AppStorage {
  /// Uses the given directory, or the platform's application support
  /// directory.
  FileAppStorage([this._directory]);

  Directory? _directory;

  // TEST-R2 R2-02: writes of one file run one after another (latest content
  // last), each through its own temporary file.
  final Map<String, Future<void>> _queues = {};
  int _tmpCounter = 0;

  Future<Directory> _dir() async {
    final d = _directory ??= Directory(
      '${(await getApplicationSupportDirectory()).path}/videokit_app',
    );
    if (!d.existsSync()) await d.create(recursive: true);
    return d;
  }

  @override
  Future<String?> read(String name) async {
    final f = File('${(await _dir()).path}/$name');
    return f.existsSync() ? f.readAsString() : null;
  }

  @override
  Future<void> write(String name, String content) {
    final previous = _queues[name] ?? Future<void>.value();
    final next = previous
        .catchError((Object _) {})
        .then((_) => _writeNow(name, content));
    _queues[name] = next;
    return next.whenComplete(() {
      if (identical(_queues[name], next)) _queues.remove(name);
    });
  }

  Future<void> _writeNow(String name, String content) async {
    final dir = await _dir();
    final tmp = File('${dir.path}/$name.$pid-${++_tmpCounter}.tmp');
    try {
      await tmp.writeAsString(content, flush: true);
      await tmp.rename('${dir.path}/$name');
    } on Object {
      if (tmp.existsSync()) await tmp.delete();
      rethrow;
    }
  }

  @override
  Future<void> deleteFile(String path) async {
    final f = File(path);
    if (f.existsSync()) await f.delete();
  }

  @override
  Future<String?> thumbnailDirectory() async {
    final d = Directory('${(await _dir()).path}/thumbnails');
    if (!d.existsSync()) await d.create(recursive: true);
    return d.path;
  }

  @override
  Future<String> writeThumbnail(String name, Uint8List bytes) async {
    final dir = (await thumbnailDirectory())!;
    final f = File('$dir/$name');
    await f.writeAsBytes(bytes, flush: true);
    return f.path;
  }

  @override
  ImageProvider thumbnailImage(String path) => FileImage(File(path));

  @override
  Future<String> writeAvatar(String name, Uint8List bytes) async {
    final d = Directory('${(await _dir()).path}/avatars');
    if (!d.existsSync()) await d.create(recursive: true);
    final f = File('${d.path}/$name');
    await f.writeAsBytes(bytes, flush: true);
    return f.path;
  }

  @override
  Future<Uint8List?> readBytes(String path) async {
    final f = File(path);
    return f.existsSync() ? f.readAsBytes() : null;
  }
}

/// In-memory storage (tests, demo without a file system).
final class MemoryAppStorage implements AppStorage {
  /// Documents by name.
  final Map<String, String> documents = {};

  /// Thumbnails by path.
  final Map<String, Uint8List> thumbnails = {};

  /// Deleted file paths, in order.
  final List<String> deleted = [];

  @override
  Future<String?> read(String name) async => documents[name];

  @override
  Future<void> write(String name, String content) async =>
      documents[name] = content;

  @override
  Future<void> deleteFile(String path) async {
    deleted.add(path);
    thumbnails.remove(path);
  }

  @override
  Future<String?> thumbnailDirectory() async => null;

  @override
  Future<String> writeThumbnail(String name, Uint8List bytes) async {
    final path = 'memory:$name';
    thumbnails[path] = bytes;
    return path;
  }

  @override
  ImageProvider thumbnailImage(String path) =>
      MemoryImage(thumbnails[path] ?? Uint8List(0));

  @override
  Future<String> writeAvatar(String name, Uint8List bytes) async {
    final path = 'memory:avatars/$name';
    thumbnails[path] = bytes;
    return path;
  }

  @override
  Future<Uint8List?> readBytes(String path) async => thumbnails[path];
}

/// Writes [content] to [name] and only logs a failure (TEST-R2 R2-02): a
/// record that could not be saved must not interrupt opening or playing.
/// The log names the file and the error type, never media names or paths.
Future<void> writeQuietly(
  AppStorage storage,
  String name,
  String content,
) async {
  try {
    await storage.write(name, content);
  } on Object catch (e) {
    debugPrint('VideoKitApp: saving $name failed (${e.runtimeType})');
  }
}
