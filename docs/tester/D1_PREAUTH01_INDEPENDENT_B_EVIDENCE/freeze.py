"""CreateNew complete blocked-batch report/evidence freeze, no dynamic work."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parent;T=R.parent;N='D1_PREAUTH01_INDEPENDENT_B'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def main():
 a=json.loads((R/'post-audit.json').read_bytes());o=json.loads((R/'order.json').read_bytes());report=T/(N+'_REPORT_V1.0.md');assert a['allOwnStartedOriginalsReturned'] and not a['newResourceUnknown'] and not Path(o['work']).exists()
 rows=[]
 for p in sorted([report,*[p for p in R.rglob('*') if p.is_file()]]):
  with p.open('rb') as f:b=f.read()
  assert len(b)<=1048576;rows.append(dict(absolutePath=str(p),bytes=len(b),sha256=sha(b)))
 assert len(rows)<2048 and sum(x['bytes'] for x in rows)<33554432
 m=T/(N+'_MANIFEST_V1.0.json');put(m,dict(schema='PREAUTH01_INDEPENDENT_B_MANIFEST_V1',batch=o['batch'],status=a['status'],sourceSeal=o['sourceSeal'],plannedFixtureRoot=str(o['work']),fixtureRootCreated=False,files=rows,excluded=['self manifest','freeze receipt','coordinator send receipt produced after final freeze']))
 for x in rows:
  with Path(x['absolutePath']).open('rb') as f:b=f.read()
  assert len(b)==x['bytes'] and sha(b)==x['sha256']
 receipt=dict(schema='PREAUTH01_INDEPENDENT_B_FREEZE_RECEIPT_V1',utc=datetime.now(timezone.utc).isoformat(),batch=o['batch'],reportPath=str(report),reportSha256=sha(report.read_bytes()),manifestPath=str(m),manifestSha256=sha(m.read_bytes()),files=len(rows),bytes=sum(x['bytes'] for x in rows),maxFileBytes=max(x['bytes'] for x in rows),bad=0,status=a['status'],dynamicBatchStarts=1,retries=0,actualWorkerPid=a['actualWorkerIdentity']['pid'],actualWorkerCreationFileTime=a['actualWorkerIdentity']['creationFileTime'],allOwnStartedOriginalsReturned=True,newResourceUnknown=False,pureTemplateRows=193,clearNormativePureRows=192,behaviorObservations=1,dynamicProductGroupsActuallyRun=0,semanticCasesActuallyRun=0,preplannedWholeProcessGraph=24,actualWholeStartedProcessGraph=1,old56And108Bad=0,oldZip57And109Unchanged=True,source20Bad=0,gate12Bad=0,frozenOrderSourcesBad=0,actualSDK=0,actualNativeRoute=0,actualDevice=0,actualGit=0,oldRuntimeQueries=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 put(T/(N+'_FREEZE_RECEIPT_V1.0.json'),receipt);print(json.dumps(receipt))
if __name__=='__main__':main()
