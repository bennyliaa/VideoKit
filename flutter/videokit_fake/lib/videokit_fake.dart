/// Dart Fake of `videokit_api` for UI development, tests and demos
/// (14 §11.1). Debug/test dependency only — never part of a host release.
///
/// Everything here is demo data: `isDemo` is always true.
library;

export 'src/clock/fake_clock.dart';
export 'src/contract/videokit_contract.dart';
export 'src/demo/demo_data.dart';
export 'src/demo/demo_media_info.dart';
export 'src/demo/demo_picture.dart';
export 'src/fake_edit_project.dart' show FakeEditProject, FakeEditProjectCodec;
export 'src/fake_session.dart';
export 'src/fake_videokit.dart';
export 'src/host_bridge.dart';
export 'src/scenario/scenario.dart';
