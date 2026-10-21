from pathlib import Path
import hashlib,json,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=R/'docs/coder/d1media3-container01';assert not (B/'evidence/media3-container02-freeze.json').exists()
s=(O/'tools/prepare_batch.py').read_text().replace('media3-container01','media3-container02').replace("O=R/'docs/coder/d1input-sink05'","O=R/'docs/coder/d1media3-container01'").replace('build-main-004','build-main-001').replace("'buildAttempt':'004'","'buildAttempt':'001'").replace('local-007','local-002')
a=s.index('def lock(path):');z=s.index("jar=B/'artifacts/",a)
block='''def lock(path):return {l.split('=')[0] for l in path.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')}
assert len(lock(B/'app/gradle.lockfile'))==17
for name in ['app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']:
 assert (B/name).read_bytes()==(O/name).read_bytes()
oldRecords=json.loads((O/'evidence/actual-consumption/artifacts.json').read_text())
assert {(x['coordinate'],x['artifact'],x['sha256']) for x in records}=={(x['coordinate'],x['artifact'],x['sha256']) for x in oldRecords}
dump(E/'dependency-license-difference.json',{'runtimeCoordinates':17,'newCoordinates':[],'versionChanges':[],'newBinaryDownloads':0,'newVerificationPins':0,'allLocksAndVerificationMetadataByteIdentical':True,'actualConsumptionIdentityClosureUnchanged':True,'inheritedLimitedNewUseIndependentAdmission':'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md','inheritedReportSha256':'4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87','scope':'Fixed extractor/decoder1.9.3 identity/license/strict finite offline use only; old report overall FAIL/functional OPEN retained','newFixIndependentReview':'PENDING','platformRuntimeAdmission':False})
dump(E/'inherited-admission.json',{'sourceEvidence':'reference/extractor-source-admission-container01.json','independentReport':'reference/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md','independentReportSha256':'4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87','status':'INHERIT_LIMITED_OFFLINE_SOURCE_LICENSE_STRICT_ADMISSION_ONLY','sourceAarClassesJarUnchanged':True,'newFixNotIndependentlyPassed':True})
'''
s=s[:a]+block+s[z:]
s=s.replace('assert jar.exists();','assert not jar.exists();').replace("zipfile.ZipFile(jar,'w',","zipfile.ZipFile(jar,'x',").replace("'versionCode':6","'versionCode':7").replace('D1-MEDIA3-CONTAINER01','D1-MEDIA3-CONTAINER02-FIX')
s=s.replace("for n in ['01','02','03','04','05']]:","for n in ['01','02','03','04','05']]+[('d1media3-container01','media3-container01-freeze.json')]:")
s=s.replace('==4511','==5556').replace("'oldFrozenUnchanged':4511","'oldFrozenUnchanged':5556")
s=s.replace("{'src/com/videokit/d1input/TemporaryOutput.java','gradle/verification-metadata.xml'}","{'src/com/videokit/d1input/TemporaryOutput.java'}").replace("'newProductionJava':['HostMp4Inspection','MatureContainerRemux']","'newProductionJava':[],'newChecks':['ContainerB01Regression','ContainerPendingOrderCheck']")
(B/'tools/prepare_batch.py').write_text(s,encoding='utf-8')
for name in ['check_review_output.py','check_review_runner.py']:
 s=(O/'tools'/name).read_text().replace('media3-container01','media3-container02').replace('D1_MEDIA3_CONTAINER01','D1_MEDIA3_CONTAINER02').replace('local-007','local-002').replace('FinalLocal007','FinalLocal002').replace('D1_INPUT_SINK04','D1_MEDIA3_CONTAINER01').replace('D1_INPUT_SINK03','D1_INPUT_SINK05').replace('coder-documented-entry-prefreeze-003','coder-documented-entry-prefreeze-001')
 if name=='check_review_output.py':s=s.replace('rows=[]',"negatives['existing-child']=positive\nrows=[]").replace('7 wrong paths','8 wrong paths')
 else:s=s.replace('==56','==60').replace("'positiveOriginalReturnedRuns':56","'positiveOriginalReturnedRuns':60").replace("'negativePaths':7","'negativePaths':8").replace('rows=[]',"targets['existing-child']=positive\nrows=[]").replace('+ 7 rejected roots','+ 8 rejected roots')
 (B/'tools'/name).write_text(s,encoding='utf-8')
# Preserve the exact failed test source, verified against the original failed compile pin.
p=B/'checks/com/videokit/d1input/ContainerPendingOrderCheck.java';current=p.read_text()
new='for(Entry waiting:Entry.values()){rejected(()->enter(s,waiting,validator),"OUTPUT_ORIGINAL_PENDING");'
old='for(int n=0;n<2;n++){rejected(()->enter(s,n==0?Entry.HOST_STRUCTURE:Entry.LEGACY_VALIDATION,validator),"OUTPUT_ORIGINAL_PENDING");'
prototype=current.replace(new,old);pin=next(x['sha256'] for x in json.loads((B/'evidence/local-001/source-pins.json').read_text()) if x['path'].endswith('/ContainerPendingOrderCheck.java'));assert hashlib.sha256(prototype.encode()).hexdigest()==pin
(B/'evidence/ContainerPendingOrderCheck-before-loop-fix.java').write_text(prototype,encoding='utf-8')
shutil.copyfile(R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-case-results.json',B/'reference/container01-phase-b-case-results.json')
print('Reused strict-build/admission/artifact tools; locks/metadata unchanged;9 old seals5556 files will be rechecked;60-process entry and8 output gates prepared.')
