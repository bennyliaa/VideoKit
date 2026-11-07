// Native sample host (14 §2.2, §9.3): a pure-engine page (the host renders the Kotlin Fake into its own SurfaceView)
// and add-to-app pages (VideoKit Flutter UI embedded through videokit-ui-android).
//
// Flavors, for the §9.3 package size comparison:
// - engine:   native API + engine only, no Flutter at all;
// - embedded: adds the add-to-app bridge and, with -Pvideokit.embedAar=true, the Flutter module AAR built by
//             `flutter build aar` in flutter/videokit_embed (13 §2.1). Without it the embedding is compile-only and
//             the embed pages report that the Flutter module is missing instead of crashing.
//
// The Kotlin Fake is debug-only (14 §11.4): release builds use the real VideoKitFactory (available from VK-M1).
plugins {
    id("videokit.android.application")
}

val embedAar = providers.gradleProperty("videokit.embedAar").orNull == "true"

android {
    namespace = "com.videokit.samplehost"

    defaultConfig {
        applicationId = "com.videokit.samplehost"
        versionCode = 1
        versionName = "1.0.0-dev.1"
    }

    flavorDimensions += "ui"
    productFlavors {
        create("engine") {
            dimension = "ui"
            applicationIdSuffix = ".engine"
        }
        create("embedded") {
            dimension = "ui"
        }
    }

    // Per-ABI APKs for the 14 §9.3 size comparison (measure/measure_size.ps1).
    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a", "x86_64")
            isUniversalApk = false
        }
    }
}

dependencies {
    implementation(project(":videokit-api-android"))
    implementation(libs.kotlinx.coroutines.android)
    debugImplementation(project(":videokit-testkit-android"))

    "embeddedImplementation"(project(":videokit-ui-android"))
    if (embedAar) {
        // Coordinates of `flutter build aar --build-number 1.0.0-dev.1` (module androidPackage com.videokit.embed).
        "embeddedDebugImplementation"("com.videokit.embed:flutter_debug:1.0.0-dev.1")
        "embeddedReleaseImplementation"("com.videokit.embed:flutter_release:1.0.0-dev.1")
    } else {
        "embeddedCompileOnly"(libs.flutter.embedding.debug)
    }
}

if (embedAar) {
    // The plugin AAR inside the Flutter module depends on the Kit by Maven coordinates; use this build's projects.
    configurations.configureEach {
        resolutionStrategy.dependencySubstitution {
            substitute(module("com.videokit:videokit-api-android")).using(project(":videokit-api-android"))
            substitute(module("com.videokit:videokit-testkit-android")).using(project(":videokit-testkit-android"))
        }
    }
}

// Lint is not part of an application's `check` by default; keep the sample host lint-clean like the libraries.
tasks.named("check") { dependsOn("lintEngineDebug", "lintEmbeddedDebug") }
