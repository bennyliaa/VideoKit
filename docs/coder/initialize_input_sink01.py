from pathlib import Path
import shutil,json,hashlib,zipfile,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink01';S=R/'docs/coder/d1render02';B.mkdir(exist_ok=True);assert not (B/'evidence/reused-source-pins.json').exists()
for n in ['src','android','upstream','checks','platform-fixtures','deps','evidence','tools','reference','app/src/main']:(B/n).mkdir(parents=True,exist_ok=True)
for n in ['gradle','offline-maven']:shutil.copytree(S/n,B/n,dirs_exist_ok=True)
for n in ['gradlew.bat','build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties']:shutil.copyfile(S/n,B/n)
pins=[]
def copy(src,dst):
 p=R/src;d=B/dst;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d);pins.append({'source':src,'path':dst,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for n in ['AsyncReadBridge','LeaseRegistry','HostFixtures','SourceAdmission']:copy(f'docs/coder/d1render02/upstream/com/videokit/spike/c14/{n}.java',f'upstream/com/videokit/spike/c14/{n}.java')
for n in ['E13SourceGroup','E13FinishOwner','E13ReturnEvents','E13Stages']:copy(f'docs/coder/d1render02/upstream/com/videokit/spike/e4/{n}.java',f'upstream/com/videokit/spike/e4/{n}.java')
copy('docs/coder/d1e13f/src/com/videokit/spike/e4/E4Owned.java','upstream/com/videokit/spike/e4/E4Owned.java')
copy('docs/coder/d1c14/src/com/videokit/spike/c14/SinkCoordinator.java','upstream/com/videokit/spike/c14/SinkCoordinator.java')
copy('docs/coder/d1e13f/android/com/videokit/spike/c14/E6Muxer.java','upstream/com/videokit/spike/c14/E6Muxer.java')
for p in ['docs/milestones/D1_INPUT_SINK01_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_INPUT_SINK01_TESTER_REQUIREMENTS_V1.0.md','docs/OFFLINE_PROGRESS_DURING_DEVICE_WAIT_V1.0.md']:copy(p,'reference/'+Path(p).name)
(B/'evidence/reused-source-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
root=ET.parse(B/'gradle/verification-metadata.xml').getroot();approved={}
for c in root.iter():
 if c.tag.split('}')[-1]!='component':continue
 for a in c:
  for h in a:
   if h.tag.split('}')[-1]=='sha256':approved[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]=h.get('value')
deps=[]
for name in ['media3-common','media3-datasource','media3-database','media3-muxer','media3-container']:
 artifact=name+'-1.9.3.aar';p=B/'offline-maven/androidx/media3'/name/'1.9.3'/artifact;h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==approved[('androidx.media3',name,'1.9.3',artifact)]
 with zipfile.ZipFile(p) as z:(B/'deps'/(name+'.jar')).write_bytes(z.read('classes.jar'))
 deps.append({'coordinate':'androidx.media3:'+name+':1.9.3','aarSha256':h,'classesJarSha256':hashlib.sha256((B/'deps'/(name+'.jar')).read_bytes()).hexdigest(),'source':'existing candidate/root-pinned Google Maven AAR; no binary download'})
(B/'evidence/real-media3-classpath.json').write_text(json.dumps(deps,indent=2),encoding='utf-8')
(B/'settings.gradle.kts').write_text((B/'settings.gradle.kts').read_text().replace('VideoKitD1Render02','VideoKitD1InputSink01'),encoding='utf-8')
(B/'app/src/main/AndroidManifest.xml').write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="D1 Input Sink Compile Probe" android:allowBackup="false" /></manifest>',encoding='utf-8')
(B/'app/build.gradle.kts').write_text('''plugins { alias(libs.plugins.android.application) }
if (gradle.startParameter.taskNames.any { it.contains("connected", true) || it.contains("managedDevice", true) }) throw GradleException("OFFLINE_COMPILE_ONLY")
android {
 namespace = "com.videokit.d1input"
 compileSdk { version = release(36) { minorApiLevel = 1 } }
 defaultConfig { applicationId = "com.videokit.d1input"; minSdk = 31; targetSdk = 36; versionCode = 1; versionName = "D1-INPUT-SINK01" }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_11; targetCompatibility = JavaVersion.VERSION_11 }
 sourceSets.getByName("debug").java.srcDirs("../src", "../android", "../upstream")
}
dependencyLocking { lockAllConfigurations() }
dependencies {
 implementation("androidx.media3:media3-datasource:1.9.3")
 implementation("androidx.media3:media3-muxer:1.9.3")
 constraints { implementation("org.jetbrains.kotlin:kotlin-stdlib:2.2.10"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0"); implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm:1.9.0") }
}
''',encoding='utf-8')
copy('docs/coder/d1render02/tools/consumption.init.gradle','tools/consumption.init.gradle')
print('NEW INPUT_SINK01 SOURCE/REAL MEDIA3 JARS READY; no device/media payload reads')
