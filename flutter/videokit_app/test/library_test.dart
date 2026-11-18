// APP-LIB-A1 (REQ-APP-09–13, 16 FT-01A): media library logic — paging,
// folders, lock, import. Device-only parts (system pickers, MediaStore
// delete dialog, BiometricPrompt, FLAG_SECURE, gallery visibility) are
// covered through the scripted DemoLibraryPlatform and listed as device
// checks in the report.
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_app/history/app_storage.dart';
import 'package:videokit_app/library/library_folder_import.dart';
import 'package:videokit_app/library/library_import.dart';
import 'package:videokit_app/library/library_transfer.dart';
import 'package:videokit_app/library/library_lock.dart';
import 'package:videokit_app/library/library_models.dart';
import 'package:videokit_app/library/library_platform.dart';
import 'package:videokit_app/library/library_store.dart';
import 'package:videokit_app/library/sha256.dart';
import 'package:videokit_app/picker/media_picker.dart';

LibraryItem item(int n, {bool image = false, String? folder}) => LibraryItem(
  id: 'item-$n',
  path: 'memory:library/item-$n',
  displayName: 'm$n',
  kind: image ? MediaKind.imageStatic : MediaKind.video,
  importedAtEpochMs: n,
  folderId: folder,
);

PickedMedia picked(String name, {bool image = false, int? size}) =>
    PickedMedia(
      uri: 'content://test/$name',
      displayName: name,
      kind: image ? MediaKind.imageStatic : MediaKind.video,
      sizeBytes: size,
    );

void main() {
  test('sha256 matches FIPS 180-4 vectors', () {
    expect(
      hex(sha256(utf8.encode('abc'))),
      'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
    );
    expect(
      hex(sha256(const [])),
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    );
    expect(
      hex(
        sha256(
          utf8.encode(
            'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq',
          ),
        ),
      ),
      '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1',
    );
  });

  group('FT01A-08 paging', () {
    LibraryPageResult page(int n, int p, int size) =>
        LibraryPageResult.of([for (var i = 0; i < n; i++) item(i)], p, size);

    test('0 items: one empty page, range 0–0', () {
      final r = page(0, 1, 20);
      expect((r.page, r.pageCount, r.total, r.first, r.last), (1, 1, 0, 0, 0));
      expect(r.items, isEmpty);
    });

    test('1, 20, 21 items at 20 per page', () {
      expect((page(1, 1, 20).first, page(1, 1, 20).last), (1, 1));
      final twenty = page(20, 1, 20);
      expect((twenty.pageCount, twenty.last), (1, 20));
      final p2 = page(21, 2, 20);
      expect((p2.pageCount, p2.first, p2.last, p2.items.length), (2, 21, 21, 1));
    });

    test('5 and 200 per page; out-of-range pages are clamped', () {
      final five = page(42, 9, 5);
      expect((five.pageCount, five.page, five.first, five.last), (9, 9, 41, 42));
      final big = page(42, 1, 200);
      expect((big.pageCount, big.last), (1, 42));
      expect(page(42, 99, 20).page, 3);
      expect(page(42, 0, 20).page, 1);
    });
  });

  group('FT01A-09 page size', () {
    test('custom 5–200 only; 4, 201 and non-numbers are rejected', () {
      expect(LibrarySettings.parsePageSize('5'), 5);
      expect(LibrarySettings.parsePageSize(' 200 '), 200);
      expect(LibrarySettings.parsePageSize('4'), isNull);
      expect(LibrarySettings.parsePageSize('201'), isNull);
      expect(LibrarySettings.parsePageSize('abc'), isNull);
      expect(LibrarySettings.parsePageSize('1e2'), isNull);
      expect(LibrarySettings.parsePageSize(''), isNull);
    });

    test('a stored invalid size falls back to 20', () {
      expect(LibrarySettings.fromJson({'pageSize': 3}).pageSize, 20);
      expect(LibrarySettings.fromJson({'pageSize': 50}).pageSize, 50);
    });

    test('the lock refuses out-of-range sizes', () async {
      final lock = LibraryLock(
        storage: MemoryAppStorage(),
        platform: DemoLibraryPlatform(),
        rounds: 2,
      );
      expect(await lock.setPageSize(4), isFalse);
      expect(await lock.setPageSize(100), isTrue);
      expect(lock.value.pageSize, 100);
    });
  });

  group('FT01A-10/11 folders and items', () {
    late MemoryAppStorage storage;
    late DemoLibraryPlatform platform;
    late LibraryStore store;

    setUp(() {
      storage = MemoryAppStorage();
      platform = DemoLibraryPlatform();
      store = LibraryStore(
        storage: storage,
        platform: platform,
        reservedNames: {'全部媒体', '未分类'},
      );
    });

    test('new / duplicate / empty / reserved / too long', () async {
      final travel = await store.createFolder(' 旅行 ');
      expect(travel.name, '旅行');
      expect(store.checkFolderName('旅行'), FolderNameError.duplicate);
      expect(store.checkFolderName('  '), FolderNameError.empty);
      expect(store.checkFolderName('未分类'), FolderNameError.duplicate);
      expect(store.checkFolderName('Work'), isNull);
      await store.createFolder('Work');
      expect(store.checkFolderName('work'), FolderNameError.duplicate);
      expect(
        store.checkFolderName('x' * (LibraryStore.maxFolderName + 1)),
        FolderNameError.tooLong,
      );
      await expectLater(
        store.createFolder(''),
        throwsA(isA<FolderNameException>()),
      );
      expect(store.folders, hasLength(2));
    });

    test('rename: same name ok, clash refused', () async {
      final a = await store.createFolder('家人');
      await store.createFolder('宠物');
      await store.renameFolder(a.id, '家人');
      await expectLater(
        store.renameFolder(a.id, '宠物'),
        throwsA(isA<FolderNameException>()),
      );
      await store.renameFolder(a.id, '家人 2');
      expect(store.folderById(a.id)!.name, '家人 2');
    });

    test('delete folder: move to 未分类 or delete media with files', () async {
      final a = await store.createFolder('A');
      final b = await store.createFolder('B');
      for (var i = 0; i < 3; i++) {
        platform.files['memory:library/item-$i'] = 10;
        await store.addItem(item(i, folder: i < 2 ? a.id : b.id));
      }
      await store.deleteFolder(a.id, deleteMedia: false);
      expect(store.countIn(const Unsorted()), 2);
      expect(platform.files, hasLength(3), reason: 'files kept');
      await store.deleteFolder(b.id, deleteMedia: true);
      expect(store.items, hasLength(2));
      expect(platform.files.containsKey('memory:library/item-2'), isFalse);
    });

    test('move and delete update counts at once; index persists', () async {
      final a = await store.createFolder('A');
      for (var i = 0; i < 4; i++) {
        await store.addItem(item(i, image: i.isEven));
      }
      await store.moveItems(['item-0', 'item-1'], a.id);
      expect(store.countIn(InFolder(a.id)), 2);
      expect(store.countIn(const Unsorted()), 2);
      expect(store.itemsIn(InFolder(a.id), LibraryFilter.image), hasLength(1));
      await store.deleteItems(['item-1']);
      expect(store.countIn(InFolder(a.id)), 1);
      expect(store.countIn(const AllMedia()), 3);
      final again = LibraryStore(storage: storage, platform: platform);
      await again.load();
      expect(again.items.map((i) => i.id), store.items.map((i) => i.id));
      expect(again.folders, store.folders);
    });

    test('an item of a vanished folder is shown under 未分类', () async {
      storage.documents[LibraryStore.fileName] = jsonEncode({
        'schema': 1,
        'counter': 1,
        'folders': [],
        'items': [item(1, folder: 'folder-9').toJson()],
      });
      await store.load();
      expect(store.items.single.folderId, isNull);
    });
  });

  group('FT01A-01/02/03 lock', () {
    var now = DateTime(2026, 11, 8, 10);
    late DemoLibraryPlatform platform;
    late LibraryLock lock;

    setUp(() {
      now = DateTime(2026, 11, 8, 10);
      platform = DemoLibraryPlatform();
      lock = LibraryLock(
        storage: MemoryAppStorage(),
        platform: platform,
        now: () => now,
        rounds: 3,
      );
    });

    test('no PIN = open; set PIN; never stored in clear', () async {
      expect(lock.unlocked, isTrue);
      await lock.setPin('123456');
      expect(lock.value.protected, isTrue);
      expect(jsonEncode(lock.value.toJson()), isNot(contains('123456')));
      lock.lock();
      expect(lock.unlocked, isFalse);
      expect(await lock.enterPin('123456'), PinCheck.ok);
      expect(lock.unlocked, isTrue);
      expect(() => lock.setPin('12a456'), throwsArgumentError);
    });

    test('5 wrong PINs → 30 s cool-down, even the right PIN waits', () async {
      await lock.setPin('123456');
      lock.lock();
      for (var i = 0; i < 4; i++) {
        expect(await lock.enterPin('000000'), PinCheck.wrong);
      }
      expect(lock.attemptsLeft, 1);
      expect(await lock.enterPin('000000'), PinCheck.coolingDown);
      expect(lock.coolDownLeft, const Duration(seconds: 30));
      expect(await lock.enterPin('123456'), PinCheck.coolingDown);
      expect(lock.unlocked, isFalse);
      now = now.add(const Duration(seconds: 31));
      expect(await lock.enterPin('123456'), PinCheck.ok);
      expect(lock.value.failedAttempts, 0);
    });

    test('the next round of 5 doubles the cool-down', () async {
      await lock.setPin('123456');
      lock.lock();
      for (var i = 0; i < 5; i++) {
        await lock.enterPin('000000');
      }
      now = now.add(const Duration(seconds: 31));
      for (var i = 0; i < 5; i++) {
        await lock.enterPin('000000');
      }
      expect(lock.coolDownLeft, const Duration(minutes: 1));
    });

    test('biometric unlock only when on; unavailable is refused', () async {
      await lock.setPin('123456');
      lock.lock();
      expect(
        await lock.unlockWithBiometrics(title: 't', negative: 'n'),
        AuthResult.unavailable,
      );
      expect(await lock.setBiometric(true), isTrue);
      expect(
        await lock.unlockWithBiometrics(title: 't', negative: 'n'),
        AuthResult.success,
      );
      expect(lock.unlocked, isTrue);
      platform.biometrics = false;
      expect(await lock.setBiometric(true), isFalse);
    });

    test('auto-lock after the delay away, not before', () async {
      await lock.setPin('123456');
      lock
        ..appLeft()
        ..appReturned();
      expect(lock.unlocked, isTrue);
      lock.appLeft();
      now = now.add(const Duration(seconds: 59));
      lock.appReturned();
      expect(lock.unlocked, isTrue);
      lock.appLeft();
      now = now.add(const Duration(seconds: 60));
      lock.appReturned();
      expect(lock.unlocked, isFalse);
      await lock.enterPin('123456');
      await lock.setLockAfter(0);
      lock
        ..appLeft()
        ..appReturned();
      expect(lock.unlocked, isFalse, reason: '0 = at once');
    });

    test('forgot PIN: screen lock then a new PIN; no screen lock → '
        'unavailable', () async {
      await lock.setPin('123456');
      lock.lock();
      expect(
        await lock.verifyOwnerForReset(title: 't'),
        AuthResult.success,
      );
      await lock.setPin('654321');
      lock.lock();
      expect(await lock.enterPin('654321'), PinCheck.ok);
      platform.deviceCredential = false;
      expect(
        await lock.verifyOwnerForReset(title: 't'),
        AuthResult.unavailable,
      );
    });

    test('settings survive a reload (FT01A-15 data kept)', () async {
      final storage = MemoryAppStorage();
      final a = LibraryLock(storage: storage, platform: platform, rounds: 3);
      await a.setPin('111111');
      await a.setPageSize(50);
      await a.setLockAfter(300);
      final b = LibraryLock(storage: storage, platform: platform, rounds: 3);
      await b.load();
      expect(b.value.protected, isTrue);
      expect((b.value.pageSize, b.value.lockAfterSeconds), (50, 300));
      expect(b.unlocked, isFalse);
      expect(await b.enterPin('111111'), PinCheck.ok);
    });
  });

  group('FT01A-04/05/06 import', () {
    late DemoLibraryPlatform platform;
    late LibraryStore store;

    setUp(() {
      platform = DemoLibraryPlatform();
      store = LibraryStore(storage: MemoryAppStorage(), platform: platform);
    });

    test('1 and 20 mixed items: counts, progress, thumbnails', () async {
      for (final n in [1, 20]) {
        final media = [
          for (var i = 0; i < n; i++)
            picked('f$n-$i.${i.isEven ? 'mp4' : 'jpg'}', image: i.isOdd),
        ];
        final job = LibraryImport(store: store, media: media, folderId: null);
        expect(job.videoCount + job.imageCount, n);
        final r = await job.run();
        expect((r.finished, r.cancelled, r.imported), (true, false, n));
        expect(r.failed, isEmpty);
        expect(r.fraction, 1);
      }
      expect(store.items, hasLength(21));
      expect(store.items.first.durationUs, isNull, reason: 'last was image');
      expect(store.items.where((i) => !i.isImage).first.durationUs, isNotNull);
      expect(platform.thumbnails, hasLength(21));
    });

    test('100 items keep the pick order of their outcomes', () async {
      final media = [for (var i = 0; i < 100; i++) picked('x$i.mp4')];
      final r = await LibraryImport(
        store: store,
        media: media,
        folderId: null,
      ).run();
      expect(r.imported, 100);
      expect(r.outcomes.map((o) => o.media), media);
    });

    test('failures are reported per item; the others go on', () async {
      final media = [
        picked('ok1.mp4'),
        picked('gone.mp4'),
        picked('broken.mp4'),
        picked('huge.mp4', size: 1 << 40),
        picked('ok2.jpg', image: true),
      ];
      platform.failures['content://test/gone.mp4'] = ImportFailure.unreadable;
      platform.corrupt.add('content://test/broken.mp4');
      final r = await LibraryImport(
        store: store,
        media: media,
        folderId: null,
      ).run();
      expect(r.imported, 2);
      expect({for (final f in r.failed) f.media.displayName: f.failure}, {
        'gone.mp4': ImportFailure.unreadable,
        'broken.mp4': ImportFailure.corrupt,
        'huge.mp4': ImportFailure.noSpace,
      });
      expect(platform.files, hasLength(2), reason: 'no partial copies');
    });

    test('cancel keeps the imported items and leaves nothing else', () async {
      platform.copyDelay = const Duration(milliseconds: 5);
      final media = [for (var i = 0; i < 10; i++) picked('c$i.mp4')];
      final job = LibraryImport(store: store, media: media, folderId: null);
      final run = job.run();
      while (job.value.done < 3) {
        await Future<void>.delayed(const Duration(milliseconds: 1));
      }
      job.cancel();
      final r = await run;
      expect(r.cancelled, isTrue);
      expect(r.imported, inInclusiveRange(3, 4));
      expect(store.items, hasLength(r.imported));
      expect(platform.files, hasLength(r.imported));
      expect(r.failed, isEmpty, reason: 'not-started items are no failures');
    });

    test('delete originals: only when on, only after the system confirmed, '
        'only imported ones', () async {
      final media = [picked('a.mp4'), picked('b.mp4')];
      platform.failures['content://test/b.mp4'] = ImportFailure.unreadable;
      var r = await LibraryImport(
        store: store,
        media: media,
        folderId: null,
      ).run();
      expect(platform.deletedOriginals, isEmpty, reason: 'switch off');
      r = await LibraryImport(
        store: store,
        media: media,
        folderId: null,
        deleteOriginals: true,
      ).run();
      expect(platform.deletedOriginals, ['content://test/a.mp4']);
      expect((r.originalsDeleted, r.originalsKept), (1, 0));
      platform
        ..confirmDelete = false
        ..deletedOriginals.clear();
      r = await LibraryImport(
        store: store,
        media: media,
        folderId: null,
        deleteOriginals: true,
      ).run();
      expect(platform.deletedOriginals, isEmpty, reason: 'user refused');
      expect((r.originalsDeleted, r.originalsKept), (0, 1));
    });

    test('imports go to the chosen folder', () async {
      final f = await store.createFolder('旅行');
      await LibraryImport(
        store: store,
        media: [picked('t.mp4')],
        folderId: f.id,
      ).run();
      expect(store.countIn(InFolder(f.id)), 1);
    });
  });

  group('REQ-APP-14 transfers', () {
    late DemoLibraryPlatform platform;
    late LibraryStore store;

    Future<List<LibraryItem>> seed(int n, {String? folder}) async {
      final out = <LibraryItem>[];
      for (var i = 0; i < n; i++) {
        final it = item(i, image: i.isOdd, folder: folder);
        platform.files[it.path] = 100;
        await store.addItem(it);
        out.add(it);
      }
      return out;
    }

    setUp(() {
      platform = DemoLibraryPlatform();
      store = LibraryStore(storage: MemoryAppStorage(), platform: platform);
    });

    test('FT01A-17 gallery: single, several, mixed; originals stay; no '
        'space reported per item', () async {
      final items = await seed(3);
      var r = await LibraryTransfer(
        store: store,
        items: items.take(1).toList(),
        target: TransferTarget.gallery,
        folderNameOf: (_) => '未分类',
      ).run();
      expect(r.succeeded, 1);
      expect(r.failed, isEmpty);
      platform.galleryFree = 150;
      r = await LibraryTransfer(
        store: store,
        items: items,
        target: TransferTarget.gallery,
        folderNameOf: (_) => '未分类',
      ).run();
      expect(r.succeeded, 1);
      expect(
        r.failed.map((f) => f.failure),
        [TransferFailure.noSpace, TransferFailure.noSpace],
      );
      expect(platform.gallery, ['m0', 'm0']);
      expect(store.items, hasLength(3), reason: 'library items stay');
    });

    test('FT01A-20 move out: per folder sub-directory, verified copies '
        'leave the library, failures stay', () async {
      final f = await store.createFolder('旅行');
      final items = [...await seed(2, folder: f.id)];
      final loose = item(9);
      platform.files[loose.path] = 100;
      await store.addItem(loose);
      items.add(loose);
      platform.mismatching.add('m1');
      final r = await LibraryTransfer(
        store: store,
        items: items,
        target: TransferTarget.directory,
        treeUri: 'tree:x',
        folderNameOf: (i) => i.folderId == null ? '未分类' : '旅行',
      ).run();
      expect(platform.directories['tree:x'], {'旅行', '未分类'});
      expect(platform.treeFiles.keys, {
        'tree:x/旅行/m0',
        'tree:x/未分类/m9',
      });
      expect(r.failed.single.failure, TransferFailure.mismatch);
      expect(store.items.map((i) => i.id), ['item-1'], reason: 'unverified');
      expect(platform.files.containsKey('memory:library/item-1'), isTrue);
    });

    test('FT01A-20 move out: unplugged target and no space keep items; '
        'cancel keeps the rest', () async {
      final items = await seed(4);
      platform.unwritableDirs.add('tree:x/未分类');
      var r = await LibraryTransfer(
        store: store,
        items: items.take(1).toList(),
        target: TransferTarget.directory,
        treeUri: 'tree:x',
        folderNameOf: (_) => '未分类',
      ).run();
      expect(r.failed.single.failure, TransferFailure.unwritable);
      expect(store.items, hasLength(4));
      platform.unwritableDirs.clear();
      platform.treeFree = 150;
      r = await LibraryTransfer(
        store: store,
        items: items.take(2).toList(),
        target: TransferTarget.directory,
        treeUri: 'tree:x',
        folderNameOf: (_) => '未分类',
      ).run();
      expect(r.succeeded, 1);
      expect(r.failed.single.failure, TransferFailure.noSpace);
      expect(store.items, hasLength(3));
      platform
        ..treeFree = null
        ..copyDelay = const Duration(milliseconds: 5);
      final job = LibraryTransfer(
        store: store,
        items: store.items.toList(),
        target: TransferTarget.directory,
        treeUri: 'tree:y',
        folderNameOf: (_) => '未分类',
      );
      final run = job.run();
      while (job.value.done < 1) {
        await Future<void>.delayed(const Duration(milliseconds: 1));
      }
      job.cancel();
      r = await run;
      expect(r.cancelled, isTrue);
      expect(store.items.length, 3 - r.succeeded);
      expect(r.failed, isEmpty, reason: 'the cancelled item is no failure');
    });

    test('unique names within a target directory', () {
      final taken = <String>{};
      expect(LibraryTransfer.uniqueName('a.mp4', taken), 'a.mp4');
      expect(LibraryTransfer.uniqueName('A.mp4', taken), 'A (2).mp4');
      expect(LibraryTransfer.uniqueName('a.mp4', taken), 'a (3).mp4');
      expect(LibraryTransfer.uniqueName('noext', taken), 'noext');
    });
  });

  group('FT01A-21 import a whole folder', () {
    late DemoLibraryPlatform platform;
    late LibraryStore store;

    TreeListing listing() => const TreeListing(
      name: '相机',
      entries: [
        TreeEntry(dir: '', uri: 'u:1', name: 'a.mp4', mimeType: 'video/mp4'),
        TreeEntry(dir: '', uri: 'u:2', name: 'notes.txt', mimeType: 'text/plain'),
        TreeEntry(dir: '旅行', uri: 'u:3', name: 'b.jpg', mimeType: 'image/jpeg'),
        TreeEntry(dir: '旅行/2025', uri: 'u:4', name: 'c.gif', mimeType: 'image/gif'),
        TreeEntry(dir: '文档', uri: 'u:5', name: 'x.pdf', mimeType: 'application/pdf'),
      ],
    );

    setUp(() {
      platform = DemoLibraryPlatform();
      store = LibraryStore(
        storage: MemoryAppStorage(),
        platform: platform,
        reservedNames: {'全部媒体', '未分类'},
      );
    });

    test('plan: folders by directory, non-media skipped, empty dirs none', () {
      final plan = planFolderImport(listing());
      expect(plan.media.map((m) => m.displayName), ['a.mp4', 'b.jpg', 'c.gif']);
      expect(plan.folderNames, ['相机', '旅行', '旅行 / 2025']);
      expect(plan.skipped, ['notes.txt', '文档/x.pdf']);
      expect(plan.media[2].kind, MediaKind.imageAnimated);
      expect(plan.folders, hasLength(3), reason: '文档 had no media');
    });

    test('clash: merge into the existing folder or make a new one; '
        'cancel creates nothing', () async {
      final existing = await store.createFolder('旅行');
      final plan = planFolderImport(listing());
      expect(
        await prepareFolderImport(store, plan, onClash: (_) async => null),
        isNull,
      );
      expect(store.folders, hasLength(1));
      final merge = await prepareFolderImport(
        store,
        plan,
        onClash: (_) async => FolderClashChoice.merge,
      );
      await merge!.run();
      expect(store.countIn(InFolder(existing.id)), 1);
      expect(store.folderByName('相机'), isNotNull);
      expect(store.folderByName('旅行 / 2025'), isNotNull);
      final separate = await prepareFolderImport(
        store,
        planFolderImport(listing()),
        onClash: (_) async => FolderClashChoice.separate,
      );
      await separate!.run();
      expect(store.folderByName('旅行 (2)'), isNotNull);
      expect(store.countIn(InFolder(existing.id)), 1, reason: 'not merged');
      expect(separate.skipped, ['notes.txt', '文档/x.pdf']);
    });

    test('folder names: too long is shortened, reserved names get a '
        'number', () {
      expect(store.uniqueFolderName('未分类'), '未分类 (2)');
      final long = 'x' * 60;
      expect(
        store.uniqueFolderName(long).length,
        lessThanOrEqualTo(LibraryStore.maxFolderName),
      );
    });
  });
}
