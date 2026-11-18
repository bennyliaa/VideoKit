import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../l10n/app_text.dart';
import 'library_lock.dart';
import 'library_lock_page.dart';
import 'library_page.dart';
import 'library_settings_page.dart' show LibraryDataWarning;

/// Entry of the media library (REQ-APP-10): `FLAG_SECURE` while any
/// library route is open (no screenshots, no picture in the recents
/// screen); first entry offers a PIN; a protected library shows the PIN
/// page until unlocked; auto-lock while inside closes whatever is open on
/// top (player, viewer, editor) and shows the PIN page again.
class LibraryGate extends StatefulWidget {
  /// Creates the gate.
  const LibraryGate({super.key});

  /// Opens the library.
  static Future<void> open(BuildContext context) => Navigator.of(context)
      .push(MaterialPageRoute<void>(builder: (_) => const LibraryGate()));

  @override
  State<LibraryGate> createState() => LibraryGateState();
}

/// State (public for tests).
class LibraryGateState extends State<LibraryGate> {
  late AppScope _scope;
  bool _started = false;
  bool _wasUnlocked = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(_scope.backend.library.setSecure(true));
    _scope.libraryLock.addListener(_onLock);
    _wasUnlocked = _scope.libraryLock.unlocked;
  }

  @override
  void dispose() {
    _scope.libraryLock.removeListener(_onLock);
    unawaited(_scope.backend.library.setSecure(false));
    super.dispose();
  }

  void _onLock() {
    final unlocked = _scope.libraryLock.unlocked;
    if (_wasUnlocked && !unlocked && mounted) {
      // Locked while inside: nothing private stays on screen.
      final route = ModalRoute.of(context);
      Navigator.of(context).popUntil((r) => r == route || r.isFirst);
    }
    _wasUnlocked = unlocked;
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final lock = _scope.libraryLock;
    return ValueListenableBuilder<LibrarySettings>(
      valueListenable: lock,
      builder: (context, s, _) {
        if (!s.setUpDone && !s.protected) {
          return _SetUpPage(lock: lock);
        }
        if (!lock.unlocked) {
          return LibraryPinPage(
            key: const ValueKey('library-unlock'),
            mode: PinMode.unlock,
            embedded: true,
            onDone: () => setState(() => _wasUnlocked = true),
          );
        }
        return const LibraryPage();
      },
    );
  }
}

/// First entry: set a PIN or not (FT01A-01).
class _SetUpPage extends StatelessWidget {
  const _SetUpPage({required this.lock});

  final LibraryLock lock;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
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
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsetsDirectional.all(d.spacing24),
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: d.targetMin * 9),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
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
                  ),
                  SizedBox(height: d.spacing16),
                  Semantics(
                    header: true,
                    child: Text(
                      a(a.l.librarySetUpTitle),
                      textAlign: TextAlign.center,
                      style: t.typography.titleLarge.copyWith(
                        color: t.colors.textPrimary,
                      ),
                    ),
                  ),
                  SizedBox(height: d.spacing12),
                  Text(
                    a(a.l.librarySetUpBody),
                    textAlign: TextAlign.center,
                    style: t.typography.body.copyWith(
                      color: t.colors.textSecondary,
                    ),
                  ),
                  // REQ-APP-14: before anything is imported.
                  SizedBox(height: d.spacing16),
                  const LibraryDataWarning(),
                  SizedBox(height: d.spacing24),
                  VkButton(
                    label: a(a.l.librarySetPin),
                    onPressed: () => unawaited(
                      pushPinPage(context, PinMode.setUp),
                    ),
                  ),
                  SizedBox(height: d.spacing8),
                  VkButton(
                    label: a(a.l.librarySkipPin),
                    variant: VkButtonVariant.text,
                    onPressed: () => unawaited(lock.skipSetUp()),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
