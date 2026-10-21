from pathlib import Path
import json,hashlib,shutil
R=Path('D:/CodexProjects/VideoKit');S=R/'docs/coder/d1input-sink01';B=R/'docs/coder/d1input-sink02';B.mkdir(exist_ok=False)
for d in ['src','android','upstream','checks','platform-fixtures','deps','gradle','offline-maven','licenses']:shutil.copytree(S/d,B/d)
for d in ['tools','reference','evidence','app/src/main']:(B/d).mkdir(parents=True,exist_ok=True)
for name in ['build.gradle.kts','settings.gradle.kts','settings-gradle.lockfile','gradle.properties','local.properties','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:shutil.copyfile(S/name,B/name)
for name in ['local_check.py','build_candidate.ps1','consumption.init.gradle','VerifyApk.java']:shutil.copyfile(S/'tools'/name,B/'tools'/name)
pins=[]
for folder in ['src','android','upstream','deps','gradle','licenses']:
 for p in sorted((S/folder).rglob('*')):
  if p.is_file():pins.append({'source':p.relative_to(R).as_posix(),'path':p.relative_to(S).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'evidence/reused-input-sink01-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
for name in ['docs/milestones/D1_INPUT_SINK02_FIX_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_INPUT_SINK02_FIX_TESTER_REQUIREMENTS_V1.0.md','docs/tester/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md','docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/IndependentBoundaryCheck.java','docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/independent-case-results.json','docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/independent-boundaries-3.stdout','docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json']:
 p=R/name;shutil.copyfile(p,B/'reference'/p.name)
assert hashlib.sha256((B/'reference/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md').read_bytes()).hexdigest()=='dc6271e9ed151e0779740c98a63e543830f5a506ea34d641d46ba8702a09c575'
p=B/'app/build.gradle.kts';p.write_text(p.read_text().replace('versionCode = 1','versionCode = 2').replace('D1-INPUT-SINK01','D1-INPUT-SINK02'),encoding='utf-8')
p=B/'settings.gradle.kts';p.write_text(p.read_text().replace('VideoKitD1InputSink01','VideoKitD1InputSink02'),encoding='utf-8')
for name in ['local_check.py','build_candidate.ps1']:
 p=B/'tools'/name;p.write_text(p.read_text().replace('input-sink01-freeze.json','input-sink02-freeze.json').replace('D1_INPUT_SINK01_REVIEW_EVIDENCE','D1_INPUT_SINK02_REVIEW_EVIDENCE').replace('d1_input_sink01_review_evidence','d1_input_sink02_review_evidence'),encoding='utf-8')
print('NEW INPUT_SINK02; old source/JAR/APK/seals unchanged')
