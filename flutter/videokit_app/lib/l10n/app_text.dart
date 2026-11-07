import 'package:flutter/widgets.dart';
import 'package:intl/intl.dart' as intl;
import 'package:videokit_ui/videokit_ui.dart';

import 'gen/app_localizations.dart';

/// App text from `lib/l10n/app_zh.arb`, pseudo-transformed under
/// [VkPseudo.locale] like the module's strings (13 §3.1).
final class AppText {
  AppText._(this.l, this._pseudo, this._locale);

  /// Text for [context]; Chinese when the delegate is absent.
  factory AppText.of(BuildContext context) {
    final locale = Localizations.maybeLocaleOf(context);
    return AppText._(
      Localizations.of<AppLocalizations>(context, AppLocalizations) ??
          lookupAppLocalizations(const Locale('zh')),
      VkPseudo.isPseudo(locale),
      locale?.toLanguageTag() ?? 'zh',
    );
  }

  /// Generated localizations.
  final AppLocalizations l;
  final bool _pseudo;
  final String _locale;

  /// Applies pseudo-localization when active.
  String call(String text) => _pseudo ? VkPseudo.transform(text) : text;

  /// "刚刚 / 5 分钟前 / 2 小时前 / 昨天 / 3 天前 / 2026/10/3".
  String relative(DateTime then, DateTime now) {
    final d = now.difference(then);
    if (d.inMinutes < 1) return this(l.timeJustNow);
    if (d.inHours < 1) return this(l.timeMinutes(d.inMinutes));
    final today = DateTime(now.year, now.month, now.day);
    final day = DateTime(then.year, then.month, then.day);
    final days = today.difference(day).inDays;
    if (days == 0) return this(l.timeHours(d.inHours));
    if (days == 1) return this(l.timeYesterday);
    if (days < 7) return this(l.timeDays(days));
    final tag = _locale.startsWith('zh') ? 'zh' : _locale;
    return this(intl.DateFormat.yMd(tag).format(then));
  }
}
