from pathlib import Path
import shutil
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-android01-freeze.json').exists()
(B/'app/build.gradle.kts').write_text('''plugins { alias(libs.plugins.android.application) }
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
''')
(B/'app/src/main/AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools">
 <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" tools:node="remove" />
 <application android:allowBackup="false" android:usesCleartextTraffic="false" android:process=":media3" android:label="VideoKit Media3 Empty Experiment" />
</manifest>
''')
T=B/'app/src/androidTest';T.mkdir(parents=True)
(T/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" android:versionCode="1" android:versionName="D1-MEDIA3-ANDROID01-READY">
 <application android:allowBackup="false" android:usesCleartextTraffic="false" />
 <instrumentation android:name="com.videokit.d1media3.android01.test.Media3Instrumentation" android:targetPackage="com.videokit.d1media3.android01" android:targetProcesses="com.videokit.d1media3.android01:media3" android:handleProfiling="false" android:functionalTest="true" />
</manifest>
''')
p=B/'settings.gradle.kts';p.write_text(p.read_text().replace('VideoKitD1Media3Container02Fix','VideoKitD1Media3Android01Ready'))
p=B/'app/gradle.lockfile';rows=[]
for line in p.read_text().splitlines():
 if line.startswith('empty='):
  configs=set(line.split('=',1)[1].split(','));configs.update(['debugAndroidTestAnnotationProcessorClasspath','debugAndroidTestRuntimeClasspath']);rows.append('empty='+','.join(sorted(configs)))
 elif line and not line.startswith('#'):
  coordinate,fields=line.split('=');configs=set(fields.split(','))
  if 'debugCompileClasspath' in configs:configs.add('debugAndroidTestCompileClasspath')
  rows.append(coordinate+'='+','.join(sorted(configs)))
 else:rows.append(line)
p.write_text('\n'.join(rows)+'\n')
N=B/'notice-assets';N.mkdir();shutil.copyfile(B/'licenses/Apache-2.0.txt',N/'Apache-2.0.txt')
(N/'NOTICE-framework.txt').write_text('Fixed Media3 1.9.3: Android Open Source Project; Guava33.3.1-android: Guava Authors; AndroidX and Kotlin/JetBrains libraries. Apache License2.0 text included. Exact closure/SBOM/identity/source/license evidence is delivered alongside this experiment. No production release admission.\n')
(B/'instrumentation-assets/SOURCE_AND_LICENSE.txt').write_text('Big Buck Bunny (2008). Copyright Blender Foundation / www.bigbuckbunny.org. Creative Commons Attribution3.0 Unported: https://creativecommons.org/licenses/by/3.0/ . Attribution: https://peach.blender.org/about/ . Published download: https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip . Approved sample is a DERIVATIVE:00:30-00:38 excerpt re-encoded H.264/AAC320x180/8s, not unchanged full original. This batch makes only an exact private test copy, no encode. SHA256720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9,349102bytes. Full inherited manifest/modifications in source delivery.\n')
print('Separate app/test identities configured;17 original coordinates retained; test compile scopes locked and test runtime expected empty pending real strict resolution.')
