import 'dart:io';

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
}

/// Files under the application support directory (path_provider).
final class FileAppStorage implements AppStorage {
  /// Uses the given directory, or the platform's application support directory.
  FileAppStorage([this._directory]);

  Directory? _directory;

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
  Future<void> write(String name, String content) async {
    final dir = await _dir();
    final tmp = File('${dir.path}/$name.tmp');
    await tmp.writeAsString(content, flush: true);
    await tmp.rename('${dir.path}/$name');
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
}

/// In-memory storage (tests, demo without a file system).
final class MemoryAppStorage implements AppStorage {
  /// Documents by name.
  final Map<String, String> documents = {};

  /// Deleted file paths, in order.
  final List<String> deleted = [];

  @override
  Future<String?> read(String name) async => documents[name];

  @override
  Future<void> write(String name, String content) async =>
      documents[name] = content;

  @override
  Future<void> deleteFile(String path) async => deleted.add(path);

  @override
  Future<String?> thumbnailDirectory() async => null;
}
