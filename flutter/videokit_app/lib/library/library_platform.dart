import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:videokit_api/videokit_api.dart';

/// Why one import item failed (REQ-APP-11: reported per item).
enum ImportFailure {
  /// Not enough free space for this item.
  noSpace,

  /// The source could not be read (moved, permission lost, I/O error).
  unreadable,

  /// Read, but not a usable video / image (corrupt).
  corrupt,

  /// Anything else.
  other,
}

/// Result of copying one item.
@immutable
final class CopyResult {
  /// Success: [bytes] written to the private file.
  const CopyResult.ok(this.bytes) : failure = null;

  /// Failure.
  const CopyResult.failed(ImportFailure this.failure) : bytes = 0;

  /// Bytes written.
  final int bytes;

  /// Failure, or null on success.
  final ImportFailure? failure;

  /// Whether the copy succeeded.
  bool get ok => failure == null;
}

/// Metadata of a private file (after import).
@immutable
final class ProbedMedia {
  /// Creates a probe result.
  const ProbedMedia({this.durationUs, this.width, this.height});

  /// Video duration (µs).
  final int? durationUs;

  /// Pixel width.
  final int? width;

  /// Pixel height.
  final int? height;
}

/// Result of a biometric or device-credential prompt.
enum AuthResult {
  /// Verified.
  success,

  /// The user cancelled (or chose the PIN instead).
  cancelled,

  /// Not available on this device (no hardware, nothing enrolled, no
  /// screen lock).
  unavailable,

  /// Failed (too many attempts, error).
  failed,
}

/// What the media library needs from the device (REQ-APP-09–11; native
/// side `com.videokit.app/library` in the App's android directory). The
/// library logic stays in Dart; this only moves bytes and asks the system.
abstract interface class LibraryPlatform {
  /// Absolute directory of the private media copies.
  Future<String> mediaDirectory();

  /// Free bytes on the private storage, or null when unknown.
  Future<int?> freeBytes();

  /// Copies [uri] to the private file [dest]; [onProgress] gets the bytes
  /// copied so far. Completes with a failure (never throws) and leaves no
  /// partial file. [cancel] completing stops the copy (result `other`, no
  /// partial file).
  Future<CopyResult> copy(
    String uri,
    String dest, {
    void Function(int bytes)? onProgress,
    Future<void>? cancel,
  });

  /// Duration and size of a private file; null when unreadable (corrupt).
  Future<ProbedMedia?> probe(String path, MediaKind kind);

  /// Writes a small thumbnail of [path] to [dest]; false when it fails.
  Future<bool> thumbnail(String path, MediaKind kind, String dest);

  /// Deletes a private file (missing is fine).
  Future<void> delete(String path);

  /// "导入后删除原文件": asks the system to delete [uris]
  /// (`MediaStore.createDeleteRequest`, the system shows its own
  /// confirmation). Returns the URIs actually deleted: empty when the user
  /// refused, or for documents the system cannot delete this way.
  Future<Set<String>> deleteOriginals(List<String> uris);

  /// Biometric unlock is possible (hardware + enrolled).
  Future<bool> canUseBiometrics();

  /// System BiometricPrompt.
  Future<AuthResult> authenticateBiometric({
    required String title,
    required String negative,
  });

  /// Whether the device has a screen lock (for "忘记密码").
  Future<bool> hasDeviceCredential();

  /// System screen-lock check (PIN / pattern / password of the device).
  Future<AuthResult> confirmDeviceCredential({required String title});

  /// `FLAG_SECURE` on the App window (library pages: no screenshots, no
  /// picture in the recents screen).
  Future<void> setSecure(bool secure);

  // ------------------------------------------------- REQ-APP-14 / 13 ---

  /// "导出到相册": writes a copy of the private file [path] into the
  /// system gallery through MediaStore (videos `Movies/VideoKit`, images
  /// `Pictures/VideoKit`); the library item stays. Null on success.
  Future<TransferFailure?> exportToGallery(
    String path, {
    required String displayName,
    required MediaKind kind,
    String? mimeType,
  });

  /// System directory picker (`ACTION_OPEN_DOCUMENT_TREE`, persistable
  /// read/write); the tree URI, or null when cancelled.
  Future<String?> pickDirectory();

  /// Sub-directory [name] of the tree (found or created); its document
  /// URI, or null when it cannot be created (unplugged, read-only).
  Future<String?> ensureDirectory(String treeUri, String name);

  /// Copies the private file [path] into directory [dirUri] as [name],
  /// then reads the copy back and compares size and SHA-256 with the
  /// source. A failure (or [cancel]) leaves no partial document. Null on a
  /// verified copy.
  Future<TransferFailure?> copyToDirectory(
    String path,
    String dirUri,
    String name, {
    String? mimeType,
    Future<void>? cancel,
  });

  /// Lists a picked directory for "导入整个文件夹": its name and every
  /// file below it with its directory path relative to the root (`''` for
  /// the root itself, `a/b` for nested ones). Null when unreadable.
  Future<TreeListing?> listTree(String treeUri);
}

/// Why one export / move-out item failed (REQ-APP-14).
enum TransferFailure {
  /// Not enough space at the target.
  noSpace,

  /// The private file could not be read.
  unreadable,

  /// The target could not be written (unplugged, read-only, revoked).
  unwritable,

  /// The copy read back differs in size or SHA-256.
  mismatch,

  /// Cancelled while this item was copied (no partial file left).
  cancelled,

  /// Anything else.
  other,
}

/// One file of a listed directory tree.
@immutable
final class TreeEntry {
  /// Creates an entry.
  const TreeEntry({
    required this.dir,
    required this.uri,
    required this.name,
    this.mimeType,
    this.sizeBytes,
  });

  /// Directory relative to the picked root (`''` = the root).
  final String dir;

  /// Document URI.
  final String uri;

  /// File name.
  final String name;

  /// MIME type as the provider reports it.
  final String? mimeType;

  /// Size, if known.
  final int? sizeBytes;
}

/// A listed directory tree.
@immutable
final class TreeListing {
  /// Creates a listing.
  const TreeListing({required this.name, required this.entries});

  /// Name of the picked directory.
  final String name;

  /// Files below it (all depths).
  final List<TreeEntry> entries;
}

/// [LibraryPlatform] over the App's channel. Without the native handler
/// (tests on the host) calls fail softly: copies fail as `other`, prompts
/// report `unavailable`.
final class ChannelLibraryPlatform implements LibraryPlatform {
  /// Creates the platform on [methods].
  ChannelLibraryPlatform({
    this.methods = const MethodChannel(channelName),
  }) {
    methods.setMethodCallHandler(_onCall);
  }

  /// Channel name (native: `LibraryChannel.kt`).
  static const String channelName = 'com.videokit.app/library';

  /// Channel.
  final MethodChannel methods;

  int _jobs = 0;
  final Map<int, void Function(int)> _progress = {};

  Future<Object?> _onCall(MethodCall call) async {
    if (call.method == 'progress') {
      final a = call.arguments as Map<Object?, Object?>;
      final job = (a['job']! as num).toInt();
      _progress[job]?.call((a['bytes']! as num).toInt());
    }
    return null;
  }

  Future<T?> _call<T>(String method, [Map<String, Object?>? args]) async {
    try {
      return await methods.invokeMethod<T>(method, args);
    } on MissingPluginException {
      return null;
    } on PlatformException {
      return null;
    }
  }

  @override
  Future<String> mediaDirectory() async =>
      await _call<String>('mediaDirectory') ?? '';

  @override
  Future<int?> freeBytes() async => (await _call<num>('freeBytes'))?.toInt();

  @override
  Future<CopyResult> copy(
    String uri,
    String dest, {
    void Function(int bytes)? onProgress,
    Future<void>? cancel,
  }) async {
    final job = ++_jobs;
    if (onProgress != null) _progress[job] = onProgress;
    unawaited(
      cancel?.then((_) => _call<void>('cancelCopy', {'job': job})),
    );
    try {
      final r = await methods.invokeMethod<Map<Object?, Object?>>('copy', {
        'job': job,
        'uri': uri,
        'dest': dest,
      });
      final failure = r?['failure'] as String?;
      if (failure != null) {
        return CopyResult.failed(
          ImportFailure.values.where((f) => f.name == failure).firstOrNull ??
              ImportFailure.other,
        );
      }
      return CopyResult.ok((r?['bytes'] as num?)?.toInt() ?? 0);
    } on MissingPluginException {
      return const CopyResult.failed(ImportFailure.other);
    } on PlatformException {
      return const CopyResult.failed(ImportFailure.other);
    } finally {
      _progress.remove(job);
    }
  }

  @override
  Future<ProbedMedia?> probe(String path, MediaKind kind) async {
    final r = await _call<Map<Object?, Object?>>('probe', {
      'path': path,
      'image': kind.isImage,
    });
    if (r == null) return null;
    int? n(String k) => (r[k] as num?)?.toInt();
    return ProbedMedia(
      durationUs: n('durationUs'),
      width: n('width'),
      height: n('height'),
    );
  }

  @override
  Future<bool> thumbnail(String path, MediaKind kind, String dest) async =>
      await _call<bool>('thumbnail', {
        'path': path,
        'image': kind.isImage,
        'dest': dest,
      }) ??
      false;

  @override
  Future<void> delete(String path) => _call<void>('delete', {'path': path});

  @override
  Future<Set<String>> deleteOriginals(List<String> uris) async {
    final r = await _call<List<Object?>>('deleteOriginals', {'uris': uris});
    return {for (final u in r ?? const <Object?>[]) if (u is String) u};
  }

  @override
  Future<bool> canUseBiometrics() async =>
      await _call<bool>('canUseBiometrics') ?? false;

  AuthResult _auth(String? r) =>
      AuthResult.values.where((a) => a.name == r).firstOrNull ??
      AuthResult.unavailable;

  @override
  Future<AuthResult> authenticateBiometric({
    required String title,
    required String negative,
  }) async => _auth(
    await _call<String>('authenticateBiometric', {
      'title': title,
      'negative': negative,
    }),
  );

  @override
  Future<bool> hasDeviceCredential() async =>
      await _call<bool>('hasDeviceCredential') ?? false;

  @override
  Future<AuthResult> confirmDeviceCredential({required String title}) async =>
      _auth(await _call<String>('confirmDeviceCredential', {'title': title}));

  @override
  Future<void> setSecure(bool secure) =>
      _call<void>('setSecure', {'secure': secure});

  TransferFailure? _transfer(Object? r) {
    if (r == 'ok') return null;
    return TransferFailure.values.where((f) => f.name == r).firstOrNull ??
        TransferFailure.other;
  }

  @override
  Future<TransferFailure?> exportToGallery(
    String path, {
    required String displayName,
    required MediaKind kind,
    String? mimeType,
  }) async => _transfer(
    await _call<String>('exportToGallery', {
      'path': path,
      'name': displayName,
      'image': kind.isImage,
      'mimeType': mimeType,
    }),
  );

  @override
  Future<String?> pickDirectory() => _call<String>('pickDirectory');

  @override
  Future<String?> ensureDirectory(String treeUri, String name) =>
      _call<String>('ensureDirectory', {'tree': treeUri, 'name': name});

  @override
  Future<TransferFailure?> copyToDirectory(
    String path,
    String dirUri,
    String name, {
    String? mimeType,
    Future<void>? cancel,
  }) async {
    final job = ++_jobs;
    unawaited(
      cancel?.then((_) => _call<void>('cancelCopy', {'job': job})),
    );
    return _transfer(
      await _call<String>('copyToDirectory', {
        'job': job,
        'path': path,
        'dir': dirUri,
        'name': name,
        'mimeType': mimeType,
      }),
    );
  }

  @override
  Future<TreeListing?> listTree(String treeUri) async {
    final r = await _call<Map<Object?, Object?>>('listTree', {
      'tree': treeUri,
    });
    if (r == null) return null;
    return TreeListing(
      name: r['name'] as String? ?? '',
      entries: [
        for (final e in r['entries'] as List<Object?>? ?? const [])
          if (e is Map<Object?, Object?>)
            TreeEntry(
              dir: e['dir'] as String? ?? '',
              uri: e['uri']! as String,
              name: e['name'] as String? ?? '',
              mimeType: e['mimeType'] as String?,
              sizeBytes: (e['size'] as num?)?.toInt(),
            ),
      ],
    );
  }
}

/// In-memory [LibraryPlatform] for the demo backend and tests: "files" are
/// byte counts in a map; tests script failures and prompt answers.
final class DemoLibraryPlatform implements LibraryPlatform {
  /// Private files: path → size.
  final Map<String, int> files = {};

  /// Source sizes by URI (unknown URIs: 4 MB).
  final Map<String, int> sourceSizes = {};

  /// URIs whose copy fails, and why.
  final Map<String, ImportFailure> failures = {};

  /// URIs whose copy succeeds but probing fails (corrupt).
  final Set<String> corrupt = {};

  /// Free space; null = unknown.
  int? free = 64 * 1024 * 1024 * 1024;

  /// Delay per copied item (tests make copies slow to cancel them).
  Duration copyDelay = Duration.zero;

  /// Answer of the system delete confirmation.
  bool confirmDelete = true;

  /// URIs the system deleted.
  final List<String> deletedOriginals = [];

  /// Biometrics available.
  bool biometrics = true;

  /// Answer of the biometric prompt.
  AuthResult biometricAnswer = AuthResult.success;

  /// Device has a screen lock.
  bool deviceCredential = true;

  /// Answer of the screen-lock check.
  AuthResult credentialAnswer = AuthResult.success;

  /// `FLAG_SECURE` as last set.
  bool secure = false;

  /// Thumbnails written.
  final Set<String> thumbnails = {};

  final Map<String, String> _sourceOf = {};

  @override
  Future<String> mediaDirectory() async => 'memory:library';

  @override
  Future<int?> freeBytes() async => free;

  @override
  Future<CopyResult> copy(
    String uri,
    String dest, {
    void Function(int bytes)? onProgress,
    Future<void>? cancel,
  }) async {
    var cancelled = false;
    unawaited(cancel?.then((_) => cancelled = true));
    final size = sourceSizes[uri] ?? 4 * 1024 * 1024;
    if (copyDelay > Duration.zero) await Future<void>.delayed(copyDelay);
    if (cancelled) return const CopyResult.failed(ImportFailure.other);
    final failure = failures[uri];
    if (failure != null) return CopyResult.failed(failure);
    final f = free;
    if (f != null && f < size) {
      return const CopyResult.failed(ImportFailure.noSpace);
    }
    onProgress?.call(size ~/ 2);
    onProgress?.call(size);
    files[dest] = size;
    _sourceOf[dest] = uri;
    if (f != null) free = f - size;
    return CopyResult.ok(size);
  }

  @override
  Future<ProbedMedia?> probe(String path, MediaKind kind) async {
    if (!files.containsKey(path) || corrupt.contains(_sourceOf[path])) {
      return null;
    }
    return kind.isImage
        ? const ProbedMedia(width: 4032, height: 3024)
        : const ProbedMedia(
            durationUs: 134000000,
            width: 1920,
            height: 1080,
          );
  }

  @override
  Future<bool> thumbnail(String path, MediaKind kind, String dest) async {
    if (!files.containsKey(path)) return false;
    thumbnails.add(dest);
    return true;
  }

  @override
  Future<void> delete(String path) async {
    final size = files.remove(path);
    final f = free;
    if (size != null && f != null) free = f + size;
  }

  @override
  Future<Set<String>> deleteOriginals(List<String> uris) async {
    if (!confirmDelete) return const {};
    deletedOriginals.addAll(uris);
    return uris.toSet();
  }

  @override
  Future<bool> canUseBiometrics() async => biometrics;

  @override
  Future<AuthResult> authenticateBiometric({
    required String title,
    required String negative,
  }) async => biometrics ? biometricAnswer : AuthResult.unavailable;

  @override
  Future<bool> hasDeviceCredential() async => deviceCredential;

  @override
  Future<AuthResult> confirmDeviceCredential({required String title}) async =>
      deviceCredential ? credentialAnswer : AuthResult.unavailable;

  @override
  Future<void> setSecure(bool secure) async => this.secure = secure;

  /// Gallery: display names written, in order.
  final List<String> gallery = [];

  /// Free space of the gallery volume; null = unknown.
  int? galleryFree;

  /// Picked directory tree URI (null = cancelled).
  String? pickedTree = 'tree:demo';

  /// Directories by tree URI → name → dir URI.
  final Map<String, Set<String>> directories = {};

  /// Copied documents: dir URI/name → size.
  final Map<String, int> treeFiles = {};

  /// Target directories that cannot be written ("unplugged").
  final Set<String> unwritableDirs = {};

  /// Names whose read-back verification fails.
  final Set<String> mismatching = {};

  /// Free space at the move-out target; null = unknown.
  int? treeFree;

  /// Listing returned for [listTree].
  TreeListing? listing;

  @override
  Future<TransferFailure?> exportToGallery(
    String path, {
    required String displayName,
    required MediaKind kind,
    String? mimeType,
  }) async {
    final size = files[path];
    if (size == null) return TransferFailure.unreadable;
    final f = galleryFree;
    if (f != null && f < size) return TransferFailure.noSpace;
    if (f != null) galleryFree = f - size;
    gallery.add(displayName);
    return null;
  }

  @override
  Future<String?> pickDirectory() async => pickedTree;

  @override
  Future<String?> ensureDirectory(String treeUri, String name) async {
    final dir = '$treeUri/$name';
    if (unwritableDirs.contains(dir)) return null;
    (directories[treeUri] ??= {}).add(name);
    return dir;
  }

  @override
  Future<TransferFailure?> copyToDirectory(
    String path,
    String dirUri,
    String name, {
    String? mimeType,
    Future<void>? cancel,
  }) async {
    var cancelled = false;
    unawaited(cancel?.then((_) => cancelled = true));
    if (copyDelay > Duration.zero) await Future<void>.delayed(copyDelay);
    if (cancelled) return TransferFailure.cancelled;
    final size = files[path];
    if (size == null) return TransferFailure.unreadable;
    if (unwritableDirs.contains(dirUri)) return TransferFailure.unwritable;
    final f = treeFree;
    if (f != null && f < size) return TransferFailure.noSpace;
    if (mismatching.contains(name)) return TransferFailure.mismatch;
    if (f != null) treeFree = f - size;
    treeFiles['$dirUri/$name'] = size;
    return null;
  }

  @override
  Future<TreeListing?> listTree(String treeUri) async => listing;
}
