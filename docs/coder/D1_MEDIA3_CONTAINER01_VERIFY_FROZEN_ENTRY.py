from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-container01';D=R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-frozen-entry-001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/media3-container01-freeze.json';s=json.loads(seal.read_text());assert sha(seal)=='6d08e618dd1b98852830468a69b5048f65b55f4bc0a9117360c7bd414423c4ed'
summary=json.loads((D/'summary.json').read_text());assert summary['frozenCandidate'] and summary['sealSha256']==sha(seal) and len(summary['runs'])==56 and all(x['exitCode']==0 for x in summary['runs'])
assert summary['productionJarSha256']==sha(B/'artifacts/media3-container01-classes.jar') and summary['toolSha256']==sha(B/'tools/review_all.py')
assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in s['files'])
for row in json.loads((B/'evidence/frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];old=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in old['files'])
receipt={'candidate':s['candidate'],'verifiedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receiptScope':'CODER_FROZEN_ENTRY_SELF_CHECK_NOT_INDEPENDENT_PHASE_B','sealSha256':sha(seal),'frozenFilesStillUnchanged':len(s['files']),'olderFrozenFilesStillUnchanged':4511,'summaryPath':(D/'summary.json').relative_to(R).as_posix(),'summarySha256':sha(D/'summary.json'),'originalReturnedTopLevelProcesses':56,'productionJarFirst':True,'sourcePinsSha256':summary['sourcePinsSha256'],'productionJarSha256':summary['productionJarSha256'],'realMp4ParseMuxAndStructure':'NOT_RUN_PLATFORM_AND_FIXTURE_GAPS','deviceSdkFieldOperations':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
out=R/'docs/coder/D1_MEDIA3_CONTAINER01_FROZEN_ENTRY_RECEIPT_V1.0.json';assert not out.exists();out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receipt':str(out),'sha256':sha(out),'summarySha256':receipt['summarySha256']},indent=2))
