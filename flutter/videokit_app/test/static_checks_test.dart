import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import '../../tools/vk_lints/vk_literal_lint.dart';
import '../tool/release_isolation.dart';

void main() {
  test('vk_literal_lint: App text from ARB, colours/sizes from tokens', () {
    // 14 §11.3 via tools/vk_lints (M0-B6 report §2.4).
    final findings = lintDirectories(['lib']);
    expect(findings.map((f) => '$f'), isEmpty);
  });

  group('release isolation (14 §11.4, 04A P3)', () {
    final root = Directory('.');

    test('lib/main.dart cannot reach videokit_fake or demo code', () {
      final r = checkIsolation(root, 'main.dart');
      expect(r.violations, isEmpty);
      expect(
        r.reachable.any((u) => u.startsWith('package:videokit_ui/')),
        isTrue,
        reason: 'the walk follows workspace packages',
      );
      expect(demoAssets(root), isEmpty, reason: 'no demo assets bundled');
    });

    test('M6-A1: artifact scan finds Fake markers; compressed is '
        'inconclusive', () {
      final dir = Directory.systemTemp.createTempSync('vk_release_');
      addTearDown(() => dir.deleteSync(recursive: true));
      File write(String name, String content) =>
          File('${dir.path}/$name')..writeAsStringSync(content);
      final clean = scanArtifact(write('clean.so', 'x VideoKitPlayer VkTheme'));
      expect(clean.readable, isTrue);
      expect(clean.found, isEmpty);
      final dirty = scanArtifact(
        write('dirty.so', 'VideoKitPlayer FakeVideoKit DemoBackend'),
      );
      expect(dirty.found, containsAll(['FakeVideoKit', 'DemoBackend']));
      final packed = scanArtifact(write('packed.apk', 'PK..deflated..'));
      expect(packed.readable, isFalse, reason: 'cannot prove absence');
      expect(fakeIsRegularDependency(root), isTrue, reason: 'demo flavor');
    });

    test('APP-LIB-A1: release not debuggable, library out of backups, '
        'internal storage only', () {
      expect(checkAndroidPrivacy(root), isEmpty);
      final k = File(
        'android/app/src/main/kotlin/com/videokit/videokit_app/'
        'LibraryChannel.kt',
      ).readAsStringSync();
      expect(k, contains('File(activity.filesDir, "library")'));
      // REQ-APP-14: "keep app data" may be offered on uninstall.
      final manifest = File(
        'android/app/src/main/AndroidManifest.xml',
      ).readAsStringSync();
      expect(manifest, contains('android:hasFragileUserData="true"'));
      // Gallery export writes through MediaStore, not into a file path.
      expect(k, contains('MediaStore.MediaColumns.RELATIVE_PATH'));
      expect(k, contains('"Movies/\$GALLERY_DIR"'));
    });

    test('APP-LIB-A1: the privacy check catches a debuggable release, '
        'missing backup rules and external storage (control)', () {
      final dir = Directory.systemTemp.createTempSync('vk_privacy_');
      addTearDown(() => dir.deleteSync(recursive: true));
      void write(String path, String content) => File('${dir.path}/$path')
        ..createSync(recursive: true)
        ..writeAsStringSync(content);
      write(
        'android/app/build.gradle.kts',
        'android { buildTypes { release { isDebuggable = true } } }',
      );
      write(
        'android/app/src/main/AndroidManifest.xml',
        '<manifest><application android:debuggable="true"/></manifest>',
      );
      write(
        'android/app/src/main/kotlin/com/videokit/videokit_app/'
            'LibraryChannel.kt',
        'val d = activity.getExternalFilesDir(null)',
      );
      final problems = checkAndroidPrivacy(dir);
      expect(problems, contains('release build is debuggable (build.gradle.kts)'));
      expect(problems, contains('main manifest sets android:debuggable="true"'));
      expect(problems.where((p) => p.startsWith('backup:')), hasLength(2));
      expect(
        problems,
        contains('library uses external storage: getExternalFilesDir'),
      );
      expect(problems, contains('library directory is not under filesDir'));
      write(
        'android/app/src/main/AndroidManifest.xml',
        '<manifest><application android:allowBackup="false"/></manifest>',
      );
      expect(
        checkAndroidPrivacy(dir).where((p) => p.startsWith('backup:')),
        isEmpty,
        reason: 'allowBackup=false is enough',
      );
    });

    test('lib/main_demo.dart does reach the Fake (control)', () {
      final r = checkIsolation(root, 'main_demo.dart');
      expect(
        r.violations.any(
          (v) => v.contains('videokit_fake') || v.contains('/backend/demo_'),
        ),
        isTrue,
        reason: 'the walk must detect the demo backend',
      );
    });
  });
}
