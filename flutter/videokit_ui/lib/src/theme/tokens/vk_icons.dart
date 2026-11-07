import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'vk_token_keys.dart';

/// Icon tokens (`icon.<name>`). Hosts may replace any icon (03 §5.1).
/// Unknown names resolve to `icon.unknown`. Defaults use Material Icons
/// Rounded (Apache-2.0, bundled with Flutter).
@immutable
class VkIcons extends ThemeExtension<VkIcons> {
  /// Creates icons; [overrides] are keyed by icon name or full key.
  VkIcons([Map<String, IconData> overrides = const {}])
    : _icons = Map.unmodifiable({
        ..._defaults,
        for (final e in overrides.entries)
          (e.key.startsWith('icon.') ? e.key.substring(5) : e.key): e.value,
      });

  static const Map<String, IconData> _defaults = {
    'play': Icons.play_arrow_rounded,
    'pause': Icons.pause_rounded,
    'seekback': Icons.replay_10_rounded,
    'seekforward': Icons.forward_10_rounded,
    'volume': Icons.volume_up_rounded,
    'mute': Icons.volume_off_rounded,
    'subtitles': Icons.subtitles_rounded,
    'audiotrack': Icons.audiotrack_rounded,
    'speed': Icons.speed_rounded,
    'rotate': Icons.rotate_right_rounded,
    'orientationlock': Icons.screen_lock_rotation_rounded,
    'fullscreen': Icons.fullscreen_rounded,
    'exitfullscreen': Icons.fullscreen_exit_rounded,
    'edit': Icons.content_cut_rounded,
    'more': Icons.more_vert_rounded,
    'back': Icons.arrow_back_rounded,
    'close': Icons.close_rounded,
    'retry': Icons.refresh_rounded,
    'split': Icons.vertical_split_rounded,
    'trim': Icons.straighten_rounded,
    'delete': Icons.delete_outline_rounded,
    'undo': Icons.undo_rounded,
    'redo': Icons.redo_rounded,
    'mask': Icons.blur_on_rounded,
    'face': Icons.face_rounded,
    'object': Icons.center_focus_strong_rounded,
    'export': Icons.ios_share_rounded,
    'check': Icons.check_rounded,
    'warning': Icons.warning_amber_rounded,
    'info': Icons.info_outline_rounded,
    'error': Icons.error_outline_rounded,
    'lock': Icons.lock_outline_rounded,
    'demo': Icons.science_outlined,
    'favorite': Icons.favorite_rounded,
    'favoriteborder': Icons.favorite_border_rounded,
    'tag': Icons.sell_outlined,
    'share': Icons.share_rounded,
    'fit': Icons.fit_screen_rounded,
    'originalsize': Icons.photo_size_select_actual_outlined,
    'previous': Icons.chevron_left_rounded,
    'next': Icons.chevron_right_rounded,
    'loop': Icons.repeat_rounded,
    'unknown': Icons.help_outline_rounded,
  };

  final Map<String, IconData> _icons;

  /// Icon names.
  Iterable<String> get names => _icons.keys;

  /// Icon for [name] (with or without the `icon.` prefix).
  IconData resolve(String name) {
    final n = name.startsWith('icon.') ? name.substring(5) : name;
    return _icons[n] ?? _icons['unknown']!;
  }

  IconData get play => resolve('play');
  IconData get pause => resolve('pause');
  IconData get demo => resolve('demo');
  IconData get check => resolve('check');
  IconData get warning => resolve('warning');
  IconData get error => resolve('error');
  IconData get info => resolve('info');

  /// Registered names with defaults (for completeness checks).
  static Iterable<String> get defaultNames => _defaults.keys;

  @override
  VkIcons copyWith({Map<String, IconData>? overrides}) =>
      overrides == null ? this : VkIcons({..._icons, ...overrides});

  @override
  VkIcons lerp(covariant VkIcons? other, double t) =>
      t < 0.5 || other == null ? this : other;

  @override
  bool operator ==(Object other) =>
      other is VkIcons && mapEquals(other._icons, _icons);

  @override
  int get hashCode => Object.hashAllUnordered(
    _icons.entries.map((e) => Object.hash(e.key, e.value)),
  );
}

/// Name kept from 03 §5.1 for host-facing docs.
typedef VideoKitIcons = VkIcons;

/// Ensures the registry and defaults agree (used by tests).
@visibleForTesting
bool vkIconsMatchRegistry() =>
    VkTokenKeys.iconNames.toSet().containsAll(VkIcons.defaultNames) &&
    VkIcons.defaultNames.toSet().containsAll(VkTokenKeys.iconNames);
