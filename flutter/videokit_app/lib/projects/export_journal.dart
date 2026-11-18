import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../history/app_storage.dart';

/// An export that was running when the App stopped (M6-A1, 08 §6 "进程终止").
@immutable
final class InterruptedExport {
  /// Creates an entry.
  const InterruptedExport({
    required this.projectId,
    required this.startedAtEpochMs,
  });

  /// "最近工程" ID of the project being exported.
  final String projectId;

  /// When the export started.
  final int startedAtEpochMs;
}

/// Remembers the export in progress (App business, 04A M6 ruling 5): set
/// when an export starts, cleared when it ends. An entry still there at the
/// next start means the App was killed during the export: the home page
/// says so (the source is untouched, the unfinished output is discarded)
/// and offers to export again. Only one export runs at a time.
class ExportJournal extends ChangeNotifier {
  /// Creates the journal.
  ExportJournal({required this.storage, DateTime Function()? now})
    : now = now ?? DateTime.now;

  /// Storage.
  final AppStorage storage;

  /// Clock.
  final DateTime Function() now;

  /// File name.
  static const String fileName = 'export_journal.json';

  InterruptedExport? _interrupted;
  String? _running;

  /// An export interrupted in an earlier run, until dismissed.
  InterruptedExport? get interrupted => _interrupted;

  /// Reads what an earlier run left (call once at start-up).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final j = jsonDecode(raw) as Map<String, Object?>;
      final id = j['projectId'];
      final at = j['startedAtEpochMs'];
      if (id is String && at is num) {
        _interrupted = InterruptedExport(
          projectId: id,
          startedAtEpochMs: at.toInt(),
        );
      }
    } on Object {
      _interrupted = null;
    }
    notifyListeners();
  }

  /// An export of [projectId] starts.
  Future<void> begin(String projectId) async {
    _running = projectId;
    await writeQuietly(
      storage,
      fileName,
      jsonEncode({
        'projectId': projectId,
        'startedAtEpochMs': now().millisecondsSinceEpoch,
      }),
    );
  }

  /// The export of [projectId] ended (completed, failed or cancelled).
  Future<void> end(String projectId) async {
    if (_running != projectId) return;
    _running = null;
    await writeQuietly(storage, fileName, '{}');
  }

  /// The user has seen the notice.
  Future<void> dismiss() async {
    _interrupted = null;
    notifyListeners();
    if (_running == null) await writeQuietly(storage, fileName, '{}');
  }
}
