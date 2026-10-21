from pathlib import Path
import shutil,json,hashlib,sys
B=Path(__file__).resolve().parents[1];D=B/('evidence/metadata-rejection-'+sys.argv[1]);D.mkdir(exist_ok=False)
coord='com/google/guava/guava-parent/33.3.1-android/guava-parent-33.3.1-android.pom';src=B/'offline-maven'/coord
for name in ['positive','negative']:
 p=D/name;p.mkdir();(p/'gradle').mkdir();shutil.copyfile(B/'gradle/verification-metadata.xml',p/'gradle/verification-metadata.xml')
 (p/'settings.gradle').write_text("rootProject.name='render02-metadata-rejection'",encoding='utf-8')
 overlay=p/'overlay'/coord;overlay.parent.mkdir(parents=True);overlay.write_bytes(src.read_bytes()+(b'\n<!-- controlled corruption: reject this different parent -->\n' if name=='negative' else b''))
 (p/'build.gradle').write_text('''repositories {
 maven { url=uri('overlay');content { includeModule('com.google.guava','guava-parent') };metadataSources { mavenPom() } }
 maven { url=uri('''+repr((B/'offline-maven').as_posix())+''');metadataSources { mavenPom();ignoreGradleMetadataRedirection() } }
}
configurations { probe }
dependencies { probe('com.google.guava:guava:33.3.1-android') { transitive=false } }
tasks.register('resolveProbe') { doLast { configurations.probe.files.each { println('RESOLVED '+it.name) } } }
''',encoding='utf-8')
 (p/'probe-input.json').write_text(json.dumps({'originalSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'probeSha256':hashlib.sha256(overlay.read_bytes()).hexdigest(),'canonicalMirrorModified':False,'verifyMetadata':True,'verificationMode':'strict'},indent=2),encoding='utf-8')
