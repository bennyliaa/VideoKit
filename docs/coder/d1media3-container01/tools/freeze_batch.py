from pathlib import Path
import json,hashlib,zipfile,datetime,os,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';seal=E/'media3-container01-freeze.json';assert not seal.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
batch=json.loads((E/'batch-validation.json').read_text());assert len(batch['runs'])==56 and batch['finalBuild']=='004' and batch['finalLocal']=='007'
for x in batch['runs']:
 p=B/x['path'];assert sha(p)==x['sha256'];v=json.loads(p.read_text());assert v['exitCode']==0 and v['originalProcessReturned']
 if x['mode']=='production':assert v['productionJarFirst'] and v['jarSha256']==sha(B/'artifacts/media3-container01-classes.jar')
for row in json.loads((E/'final-source-dependency-inputs.json').read_text()):assert sha(B/row['path'])==row['sha256']
for row in json.loads((E/'local-007/source-pins.json').read_text()):assert sha(B/row['path'])==row['sha256']
oldCount=0
for x in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sealSha256'];old=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in old['files']);oldCount+=len(old['files'])
assert oldCount==4511
reports=[R/'docs/coder'/n for n in ['D1_MEDIA3_CONTAINER01_DELIVERY_V1.0.md','D1_MEDIA3_CONTAINER01_INTERFACE_DECISIONS_V1.0.md']];archive=R/'docs/coder/D1-20261021-MEDIA3-CONTAINER01-source.zip';assert not archive.exists()
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
value={'schemaVersion':1,'candidate':'D1-20261021-MEDIA3-CONTAINER01','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_LIMITED_READING_PROGRESS_WITH_PLATFORM_AND_FIXTURE_GAPS_PENDING_COORDINATOR_REVIEW','newIndependentReview':'PENDING','newUseIndependentAdmission':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','finalLocal':'007','finalBuild':'004','topLevelReviewProcesses':56,'actualNewReadingBoundaryGroups':7,'actualApprovedSampleRawReadModes':2,'platformProbesNotFunctionalPASS':True,'actualRuntimeCoordinates':17,'newUseCoordinates':['androidx.media3:media3-extractor:1.9.3','androidx.media3:media3-decoder:1.9.3'],'newOfficialPomPins':2,'newBinaryOrModulePins':0,'newBinaryDownloads':0,'allOldPinsRetained':True,'strictVerification':True,'verifyMetadata':True,'strictLocks':True,'oldFrozenFilesUnchanged':4511,'realContainerParseMuxRemuxStructure':'NOT_RUN','actualAndroidFDCodecFsyncIsolatedContentBusinessCommitPlayback':'NOT_RUN','deviceSdkFieldOperations':0,'occupancyOrOldHandleQueries':0,'newAndroidPlatformPorts':0,'fakeMedia3Classes':0,'newEncodedFixture':False,'noNewExecutionAuthority':True,'finalM0PublicApi':False,'archiveMembers':len(rows),'files':rows+[arch],'archive':arch,'excluded':'Mirrors/Gradle caches/JDK/SDK/build/classes/original sample.mp4; exact JVM deps, official metadata, source, production artifacts and raw receipts included'}
dump(seal,value);assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'seal':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'reports':[x for x in rows if x['path'] in [p.relative_to(R).as_posix() for p in reports]]},ensure_ascii=False,indent=2))
