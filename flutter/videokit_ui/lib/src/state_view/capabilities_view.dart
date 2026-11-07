import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';

import '../common/vk_buttons.dart';
import '../common/vk_info_rows.dart';
import '../export/export_panel.dart' show vkCodecName, vkFormatLine;
import '../foundation/format.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';

/// Read-only capability page (J4, design page 12 "查看能力说明"): decoders,
/// container/codec support and the device's suggested limits from
/// [VideoKitCapabilities]. The host decides how it is shown (route, sheet);
/// nothing here can be changed.
class VideoKitCapabilitiesView extends StatelessWidget {
  /// Creates the view.
  const VideoKitCapabilitiesView({super.key, required this.capabilities});

  /// Report from `VideoKit.capabilities`.
  final VideoKitCapabilities capabilities;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final c = capabilities;
    String codec(CodecInfo i) => s.capabilitiesCodecValue(
      s.text(
        i.hardwareAccelerated ? 'capabilitiesHardware' : 'capabilitiesSoftware',
      ),
      i.maxResolution == null
          ? s.text('capabilitiesNone')
          : s.infoDimensionsValue(
              i.maxResolution!.width,
              i.maxResolution!.height,
            ),
    );
    String level(SupportLevel l) => s.text(switch (l) {
      SupportLevel.supported => 'capabilitiesSupported',
      SupportLevel.partial => 'capabilitiesPartial',
      SupportLevel.unsupported => 'capabilitiesUnsupported',
    });
    List<(String, String)> orNone(List<(String, String)> rows) =>
        rows.isEmpty ? [(s.text('capabilitiesNone'), '')] : rows;
    final sections = <(String, List<(String, String)>)>[
      (
        s.text('capabilitiesVideoDecoders'),
        orNone([
          for (final i in c.decoders.video) (vkCodecName(i.mimeType), codec(i)),
        ]),
      ),
      (
        s.text('capabilitiesAudioDecoders'),
        orNone([
          for (final i in c.decoders.audio) (vkCodecName(i.mimeType), codec(i)),
        ]),
      ),
      (
        s.text('capabilitiesFormats'),
        orNone([
          for (final f in c.containerCodecSupport)
            (
              vkFormatLine(f.container, f.videoCodec, f.audioCodec),
              level(f.level),
            ),
        ]),
      ),
      (
        s.text('capabilitiesLimits'),
        [
          (
            s.text('capabilitiesSessions'),
            s.capabilitiesSessionsValue(c.suggestedHardwareVideoSessions),
          ),
          (
            s.text('capabilitiesMaxResolution'),
            s.infoDimensionsValue(
              c.maxSuggestedResolution.width,
              c.maxSuggestedResolution.height,
            ),
          ),
          (
            s.text('capabilitiesMaxFrameRate'),
            VkFormat.frameRate(s, c.maxSuggestedFrameRate.toDouble()),
          ),
        ],
      ),
    ];
    return ListView(
      padding: EdgeInsetsDirectional.all(d.spacing16),
      children: [
        for (final (title, rows) in sections) ...[
          Padding(
            padding: EdgeInsetsDirectional.only(
              top: d.spacing16,
              bottom: d.spacing4,
            ),
            child: Semantics(
              header: true,
              child: Text(
                title,
                style: t.typography.label.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
          ),
          VkInfoRows(rows: rows),
        ],
      ],
    );
  }
}

/// Full page around [VideoKitCapabilitiesView] for hosts that push it as a
/// route (J4): back button, title "能力说明", the report once loaded.
class VideoKitCapabilitiesPage extends StatelessWidget {
  /// Creates the page.
  const VideoKitCapabilitiesPage({super.key, required this.capabilities});

  /// Pending report (`VideoKit.capabilities(const CapabilityRequest())`).
  final Future<VideoKitCapabilities> capabilities;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Scaffold(
      backgroundColor: t.colors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing8),
              child: Row(
                children: [
                  VkIconButton(
                    icon: t.icons.resolve('back'),
                    semanticLabel: s.text('playerBack'),
                    onPressed: () => Navigator.of(context).maybePop(),
                  ),
                  SizedBox(width: d.spacing8),
                  Expanded(
                    child: Semantics(
                      header: true,
                      child: Text(
                        s.text('capabilitiesTitle'),
                        style: t.typography.titleLarge.copyWith(
                          color: t.colors.textPrimary,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: FutureBuilder<VideoKitCapabilities>(
                future: capabilities,
                builder: (context, snap) => switch (snap) {
                  AsyncSnapshot(:final data?) => VideoKitCapabilitiesView(
                    capabilities: data,
                  ),
                  AsyncSnapshot(hasError: true) => Center(
                    child: Text(
                      s.text('capabilitiesNone'),
                      style: t.typography.body.copyWith(
                        color: t.colors.textSecondary,
                      ),
                    ),
                  ),
                  _ => const Center(child: CircularProgressIndicator()),
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
