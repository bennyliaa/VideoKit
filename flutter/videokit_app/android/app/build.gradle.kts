plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.videokit.videokit_app"
    // Same platform as the videokit_flutter_android plugin and the Kit (37, minor 2): the plugin requires 37,
    // and `compileSdk = 37` alone would ask for android-37, which is not an installed platform.
    compileSdk {
        version = release(37) {
            minorApiLevel = 2
        }
    }
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.videokit.app"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        // VideoKit platform floor: Android 12 / API 31 (13 §2), same as the videokit_flutter_android plugin.
        minSdk = 31
        targetSdk = flutter.targetSdkVersion
        // Uses the version code from pubspec.yaml. When using split APKs, 1000 * ABI_VERSION
        // is added automatically by Flutter. (https://developer.android.com/studio/build/configure-apk-splits#configure-APK-versions)
        // You can force using the value of versionCode by specifying the `-P force-version-code-ignoring-abi=true`
        // flag during build.
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}

// App native part (REQ-APP-01~03, M1-A1): the export "另存为" sink implements the Kit sink API. The plugin keeps
// its Kit dependencies `implementation`, so the App declares the API it compiles against. Resolved from the Kit
// projects by the composite build in settings.gradle.kts; versions match gradle/libs.versions.toml.
dependencies {
    implementation("com.videokit:videokit-api-android:1.0.0-dev.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
}
