from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-container02';D=R/'docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/coder-frozen-entry-001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/media3-container02-freeze.json';s=json.loads(seal.read_text());assert sha(seal)=='0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d'
summary=json.loads((D/'summary.json').read_text());assert summary['frozenCandidate'] and summary['sealSha256']==sha(seal) and len(summary['runs'])==60 and all(x['exitCode']==0 for x in summary['runs']);assert summary['productionJarSha256']==sha(B/'artifacts/media3-container02-classes.jar') and summary['toolSha256']==sha(B/'tools/review_all.py')
assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in s['files'])
for row in json.loads((B/'evidence/frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];old=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in old['files'])
oldEvidence=[]
for folder,file in [('D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json')]:
 p=R/'docs/tester'/folder/file;m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);oldEvidence.append({'manifest':p.relative_to(R).as_posix(),'manifestSha256':sha(p),'filesUnchanged':len(m['evidenceFiles']),'reportSha256':m['reportSha256']})
receipt={'candidate':s['candidate'],'verifiedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'CODER_FROZEN_ENTRY_SELF_CHECK_NOT_NEW_INDEPENDENT_REVIEW','sealSha256':sha(seal),'frozenFilesUnchanged':len(s['files']),'priorCandidateFilesUnchanged':5556,'oldIndependentEvidence':oldEvidence,'summaryPath':(D/'summary.json').relative_to(R).as_posix(),'summarySha256':sha(D/'summary.json'),'originalReturnedTopLevelProcesses':60,'sourcePinsSha256':summary['sourcePinsSha256'],'productionJarSha256':summary['productionJarSha256'],'MC_B01':'CODER_FIX_CHECKED_PENDING_INDEPENDENT','actualContainerGoal':'OPEN_NOT_RUN','deviceSdkFieldOperations':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
out=R/'docs/coder/D1_MEDIA3_CONTAINER02_FIX_FROZEN_ENTRY_RECEIPT_V1.0.json';assert not out.exists();out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receipt':str(out),'sha256':sha(out),'summarySha256':receipt['summarySha256']},indent=2))
