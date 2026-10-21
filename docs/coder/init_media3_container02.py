from pathlib import Path
import shutil,json,hashlib
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1media3-container01';B=R/'docs/coder/d1media3-container02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=O/'evidence/media3-container01-freeze.json';assert sha(seal)=='6d08e618dd1b98852830468a69b5048f65b55f4bc0a9117360c7bd414423c4ed';assert all(sha(R/x['path'])==x['sha256'] for x in json.loads(seal.read_text())['files'])
B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses','offline-maven','reference']:shutil.copytree(O/name,B/name)
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','settings-gradle.lockfile']:shutil.copyfile(O/name,B/name)
for name in ['app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:
 p=B/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/name,p)
for name in ['tools','evidence','artifacts']:(B/name).mkdir()
for name in ['local_check.py','review_all.py','run_suites.py','build_candidate.ps1','consumption.init.gradle','VerifyApk.java']:
 s=(O/'tools'/name).read_text().replace('media3-container01','media3-container02');(B/'tools'/name).write_text(s,encoding='utf-8')
p=B/'app/build.gradle.kts';p.write_text(p.read_text().replace('versionCode = 6','versionCode = 7').replace('D1-MEDIA3-CONTAINER01','D1-MEDIA3-CONTAINER02-FIX'))
p=B/'settings.gradle.kts';p.write_text(p.read_text().replace('VideoKitD1Media3Container01','VideoKitD1Media3Container02Fix'))
for name in ['completion-matrix.json','media3-container01-sbom.cdx.json']:shutil.copyfile(O/name,B/name.replace('container01','container02'))
report=R/'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md';assert sha(report)=='4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87';shutil.copyfile(report,B/'reference'/report.name)
shutil.copyfile(R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/IndependentContainerBoundaryCheck.java',B/'reference/IndependentContainerBoundaryCheck-original.java')
shutil.copyfile(R/'docs/milestones/D1_MEDIA3_CONTAINER02_FIX_CODER_REQUIREMENTS_V1.0.md',B/'reference/D1_MEDIA3_CONTAINER02_FIX_CODER_REQUIREMENTS_V1.0.md')
shutil.copyfile(O/'evidence/extractor-source-admission.json',B/'reference/extractor-source-admission-container01.json')
shutil.copyfile(O/'evidence/dependency-license-difference.json',B/'reference/dependency-license-difference-container01.json')
pins=[{'path':p.relative_to(B).as_posix(),'source':(O/p.relative_to(B)).relative_to(R).as_posix(),'sha256':sha(p)} for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle'] for p in sorted((B/folder).rglob('*')) if p.is_file()]
(B/'evidence/baseline-pins.json').write_text(json.dumps(pins,indent=2),encoding='utf-8');print('Created new container02; container01 sealed files1045 unchanged; inherited exact admitted17-coordinate closure.')
