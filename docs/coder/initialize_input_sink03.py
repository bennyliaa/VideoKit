from pathlib import Path
import json,hashlib,shutil
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1input-sink02';B=R/'docs/coder/d1input-sink03';B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','offline-maven','licenses','tools']:shutil.copytree(O/name,B/name)
for name in ['reference','evidence','app/src/main']:(B/name).mkdir(parents=True,exist_ok=True)
for name in ['build.gradle.kts','settings.gradle.kts','settings-gradle.lockfile','gradle.properties','local.properties','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:shutil.copyfile(O/name,B/name)
pins=[]
for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses']:
 for p in sorted((O/folder).rglob('*')):
  if p.is_file():pins.append({'source':p.relative_to(R).as_posix(),'path':p.relative_to(O).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(B/'evidence/reused-input-sink02-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8')
for name in ['app/build.gradle.kts','settings.gradle.kts']:
 p=B/name;p.write_text(p.read_text().replace('versionCode = 2','versionCode = 3').replace('INPUT-SINK02','INPUT-SINK03').replace('InputSink02','InputSink03'),encoding='utf-8')
for name in ['local_check.py','build_candidate.ps1','run_return_checks.py','run_production_core.py']:
 p=B/'tools'/name;p.write_text(p.read_text().replace('input-sink02','input-sink03').replace('INPUT_SINK02','INPUT_SINK03'),encoding='utf-8')
for name in ['D1_INPUT_SINK03_FIX_CODER_REQUIREMENTS_V1.0.md','D1_INPUT_SINK03_FIX_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/name,B/'reference'/name)
T=R/'docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE'
for p in T.iterdir():
 if p.is_file() and (p.suffix in ['.java','.py','.json','.stdout','.stderr']):shutil.copyfile(p,B/'reference'/p.name)
p=R/'docs/tester/D1_INPUT_SINK02_FIX_REVIEW_REPORT_V1.0.md';assert hashlib.sha256(p.read_bytes()).hexdigest()=='c176949cf1c68978bf600ee62997e53360234835f09679ad816fd785db3db71f';shutil.copyfile(p,B/'reference'/p.name)
print('New candidate INPUT_SINK03 initialized; all old files untouched')
