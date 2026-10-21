plugins { alias(libs.plugins.android.application) }
if (gradle.startParameter.taskNames.any { it.contains("connected", true) || it.contains("managedDevice", true) }) throw GradleException("OFFLINE_COMPILE_ONLY")
android {
 namespace = "com.videokit.d1input"
 compileSdk { version = release(36) { minorApiLevel = 1 } }
 defaultConfig { applicationId = "com.videokit.d1input"; minSdk = 31; targetSdk = 36; versionCode = 7; versionName = "D1-MEDIA3-CONTAINER02-FIX" }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
 sourceSets.getByName("debug").java.srcDirs("../src", "../android", "../upstream")
}
dependencyLocking { lockAllConfigurations(); lockMode.set(LockMode.STRICT) }
dependencies {
 implementation("androidx.media3:media3-datasource:1.9.3")
 implementation("androidx.media3:media3-muxer:1.9.3")
 implementation("androidx.media3:media3-extractor:1.9.3")
 constraints { implementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0") }
}
