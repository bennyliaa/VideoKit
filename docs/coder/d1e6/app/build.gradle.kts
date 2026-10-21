plugins { alias(libs.plugins.android.application) }

val requested = gradle.startParameter.taskNames.map { it.substringAfterLast(':').lowercase() }
if (requested.any { it.startsWith("connected") || it.contains("manageddevice") || it == "devicecheck" ||
    (it.endsWith("androidtest") && listOf("assemble", "bundle", "package", "compile").none(it::startsWith)) }) {
    throw GradleException("E4_LOCAL_BUILD_ONLY_NO_DEVICE_TASKS")
}
android {
    namespace = "com.videokit.spike.e4"
    compileSdk { version = release(36) { minorApiLevel = 1 } }
    defaultConfig {
        applicationId = "com.videokit.app"
        minSdk = 31
        targetSdk = 36
        versionCode = 6
        versionName = "D1-E6"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk { abiFilters += "arm64-v8a" }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures { buildConfig = true }
    sourceSets.getByName("debug").java.srcDirs("../src", "../android", "../upstream-c14/src", "../upstream-c14/android")
    sourceSets.getByName("debug").jniLibs.srcDir("../upstream-c14/native-libs")
    sourceSets.getByName("debug").assets.srcDir("../upstream-c14/notice-assets")
    packaging { jniLibs { keepDebugSymbols += "**/*.so" } }
    tasks.configureEach {
        if (name.startsWith("connected") || name.contains("ManagedDevice")) enabled = false
    }
}
dependencyLocking { lockAllConfigurations() }
dependencies {
    debugImplementation(libs.media3.spike.muxer)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    // Use the already approved/cached C14 runtime alignment; no dependency downloads.
    constraints {
        debugImplementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10")
        androidTestImplementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10")
        androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
        androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0")
    }
}
