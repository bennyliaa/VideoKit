plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 02 §4.0.1: Android assembly of the real VideoKit (VideoKitFactory → core runtime + playback + Media3 engine) and
// the Android capability probe. The assembly needs the Media3 engine module, so Media3 is reachable here
// transitively (recorded deviation from 02 §4.0.1, which lists core and api-android only); this module itself uses
// only Android SDK APIs (MediaCodecList, SystemClock). UI libraries, Flutter and AI runtimes stay forbidden.
videokitDependencyRules {
    forbiddenModules.set(
        mapOf(
            "com\\.google\\.android\\.exoplayer.*:.*" to "Legacy ExoPlayer is not allowed (Media3 only)",
            "androidx\\.compose.*:.*" to "Android UI (Compose) is not allowed",
            "androidx\\.(appcompat|fragment|activity|recyclerview|constraintlayout|viewpager|viewpager2|transition):.*" to
                "Android UI libraries are not allowed",
            "io\\.flutter:.*" to "Flutter embedding is not allowed",
            "org\\.tensorflow:.*" to "AI runtime (TensorFlow) is not allowed",
            "com\\.google\\.mlkit:.*" to "AI runtime (ML Kit) is not allowed",
            "com\\.microsoft\\.onnxruntime:.*" to "AI runtime (ONNX Runtime) is not allowed",
            "org\\.opencv:.*" to "AI/vision runtime (OpenCV) is not allowed",
        ),
    )
}

dependencies {
    api(project(":videokit-api-android"))
    implementation(project(":videokit-playback"))
    implementation(project(":videokit-media3"))

    testImplementation(libs.junit)
}
