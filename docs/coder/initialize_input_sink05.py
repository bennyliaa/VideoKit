from pathlib import Path
import json,hashlib,shutil
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1input-sink04';B=R/'docs/coder/d1input-sink05';B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','offline-maven','licenses','reference']:shutil.copytree(O/name,B/name)
for name in ['tools','evidence','app/src/main']:(B/name).mkdir(parents=True,exist_ok=True)
for name in ['build.gradle.kts','settings.gradle.kts','settings-gradle.lockfile','gradle.properties','local.properties','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:shutil.copyfile(O/name,B/name)
for name in ['local_check.py','build_candidate.ps1','run_suites.py','review_all.py','consumption.init.gradle','VerifyApk.java','check_review_output.py','check_review_runner.py']:
 s=(O/'tools'/name).read_text();s=s.replace('input-sink04','input-sink05').replace('INPUT_SINK04','INPUT_SINK05').replace('INPUT_SINK03','INPUT_SINK04').replace('INPUT_SINK02','INPUT_SINK03').replace("'old03'","'old04'").replace("'old02'","'old03'");(B/'tools'/name).write_text(s,encoding='utf-8')
pins=[]
for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses']:
 for p in sorted((O/folder).rglob('*')):
  if p.is_file():pins.append({'source':p.relative_to(R).as_posix(),'path':p.relative_to(O).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'evidence/reused-input-sink04-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
for name in ['app/build.gradle.kts','settings.gradle.kts']:
 p=B/name;p.write_text(p.read_text().replace('versionCode = 4','versionCode = 5').replace('INPUT-SINK04','INPUT-SINK05').replace('InputSink04','InputSink05'),encoding='utf-8')
for name in ['D1_INPUT_SINK05_FIX_CODER_REQUIREMENTS_V1.0.md','D1_INPUT_SINK05_FIX_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/name,B/'reference'/name)
T=R/'docs/tester/D1_INPUT_SINK04_REVIEW_EVIDENCE'
for p in T.iterdir():
 if p.is_file() and p.suffix in ['.java','.py','.json','.stdout','.stderr']:shutil.copyfile(p,B/'reference'/p.name)
p=R/'docs/tester/D1_INPUT_SINK04_FIX_REVIEW_REPORT_V1.0.md';assert hashlib.sha256(p.read_bytes()).hexdigest()=='f527fea952e07f8ee568272170c7ad7b44ae956e2e047fb860d0d1d51796f8c5';shutil.copyfile(p,B/'reference'/p.name)
print('INPUT_SINK05 initialized; old 3683 frozen files untouched')
