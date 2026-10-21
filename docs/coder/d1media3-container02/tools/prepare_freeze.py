from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';assert not (E/'media3-container02-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=[]
for name,file in [('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json')]:
 p=R/'docs/tester'/name/file;m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'];assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);prior.append({'manifestPath':p.relative_to(R).as_posix(),'manifestSha256':sha(p),'filesUnchanged':len(m['evidenceFiles']),'reportSha256':m['reportSha256']})
(E/'older-independent-evidence-preservation.json').write_text(json.dumps(prior,indent=2),encoding='utf-8')
s=(R/'docs/coder/d1media3-container01/tools/freeze_batch.py').read_text().replace('media3-container01','media3-container02').replace('D1-20261021-MEDIA3-CONTAINER01','D1-20261021-MEDIA3-CONTAINER02-FIX').replace('D1_MEDIA3_CONTAINER01_DELIVERY','D1_MEDIA3_CONTAINER02_FIX_DELIVERY').replace('D1_MEDIA3_CONTAINER01_INTERFACE_DECISIONS','D1_MEDIA3_CONTAINER02_FIX_ADMISSION_ORDER').replace('local-007','local-002').replace("=='004'","=='001'").replace("=='007'","=='002'").replace("'finalLocal':'007'","'finalLocal':'002'").replace("'finalBuild':'004'","'finalBuild':'001'").replace('==56','==60').replace("'topLevelReviewProcesses':56","'topLevelReviewProcesses':60").replace('==4511','==5556').replace("'oldFrozenFilesUnchanged':4511","'oldFrozenFilesUnchanged':5556")
s=s.replace('FROZEN_LIMITED_READING_PROGRESS_WITH_PLATFORM_AND_FIXTURE_GAPS_PENDING_COORDINATOR_REVIEW','FROZEN_PENDING_INDEPENDENT_MC_B01_FIX_REVIEW_FUNCTIONAL_SCOPE_OPEN')
s=s.replace("'newUseIndependentAdmission':'PENDING'","'newUseIndependentAdmission':'INHERIT_CONTAINER01_PHASE_B_LIMITED_OFFLINE_ADMISSION'").replace("'actualNewReadingBoundaryGroups':7","'inheritedReadingBoundaryGroups':7,'exactTesterInputReplayCases':8,'keyInspectionOrderCases':22").replace("'newOfficialPomPins':2","'newOfficialPomPins':0").replace("'newUseCoordinates':['androidx.media3:media3-extractor:1.9.3','androidx.media3:media3-decoder:1.9.3']","'newUseCoordinates':[]")
s=s.replace("assert oldCount==5556","""assert oldCount==5556
for row in json.loads((E/'older-independent-evidence-preservation.json').read_text()):
 p=R/row['manifestPath'];assert sha(p)==row['manifestSha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles'])
prior=json.loads((E/'prior-independent-review-preservation.json').read_text());p=R/prior['manifestPath'];assert sha(p)==prior['manifestSha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==prior['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles'])
for name in ['app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']:
 assert (B/name).read_bytes()==(R/'docs/coder/d1media3-container01'/name).read_bytes()
assert len(json.loads((B/'inspection-order-matrix.json').read_text())['cases'])==22
assert json.loads((E/'local-001/compile.json').read_text())['exitCode']==1
assert json.loads((E/'local-002/compile.json').read_text())['exitCode']==0
""")
(B/'tools/freeze_batch.py').write_text(s,encoding='utf-8')
print('Freeze script derived from prior sealed workflow; old01/05/phaseA independent evidence rechecked without modification.')
