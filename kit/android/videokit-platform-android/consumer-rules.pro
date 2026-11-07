# Consumer R8 rules for videokit-platform-android (13 §2).
#
# VideoKitFactory (videokit-api-android) finds the assembly by name, so hosts that only compile against the API do
# not pull the engine in. Keep the object and its create(Context, VideoKitConfig) entry point.
-keep class com.videokit.platform.android.AndroidVideoKitAssembly {
    public static final com.videokit.platform.android.AndroidVideoKitAssembly INSTANCE;
    public com.videokit.api.VideoKit create(android.content.Context, com.videokit.api.VideoKitConfig);
}
