from pathlib import Path
import json,hashlib,zipfile,datetime,os,re
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=B/'evidence';seal=E/'input-sink05-freeze.json';assert not seal.exists(),'FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=json.loads((E/'final-source-dependency-inputs.json').read_text());assert all(sha(B/x['path'])==x['sha256'] for x in inputs)
assert all(sha(B/x['path'])==x['sha256'] for x in json.loads((E/'local-005/source-pins.json').read_text()))
receipt=json.loads((E/'build-main-001/receipt.json').read_text(encoding='utf-8-sig'));assert receipt['exitCode']==0 and receipt['strictLockMode'] and receipt['strictVerification'] and receipt['offline'] and receipt['verifyMetadata'] and not receipt['writeNewCandidateExactLocks']
audit=json.loads((E/'artifact-audit.json').read_text());assert all(sha(R/x['path'])==x['sha256'] for x in audit['artifacts'])
batch=json.loads((E/'batch-validation.json').read_text());assert batch['independent']=='PENDING' and batch['D1']=='NOT_PASSED' and batch['M0']=='NOT_STARTED' and len(batch['runs'])==50
for x in batch['runs']:
 p=B/x['path'];assert sha(p)==x['sha256'];r=json.loads(p.read_text());assert r['exitCode']==0 and r['originalProcessReturned']
 if x['mode']=='production':assert r['productionJarFirst'] and r['jarSha256']==sha(B/'artifacts/input-sink05-classes.jar')
assert len(json.loads((B/'phase-exception-matrix.json').read_text())['cases'])==63
assert len(json.loads((B/'tester23-regression-map.json').read_text())['cases'])==23
assert len(json.loads((B/'independent-regression-map.json').read_text())['cases'])==19
oldFiles=0
for old in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/old['sealPath'];assert sha(p)==old['sealSha256'];f=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in f['files']);oldFiles+=len(f['files'])
assert oldFiles==3683
reports=[R/'docs/coder'/n for n in ['D1_INPUT_SINK05_FIX_DELIVERY_V1.0.md','D1_INPUT_SINK05_RESPONSE_ORDER_MODEL_V1.0.md','D1_INPUT_SINK05_INDEPENDENT_CHECK_PLAN_V1.0.md']]
archive=R/'docs/coder/D1-20261021-INPUT-SINK05-source.zip';assert not archive.exists();links=[]
for p in reports:
 for target in re.findall(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',p.read_text()):
  q=Path(target);assert q.is_file() or q in [archive,seal],target;links.append({'source':p.name,'target':target,'existsOrCreatedByFreeze':True})
assert json.loads((B/'completion-matrix.json').read_text())['newIndependentResult']=='PENDING'
dump(E/'delivery-verification.json',{'result':'PASS_CODER_LIMITED_LOCAL_BINDING_ONLY','newIndependent':'PENDING','suiteCounts':{'coreGroups':20,'oldTailScenarios':17,'testerRegressionScenarios':23,'phaseExceptionMatrix':63,'inputRegressions':5},'notSummedOrClaimedAllUnique':True,'finalLocal':'005','finalSourceSuite':'004','finalProductionSuite':'005','finalBuild':'001','sourceDependencyInputFiles':len(inputs),'oldFrozenFilesUnchanged':3683,'linkChecks':links,'realMediaFormatAndDevice':'NOT_RUN','D1':'NOT_PASSED','M0':'NOT_STARTED'})
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
value={'schemaVersion':1,'candidate':'D1-20261021-INPUT-SINK05','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PENDING_INDEPENDENT_B06_B07_FIX_REVIEW','coderLimitedFix':'PASS','newIndependentReview':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','finalLocal':'005','finalSourceSuite':'004','finalProductionSuite':'005','coreGroups':20,'originalReturnScenarios':17,'testerRegressionScenarios':23,'phaseExceptionCases':63,'inputExceptionCases':5,'countsOverlapNotSummed':True,'finalBuild':'001','actualFramework':'real Android/Media3 1.9.3 ABI compile; production JAR first JVM checks','actualRuntimeCoordinates':15,'newCoordinatesOrVersionChanges':0,'dependencyAdmission':'INHERIT_OLD_PHASE_B_LIMITED_OFFLINE_ONLY','metadataVerification':True,'verificationMode':'strict','lockMode':'STRICT','newVerificationPins':0,'newBinaryDownloads':0,'deviceSdkFieldOperations':0,'oldHandleQueries':0,'occupancyQueries':0,'nativeOrExternalHostBuilds':0,'oldFrozenFilesUnchanged':3683,'runtimePlatformFDCodecMuxerAndMediaValidation':'NOT_RUN','hostBusinessCommit':'NOT_RUN_CONTROLLED_PORT_ONLY','finalM0PublicAPIFrozen':False,'files':rows+[arch],'archiveMembers':len(rows),'archive':arch,'excluded':'417MB mirror/Gradle caches/JDK/SDK/build/classes excluded; actual JVM deps, all verified metadata, source, original historical failures, final raw checks and production artifacts retained','noNewExecutionAuthorityCreated':True}

assert len(json.loads((B/'return-value-matrix.json').read_text())['hostResultCases'])==88
assert json.loads((B/'return-value-matrix.json').read_text())['transitionCaseCount']==33
toolGate=json.loads((E/'tool-output-gate/summary.json').read_text());assert toolGate['positiveActualJdkCompileAnd20Groups'] and len(toolGate['negativeCases'])==7 and toolGate['toolSha256']==sha(B/'tools/local_check.py')
runnerGate=json.loads((E/'review-runner-gate/summary.json').read_text());assert runnerGate['positiveOriginalReturnedRuns']==50 and runnerGate['negativePaths']==7 and runnerGate['runnerSha256']==sha(B/'tools/review_all.py')
value.update(hostReturnCases=88,transitionCases=33,oldQueryCases=2,extraAuthorityCases=3,extraPrivateCancellationCases=6,reviewOutputPositiveActual=True,reviewOutputNegativePathsPerEntry=7,documentedFullReviewRunnerActual=True,newHostProtocolFields=0)


order=json.loads((B/'response-order-matrix.json').read_text());assert order['caseCount']==30 and order['coordinatorCases']==7 and order['originalDefectRegressions']==2
assert json.loads((E/'prototype-check-history.json').read_text())['initialExitNotReturnProof']
value.update(responseOrderCases=30,coordinatorOrderCases=7,originalResponseRegressions=2,independentHostResultRegressionCases=8,allTerminalSourcesSharedIrreversibleGate=True,rawResponseFactAndAdoptionSeparated=True,exactOriginalResponseObserverAndThreadEligibility=True,counterZeroNotReturnProof=True,initialPrototypeCheckFailurePreserved=True,documentedRunnerTopLevelRuns=50)

dump(seal,value);assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'candidate':value['candidate'],'sealPath':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'mainReport':next(x for x in rows if x['path'].endswith('D1_INPUT_SINK05_FIX_DELIVERY_V1.0.md'))},ensure_ascii=False,indent=2))

