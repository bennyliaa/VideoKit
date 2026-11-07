plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 02 §4.0.1 / 15 §2.3: Android implementation of the ImageEngine SPI with platform APIs only (ImageDecoder,
// BitmapRegionDecoder, AnimatedImageDrawable, ExifInterface of the SDK); no third-party image library (15 §2.3).
// The rules (decode size, tiles, memory quota) live in videokit-image.
videokitDependencyRules {
    forbiddenModules.set(
        mapOf(
            "androidx\\.media3:.*" to "Media3 is not used for images (15 §2.3)",
            "com\\.google\\.android\\.exoplayer.*:.*" to "ExoPlayer is not allowed",
            "io\\.coil-kt.*:.*" to "No third-party image library (15 §2.3)",
            "com\\.github\\.bumptech\\.glide:.*" to "No third-party image library (15 §2.3)",
            "com\\.facebook\\.fresco:.*" to "No third-party image library (15 §2.3)",
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
    api(project(":videokit-image"))

    testImplementation(project(":videokit-testkit"))
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
