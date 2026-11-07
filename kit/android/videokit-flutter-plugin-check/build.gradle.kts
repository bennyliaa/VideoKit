import com.android.build.api.dsl.LibraryExtension
import kotlinx.validation.ApiValidationExtension
import org.jetbrains.kotlin.gradle.dsl.ExplicitApiMode
import org.jetbrains.kotlin.gradle.dsl.KotlinAndroidProjectExtension

// Compiles and unit-tests the Android sources of the Flutter plugin (flutter/videokit_flutter_android/android)
// inside the Kit build, against the Kit projects and the Flutter embedding, so `gradlew build` covers the plugin
// without a Flutter app (M0-B2). The sources stay in the plugin package; this module only points at them.
plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

val pluginAndroidDir = rootProject.layout.projectDirectory.dir("flutter/videokit_flutter_android/android")

extensions.configure<LibraryExtension> {
    // Same namespace as the plugin, so R/BuildConfig-free sources compile unchanged.
    namespace = "com.videokit.flutter"
    sourceSets.getByName("main").java.srcDir(pluginAndroidDir.dir("src/main/kotlin"))
    sourceSets.getByName("debug").java.srcDir(pluginAndroidDir.dir("src/debug/kotlin"))
    sourceSets.getByName("test").java.srcDir(pluginAndroidDir.dir("src/test/kotlin"))
}

extensions.configure<KotlinAndroidProjectExtension> {
    // Plugin code is not public Kit API, and the Pigeon generated file has no explicit visibility modifiers.
    explicitApi = ExplicitApiMode.Disabled
    compilerOptions {
        // Pigeon's generated code produces warnings that are not ours to fix.
        allWarningsAsErrors.set(false)
    }
}

// Not a published API: no ABI dump for this module.
extensions.configure<ApiValidationExtension> {
    validationDisabled = true
}

// A Flutter plugin legitimately depends on the Flutter embedding and its AndroidX UI dependencies. Media3 reaches
// the plugin only transitively with the real engine (videokit-platform-android → videokit-media3, VK-M1); the plugin
// code itself never uses it. AI runtimes remain forbidden (02 §4.0.1).
videokitDependencyRules {
    forbiddenModules.set(
        mapOf(
            "org\\.tensorflow:.*" to "AI runtime (TensorFlow) is not allowed",
            "com\\.google\\.mlkit:.*" to "AI runtime (ML Kit) is not allowed",
            "com\\.microsoft\\.onnxruntime:.*" to "AI runtime (ONNX Runtime) is not allowed",
            "org\\.opencv:.*" to "AI/vision runtime (OpenCV) is not allowed",
        ),
    )
}

dependencies {
    implementation(project(":videokit-api-android"))
    implementation(project(":videokit-platform-android"))
    implementation(libs.kotlinx.coroutines.core)
    // Pigeon generated setUp() runs @async methods on Dispatchers.Main (Android main dispatcher).
    implementation(libs.kotlinx.coroutines.android)
    // Debug-only Fake backend (14 §11.4), mirrors debugImplementation in the plugin's own build file.
    debugImplementation(project(":videokit-testkit-android"))
    compileOnly(libs.flutter.embedding.debug)

    testImplementation(libs.flutter.embedding.debug)
    testImplementation(project(":videokit-testkit-android"))
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
