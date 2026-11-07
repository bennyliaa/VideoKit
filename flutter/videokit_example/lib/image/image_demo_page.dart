import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_fake/videokit_fake.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../demo/demo_host.dart';
import '../gallery/gallery_text.dart';

/// One demo image of the image viewer page.
@immutable
final class DemoImage {
  /// Creates an entry.
  const DemoImage(this.id, this.kind, this.mimeType, this.bytes, this.scenario);

  /// Media token suffix.
  final String id;

  /// Static or animated.
  final MediaKind kind;

  /// MIME type (info panel format).
  final String mimeType;

  /// Known length (info panel file size).
  final int bytes;

  /// Fake scenario.
  final String scenario;

  /// ARB display name.
  String name(GalleryText g) => g(switch (id) {
    'dune' => g.l.demoImageDune,
    'fireworks' => g.l.demoImageFireworks,
    'forest' => g.l.demoImageForest,
    _ => g.l.demoImageBroken,
  });

  /// Source for binding.
  VideoKitMediaSource source(String displayName) => VideoKitMediaSource(
    mediaToken: 'image-$id',
    mediaKind: kind,
    displayName: displayName,
    sourceRef: DemoSourceRef(scenario),
    mimeType: mimeType,
    knownLength: bytes,
  );
}

/// Pages of the demo: static, animated, static, unsupported format.
const List<DemoImage> demoImages = [
  DemoImage('dune', MediaKind.imageStatic, 'image/heic', 3200000, 'normal'),
  DemoImage(
    'fireworks',
    MediaKind.imageAnimated,
    'image/gif',
    4600000,
    'normal',
  ),
  DemoImage('forest', MediaKind.imageStatic, 'image/webp', 1800000, 'normal'),
  DemoImage(
    'broken',
    MediaKind.imageStatic,
    'image/jxl',
    900000,
    'unsupportedContainer',
  ),
];

/// Host callbacks of the image page: page requests move through
/// [demoImages]; past either end the host answers `unavailable`.
class ImageDemoHost extends DemoHostCallbacks {
  /// Creates the host.
  ImageDemoHost() {
    image = true;
  }

  /// Current page.
  int index = 0;

  /// Called after the host accepted a page change.
  ValueChanged<int>? onPage;

  @override
  Future<NavigationResult> onNavigationRequested(
    NavigationRequest request,
  ) async {
    final next =
        index + (request.direction == NavigationDirection.next ? 1 : -1);
    if (next < 0 || next >= demoImages.length) {
      return NavigationResult.unavailable;
    }
    index = next;
    // Re-bind after answering (the request completes first).
    scheduleMicrotask(() => onPage?.call(next));
    return NavigationResult.accepted;
  }
}

/// UI-03 `VideoKitImageViewer` driven by the Dart Fake (M0-B3 item 4).
class ImageDemoPage extends StatefulWidget {
  /// Creates the page.
  const ImageDemoPage({super.key, this.initialIndex = 0});

  /// First page.
  final int initialIndex;

  @override
  State<ImageDemoPage> createState() => ImageDemoPageState();
}

/// State (public for tests).
class ImageDemoPageState extends State<ImageDemoPage>
    with SingleTickerProviderStateMixin {
  final ImageDemoHost _host = ImageDemoHost();
  late final FakeVideoKit kit = FakeVideoKit(
    config: VideoKitConfig(hostCallbacks: _host),
  );

  /// Session of the current page. Each page gets its own session (R1-10):
  /// a page that failed fatally (unsupported format) must not be re-bound
  /// (`error_fatal.rebind.rejected`), and errors stay with their page.
  VideoKitSession? session;
  int _generation = 0;

  /// Current page.
  int get index => _host.index;

  @override
  void initState() {
    super.initState();
    _host
      ..clock = kit.clock
      ..index = widget.initialIndex
      ..onPage = (i) => unawaited(_bindPage(i));
    kit.clock.attachTicker(this);
    unawaited(_bindPage(_host.index));
  }

  /// Opens page [i] in a new session and closes the previous one.
  Future<void> _bindPage(int i) async {
    final generation = ++_generation;
    final s = await kit.createSession(
      const VideoKitSessionConfig(debugLabel: 'image'),
    );
    if (!mounted || generation != _generation) {
      await s.close();
      return;
    }
    final g = GalleryText.of(context);
    final img = demoImages[i];
    final old = session;
    setState(() => session = s);
    if (old != null) unawaited(old.close());
    await s.bind(img.source(img.name(g)), hostActions: DemoHostActions.image());
    if (img.kind == MediaKind.imageAnimated && mounted) {
      unawaited(s.execute(const Play()));
    }
  }

  @override
  void dispose() {
    _generation++;
    unawaited(session?.close());
    kit.clock.detachTicker();
    unawaited(kit.close());
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = session;
    final img = demoImages[_host.index];
    return Scaffold(
      backgroundColor: t.colors.playerCanvas,
      body: s == null
          ? VideoKitStateView(
              model: mapSessionState(phase: SessionPhase.created)!,
            )
          : VideoKitImageViewer(
              key: ObjectKey(s),
              session: s,
              title: img.name(g),
              source: img.source(img.name(g)),
              pictureBuilder: (context, session) =>
                  DemoSessionPicture(session: session),
              resolveHostString: (k) => DemoHostActions.resolve(context, k),
              onBack: () => Navigator.of(context).maybePop(),
              onStateAction: (_) => unawaited(_bindPage(_host.index)),
            ),
    );
  }
}
