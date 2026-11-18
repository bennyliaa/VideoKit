import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'library_lock.dart';
import 'library_platform.dart';

/// What the PIN page is for.
enum PinMode {
  /// Unlock the library (design page 27 first screen).
  unlock,

  /// Set a new PIN (enter, then confirm).
  setUp,

  /// Check the current PIN (before changing or turning it off).
  verify,
}

/// Six dots and a number pad (design page 27): "私密媒体库 / 输入密码",
/// biometric key at the bottom start, "删除", "忘记密码？".
class LibraryPinPage extends StatefulWidget {
  /// Creates the page.
  const LibraryPinPage({
    super.key,
    required this.mode,
    this.onDone,
    this.embedded = false,
  });

  /// Purpose.
  final PinMode mode;

  /// Called when unlocked / set / verified ([embedded] pages; routes pop
  /// with true instead).
  final VoidCallback? onDone;

  /// Shown inside the library gate rather than as its own route.
  final bool embedded;

  @override
  State<LibraryPinPage> createState() => LibraryPinPageState();
}

/// State (public for tests).
class LibraryPinPageState extends State<LibraryPinPage> {
  String _pin = '';
  String? _first;
  String? _error;
  bool _busy = false;
  Timer? _tick;
  bool _triedBiometric = false;
  late PinMode _mode = widget.mode;

  /// Digits entered.
  String get pin => _pin;

  /// Message shown under the dots.
  String? get error => _error;

  LibraryLock get _lock => AppScope.of(context).libraryLock;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // REQ-APP-10: biometric first when turned on (the PIN stays possible).
    if (!_triedBiometric &&
        _mode == PinMode.unlock &&
        _lock.value.biometric) {
      _triedBiometric = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) unawaited(biometric());
      });
    }
    _startTickIfCooling();
  }

  @override
  void dispose() {
    _tick?.cancel();
    super.dispose();
  }

  void _startTickIfCooling() {
    if (_lock.coolDownLeft <= Duration.zero) return;
    _tick?.cancel();
    _tick = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return;
      if (_lock.coolDownLeft <= Duration.zero) {
        t.cancel();
        setState(() => _error = null);
      } else {
        setState(() => _error = _coolDownText());
      }
    });
    _error = _coolDownText();
  }

  String _coolDownText() {
    final a = AppText.of(context);
    final s = (_lock.coolDownLeft.inMilliseconds / 1000).ceil();
    return a(a.l.libraryCoolDown(s));
  }

  void _finish() {
    if (widget.embedded) {
      widget.onDone?.call();
    } else {
      widget.onDone?.call();
      Navigator.of(context).pop(true);
    }
  }

  /// Taps digit [d].
  Future<void> digit(int d) async {
    if (_busy || _pin.length >= LibraryLock.pinLength) return;
    if (_lock.coolDownLeft > Duration.zero && _mode != PinMode.setUp) return;
    setState(() {
      _pin += '$d';
      if (_lock.coolDownLeft <= Duration.zero) _error = null;
    });
    if (_pin.length == LibraryLock.pinLength) await _complete();
  }

  /// "删除" one digit.
  void backspace() {
    if (_pin.isEmpty || _busy) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
  }

  Future<void> _complete() async {
    final a = AppText.of(context);
    final entered = _pin;
    setState(() => _busy = true);
    try {
      switch (_mode) {
        case PinMode.setUp:
          final first = _first;
          if (first == null) {
            setState(() {
              _first = entered;
              _pin = '';
            });
            return;
          }
          if (first != entered) {
            setState(() {
              _first = null;
              _pin = '';
              _error = a(a.l.libraryPinMismatch);
            });
            return;
          }
          await _lock.setPin(entered);
          if (mounted) _finish();
        case PinMode.unlock || PinMode.verify:
          final r = await _lock.enterPin(entered);
          if (!mounted) return;
          switch (r) {
            case PinCheck.ok:
              _finish();
            case PinCheck.wrong:
              setState(() {
                _pin = '';
                _error = a(a.l.libraryWrongPin(_lock.attemptsLeft));
              });
            case PinCheck.coolingDown:
              setState(() => _pin = '');
              _startTickIfCooling();
              setState(() {});
          }
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  /// Fingerprint / face (system BiometricPrompt).
  Future<void> biometric() async {
    final a = AppText.of(context);
    final r = await _lock.unlockWithBiometrics(
      title: a(a.l.libraryBiometricPrompt),
      negative: a(a.l.libraryUsePin),
    );
    if (!mounted) return;
    if (r == AuthResult.success) _finish();
  }

  /// "忘记密码？": system screen lock, then a new PIN (FT01A-03).
  Future<void> forgot() async {
    final a = AppText.of(context);
    final r = await _lock.verifyOwnerForReset(title: a(a.l.libraryResetVerify));
    if (!mounted) return;
    switch (r) {
      case AuthResult.success:
        setState(() {
          _mode = PinMode.setUp;
          _first = null;
          _pin = '';
          _error = null;
        });
      case AuthResult.unavailable:
        await showDialog<void>(
          context: context,
          builder: (context) => _InfoDialog(text: a(a.l.libraryNoDeviceLock)),
        );
      case AuthResult.cancelled || AuthResult.failed:
        setState(() => _error = a(a.l.libraryResetFailed));
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final prompt = switch (_mode) {
      PinMode.unlock => a(a.l.libraryEnterPin),
      PinMode.verify => a(a.l.libraryCurrentPin),
      PinMode.setUp =>
        _first == null ? a(a.l.libraryNewPin) : a(a.l.libraryConfirmPin),
    };
    final lock = _lock.value;
    final showBiometric = _mode == PinMode.unlock && lock.biometric;
    Widget key(String label, VoidCallback? onTap, {String? semantic}) =>
        Semantics(
          button: true,
          label: semantic ?? label,
          excludeSemantics: true,
          child: Material(
            color: t.colors.surface,
            borderRadius: BorderRadius.circular(d.cornerLarge),
            child: InkWell(
              borderRadius: BorderRadius.circular(d.cornerLarge),
              onTap: onTap,
              child: SizedBox(
                height: d.targetMin * 1.3,
                child: Center(
                  child: Text(
                    label,
                    style: t.typography.titleLarge.copyWith(
                      color: t.colors.textPrimary,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
    Widget row(List<Widget> keys) => Padding(
      padding: EdgeInsetsDirectional.only(bottom: d.spacing12),
      child: Row(
        children: [
          for (final (i, k) in keys.indexed) ...[
            if (i > 0) SizedBox(width: d.spacing16),
            Expanded(child: k),
          ],
        ],
      ),
    );
    Widget num(int n) => key(
      '$n',
      () => unawaited(digit(n)),
      semantic: a(a.l.libraryPinDigit(n)),
    );
    final body = SafeArea(
      child: LayoutBuilder(
        builder: (context, c) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: c.maxHeight),
            child: Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: d.targetMin * 8),
                child: Padding(
                  padding: EdgeInsetsDirectional.all(d.spacing24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: EdgeInsetsDirectional.all(d.spacing24),
                        decoration: BoxDecoration(
                          color: t.colors.primaryContainer,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          t.icons.resolve('lock'),
                          size: d.icon24 * 1.5,
                          color: t.colors.primary,
                        ),
                      ),
                      SizedBox(height: d.spacing16),
                      Semantics(
                        header: true,
                        child: Text(
                          a(a.l.libraryLockTitle),
                          style: t.typography.titleLarge.copyWith(
                            color: t.colors.textPrimary,
                          ),
                        ),
                      ),
                      SizedBox(height: d.spacing8),
                      Text(
                        prompt,
                        style: t.typography.body.copyWith(
                          color: t.colors.textSecondary,
                        ),
                      ),
                      SizedBox(height: d.spacing16),
                      Semantics(
                        label: a(a.l.libraryPinProgress(_pin.length)),
                        excludeSemantics: true,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            for (var i = 0; i < LibraryLock.pinLength; i++)
                              Container(
                                margin: EdgeInsetsDirectional.symmetric(
                                  horizontal: d.spacing8,
                                ),
                                width: d.spacing16,
                                height: d.spacing16,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: i < _pin.length
                                      ? t.colors.primary
                                      : null,
                                  border: i < _pin.length
                                      ? null
                                      : Border.all(
                                          color: t.colors.textSecondary,
                                          width: d.borderWidth * 2,
                                        ),
                                ),
                              ),
                          ],
                        ),
                      ),
                      SizedBox(height: d.spacing8),
                      SizedBox(
                        height: d.targetMin,
                        child: Center(
                          child: _error == null
                              ? null
                              : Semantics(
                                  liveRegion: true,
                                  child: Text(
                                    _error!,
                                    textAlign: TextAlign.center,
                                    style: t.typography.bodySmall.copyWith(
                                      color: t.colors.error,
                                    ),
                                  ),
                                ),
                        ),
                      ),
                      row([num(1), num(2), num(3)]),
                      row([num(4), num(5), num(6)]),
                      row([num(7), num(8), num(9)]),
                      row([
                        if (showBiometric)
                          VkIconButton(
                            icon: t.icons.resolve('face'),
                            semanticLabel: a(a.l.libraryBiometricUnlock),
                            style: t.components.buttonText,
                            onPressed: () => unawaited(biometric()),
                          )
                        else
                          const SizedBox.shrink(),
                        num(0),
                        key(a(a.l.libraryPinDelete), backspace),
                      ]),
                      if (_mode == PinMode.unlock ||
                          _mode == PinMode.verify) ...[
                        SizedBox(height: d.spacing16),
                        VkButton(
                          label: a(a.l.libraryForgotPin),
                          variant: VkButtonVariant.text,
                          onPressed: () => unawaited(forgot()),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.background,
        leading: VkIconButton(
          icon: t.icons.resolve('back'),
          semanticLabel: s.text('playerBack'),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
      ),
      body: body,
    );
  }
}

class _InfoDialog extends StatelessWidget {
  const _InfoDialog({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    return AlertDialog(
      backgroundColor: t.colors.surfaceHigh,
      content: Text(
        text,
        style: t.typography.body.copyWith(color: t.colors.textPrimary),
      ),
      actions: [
        VkButton(
          label: a(a.l.libraryConfirm),
          variant: VkButtonVariant.text,
          onPressed: () => Navigator.of(context).pop(),
        ),
      ],
    );
  }
}

/// Pushes the PIN page for [mode]; true when it finished.
Future<bool> pushPinPage(BuildContext context, PinMode mode) async =>
    await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => LibraryPinPage(mode: mode)),
    ) ??
    false;
