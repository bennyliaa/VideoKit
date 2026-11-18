import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';

import '../history/app_storage.dart';
import 'library_platform.dart';
import 'sha256.dart';

/// Media library settings (design page 27 "媒体库设置").
@immutable
final class LibrarySettings {
  /// Creates settings.
  const LibrarySettings({
    this.pinHash,
    this.pinSalt,
    this.biometric = false,
    this.lockAfterSeconds = defaultLockAfterSeconds,
    this.pageSize = defaultPageSize,
    this.showFolderBar = true,
    this.setUpDone = false,
    this.failedAttempts = 0,
    this.lockedUntilEpochMs = 0,
  });

  /// Default page size (REQ-APP-12).
  static const int defaultPageSize = 20;

  /// Page sizes offered as chips.
  static const List<int> pageSizeChoices = [10, 20, 50, 100];

  /// Custom page size range.
  static const int minPageSize = 5;

  /// Custom page size range.
  static const int maxPageSize = 200;

  /// Default auto-lock (REQ-APP-10: 1 minute).
  static const int defaultLockAfterSeconds = 60;

  /// Auto-lock choices (0 = at once).
  static const List<int> lockAfterChoices = [0, 30, 60, 300, 900];

  /// Salted PIN hash (hex); null = no password protection.
  final String? pinHash;

  /// Salt (hex).
  final String? pinSalt;

  /// Fingerprint / face unlock on.
  final bool biometric;

  /// Lock after leaving the App this long.
  final int lockAfterSeconds;

  /// Items per page.
  final int pageSize;

  /// Folder bar shown by default (tablet / landscape).
  final bool showFolderBar;

  /// The first-entry choice (set a password or not) was made.
  final bool setUpDone;

  /// Wrong PINs in a row.
  final int failedAttempts;

  /// No PIN accepted before this time (cool-down).
  final int lockedUntilEpochMs;

  /// Password protection on.
  bool get protected => pinHash != null;

  /// Returns a copy.
  LibrarySettings copyWith({
    String? Function()? pinHash,
    String? Function()? pinSalt,
    bool? biometric,
    int? lockAfterSeconds,
    int? pageSize,
    bool? showFolderBar,
    bool? setUpDone,
    int? failedAttempts,
    int? lockedUntilEpochMs,
  }) => LibrarySettings(
    pinHash: pinHash == null ? this.pinHash : pinHash(),
    pinSalt: pinSalt == null ? this.pinSalt : pinSalt(),
    biometric: biometric ?? this.biometric,
    lockAfterSeconds: lockAfterSeconds ?? this.lockAfterSeconds,
    pageSize: pageSize ?? this.pageSize,
    showFolderBar: showFolderBar ?? this.showFolderBar,
    setUpDone: setUpDone ?? this.setUpDone,
    failedAttempts: failedAttempts ?? this.failedAttempts,
    lockedUntilEpochMs: lockedUntilEpochMs ?? this.lockedUntilEpochMs,
  );

  /// JSON form.
  Map<String, Object?> toJson() => {
    'pinHash': ?pinHash,
    'pinSalt': ?pinSalt,
    'biometric': biometric,
    'lockAfterSeconds': lockAfterSeconds,
    'pageSize': pageSize,
    'showFolderBar': showFolderBar,
    'setUpDone': setUpDone,
    'failedAttempts': failedAttempts,
    'lockedUntilEpochMs': lockedUntilEpochMs,
  };

  /// Parses [j]; broken values fall back to defaults.
  static LibrarySettings fromJson(Map<String, Object?> j) {
    int n(String k, int d) => (j[k] as num?)?.toInt() ?? d;
    final size = n('pageSize', defaultPageSize);
    return LibrarySettings(
      pinHash: j['pinHash'] as String?,
      pinSalt: j['pinSalt'] as String?,
      biometric: j['biometric'] as bool? ?? false,
      lockAfterSeconds: math.max(
        0,
        n('lockAfterSeconds', defaultLockAfterSeconds),
      ),
      pageSize: validPageSize(size) ? size : defaultPageSize,
      showFolderBar: j['showFolderBar'] as bool? ?? true,
      setUpDone: j['setUpDone'] as bool? ?? false,
      failedAttempts: n('failedAttempts', 0),
      lockedUntilEpochMs: n('lockedUntilEpochMs', 0),
    );
  }

  /// Whether [size] is an allowed page size (5–200).
  static bool validPageSize(int size) =>
      size >= minPageSize && size <= maxPageSize;

  /// Parses a custom page size typed by the user; null when not a number
  /// or out of 5–200 (FT01A-09).
  static int? parsePageSize(String text) {
    final v = int.tryParse(text.trim());
    return v != null && validPageSize(v) ? v : null;
  }
}

/// Result of entering a PIN.
enum PinCheck {
  /// Right: unlocked.
  ok,

  /// Wrong; more attempts left.
  wrong,

  /// Wrong too often: cooling down ([LibraryLock.coolDownLeft]).
  coolingDown,
}

/// Lock state and settings of the media library (REQ-APP-10): 6-digit PIN
/// (salted, iterated SHA-256; never stored in clear), biometric unlock,
/// cool-down after 5 wrong PINs, auto-lock after leaving the App.
class LibraryLock extends ValueNotifier<LibrarySettings> {
  /// Creates the lock.
  LibraryLock({
    required this.storage,
    required this.platform,
    DateTime Function()? now,
    math.Random? random,
    this.rounds = defaultRounds,
  }) : now = now ?? DateTime.now,
       _random = random ?? math.Random.secure(),
       super(const LibrarySettings());

  /// Settings storage.
  final AppStorage storage;

  /// System prompts.
  final LibraryPlatform platform;

  /// Clock.
  final DateTime Function() now;

  final math.Random _random;

  /// Settings file.
  static const String fileName = 'library_settings.json';

  /// PIN length.
  static const int pinLength = 6;

  /// Wrong PINs before a cool-down.
  static const int maxAttempts = 5;

  /// First cool-down (doubles for each further round, up to [maxCoolDown]).
  static const Duration firstCoolDown = Duration(seconds: 30);

  /// Longest cool-down.
  static const Duration maxCoolDown = Duration(minutes: 5);

  /// Hash rounds of the App (tests use fewer to stay fast).
  static const int defaultRounds = 10000;

  /// Hash rounds. Changing it invalidates stored PINs, so the App keeps
  /// [defaultRounds].
  final int rounds;

  bool _unlocked = false;
  DateTime? _leftAt;

  /// Whether the library is open now (no PIN set counts as open).
  bool get unlocked => _unlocked || !value.protected;

  /// Loads the settings.
  Future<void> load() async {
    final raw = await storage.read(fileName);
    if (raw == null) return;
    try {
      value = LibrarySettings.fromJson(
        jsonDecode(raw) as Map<String, Object?>,
      );
    } on Object {
      value = const LibrarySettings();
    }
  }

  Future<void> _save(LibrarySettings s) async {
    value = s;
    await writeQuietly(storage, fileName, jsonEncode(s.toJson()));
  }

  /// Whether [pin] has the right form (6 digits).
  static bool validPin(String pin) =>
      pin.length == pinLength && RegExp(r'^\d+$').hasMatch(pin);

  String _hash(String pin, String salt) {
    var h = utf8.encode('$salt:$pin');
    for (var i = 0; i < rounds; i++) {
      h = sha256([...h, ...utf8.encode(salt)]);
    }
    return hex(h);
  }

  /// Sets (or replaces) the PIN and unlocks.
  Future<void> setPin(String pin) async {
    if (!validPin(pin)) throw ArgumentError.value(pin, 'pin');
    final salt = hex([for (var i = 0; i < 16; i++) _random.nextInt(256)]);
    _unlocked = true;
    await _save(
      value.copyWith(
        pinHash: () => _hash(pin, salt),
        pinSalt: () => salt,
        setUpDone: true,
        failedAttempts: 0,
        lockedUntilEpochMs: 0,
      ),
    );
  }

  /// Turns password protection off (and biometrics with it).
  Future<void> clearPin() => _save(
    value.copyWith(
      pinHash: () => null,
      pinSalt: () => null,
      biometric: false,
      setUpDone: true,
      failedAttempts: 0,
      lockedUntilEpochMs: 0,
    ),
  );

  /// First entry: the user chose not to set a password.
  Future<void> skipSetUp() => _save(value.copyWith(setUpDone: true));

  /// Cool-down left (zero when none).
  Duration get coolDownLeft {
    final left = value.lockedUntilEpochMs - now().millisecondsSinceEpoch;
    return left > 0 ? Duration(milliseconds: left) : Duration.zero;
  }

  /// Checks [pin]; unlocks when right. While cooling down every PIN is
  /// refused without checking.
  Future<PinCheck> enterPin(String pin) async {
    if (coolDownLeft > Duration.zero) return PinCheck.coolingDown;
    final hash = value.pinHash;
    final salt = value.pinSalt;
    if (hash == null || salt == null) {
      _unlocked = true;
      return PinCheck.ok;
    }
    if (validPin(pin) && _hash(pin, salt) == hash) {
      _unlocked = true;
      await _save(value.copyWith(failedAttempts: 0, lockedUntilEpochMs: 0));
      return PinCheck.ok;
    }
    final failed = value.failedAttempts + 1;
    if (failed % maxAttempts == 0) {
      final round = failed ~/ maxAttempts - 1;
      final ms = math.min(
        firstCoolDown.inMilliseconds * (1 << round.clamp(0, 10)),
        maxCoolDown.inMilliseconds,
      );
      await _save(
        value.copyWith(
          failedAttempts: failed,
          lockedUntilEpochMs: now().millisecondsSinceEpoch + ms,
        ),
      );
      return PinCheck.coolingDown;
    }
    await _save(value.copyWith(failedAttempts: failed));
    return PinCheck.wrong;
  }

  /// Wrong PINs left before the next cool-down.
  int get attemptsLeft => maxAttempts - value.failedAttempts % maxAttempts;

  /// Fingerprint / face unlock (only when turned on and protected).
  Future<AuthResult> unlockWithBiometrics({
    required String title,
    required String negative,
  }) async {
    if (!value.protected || !value.biometric) return AuthResult.unavailable;
    final r = await platform.authenticateBiometric(
      title: title,
      negative: negative,
    );
    if (r == AuthResult.success) {
      _unlocked = true;
      notifyListeners();
    }
    return r;
  }

  /// Turns biometric unlock on or off; turning on needs it to be available.
  Future<bool> setBiometric(bool on) async {
    if (on && !await platform.canUseBiometrics()) return false;
    await _save(value.copyWith(biometric: on && value.protected));
    return true;
  }

  /// "忘记密码": the device screen lock proves the owner; then the PIN may
  /// be set again ([setPin]). Unavailable without a screen lock.
  Future<AuthResult> verifyOwnerForReset({required String title}) async {
    if (!await platform.hasDeviceCredential()) return AuthResult.unavailable;
    return platform.confirmDeviceCredential(title: title);
  }

  /// Auto-lock delay setting.
  Future<void> setLockAfter(int seconds) =>
      _save(value.copyWith(lockAfterSeconds: math.max(0, seconds)));

  /// Page size setting (5–200); false when out of range.
  Future<bool> setPageSize(int size) async {
    if (!LibrarySettings.validPageSize(size)) return false;
    await _save(value.copyWith(pageSize: size));
    return true;
  }

  /// Folder bar default.
  Future<void> setShowFolderBar(bool show) =>
      _save(value.copyWith(showFolderBar: show));

  /// Locks now.
  void lock() {
    if (!_unlocked) return;
    _unlocked = false;
    notifyListeners();
  }

  /// The App went to the background (or the screen turned off).
  void appLeft() => _leftAt = now();

  /// The App came back: locks when it was away at least the auto-lock
  /// delay.
  void appReturned() {
    final left = _leftAt;
    _leftAt = null;
    if (left == null) return;
    if (now().difference(left).inSeconds >= value.lockAfterSeconds) lock();
  }
}
