from pathlib import Path
import shutil,json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'docs/coder/d1media3-android01';B=R/'docs/coder/d1media3-android02'
assert not B.exists();B.mkdir()
for name in ['src','android','upstream','checks','platform-fixtures','instrumentation','instrumentation-assets','notice-assets','deps','licenses','offline-maven','gradle']:
    shutil.copytree(O/name,B/name)
for name in ['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties']:
    shutil.copyfile(O/name,B/name)
for sub in ['app/src','tools','evidence','artifacts','reference']:(B/sub).mkdir(parents=True,exist_ok=True)
shutil.copytree(O/'app/src',B/'app/src',dirs_exist_ok=True)
for name in ['build.gradle.kts','gradle.lockfile']:shutil.copyfile(O/'app'/name,B/'app'/name)
for name in ['consumption.init.gradle','VerifyApk.java']:shutil.copyfile(O/'tools'/name,B/'tools'/name)
for p in [B/'app/build.gradle.kts',B/'app/src/androidTest/AndroidManifest.xml',B/'settings.gradle.kts']+list((B/'instrumentation').rglob('*.java'))+list((B/'src/com/videokit/d1android').glob('*.java')):
    text=p.read_text().replace('android01','android02').replace('ANDROID01-READY','ANDROID02-CONTAINER').replace('Android01Ready','Android02Container').replace('D1MA01-','D1MA02-')
    p.write_text(text,encoding='utf-8')
old=B/'instrumentation/com/videokit/d1media3/android01';old.rename(old.with_name('android02'))
for rel in ['docs/milestones/D1_MEDIA3_ANDROID02_CONTAINER_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_MEDIA3_ANDROID02_CONTAINER_TESTER_REQUIREMENTS_V1.0.md','docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03_REPORT_V1.0.md']:
    shutil.copyfile(R/rel,B/'reference'/Path(rel).name)
shutil.copytree(R/'docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03',B/'reference/qualification03')
shutil.copytree(O/'reference',B/'reference/android01',ignore=shutil.ignore_patterns('generation-proposal-source'))
shutil.copyfile(O/'media3-android01-sbom.cdx.json',B/'reference/android01-sbom.cdx.json')
shutil.copyfile(O/'evidence/dependency-license-difference.json',B/'reference/android01-dependency-license-difference.json')
src=R/'docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4';data=src.read_bytes();assert len(data)==8849 and hashlib.sha256(data).hexdigest()=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
(B/'instrumentation-assets/qualified-six-avc.mp4').write_bytes(data)
qualification=B/'reference/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03_REPORT_V1.0.md';assert hashlib.sha256(qualification.read_bytes()).hexdigest()=='a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926'
manifest={'asset':'qualified-six-avc.mp4','bytes':8849,'sha256':hashlib.sha256(data).hexdigest(),'origin':'VideoKit original synthetic six-frame generation D1GEN01-CANDIDATE-001, not BBB','qualificationScope':'D1QUAL03-CANDIDATE-001','qualificationReportSha256':hashlib.sha256(qualification.read_bytes()).hexdigest(),'qualification':'PASS_HOST_CONTAINER_QUALIFICATION_ONLY','notMedia3OrIsolationOrPlaybackEvidence':True,'sampleRepresentation':'Expected Media3 AnnexB4, one IDR NAL each,1340B; actual getter output required','ptsUs':[i*200000 for i in range(6)],'durationUs':1200000,'csdAnnexBHex':'0000000167420028f40809880000000168ce3880','csdSha256':'f6dcad95142c58fce67217fc175449c88b9c697f07db35952c617a66199e75a8','sampleAnnexBHashes':['299447d41af824c07d904ddf424063922e4546edb29d01b0b32e4f3a4e84433f','05f0f4e598823343f8d021b3aa2c62c1a6ca5e9e6446e46b3eff737a3f44709c','01905769af8def741f27e914901dd27767e0faa351874cbb0d9b75bb6d7df2dc','21ab0d10a58ca53b72c1a01eb5ca9014094ca1afd63011e861973ebf27d14032','71c19f10000d2fa907b705369e2c55e147702a841eda326cdcd5ba6feedddaae','ba1f530d497d0c40a9402768be6a0dfcd3ba19b690b5a561218ddf8e5a3f3500']}
(B/'instrumentation-assets/qualified-fixture.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'instrumentation-assets/SYNTHETIC_SOURCE.txt').write_text('VideoKit original synthetic pixels; generated once with JCodec0.2.5 tool02. Exact file independently HOST_CONTAINER-qualified, not Media3/decoder/isolation certified. No JCodec runtime/code in either APK. Generation/qualification full source and license evidence delivered externally. No additional generation in Android02.\n',encoding='utf-8')
print('new isolated Android02 sources and exact fixture copied; no builds or device operations')
