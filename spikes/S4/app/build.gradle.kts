plugins {
    id("com.android.application")
}

android {
    namespace = "com.videokit.spike.s4"
    compileSdk {
        version = release(37) {
            minorApiLevel = 2
        }
    }
    defaultConfig {
        applicationId = "com.videokit.spike.s4"
        minSdk = 31
        targetSdk = 35
        versionCode = 1
        versionName = "s4"
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
    // Main process: playback through the Kit while the export runs (15 §4 S4).
    implementation("com.videokit:videokit-media3:1.0.0-dev.1")
    implementation("com.videokit:videokit-api-android:1.0.0-dev.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
    // Worker: Media3 Transformer (Apache-2.0), same version as the Kit's Media3.
    implementation("androidx.media3:media3-transformer:1.11.1")
    implementation("androidx.media3:media3-effect:1.11.1")
    implementation("androidx.media3:media3-muxer:1.11.1")
    implementation("androidx.media3:media3-exoplayer:1.11.1")
}
