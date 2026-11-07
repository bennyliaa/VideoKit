// VideoKit literal lint (14 §11.3) — reusable replacement for the planned
// custom_lint plugin (see M0-B6 report §2.4):
//
//   dart run tools/vk_lints/vk_literal_lint.dart videokit_ui/lib/src
//
// Rules (theme/ and l10n/ directories are exempt):
//   VK001 colour literal        Color(0x…), Color.fromARGB/RGBO(…), Colors.*
//   VK002 font size literal     fontSize: <number>
//   VK003 size literal          a bare number as an EdgeInsets*/SizedBox
//                               argument (multipliers such as
//                               `d.targetMin * 2` are allowed)
//   VK004 text literal          Text('…'), label:/semanticLabel:/title:/
//                               tooltip:/message: '…' (user-visible text
//                               comes from ARB)
// Suppress one line with `// vk-lint: ignore VK00x <reason>`.
import 'dart:io';

/// One finding.
final class LintFinding {
  /// Creates a finding.
  const LintFinding(this.path, this.line, this.rule, this.text);

  /// File path.
  final String path;

  /// 1-based line.
  final int line;

  /// Rule ID.
  final String rule;

  /// Source line.
  final String text;

  @override
  String toString() => '$path:$line: $rule ${text.trim()}';
}

/// Directories exempt from the rules.
const List<String> exemptDirectories = ['theme', 'l10n', 'gen'];

final RegExp _colour = RegExp(
  r'\bColor\(\s*0x|\bColor\.from(?:ARGB|RGBO)\(|\bColors\.',
);
final RegExp _fontSize = RegExp(r'fontSize:\s*-?\d');
final RegExp _textLiteral = RegExp(
  r'''\bText\(\s*['"]|\b(?:label|semanticLabel|title|tooltip|message|hint):\s*['"]''',
);
final RegExp _sizeCall = RegExp(
  r'\b(?:EdgeInsets(?:Directional)?\.(?:all|symmetric|only|fromLTRB|fromSTEB)|SizedBox(?:\.square|\.fromSize)?)\(',
);
final RegExp _bareNumber = RegExp(r'^\s*(?:\w+\s*:\s*)?-?\d+(?:\.\d+)?\s*$');
final RegExp _zero = RegExp(r'^\s*(?:\w+\s*:\s*)?0(?:\.0)?\s*$');

/// Top-level arguments of the call whose `(` is at [open] in [src].
List<String> _arguments(String src, int open) {
  final args = <String>[];
  var depth = 0;
  var start = open + 1;
  String? quote;
  for (var i = open; i < src.length; i++) {
    final c = src[i];
    if (quote != null) {
      if (c == quote && src[i - 1] != r'\') quote = null;
      continue;
    }
    if (c == "'" || c == '"') {
      quote = c;
    } else if (c == '(' || c == '[' || c == '{') {
      depth++;
    } else if (c == ')' || c == ']' || c == '}') {
      depth--;
      if (depth == 0) {
        args.add(src.substring(start, i));
        return args;
      }
    } else if (c == ',' && depth == 1) {
      args.add(src.substring(start, i));
      start = i + 1;
    }
  }
  return args;
}

bool _suppressed(String line, String rule) =>
    line.contains('vk-lint: ignore $rule') ||
    line.contains('vk-lint: ignore all');

/// Lints one Dart source.
List<LintFinding> lintSource(String path, String src) {
  final out = <LintFinding>[];
  final lines = src.split('\n');
  int lineOf(int offset) => '\n'.allMatches(src.substring(0, offset)).length;
  for (final (i, l) in lines.indexed) {
    final code = l.split('//').first;
    void check(RegExp re, String rule) {
      if (re.hasMatch(code) && !_suppressed(l, rule)) {
        out.add(LintFinding(path, i + 1, rule, l));
      }
    }

    check(_colour, 'VK001');
    check(_fontSize, 'VK002');
    check(_textLiteral, 'VK004');
  }
  for (final m in _sizeCall.allMatches(src)) {
    final open = m.end - 1;
    final line = lineOf(m.start);
    final text = lines[line];
    if (text.trimLeft().startsWith('//') || _suppressed(text, 'VK003')) {
      continue;
    }
    final args = _arguments(src, open);
    final bad = args.where(
      (a) => _bareNumber.hasMatch(a) && !_zero.hasMatch(a),
    );
    if (bad.isNotEmpty) out.add(LintFinding(path, line + 1, 'VK003', text));
  }
  return out;
}

/// Lints every `.dart` file under [roots], skipping [exemptDirectories].
List<LintFinding> lintDirectories(List<String> roots) {
  final out = <LintFinding>[];
  for (final root in roots) {
    final dir = Directory(root);
    if (!dir.existsSync()) continue;
    for (final f in dir.listSync(recursive: true).whereType<File>()) {
      if (!f.path.endsWith('.dart')) continue;
      final parts = f.uri.pathSegments;
      if (parts.any(exemptDirectories.contains)) continue;
      out.addAll(lintSource(f.path, f.readAsStringSync()));
    }
  }
  return out;
}

void main(List<String> args) {
  final findings = lintDirectories(args.isEmpty ? ['lib'] : args);
  for (final f in findings) {
    stderr.writeln(f);
  }
  stdout.writeln('vk_literal_lint: ${findings.length} finding(s)');
  if (findings.isNotEmpty) exitCode = 1;
}
