// Release isolation check (14 §11.4, 04A P3) without Gradle:
//
//   dart run tool/release_isolation.dart [--artifact=<apk|libapp.so>]
//                                                (from videokit_app)
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

/// Strings that must not appear in a release artifact (VK-M8, 11 §7): Fake
/// classes, the demo backend and demo source refs.
const List<String> forbiddenArtifactMarkers = [
  'FakeVideoKit',
  'FakeEditProject',
  'FakeAvatarTools',
  'DemoBackend',
  'DemoMediaPicker',
  'package:videokit_fake/',
];

/// Result of scanning one built artifact.
final class ArtifactScan {
  /// Creates a result.
  ArtifactScan(this.path, this.found, {required this.readable});

  /// Scanned file.
  final String path;

  /// Forbidden markers found.
  final List<String> found;

  /// False when the file looks compressed (e.g. a deflated `libapp.so` in
  /// an APK): absence then proves nothing and the scan is inconclusive.
  final bool readable;
}

/// Scans the bytes of [file] (an APK with stored native libraries, or an
/// extracted `libapp.so`) for [forbiddenArtifactMarkers]. Dart AOT keeps
/// class names unless obfuscated, so a Fake that was compiled in shows up.
ArtifactScan scanArtifact(File file) {
  final bytes = file.readAsBytesSync();
  final text = latin1.decode(bytes, allowInvalid: true);
  final found = [
    for (final m in forbiddenArtifactMarkers)
      if (text.contains(m)) m,
  ];
  // A release snapshot always names the module's own classes; if even
  // those are missing the native library was compressed.
  final readable = text.contains('VideoKitPlayer') || text.contains('VkTheme');
  return ArtifactScan(file.path, found, readable: readable);
}

/// Whether `videokit_fake` is a regular (not dev) dependency of the App.
/// That is allowed (the demo flavor `main_demo.dart` needs it and the
/// release snapshot only contains what `main.dart` reaches), but the
/// report says so.
bool fakeIsRegularDependency(Directory packageRoot) {
  final yaml = File('${packageRoot.path}/pubspec.yaml').readAsStringSync();
  final deps = yaml.split(RegExp(r'^dev_dependencies:', multiLine: true)).first;
  return RegExp(r'^\s+videokit_fake:', multiLine: true).hasMatch(deps);
}

/// APP-LIB-A1 (REQ-APP-10, not encrypted, so privacy rests on these): the
/// Android sources of the App must keep
///
/// * the release build not debuggable (no `isDebuggable = true` in the
///   release block, no `android:debuggable="true"` in the main manifest);
/// * the media library out of backups (`allowBackup="false"`, or both
///   backup rule files excluding `library/`);
/// * the library files in internal storage (`LibraryChannel.kt` never uses
///   external app-specific or shared storage).
///
/// Returns the problems found (empty = ok).
List<String> checkAndroidPrivacy(Directory packageRoot) {
  final problems = <String>[];
  final app = '${packageRoot.path}/android/app';
  final gradle = File('$app/build.gradle.kts');
  if (gradle.existsSync()) {
    final text = gradle.readAsStringSync();
    final release = RegExp(
      r'release\s*\{([^{}]*(\{[^{}]*\}[^{}]*)*)\}',
    ).firstMatch(text)?.group(1);
    if (release != null &&
        RegExp(r'isDebuggable\s*=\s*true').hasMatch(release)) {
      problems.add('release build is debuggable (build.gradle.kts)');
    }
  }
  final manifest = File('$app/src/main/AndroidManifest.xml');
  if (!manifest.existsSync()) {
    problems.add('main AndroidManifest.xml missing');
    return problems;
  }
  final m = manifest.readAsStringSync();
  if (RegExp(r'android:debuggable\s*=\s*"true"').hasMatch(m)) {
    problems.add('main manifest sets android:debuggable="true"');
  }
  final noBackup = RegExp(r'android:allowBackup\s*=\s*"false"').hasMatch(m);
  if (!noBackup) {
    for (final (attr, file) in const [
      ('android:dataExtractionRules', 'data_extraction_rules.xml'),
      ('android:fullBackupContent', 'backup_rules.xml'),
    ]) {
      final rules = File('$app/src/main/res/xml/$file');
      if (!m.contains(attr) || !rules.existsSync()) {
        problems.add('backup: $attr / res/xml/$file missing');
      } else if (!rules.readAsStringSync().contains('path="library/"')) {
        problems.add('backup: $file does not exclude library/');
      }
    }
  }
  final channel = File(
    '$app/src/main/kotlin/com/videokit/videokit_app/LibraryChannel.kt',
  );
  if (channel.existsSync()) {
    final k = channel.readAsStringSync();
    for (final bad in const [
      'getExternalFilesDir',
      'externalCacheDir',
      'getExternalCacheDir',
      'getExternalStorageDirectory',
      'getExternalStoragePublicDirectory',
      'externalMediaDirs',
    ]) {
      if (k.contains(bad)) problems.add('library uses external storage: $bad');
    }
    if (!k.contains('filesDir')) {
      problems.add('library directory is not under filesDir');
    }
  }
  return problems;
}

/// Usage:
///
///     dart run tool/release_isolation.dart [packageRoot]
///         [--artifact=build/app/outputs/flutter-apk/app-release.apk] ...
///
/// Without `--artifact` only the source graph and assets are checked (no
/// build needed). Exit code 1 on any violation or an inconclusive scan.
void main(List<String> args) {
  final positional = [
    for (final a in args)
      if (!a.startsWith('--')) a,
  ];
  final artifacts = [
    for (final a in args)
      if (a.startsWith('--artifact=')) a.substring('--artifact='.length),
  ];
  final root = Directory(positional.isEmpty ? '.' : positional.first);
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
  if (fakeIsRegularDependency(root)) {
    stdout.writeln(
      'note: videokit_fake is a regular dependency (demo flavor); release '
      'safety relies on the graph check above',
    );
  }
  final privacy = checkAndroidPrivacy(root);
  for (final p in privacy) {
    stderr.writeln('PRIVACY: $p');
  }
  if (privacy.isEmpty) {
    stdout.writeln(
      'android: release not debuggable, library excluded from backup, '
      'internal storage only',
    );
  }
  var failed = !report.ok || assets.isNotEmpty || privacy.isNotEmpty;
  for (final path in artifacts) {
    final f = File(path);
    if (!f.existsSync()) {
      stderr.writeln('MISSING artifact: $path');
      failed = true;
      continue;
    }
    final scan = scanArtifact(f);
    if (!scan.readable) {
      stderr.writeln(
        'INCONCLUSIVE artifact (compressed?): $path; scan the extracted '
        'lib/arm64-v8a/libapp.so instead',
      );
      failed = true;
    }
    for (final m in scan.found) {
      stderr.writeln('FORBIDDEN in artifact $path: $m');
    }
    if (scan.found.isNotEmpty) failed = true;
    if (scan.readable && scan.found.isEmpty) {
      stdout.writeln('artifact clean: $path');
    }
  }
  if (failed) exitCode = 1;
}

/// Package roots in package_config may lack the trailing slash.
String _dirUri(String u) => u.endsWith('/') ? u : '$u/';
