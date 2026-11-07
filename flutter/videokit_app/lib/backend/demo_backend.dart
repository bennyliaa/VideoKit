import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import '../picker/media_picker.dart';
import 'app_backend.dart';

/// One demo document offered by [DemoMediaPicker].
@immutable
final class DemoDocument {
  /// Creates an entry.
  const DemoDocument(this.id, this.kind, this.mimeType, this.scenario);

  /// URI suffix and ARB key selector.
  final String id;

  /// Kind.
  final MediaKind kind;

  /// MIME type.
  final String mimeType;

  /// Fake scenario.
  final String scenario;

  /// URI (`demo:<id>`).
  String get uri => 'demo:$id';

  /// ARB display name.
  String name(AppText t) => t(switch (id) {
    'valley' => t.l.demoValley,
    'street' => t.l.demoStreet,
    'dune' => t.l.demoDune,
    'fireworks' => t.l.demoFireworks,
    'family' => t.l.demoFamily,
    'travel' => t.l.demoTravel,
    _ => t.l.demoUnsupported,
  });
}

/// Documents of the demo picker (design page 7 names).
const List<DemoDocument> demoDocuments = [
  DemoDocument('valley', MediaKind.video, 'video/x-matroska', 'normal'),
  DemoDocument('street', MediaKind.video, 'video/mp4', 'normal'),
  DemoDocument('dune', MediaKind.imageStatic, 'image/heic', 'normal'),
  DemoDocument('fireworks', MediaKind.imageAnimated, 'image/gif', 'normal'),
  DemoDocument('family', MediaKind.video, 'video/x-msvideo', 'buffering'),
  DemoDocument('travel', MediaKind.video, 'video/mp4', 'normal'),
  DemoDocument(
    'unsupported',
    MediaKind.video,
    'video/x-matroska',
    'unsupported',
  ),
];

/// Demo picker (M0): a sheet listing [demoDocuments], multi-select.
/// `demo:travel` reports [MediaAccess.missing] until re-selected, so the
/// "无法打开 / 重新选择" path is visible.
class DemoMediaPicker implements MediaPickerService {
  /// Creates the picker.
  DemoMediaPicker();

  /// URIs that report missing.
  final Set<String> missing = {'demo:travel'};

  /// Released permissions, in order (diagnostics / tests).
  final List<String> released = [];

  final StreamController<List<PickedMedia>> _incoming =
      StreamController.broadcast();

  /// Simulates "用 VideoKit 打开" from another app (temporary grant).
  void simulateIncoming(List<PickedMedia> media) => _incoming.add(media);

  /// Picked media for [d].
  PickedMedia media(DemoDocument d, AppText t, {bool persistable = true}) =>
      PickedMedia(
        uri: d.uri,
        displayName: d.name(t),
        kind: d.kind,
        mimeType: d.mimeType,
        persistable: persistable,
      );

  @override
  Future<List<PickedMedia>> pick(
    BuildContext context, {
    bool multiple = true,
    Set<MediaKind> kinds = const {MediaKind.video, MediaKind.imageStatic},
  }) async {
    final t = AppText.of(context);
    final docs = [
      for (final d in demoDocuments)
        if (kinds.contains(d.kind) ||
            (d.kind.isImage && kinds.any((k) => k.isImage)))
          d,
    ];
    final picked = await showModalBottomSheet<List<DemoDocument>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: VkTheme.of(context).colors.surface,
      builder: (context) => _DemoPickerSheet(docs: docs, multiple: multiple),
    );
    return [for (final d in picked ?? const <DemoDocument>[]) media(d, t)];
  }

  @override
  Future<PickedMedia?> reselect(
    BuildContext context,
    PickedMedia previous,
  ) async {
    final r = await pick(context, multiple: false, kinds: {previous.kind});
    if (r.isEmpty) return null;
    // Re-selecting the moved demo file "finds" it again.
    missing.remove(r.single.uri);
    return r.single;
  }

  @override
  Future<MediaAccess> checkAccess(String uri) async =>
      missing.contains(uri) ? MediaAccess.missing : MediaAccess.ok;

  @override
  Future<void> releaseAccess(String uri) async => released.add(uri);

  @override
  Stream<List<PickedMedia>> get incoming => _incoming.stream;

  /// Closes the incoming stream.
  Future<void> close() => _incoming.close();
}

class _DemoPickerSheet extends StatefulWidget {
  const _DemoPickerSheet({required this.docs, required this.multiple});

  final List<DemoDocument> docs;
  final bool multiple;

  @override
  State<_DemoPickerSheet> createState() => _DemoPickerSheetState();
}

class _DemoPickerSheetState extends State<_DemoPickerSheet> {
  final List<DemoDocument> _chosen = [];

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    return SafeArea(
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxHeight: MediaQuery.sizeOf(context).height * 0.85,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Semantics(
                    header: true,
                    child: Text(
                      a(a.l.pickerTitle),
                      style: t.typography.title.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ),
                  Text(
                    a(a.l.pickerDemoNote),
                    style: t.typography.bodySmall.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Flexible(
              child: ListView(
                shrinkWrap: true,
                children: [
                  for (final doc in widget.docs)
                    _row(context, doc, _chosen.contains(doc)),
                ],
              ),
            ),
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing16),
              child: VkButton(
                label: widget.multiple
                    ? a(a.l.pickerConfirm(_chosen.length))
                    : a(a.l.pickerConfirmOne),
                onPressed: _chosen.isEmpty
                    ? null
                    : () => Navigator.of(context).pop(List.of(_chosen)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _row(BuildContext context, DemoDocument doc, bool chosen) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    void toggle() => setState(() {
      if (!widget.multiple) _chosen.clear();
      chosen ? _chosen.remove(doc) : _chosen.add(doc);
    });
    return Semantics(
      checked: chosen,
      button: true,
      label: doc.name(a),
      onTap: toggle,
      child: ExcludeSemantics(
        child: InkWell(
          onTap: toggle,
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: d.targetMin),
            child: Padding(
              padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing16),
              child: Row(
                children: [
                  Icon(
                    t.icons.resolve(doc.kind.isImage ? 'fit' : 'clips'),
                    color: t.colors.textSecondary,
                  ),
                  SizedBox(width: d.spacing12),
                  Expanded(
                    child: Text(
                      doc.name(a),
                      style: t.typography.body.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ),
                  Icon(
                    t.icons.resolve(chosen ? 'checkboxon' : 'checkboxoff'),
                    color: chosen ? t.colors.primary : t.colors.borderStrong,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// M0 backend: the Dart Fake (demo data only, REQ-APP-06: not in release
/// builds from M1).
class DemoBackend implements AppBackend {
  /// Creates the backend.
  DemoBackend({FakeVideoKit? kit, DemoMediaPicker? picker})
    : _kit = kit ?? FakeVideoKit(),
      _picker = picker ?? DemoMediaPicker();

  final FakeVideoKit _kit;
  final DemoMediaPicker _picker;

  /// The Fake (tests drive its clock).
  FakeVideoKit get fake => _kit;

  @override
  bool get isDemo => true;

  @override
  DemoMediaPicker get picker => _picker;

  @override
  VideoKit get videoKit => _kit;

  @override
  VideoKitMediaSource sourceFor(HistoryEntry entry) {
    final doc = demoDocuments.where((d) => d.uri == entry.uri).firstOrNull;
    return VideoKitMediaSource(
      mediaToken: entry.uri,
      mediaKind: entry.kind,
      displayName: entry.displayName,
      sourceRef: DemoSourceRef(doc?.scenario ?? 'normal'),
      mimeType: entry.mimeType,
    );
  }

  @override
  VideoKitPictureBuilder? get pictureBuilder =>
      (context, session) => DemoSessionPicture(session: session);

  @override
  Widget thumbnail(BuildContext context, HistoryEntry entry) {
    return DemoPicture(
      seed: stableHash(entry.uri),
      positionUs: entry.lastPositionUs ?? 0,
      durationUs: entry.durationUs,
      animated: entry.kind == MediaKind.imageAnimated,
    );
  }

  @override
  VideoKitOutputSink get exportSink => const VideoKitOutputSink(
    sinkRef: 'demo:app-export',
    capabilities: SinkCapabilities(
      fileDescriptor: true,
      knownFreeSpaceBytes: 12400000000,
    ),
  );

  /// Demo: no system dialog; the Fake writes no file.
  @override
  Future<VideoKitOutputSink?> prepareExport({
    required String suggestedName,
    required String mimeType,
  }) async => exportSink;

  @override
  Future<List<OutputFormat>> presets() async =>
      FakeVideoKit.demoCapabilities().outputFormats;

  @override
  void attach(TickerProvider vsync) => _kit.clock.attachTicker(vsync);

  @override
  void detach() => _kit.clock.detachTicker();

  @override
  Future<void> close() async {
    detach();
    await _picker.close();
    await _kit.close();
  }
}
