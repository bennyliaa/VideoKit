import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../picker/media_picker.dart';
import 'library_models.dart';
import 'library_platform.dart';
import 'library_store.dart';

/// Outcome of one picked item.
@immutable
final class ImportOutcome {
  /// Creates an outcome.
  const ImportOutcome(this.media, {this.item, this.failure});

  /// The picked document.
  final PickedMedia media;

  /// The library item, when imported.
  final LibraryItem? item;

  /// Why it failed (null: imported, or not reached because cancelled).
  final ImportFailure? failure;

  /// Imported.
  bool get ok => item != null;
}

/// Progress of an import ("正在导入 7 / 12 · 58%", design page 27).
@immutable
final class ImportProgress {
  /// Creates a progress value.
  const ImportProgress({
    required this.total,
    required this.done,
    required this.bytesTotal,
    required this.bytesDone,
    this.outcomes = const [],
    this.finished = false,
    this.cancelled = false,
    this.originalsDeleted = 0,
    this.originalsKept = 0,
  });

  /// Items picked.
  final int total;

  /// Items finished (imported or failed).
  final int done;

  /// Known total size (items without a size count 0).
  final int bytesTotal;

  /// Bytes copied so far.
  final int bytesDone;

  /// Outcomes so far, in pick order.
  final List<ImportOutcome> outcomes;

  /// All items handled (or cancelled).
  final bool finished;

  /// The user cancelled.
  final bool cancelled;

  /// Originals deleted after the system confirmation.
  final int originalsDeleted;

  /// Originals the user asked to delete but which were kept (refused in
  /// the system dialog, or not deletable).
  final int originalsKept;

  /// Imported items.
  int get imported => outcomes.where((o) => o.ok).length;

  /// Failed items.
  List<ImportOutcome> get failed => [
    for (final o in outcomes)
      if (o.failure != null) o,
  ];

  /// Item number shown ("正在导入 7 / 12"): the one being copied.
  int get current => finished ? done : (done + 1).clamp(1, total);

  /// 0–1 by bytes when sizes are known, else by items.
  double get fraction {
    if (total == 0) return 1;
    if (bytesTotal > 0) return (bytesDone / bytesTotal).clamp(0.0, 1.0);
    return done / total;
  }
}

/// Imports picked media into the library (REQ-APP-11): copies each item
/// to the private directory, probes it and makes its thumbnail; a failing
/// item is reported and the next one continues; cancelling keeps what is
/// done and leaves no partial copy. Originals are deleted only through the
/// system confirmation, and only those that were imported.
class LibraryImport extends ValueNotifier<ImportProgress> {
  /// Prepares the import of [media] into [folderId] (null = "未分类").
  LibraryImport({
    required this.store,
    required this.media,
    required this.folderId,
    this.deleteOriginals = false,
    this.folderIds,
    this.skipped = const [],
  }) : assert(folderIds == null || folderIds.length == media.length),
       super(
         ImportProgress(
           total: media.length,
           done: 0,
           bytesTotal: media.fold(0, (s, m) => s + (m.sizeBytes ?? 0)),
           bytesDone: 0,
         ),
       );

  /// Library.
  final LibraryStore store;

  /// Picked media.
  final List<PickedMedia> media;

  /// Target folder.
  final String? folderId;

  /// "导入整个文件夹": the folder of each item (parallel to [media]);
  /// overrides [folderId].
  final List<String?>? folderIds;

  /// "导入整个文件夹": non-media files that were not imported (reported).
  final List<String> skipped;

  /// "导入后删除手机里的原文件" (can change until the copy finishes).
  bool deleteOriginals;

  final Completer<void> _cancel = Completer<void>();
  bool _started = false;

  /// Counts for the header ("3 个视频、9 张图片").
  int get videoCount => media.where((m) => !m.kind.isImage).length;

  /// Images picked.
  int get imageCount => media.where((m) => m.kind.isImage).length;

  /// Cancels: the item being copied is dropped, later ones are not
  /// started; imported ones stay.
  void cancel() {
    if (!_cancel.isCompleted) _cancel.complete();
  }

  /// Runs the import once; completes when finished or cancelled.
  Future<ImportProgress> run() async {
    if (_started) return value;
    _started = true;
    final platform = store.platform;
    final dir = await platform.mediaDirectory();
    final outcomes = <ImportOutcome>[];
    var bytesDone = 0;
    for (final (index, m) in media.indexed) {
      if (_cancel.isCompleted) break;
      final targetFolder = folderIds?[index] ?? folderId;
      final id = store.newId('item');
      final dest = '$dir/$id${_extension(m)}';
      final base = bytesDone;
      // A known size larger than the free space fails at once.
      final free = await platform.freeBytes();
      final size = m.sizeBytes;
      CopyResult r;
      if (free != null && size != null && size > free) {
        r = const CopyResult.failed(ImportFailure.noSpace);
      } else {
        r = await platform.copy(
          m.uri,
          dest,
          cancel: _cancel.future,
          onProgress: (b) =>
              value = _progress(outcomes, base + b.clamp(0, size ?? b)),
        );
      }
      if (_cancel.isCompleted && !r.ok) {
        await platform.delete(dest);
        break;
      }
      if (!r.ok) {
        await platform.delete(dest);
        outcomes.add(ImportOutcome(m, failure: r.failure));
        bytesDone = base + (size ?? 0);
        value = _progress(outcomes, bytesDone);
        continue;
      }
      final probed = await platform.probe(dest, m.kind);
      if (probed == null) {
        await platform.delete(dest);
        outcomes.add(ImportOutcome(m, failure: ImportFailure.corrupt));
        bytesDone = base + (size ?? 0);
        value = _progress(outcomes, bytesDone);
        continue;
      }
      final thumbDest = '$dir/thumbs/$id.jpg';
      final thumbOk = await platform.thumbnail(dest, m.kind, thumbDest);
      final item = LibraryItem(
        id: id,
        path: dest,
        displayName: m.displayName,
        kind: m.kind,
        importedAtEpochMs: store.now().millisecondsSinceEpoch,
        folderId: targetFolder,
        mimeType: m.mimeType,
        sizeBytes: r.bytes,
        durationUs: m.kind.isImage ? null : probed.durationUs,
        width: probed.width,
        height: probed.height,
        thumbnailPath: thumbOk ? thumbDest : null,
      );
      await store.addItem(item);
      outcomes.add(ImportOutcome(m, item: item));
      bytesDone = base + (size ?? r.bytes);
      value = _progress(outcomes, bytesDone);
    }
    var deleted = 0;
    var kept = 0;
    if (deleteOriginals && !_cancel.isCompleted) {
      final uris = [
        for (final o in outcomes)
          if (o.ok) o.media.uri,
      ];
      if (uris.isNotEmpty) {
        final gone = await platform.deleteOriginals(uris);
        deleted = gone.length;
        kept = uris.length - gone.length;
      }
    }
    value = _progress(
      outcomes,
      bytesDone,
      finished: true,
      cancelled: _cancel.isCompleted,
      deleted: deleted,
      kept: kept,
    );
    return value;
  }

  ImportProgress _progress(
    List<ImportOutcome> outcomes,
    int bytesDone, {
    bool finished = false,
    bool cancelled = false,
    int deleted = 0,
    int kept = 0,
  }) => ImportProgress(
    total: media.length,
    done: outcomes.length,
    bytesTotal: value.bytesTotal,
    bytesDone: value.bytesTotal > 0
        ? bytesDone.clamp(0, value.bytesTotal)
        : bytesDone,
    outcomes: List.unmodifiable(outcomes),
    finished: finished,
    cancelled: cancelled,
    originalsDeleted: deleted,
    originalsKept: kept,
  );

  static String _extension(PickedMedia m) {
    final name = m.displayName;
    final dot = name.lastIndexOf('.');
    if (dot > 0 && dot >= name.length - 6) {
      final ext = name.substring(dot).toLowerCase();
      if (RegExp(r'^\.[a-z0-9]+$').hasMatch(ext)) return ext;
    }
    return switch (m.mimeType) {
      'video/mp4' => '.mp4',
      'video/quicktime' => '.mov',
      'video/x-matroska' => '.mkv',
      'video/webm' => '.webm',
      'image/jpeg' => '.jpg',
      'image/png' => '.png',
      'image/gif' => '.gif',
      'image/heic' => '.heic',
      'image/webp' => '.webp',
      _ => m.kind == MediaKind.video ? '.mp4' : '.img',
    };
  }
}
