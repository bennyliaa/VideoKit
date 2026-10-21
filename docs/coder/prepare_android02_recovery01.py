from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/coder/d1media3-android02';B=R/'docs/coder/d1media3-android02-recovery01';assert not B.exists();B.mkdir()
for n in ['src','android','upstream','checks','platform-fixtures','instrumentation','instrumentation-assets','notice-assets','deps','licenses','reference','gradle','offline-maven','app/src']:
 shutil.copytree(O/n,B/n)
for n in ['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile']:shutil.copyfile(O/n,B/n)
for n in ['tools','evidence','artifacts','patches']:(B/n).mkdir()
for n in ['consumption.init.gradle','VerifyApk.java']:shutil.copyfile(O/'tools'/n,B/'tools'/n)
for n in ['D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_CODER_REQUIREMENTS_V1.0.md','D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/n,B/'reference'/n)
for n in ['build-main-001','nonmedia-001']:shutil.copytree(O/'evidence'/n,B/'reference/android02-original-evidence'/n)
for n in ['execution-plan.json','comparison-and-lifecycle-contract.json','completion-matrix.json','baseline-preservation.json','source-differences.json','dependency-license-and-consumption.json','build-failure-audit.json']:shutil.copyfile(O/'evidence'/n,B/'reference'/('android02-'+n))
shutil.copyfile(R/'docs/coder/D1_MEDIA3_ANDROID02_CONTAINER_DELIVERY_V1.0.md',B/'reference/D1_MEDIA3_ANDROID02_CONTAINER_DELIVERY_V1.0.md')
paths=sorted(p for n in ['src','android','upstream','instrumentation','instrumentation-assets','notice-assets','app/src','gradle'] for p in (B/n).rglob('*') if p.is_file())+[B/n for n in ['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','app/build.gradle.kts','app/gradle.lockfile']]
pins=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
assert all((O/x['path']).read_bytes()==(B/x['path']).read_bytes() for x in pins)
(B/'evidence/initial-recovery-input-pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print('Independent recovery sources/mirror prepared; original frozen inputs unchanged; no cache copied')
