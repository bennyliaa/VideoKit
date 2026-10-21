from pathlib import Path
import json,hashlib,zipfile,datetime,re,shutil
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1render02-capture';E=B/'evidence';seal=E/'capture-adapt-freeze.json';assert not seal.exists(),'FROZEN'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
policy=json.loads((B/'release/capture-policy.json').read_text());assert policy['mode']=='PREPARATION_ONLY' and policy['entrySha256']==sha(B/'tools/capture_render02.ps1')
for p in json.loads((E/'source-provenance.json').read_text()):assert sha(R/p['source'])==p['sha256'] and sha(B/p['copy'])==p['sha256']
for p in json.loads((E/'selfcheck-005/tested-source-pins.json').read_text()):assert sha(B/p['path'])==p['sha256']
summary=json.loads((E/'selfcheck-005/summary.json').read_text());assert len(summary['cases'])==17 and summary['ownersNaturallyReturned']==21
owners=json.loads((E/'selfcheck-005/original-owner-audit.json').read_text());assert all(x['returned'] and x['pipeReadersJoined'] and x['processHandleCloseReturned'] and not x['unknown'] for x in owners)
assert json.loads((B/'release/activation-required.template.json').read_text())['approvedForExecution'] is False
for p in json.loads((E/'original-preservation.json').read_text())['productCandidates']:
 s=R/'docs/coder'/p['candidate']/'evidence'/('render01-freeze.json' if p['candidate']=='d1render01' else 'render02-freeze.json');assert sha(s)==p['sealSha256'];assert all(sha(R/x['path'])==x['sha256'] for x in json.loads(s.read_text())['files'])
reports=[R/'docs/coder/D1_RENDER02_CAPTURE_ADAPT_DELIVERY_V1.0.md',R/'docs/coder/D1_RENDER02_CAPTURE_ADAPT_ACTIVATION_PLAN_V1.0.md']
archive=R/'docs/coder/D1-20261020-RENDER02-CAPTURE-ADAPT-source.zip';assert not archive.exists()
links=[]
for p in reports:
 for x in re.findall(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',p.read_text()):
  q=Path(x);ok=q.is_file() or q in [archive,seal];links.append({'report':p.name,'target':x,'validOrCreatedByFreeze':ok});assert ok,x
matrix=json.loads((B/'completion-matrix.json').read_text());assert matrix['mode']=='PREPARATION_ONLY' and matrix['D1']=='NOT_PASSED' and matrix['M0']=='NOT_STARTED'
dump(E/'delivery-verification.json',{'result':'PASS_OFFLINE_BINDING_ONLY','entrySha256':sha(B/'tools/capture_render02.ps1'),'testedCases':17,'originalOuterOwnersReturned':21,'reportLinkChecks':links,'production':'NOT_RUN','productOrSDKActions':0,'frozenProductFilesPreserved':881,'independentAdmission':'PENDING_REVIEW','screenshots':'NOT_RUN_SAFE_LIVE_PARENT_NOT_EXPRESSIBLE'})
# The original work/evidence snapshots are finite local fixtures, included as historical facts.
files=sorted([p for p in B.rglob('*') if p.is_file() and p!=seal and '__pycache__' not in p.parts]+reports)
assert not any(p.suffix.lower() in ['.apk','.jks','.p12','.keystore'] for p in files)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(files)
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
value={'schemaVersion':1,'candidateId':'D1-20261020-RENDER02-CAPTURE-ADAPT','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_PREPARATION_ONLY_PENDING_INDEPENDENT_REVIEW','mode':'PREPARATION_ONLY','entrySha256':policy['entrySha256'],'sourcePlanSha256':'1db733cd14d51b47d41df3670a5d9d84b1f68f599aeb3d02b8d1d814236810d1','mappedRoles':28,'serialPreparedRoles':25,'screenshots':'3 NOT_RUN_LIVE_PARENT_ASSOCIATION_UNPROVEN','spare4AuthorizeNothing':True,'sdkChildCap':32,'textCap':4194304,'binaryArchiveCap':16777216,'sdkExecuted':0,'deviceExecuted':0,'oldHandlesQueried':0,'productChanges':0,'gradleNativeHostBuilds':0,'independentReview':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','newExecutionAuthorityCreated':False,'files':rows+[arch],'archiveMembers':len(files),'archive':arch}
dump(seal,value)
print(json.dumps({'candidate':value['candidateId'],'entrySha256':policy['entrySha256'],'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'mainReport':next(x for x in rows if x['path'].endswith('CAPTURE_ADAPT_DELIVERY_V1.0.md'))},ensure_ascii=False,indent=2))
