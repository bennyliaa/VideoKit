import 'package:flutter/foundation.dart';

/// Token value type (03 §5.2, SkinKit's seven categories).
enum VkTokenType {
  color,
  typography,
  dimension,
  animation,
  icon,
  drawable,
  component,
}

/// A registered token: stable SkinKit-style key (lower case, dot separated)
/// and its type. Keys are used only for host overrides and future SkinKit
/// mapping; components use the strongly typed fields (14 §7.1).
@immutable
final class VkTokenKey {
  const VkTokenKey._(this.key, this.type);

  /// Stable key, e.g. `color.surfacevariant`.
  final String key;

  /// Type.
  final VkTokenType type;

  /// Whether the token lives in the VideoKit-specific namespace.
  bool get isVideoKitSpecific => key.startsWith('apps.videokit.');

  @override
  bool operator ==(Object other) =>
      other is VkTokenKey && other.key == key && other.type == type;

  @override
  int get hashCode => Object.hash(key, type);

  @override
  String toString() => key;
}

/// Registry of every VideoKit theme token (14 §7.2), schema version 1.
abstract final class VkTokenKeys {
  static const _c = VkTokenType.color;
  static const _t = VkTokenType.typography;
  static const _d = VkTokenType.dimension;
  static const _a = VkTokenType.animation;
  static const _i = VkTokenType.icon;
  static const _r = VkTokenType.drawable;
  static const _p = VkTokenType.component;

  // ---------------------------------------------------------------- color
  static const background = VkTokenKey._('color.background', _c);
  static const surface = VkTokenKey._('color.surface', _c);
  static const surfaceVariant = VkTokenKey._('color.surfacevariant', _c);
  static const surfaceHigh = VkTokenKey._('color.surfacehigh', _c);
  static const border = VkTokenKey._('color.border', _c);
  static const borderStrong = VkTokenKey._('color.border.strong', _c);
  static const divider = VkTokenKey._('color.divider', _c);
  static const focusRing = VkTokenKey._('color.focusring', _c);
  static const scrim = VkTokenKey._('color.scrim', _c);
  static const textPrimary = VkTokenKey._('color.text.primary', _c);
  static const textSecondary = VkTokenKey._('color.text.secondary', _c);
  static const textTertiary = VkTokenKey._('color.text.tertiary', _c);
  static const primary = VkTokenKey._('color.primary', _c);
  static const onPrimary = VkTokenKey._('color.onprimary', _c);
  static const primaryContainer = VkTokenKey._('color.primarycontainer', _c);
  static const onPrimaryContainer = VkTokenKey._(
    'color.onprimarycontainer',
    _c,
  );
  static const disabledContent = VkTokenKey._('color.disabled.content', _c);
  static const disabledContainer = VkTokenKey._('color.disabled.container', _c);
  static const success = VkTokenKey._('color.status.success', _c);
  static const successContent = VkTokenKey._(
    'color.status.success.content',
    _c,
  );
  static const successContainer = VkTokenKey._(
    'color.status.success.container',
    _c,
  );
  static const warning = VkTokenKey._('color.status.warning', _c);
  static const warningContent = VkTokenKey._(
    'color.status.warning.content',
    _c,
  );
  static const warningContainer = VkTokenKey._(
    'color.status.warning.container',
    _c,
  );
  static const error = VkTokenKey._('color.status.error', _c);
  static const errorContent = VkTokenKey._('color.status.error.content', _c);
  static const errorContainer = VkTokenKey._(
    'color.status.error.container',
    _c,
  );
  static const info = VkTokenKey._('color.status.info', _c);
  static const infoContent = VkTokenKey._('color.status.info.content', _c);
  static const infoContainer = VkTokenKey._('color.status.info.container', _c);
  static const shadowFloating = VkTokenKey._('color.elevation.floating', _c);
  static const shadowModal = VkTokenKey._('color.elevation.modal', _c);
  static const selection = VkTokenKey._('apps.videokit.color.selection', _c);
  static const trackTracked = VkTokenKey._(
    'apps.videokit.color.track.tracked',
    _c,
  );
  static const trackLowConfidence = VkTokenKey._(
    'apps.videokit.color.track.lowconfidence',
    _c,
  );
  static const trackAmbiguous = VkTokenKey._(
    'apps.videokit.color.track.ambiguous',
    _c,
  );
  static const trackLost = VkTokenKey._('apps.videokit.color.track.lost', _c);
  static const demo = VkTokenKey._('apps.videokit.color.demo', _c);
  static const demoContent = VkTokenKey._(
    'apps.videokit.color.demo.content',
    _c,
  );
  static const playerCanvas = VkTokenKey._(
    'apps.videokit.color.player.canvas',
    _c,
  );
  static const playerControlsContent = VkTokenKey._(
    'apps.videokit.color.player.controls.content',
    _c,
  );

  // ----------------------------------------------------------- typography
  static const display = VkTokenKey._('typography.display', _t);
  static const titleLarge = VkTokenKey._('typography.titlelarge', _t);
  static const title = VkTokenKey._('typography.title', _t);
  static const body = VkTokenKey._('typography.body', _t);
  static const bodySmall = VkTokenKey._('typography.bodysmall', _t);
  static const label = VkTokenKey._('typography.label', _t);
  static const caption = VkTokenKey._('typography.caption', _t);
  static const timecode = VkTokenKey._('apps.videokit.typography.timecode', _t);

  // ------------------------------------------------------------ dimension
  static const spacing4 = VkTokenKey._('dimension.spacing.s4', _d);
  static const spacing8 = VkTokenKey._('dimension.spacing.s8', _d);
  static const spacing12 = VkTokenKey._('dimension.spacing.s12', _d);
  static const spacing16 = VkTokenKey._('dimension.spacing.s16', _d);
  static const spacing24 = VkTokenKey._('dimension.spacing.s24', _d);
  static const spacing32 = VkTokenKey._('dimension.spacing.s32', _d);
  static const cornerSmall = VkTokenKey._('dimension.corner.small', _d);
  static const cornerMedium = VkTokenKey._('dimension.corner.medium', _d);
  static const cornerLarge = VkTokenKey._('dimension.corner.large', _d);
  static const cornerXLarge = VkTokenKey._('dimension.corner.xlarge', _d);
  static const cornerFull = VkTokenKey._('dimension.corner.full', _d);
  static const targetMin = VkTokenKey._('dimension.target.min', _d);
  static const icon16 = VkTokenKey._('dimension.icon.s16', _d);
  static const icon20 = VkTokenKey._('dimension.icon.s20', _d);
  static const icon24 = VkTokenKey._('dimension.icon.s24', _d);
  static const borderWidth = VkTokenKey._('dimension.border.width', _d);
  static const focusRingWidth = VkTokenKey._('dimension.focusring.width', _d);
  static const floatingOffsetY = VkTokenKey._(
    'dimension.elevation.floating.offsety',
    _d,
  );
  static const floatingBlur = VkTokenKey._(
    'dimension.elevation.floating.blur',
    _d,
  );
  static const modalOffsetY = VkTokenKey._(
    'dimension.elevation.modal.offsety',
    _d,
  );
  static const modalBlur = VkTokenKey._('dimension.elevation.modal.blur', _d);
  static const controlBarHeight = VkTokenKey._(
    'apps.videokit.dimension.controlbar.height',
    _d,
  );
  static const seekBarTrack = VkTokenKey._(
    'apps.videokit.dimension.seekbar.track',
    _d,
  );
  static const seekBarTrackActive = VkTokenKey._(
    'apps.videokit.dimension.seekbar.trackactive',
    _d,
  );
  static const seekBarThumb = VkTokenKey._(
    'apps.videokit.dimension.seekbar.thumb',
    _d,
  );
  static const timelineClipRow = VkTokenKey._(
    'apps.videokit.dimension.timeline.cliprow',
    _d,
  );
  static const timelineMaskRow = VkTokenKey._(
    'apps.videokit.dimension.timeline.maskrow',
    _d,
  );
  static const timelineCoverageStrip = VkTokenKey._(
    'apps.videokit.dimension.timeline.coveragestrip',
    _d,
  );
  static const maskBoxStroke = VkTokenKey._(
    'apps.videokit.dimension.maskbox.stroke',
    _d,
  );
  static const maskBoxHandle = VkTokenKey._(
    'apps.videokit.dimension.maskbox.handle',
    _d,
  );
  static const maskBoxHandleTarget = VkTokenKey._(
    'apps.videokit.dimension.maskbox.handletarget',
    _d,
  );
  static const badgeSize = VkTokenKey._('dimension.badge.size', _d);
  static const badgeInset = VkTokenKey._('dimension.badge.inset', _d);
  static const pendingRingSize = VkTokenKey._(
    'apps.videokit.dimension.pendingring.size',
    _d,
  );
  static const pendingRingStroke = VkTokenKey._(
    'apps.videokit.dimension.pendingring.stroke',
    _d,
  );

  // ------------------------------------------------------------ animation
  static const animPress = VkTokenKey._('animation.press', _a);
  static const animSmall = VkTokenKey._('animation.small', _a);
  static const animNormal = VkTokenKey._('animation.normal', _a);
  static const animPage = VkTokenKey._('animation.page', _a);

  // ----------------------------------------------------------------- icon
  /// Icon names (registered as `icon.<name>`).
  static const List<String> iconNames = [
    'play',
    'pause',
    'seekback',
    'seekforward',
    'volume',
    'mute',
    'subtitles',
    'audiotrack',
    'speed',
    'rotate',
    'orientationlock',
    'fullscreen',
    'exitfullscreen',
    'edit',
    'more',
    'back',
    'close',
    'retry',
    'split',
    'trim',
    'delete',
    'undo',
    'redo',
    'mask',
    'face',
    'object',
    'export',
    'check',
    'warning',
    'info',
    'error',
    'lock',
    'demo',
    'favorite',
    'favoriteborder',
    'tag',
    'share',
    'fit',
    'originalsize',
    'previous',
    'next',
    'loop',
    'unknown',
  ];

  /// Icon key for [name] (`icon.<name>`).
  static VkTokenKey icon(String name) => VkTokenKey._('icon.$name', _i);

  // ------------------------------------------------------------- drawable
  static const glassPlayer = VkTokenKey._('drawable.glass.player', _r);

  // ------------------------------------------------------------ component
  static const buttonPrimary = VkTokenKey._('component.button.primary', _p);
  static const buttonSecondary = VkTokenKey._('component.button.secondary', _p);
  static const buttonText = VkTokenKey._('component.button.text', _p);
  static const buttonIcon = VkTokenKey._('component.button.icon', _p);
  static const chipDefault = VkTokenKey._('component.chip.default', _p);
  static const badgeDefault = VkTokenKey._('component.badge.default', _p);
  static const sheetDefault = VkTokenKey._('component.sheet.default', _p);
  static const menuDefault = VkTokenKey._('component.menu.default', _p);
  static const toastDefault = VkTokenKey._('component.toast.default', _p);
  static const progressDefault = VkTokenKey._('component.progress.default', _p);
  static const sliderSurface = VkTokenKey._('component.slider.surface', _p);
  static const seekBar = VkTokenKey._('apps.videokit.component.seekbar', _p);
  static const hostActionBar = VkTokenKey._(
    'apps.videokit.component.hostactionbar',
    _p,
  );

  /// Every registered key.
  static final List<VkTokenKey> all = List.unmodifiable([
    background,
    surface,
    surfaceVariant,
    surfaceHigh,
    border,
    borderStrong,
    divider,
    focusRing,
    scrim,
    textPrimary,
    textSecondary,
    textTertiary,
    primary,
    onPrimary,
    primaryContainer,
    onPrimaryContainer,
    disabledContent,
    disabledContainer,
    success,
    successContent,
    successContainer,
    warning,
    warningContent,
    warningContainer,
    error,
    errorContent,
    errorContainer,
    info,
    infoContent,
    infoContainer,
    shadowFloating,
    shadowModal,
    selection,
    trackTracked,
    trackLowConfidence,
    trackAmbiguous,
    trackLost,
    demo,
    demoContent,
    playerCanvas,
    playerControlsContent,
    display,
    titleLarge,
    title,
    body,
    bodySmall,
    label,
    caption,
    timecode,
    spacing4,
    spacing8,
    spacing12,
    spacing16,
    spacing24,
    spacing32,
    cornerSmall,
    cornerMedium,
    cornerLarge,
    cornerXLarge,
    cornerFull,
    targetMin,
    icon16,
    icon20,
    icon24,
    borderWidth,
    focusRingWidth,
    floatingOffsetY,
    floatingBlur,
    modalOffsetY,
    modalBlur,
    controlBarHeight,
    seekBarTrack,
    seekBarTrackActive,
    seekBarThumb,
    timelineClipRow,
    timelineMaskRow,
    timelineCoverageStrip,
    maskBoxStroke,
    maskBoxHandle,
    maskBoxHandleTarget,
    badgeSize,
    badgeInset,
    pendingRingSize,
    pendingRingStroke,
    animPress,
    animSmall,
    animNormal,
    animPage,
    for (final n in iconNames) icon(n),
    glassPlayer,
    buttonPrimary,
    buttonSecondary,
    buttonText,
    buttonIcon,
    chipDefault,
    badgeDefault,
    sheetDefault,
    menuDefault,
    toastDefault,
    progressDefault,
    sliderSurface,
    seekBar,
    hostActionBar,
  ]);

  static final Map<String, VkTokenKey> _byKey = {for (final k in all) k.key: k};

  /// Registered token for [key], or null.
  static VkTokenKey? byKey(String key) => _byKey[key];

  /// Keys of [type].
  static List<VkTokenKey> ofType(VkTokenType type) =>
      all.where((k) => k.type == type).toList(growable: false);
}
