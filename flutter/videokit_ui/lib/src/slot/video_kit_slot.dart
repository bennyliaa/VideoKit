import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../foundation/layout_class.dart';
import '../foundation/selector.dart';
import '../l10n/vk_strings.dart';
import '../player/media_surface.dart';
import '../theme/theme_scope.dart';
import 'visibility_reporter.dart';

/// Degradation the host applied to a slot (14 §5.5; the host performs it,
/// the slot explains it).
enum SlotDegradation {
  /// Playing at a lower resolution.
  lowResolution,

  /// Paused to release the decoder; shows the cover, tap to resume.
  pausedForResources,

  /// Not played at all (M3, 07 §3 "改显示静态占位"): the device has no
  /// decoder left, so the host shows a placeholder instead of creating
  /// sessions again and again; tap lets the host try once more.
  placeholder,
}

/// What a slot needs from the session state; equal values skip rebuilds
/// so one slot's updates never rebuild the others (14 §5.5).
@immutable
final class _SlotView {
  _SlotView(VideoKitSessionState st)
    : phase = st.phase,
      kind = st.mediaKind,
      activeAudio = st.activeAudio,
      error = st.error,
      positionUs = st.positionUs,
      durationUs = st.durationUs,
      bufferedUs = st.bufferedUs,
      hiddenForLock = st.hiddenForLock;

  final SessionPhase phase;
  final MediaKind? kind;
  final bool activeAudio;
  final VideoKitStableError? error;
  final int positionUs;
  final int? durationUs;
  final int? bufferedUs;
  final bool hiddenForLock;

  bool get isVideo => kind == MediaKind.video;

  bool get loading =>
      phase == SessionPhase.created ||
      phase == SessionPhase.binding ||
      phase == SessionPhase.buffering;

  bool get failed =>
      phase == SessionPhase.errorRecoverable ||
      phase == SessionPhase.errorFatal;

  @override
  bool operator ==(Object other) =>
      other is _SlotView &&
      other.phase == phase &&
      other.kind == kind &&
      other.activeAudio == activeAudio &&
      other.error == error &&
      other.positionUs == positionUs &&
      other.durationUs == durationUs &&
      other.bufferedUs == bufferedUs &&
      other.hiddenForLock == hiddenForLock;

  @override
  int get hashCode => Object.hash(
    phase,
    kind,
    activeAudio,
    error,
    positionUs,
    durationUs,
    bufferedUs,
    hiddenForLock,
  );
}

/// UI-05 single slot (14 §5.5, design page 14): picture plus badges
/// (audio/muted, loading, image kind, degradation, error). No control bar;
/// what a tap does is the host's decision.
///
/// The "设为发声" badge only calls [onActivateAudio]; the host or resource
/// coordinator then sends `SetActiveAudio(true, epoch)` (07 §4) — the UI
/// does not enforce the single-audio rule itself.
class VideoKitSlot extends StatelessWidget {
  /// Creates a slot.
  const VideoKitSlot({
    super.key,
    required this.session,
    this.index,
    this.title,
    this.onActivateAudio,
    this.onTap,
    this.onLongPress,
    this.onRetry,
    this.onRemove,
    this.degradation,
    this.pictureBuilder,
    this.reportVisibility = true,
    this.onVisibilityChanged,
  });

  /// Session of this slot.
  final VideoKitSession session;

  /// 1-based position, for the screen-reader label.
  final int? index;

  /// Display name (screen reader only).
  final String? title;

  /// Called with the session ID when the muted badge is pressed.
  final ValueChanged<String>? onActivateAudio;

  /// Slot tapped (host: enter single view, toggle audio, resume …).
  final VoidCallback? onTap;

  /// Slot long-pressed.
  final VoidCallback? onLongPress;

  /// Retry from the error placeholder (shown only for retryable errors).
  final VoidCallback? onRetry;

  /// Remove from the error placeholder.
  final VoidCallback? onRemove;

  /// Degradation applied by the host.
  final SlotDegradation? degradation;

  /// Picture without texture (Dart Fake).
  final VideoKitPictureBuilder? pictureBuilder;

  /// Report scrolled-out, covered and background states to the session
  /// (`SetVisibility`, 07 §5.3; [VideoKitVisibilityReporter]).
  final bool reportVisibility;

  /// Called after each visibility change sent to the session.
  final ValueChanged<SessionVisibility>? onVisibilityChanged;

  @override
  Widget build(BuildContext context) {
    return VideoKitVisibilityReporter(
      session: session,
      enabled: reportVisibility,
      onChanged: onVisibilityChanged,
      child: VkSelector<VideoKitSessionState, _SlotView>(
        listenable: session.state,
        select: _SlotView.new,
        builder: _build,
      ),
    );
  }

  Widget _build(BuildContext context, _SlotView v) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final paused = degradation == SlotDegradation.pausedForResources;
    final placeholder = degradation == SlotDegradation.placeholder;
    final radius = BorderRadius.circular(d.cornerLarge);
    final label = s.slotLabel(index ?? 1, title ?? '');
    final value = [
      if (v.isVideo)
        v.activeAudio ? s.text('slotActiveAudio') : s.text('playerMute'),
      if (v.loading) s.text('slotLoading'),
      if (v.failed && !placeholder)
        s.error(v.error?.code ?? ErrorCode.internalErrorRedacted),
      if (paused) s.text('slotPausedTitle'),
      if (placeholder) s.text('slotPlaceholderTitle'),
      if (degradation == SlotDegradation.lowResolution)
        s.text('slotLowResolution'),
    ].join('，');

    final content = Stack(
      fit: StackFit.expand,
      children: [
        ColoredBox(color: t.colors.playerCanvas),
        if (!v.failed && !placeholder)
          VkMediaSurface(session: session, builder: pictureBuilder),
        // Whole-slot gesture under the badges; Semantics below carries it.
        GestureDetector(
          excludeFromSemantics: true,
          behavior: HitTestBehavior.opaque,
          onTap: onTap,
          onLongPress: onLongPress,
        ),
        if (v.loading && !v.failed && !paused && !placeholder)
          Center(
            child: ExcludeSemantics(
              child: SizedBox.square(
                dimension: d.targetMin * 0.75,
                child: CircularProgressIndicator(
                  strokeWidth: d.pendingRingStroke,
                  color: t.components.progress.indicator,
                ),
              ),
            ),
          ),
        if (paused) _PausedCover(onTap: onTap),
        // The host chose a placeholder for a denied slot (07 §3): it wins
        // over the resource error the session reports.
        if (placeholder) _PausedCover(onTap: onTap, placeholder: true),
        if (v.failed && !placeholder)
          _ErrorPlaceholder(
            error: v.error,
            fatal: v.phase == SessionPhase.errorFatal,
            onRetry: onRetry,
            onRemove: onRemove,
          ),
        if (!v.failed) ..._badges(context, v),
        if (v.isVideo && !v.failed && !paused && !placeholder)
          _progress(context, v),
      ],
    );

    return Semantics(
      container: true,
      label: label,
      value: value,
      selected: v.activeAudio,
      onTap: onTap,
      onLongPress: onLongPress,
      child: AnimatedContainer(
        duration: t.animations.small.duration,
        curve: t.animations.small.curve,
        decoration: BoxDecoration(
          borderRadius: radius,
          border: Border.all(
            color: v.activeAudio ? t.colors.primary : t.colors.playerCanvas,
            width: d.focusRingWidth * 1.5,
          ),
        ),
        child: ClipRRect(borderRadius: radius, child: content),
      ),
    );
  }

  List<Widget> _badges(BuildContext context, _SlotView v) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final disc = t.components.hostActionBar.item;
    final kindText = switch (v.kind) {
      MediaKind.imageAnimated => s.text('slotAnimated'),
      MediaKind.imageStatic || MediaKind.imageUnknown => s.text('slotImage'),
      _ => null,
    };
    // TEST-R4 R4-03 / R3-05: the audio control and the badges share one
    // top row, so at 200 % text they never overlap or cut each other; the
    // badges shrink (ellipsis) and use short texts at large text.
    final large = VkLayoutClass.iconScale(context) > 1;
    final lowRes = degradation == SlotDegradation.lowResolution;
    final audio = !v.isVideo
        ? null
        : v.activeAudio
        ? Padding(
            padding: EdgeInsetsDirectional.all(d.spacing4),
            child: _Pill(
              icon: t.icons.resolve('volume'),
              text: s.text('slotActiveAudio'),
              background: t.colors.primary,
              content: t.colors.onPrimary,
            ),
          )
        : VkIconButton(
            icon: t.icons.resolve('mute'),
            semanticLabel: s.text('slotActivateAudio'),
            style: disc,
            iconSize: d.icon20,
            onPressed: onActivateAudio == null
                ? null
                : () => onActivateAudio!(session.sessionId),
          );
    final hasBadges = kindText != null || lowRes;
    if (audio == null && !hasBadges) return const [];
    return [
      PositionedDirectional(
        top: d.spacing4,
        start: d.spacing4,
        end: d.spacing4,
        child: LayoutBuilder(
          builder: (context, c) {
            final short = large || c.maxWidth < d.targetMin * 4;
            // Audio control at the start, badges at the end edge.
            return Row(
              mainAxisAlignment: audio == null
                  ? MainAxisAlignment.end
                  : MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // The "发声" pill may shrink; the mute button has a fixed
                // size and leaves the rest to the badges (R5-03).
                if (audio != null)
                  v.activeAudio ? Flexible(flex: 3, child: audio) : audio,
                if (hasBadges)
                  Flexible(
                    flex: 4,
                    child: Align(
                      alignment: AlignmentDirectional.topEnd,
                      child: Padding(
                        padding: EdgeInsetsDirectional.only(
                          top: d.spacing4,
                          start: d.spacing4,
                          end: d.spacing4,
                        ),
                        child: ExcludeSemantics(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              if (kindText != null)
                                _Pill(
                                  text: kindText,
                                  background: disc.normal.background,
                                  content: t.colors.playerControlsContent,
                                ),
                              if (lowRes)
                                Padding(
                                  padding: EdgeInsetsDirectional.only(
                                    top: d.spacing4,
                                  ),
                                  child: _Pill(
                                    icon: t.icons.resolve('warning'),
                                    text: s.text(
                                      short
                                          ? 'slotLowResolutionShort'
                                          : 'slotLowResolution',
                                    ),
                                    background: t.colors.warningContainer,
                                    content: t.colors.textPrimary,
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    ];
  }

  Widget _progress(BuildContext context, _SlotView v) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final bar = t.components.seekBar;
    final duration = v.durationUs ?? 0;
    final played = duration <= 0
        ? 0.0
        : (v.positionUs / duration).clamp(0.0, 1.0);
    final buffered = duration <= 0 || v.bufferedUs == null
        ? 0.0
        : (v.bufferedUs! / duration).clamp(0.0, 1.0);
    return PositionedDirectional(
      start: d.spacing12,
      end: d.spacing12,
      bottom: d.spacing12,
      child: ExcludeSemantics(
        // Design page 14: the slot bar carries a thumb at the position
        // (display only; the slot is not a seek control).
        child: LayoutBuilder(
          builder: (context, c) {
            final playedColor = v.activeAudio
                ? bar.played
                : t.colors.playerControlsContent;
            final thumb = bar.thumbSize * 0.75;
            final x = (c.maxWidth * played).clamp(0.0, c.maxWidth);
            return SizedBox(
              height: thumb,
              child: Stack(
                clipBehavior: Clip.none,
                alignment: AlignmentDirectional.centerStart,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(d.cornerFull),
                    child: SizedBox(
                      height: bar.trackHeight,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          ColoredBox(color: bar.track),
                          FractionallySizedBox(
                            alignment: AlignmentDirectional.centerStart,
                            widthFactor: buffered,
                            child: ColoredBox(color: bar.buffered),
                          ),
                          FractionallySizedBox(
                            alignment: AlignmentDirectional.centerStart,
                            widthFactor: played,
                            child: ColoredBox(color: playedColor),
                          ),
                        ],
                      ),
                    ),
                  ),
                  PositionedDirectional(
                    start: x - thumb / 2,
                    child: Container(
                      width: thumb,
                      height: thumb,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: playedColor,
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  const _Pill({
    required this.text,
    required this.background,
    required this.content,
    this.icon,
  });

  final String text;
  final Color background;
  final Color content;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final style = t.typography.label.copyWith(color: content);
    return LayoutBuilder(
      builder: (context, c) {
        // TEST-R5 R5-03: the text shows whenever it fits in full; only a
        // pill too narrow for it falls back to the icon alone.
        final painter = TextPainter(
          text: TextSpan(text: text, style: style),
          textDirection: Directionality.of(context),
          textScaler: MediaQuery.textScalerOf(context),
          maxLines: 1,
        )..layout();
        final textWidth = painter.width;
        painter.dispose();
        final chrome =
            d.spacing8 * 2 + (icon != null ? d.icon16 + d.spacing4 : 0);
        final iconOnly = icon != null && c.maxWidth < chrome + textWidth;
        return Container(
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: iconOnly ? d.spacing4 : d.spacing8,
            vertical: d.spacing4,
          ),
          decoration: BoxDecoration(
            color: background,
            borderRadius: BorderRadius.circular(d.cornerFull),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null) Icon(icon, size: d.icon16, color: content),
              if (!iconOnly) ...[
                if (icon != null) SizedBox(width: d.spacing4),
                Flexible(
                  child: Text(
                    text,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: style,
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

/// Cover shown while the host paused the slot for resources.
class _PausedCover extends StatelessWidget {
  const _PausedCover({this.onTap, this.placeholder = false});

  final VoidCallback? onTap;

  /// [SlotDegradation.placeholder] texts instead of the paused ones.
  final bool placeholder;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final white = t.colors.playerControlsContent;
    return GestureDetector(
      excludeFromSemantics: true,
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: ColoredBox(
        color: t.colors.scrim,
        // Small slots (phone 3×3, R1-12b): icon and a one-line short text;
        // the full reason stays in the slot's screen reader value.
        child: LayoutBuilder(
          builder: (context, c) {
            final small =
                c.maxWidth < d.targetMin * 3 || c.maxHeight < d.targetMin * 3;
            // TEST-R4 R4-03: at large text the content starts below the
            // slot's top row (audio control), so it never covers the icon.
            final large = VkLayoutClass.iconScale(context) > 1;
            return Center(
              child: SingleChildScrollView(
                padding: EdgeInsetsDirectional.fromSTEB(
                  d.spacing8,
                  large ? d.targetMin : d.spacing8,
                  d.spacing8,
                  d.spacing8,
                ),
                child: ExcludeSemantics(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        placeholder ? t.icons.resolve('movie') : t.icons.pause,
                        size:
                            (small ? d.icon24 : d.targetMin * 0.75) *
                            VkLayoutClass.iconScale(context),
                        color: white,
                      ),
                      // TEST-R3 R3-05: at large text the label keeps clear
                      // of the icon.
                      SizedBox(
                        height: VkLayoutClass.iconScale(context) > 1
                            ? d.spacing8
                            : d.spacing4,
                      ),
                      Text(
                        s.text(
                          placeholder
                              ? (small
                                    ? 'slotPlaceholderShort'
                                    : 'slotPlaceholderTitle')
                              : (small ? 'slotPausedShort' : 'slotPausedTitle'),
                        ),
                        textAlign: TextAlign.center,
                        maxLines: small ? 1 : null,
                        overflow: small ? TextOverflow.ellipsis : null,
                        style: t.typography.label.copyWith(color: white),
                      ),
                      if (!small)
                        Text(
                          s.text(
                            placeholder
                                ? 'slotPlaceholderDetail'
                                : 'slotPausedDetail',
                          ),
                          textAlign: TextAlign.center,
                          style: t.typography.caption.copyWith(
                            color: white.withValues(alpha: 0.8),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

/// Compact error placeholder: icon, one-line reason, retry/remove. Only
/// this slot is affected.
class _ErrorPlaceholder extends StatelessWidget {
  const _ErrorPlaceholder({
    required this.error,
    required this.fatal,
    this.onRetry,
    this.onRemove,
  });

  final VideoKitStableError? error;
  final bool fatal;
  final VoidCallback? onRetry;
  final VoidCallback? onRemove;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final canRetry = !fatal && (error?.retryable ?? false) && onRetry != null;
    // TEST-R5 R5-02: in a small cell or at large text the actions become
    // icon buttons with spoken labels, so "移除" is never cut off.
    Widget actions(bool compact) => Wrap(
      alignment: WrapAlignment.center,
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: compact
          ? [
              if (canRetry)
                VkIconButton(
                  icon: t.icons.resolve('retry'),
                  semanticLabel: s.text('actionRetry'),
                  onPressed: onRetry,
                ),
              if (onRemove != null)
                VkIconButton(
                  icon: t.icons.resolve('close'),
                  semanticLabel: s.text('slotRemove'),
                  onPressed: onRemove,
                ),
            ]
          : [
              if (canRetry)
                VkButton(label: s.text('actionRetry'), onPressed: onRetry),
              if (onRemove != null)
                VkButton(
                  label: s.text('slotRemove'),
                  variant: VkButtonVariant.secondary,
                  onPressed: onRemove,
                ),
            ],
    );
    return ColoredBox(
      color: t.colors.surfaceVariant,
      child: LayoutBuilder(
        builder: (context, c) {
          final compact =
              VkLayoutClass.iconScale(context) > 1 ||
              c.maxWidth < d.targetMin * 3 ||
              c.maxHeight < d.targetMin * 3;
          return _errorBody(context, compact, actions(compact));
        },
      ),
    );
  }

  Widget _errorBody(BuildContext context, bool compact, Widget actions) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final canRetry = !fatal && (error?.retryable ?? false) && onRetry != null;
    return SizedBox.expand(
      child: Center(
        child: SingleChildScrollView(
          padding: EdgeInsetsDirectional.all(d.spacing8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                t.icons.warning,
                size: compact ? d.icon24 : d.targetMin * 0.75,
                color: t.colors.error,
              ),
              SizedBox(height: d.spacing4),
              Text(
                s.error(error?.code ?? ErrorCode.internalErrorRedacted),
                textAlign: TextAlign.center,
                maxLines: compact ? 1 : 2,
                overflow: TextOverflow.ellipsis,
                style: t.typography.label.copyWith(color: t.colors.textPrimary),
              ),
              // A compact cell keeps room for the actions; the reason is
              // still spoken with the slot.
              if (!compact)
                Text(
                  s.text('slotErrorOnly'),
                  textAlign: TextAlign.center,
                  style: t.typography.caption.copyWith(
                    color: t.colors.textSecondary,
                  ),
                ),
              if (canRetry || onRemove != null) ...[
                SizedBox(height: compact ? d.spacing4 : d.spacing8),
                actions,
              ],
            ],
          ),
        ),
      ),
    );
  }
}
