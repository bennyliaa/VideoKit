plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 15 §1.5 / §2.8 (option c1), M6-B1: export worker in the :videokit_export process (Media3 Transformer) and the
// main process exporter that supervises it (CompositionExporter SPI).
// Like videokit-media3 it may use androidx.media3; UI libraries, Flutter and AI runtimes stay forbidden.
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
    api(project(":videokit-core"))
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.media3.common)
    implementation(libs.media3.datasource)
    implementation(libs.media3.extractor)
    implementation(libs.media3.transformer)
    implementation(libs.media3.effect)
    implementation(libs.media3.muxer)
    // DecoderInputBuffer of the asset loader; transitive through Transformer, declared so it is on the compile path.
    implementation(libs.media3.decoder)

    testImplementation(project(":videokit-testkit"))
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
