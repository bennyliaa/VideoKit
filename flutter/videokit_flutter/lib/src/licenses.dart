import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Asset with the open source notices of the plugin and the native Kit (04A X1): Media3, kotlinx.coroutines, the
/// Kotlin standard library and their dependencies, with the Apache License 2.0 text.
const String kVideoKitNoticeAsset = 'packages/videokit_flutter/assets/NOTICE';

/// Packages the notice is listed under on the system licence page (`showLicensePage`).
const List<String> kVideoKitNoticePackages = ['VideoKit (Media3, kotlinx.coroutines, Kotlin)'];

bool _registered = false;

/// Adds the VideoKit notice to Flutter's [LicenseRegistry] once per process (04A X1), so hosts show it with the
/// system licence page. Called by `FlutterVideoKit.connect`; safe to call again.
void registerVideoKitLicenses({AssetBundle? bundle}) {
  if (_registered) return;
  _registered = true;
  LicenseRegistry.addLicense(() async* {
    final text = await (bundle ?? rootBundle).loadString(kVideoKitNoticeAsset);
    yield LicenseEntryWithLineBreaks(kVideoKitNoticePackages, text);
  });
}

/// Test hook: allows a new registration in the same process.
@visibleForTesting
void resetVideoKitLicensesForTest() => _registered = false;
