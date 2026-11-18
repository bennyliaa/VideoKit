import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../editor/edit_demo_page.dart';
import '../features/feature_switch_page.dart';
import '../image/image_demo_page.dart';
import '../multiview/multi_view_demo_page.dart';
import '../player/player_demo_page.dart';
import 'components_page.dart';
import 'gallery_settings.dart';
import 'gallery_text.dart';

/// M0-B1 theme gallery (design pages 5, 6, 22): switch dark/light, host
/// primary, Chinese/pseudo-localization, text scale and reduced motion;
/// shows colour and status tokens, text styles, dimensions, animations,
/// component styles in every state and error texts. The demo badge is
/// permanent (03 §8.3).
class GalleryPage extends StatelessWidget {
  /// Creates the page.
  const GalleryPage({
    super.key,
    required this.settings,
    required this.onChanged,
  });

  /// Current settings.
  final GallerySettings settings;

  /// Settings change callback.
  final ValueChanged<GallerySettings> onChanged;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        title: Text(g(g.l.galleryTitle), style: t.typography.title),
        backgroundColor: t.colors.surface,
      ),
      body: Stack(
        children: [
          ListView(
            padding: EdgeInsetsDirectional.fromSTEB(
              d.spacing16,
              d.spacing16,
              d.spacing16,
              d.spacing32 * 2,
            ),
            children: [
              _SettingsSection(settings: settings, onChanged: onChanged),
              GallerySection(
                title: g(g.l.sectionDemos),
                child: const _DemoLinks(),
              ),
              GallerySection(
                title: g(g.l.sectionColors),
                child: const _ColorGrid(),
              ),
              GallerySection(
                title: g(g.l.sectionStatus),
                child: const _StatusRow(),
              ),
              GallerySection(
                title: g(g.l.sectionComponents),
                child: const _Components(),
              ),
              GallerySection(
                title: g(g.l.sectionTypography),
                child: const _TypographySamples(),
              ),
              GallerySection(
                title: g(g.l.sectionDimensions),
                child: const _DimensionSamples(),
              ),
              GallerySection(
                title: g(g.l.sectionAnimations),
                child: const _AnimationSample(),
              ),
              GallerySection(
                title: g(g.l.sectionErrors),
                child: const _ErrorTexts(),
              ),
            ],
          ),
          const PositionedDirectional(
            top: 0,
            end: 0,
            child: SafeArea(child: GalleryDemoBadge()),
          ),
        ],
      ),
    );
  }
}

/// Permanent "演示模式 · 模拟数据" badge drawn from VideoKit tokens.
class GalleryDemoBadge extends StatelessWidget {
  /// Creates the badge.
  const GalleryDemoBadge({super.key});

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final text = VkStrings.of(context).demoBadge;
    return Semantics(
      label: text,
      container: true,
      child: ExcludeSemantics(
        child: Container(
          margin: EdgeInsetsDirectional.all(d.spacing8),
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4,
          ),
          decoration: BoxDecoration(
            color: t.colors.demo,
            borderRadius: BorderRadius.circular(d.cornerFull),
            boxShadow: [d.floatingShadow(t.colors.shadowFloating)],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(t.icons.demo, size: d.icon16, color: t.colors.demoContent),
              SizedBox(width: d.spacing4),
              Flexible(
                child: Text(
                  text,
                  style: t.typography.label.copyWith(
                    color: t.colors.demoContent,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

String _hex(Color c) =>
    '#${(c.toARGB32() & 0xFFFFFF).toRadixString(16).padLeft(6, '0').toUpperCase()}';

/// Titled gallery section (shared by the gallery pages).
class GallerySection extends StatelessWidget {
  /// Creates a section.
  const GallerySection({super.key, required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    return Padding(
      padding: EdgeInsetsDirectional.only(bottom: t.dimensions.spacing24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Semantics(
            header: true,
            child: Text(title, style: t.typography.titleLarge),
          ),
          SizedBox(height: t.dimensions.spacing12),
          child,
        ],
      ),
    );
  }
}

class _SettingsSection extends StatelessWidget {
  const _SettingsSection({required this.settings, required this.onChanged});

  final GallerySettings settings;
  final ValueChanged<GallerySettings> onChanged;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    Widget row(String label, Widget control) => Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
      child: Wrap(
        spacing: d.spacing12,
        runSpacing: d.spacing8,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Text(label, style: t.typography.label),
          control,
        ],
      ),
    );
    Widget chips<T>(
      List<T> values,
      T selected,
      String Function(T) label,
      void Function(T) pick,
    ) => Wrap(
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: [
        for (final v in values)
          GalleryChoice(
            label: label(v),
            selected: v == selected,
            onPressed: () => pick(v),
          ),
      ],
    );

    return GallerySection(
      title: g(g.l.sectionSettings),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          row(
            g(g.l.settingTheme),
            chips<VideoKitThemeMode>(
              const [
                VideoKitThemeMode.dark,
                VideoKitThemeMode.light,
                VideoKitThemeMode.system,
              ],
              settings.mode,
              (m) => g(switch (m) {
                VideoKitThemeMode.light => g.l.themeLight,
                VideoKitThemeMode.system ||
                VideoKitThemeMode.followHost => g.l.themeSystem,
                VideoKitThemeMode.dark => g.l.themeDark,
              }),
              (m) => onChanged(settings.copyWith(mode: m)),
            ),
          ),
          row(
            g(g.l.settingHostPrimary),
            Wrap(
              spacing: d.spacing8,
              runSpacing: d.spacing8,
              children: [
                for (final p in galleryPrimaryPresets)
                  GalleryChoice(
                    swatch: p,
                    label: p == null ? g(g.l.hostPrimaryDefault) : _hex(p),
                    selected: settings.primary == p,
                    onPressed: () =>
                        onChanged(settings.copyWith(primary: () => p)),
                  ),
              ],
            ),
          ),
          row(
            g(g.l.settingLanguage),
            chips<Locale>(
              galleryLocales,
              settings.locale,
              (l) => g(
                VkPseudo.isPseudo(l) ? g.l.languagePseudo : g.l.languageChinese,
              ),
              (l) => onChanged(settings.copyWith(locale: l)),
            ),
          ),
          row(
            g(g.l.settingTextScale),
            chips<double>(
              galleryTextScales,
              settings.textScale,
              (v) => VkFormat.percent(s, v),
              (v) => onChanged(settings.copyWith(textScale: v)),
            ),
          ),
          SwitchListTile(
            contentPadding: EdgeInsetsDirectional.zero,
            title: Text(g(g.l.settingReduceMotion), style: t.typography.label),
            value: settings.reduceMotion,
            onChanged: (v) => onChanged(settings.copyWith(reduceMotion: v)),
          ),
          Text(
            g(g.l.schemaVersion(t.schemaVersion)),
            style: t.typography.caption,
          ),
        ],
      ),
    );
  }
}

class _ColorGrid extends StatelessWidget {
  const _ColorGrid();

  /// Foreground shown on each colour: its registered contrast partner,
  /// otherwise the better of the two text colours.
  static (VkTokenKey, VkContrastPair?) _onFor(VkColors c, VkTokenKey key) {
    for (final p in VkContrastPairs.all) {
      if (p.background == key && p.minimum >= VkContrastPairs.text) {
        return (p.foreground, p);
      }
    }
    final a = VkContrast.ratio(c.textPrimary, c[key]);
    final b = VkContrast.ratio(c.background, c[key]);
    return (a >= b ? VkTokenKeys.textPrimary : VkTokenKeys.background, null);
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    return Wrap(
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: [
        for (final key in VkTokenKeys.ofType(VkTokenType.color))
          Builder(
            builder: (context) {
              final bg = t.colors[key];
              final (onKey, _) = _onFor(t.colors, key);
              final on = t.colors[onKey];
              final ratio = VkContrast.ratio(on, bg);
              return Semantics(
                label: g(g.l.colorSwatch(key.key, _hex(bg))),
                child: ConstrainedBox(
                  constraints: BoxConstraints(minWidth: d.targetMin * 3),
                  child: Container(
                    padding: EdgeInsetsDirectional.all(d.spacing8),
                    decoration: BoxDecoration(
                      color: bg,
                      borderRadius: BorderRadius.circular(d.cornerMedium),
                      border: Border.all(
                        color: t.colors.border,
                        width: d.borderWidth,
                      ),
                    ),
                    child: ExcludeSemantics(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            key.key,
                            style: t.typography.caption.copyWith(color: on),
                          ),
                          Text(
                            _hex(bg),
                            style: t.typography.timecode.copyWith(color: on),
                          ),
                          Text(
                            g(g.l.contrastRatio(VkFormat.number(s, ratio))),
                            style: t.typography.caption.copyWith(color: on),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
      ],
    );
  }
}

class _StatusRow extends StatelessWidget {
  const _StatusRow();

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final c = t.colors;
    final d = t.dimensions;
    // Status is never colour-only: each chip has an icon and a label.
    final items = [
      (c.trackTracked, t.icons.check, g(g.l.statusTracked)),
      (c.trackLowConfidence, t.icons.warning, g(g.l.statusLowConfidence)),
      (c.trackAmbiguous, t.icons.resolve('info'), g(g.l.statusAmbiguous)),
      (c.trackLost, t.icons.error, g(g.l.statusLost)),
      (c.info, t.icons.info, g(g.l.statusInfo)),
      (c.demo, t.icons.demo, VkStrings.of(context).demoBadge),
    ];
    final containers = [
      (c.successContainer, c.success, t.icons.check, g(g.l.statusTracked)),
      (
        c.warningContainer,
        c.warning,
        t.icons.warning,
        g(g.l.statusLowConfidence),
      ),
      (c.errorContainer, c.error, t.icons.error, g(g.l.statusLost)),
      (c.infoContainer, c.info, t.icons.info, g(g.l.statusInfo)),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: d.spacing12,
          runSpacing: d.spacing8,
          children: [
            for (final (color, icon, label) in items)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(icon, color: color, size: d.icon20),
                  SizedBox(width: d.spacing4),
                  Flexible(child: Text(label, style: t.typography.bodySmall)),
                ],
              ),
          ],
        ),
        SizedBox(height: d.spacing12),
        Wrap(
          spacing: d.spacing8,
          runSpacing: d.spacing8,
          children: [
            for (final (bg, fg, icon, label) in containers)
              Container(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing12,
                  vertical: d.spacing8,
                ),
                decoration: BoxDecoration(
                  color: bg,
                  borderRadius: BorderRadius.circular(d.cornerSmall),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(icon, color: fg, size: d.icon16),
                    SizedBox(width: d.spacing4),
                    Flexible(child: Text(label, style: t.typography.bodySmall)),
                  ],
                ),
              ),
          ],
        ),
      ],
    );
  }
}

class _Components extends StatelessWidget {
  const _Components();

  static String _stateLabel(GalleryText g, VkInteractionState s) =>
      g(switch (s) {
        VkInteractionState.normal => g.l.stateNormal,
        VkInteractionState.pressed => g.l.statePressed,
        VkInteractionState.focused => g.l.stateFocused,
        VkInteractionState.disabled => g.l.stateDisabled,
        VkInteractionState.selected => g.l.stateSelected,
        VkInteractionState.hovered => g.l.stateHovered,
      });

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final c = t.components;
    final d = t.dimensions;
    Widget box(VkBoxStyle style, {String? label, IconData? icon}) =>
        ConstrainedBox(
          constraints: BoxConstraints(
            minWidth: style.minSize,
            minHeight: style.minSize,
          ),
          child: Container(
            padding: style.padding,
            decoration: style.decoration,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (icon != null)
                  Icon(icon, color: style.content, size: d.icon24),
                if (label != null)
                  Flexible(child: Text(label, style: style.textStyle)),
              ],
            ),
          ),
        );
    Widget states(
      String title,
      VkStateStyle<VkBoxStyle> style, {
      String? label,
      IconData? icon,
    }) => Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: t.typography.label),
          SizedBox(height: d.spacing8),
          Wrap(
            spacing: d.spacing8,
            runSpacing: d.spacing8,
            children: [
              for (final s in VkInteractionState.values)
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    box(style.of(s), label: label, icon: icon),
                    SizedBox(height: d.spacing4),
                    Text(_stateLabel(g, s), style: t.typography.caption),
                  ],
                ),
            ],
          ),
        ],
      ),
    );
    final seek = c.seekBar;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        states(
          g(g.l.componentButtonPrimary),
          c.buttonPrimary,
          label: g(g.l.componentButtonPrimary),
        ),
        states(
          g(g.l.componentButtonSecondary),
          c.buttonSecondary,
          label: g(g.l.componentButtonSecondary),
        ),
        states(
          g(g.l.componentButtonText),
          c.buttonText,
          label: g(g.l.componentButtonText),
        ),
        states(g(g.l.componentButtonIcon), c.buttonIcon, icon: t.icons.play),
        states(g(g.l.componentChip), c.chip, label: g(g.l.componentChip)),
        Row(children: [box(c.badge.normal, label: g(g.l.componentBadge(3)))]),
        SizedBox(height: d.spacing16),
        Text(g(g.l.componentSeekBar), style: t.typography.label),
        SizedBox(height: d.spacing8),
        Container(
          padding: EdgeInsetsDirectional.all(d.spacing12),
          decoration: BoxDecoration(
            gradient: t.drawables.glassPlayer.gradient(fromTop: false),
            color: t.colors.playerCanvas,
            borderRadius: BorderRadius.circular(d.cornerMedium),
          ),
          child: Row(
            children: [
              Text(
                VkFormat.timecode(84000000),
                style: seek.bubble.textStyle.copyWith(
                  color: t.colors.playerControlsContent,
                ),
              ),
              SizedBox(width: d.spacing8),
              Expanded(
                child: SizedBox(
                  height: seek.thumbSize,
                  child: CustomPaint(
                    painter: _SeekPainter(seek, played: 0.27, buffered: 0.5),
                  ),
                ),
              ),
              SizedBox(width: d.spacing8),
              Text(
                VkFormat.timecode(312000000),
                style: seek.bubble.textStyle.copyWith(
                  color: t.colors.playerControlsContent,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _SeekPainter extends CustomPainter {
  _SeekPainter(this.style, {required this.played, required this.buffered});

  final VkSeekBarStyle style;
  final double played;
  final double buffered;

  @override
  void paint(Canvas canvas, Size size) {
    final y = size.height / 2;
    final h = style.trackHeight;
    RRect bar(double from, double to) => RRect.fromLTRBR(
      size.width * from,
      y - h / 2,
      size.width * to,
      y + h / 2,
      Radius.circular(h / 2),
    );
    canvas
      ..drawRRect(bar(0, 1), Paint()..color = style.track)
      ..drawRRect(bar(0, buffered), Paint()..color = style.buffered)
      ..drawRRect(bar(0, played), Paint()..color = style.played)
      ..drawCircle(
        Offset(size.width * played, y),
        style.thumbSize / 2,
        Paint()..color = style.thumb.normal,
      );
  }

  @override
  bool shouldRepaint(_SeekPainter old) =>
      old.style != style || old.played != played || old.buffered != buffered;
}

class _TypographySamples extends StatelessWidget {
  const _TypographySamples();

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final key in VkTokenKeys.ofType(VkTokenType.typography))
          Padding(
            padding: EdgeInsetsDirectional.only(bottom: t.dimensions.spacing8),
            child: Text(
              key == VkTokenKeys.timecode
                  ? g.l.timecodeRange(
                      VkFormat.timecode(84000000),
                      VkFormat.timecode(312000000),
                    )
                  : g(
                      g.l.typographySample(
                        key.key,
                        VkFormat.number(s, t.typography[key].fontSize ?? 0),
                      ),
                    ),
              style: t.typography[key],
            ),
          ),
      ],
    );
  }
}

class _DimensionSamples extends StatelessWidget {
  const _DimensionSamples();

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final spacing = [
      VkTokenKeys.spacing4,
      VkTokenKeys.spacing8,
      VkTokenKeys.spacing12,
      VkTokenKeys.spacing16,
      VkTokenKeys.spacing24,
      VkTokenKeys.spacing32,
    ];
    final corners = [
      VkTokenKeys.cornerSmall,
      VkTokenKeys.cornerMedium,
      VkTokenKeys.cornerLarge,
      VkTokenKeys.cornerXLarge,
    ];
    String label(VkTokenKey k) =>
        g(g.l.dimensionValue(k.key.split('.').last, VkFormat.number(s, d[k])));
    return Wrap(
      spacing: d.spacing16,
      runSpacing: d.spacing12,
      crossAxisAlignment: WrapCrossAlignment.end,
      children: [
        for (final k in spacing)
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: d[k],
                height: d.targetMin,
                color: t.colors.selection,
              ),
              Text(label(k), style: t.typography.caption),
            ],
          ),
        for (final k in corners)
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: d.targetMin,
                height: d.targetMin,
                decoration: BoxDecoration(
                  color: t.colors.primaryContainer,
                  border: Border.all(
                    color: t.colors.primary,
                    width: d.borderWidth,
                  ),
                  borderRadius: BorderRadius.circular(d[k]),
                ),
              ),
              Text(label(k), style: t.typography.caption),
            ],
          ),
      ],
    );
  }
}

class _AnimationSample extends StatefulWidget {
  const _AnimationSample();

  @override
  State<_AnimationSample> createState() => _AnimationSampleState();
}

class _AnimationSampleState extends State<_AnimationSample> {
  bool _on = false;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final a = t.animations;
    final d = t.dimensions;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Semantics(
              label: g(g.l.animationToggle),
              child: Switch(
                value: _on,
                onChanged: (v) => setState(() => _on = v),
              ),
            ),
            SizedBox(width: d.spacing12),
            Expanded(
              child: AnimatedAlign(
                duration: a.normal.duration,
                curve: a.normal.curve,
                alignment: _on
                    ? AlignmentDirectional.centerEnd
                    : AlignmentDirectional.centerStart,
                child: Container(
                  width: d.targetMin,
                  height: d.icon24,
                  decoration: BoxDecoration(
                    color: t.colors.primary,
                    borderRadius: BorderRadius.circular(d.cornerFull),
                  ),
                ),
              ),
            ),
          ],
        ),
        Text(
          g(
            g.l.animationDurations(
              a.press.duration.inMilliseconds,
              a.small.duration.inMilliseconds,
              a.normal.duration.inMilliseconds,
              a.page.duration.inMilliseconds,
            ),
          ),
          style: t.typography.timecode,
        ),
      ],
    );
  }
}

class _ErrorTexts extends StatelessWidget {
  const _ErrorTexts();

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final s = VkStrings.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final code in ErrorCode.values)
          Padding(
            padding: EdgeInsetsDirectional.only(bottom: t.dimensions.spacing4),
            child: Text(
              g(g.l.errorLine(code.wireName, s.error(code))),
              style: t.typography.bodySmall,
            ),
          ),
      ],
    );
  }
}

/// Links to the component and Fake-driven demo pages.
class _DemoLinks extends StatelessWidget {
  const _DemoLinks();

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final g = GalleryText.of(context);
    final d = t.dimensions;
    Widget link(String label, Widget Function() page) => VkButton(
      label: label,
      variant: VkButtonVariant.secondary,
      onPressed: () =>
          Navigator.of(context)
              .push(MaterialPageRoute<void>(builder: (_) => page())),
    );
    return Wrap(
      spacing: d.spacing8,
      runSpacing: d.spacing8,
      children: [
        link(g(g.l.navComponents), () => const ComponentsPage()),
        link(g(g.l.navPlayer), () => const PlayerDemoPage()),
        link(g(g.l.navImageViewer), () => const ImageDemoPage()),
        link(g(g.l.navMultiView), () => const MultiViewDemoPage()),
        link(g(g.l.navEditor), () => const EditDemoPage()),
        link(g(g.l.navFeatures), () => const FeatureSwitchPage()),
      ],
    );
  }
}

/// Settings choice of the gallery, drawn from `component.chip.default`
/// (R1-13: the Material chip's selected colours did not reach 4.5:1).
class GalleryChoice extends StatelessWidget {
  /// Creates a choice.
  const GalleryChoice({
    super.key,
    required this.label,
    required this.selected,
    required this.onPressed,
    this.swatch,
  });

  /// Text.
  final String label;

  /// Selected.
  final bool selected;

  /// Picks it.
  final VoidCallback onPressed;

  /// Colour sample (host primary presets).
  final Color? swatch;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    return VkPressable(
      style: t.components.chip,
      semanticLabel: label,
      selected: selected,
      onPressed: onPressed,
      builder: (context, box) => Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (swatch case final c?) ...[
            DecoratedBox(
              decoration: BoxDecoration(
                color: c,
                shape: BoxShape.circle,
                border: Border.all(color: box.content, width: d.borderWidth),
              ),
              child: SizedBox.square(dimension: d.icon16),
            ),
            SizedBox(width: d.spacing8),
          ],
          Text(label, style: box.textStyle),
        ],
      ),
    );
  }
}
