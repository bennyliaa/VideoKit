from pathlib import Path
import hashlib,json,datetime,zipfile
R=Path(__file__).resolve().parents[2];B=R/'docs/coder/d1media3-android01';E=B/'evidence';seal=E/'media3-android01-freeze.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(seal)=='fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a';s=json.loads(seal.read_text());assert len(s['files'])==740
assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in s['files'])
with zipfile.ZipFile(R/s['archive']['path']) as z:
 assert len(z.namelist())==739 and z.testzip() is None
 for x in s['files'][:-1]:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
oldCount=0
for row in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];v=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in v['files']);oldCount+=len(v['files'])
assert oldCount==6232
for row in json.loads((E/'prior-independent-evidence-preservation.json').read_text()):
 p=R/row['manifestPath'];assert sha(p)==row['manifestSha256'];v=json.loads(p.read_text());assert sha(R/v['report'])==v['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in v['evidenceFiles'])
p=R/'docs/tester/D1_MEDIA3_ANDROID01_REVIEW_EVIDENCE/coder-frozen-entry-001/summary.json';v=json.loads(p.read_text());assert v['frozenCandidate'] and v['sealSha256']==sha(seal) and len(v['runs'])==62 and v['allOriginalProcessesReturned'] and all(x['exitCode']==0 for x in v['runs'])
assert v['productionJarSha256']==sha(B/'artifacts/media3-android01-classes.jar') and v['deviceSdkFieldOperations']==0
receipt={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sealSha256':sha(seal),'frozenFilesUnchanged':740,'oldFrozenFilesUnchanged':6232,'priorIndependentManifestsUnchanged':5,'postfreezeReadOnlyEntry':p.relative_to(R).as_posix(),'postfreezeSummarySha256':sha(p),'postfreezeRuns':62,'allPostfreezeOriginalProcessesReturned':True,'earlierLocalDuplicateOriginal':'UNKNOWN_RETAINED_NOT_OVERRIDDEN','fixture':'BLOCKED','actualAndroidRuns':0,'toolBuildGenerationCalls':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
out=R/'docs/coder/D1_MEDIA3_ANDROID01_READY_POST_FREEZE_RECEIPT.json';assert not out.exists();out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receiptPath':out.relative_to(R).as_posix(),'receiptSha256':sha(out),**receipt},indent=2))
