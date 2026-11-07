import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';

/// One record on the home page (design page 7): thumbnail with duration
/// or "图片" badge and resume progress, name, parameters, "看到 01:41 ·
/// 2 小时前" / "上次查看 · 昨天", or "无法打开" with "重新选择".
class HistoryTile extends StatelessWidget {
  /// Creates a tile.
  const HistoryTile({
    super.key,
    required this.entry,
    required this.grid,
    required this.onOpen,
    required this.onReselect,
    required this.onMenu,
  });

  /// Record.
  final HistoryEntry entry;

  /// Grid (card) or list (row) form.
  final bool grid;

  /// Open / resume.
  final VoidCallback onOpen;

  /// "重新选择".
  final VoidCallback onReselect;

  /// Long press / "更多".
  final VoidCallback onMenu;

  String? _meta(AppText a) {
    final e = entry;
    final w = e.width;
    final h = e.height;
    final size = w == null || h == null
        ? null
        : (!e.isImage && w > h && const [480, 720, 1080, 1440, 2160].contains(h)
              ? a(a.l.resolutionLines(h))
              : a(a.l.dimensions(w, h)));
    if (e.isImage) return size == null ? null : a(a.l.metaImage(size));
    final codec = e.videoCodec;
    if (size == null) return null;
    return codec == null ? size : a(a.l.metaVideo(size, vkCodecName(codec)));
  }

  String _when(AppText a, DateTime now) => a.relative(
    DateTime.fromMillisecondsSinceEpoch(entry.lastOpenedAtEpochMs),
    now,
  );

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final now = AppScope.of(context).history.now();
    final e = entry;
    final meta = _meta(a);
    final pos = e.lastPositionUs;
    final second = e.unavailable
        ? null
        : (e.isImage
              ? a(a.l.entryViewed(_when(a, now)))
              : (pos != null && pos > 0
                    ? a(a.l.entryWatched(VkFormat.timecode(pos), _when(a, now)))
                    : a(a.l.entryNew(_when(a, now)))));
    final texts = <Widget>[
      Text(
        e.displayName,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: t.typography.title.copyWith(
          color: e.unavailable ? t.colors.textSecondary : t.colors.textPrimary,
        ),
      ),
      if (e.unavailable) ...[
        Text(
          a(a.l.unavailable),
          style: t.typography.label.copyWith(color: t.colors.error),
        ),
        Text(
          a(a.l.unavailableReason),
          style: t.typography.bodySmall.copyWith(color: t.colors.textSecondary),
        ),
        if (!grid)
          VkButton(
            label: a(a.l.reselect),
            variant: VkButtonVariant.text,
            onPressed: onReselect,
          ),
      ] else ...[
        if (meta != null && !grid)
          Text(
            meta,
            style: t.typography.bodySmall.copyWith(
              color: t.colors.textSecondary,
            ),
          ),
        if (second != null)
          Text(
            second,
            style: t.typography.bodySmall.copyWith(
              color: t.colors.textSecondary,
            ),
          ),
        if (!e.persistable)
          Text(
            a(a.l.temporaryGrant),
            style: t.typography.caption.copyWith(color: t.colors.warning),
          ),
      ],
    ];
    final thumb = _Thumbnail(entry: e);
    final body = MergeSemantics(
      child: Semantics(
        button: true,
        child: InkWell(
          onTap: e.unavailable ? onReselect : onOpen,
          onLongPress: onMenu,
          borderRadius: BorderRadius.circular(d.cornerLarge),
          child: grid
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    AspectRatio(aspectRatio: 16 / 10, child: thumb),
                    SizedBox(height: d.spacing8),
                    ...texts,
                  ],
                )
              : Padding(
                  padding: EdgeInsetsDirectional.all(d.spacing12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(
                        width: d.targetMin * 2.25,
                        child: AspectRatio(aspectRatio: 16 / 9, child: thumb),
                      ),
                      SizedBox(width: d.spacing12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: texts,
                        ),
                      ),
                    ],
                  ),
                ),
        ),
      ),
    );
    final action = e.unavailable
        ? VkButton(
            label: a(a.l.reselect),
            variant: VkButtonVariant.text,
            onPressed: onReselect,
          )
        : VkIconButton(
            icon: t.icons.resolve('more'),
            semanticLabel: a(a.l.menuMore),
            onPressed: onMenu,
          );
    if (grid) {
      return Stack(
        children: [
          body,
          PositionedDirectional(
            top: d.spacing4,
            end: d.spacing4,
            child: e.unavailable
                ? const SizedBox.shrink()
                : VkIconButton(
                    icon: t.icons.resolve('more'),
                    semanticLabel: a(a.l.menuMore),
                    onPressed: onMenu,
                    style: t.components.hostActionBar.item,
                  ),
          ),
          if (e.unavailable)
            PositionedDirectional(bottom: 0, end: 0, child: action),
        ],
      );
    }
    return Container(
      decoration: BoxDecoration(
        color: t.colors.surface,
        borderRadius: BorderRadius.circular(d.cornerLarge),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(child: body),
          if (!e.unavailable)
            Padding(
              padding: EdgeInsetsDirectional.only(top: d.spacing4),
              child: action,
            ),
        ],
      ),
    );
  }
}

class _Thumbnail extends StatelessWidget {
  const _Thumbnail({required this.entry});

  final HistoryEntry entry;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final d = t.dimensions;
    final e = entry;
    final duration = e.durationUs;
    final pos = e.lastPositionUs;
    final progress = duration == null || duration <= 0 || pos == null
        ? null
        : (pos / duration).clamp(0.0, 1.0);
    return ExcludeSemantics(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(d.cornerMedium),
        child: e.unavailable
            ? ColoredBox(
                color: t.colors.surfaceVariant,
                child: Center(
                  child: Icon(
                    t.icons.warning,
                    size: d.icon24 * 1.5,
                    color: t.colors.textSecondary,
                  ),
                ),
              )
            : Stack(
                fit: StackFit.expand,
                children: [
                  if (e.thumbnailPath case final path?)
                    Image(
                      image: AppScope.of(context).storage.thumbnailImage(path),
                      fit: BoxFit.cover,
                      excludeFromSemantics: true,
                      errorBuilder: (context, _, _) =>
                          AppScope.of(context).backend.thumbnail(context, e),
                    )
                  else
                    AppScope.of(context).backend.thumbnail(context, e),
                  if (e.isImage)
                    PositionedDirectional(
                      top: d.spacing8,
                      start: d.spacing8,
                      child: _Chip(text: a(a.l.imageBadge)),
                    ),
                  if (!e.isImage && duration != null)
                    PositionedDirectional(
                      bottom: d.spacing8,
                      end: d.spacing8,
                      child: _Chip(text: VkFormat.timecode(duration)),
                    ),
                  if (progress != null)
                    PositionedDirectional(
                      start: 0,
                      end: 0,
                      bottom: 0,
                      child: SizedBox(
                        height: d.seekBarTrack,
                        child: Stack(
                          fit: StackFit.expand,
                          children: [
                            ColoredBox(color: t.components.seekBar.track),
                            FractionallySizedBox(
                              alignment: AlignmentDirectional.centerStart,
                              widthFactor: progress,
                              child: ColoredBox(color: t.colors.primary),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return Container(
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing8,
        vertical: d.spacing4 / 2,
      ),
      decoration: BoxDecoration(
        color: t.drawables.glassPlayer.color,
        borderRadius: BorderRadius.circular(d.cornerFull),
      ),
      child: Text(
        text,
        style: t.typography.label.copyWith(
          color: t.colors.playerControlsContent,
        ),
      ),
    );
  }
}
