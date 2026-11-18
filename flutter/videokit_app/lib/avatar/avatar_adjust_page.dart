import 'dart:async';

import 'package:flutter/material.dart';
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_ui/videokit_ui.dart';

import '../app_scope.dart';
import '../history/history_entry.dart';
import '../l10n/app_text.dart';
import 'avatar_store.dart';
import 'avatar_widgets.dart';

/// Tools of "调整头像" (design page 25).
enum AvatarTool {
  /// Drag up / down to resize ("缩放").
  scale,

  /// Drag to move ("移动").
  move,

  /// Brush away edge pixels ("擦除").
  erase,

  /// Brush the original pixels back ("恢复").
  restore,
}

/// "调整头像" (design page 25, second picture; REQ-ED-07). App business
/// (04A E6 5): runs the Kit's optional cut-out on the picked photo, shows
/// the original and the result on a checkerboard, and offers scale, move,
/// erase and restore, brush size, edge softening, "裁到头部" and
/// "重新识别". "使用此头像" saves the PNG in the App and pops with the
/// [MaskAvatar] (token, size, offset).
class AvatarAdjustPage extends StatefulWidget {
  /// Creates the page.
  const AvatarAdjustPage({
    super.key,
    required this.tools,
    required this.entry,
    required this.source,
  });

  /// The Kit's avatar tools.
  final VideoKitAvatarTools tools;

  /// The picked photo (for the "原图" thumbnail).
  final HistoryEntry entry;

  /// The picked photo as a media source (read through the host).
  final VideoKitMediaSource source;

  @override
  State<AvatarAdjustPage> createState() => AvatarAdjustPageState();
}

/// State (public for tests).
class AvatarAdjustPageState extends State<AvatarAdjustPage> {
  /// Current cut-out, null while preparing or after a failure.
  AvatarImage? avatar;

  /// Error text key, when the cut-out failed.
  String? errorCode;

  /// A cut-out or refinement is running.
  bool busy = false;

  /// Selected tool.
  AvatarTool tool = AvatarTool.erase;

  /// Brush size 0–1 ("笔刷大小").
  double brush = 0.4;

  /// Edge softening 0–1 ("边缘柔化").
  double feather = 0.5;

  /// "裁到头部（含头发）".
  bool cropToHead = true;

  /// Size relative to the tracked head (stored with the mask, 04A E5 4).
  double scale = 1.0;

  /// Offset relative to the head box (stored with the mask).
  Offset offset = Offset.zero;

  final List<(double, double)> _stroke = [];
  late AppScope _scope;
  bool _started = false;
  int _generation = 0;

  static const double _scaleMin = 0.5;
  static const double _scaleMax = 2.0;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _scope = AppScope.of(context);
    if (_started) return;
    _started = true;
    unawaited(prepare());
  }

  /// Runs (or re-runs, "重新识别") the cut-out with the current options.
  Future<void> prepare() async {
    final gen = ++_generation;
    setState(() {
      busy = true;
      errorCode = null;
    });
    try {
      final r = await widget.tools.prepareAvatar(
        widget.source,
        options: AvatarPrepareOptions(cropToHead: cropToHead, feather: feather),
      );
      if (!mounted || gen != _generation) return;
      setState(() {
        avatar = r;
        busy = false;
      });
    } on VideoKitException catch (e) {
      if (!mounted || gen != _generation) return;
      final code = e.error.diagnostic ?? e.error.code.wireName;
      setState(() {
        avatar = null;
        busy = false;
        errorCode = code.contains('AVATAR_NO_FACE') ||
                e.error.code.wireName == 'AVATAR_NO_FACE'
            ? 'AVATAR_NO_FACE'
            : (code.contains('AVATAR_IMAGE_UNSUPPORTED') ||
                      e.error.code.wireName == 'AVATAR_IMAGE_UNSUPPORTED'
                  ? 'AVATAR_IMAGE_UNSUPPORTED'
                  : 'FAILED');
      });
    }
  }

  Future<void> _refine(List<AvatarStroke> strokes, {double? newFeather}) async {
    final current = avatar;
    if (current == null) return;
    setState(() => busy = true);
    try {
      final r = await widget.tools.refineAvatar(
        current,
        strokes,
        feather: newFeather,
      );
      if (mounted) setState(() => avatar = r);
    } on VideoKitException {
      // Keep the previous result.
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  /// Applies one brush stroke along normalized result points.
  Future<void> applyStroke(List<(double, double)> points) => _refine([
    AvatarStroke(
      brush: tool == AvatarTool.restore
          ? AvatarBrush.restore
          : AvatarBrush.erase,
      points: points,
      radius: 0.02 + brush * 0.13,
    ),
  ]);

  /// "使用此头像" / "完成": saves the PNG in the App and pops.
  Future<void> use() async {
    final a = avatar;
    if (a == null) return;
    final String token;
    try {
      token = await _scope.avatars.save(a.png);
    } on AvatarStoreFullException {
      // 04A E7 Q4: never evict an avatar a kept project uses.
      if (!mounted) return;
      final t = AppText.of(context);
      ScaffoldMessenger.of(context)
        ..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(content: Text(t(t.l.avatarStoreFull))));
      return;
    }
    if (!mounted) return;
    Navigator.of(context).pop(
      MaskAvatar(
        avatarToken: token,
        scale: scale,
        offsetX: offset.dx,
        offsetY: offset.dy,
      ),
    );
  }

  (double, double) _toPng(Offset p, double size) => (
    ((p.dx / size - 0.5 - offset.dx) / scale + 0.5).clamp(0.0, 1.0),
    ((p.dy / size - 0.5 - offset.dy) / scale + 0.5).clamp(0.0, 1.0),
  );

  void _panUpdate(DragUpdateDetails e, double size) {
    switch (tool) {
      case AvatarTool.scale:
        setState(
          () => scale = (scale * (1 - e.delta.dy / size)).clamp(
            _scaleMin,
            _scaleMax,
          ),
        );
      case AvatarTool.move:
        setState(
          () => offset = Offset(
            (offset.dx + e.delta.dx / size).clamp(-0.5, 0.5),
            (offset.dy + e.delta.dy / size).clamp(-0.5, 0.5),
          ),
        );
      case AvatarTool.erase || AvatarTool.restore:
        setState(() => _stroke.add(_toPng(e.localPosition, size)));
    }
  }

  void _panEnd(double size) {
    if (_stroke.isEmpty) return;
    final points = List.of(_stroke);
    setState(_stroke.clear);
    unawaited(applyStroke(points));
  }

  String _errorText(AppText a) => a(switch (errorCode) {
    'AVATAR_NO_FACE' => a.l.avatarNoFace,
    'AVATAR_IMAGE_UNSUPPORTED' => a.l.avatarUnsupported,
    _ => a.l.avatarFailed,
  });

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final a = AppText.of(context);
    final s = VkStrings.of(context);
    final d = t.dimensions;
    final current = avatar;
    return Scaffold(
      backgroundColor: t.colors.background,
      appBar: AppBar(
        backgroundColor: t.colors.background,
        leading: VkIconButton(
          icon: t.icons.resolve('back'),
          semanticLabel: s.text('playerBack'),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        title: Text(
          a(a.l.avatarAdjustTitle),
          style: t.typography.titleLarge.copyWith(color: t.colors.textPrimary),
        ),
        actions: [
          Padding(
            padding: EdgeInsetsDirectional.only(end: d.spacing12),
            child: VkButton(
              label: a(a.l.avatarDone),
              onPressed: current == null || busy ? null : () => unawaited(use()),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: ListView(
                padding: EdgeInsetsDirectional.symmetric(
                  horizontal: d.spacing16,
                ),
                children: [
                  SizedBox(height: d.spacing12),
                  _pictures(context, a, current),
                  if (current != null &&
                      current.warnings.contains(AvatarImage.multipleFaces))
                    Padding(
                      padding: EdgeInsetsDirectional.only(top: d.spacing8),
                      child: Text(
                        a(a.l.avatarMultipleFaces),
                        style: t.typography.bodySmall.copyWith(
                          color: t.colors.warning,
                        ),
                      ),
                    ),
                  if (errorCode != null)
                    Padding(
                      padding: EdgeInsetsDirectional.only(top: d.spacing12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            _errorText(a),
                            style: t.typography.body.copyWith(
                              color: t.colors.error,
                            ),
                          ),
                          SizedBox(height: d.spacing8),
                          VkButton(
                            label: a(a.l.avatarChangePhoto),
                            variant: VkButtonVariant.secondary,
                            onPressed: () => Navigator.of(context).maybePop(),
                          ),
                        ],
                      ),
                    ),
                  ..._tools(context, a),
                ],
              ),
            ),
            Padding(
              padding: EdgeInsetsDirectional.all(d.spacing16),
              child: Row(
                children: [
                  Expanded(
                    child: VkButton(
                      label: a(a.l.avatarRedetect),
                      variant: VkButtonVariant.outline,
                      onPressed: busy ? null : () => unawaited(prepare()),
                    ),
                  ),
                  SizedBox(width: d.spacing12),
                  Expanded(
                    child: VkButton(
                      label: a(a.l.avatarUse),
                      onPressed: current == null || busy
                          ? null
                          : () => unawaited(use()),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _pictures(BuildContext context, AppText a, AvatarImage? current) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final original = Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(d.cornerMedium),
          child: AspectRatio(
            aspectRatio: 3 / 4,
            child: Stack(
              fit: StackFit.expand,
              children: [
                _scope.backend.thumbnail(context, widget.entry),
                if (current?.sourceFaceBox case final box?)
                  DashedBox(region: box),
              ],
            ),
          ),
        ),
        SizedBox(height: d.spacing4),
        Text(
          a(a.l.avatarOriginal),
          style: t.typography.caption.copyWith(color: t.colors.textSecondary),
        ),
      ],
    );
    final result = LayoutBuilder(
      builder: (context, c) {
        final size = c.maxWidth;
        return Semantics(
          image: true,
          label: a(a.l.avatarResult),
          child: SizedBox.square(
            dimension: size,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(d.cornerLarge),
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onPanUpdate: current == null
                    ? null
                    : (e) => _panUpdate(e, size),
                onPanEnd: current == null ? null : (_) => _panEnd(size),
                child: AvatarChecker(
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      if (current != null)
                        Transform.translate(
                          offset: Offset(offset.dx * size, offset.dy * size),
                          child: Transform.scale(
                            scale: scale,
                            child: Image.memory(
                              current.png,
                              fit: BoxFit.contain,
                              gaplessPlayback: true,
                            ),
                          ),
                        ),
                      if (current != null)
                        DecoratedBox(
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: t.colors.selection,
                              width: d.focusRingWidth,
                            ),
                            borderRadius: BorderRadius.circular(
                              d.cornerLarge,
                            ),
                          ),
                        ),
                      for (final (x, y) in _stroke)
                        Positioned(
                          left: x * size - d.spacing4,
                          top: y * size - d.spacing4,
                          width: d.spacing8,
                          height: d.spacing8,
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: t.colors.primary.withValues(alpha: 0.6),
                            ),
                          ),
                        ),
                      if (current != null)
                        PositionedDirectional(
                          start: d.spacing12,
                          bottom: d.spacing12,
                          child: Container(
                            padding: EdgeInsetsDirectional.symmetric(
                              horizontal: d.spacing12,
                              vertical: d.spacing4,
                            ),
                            decoration: BoxDecoration(
                              color: t.colors.success,
                              borderRadius: BorderRadius.circular(
                                d.cornerFull,
                              ),
                            ),
                            child: Text(
                              a(a.l.avatarAutoRemoved),
                              style: t.typography.label.copyWith(
                                color: t.colors.successContent,
                              ),
                            ),
                          ),
                        ),
                      if (busy)
                        Center(
                          child: Semantics(
                            label: a(a.l.avatarPreparing),
                            child: CircularProgressIndicator(
                              color: t.colors.primary,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(flex: 2, child: original),
        Padding(
          padding: EdgeInsetsDirectional.symmetric(horizontal: d.spacing8),
          child: Icon(
            t.icons.resolve('next'),
            color: t.colors.textSecondary,
          ),
        ),
        Expanded(flex: 4, child: result),
      ],
    );
  }

  List<Widget> _tools(BuildContext context, AppText a) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final enabled = avatar != null && !busy;
    Widget toolButton(AvatarTool value, String icon, String label) =>
        Expanded(
          child: _ToolButton(
            icon: t.icons.resolve(icon),
            label: label,
            selected: tool == value,
            onTap: enabled ? () => setState(() => tool = value) : null,
          ),
        );
    Widget slider(String label, double value, ValueChanged<double>? onEnd) =>
        Row(
          children: [
            SizedBox(
              width: d.targetMin * 2,
              child: Text(
                label,
                style: t.typography.label.copyWith(
                  color: t.colors.textSecondary,
                ),
              ),
            ),
            Expanded(
              child: VkSlider(
                value: value,
                semanticLabel: label,
                semanticValue: (v) => VkFormat.percent(VkStrings.of(context), v),
                onChangeEnd: onEnd,
              ),
            ),
          ],
        );
    return [
      Padding(
        padding: EdgeInsetsDirectional.only(
          top: d.spacing16,
          bottom: d.spacing8,
        ),
        child: Semantics(
          header: true,
          child: Text(
            a(a.l.avatarAdjust),
            style: t.typography.label.copyWith(color: t.colors.textSecondary),
          ),
        ),
      ),
      Row(
        children: [
          toolButton(AvatarTool.scale, 'fit', a(a.l.avatarToolScale)),
          SizedBox(width: d.spacing8),
          toolButton(AvatarTool.move, 'move', a(a.l.avatarToolMove)),
          SizedBox(width: d.spacing8),
          toolButton(AvatarTool.erase, 'erase', a(a.l.avatarToolErase)),
          SizedBox(width: d.spacing8),
          toolButton(AvatarTool.restore, 'restore', a(a.l.avatarToolRestore)),
        ],
      ),
      SizedBox(height: d.spacing12),
      slider(
        a(a.l.avatarBrushSize),
        brush,
        enabled ? (v) => setState(() => brush = v) : null,
      ),
      slider(
        a(a.l.avatarFeather),
        feather,
        enabled
            ? (v) {
                setState(() => feather = v);
                unawaited(_refine(const [], newFeather: v));
              }
            : null,
      ),
      SizedBox(height: d.spacing8),
      Container(
        padding: EdgeInsetsDirectional.symmetric(
          horizontal: d.spacing16,
          vertical: d.spacing8,
        ),
        decoration: BoxDecoration(
          color: t.colors.surface,
          borderRadius: BorderRadius.circular(d.cornerLarge),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                a(a.l.avatarCropToHead),
                style: t.typography.body.copyWith(color: t.colors.textPrimary),
              ),
            ),
            VkSwitch(
              value: cropToHead,
              semanticLabel: a(a.l.avatarCropToHead),
              onChanged: busy
                  ? null
                  : (v) {
                      setState(() => cropToHead = v);
                      unawaited(prepare());
                    },
            ),
          ],
        ),
      ),
      SizedBox(height: d.spacing16),
    ];
  }
}

class _ToolButton extends StatelessWidget {
  const _ToolButton({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final t = VkTheme.of(context);
    final d = t.dimensions;
    final color = onTap == null
        ? t.colors.disabledContent
        : (selected ? t.colors.primary : t.colors.textSecondary);
    return Semantics(
      button: true,
      selected: selected,
      enabled: onTap != null,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Container(
          constraints: BoxConstraints(minHeight: d.targetMin * 1.5),
          padding: EdgeInsetsDirectional.symmetric(vertical: d.spacing8),
          decoration: BoxDecoration(
            color: selected ? t.colors.primaryContainer : t.colors.surface,
            borderRadius: BorderRadius.circular(d.cornerMedium),
            border: Border.all(
              color: selected ? t.colors.primary : t.colors.surface,
              width: d.focusRingWidth,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: d.icon24),
              SizedBox(height: d.spacing4),
              Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: t.typography.label.copyWith(color: color),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
