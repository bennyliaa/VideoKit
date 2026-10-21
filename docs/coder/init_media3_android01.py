from pathlib import Path
import shutil,hashlib,json
R=Path('D:/CodexProjects/VideoKit');O=R/'docs/coder/d1media3-container02';B=R/'docs/coder/d1media3-android01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=O/'evidence/media3-container02-freeze.json';assert sha(s)=='0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d';assert all(sha(R/x['path'])==x['sha256'] for x in json.loads(s.read_text())['files'])
B.mkdir(exist_ok=False)
for name in ['src','android','upstream','checks','platform-fixtures','deps','gradle','licenses','offline-maven','reference']:shutil.copytree(O/name,B/name)
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','settings-gradle.lockfile']:shutil.copyfile(O/name,B/name)
for name in ['app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml']:
 p=B/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(O/name,p)
for name in ['tools','evidence','artifacts','instrumentation','instrumentation-assets']:(B/name).mkdir()
for name in ['local_check.py','review_all.py','run_suites.py','consumption.init.gradle','VerifyApk.java']:
 t=(O/'tools'/name).read_text().replace('media3-container02','media3-android01').replace("r'd1media3-container([0-9]{2})'","r'd1media3-android([0-9]{2})'").replace("'D1_MEDIA3_CONTAINER'","'D1_MEDIA3_ANDROID'").replace("'media3-container'+","'media3-android'+").replace('artifacts/media3-container','artifacts/media3-android');(B/'tools'/name).write_text(t,encoding='utf-8')
for file,digest in [('D1_MEDIA3_CONTAINER02_FIX_REVIEW_REPORT_V1.0.md','e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649'),('D1_MEDIA3_ANDROID01_READY_PHASE_A_REPORT_V1.0.md','36c5d4fecfe13b955a96e9194a4f59024df115d85ab3a6292db1794ab205a4cf')]:
 p=R/'docs/tester'/file;assert sha(p)==digest;shutil.copyfile(p,B/'reference'/file)
for p in (R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE').glob('*.json'):shutil.copyfile(p,B/'reference'/('phase-a-'+p.name))
shutil.copyfile(R/'docs/milestones/D1_MEDIA3_ANDROID01_READY_CODER_REQUIREMENTS_V1.0.md',B/'reference/D1_MEDIA3_ANDROID01_READY_CODER_REQUIREMENTS_V1.0.md')
pins=[{'path':p.relative_to(B).as_posix(),'source':(O/p.relative_to(B)).relative_to(R).as_posix(),'sha256':sha(p)} for folder in ['src','android','upstream','checks','platform-fixtures','deps','gradle'] for p in sorted((B/folder).rglob('*')) if p.is_file()];(B/'evidence/baseline-pins.json').write_text(json.dumps(pins,indent=2))
sample=R/'test_media/imgs_and_videos/videos/sample.mp4';assert sha(sample)=='720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9' and sample.stat().st_size==349102
shutil.copyfile(sample,B/'instrumentation-assets/sample.mp4')
for name in ['VIDEO_README.txt','video_manifest.json']:shutil.copyfile(sample.parent/name,B/'reference'/name)
print('New Android01 source baseline copied and pinned; exact approved asset copied only. No build/device/encoder execution.')
