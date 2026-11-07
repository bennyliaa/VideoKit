plugins {
    id("com.android.application")
}

android {
    namespace = "com.videokit.spike.s1"
    compileSdk {
        version = release(37) {
            minorApiLevel = 2
        }
    }
    defaultConfig {
        applicationId = "com.videokit.spike.s1"
        minSdk = 31
        targetSdk = 35
        versionCode = 1
        versionName = "s1"
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
    implementation("com.videokit:videokit-media3:1.0.0-dev.1")
    implementation("com.videokit:videokit-api-android:1.0.0-dev.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.11.0")
}
