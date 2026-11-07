# Consumer R8 rules for videokit-ui-android (13 §2).
#
# FragmentManager re-creates the embed fragments reflectively after configuration changes and process death.
-keep public class com.videokit.ui.android.VideoKit*Fragment {
    public <init>();
}
# The plugin resolves the debug Fake backend by name; the bridge sets an explicit backend, so nothing else here
# is looked up reflectively.
