from pathlib import Path
import json,hashlib,shutil
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1input-sink03';B=R/'docs/coder/d1input-sink04';B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','offline-maven','licenses','tools']:shutil.copytree(O/name,B/name)
for name in ['reference','evidence','app/src/main']:(B/name).mkdir(parents=True,exist_ok=True)
for name in ['build.gradle.kts','settings.gradle.kts','settings-gradle.lockfile','gradle.properties','local.properties','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:shutil.copyfile(O/name,B/name)
pins=[]
for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses']:
 for p in sorted((O/folder).rglob('*')):
  if p.is_file():pins.append({'source':p.relative_to(R).as_posix(),'path':p.relative_to(O).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'evidence/reused-input-sink03-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
for name in ['app/build.gradle.kts','settings.gradle.kts']:
 p=B/name;p.write_text(p.read_text().replace('versionCode = 3','versionCode = 4').replace('INPUT-SINK03','INPUT-SINK04').replace('InputSink03','InputSink04'),encoding='utf-8')
for name in ['build_candidate.ps1','run_suites.py']:
 p=B/'tools'/name;p.write_text(p.read_text().replace('input-sink03','input-sink04').replace('INPUT_SINK03','INPUT_SINK04'),encoding='utf-8')
for name in ['D1_INPUT_SINK04_FIX_CODER_REQUIREMENTS_V1.0.md','D1_INPUT_SINK04_FIX_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/name,B/'reference'/name)
T=R/'docs/tester/D1_INPUT_SINK03_REVIEW_EVIDENCE'
for p in T.iterdir():
 if p.is_file() and p.suffix in ['.java','.py','.json','.stdout','.stderr']:shutil.copyfile(p,B/'reference'/p.name)
p=R/'docs/tester/D1_INPUT_SINK03_FIX_REVIEW_REPORT_V1.0.md';assert hashlib.sha256(p.read_bytes()).hexdigest()=='dfd9266819457f5d153d1a1d0c4d34fa65e7ee19e06b5e3cd027ad3d2172b5f3';shutil.copyfile(p,B/'reference'/p.name)
for name in ['D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md','official-added-dependencies']:
 p=O/'reference'/name
 if p.is_dir():shutil.copytree(p,B/'reference'/name)
 elif p.is_file():shutil.copyfile(p,B/'reference'/name)
print('INPUT_SINK04 initialized; all prior frozen files untouched')
