import kotlinx.validation.ApiValidationExtension
import org.jetbrains.kotlin.gradle.dsl.ExplicitApiMode
import org.jetbrains.kotlin.gradle.dsl.KotlinAndroidProjectExtension

// add-to-app bridge for native hosts (14 §9): Flutter engine group and prewarming, Fragment / View wrappers and the
// per-engine embed channel. The Flutter UI itself (`videokitEmbedMain`) and the plugin classes reach the host app
// through the Flutter module AAR (`flutter build aar`, 13 §2.1), so the Flutter embedding and the plugin are
// compile-only here.
plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

extensions.configure<KotlinAndroidProjectExtension> {
    // The committed Pigeon output (gen/) has no visibility modifiers and produces compiler warnings; the
    // hand-written public API still declares `public` explicitly and is tracked by the ABI dump.
    explicitApi = ExplicitApiMode.Disabled
    compilerOptions {
        allWarningsAsErrors.set(false)
    }
}

extensions.configure<ApiValidationExtension> {
    // The embed protocol is internal to the bridge and the Flutter module; it is versioned by its own handshake.
    ignoredPackages += "com.videokit.ui.android.gen"
}

// M0-B3 rule: the bridge depends only on api-android (with the Kotlin stdlib and coroutines it exports) and the
// Flutter embedding (with the AndroidX libraries the embedding itself brings). Media3 and AI runtimes stay forbidden.
videokitDependencyRules {
    allowedModules.set(
        listOf(
            "org\\.jetbrains\\.kotlin:kotlin-stdlib.*",
            "org\\.jetbrains\\.kotlinx:kotlinx-coroutines-(core|core-jvm|bom)",
            "org\\.jetbrains:annotations",
            "io\\.flutter:.*",
            // Transitive dependencies of io.flutter:flutter_embedding_* (Fragment, lifecycle, window, ...).
            "androidx\\..*:.*",
            "com\\.getkeepsafe\\.relinker:relinker",
            // Nullness annotations of androidx.exifinterface, itself a dependency of the embedding.
            "org\\.jspecify:jspecify",
            // Brought by the embedding's androidx.lifecycle (1.7.1, aligned to 1.11.0 by the coroutines BOM). The
            // bridge's own code does not use Dispatchers.Main (MainDispatcher, non-@async embed channel).
            "org\\.jetbrains\\.kotlinx:kotlinx-coroutines-android",
        ),
    )
    forbiddenModules.set(
        mapOf(
            "androidx\\.media3:.*" to "Media3 is not allowed in the UI bridge (the Kit owns playback)",
            "androidx\\.compose.*:.*" to "Compose is not used by the UI bridge",
            "org\\.tensorflow:.*" to "AI runtime (TensorFlow) is not allowed",
            "com\\.google\\.mlkit:.*" to "AI runtime (ML Kit) is not allowed",
            "com\\.microsoft\\.onnxruntime:.*" to "AI runtime (ONNX Runtime) is not allowed",
            "org\\.opencv:.*" to "AI/vision runtime (OpenCV) is not allowed",
        ),
    )
}

dependencies {
    api(project(":videokit-api-android"))
    // Provided at runtime by the Flutter module AAR (embedding, AndroidX Fragment, the VideoKit plugin).
    compileOnly(libs.flutter.embedding.debug)
    // Plugin classes only, without the plugin's own runtime dependencies (they ship inside the Flutter module AAR).
    compileOnly(project(":videokit-flutter-plugin-check")) { isTransitive = false }

    testImplementation(libs.flutter.embedding.debug)
    testImplementation(project(":videokit-flutter-plugin-check"))
    testImplementation(project(":videokit-testkit"))
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
