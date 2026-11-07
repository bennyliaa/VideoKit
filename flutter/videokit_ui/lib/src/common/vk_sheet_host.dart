import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../foundation/layout_class.dart';
import '../l10n/vk_strings.dart';
import '../theme/theme_scope.dart';
import 'vk_buttons.dart';

/// A panel shown by [VkSheetHost].
@immutable
final class VkSheetEntry {
  /// Creates an entry.
  const VkSheetEntry({
    required this.id,
    required this.title,
    required this.builder,
  });

  /// Stable ID (e.g. `tracks`, `hostActionsOverflow`).
  final String id;

  /// Panel title (from ARB).
  final String title;

  /// Content builder.
  final WidgetBuilder builder;
}

/// A short notice shown by [VkSheetHost].
@immutable
final class VkToastEntry {
  /// Creates a toast.
  const VkToastEntry({
    required this.message,
    this.actionLabel,
    this.onAction,
    this.duration = const Duration(seconds: 3),
  });

  /// Message (from ARB).
  final String message;

  /// Optional action label (e.g. 重试).
  final String? actionLabel;

  /// Action callback.
  final VoidCallback? onAction;

  /// Display time.
  final Duration duration;
}

/// Controls the panels and toasts of one [VkSheetHost].
class VkSheetController extends ChangeNotifier {
  final List<VkSheetEntry> _panels = [];
  VkToastEntry? _toast;
  Timer? _toastTimer;

  /// Open panels, bottom first.
  List<VkSheetEntry> get panels => List.unmodifiable(_panels);

  /// Whether any panel is open.
  bool get hasPanel => _panels.isNotEmpty;

  /// Current toast.
  VkToastEntry? get toast => _toast;

  /// Whether panel [id] is open.
  bool isOpen(String id) => _panels.any((p) => p.id == id);

  /// Opens [entry] (replaces an open panel with the same id).
  void show(VkSheetEntry entry) {
    _panels
      ..removeWhere((p) => p.id == entry.id)
      ..add(entry);
    notifyListeners();
  }

  /// Closes the top panel; returns whether one was closed.
  bool closeTop() {
    if (_panels.isEmpty) return false;
    _panels.removeLast();
    notifyListeners();
    return true;
  }

  /// Closes panel [id].
  void close(String id) {
    final before = _panels.length;
    _panels.removeWhere((p) => p.id == id);
    if (before != _panels.length) notifyListeners();
  }

  /// Shows a toast, replacing the current one.
  void showToast(VkToastEntry entry) {
    _toastTimer?.cancel();
    _toast = entry;
    _toastTimer = Timer(entry.duration, hideToast);
    notifyListeners();
  }

  /// Hides the toast.
  void hideToast() {
    _toastTimer?.cancel();
    _toastTimer = null;
    if (_toast == null) return;
    _toast = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _toastTimer?.cancel();
    super.dispose();
  }
}

/// Self-contained overlay for VideoKit components (14 §4.5): panels
/// (bottom sheet in compact layout, side panel from medium), menus and
/// toasts render inside the component's own bounds — no Navigator, Overlay
/// or Scaffold is assumed. Back/Esc closes the top panel; without panels
/// back is left to the host.
class VkSheetHost extends StatefulWidget {
  /// Creates a host.
  const VkSheetHost({super.key, required this.controller, required this.child});

  /// Controller.
  final VkSheetController controller;

  /// Component content.
  final Widget child;

  /// Nearest controller.
  static VkSheetController of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<_VkSheetScope>()!.controller;

  /// Nearest controller, if any.
  static VkSheetController? maybeOf(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<_VkSheetScope>()?.controller;

  @override
  State<VkSheetHost> createState() => _VkSheetHostState();
}

class _VkSheetScope extends InheritedWidget {
  const _VkSheetScope({required this.controller, required super.child});

  final VkSheetController controller;

  @override
  bool updateShouldNotify(_VkSheetScope old) => old.controller != controller;
}

class _VkSheetHostState extends State<VkSheetHost> {
  @override
  Widget build(BuildContext context) {
    final c = widget.controller;
    return _VkSheetScope(
      controller: c,
      child: ListenableBuilder(
        listenable: c,
        builder: (context, _) => PopScope(
          canPop: !c.hasPanel,
          onPopInvokedWithResult: (didPop, _) {
            // TEST-R2 R2-01: every PopScope of the route hears the same back
            // press. Closing is deferred so that, during this dispatch, the
            // page can still see that a panel was open (`hasOpenPanel`) and
            // leave the back press to it.
            if (!didPop && c.hasPanel) scheduleMicrotask(c.closeTop);
          },
          child: CallbackShortcuts(
            bindings: {
              const SingleActivator(LogicalKeyboardKey.escape): c.closeTop,
            },
            child: VkLayoutBuilder(
              builder: (context, layout, _) => Stack(
                children: [
                  // A panel is modal (R1-14): the content behind it leaves the
                  // semantics tree, so screen readers cannot reach controls
                  // under the scrim. Always wrapped, so toggling keeps state.
                  Positioned.fill(
                    child: ExcludeSemantics(
                      excluding: c.hasPanel,
                      child: widget.child,
                    ),
                  ),
                  if (c.hasPanel) ..._panel(context, c, layout),
                  if (c.toast != null) _toast(context, c),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  List<Widget> _panel(
    BuildContext context,
    VkSheetController c,
    VkLayoutClass layout,
  ) {
    final t = VkTheme.of(context);
    final entry = c.panels.last;
    final side = layout != VkLayoutClass.compact;
    final style = t.components.sheet.normal;
    final r = Radius.circular(style.radius);
    final body = FocusScope(
      autofocus: true,
      child: Container(
        decoration: BoxDecoration(
          color: style.background,
          borderRadius: side
              ? BorderRadiusDirectional.horizontal(start: r)
                    .resolve(Directionality.of(context))
              : BorderRadius.vertical(top: r),
          boxShadow: [t.dimensions.modalShadow(t.colors.shadowModal)],
        ),
        padding: style.padding,
        child: SafeArea(
          top: side,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Semantics(
                      header: true,
                      child: Text(entry.title, style: t.typography.titleLarge),
                    ),
                  ),
                  VkIconButton(
                    icon: t.icons.resolve('close'),
                    semanticLabel: VkStrings.of(context).text('commonClose'),
                    onPressed: c.closeTop,
                  ),
                ],
              ),
              SizedBox(height: t.dimensions.spacing8),
              Flexible(
                child: SingleChildScrollView(child: entry.builder(context)),
              ),
            ],
          ),
        ),
      ),
    );
    return [
      Positioned.fill(
        child: Semantics(
          label: VkStrings.of(context).text('commonClose'),
          button: true,
          onTap: c.closeTop,
          child: GestureDetector(
            onTap: c.closeTop,
            child: ColoredBox(color: t.colors.scrim),
          ),
        ),
      ),
      if (side)
        PositionedDirectional(
          top: 0,
          bottom: 0,
          end: 0,
          child: LayoutBuilder(
            builder: (context, _) => ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: VkLayoutClass.mediumMinWidth * 0.6,
                minWidth: VkLayoutClass.mediumMinWidth * 0.5,
              ),
              child: body,
            ),
          ),
        )
      else
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: LayoutBuilder(
            builder: (context, _) => ConstrainedBox(
              constraints: BoxConstraints(
                maxHeight: MediaQuery.sizeOf(context).height * 0.75,
              ),
              child: body,
            ),
          ),
        ),
    ];
  }

  Widget _toast(BuildContext context, VkSheetController c) {
    final t = VkTheme.of(context);
    final toast = c.toast!;
    final style = t.components.toast.normal;
    return Positioned(
      left: t.dimensions.spacing16,
      right: t.dimensions.spacing16,
      bottom: t.dimensions.spacing32 * 2,
      child: SafeArea(
        child: Center(
          child: Semantics(
            liveRegion: true,
            container: true,
            child: Container(
              padding: style.padding,
              decoration: style.decoration.copyWith(
                boxShadow: [
                  t.dimensions.floatingShadow(t.colors.shadowFloating),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Flexible(child: Text(toast.message, style: style.textStyle)),
                  if (toast.actionLabel != null && toast.onAction != null) ...[
                    SizedBox(width: t.dimensions.spacing8),
                    VkButton(
                      label: toast.actionLabel!,
                      variant: VkButtonVariant.text,
                      onPressed: () {
                        c.hideToast();
                        toast.onAction!();
                      },
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
