plugins { alias(libs.plugins.android.application) }
if (gradle.startParameter.taskNames.any { it.contains("connected", true) || it.contains("managedDevice", true) }) throw GradleException("OFFLINE_BUILD_ONLY")
android {
    namespace = "com.videokit.d1present"
    compileSdk { version = release(36) { minorApiLevel = 1 } }
    defaultConfig {
        // A separately reviewable empty sandbox. Never a way around the disabled original phone app.
        applicationId = "com.videokit.d1present"
        minSdk = 31
        targetSdk = 36
        versionCode = 2
        versionName = "D1-RENDER02"
        testInstrumentationRunner = "com.videokit.d1present.RenderInstrumentation"
        ndk { abiFilters += "arm64-v8a" }
    }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
    buildFeatures { buildConfig = true }
    sourceSets.getByName("debug").java.srcDirs("../src", "../android", "../upstream")
    sourceSets.getByName("debug").jniLibs.srcDir("../native-libs")
    sourceSets.getByName("debug").assets.srcDirs("../notice-assets", "../fixture-assets")
    packaging { jniLibs { keepDebugSymbols += "**/*.so" } }
}
dependencyLocking { lockAllConfigurations() }
dependencies {
    // Preserve the approved runtime alignment; no new backend/download. Not claimed as a player.
    debugImplementation(libs.media3.spike.muxer)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    constraints {
        debugImplementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10")
        androidTestImplementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10")
        androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
        androidTestImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0")
    }
}
