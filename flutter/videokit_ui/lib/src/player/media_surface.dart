import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

/// Builds the picture when the session has no texture (the Dart Fake):
/// the example app passes the demo picture of `videokit_fake`.
typedef VideoKitPictureBuilder = Widget Function(
  BuildContext context,
  VideoKitSession session,
);

/// Picture layer shared by UI-01/03/05 (14 §5.1 `VkMediaSurface`; package
/// internal): the texture when available, otherwise [builder]; transformed
/// by the session transform, or [transformOverride] during a gesture.
///
/// Holds a texture lease (04A S7) while mounted and releases it on dispose
/// or when the session changes.
class VkMediaSurface extends StatefulWidget {
  /// Creates a surface.
  const VkMediaSurface({
    super.key,
    required this.session,
    this.builder,
    this.transformOverride,
  });

  /// Session.
  final VideoKitSession session;

  /// Picture without texture.
  final VideoKitPictureBuilder? builder;

  /// Local gesture transform applied instead of the session transform.
  final MediaTransform? transformOverride;

  @override
  State<VkMediaSurface> createState() => _VkMediaSurfaceState();
}

class _VkMediaSurfaceState extends State<VkMediaSurface> {
  VideoKitTextureLease? _lease;
  VideoKitSession? _leaseOwner;

  VideoKitTextureLease _acquire() {
    final session = widget.session;
    final current = _lease;
    if (current != null && identical(session, _leaseOwner)) return current;
    current?.release();
    _leaseOwner = session;
    return _lease = session.acquireTexture();
  }

  @override
  void dispose() {
    _lease?.release();
    _lease = null;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final session = widget.session;
    final builder = widget.builder;
    return ValueListenableBuilder<int?>(
      valueListenable: _acquire().textureId,
      builder: (context, textureId, _) => ValueListenableBuilder<VideoSize?>(
        valueListenable: session.videoSize,
        builder: (context, videoSize, _) =>
            ValueListenableBuilder<VideoKitSessionState>(
              valueListenable: session.state,
              builder: (context, st, _) {
                if (st.hiddenForLock) return const SizedBox.expand();
                final transform = widget.transformOverride ?? st.transform;
                final media = videoSize ?? const VideoSize(16, 9);
                final ratio = media.aspectRatio == 0
                    ? 16 / 9
                    : media.aspectRatio;
                final Widget content = textureId != null
                    ? Texture(textureId: textureId)
                    : (builder?.call(context, session) ??
                          const SizedBox.expand());
                return LayoutBuilder(
                  builder: (context, c) {
                    final fit = switch (transform.fitMode) {
                      FitMode.fit => BoxFit.contain,
                      FitMode.fill => BoxFit.cover,
                      FitMode.original => BoxFit.none,
                    };
                    final dpr = MediaQuery.devicePixelRatioOf(context);
                    final box = transform.fitMode == FitMode.original
                        ? Size(media.width / dpr, media.height / dpr)
                        : Size(c.maxWidth, c.maxWidth / ratio);
                    return ClipRect(
                      child: Transform.translate(
                        offset: Offset(
                          transform.panX * c.maxWidth,
                          transform.panY * c.maxHeight,
                        ),
                        child: Transform.scale(
                          scale: transform.scale,
                          child: RotatedBox(
                            quarterTurns: transform.rotationDeg ~/ 90,
                            child: FittedBox(
                              fit: fit,
                              clipBehavior: Clip.hardEdge,
                              child: SizedBox(
                                width: box.width,
                                height: box.height,
                                child: content,
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                );
              },
            ),
      ),
    );
  }
}
