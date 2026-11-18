import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_pressable.dart';
import '../common/vk_segmented.dart';
import '../foundation/format.dart';
import '../foundation/selector.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import '../theme/tokens/vk_component_styles.dart';
import 'picture_style.dart';

/// Readable codec name of a track (R1-03): "AAC", "DTS", "WebVTT"…; an
/// unknown value is shown as it is. Technical names, not translated.
String vkTrackCodecName(String codec) =>
    switch (codec.split(';').first.trim().toLowerCase()) {
      'audio/mp4a-latm' || 'audio/aac' => 'AAC',
      'audio/vnd.dts' || 'audio/dts' => 'DTS',
      'audio/vnd.dts.hd' => 'DTS-HD',
      'audio/ac3' => 'AC-3',
      'audio/eac3' => 'E-AC-3',
      'audio/eac3-joc' => 'E-AC-3 JOC',
      'audio/ac4' => 'AC-4',
      'audio/true-hd' => 'TrueHD',
      'audio/opus' => 'Opus',
      'audio/vorbis' => 'Vorbis',
      'audio/mpeg' => 'MP3',
      'audio/flac' => 'FLAC',
      'audio/raw' => 'PCM',
      'audio/alac' => 'ALAC',
      'text/vtt' => 'WebVTT',
      'application/x-subrip' => 'SRT',
      'text/x-ssa' => 'SSA/ASS',
      'application/ttml+xml' => 'TTML',
      'application/pgs' => 'PGS',
      'application/dvbsubs' => 'DVB',
      'application/vobsub' => 'VobSub',
      'application/cea-608' => 'CEA-608',
      'application/cea-708' => 'CEA-708',
      _ => codec,
    };

/// Channel layout of an audio track (04A C1): 1 → 单声道, 2 → 2.0, 6 → 5.1,
/// 8 → 7.1, otherwise "N 声道"; null when unknown.
String? vkChannelLayout(VkStrings s, int? channels) => switch (channels) {
  null || <= 0 => null,
  1 => s.text('trackChannelsMono'),
  2 => '2.0',
  6 => '5.1',
  8 => '7.1',
  final n => s.trackChannelsCount(n),
};

/// Track subtitle: codec name and channel layout ("AAC 2.0", "DTS 5.1");
/// only the codec when the channel count is unknown (04A C1, R1-03).
String? vkTrackDetail(VkStrings s, TrackInfo t) {
  final codec = t.codec == null ? null : vkTrackCodecName(t.codec!);
  final layout = vkChannelLayout(s, t.channelCount);
  if (codec == null) return layout;
  if (layout == null) return codec;
  return s.trackCodecChannels(codec, layout);
}

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
  static String trackName(
    VkStrings s,
    TrackInfo t,
    int index, {
    bool audio = false,
  }) {
    final label = t.label?.trim();
    if (label != null &&
        label.isNotEmpty &&
        !_noLanguage.contains(label.toLowerCase())) {
      return label;
    }
    final lang = t.language?.trim();
    // TEST-R2 R2-04: "und" (ISO 639 undetermined) and other non-language
    // codes mean nothing to users: "音轨 N" instead.
    if (lang != null &&
        lang.isNotEmpty &&
        !_noLanguage.contains(lang.toLowerCase())) {
      return lang;
    }
    return audio ? s.trackAudioUnnamed(index + 1) : s.trackUnnamed(index + 1);
  }

  /// ISO 639-2 codes that carry no language (undetermined, multiple, no
  /// linguistic content, uncoded).
  static const Set<String> _noLanguage = {
    'und',
    'mul',
    'zxx',
    'mis',
    'unknown',
  };

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
        // Design page 11: neutral segmented tabs.
        VkSegmented<TrackSettingsTab>(
          segments: [
            for (final tab in TrackSettingsTab.values)
              VkSegment(value: tab, label: tabLabel(tab)),
          ],
          selected: _tab,
          onChanged: (tab) => setState(() => _tab = tab),
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
            detail: vkTrackDetail(s, tr),
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
            title: TrackSettingsSheet.trackName(s, tr, i, audio: true),
            detail: vkTrackDetail(s, tr),
            selected: st.selectedAudioTrackId == tr.id,
            unsupported: !tr.supported,
            onPressed: () => widget.onCommand(SelectAudioTrack(tr.id)),
          ),
      ],
    );
  }

  /// Speed options (design page 11): filled chips, the selected one in the
  /// primary colour, "1.0×" labels; one row of equal chips when they fit,
  /// otherwise wrapped (large text).
  Widget _speed(BuildContext context, VideoKitSessionState st) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget chip(double v, {bool tight = false}) => VkPressable(
      // Equal chips in one row use a narrow side padding so "0.75×" fits.
      // UI-AUDIT-A4 (design page 11): rounded rectangles, not discs.
      style: t.components.chip.copyWithAll(
        (b) => b.copyWith(
          radius: d.cornerMedium,
          padding: tight
              ? EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing4,
                  vertical: d.spacing8,
                )
              : null,
        ),
      ),
      semanticLabel: VkFormat.speed(s, v),
      selected: st.speed == v,
      onPressed: () => widget.onCommand(SetSpeed(v)),
      builder: (context, box) => FittedBox(
        fit: BoxFit.scaleDown,
        child: Text(VkFormat.speed(s, v), maxLines: 1, style: box.textStyle),
      ),
    );
    return LayoutBuilder(
      builder: (context, c) {
        final n = widget.speeds.length;
        final each = (c.maxWidth - d.spacing8 * (n - 1)) / n;
        final scaled = MediaQuery.textScalerOf(context).scale(1) > 1.3;
        if (n > 0 && each >= d.targetMin && !scaled) {
          return Row(
            children: [
              for (final (i, v) in widget.speeds.indexed) ...[
                if (i > 0) SizedBox(width: d.spacing8),
                Expanded(child: chip(v, tight: true)),
              ],
            ],
          );
        }
        return Wrap(
          spacing: d.spacing8,
          runSpacing: d.spacing8,
          children: [for (final v in widget.speeds) chip(v)],
        );
      },
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
    // Design page 11: rows sit on the sheet; only the chosen one is filled.
    final menu = t.components.menu;
    final plain = menu.normal.copyWith(
      background: t.colors.surface.withValues(alpha: 0),
    );
    final style = VkStateStyle<VkBoxStyle>(
      normal: plain,
      pressed: menu.pressed,
      focused: menu.focused,
      disabled: menu.disabled.copyWith(background: plain.background),
      selected: menu.selected,
      hovered: menu.hovered,
    );
    return Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing4),
      child: VkPressable(
        style: style,
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
