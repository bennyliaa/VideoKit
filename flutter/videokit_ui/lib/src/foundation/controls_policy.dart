import 'package:flutter/widgets.dart';
import 'package:videokit_api/videokit_api.dart';

import '../state_view/state_mapping.dart';

/// How the controls layer behaves while a state view is shown (package
/// internal; UI-01 and UI-03 share it).
enum VkControlsMode {
  /// Usable.
  normal,

  /// A recoverable error, released or locked state: controls stay visible
  /// with a disabled look and let taps through to the state view's actions
  /// (TEST-R1 R1-09/R1-02).
  disabled,

  /// Opening (design page 12, ruling 2026-11-08 in TEST-PLAN-6 §4A): back,
  /// title and the spinner; the bottom controls keep a disabled look; host
  /// actions and "more" are not shown yet.
  loading,

  /// An unsupported or fatal error (04A U1, design page 12): only back and
  /// title stay; bottom controls, host actions and "more" are hidden.
  minimal,
}

/// Mode for [model] (the mapped state view) and session state [st].
VkControlsMode vkControlsMode(StateViewModel? model, VideoKitSessionState st) {
  switch (model?.kind) {
    case StateViewKind.error:
      final code = st.error?.code;
      final unsupported =
          code == ErrorCode.unsupportedContainer ||
          code == ErrorCode.unsupportedVideoCodec ||
          code == ErrorCode.unsupportedAudioCodec;
      return unsupported || st.phase == SessionPhase.errorFatal
          ? VkControlsMode.minimal
          : VkControlsMode.disabled;
    case StateViewKind.released || StateViewKind.locked:
      return VkControlsMode.disabled;
    case StateViewKind.loading:
      return VkControlsMode.loading;
    default:
      return VkControlsMode.normal;
  }
}

/// Glass gradient behind [child]; the gradient itself is not hit-testable,
/// so empty areas of the bars do not swallow taps meant for the layers
/// below (state view actions, picture gestures; TEST-R1 R1-09).
Widget vkGlassBehind(Gradient gradient, Widget child) => Stack(
  children: [
    Positioned.fill(
      child: IgnorePointer(
        child: DecoratedBox(decoration: BoxDecoration(gradient: gradient)),
      ),
    ),
    child,
  ],
);
