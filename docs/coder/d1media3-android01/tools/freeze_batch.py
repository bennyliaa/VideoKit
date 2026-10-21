from pathlib import Path
import json,hashlib,zipfile,datetime,os
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';seal=E/'media3-android01-freeze.json';assert not seal.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
batch=json.loads((E/'batch-validation.json').read_text());assert len(batch['runs'])==62 and batch['finalBuild']=='004'
for x in batch['runs']:
 p=B/x['path'];assert sha(p)==x['sha256'];r=json.loads(p.read_text());assert r['exitCode']==0 and r['originalProcessReturned']
for name in ['final-source-dependency-inputs.json','local-002/source-pins.json']:
 for row in json.loads((E/name).read_text()):assert sha(B/row['path'])==row['sha256']
oldCount=0
for row in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];old=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in old['files']);oldCount+=len(old['files'])
assert oldCount==6232
for row in json.loads((E/'prior-independent-evidence-preservation.json').read_text()):
 p=R/row['manifestPath'];assert sha(p)==row['manifestSha256'];v=json.loads(p.read_text());assert sha(R/v['report'])==v['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in v['evidenceFiles'])
audit=json.loads((E/'artifact-audit.json').read_text())
for row in audit['apks']+audit['jarArtifacts']:assert sha(B/row['path'])==row['sha256']
plan=json.loads((E/'execution-plan.json').read_text());assert len(plan['methods'])==6 and len(plan['proposedOperations'])==14 and plan['currentDeviceOrSdkFieldOperations']==0
for row in plan['apks']:assert sha(B/row['path'])==row['sha256']
assert len(json.loads((E/'completion-matrix.json').read_text())['rows'])==24
assert json.loads((E/'earlier-suite-pending.json').read_text())['processReturnProven']==False
assert json.loads((E/'generation-proposal.json').read_text())['currentBuildLoadEncodeDecodeCalls']==0
main=R/'docs/coder/D1_MEDIA3_ANDROID01_READY_DELIVERY_V1.0.md';archive=R/'docs/coder/D1-20261021-MEDIA3-ANDROID01-READY-source.zip';assert not archive.exists()
exclude={'offline-maven','build-tools-gradle-home','.gradle','.kotlin','build','classes','__pycache__'};files=[]
for folder,dirs,names in os.walk(B):
 dirs[:]=[d for d in dirs if d not in exclude and not (Path(folder)==E and d=='suites-001')]
 for name in names:
  p=Path(folder)/name
  if p!=seal:files.append(p)
files=sorted(files+[main]);assert not any(p.suffix.lower() in ['.jks','.keystore','.p12'] for p in files)
media=[p for p in files if p.suffix.lower() in ['.mp4','.mkv','.wav','.mp3','.m2ts','.ts','.mov','.webm','.avi']];assert media==[B/'instrumentation-assets/sample.mp4']
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(rows)
 for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
value={'schemaVersion':1,'candidate':'D1-20261021-MEDIA3-ANDROID01-READY','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_OFFLINE_CANDIDATE_PENDING_INDEPENDENT_B_REVIEW_WITH_FIXTURE_AND_EARLIER_LOCAL_ORIGINAL_RETURN_GAPS','newIndependentReview':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','finalBuild':'004','finalLocal':'002','documentedReviewProcessesReturned':62,'hostReadinessGroups':6,'actualAndroidDeviceRuns':0,'deviceSdkFieldOperations':0,'actualMuxOutputWrites':0,'fixture':'BLOCKED','generation':'PROPOSAL_ONLY_TOOL_UNBUILT_NOT_AUTHORIZED','localEarlierDuplicateSuite':'UNKNOWN_ORIGINAL_PROCESS_NOT_RETURNED_RETAINED_NOT_REPLACED_BY_OTHER_GREEN_RUN','pendingRunExcluded':'evidence/suites-001; immutable snapshot of29 actually returned receipts separately included','oldFrozenFilesUnchanged':6232,'strict':True,'metadataVerification':True,'strictLocks':True,'appCompileExternal':12,'appRuntimeExternal':17,'testCompileExternal':12,'testRuntimeExternal':0,'newRuntimeCoordinates':[],'newTestRuntimeCoordinates':[],'newBinaryDownloads':0,'newEncoderBuildLoadGenerationCalls':0,'newPlatformStandins':0,'sameUidIsRceIsolation':False,'productReadyCommitPlaybackOrIsolatedValidation':False,'noNewExecutionAuthority':True,'archiveMembers':len(rows),'archive':arch,'files':rows+[arch],'excluded':'Mirrors/cache/build/classes/keys/original test_media directory and active earlier suites-001; approved exact sample private build asset deliberately included with derivative CC BY3.0 notice'}
seal.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'seal':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'mainReportSha256':sha(main)},indent=2))
