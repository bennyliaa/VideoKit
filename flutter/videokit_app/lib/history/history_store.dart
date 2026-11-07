import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../picker/media_picker.dart';
import 'app_storage.dart';
import 'history_entry.dart';

/// Play history of the App (REQ-APP-07/08): newest first, at most [limit]
/// entries, stored only in the app-private directory. Removing entries
/// (single, eviction past the limit, clear) also deletes their thumbnails
/// and releases their long-term permission.
class HistoryStore extends ChangeNotifier {
  /// Creates a store.
  HistoryStore({
    required this.storage,
    required this.picker,
    DateTime Function()? now,
  }) : now = now ?? DateTime.now;

  /// Record limit.
  static const int limit = 200;

  /// Document name.
  static const String fileName = 'history.json';

  /// Storage.
  final AppStorage storage;

  /// Picker (permission release).
  final MediaPickerService picker;

  /// Clock (tests).
  final DateTime Function() now;

  List<HistoryEntry> _entries = const [];
  int _counter = 0;

  /// Entries, newest first.
  List<HistoryEntry> get entries => _entries;

  /// Loads the saved history; broken files start empty (never fatal).
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      final json = jsonDecode(raw) as Map<String, Object?>;
      final list = (json['entries'] as List<Object?>? ?? const [])
          .cast<Map<String, Object?>>();
      _entries = [for (final e in list) ?_tryParse(e)];
      _counter = (json['counter'] as num?)?.toInt() ?? _entries.length;
    } on Object {
      _entries = const [];
    }
    notifyListeners();
  }

  static HistoryEntry? _tryParse(Map<String, Object?> e) {
    try {
      return HistoryEntry.fromJson(e);
    } on Object {
      return null;
    }
  }

  Future<void> _save() async {
    notifyListeners();
    await storage.write(
      fileName,
      jsonEncode({
        'schema': 1,
        'counter': _counter,
        'entries': [for (final e in _entries) e.toJson()],
      }),
    );
  }

  /// Entry with [id].
  HistoryEntry? byId(String id) =>
      _entries.where((e) => e.id == id).firstOrNull;

  /// Records [media] as opened now (one entry per file, REQ-APP-07) and
  /// returns it; an existing entry for the same URI moves to the top.
  Future<HistoryEntry> recordOpened(PickedMedia media) async {
    final existing = _entries.where((e) => e.uri == media.uri).firstOrNull;
    final at = now().millisecondsSinceEpoch;
    final entry =
        existing?.copyWith(
          displayName: media.displayName,
          lastOpenedAtEpochMs: at,
          persistable: media.persistable,
          unavailable: false,
        ) ??
        HistoryEntry(
          id: 'h${++_counter}',
          uri: media.uri,
          displayName: media.displayName,
          kind: media.kind,
          mimeType: media.mimeType,
          lastOpenedAtEpochMs: at,
          persistable: media.persistable,
        );
    _entries = [
      entry,
      for (final e in _entries)
        if (e.id != entry.id) e,
    ];
    await _evict();
    await _save();
    return entry;
  }

  Future<void> _evict() async {
    if (_entries.length <= limit) return;
    final dropped = _entries.sublist(limit);
    _entries = _entries.sublist(0, limit);
    for (final e in dropped) {
      await _forget(e);
    }
  }

  Future<void> _forget(HistoryEntry e) async {
    final thumb = e.thumbnailPath;
    if (thumb != null) await storage.deleteFile(thumb);
    if (e.persistable) await picker.releaseAccess(e.uri);
  }

  /// Updates [id] after a session: snapshot from `captureState()`, media
  /// facts reported by the session.
  Future<void> updatePlayback(
    String id, {
    VideoKitPlaybackState? snapshot,
    int? positionUs,
    int? durationUs,
    int? width,
    int? height,
    MediaKind? kind,
    String? videoCodec,
    String? mimeType,
    String? thumbnailPath,
  }) async {
    final e = byId(id);
    if (e == null) {
      // Not recorded (history off): drop the orphan thumbnail.
      if (thumbnailPath != null) await storage.deleteFile(thumbnailPath);
      return;
    }
    final old = e.thumbnailPath;
    if (thumbnailPath != null && old != null && old != thumbnailPath) {
      await storage.deleteFile(old);
    }
    _replace(
      e.copyWith(
        playbackState: snapshot,
        // Images have no resume position (an animated image keeps its
        // snapshot only for looping, 04A L3).
        lastPositionUs: (kind ?? e.kind).isImage
            ? null
            : positionUs ?? snapshot?.positionUs,
        durationUs: durationUs,
        width: width,
        height: height,
        kind: kind,
        videoCodec: videoCodec,
        mimeType: mimeType,
        thumbnailPath: thumbnailPath,
      ),
    );
    await _save();
  }

  /// Clears the resume position ("从头播放").
  Future<void> resetPosition(String id) async {
    final e = byId(id);
    if (e == null) return;
    _replace(e.copyWith(clearPlayback: true));
    await _save();
  }

  /// Marks [id] as not openable (moved, deleted, revoked).
  Future<void> markUnavailable(String id) async {
    final e = byId(id);
    if (e == null || e.unavailable) return;
    _replace(e.copyWith(unavailable: true));
    await _save();
  }

  /// Sets the favourite flag of [id] (App host action "收藏", M2).
  Future<HistoryEntry?> setFavorite(String id, bool favorite) async {
    final e = byId(id);
    if (e == null) return null;
    final next = e.copyWith(favorite: favorite);
    _replace(next);
    await _save();
    return next;
  }

  /// Replaces the tags of [id] (trimmed, empty and duplicate tags dropped).
  Future<HistoryEntry?> setTags(String id, List<String> tags) async {
    final e = byId(id);
    if (e == null) return null;
    final clean = <String>[];
    for (final t in tags) {
      final v = t.trim();
      if (v.isNotEmpty && !clean.contains(v)) clean.add(v);
    }
    final next = e.copyWith(tags: List.unmodifiable(clean));
    _replace(next);
    await _save();
    return next;
  }

  /// Points [id] at a re-selected file ("重新选择").
  Future<HistoryEntry?> relink(String id, PickedMedia media) async {
    final e = byId(id);
    if (e == null) return null;
    if (e.uri != media.uri && e.persistable) {
      await picker.releaseAccess(e.uri);
    }
    final next = e.copyWith(
      uri: media.uri,
      displayName: media.displayName,
      persistable: media.persistable,
      unavailable: false,
      lastOpenedAtEpochMs: now().millisecondsSinceEpoch,
    );
    _entries = [
      next,
      for (final x in _entries)
        if (x.id != id) x,
    ];
    await _save();
    return next;
  }

  void _replace(HistoryEntry e) {
    _entries = [for (final x in _entries) x.id == e.id ? e : x];
  }

  /// Deletes one record (thumbnail and permission released).
  Future<void> remove(String id) async {
    final e = byId(id);
    if (e == null) return;
    _entries = [
      for (final x in _entries)
        if (x.id != id) x,
    ];
    await _forget(e);
    await _save();
  }

  /// Deletes everything (REQ-APP-08).
  Future<void> clear() async {
    final all = _entries;
    _entries = const [];
    for (final e in all) {
      await _forget(e);
    }
    await _save();
  }
}
