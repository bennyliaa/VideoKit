import 'package:flutter/painting.dart';

import 'contrast.dart';
import 'tokens/vk_component_styles.dart';
import 'tokens/vk_dimensions.dart';
import 'tokens/vk_drawables.dart';
import 'tokens/vk_token_keys.dart';
import 'tokens/vk_typography.dart';
import 'tokens/vk_colors.dart';

/// Default token values of UI design V1.0 (14 §7.2, frozen 2026-11-07).
abstract final class VkDefaultTokens {
  static const Color _black60 = Color(0x99000000);

  /// Dark colours (key → value).
  static final Map<String, Color> darkColors = Map.unmodifiable({
    VkTokenKeys.background.key: const Color(0xFF0E1015),
    VkTokenKeys.surface.key: const Color(0xFF171A21),
    VkTokenKeys.surfaceVariant.key: const Color(0xFF1F232C),
    VkTokenKeys.surfaceHigh.key: const Color(0xFF2A2F3A),
    VkTokenKeys.border.key: const Color(0xFF343A46),
    VkTokenKeys.borderStrong.key: const Color(0xFF6E7582),
    VkTokenKeys.divider.key: const Color(0xFF262B35),
    VkTokenKeys.focusRing.key: const Color(0xFF4CC9F0),
    VkTokenKeys.scrim.key: _black60,
    VkTokenKeys.textPrimary.key: const Color(0xFFEEF0F4),
    VkTokenKeys.textSecondary.key: const Color(0xFFA3A9B5),
    VkTokenKeys.textTertiary.key: const Color(0xFF858C9B),
    VkTokenKeys.primary.key: const Color(0xFFFF7A45),
    VkTokenKeys.onPrimary.key: const Color(0xFF1A0E08),
    VkTokenKeys.primaryContainer.key: const Color(0xFF3A2219),
    VkTokenKeys.onPrimaryContainer.key: const Color(0xFFFFD3C0),
    VkTokenKeys.disabledContent.key: const Color(0xFF6E7582),
    VkTokenKeys.disabledContainer.key: const Color(0xFF1F232C),
    VkTokenKeys.success.key: const Color(0xFF34D399),
    VkTokenKeys.successContent.key: const Color(0xFF062A1C),
    VkTokenKeys.successContainer.key: const Color(0xFF123A2C),
    VkTokenKeys.warning.key: const Color(0xFFFBBF24),
    VkTokenKeys.warningContent.key: const Color(0xFF2A1E02),
    VkTokenKeys.warningContainer.key: const Color(0xFF3A2E10),
    VkTokenKeys.error.key: const Color(0xFFF87171),
    VkTokenKeys.errorContent.key: const Color(0xFF2E0A0A),
    VkTokenKeys.errorContainer.key: const Color(0xFF3D1818),
    VkTokenKeys.info.key: const Color(0xFF4CC9F0),
    VkTokenKeys.infoContent.key: const Color(0xFF05222C),
    VkTokenKeys.infoContainer.key: const Color(0xFF123340),
    VkTokenKeys.shadowFloating.key: const Color(0x3D000000),
    VkTokenKeys.shadowModal.key: const Color(0x66000000),
    VkTokenKeys.selection.key: const Color(0xFF4CC9F0),
    VkTokenKeys.trackTracked.key: const Color(0xFF34D399),
    VkTokenKeys.trackLowConfidence.key: const Color(0xFFFBBF24),
    VkTokenKeys.trackAmbiguous.key: const Color(0xFFA78BFA),
    VkTokenKeys.trackLost.key: const Color(0xFFF87171),
    VkTokenKeys.demo.key: const Color(0xFFEC4899),
    VkTokenKeys.demoContent.key: const Color(0xFF000000),
    VkTokenKeys.playerCanvas.key: const Color(0xFF000000),
    VkTokenKeys.playerControlsContent.key: const Color(0xFFFFFFFF),
  });

  /// Light colours (key → value).
  static final Map<String, Color> lightColors = Map.unmodifiable({
    VkTokenKeys.background.key: const Color(0xFFF4F5F7),
    VkTokenKeys.surface.key: const Color(0xFFFFFFFF),
    VkTokenKeys.surfaceVariant.key: const Color(0xFFF0F1F4),
    VkTokenKeys.surfaceHigh.key: const Color(0xFFE3E6EB),
    VkTokenKeys.border.key: const Color(0xFFD5D9E0),
    VkTokenKeys.borderStrong.key: const Color(0xFF7C828E),
    VkTokenKeys.divider.key: const Color(0xFFE6E8EC),
    VkTokenKeys.focusRing.key: const Color(0xFF0E7FA8),
    VkTokenKeys.scrim.key: _black60,
    VkTokenKeys.textPrimary.key: const Color(0xFF15181E),
    VkTokenKeys.textSecondary.key: const Color(0xFF4B5260),
    VkTokenKeys.textTertiary.key: const Color(0xFF646B78),
    VkTokenKeys.primary.key: const Color(0xFFC2410C),
    VkTokenKeys.onPrimary.key: const Color(0xFFFFFFFF),
    VkTokenKeys.primaryContainer.key: const Color(0xFFFFE8DC),
    VkTokenKeys.onPrimaryContainer.key: const Color(0xFF7A2E06),
    VkTokenKeys.disabledContent.key: const Color(0xFF8A909B),
    VkTokenKeys.disabledContainer.key: const Color(0xFFF0F1F4),
    VkTokenKeys.success.key: const Color(0xFF047857),
    VkTokenKeys.successContent.key: const Color(0xFFFFFFFF),
    VkTokenKeys.successContainer.key: const Color(0xFFDDF6EC),
    VkTokenKeys.warning.key: const Color(0xFFA16207),
    VkTokenKeys.warningContent.key: const Color(0xFFFFFFFF),
    VkTokenKeys.warningContainer.key: const Color(0xFFFDF1D8),
    VkTokenKeys.error.key: const Color(0xFFC53030),
    VkTokenKeys.errorContent.key: const Color(0xFFFFFFFF),
    VkTokenKeys.errorContainer.key: const Color(0xFFFBE3E3),
    VkTokenKeys.info.key: const Color(0xFF0E7FA8),
    VkTokenKeys.infoContent.key: const Color(0xFFFFFFFF),
    VkTokenKeys.infoContainer.key: const Color(0xFFDDF1F8),
    VkTokenKeys.shadowFloating.key: const Color(0x3D000000),
    VkTokenKeys.shadowModal.key: const Color(0x66000000),
    VkTokenKeys.selection.key: const Color(0xFF4CC9F0),
    VkTokenKeys.trackTracked.key: const Color(0xFF047857),
    VkTokenKeys.trackLowConfidence.key: const Color(0xFFB7791F),
    VkTokenKeys.trackAmbiguous.key: const Color(0xFF7C5CD6),
    VkTokenKeys.trackLost.key: const Color(0xFFD64545),
    VkTokenKeys.demo.key: const Color(0xFFD63384),
    VkTokenKeys.demoContent.key: const Color(0xFF000000),
    VkTokenKeys.playerCanvas.key: const Color(0xFF000000),
    VkTokenKeys.playerControlsContent.key: const Color(0xFFFFFFFF),
  });

  /// `drawable.glass.player`: black, 0.55, no blur, fallback scrim.
  static VkDrawables drawables(VkColors c) => VkDrawables(
    glassPlayer: VkGlass(
      tint: VkContrast.black,
      opacity: 0.55,
      fallbackSurface: c.scrim,
    ),
  );

  /// Overlay shares for interaction states (pressed 12 %, hovered 8 %).
  static const double pressedOverlay = 0.12;
  static const double hoveredOverlay = 0.08;

  /// Component styles derived from colours, typography and dimensions, so a
  /// host primary override flows into buttons/chips automatically.
  static VkComponentStyles components(
    VkColors c,
    VkTypography t,
    VkDimensions d,
  ) {
    VkStateStyle<VkBoxStyle> states(
      VkBoxStyle normal, {
      required VkBoxStyle selected,
    }) {
      Color over(Color base, Color content, double a) =>
          VkContrast.blend(content, base, a);
      return VkStateStyle(
        normal: normal,
        pressed: normal.copyWith(
          background: over(normal.background, normal.content, pressedOverlay),
        ),
        hovered: normal.copyWith(
          background: over(normal.background, normal.content, hoveredOverlay),
        ),
        focused: normal.copyWith(
          border: c.focusRing,
          borderWidth: d.focusRingWidth,
        ),
        disabled: normal.copyWith(
          background: normal.background.a == 0
              ? normal.background
              : c.disabledContainer,
          content: c.disabledContent,
          border: normal.borderWidth > 0 ? c.disabledContainer : normal.border,
        ),
        selected: selected,
      );
    }

    const transparent = Color(0x00000000);
    final buttonPadding = EdgeInsetsDirectional.symmetric(
      horizontal: d.spacing16,
      vertical: d.spacing12,
    );
    VkBoxStyle box({
      required Color background,
      required Color content,
      Color border = transparent,
      double? borderWidth,
      double? radius,
      EdgeInsetsDirectional? padding,
      double? minSize,
      TextStyle? text,
    }) => VkBoxStyle(
      background: background,
      content: content,
      border: border,
      borderWidth: borderWidth ?? 0,
      radius: radius ?? d.cornerMedium,
      padding: padding ?? buttonPadding,
      minSize: minSize ?? d.targetMin,
      textStyle: (text ?? t.label).copyWith(color: content),
    );

    final primary = box(background: c.primary, content: c.onPrimary);
    final secondary = box(
      background: c.surfaceHigh,
      content: c.textPrimary,
      border: c.borderStrong,
      borderWidth: d.borderWidth,
    );
    final text = box(background: transparent, content: c.primary);
    final icon = box(
      background: transparent,
      content: c.textPrimary,
      radius: d.cornerFull,
      padding: EdgeInsetsDirectional.all(d.spacing12),
    );
    final chipPadding = EdgeInsetsDirectional.symmetric(
      horizontal: d.spacing12,
      vertical: d.spacing8,
    );
    final chip = box(
      background: c.surfaceVariant,
      content: c.textSecondary,
      border: c.borderStrong,
      borderWidth: d.borderWidth,
      radius: d.cornerFull,
      padding: chipPadding,
    );
    final badge = box(
      background: c.primary,
      content: c.onPrimary,
      radius: d.cornerFull,
      padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing4),
      minSize: d.badgeSize,
      text: t.caption,
    );
    final selectedBox = primary.copyWith(
      background: c.primaryContainer,
      content: c.onPrimaryContainer,
    );
    // Panels, menus and toasts: no interaction states of their own.
    final sheet = box(
      background: c.surface,
      content: c.textPrimary,
      radius: d.cornerXLarge,
      padding: EdgeInsetsDirectional.all(d.spacing16),
      minSize: 0,
      text: t.body,
    );
    final menu = box(
      background: c.surfaceHigh,
      content: c.textPrimary,
      radius: d.cornerMedium,
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing16,
        vertical: d.spacing12,
      ),
      text: t.body,
    );
    final toast = box(
      background: c.surfaceHigh,
      content: c.textPrimary,
      radius: d.cornerMedium,
      padding: EdgeInsetsDirectional.symmetric(
        horizontal: d.spacing16,
        vertical: d.spacing12,
      ),
      minSize: 0,
      text: t.bodySmall,
    );
    // Host action item over the picture: translucent dark disc, white icon;
    // selected = primary fill (14 §5.4).
    final hostItem = box(
      background: VkContrast.black.withValues(alpha: 0.35),
      content: c.playerControlsContent,
      radius: d.cornerFull,
      padding: EdgeInsetsDirectional.all(d.spacing12),
      text: t.caption.copyWith(color: c.playerControlsContent),
    );
    final controls = c.playerControlsContent;
    return VkComponentStyles(
      buttonPrimary: states(primary, selected: selectedBox),
      buttonSecondary: states(
        secondary,
        selected: selectedBox.copyWith(
          border: c.primary,
          borderWidth: d.borderWidth,
        ),
      ),
      buttonText: states(
        text,
        selected: text.copyWith(background: c.primaryContainer),
      ),
      buttonIcon: states(
        icon,
        selected: icon.copyWith(
          background: c.primaryContainer,
          content: c.onPrimaryContainer,
        ),
      ),
      chip: states(
        chip,
        selected: chip.copyWith(
          background: c.primaryContainer,
          content: c.onPrimaryContainer,
          border: c.primary,
        ),
      ),
      badge: VkStateStyle.all(badge),
      sheet: VkStateStyle.all(sheet),
      menu: states(
        menu,
        selected: menu.copyWith(
          background: c.primaryContainer,
          content: c.onPrimaryContainer,
        ),
      ),
      toast: VkStateStyle.all(toast),
      progress: VkProgressStyle(
        track: c.surfaceHigh,
        indicator: c.primary,
        height: d.seekBarTrack,
        radius: d.cornerFull,
      ),
      hostActionBar: VkHostActionBarStyle(
        item: states(
          hostItem,
          selected: hostItem.copyWith(
            background: c.primary,
            content: c.onPrimary,
          ),
        ),
        pendingIndicator: c.warning,
        label: t.caption.copyWith(color: c.playerControlsContent),
        badge: badge.copyWith(background: c.error, content: c.errorContent),
        spacing: d.spacing8,
      ),
      // 14 §7.2 (M0-B2 review): on ordinary surfaces the track must reach
      // 3:1 against the surface in both modes.
      sliderSurface: VkSeekBarStyle(
        track: c.borderStrong,
        buffered: c.textTertiary,
        played: c.primary,
        preview: c.primary.withValues(alpha: 0.6),
        thumb: VkStateStyle(
          normal: c.primary,
          pressed: c.primary,
          focused: c.focusRing,
          disabled: c.disabledContent,
          selected: c.primary,
          hovered: c.primary,
        ),
        trackHeight: d.seekBarTrack,
        trackHeightActive: d.seekBarTrackActive,
        thumbSize: d.seekBarThumb,
        bubble: box(
          background: c.surfaceHigh,
          content: c.textPrimary,
          radius: d.cornerSmall,
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4,
          ),
          minSize: 0,
          text: t.timecode,
        ),
      ),
      seekBar: VkSeekBarStyle(
        track: controls.withValues(alpha: 0.24),
        buffered: controls.withValues(alpha: 0.48),
        played: c.primary,
        preview: c.primary.withValues(alpha: 0.6),
        thumb: VkStateStyle(
          normal: c.primary,
          pressed: c.primary,
          focused: c.focusRing,
          disabled: c.disabledContent,
          selected: c.primary,
          hovered: c.primary,
        ),
        trackHeight: d.seekBarTrack,
        trackHeightActive: d.seekBarTrackActive,
        thumbSize: d.seekBarThumb,
        bubble: box(
          background: c.surfaceHigh,
          content: c.textPrimary,
          radius: d.cornerSmall,
          padding: EdgeInsetsDirectional.symmetric(
            horizontal: d.spacing8,
            vertical: d.spacing4,
          ),
          minSize: 0,
          text: t.timecode,
        ),
      ),
    );
  }
}
