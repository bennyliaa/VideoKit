import 'package:flutter/services.dart';

/// Runtime permissions the App asks for (VK-M8). Photos and videos are
/// opened through the system document picker (`ACTION_OPEN_DOCUMENT`,
/// REQ-APP-01), which needs no storage permission; the camera is asked for
/// only when the user taps "拍一张".
enum AppPermission {
  /// Camera ("拍一张", REQ-ED-07).
  camera,
}

/// State of a permission.
enum PermissionState {
  /// Granted.
  granted,

  /// Denied this time; asking again may show the system dialog.
  denied,

  /// Denied with "don't ask again": only the system settings can change it.
  permanentlyDenied,

  /// Not available on this build or device (e.g. the native side is not
  /// there yet).
  unavailable,
}

/// The App's permission service (App business, not the module).
abstract interface class AppPermissions {
  /// Current state of [p] without asking.
  Future<PermissionState> status(AppPermission p);

  /// Asks for [p] (the system dialog) and returns the result.
  Future<PermissionState> request(AppPermission p);

  /// Opens the App's page in the system settings.
  Future<void> openSettings();
}

/// Demo permissions (tests and the demo flavor): the answers are set by
/// the caller; records each request.
final class DemoPermissions implements AppPermissions {
  /// Creates the service; every permission starts as [initial].
  DemoPermissions({PermissionState initial = PermissionState.granted})
    : _initial = initial;

  final PermissionState _initial;
  final Map<AppPermission, PermissionState> _states = {};

  /// Sets what [status] reports for [p] (tests: "not asked yet").
  void setStatus(AppPermission p, PermissionState s) => _states[p] = s;

  /// What the next [request] returns per permission (default: granted).
  final Map<AppPermission, PermissionState> answers = {};

  /// Requests, in order.
  final List<AppPermission> requested = [];

  /// Settings openings.
  int settingsOpened = 0;

  @override
  Future<PermissionState> status(AppPermission p) async =>
      _states[p] ?? _initial;

  @override
  Future<PermissionState> request(AppPermission p) async {
    requested.add(p);
    final r = answers[p] ?? PermissionState.granted;
    _states[p] = r;
    return r;
  }

  @override
  Future<void> openSettings() async => settingsOpened++;
}

/// Permissions over the App's own channel (native side: VK-M8 / M5A native
/// batch). Until the native handler exists every call reports
/// [PermissionState.unavailable].
final class ChannelPermissions implements AppPermissions {
  /// Creates the service on [methods].
  const ChannelPermissions({
    this.methods = const MethodChannel('videokit_app/permissions'),
  });

  /// Channel.
  final MethodChannel methods;

  Future<PermissionState> _call(String method, AppPermission p) async {
    try {
      final r = await methods.invokeMethod<String>(method, {
        'permission': p.name,
      });
      return PermissionState.values
              .where((s) => s.name == r)
              .firstOrNull ??
          PermissionState.unavailable;
    } on MissingPluginException {
      return PermissionState.unavailable;
    } on PlatformException {
      return PermissionState.unavailable;
    }
  }

  @override
  Future<PermissionState> status(AppPermission p) => _call('status', p);

  @override
  Future<PermissionState> request(AppPermission p) => _call('request', p);

  @override
  Future<void> openSettings() async {
    try {
      await methods.invokeMethod<void>('openSettings');
    } on MissingPluginException {
      // Native side not there yet.
    } on PlatformException {
      // Ignored: nothing else to do.
    }
  }
}
