import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_pressable.dart';
import '../foundation/format.dart';
import '../foundation/selector.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';

/// Tabs of [TrackSettingsSheet].
enum TrackSettingsTab { subtitles, audio, speed }

/// Speed steps (14 §12; hosts may trim).
const List<double> vkDefaultSpeeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];

/// UI-02 track and settings panel (14 §5.2, design page 11): subtitle
/// (single choice with "off"), audio track (single choice; unsupported
/// tracks stay visible, greyed and labelled) and speed. Selecting sends the
/// command immediately and keeps the panel open; the selection shown is
/// always the session state, so a rejected command snaps back by itself.
class TrackSettingsSheet extends StatefulWidget {
  /// Creates the panel content.
  const TrackSettingsSheet({
    super.key,
    required this.session,
    required this.onCommand,
    this.initialTab = TrackSettingsTab.subtitles,
    this.speeds = vkDefaultSpeeds,
  });

  /// Session.
  final VideoKitSession session;

  /// Sends a command (the player routes it through its dispatcher).
  final ValueChanged<VideoKitCommand> onCommand;

  /// Initial tab.
  final TrackSettingsTab initialTab;

  /// Offered speeds.
  final List<double> speeds;

  /// Display name of a track.
  static String trackName(VkStrings s, TrackInfo t, int index) {
    final label = t.label;
    if (label != null && label.isNotEmpty) return label;
    final lang = t.language;
    if (lang != null && lang.isNotEmpty) return lang;
    return s.trackUnnamed(index + 1);
  }

  @override
  State<TrackSettingsSheet> createState() => _TrackSettingsSheetState();
}

class _TrackSettingsSheetState extends State<TrackSettingsSheet> {
  late TrackSettingsTab _tab = widget.initialTab;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    String tabLabel(TrackSettingsTab tab) => switch (tab) {
      TrackSettingsTab.subtitles => s.text('playerSubtitles'),
      TrackSettingsTab.audio => s.text('playerAudioTrack'),
      TrackSettingsTab.speed => s.text('playerSpeed'),
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: EdgeInsetsDirectional.all(d.spacing4),
          decoration: BoxDecoration(
            color: t.colors.surfaceVariant,
            borderRadius: BorderRadius.circular(d.cornerMedium),
          ),
          child: Row(
            children: [
              for (final tab in TrackSettingsTab.values)
                Expanded(
                  child: VkPressable(
                    style: t.components.chip,
                    semanticLabel: tabLabel(tab),
                    selected: tab == _tab,
                    onPressed: () => setState(() => _tab = tab),
                    builder: (context, box) => Text(
                      tabLabel(tab),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: box.textStyle,
                    ),
                  ),
                ),
            ],
          ),
        ),
        SizedBox(height: d.spacing12),
        VkSelector<VideoKitSessionState, VideoKitSessionState>(
          listenable: widget.session.state,
          select: (st) => st,
          equals: (a, b) =>
              a.selectedSubtitleTrackId == b.selectedSubtitleTrackId &&
              a.selectedAudioTrackId == b.selectedAudioTrackId &&
              a.speed == b.speed &&
              a.audioTracks == b.audioTracks &&
              a.subtitleTracks == b.subtitleTracks,
          builder: (context, st) => switch (_tab) {
            TrackSettingsTab.subtitles => _subtitles(context, st),
            TrackSettingsTab.audio => _audio(context, st),
            TrackSettingsTab.speed => _speed(context, st),
          },
        ),
      ],
    );
  }

  Widget _empty(BuildContext context, String text) {
    final t = VkTheme.of(context);
    return Padding(
      padding: EdgeInsetsDirectional.symmetric(
        vertical: t.dimensions.spacing16,
      ),
      child: Text(
        text,
        style: t.typography.body.copyWith(color: t.colors.textSecondary),
      ),
    );
  }

  Widget _subtitles(BuildContext context, VideoKitSessionState st) {
    final s = VkStrings.of(context);
    if (st.subtitleTracks.isEmpty) {
      return _empty(context, s.text('tracksNoSubtitles'));
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _TrackRow(
          title: s.text('tracksSubtitlesOff'),
          selected: st.selectedSubtitleTrackId == null,
          onPressed: () => widget.onCommand(const SelectSubtitleTrack(null)),
        ),
        for (final (i, tr) in st.subtitleTracks.indexed)
          _TrackRow(
            title: TrackSettingsSheet.trackName(s, tr, i),
            detail: tr.codec,
            selected: st.selectedSubtitleTrackId == tr.id,
            unsupported: !tr.supported,
            onPressed: () => widget.onCommand(SelectSubtitleTrack(tr.id)),
          ),
      ],
    );
  }

  Widget _audio(BuildContext context, VideoKitSessionState st) {
    final s = VkStrings.of(context);
    if (st.audioTracks.isEmpty) return _empty(context, s.text('tracksNoAudio'));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final (i, tr) in st.audioTracks.indexed)
          _TrackRow(
            title: TrackSettingsSheet.trackName(s, tr, i),
            detail: tr.codec,
            selected: st.selectedAudioTrackId == tr.id,
            unsupported: !tr.supported,
            onPressed: () => widget.onCommand(SelectAudioTrack(tr.id)),
          ),
      ],
    );
  }

  Widget _speed(BuildContext context, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    return Wrap(
      spacing: t.dimensions.spacing8,
      runSpacing: t.dimensions.spacing8,
      children: [
        for (final v in widget.speeds)
          VkPressable(
            style: t.components.chip,
            semanticLabel: s.speedValue(
              VkFormat.number(s, v, maxFractionDigits: 2),
            ),
            selected: st.speed == v,
            onPressed: () => widget.onCommand(SetSpeed(v)),
            builder: (context, box) => Text(
              s.speedValue(VkFormat.number(s, v, maxFractionDigits: 2)),
              style: box.textStyle,
            ),
          ),
      ],
    );
  }
}

class _TrackRow extends StatelessWidget {
  const _TrackRow({
    required this.title,
    required this.selected,
    required this.onPressed,
    this.detail,
    this.unsupported = false,
  });

  final String title;
  final String? detail;
  final bool selected;
  final bool unsupported;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing4),
      child: VkPressable(
        style: t.components.menu,
        semanticLabel: title,
        semanticHint: unsupported ? s.text('tracksUnsupported') : null,
        selected: selected,
        onPressed: unsupported ? null : onPressed,
        builder: (context, box) => Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: box.textStyle),
                  if (detail != null)
                    Text(
                      detail!,
                      style: t.typography.caption.copyWith(
                        color: unsupported
                            ? t.colors.disabledContent
                            : t.colors.textSecondary,
                      ),
                    ),
                ],
              ),
            ),
            if (unsupported)
              Container(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing8,
                  vertical: d.spacing4,
                ),
                decoration: BoxDecoration(
                  color: t.colors.surfaceHigh,
                  borderRadius: BorderRadius.circular(d.cornerFull),
                ),
                child: Text(
                  s.text('tracksUnsupported'),
                  style: t.typography.caption,
                ),
              ),
            if (selected)
              Icon(t.icons.check, color: t.colors.primary, size: d.icon24),
          ],
        ),
      ),
    );
  }
}
