/// VideoKit Flutter UI (03, 14 §4–§7). Depends only on `videokit_api`.
///
/// Exports the theme (seven SkinKit-aligned token categories),
/// localization, formatting and layout foundations, common components and
/// UI-01/02/04/09 (M0-B2). Controllers, `VkSelector`, `CommandDispatcher`
/// and `AutoHidePolicy` are internal (14 §4.1).
library;

export 'src/common/vk_badge.dart';
export 'src/common/vk_buttons.dart';
export 'src/common/vk_pressable.dart';
export 'src/common/vk_segmented.dart';
export 'src/common/vk_sheet_host.dart';
export 'src/common/vk_slider.dart';
export 'src/common/vk_switch.dart';
export 'src/editor/editor_autosave.dart';
export 'src/editor/editor_controller.dart';
export 'src/editor/editor_panels.dart';
export 'src/editor/timeline_scale.dart';
export 'src/editor/timeline_view.dart';
export 'src/editor/video_kit_editor.dart';
export 'src/export/export_panel.dart';
export 'src/foundation/audio_grant.dart';
export 'src/foundation/feature_scope.dart';
export 'src/foundation/format.dart';
export 'src/foundation/layout_class.dart';
export 'src/host_action/host_action_bar.dart';
export 'src/image_viewer/image_info_sheet.dart';
export 'src/image_viewer/video_kit_image_viewer.dart';
export 'src/l10n/gen/videokit_localizations.dart';
export 'src/l10n/pseudo.dart';
export 'src/mask/coverage_check_sheet.dart';
export 'src/mask/coverage_strip.dart';
export 'src/mask/mask_editor.dart';
export 'src/mask/mask_overlay.dart';
export 'src/l10n/vk_strings.dart';
export 'src/player/media_info_sheet.dart';
export 'src/player/media_surface.dart' show VideoKitPictureBuilder;
export 'src/player/track_settings_sheet.dart';
export 'src/player/video_kit_player.dart';
export 'src/player/vk_seek_bar.dart';
export 'src/slot/audio_coordinator.dart';
export 'src/slot/multi_view_scaffold.dart';
export 'src/slot/video_kit_slot.dart';
export 'src/slot/video_kit_slot_grid.dart';
export 'src/slot/visibility_reporter.dart';
export 'src/state_view/state_mapping.dart';
export 'src/state_view/capabilities_view.dart';
export 'src/state_view/state_view.dart';
export 'src/theme/contrast.dart';
export 'src/theme/default_theme_source.dart';
export 'src/theme/default_tokens.dart';
export 'src/theme/theme_data.dart';
export 'src/theme/theme_scope.dart';
export 'src/theme/theme_source.dart';
export 'src/theme/tokens/vk_animations.dart';
export 'src/theme/tokens/vk_colors.dart';
export 'src/theme/tokens/vk_component_styles.dart';
export 'src/theme/tokens/vk_contrast_pairs.dart';
export 'src/theme/tokens/vk_dimensions.dart';
export 'src/theme/tokens/vk_drawables.dart';
export 'src/theme/tokens/vk_icons.dart';
export 'src/theme/tokens/vk_token_keys.dart';
export 'src/theme/tokens/vk_typography.dart';
