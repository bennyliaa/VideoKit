plugins { alias(libs.plugins.android.application) }
if (gradle.startParameter.taskNames.any { it.contains("connected",true)||it.contains("managedDevice",true)||it.contains("install",true) }) throw GradleException("OFFLINE_APP_TEST_BUILD_ONLY")
android {
 namespace = "com.videokit.d1media3.android01"
 testNamespace = "com.videokit.d1media3.android01.test"
 compileSdk { version = release(36) { minorApiLevel = 1 } }
 defaultConfig {
  applicationId = "com.videokit.d1media3.android01"
  testApplicationId = "com.videokit.d1media3.android01.test"
  minSdk = 31; targetSdk = 36; versionCode = 1; versionName = "D1-MEDIA3-ANDROID01-READY"
  testInstrumentationRunner = "com.videokit.d1media3.android01.test.Media3Instrumentation"
 }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
 sourceSets.getByName("debug").java.srcDirs("../src","../android","../upstream")
 sourceSets.getByName("debug").assets.srcDir("../notice-assets")
 sourceSets.getByName("androidTest").java.srcDir("../instrumentation")
 sourceSets.getByName("androidTest").assets.srcDirs("../instrumentation-assets","../notice-assets")
}
dependencyLocking { lockAllConfigurations(); lockMode.set(LockMode.STRICT) }
dependencies {
 implementation("androidx.media3:media3-datasource:1.9.3")
 implementation("androidx.media3:media3-muxer:1.9.3")
 implementation("androidx.media3:media3-extractor:1.9.3")
 // Framework Instrumentation; no new AndroidX runner/junit/encoder dependency.
 constraints { implementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0") }
}
