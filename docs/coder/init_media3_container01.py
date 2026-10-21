from pathlib import Path
import shutil,json,hashlib,urllib.request,datetime,zipfile,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1input-sink05';B=R/'docs/coder/d1media3-container01'
B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses','offline-maven']:
 shutil.copytree(O/name,B/name)
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','settings-gradle.lockfile']:
 shutil.copyfile(O/name,B/name)
for name in ['app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:
 p=B/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/name,p)
for name in ['tools','evidence','reference','artifacts']: (B/name).mkdir()
for name in ['build_candidate.ps1','consumption.init.gradle','VerifyApk.java','run_suites.py','local_check.py','review_all.py']:
 shutil.copyfile(O/'tools'/name,B/'tools'/name)
pins=[{'path':p.relative_to(B).as_posix(),'source':(O/p.relative_to(B)).relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle'] for p in sorted((B/folder).rglob('*')) if p.is_file()]
(B/'evidence/baseline-pins.json').write_text(json.dumps(pins,indent=2))
print('CREATED',B,len(pins))
