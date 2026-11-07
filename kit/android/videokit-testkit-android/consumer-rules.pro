# Consumer R8 rules for videokit-testkit-android (13 §2).
# The testkit is a debug/test-only dependency (14 §11.4) and must not be shipped in release builds.
# Enum names of the testkit are used as demo source references (demo:<scenario>); keep them readable.
-keepclassmembers enum com.videokit.testkit.** {
    <fields>;
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
