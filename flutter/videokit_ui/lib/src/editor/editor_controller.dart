import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_sheet_host.dart';
import '../l10n/vk_strings.dart';
import 'timeline_scale.dart';

/// Editor work areas (design page 16 bottom navigation).
enum EditorMode {
  /// Clip editing.
  clips,

  /// Masks (manual, face, object) and tracking.
  mask,

  /// Export.
  export,
}

/// Owner of the editor's local state (14 §5.6 `EditorController`): the
/// project and its preview session, selection, timeline zoom, mode. The
/// project stays the only authority on the edit itself; every change goes
/// through [apply] once, at the end of a gesture (14 §6.3).
class EditorController extends ChangeNotifier {
  /// Creates a controller.
  EditorController({required this.project, required this.strings}) {
    project.state.addListener(_onProject);
    unawaited(_loadPreview());
  }

  /// Project (owned by the host).
  final VideoKitEditProject project;

  /// Strings of the owning widget.
  VkStrings Function() strings;

  /// Panels and notices.
  final VkSheetController sheets = VkSheetController();

  VideoKitSession? _preview;
  bool _disposed = false;

  /// Preview session once loaded.
  VideoKitSession? get preview => _preview;

  /// Current work area.
  EditorMode get mode => _mode;
  EditorMode _mode = EditorMode.clips;

  /// Selected clip.
  String? get selectedClipId => _selectedClipId;
  String? _selectedClipId;

  /// Selected mask.
  String? get selectedMaskId => _selectedMaskId;
  String? _selectedMaskId;

  /// Timeline zoom and scroll.
  TimelineScale get scale => _scale;
  TimelineScale _scale = const TimelineScale(pxPerSecond: 24);

  /// Project state.
  VideoKitEditState get state => project.state.value;

  /// Playhead (output time) from the preview session.
  int get playheadUs => _preview?.state.value.positionUs ?? 0;

  Future<void> _loadPreview() async {
    final p = await project.previewSession();
    if (_disposed) return;
    _preview = p;
    p.state.addListener(notifyListeners);
    notifyListeners();
  }

  void _onProject() {
    final st = state;
    if (_selectedClipId != null &&
        !st.timeline.clips.any((c) => c.clipId == _selectedClipId)) {
      _selectedClipId = null;
    }
    if (_selectedMaskId != null && st.maskById(_selectedMaskId!) == null) {
      _selectedMaskId = null;
    }
    notifyListeners();
  }

  /// Switches the work area.
  set mode(EditorMode m) {
    if (m == _mode) return;
    _mode = m;
    notifyListeners();
  }

  /// Selects a clip (null clears).
  void selectClip(String? clipId) {
    _selectedClipId = clipId;
    notifyListeners();
  }

  /// Selects a mask (null clears).
  void selectMask(String? maskId) {
    _selectedMaskId = maskId;
    notifyListeners();
  }

  /// Sets the timeline scale.
  set scale(TimelineScale s) {
    if (s == _scale) return;
    _scale = s;
    notifyListeners();
  }

  /// Applies [command]; rejected/unsupported results show a notice and the
  /// UI falls back to the project state (14 §6.3).
  Future<EditCommandResult> apply(VideoKitEditCommand command) async {
    final r = await project.apply(command);
    _feedback(r);
    return r;
  }

  void _feedback(EditCommandResult r) {
    if (_disposed) return;
    final s = strings();
    switch (r) {
      case EditRejected(:final error):
        sheets.showToast(VkToastEntry(message: s.error(error.code)));
      case EditUnsupported():
        sheets.showToast(VkToastEntry(message: s.text('commandUnavailable')));
      case EditApplied() || EditProjectReleased():
        break;
    }
  }

  /// Undo.
  Future<void> undo() async => _feedback(await project.undo());

  /// Redo.
  Future<void> redo() async => _feedback(await project.redo());

  /// Moves the playhead (preview seek, closest sync at the end).
  Future<void> seek(int us, {SeekMode mode = SeekMode.closestSync}) async {
    final p = _preview;
    if (p == null) return;
    final d = state.timeline.durationUs;
    await p.execute(SeekTo(us.clamp(0, d < 0 ? 0 : d), mode: mode));
  }

  /// Play/pause the preview.
  Future<void> togglePlay() async {
    final p = _preview;
    if (p == null) return;
    final playing = p.state.value.phase == SessionPhase.playing;
    await p.execute(playing ? const Pause() : const Play());
  }

  /// Clip under output time [us].
  EditClip? clipAt(int us) {
    var start = 0;
    for (final c in state.timeline.clips) {
      if (us >= start && us < start + c.durationUs) return c;
      start += c.durationUs;
    }
    return null;
  }

  /// Output start of every clip, in order.
  List<int> clipStarts() {
    final out = <int>[];
    var start = 0;
    for (final c in state.timeline.clips) {
      out.add(start);
      start += c.durationUs;
    }
    return out;
  }

  /// Splits the clip under the playhead (or the selected clip) there.
  Future<void> splitAtPlayhead() async {
    final at = playheadUs;
    final clip = clipAt(at);
    if (clip == null) return;
    final r = await apply(SplitAt(clip.clipId, at));
    if (r is EditApplied && r.createdId != null) selectClip(r.createdId);
  }

  /// Removes the selected clip.
  Future<void> removeSelected() async {
    final id = _selectedClipId;
    if (id == null) return;
    await apply(RemoveClip(id));
  }

  /// Moves [clipId] by [delta] positions.
  Future<void> moveBy(String clipId, int delta) async {
    final clips = state.timeline.clips;
    final i = clips.indexWhere((c) => c.clipId == clipId);
    final to = i + delta;
    if (i < 0 || to < 0 || to >= clips.length) return;
    await apply(MoveClip(clipId, to));
  }

  @override
  void dispose() {
    _disposed = true;
    project.state.removeListener(_onProject);
    _preview?.state.removeListener(notifyListeners);
    sheets.dispose();
    super.dispose();
  }
}
