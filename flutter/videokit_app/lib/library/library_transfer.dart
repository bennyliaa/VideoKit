import 'dart:async';

import 'package:flutter/foundation.dart';

import 'library_models.dart';
import 'library_platform.dart';
import 'library_store.dart';

/// Where a transfer takes the media (REQ-APP-14).
enum TransferTarget {
  /// "导出到相册": copies into the system gallery; library items stay.
  gallery,

  /// "移动到文件夹": copies into a picked directory (one sub-directory per
  /// library folder), verifies each copy, then removes it from the library.
  directory,
}

/// Outcome of one item.
@immutable
final class TransferOutcome {
  /// Creates an outcome.
  const TransferOutcome(this.item, [this.failure]);

  /// The library item.
  final LibraryItem item;

  /// Why it failed; null = done.
  final TransferFailure? failure;

  /// Done.
  bool get ok => failure == null;
}

/// Progress of a transfer.
@immutable
final class TransferProgress {
  /// Creates a value.
  const TransferProgress({
    required this.total,
    this.outcomes = const [],
    this.finished = false,
    this.cancelled = false,
  });

  /// Items to transfer.
  final int total;

  /// Outcomes so far, in order.
  final List<TransferOutcome> outcomes;

  /// All handled or cancelled.
  final bool finished;

  /// The user cancelled.
  final bool cancelled;

  /// Items handled.
  int get done => outcomes.length;

  /// Items done successfully.
  int get succeeded => outcomes.where((o) => o.ok).length;

  /// Failed items (a cancelled in-flight item is not a failure).
  List<TransferOutcome> get failed => [
    for (final o in outcomes)
      if (!o.ok && o.failure != TransferFailure.cancelled) o,
  ];

  /// Item number shown ("正在导出 3 / 12").
  int get current => finished ? done : (done + 1).clamp(1, total);

  /// 0–1 by items.
  double get fraction => total == 0 ? 1 : done / total;
}

/// Export to the gallery or move out to a directory (REQ-APP-14), item by
/// item; a failing item is reported and the next goes on; cancelling stops
/// after (or inside) the current item without leaving a partial file. In
/// [TransferTarget.directory] an item leaves the library only after its
/// copy was verified (size and SHA-256), so an interrupted move keeps
/// every unverified item in the library.
class LibraryTransfer extends ValueNotifier<TransferProgress> {
  /// Prepares the transfer of [items].
  LibraryTransfer({
    required this.store,
    required this.items,
    required this.target,
    this.treeUri,
    required this.folderNameOf,
  }) : assert(target == TransferTarget.gallery || treeUri != null),
       super(TransferProgress(total: items.length));

  /// Library.
  final LibraryStore store;

  /// Items (whole folders when the selection says so).
  final List<LibraryItem> items;

  /// Gallery or directory.
  final TransferTarget target;

  /// Picked directory ([TransferTarget.directory]).
  final String? treeUri;

  /// Sub-directory name for an item (its library folder; "未分类" for
  /// items without one).
  final String Function(LibraryItem item) folderNameOf;

  final Completer<void> _cancel = Completer<void>();
  bool _started = false;

  /// Cancels.
  void cancel() {
    if (!_cancel.isCompleted) _cancel.complete();
  }

  /// Runs once.
  Future<TransferProgress> run() async {
    if (_started) return value;
    _started = true;
    final platform = store.platform;
    final outcomes = <TransferOutcome>[];
    final dirs = <String, String?>{};
    final taken = <String, Set<String>>{};
    void report() => value = TransferProgress(
      total: items.length,
      outcomes: List.unmodifiable(outcomes),
    );
    for (final item in items) {
      if (_cancel.isCompleted) break;
      TransferFailure? failure;
      if (target == TransferTarget.gallery) {
        failure = await platform.exportToGallery(
          item.path,
          displayName: item.displayName,
          kind: item.kind,
          mimeType: item.mimeType,
        );
      } else {
        final folder = folderNameOf(item);
        final dir = dirs.containsKey(folder)
            ? dirs[folder]
            : dirs[folder] = await platform.ensureDirectory(treeUri!, folder);
        if (dir == null) {
          failure = TransferFailure.unwritable;
        } else {
          final name = uniqueName(item.displayName, taken[dir] ??= {});
          failure = await platform.copyToDirectory(
            item.path,
            dir,
            name,
            mimeType: item.mimeType,
            cancel: _cancel.future,
          );
          // Verified: only now does it leave the library.
          if (failure == null) await store.deleteItems([item.id]);
        }
      }
      outcomes.add(TransferOutcome(item, failure));
      report();
    }
    value = TransferProgress(
      total: items.length,
      outcomes: List.unmodifiable(outcomes),
      finished: true,
      cancelled: _cancel.isCompleted,
    );
    return value;
  }

  /// [name] made unique within one target directory of this run
  /// ("a.mp4", "a (2).mp4"); the native side also refuses to overwrite.
  static String uniqueName(String name, Set<String> taken) {
    var candidate = name;
    final dot = name.lastIndexOf('.');
    final base = dot > 0 ? name.substring(0, dot) : name;
    final ext = dot > 0 ? name.substring(dot) : '';
    for (var n = 2; taken.contains(candidate.toLowerCase()); n++) {
      candidate = '$base ($n)$ext';
    }
    taken.add(candidate.toLowerCase());
    return candidate;
  }
}
