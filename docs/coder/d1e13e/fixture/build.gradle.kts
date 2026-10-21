plugins { alias(libs.plugins.android.application) }
// This Debug fixture is Java only. AGP's built-in Kotlin defaults must not add a runtime.
configurations.configureEach { exclude(group = "org.jetbrains.kotlin"); exclude(group = "org.jetbrains", module = "annotations") }
dependencyLocking { lockAllConfigurations() }
android {
    namespace = "com.videokit.e13.sender"
    compileSdk { version = release(36) { minorApiLevel = 1 } }
    defaultConfig { applicationId = "com.videokit.e13.sender"; minSdk = 31; targetSdk = 36; versionCode = 2; versionName = "E13E-negative-fixture" }
    signingConfigs {
        create("ordinaryFixture") {
            storeFile = file("../fixture-signing.p12")
            storePassword = "e13fixture"
            keyAlias = "e13-ordinary"
            keyPassword = "e13fixture"
        }
    }
    buildTypes { getByName("debug") { signingConfig = signingConfigs.getByName("ordinaryFixture") } }
    sourceSets.getByName("debug").java.srcDir("../binding")
    compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
}
