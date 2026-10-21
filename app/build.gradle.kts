plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

// D1 C14: vulnerable UTP/emulator-control tool dependencies remain pinned, not silently overridden.
// Compile/package stays available. Device tests later use explicitly authorized direct instrumentation.
val d1ToolProbe = providers.gradleProperty("videokit.d1.toolGuardProbe").orNull
val d1RequestedTools = gradle.startParameter.taskNames + listOfNotNull(d1ToolProbe)
if (d1RequestedTools.any {
        val name = it.substringAfterLast(':').lowercase()
        name.startsWith("connected") || name == "devicecheck" || name.contains("manageddevice") ||
            (name.endsWith("androidtest") && listOf("assemble", "bundle", "package", "compile").none(name::startsWith))
    }) {
    throw GradleException("D1_C14_TOOL_EXECUTION_RESTRICTED: UTP/managed/connected Gradle device tasks require a supported patched toolchain review. No device action has run.")
}
tasks.configureEach {
    var d1Type: Class<*>? = javaClass
    var d1Restricted = false
    while (d1Type != null) {
        val d1Name = d1Type.name
        if (d1Name.startsWith("com.android.build.gradle.internal.tasks.") &&
            (d1Name.contains("ManagedDevice") || d1Name.endsWith("DeviceProviderInstrumentTestTask"))) {
            d1Restricted = true
        }
        d1Type = d1Type.superclass
    }
    if (d1Restricted) {
        enabled = false
        description = "D1_C14_RESTRICTED_UTP: ${description.orEmpty()}"
    }
}

android {
    namespace = "com.videokit.app"
    ndkVersion = "30.0.16248370" // Installed NDK used for the D1 C14 ARM64 JNI lease adapter.
    compileSdk {
        version = release(36) {
            minorApiLevel = 1
        }
    }

    defaultConfig {
        applicationId = "com.videokit.app"
        minSdk = 31
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
    }
    packaging { jniLibs { keepDebugSymbols += "**/*.so" } }
    sourceSets.getByName("debug").java.srcDirs(
        "../docs/coder/d1c14/src", "../docs/coder/d1c14/android"
    )
    sourceSets.getByName("androidTest").java.srcDir("../docs/coder/d1c14/device")
    sourceSets.getByName("debug").jniLibs.srcDir("../docs/coder/d1c14/native-libs")
    sourceSets.getByName("debug").assets.srcDir("../docs/coder/d1c14/notice-assets")
}

dependencyLocking { lockAllConfigurations() }

dependencies {
    debugImplementation(libs.media3.spike.exoplayer)
    debugImplementation(libs.media3.spike.transformer)
    debugImplementation(libs.media3.spike.muxer)
    debugImplementation(libs.media3.spike.ui)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    testImplementation(libs.junit)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
    debugImplementation(libs.androidx.compose.ui.tooling)
}
