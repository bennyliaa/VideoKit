import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

/// Rebuilds only when the selected slice of a [ValueListenable] changes
/// (14 §4.2). E.g. buttons select `phase`/`muted` and are not rebuilt by
/// 4 Hz position updates.
class VkSelector<S, T> extends StatefulWidget {
  /// Creates a selector.
  const VkSelector({
    super.key,
    required this.listenable,
    required this.select,
    required this.builder,
    this.equals,
  });

  /// Source.
  final ValueListenable<S> listenable;

  /// Picks the needed fields.
  final T Function(S state) select;

  /// Builds from the selected value.
  final Widget Function(BuildContext context, T value) builder;

  /// Equality of selected values; defaults to `==`.
  final bool Function(T a, T b)? equals;

  @override
  State<VkSelector<S, T>> createState() => _VkSelectorState<S, T>();
}

class _VkSelectorState<S, T> extends State<VkSelector<S, T>> {
  late T _value;

  @override
  void initState() {
    super.initState();
    _value = widget.select(widget.listenable.value);
    widget.listenable.addListener(_onChange);
  }

  @override
  void didUpdateWidget(VkSelector<S, T> oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!identical(oldWidget.listenable, widget.listenable)) {
      oldWidget.listenable.removeListener(_onChange);
      widget.listenable.addListener(_onChange);
    }
    _value = widget.select(widget.listenable.value);
  }

  bool _same(T a, T b) => (widget.equals ?? (x, y) => x == y)(a, b);

  void _onChange() {
    final next = widget.select(widget.listenable.value);
    if (_same(_value, next)) return;
    setState(() => _value = next);
  }

  @override
  void dispose() {
    widget.listenable.removeListener(_onChange);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.builder(context, _value);
}
