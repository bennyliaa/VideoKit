// Release isolation check (14 §11.4, 04A P3) without Gradle:
//
//   dart run tool/release_isolation.dart            (from videokit_app)
//
// Walks the import/export graph from `lib/main.dart` through the workspace
// packages (via .dart_tool/package_config.json) and fails if the release
// entry point can reach `package:videokit_fake`, a `demo/` library or a
// demo asset. AOT compiles only libraries reachable from the entry point,
// so an unreachable Fake is not in the release snapshot. Exit code 1 on
// violations; the same logic runs in test/release_isolation_test.dart.
import 'dart:convert';
import 'dart:io';

/// Forbidden in the release graph.
const List<String> forbiddenPackages = ['videokit_fake'];

/// Result of a walk.
final class IsolationReport {
  /// Creates a report.
  IsolationReport(this.reachable, this.violations);

  /// Reachable library URIs (`package:` or `file:`).
  final Set<String> reachable;

  /// `importer -> imported` edges into forbidden code.
  final List<String> violations;

  /// Whether the graph is clean.
  bool get ok => violations.isEmpty;
}

final RegExp _directive = RegExp(
  r'''^\s*(?:import|export|part)\s+['"]([^'"]+)['"]''',
  multiLine: true,
);

/// Package name → lib directory, from the workspace package config.
Map<String, Directory> readPackageConfig(Directory packageRoot) {
  var dir = packageRoot.absolute;
  File? config;
  while (true) {
    final f = File('${dir.path}/.dart_tool/package_config.json');
    if (f.existsSync()) {
      config = f;
      break;
    }
    final parent = dir.parent;
    if (parent.path == dir.path) break;
    dir = parent;
  }
  if (config == null) {
    throw StateError('package_config.json not found above ${packageRoot.path}');
  }
  final json = jsonDecode(config.readAsStringSync()) as Map<String, Object?>;
  final base = config.parent.uri;
  return {
    for (final p
        in (json['packages']! as List<Object?>).cast<Map<String, Object?>>())
      p['name']! as String: Directory.fromUri(
        base
            .resolve(_dirUri(p['rootUri']! as String))
            .resolve('${p['packageUri'] ?? 'lib/'}'),
      ),
  };
}

String? _packageOf(String uri) =>
    uri.startsWith('package:') ? uri.substring(8).split('/').first : null;

/// Walks from [entry] (a file under [packageRoot]/lib).
IsolationReport checkIsolation(Directory packageRoot, String entry) {
  final packages = readPackageConfig(packageRoot);
  final selfName = RegExp(r'^name:\s*(\S+)', multiLine: true)
      .firstMatch(File('${packageRoot.path}/pubspec.yaml').readAsStringSync())!
      .group(1)!;
  File? resolve(String uri, Uri from) {
    if (uri.startsWith('dart:')) return null;
    if (uri.startsWith('package:')) {
      final name = _packageOf(uri)!;
      final lib = packages[name];
      if (lib == null) return null;
      return File.fromUri(lib.uri.resolve(uri.substring(8 + name.length + 1)));
    }
    return File.fromUri(from.resolve(uri));
  }

  String label(File f) {
    final p = f.absolute.uri.toString();
    for (final MapEntry(key: name, value: lib) in packages.entries) {
      final l = lib.absolute.uri.toString();
      if (p.startsWith(l)) return 'package:$name/${p.substring(l.length)}';
    }
    return p;
  }

  final start = File('${packageRoot.path}/lib/$entry').absolute;
  final reachable = <String>{};
  final violations = <String>[];
  final queue = [start];
  while (queue.isNotEmpty) {
    final f = queue.removeLast();
    final name = label(f);
    if (!reachable.add(name) || !f.existsSync()) continue;
    for (final m in _directive.allMatches(f.readAsStringSync())) {
      final uri = m.group(1)!;
      final target = resolve(uri, f.uri);
      if (target == null) continue;
      final targetLabel = label(target);
      final pkg = _packageOf(targetLabel);
      final demoLib =
          pkg == selfName && targetLabel.contains('/demo/') ||
          targetLabel.contains('/backend/demo_');
      if (forbiddenPackages.contains(pkg) || demoLib) {
        violations.add('$name -> $targetLabel');
        continue;
      }
      queue.add(target);
    }
  }
  return IsolationReport(reachable, violations);
}

/// Demo assets declared in pubspec (`flutter.assets` under `demo/`).
List<String> demoAssets(Directory packageRoot) {
  final yaml = File('${packageRoot.path}/pubspec.yaml').readAsStringSync();
  return [
    for (final m in RegExp(
      r'^\s*-\s*(\S*demo\S*)\s*$',
      multiLine: true,
    ).allMatches(yaml))
      m.group(1)!,
  ];
}

void main(List<String> args) {
  final root = Directory(args.isEmpty ? '.' : args.first);
  final report = checkIsolation(root, 'main.dart');
  final assets = demoAssets(root);
  stdout.writeln(
    'release entry lib/main.dart: ${report.reachable.length} libraries',
  );
  for (final v in report.violations) {
    stderr.writeln('FORBIDDEN import: $v');
  }
  for (final a in assets) {
    stderr.writeln('FORBIDDEN demo asset: $a');
  }
  if (!report.ok || assets.isNotEmpty) exitCode = 1;
}

/// Package roots in package_config may lack the trailing slash.
String _dirUri(String u) => u.endsWith('/') ? u : '$u/';
