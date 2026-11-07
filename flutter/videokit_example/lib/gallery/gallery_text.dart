import 'package:flutter/widgets.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../l10n/gen/example_localizations.dart';

/// Example-app text from `lib/l10n/app_zh.arb`, pseudo-transformed under
/// [VkPseudo.locale] like VideoKit's own strings (13 §3.1).
final class GalleryText {
  GalleryText._(this.l, this._pseudo);

  /// Text for [context]; falls back to Chinese when the delegate is absent.
  factory GalleryText.of(BuildContext context) => GalleryText._(
    Localizations.of<ExampleLocalizations>(context, ExampleLocalizations) ??
        lookupExampleLocalizations(const Locale('zh')),
    VkPseudo.isPseudo(Localizations.maybeLocaleOf(context)),
  );

  /// Generated localizations.
  final ExampleLocalizations l;
  final bool _pseudo;

  /// Applies pseudo-localization when active.
  String call(String text) => _pseudo ? VkPseudo.transform(text) : text;
}
