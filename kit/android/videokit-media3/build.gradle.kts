plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 02 §4.0.1: Media3 implementation of the platform engines (VK-M1: PlaybackEngine with HostDataSource).
// Media3 is the only module allowed to use androidx.media3; UI libraries, Flutter and AI runtimes stay forbidden.
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
    api(project(":videokit-playback"))
    implementation(libs.media3.common)
    implementation(libs.media3.datasource)
    implementation(libs.media3.extractor)
    implementation(libs.media3.exoplayer)

    testImplementation(project(":videokit-testkit"))
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
