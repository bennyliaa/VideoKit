from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=R/'docs/coder/d1media3-android02-recovery01';B=R/'docs/coder/d1media3-android02-fix02';assert not B.exists();B.mkdir()
for n in ['src','android','upstream','checks','platform-fixtures','instrumentation','instrumentation-assets','notice-assets','deps','licenses','reference','gradle','offline-maven','app/src']:shutil.copytree(O/n,B/n)
for n in ['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile']:shutil.copyfile(O/n,B/n)
for n in ['tools','evidence','artifacts','patches']:(B/n).mkdir()
for n in ['consumption.init.gradle','VerifyApk.java']:shutil.copyfile(O/'tools'/n,B/'tools'/n)
for n in ['D1_MEDIA3_ANDROID02_FIX02_CODER_REQUIREMENTS_V1.0.md','D1_MEDIA3_ANDROID02_FIX02_TESTER_REQUIREMENTS_V1.0.md']:shutil.copyfile(R/'docs/milestones'/n,B/'reference'/n)
shutil.copyfile(R/'docs/tester/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_PHASE_B_REVIEW_REPORT_V1.0.md',B/'reference/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_PHASE_B_REVIEW_REPORT_V1.0.md')
shutil.copytree(R/'docs/tester/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_REVIEW_EVIDENCE',B/'reference/recovery01-independent-b')
for n in ['execution-plan.json','comparison-and-lifecycle-contract.json','delivery-summary.json','known-observation-gaps.json']:shutil.copyfile(O/'evidence'/n,B/'reference'/('recovery01-'+n))
for n in ['src/com/videokit/d1android/ExperimentContract.java','app/build.gradle.kts','app/src/androidTest/AndroidManifest.xml']:
 p=B/n;p.write_text(p.read_text().replace('D1-MEDIA3-ANDROID02-RECOVERY01','D1-MEDIA3-ANDROID02-FIX02'),encoding='utf-8')
s=(O/'tools/build_once.py').read_text().replace("E/'recovery01-freeze.json'","E/'fix02-freeze.json'").replace("HOME=B/'recovery-gradle-home'","HOME=B/'fix02-gradle-home'").replace('D1_MEDIA3_ANDROID02_BUILD_RECOVERY01','D1_MEDIA3_ANDROID02_FIX02')
s=s.replace("assert prior.get('daemonOriginalReturned') and prior.get('exitCode') in [0,1] and (prior.get('sourceCompileFailure') or (E/'stage-a-source-change-authority.json').exists())","assert prior.get('daemonOriginalReturned') and prior.get('exitCode')==1 and prior.get('sourceCompileFailure')")
(B/'tools/build_once.py').write_text(s,encoding='utf-8')
print('FIX02 independent inputs prepared, no cache or old candidate mutation')
