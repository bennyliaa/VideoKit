# Consumer R8 rules for videokit-api-android (13 §2). Android hosts always depend on this module, so the
# rules for the platform independent videokit-api jar live here as well.
#
# Enum constant names are part of the stable contract: they are wire names on the Flutter channel, in
# serialized snapshots, in spec/errors.json and in ErrorCode.fromWireName(). Obfuscating them would
# silently map every code to INTERNAL_ERROR_REDACTED.
-keepclassmembers enum com.videokit.api.** {
    <fields>;
    public static **[] values();
    public static ** valueOf(java.lang.String);
}
