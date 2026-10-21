from pathlib import Path
import json,hashlib,zipfile,datetime,os,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';seal=E/'media3-container02-freeze.json';assert not seal.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=json.loads((E/'batch-validation.json').read_text());assert len(batch['runs'])==60 and batch['finalBuild']=='001' and batch['finalLocal']=='002'
for x in batch['runs']:
 p=B/x['path'];assert sha(p)==x['sha256'];v=json.loads(p.read_text());assert v['exitCode']==0 and v['originalProcessReturned']
 if x['mode']=='production':assert v['productionJarFirst'] and v['jarSha256']==sha(B/'artifacts/media3-container02-classes.jar')
for row in json.loads((E/'final-source-dependency-inputs.json').read_text()):assert sha(B/row['path'])==row['sha256']
for row in json.loads((E/'local-002/source-pins.json').read_text()):assert sha(B/row['path'])==row['sha256']
oldCount=0
for x in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sealSha256'];old=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in old['files']);oldCount+=len(old['files'])
assert oldCount==5556
for row in json.loads((E/'older-independent-evidence-preservation.json').read_text()):
 p=R/row['manifestPath'];assert sha(p)==row['manifestSha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles'])
prior=json.loads((E/'prior-independent-review-preservation.json').read_text());p=R/prior['manifestPath'];assert sha(p)==prior['manifestSha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==prior['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles'])
for name in ['app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']:
 assert (B/name).read_bytes()==(R/'docs/coder/d1media3-container01'/name).read_bytes()
assert len(json.loads((B/'inspection-order-matrix.json').read_text())['cases'])==22
assert json.loads((E/'local-001/compile.json').read_text())['exitCode']==1
assert json.loads((E/'local-002/compile.json').read_text())['exitCode']==0

reports=[R/'docs/coder'/n for n in ['D1_MEDIA3_CONTAINER02_FIX_DELIVERY_V1.0.md','D1_MEDIA3_CONTAINER02_FIX_ADMISSION_ORDER_V1.0.md']];archive=R/'docs/coder/D1-20261021-MEDIA3-CONTAINER02-FIX-source.zip';assert not archive.exists()
for p in reports:
 for target in re.findall(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',p.read_text()):assert Path(target).is_file() or Path(target) in [archive,seal],target
assert len(json.loads((B/'completion-matrix.json').read_text(encoding='utf-8'))['cases'])==32
excludes={'offline-maven','build-tools-gradle-home','.gradle','.kotlin','build','classes','__pycache__'};files=[]
for directory,dirs,names in os.walk(B):
 dirs[:]=[d for d in dirs if d not in excludes]
 for n in names:
  p=Path(directory)/n
  if p!=seal:files.append(p)
files=sorted(files+reports);assert not any(p.suffix.lower() in ['.jks','.keystore','.p12','.mp4'] for p in files)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(rows)
 for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
value={'schemaVersion':1,'candidate':'D1-20261021-MEDIA3-CONTAINER02-FIX','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PENDING_INDEPENDENT_MC_B01_FIX_REVIEW_FUNCTIONAL_SCOPE_OPEN','newIndependentReview':'PENDING','newUseIndependentAdmission':'INHERIT_CONTAINER01_PHASE_B_LIMITED_OFFLINE_ADMISSION','D1':'NOT_PASSED','M0':'NOT_STARTED','finalLocal':'002','finalBuild':'001','topLevelReviewProcesses':60,'inheritedReadingBoundaryGroups':7,'exactTesterInputReplayCases':8,'keyInspectionOrderCases':22,'actualApprovedSampleRawReadModes':2,'platformProbesNotFunctionalPASS':True,'actualRuntimeCoordinates':17,'newUseCoordinates':[],'newOfficialPomPins':0,'newBinaryOrModulePins':0,'newBinaryDownloads':0,'allOldPinsRetained':True,'strictVerification':True,'verifyMetadata':True,'strictLocks':True,'oldFrozenFilesUnchanged':5556,'realContainerParseMuxRemuxStructure':'NOT_RUN','actualAndroidFDCodecFsyncIsolatedContentBusinessCommitPlayback':'NOT_RUN','deviceSdkFieldOperations':0,'occupancyOrOldHandleQueries':0,'newAndroidPlatformPorts':0,'fakeMedia3Classes':0,'newEncodedFixture':False,'noNewExecutionAuthority':True,'finalM0PublicApi':False,'archiveMembers':len(rows),'files':rows+[arch],'archive':arch,'excluded':'Mirrors/Gradle caches/JDK/SDK/build/classes/original sample.mp4; exact JVM deps, official metadata, source, production artifacts and raw receipts included'}
dump(seal,value);assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'seal':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'reports':[x for x in rows if x['path'] in [p.relative_to(R).as_posix() for p in reports]]},ensure_ascii=False,indent=2))
