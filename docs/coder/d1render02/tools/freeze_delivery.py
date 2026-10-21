from pathlib import Path
import json,hashlib,shutil,zipfile,datetime,re
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1render02';E=B/'evidence';seal=E/'render02-freeze.json';assert not seal.exists(),'FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for x in json.loads((E/'build-inputs-final.json').read_text(encoding='utf-8')):assert sha(B/x['path'])==x['sha256'],x['path']
for folder in ['local-001','controlled-regression-001']:
 for x in json.loads((E/folder/'source-pins.json').read_text(encoding='utf-8')):assert sha(B/x['path'])==x['sha256'],x['path']
old=R/'docs/coder/d1render01/evidence/render01-freeze.json';legacy=json.loads(old.read_text(encoding='utf-8'));assert all(sha(R/x['path'])==x['sha256'] for x in legacy['files'])
assert sha(R/'docs/tester/D1_RENDER01_OFFLINE_REVIEW_REPORT_V1.0.md')=='c92a0b89b49180fac2db74524dbf7e043cfda6c7ea984074b9b90fe13ba3aed8'
requirements=[]
for name in ['docs/milestones/D1_RENDER02_FIX_CODER_REQUIREMENTS_V1.0.md','docs/milestones/D1_RENDER02_FIX_TESTER_REQUIREMENTS_V1.0.md','docs/tester/D1_RENDER01_OFFLINE_REVIEW_REPORT_V1.0.md','docs/tester/D1_RENDER01_OFFLINE_REVIEW_EVIDENCE/metadata-parent-bom-closure-audit.json','docs/tester/D1_RENDER01_OFFLINE_REVIEW_EVIDENCE/consolidated-findings.json']:
 p=R/name;dest=B/'reference'/p.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p,dest);requirements.append({'source':name,'path':dest.relative_to(B).as_posix(),'sha256':sha(p)})
dump(E/'requirement-pins.json',requirements)
sources=[p for folder in ['src','android','upstream','app/src'] for p in (B/folder).rglob('*.java')]
dump(E/'production-source-index.json',[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in sorted(sources)])
reports=[R/'docs/coder'/n for n in ['D1_RENDER02_FIX_DELIVERY_V1.0.md','D1_RENDER02_FIX_TECHNICAL_DECISIONS_V1.0.md','D1_RENDER02_FIX_DEVICE_PLAN_V1.0.md']]
archive=R/'docs/coder/D1-20261020-RENDER02-source.zip';assert not archive.exists()
links=[]
for p in reports:
 for target in re.findall(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',p.read_text(encoding='utf-8')):
  q=Path(target);ok=q.is_file() or q in [seal,archive];links.append({'report':p.name,'target':target,'validOrCreatedByFreeze':ok});assert ok,target
audit=json.loads((E/'apk-audit/artifact-audit.json').read_text(encoding='utf-8'));assert all(sha(R/x['path'])==x['sha256'] for x in audit['artifacts'])
matrix=json.loads((B/'completion-matrix.json').read_text(encoding='utf-8'));assert matrix['D1']=='NOT_PASSED' and matrix['M0']=='NOT_STARTED';assert all(x['status'] in ['PASS','FAIL','NOT_RUN','BLOCKED'] for x in matrix['rows'])
dump(E/'delivery-verification.json',{'result':'PASS_SOURCE_TEST_BUILD_REPORT_BINDING_ONLY','legacyFrozenFilesUnchanged':len(legacy['files']),'legacySealSha256':sha(old),'reportLinks':links,'productionJavaFiles':len(sources),'deviceOperations':0,'sdkFieldCommands':0,'nativeFixtureHostRebuilds':0,'runtime':'NOT_RUN','independentNewMetadataAdmission':'PENDING_TESTER_REVIEW','D1':'NOT_PASSED','M0':'NOT_STARTED'})
exclude={'offline-maven','.gradle','.kotlin','build','fresh-gradle-home','classes','verifier-classes','__pycache__'}
files=sorted([p for p in B.rglob('*') if p.is_file() and not any(x in exclude for x in p.relative_to(B).parts) and p!=seal]+reports)
assert not any(p.suffix.lower() in ['.jks','.keystore','.p12'] for p in files)
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(files)
 for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files+[archive]]
value={'schemaVersion':1,'candidateId':'D1-20261020-RENDER02','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PENDING_TESTER_CONCENTRATED_REVIEW','D1':'NOT_PASSED','M0':'NOT_STARTED','runtimeExecution':'NOT_RUN','metadataVerification':True,'verificationMode':'strict','newMetadataAdmission':'PENDING_TESTER_REVIEW_NOT_HISTORICAL_APPROVAL','actualArtifacts':327,'actualMetadata':192,'finalBuildAttempt':'005','fullFreshBuildAttempt':'003','render01AllFrozenFilesPreserved':477,'nativeFixtureHostRebuilds':0,'runtimeLockedComponents':35,'newBinaryDownloads':0,'noExecutionAuthorityCreated':True,'files':rows,'archiveMembers':len(files),'archive':rows[-1],'excluded':'offline-maven, Gradle caches/build outputs/tool runtimes/private keys; complete input pin manifest and consumed metadata retained'}
dump(seal,value)
print(json.dumps({'candidate':value['candidateId'],'sealSha256':sha(seal),'archive':value['archive'],'frozenFiles':len(rows),'mainReport':next(x for x in rows if x['path'].endswith('D1_RENDER02_FIX_DELIVERY_V1.0.md'))},ensure_ascii=False,indent=2))
