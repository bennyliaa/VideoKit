from pathlib import Path
import json,hashlib,zipfile,datetime,os,re
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink02';E=B/'evidence';seal=E/'input-sink02-freeze.json';assert not seal.exists(),'FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=json.loads((E/'final-source-dependency-inputs.json').read_text());assert all(sha(B/x['path'])==x['sha256'] for x in inputs)
tests=json.loads((E/'local-003/source-pins.json').read_text());assert all(sha(B/x['path'])==x['sha256'] for x in tests)
assert 'groups=20' in (E/'local-003/checks.stdout').read_text()
receipt=json.loads((E/'build-main-001/receipt.json').read_text(encoding='utf-8-sig'));assert receipt['exitCode']==0 and receipt['strictLockMode'] and receipt['strictVerification'] and receipt['offline'] and receipt['verifyMetadata'] and not receipt['writeNewCandidateExactLocks']
audit=json.loads((E/'artifact-audit.json').read_text());assert all(sha(R/x['path'])==x['sha256'] for x in audit['artifacts'])
for name in ['return-003','production-core-001']:
 p=E/name;r=json.loads((p/'run.json').read_text());assert r['exitCode']==0 and r['originalProcessReturned'] and r['productionJarFirst'] and r['jarSha256']==sha(B/'artifacts/input-sink02-classes.jar')
assert 'originalReturnScenarios=17 originalThreadsJoined=true retainedSources=0 retainedOutputs=0' in (E/'return-003/run.stdout').read_text()
assert 'groups=20' in (E/'production-core-001/run.stdout').read_text()
oldFiles=0
for old in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/old['sealPath'];assert sha(p)==old['sealSha256'];f=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in f['files']);oldFiles+=len(f['files'])
assert oldFiles==2033
batch=json.loads((E/'batch-validation.json').read_text());assert batch['independent']=='PENDING' and batch['D1']=='NOT_PASSED' and batch['M0']=='NOT_STARTED'
reports=[R/'docs/coder'/name for name in ['D1_INPUT_SINK02_FIX_DELIVERY_V1.0.md','D1_INPUT_SINK02_STATE_MODEL_V1.0.md','D1_INPUT_SINK02_INDEPENDENT_CHECK_PLAN_V1.0.md']]
archive=R/'docs/coder/D1-20261021-INPUT-SINK02-source.zip';assert not archive.exists();links=[]
for p in reports:
 for target in re.findall(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',p.read_text()):
  q=Path(target);assert q.is_file() or q in [archive,seal],target;links.append({'source':p.name,'target':target,'existsOrCreatedByFreeze':True})
assert len(json.loads((B/'independent-regression-map.json').read_text())['cases'])==19
assert json.loads((B/'completion-matrix.json').read_text())['newIndependentResult']=='PENDING'
dump(E/'delivery-verification.json',{'result':'PASS_CODER_LIMITED_LOCAL_BINDING_ONLY','independent':'PENDING','localSemanticGroups':20,'originalReturnScenarios':17,'testerOriginalFiveBaselinePreserved':True,'finalLocal':'003','finalReturn':'003_PRODUCTION_JAR_FIRST','finalBuild':'001','sourceDependencyInputFiles':len(inputs),'oldFrozenFilesUnchanged':2033,'linkChecks':links,'realMediaFormatAndDevice':'NOT_RUN','dependencyNewUseAdmission':'INHERIT_OLD_PHASE_B_LIMITED_OFFLINE_ONLY','D1':'NOT_PASSED','M0':'NOT_STARTED'})
excludes={'offline-maven','build-tools-gradle-home','.gradle','.kotlin','build','classes','__pycache__'};files=[]
for directory,dirs,names in os.walk(B):
 dirs[:]=[d for d in dirs if d not in excludes]
 for n in names:
  p=Path(directory)/n
  if p!=seal:files.append(p)
files=sorted(files+reports);assert not any(p.suffix.lower() in ['.jks','.keystore','.p12'] for p in files)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(files)
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
value={'schemaVersion':1,'candidate':'D1-20261021-INPUT-SINK02','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PENDING_INDEPENDENT_FIX_REVIEW','coderLimitedB01B02Fix':'PASS','newIndependentReview':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','finalLocal':'003','localSemanticGroups':20,'finalProductionReturn':'003','originalReturnScenarios':17,'finalProductionCore':'001','finalBuild':'001','actualFramework':'Media3 1.9.3 and Android real compile; actual production JAR first JVM replay','actualRuntimeCoordinates':15,'newCoordinatesOrVersionChanges':0,'dependencyNewUseAdmission':'INHERIT_INPUT_SINK01_PHASE_B_LIMITED_OFFLINE_ONLY','metadataVerification':True,'verificationMode':'strict','lockMode':'STRICT','newVerificationPins':0,'newBinaryDownloads':0,'deviceSdkFieldOperations':0,'oldHandleQueries':0,'occupancyQueries':0,'nativeOrExternalHostBuilds':0,'oldFrozenFilesUnchanged':2033,'runtimePlatformFDCodecMuxerAndMediaValidation':'NOT_RUN','hostBusinessCommit':'NOT_RUN_CONTROLLED_PORT_ONLY','finalM0PublicAPIFrozen':False,'files':rows+[arch],'archiveMembers':len(rows),'archive':arch,'excluded':'417MB offline mirror/Gradle caches/JDK/SDK/build outputs; real JVM deps, all actually verified metadata, production artifacts, original failure and final passing evidence retained','noNewExecutionAuthorityCreated':True}
dump(seal,value)
assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'candidate':value['candidate'],'sealPath':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'mainReport':next(x for x in rows if x['path'].endswith('D1_INPUT_SINK02_FIX_DELIVERY_V1.0.md'))},ensure_ascii=False,indent=2))
