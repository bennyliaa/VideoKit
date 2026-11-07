// Android part of the videokit_flutter_android plugin, built by the Flutter app's Gradle build.
//
// The plugin depends on the native Kit by Maven coordinates. Inside this repository a Flutter app resolves
// them from the Kit build with a composite build in its android/settings.gradle.kts:
//     includeBuild("<repo>")            // substitutes com.videokit:videokit-* with the Kit projects
// The Kit build itself also compiles and unit-tests these sources (kit/android/videokit-flutter-plugin-check),
// so `gradlew build` at the repository root covers the plugin code without a Flutter app.
//
// Versions are literal here because the app's build has no access to the Kit's version catalog; they must
// match gradle/libs.versions.toml (13 §2; Flutter platform packages may use Java/Kotlin 17, 04A B6).
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

// Builds that cannot use includeBuild (the generated Flutter module host of `flutter build aar`) resolve the Kit
// from the repository's local Maven publication: run `./gradlew publishKitMaven` at the repository root first.
// Every project of the consuming build resolves the plugin's dependencies (the Flutter module's `:flutter` project
// too), so the repository is added to all of them, like Flutter's own Gradle plugin adds its engine repository.
val kitMaven = file("../../../build/kit-maven")
if (kitMaven.isDirectory) {
    rootProject.allprojects {
        repositories {
            maven {
                name = "KitMaven"
                url = uri(kitMaven)
            }
        }
    }
}

group = "com.videokit.flutter"
version = "1.0.0-dev.1"

android {
    namespace = "com.videokit.flutter"
    // Same platform as the Kit (gradle/libs.versions.toml: 37 minor 2); `compileSdk = 37` asks for android-37,
    // which is not an installed platform.
    compileSdk {
        version = release(37) {
            minorApiLevel = 2
        }
    }

    defaultConfig {
        minSdk = 31
        // Consumers (Flutter apps and modules) may compile with Flutter's default compileSdk; the plugin API needs 31 only.
        aarMetadata {
            minCompileSdk = 31
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    implementation("com.videokit:videokit-api-android:1.0.0-dev.1")
    // The real VideoKit (core runtime + Media3 engine), reached through VideoKitFactory (VK-M1).
    implementation("com.videokit:videokit-platform-android:1.0.0-dev.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.11.0")
    // Pigeon generated setUp() runs @async methods on Dispatchers.Main, which needs the Android main dispatcher.
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
    // The Kotlin Fake backend is debug-only (14 §11.4): release builds without VideoKitFlutter.setBackend() fail the handshake.
    debugImplementation("com.videokit:videokit-testkit-android:1.0.0-dev.1")
}
