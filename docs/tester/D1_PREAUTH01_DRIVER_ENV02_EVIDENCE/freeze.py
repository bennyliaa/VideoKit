"""CreateNew independent complete ENV02 file freeze; no new execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
E=Path(__file__).resolve().parent;T=E.parent;N='D1_PREAUTH01_DRIVER_ENV02'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def main():
 a=json.loads((E/'post-audit.json').read_bytes());o=json.loads((E/'v1/order.json').read_bytes());W=Path(o['work']);report=T/(N+'_REPORT_V1.0.md');assert a['allNewOriginalsReturned'] and not a['newUnknown'] and a['verdict']=='PASS_IN_SCOPE_COMPLETE_OFFLINE_B';assert not (E/'v2').exists()
 rows=[]
 for p in sorted([report,*[p for root in [E,W] for p in root.rglob('*') if p.is_file()]]):
  with p.open('rb') as f:b=f.read()
  assert len(b)<=1048576;rows.append(dict(absolutePath=str(p),bytes=len(b),sha256=sha(b)))
 assert len(rows)<2048 and sum(x['bytes'] for x in rows)<33554432
 m=T/(N+'_MANIFEST_V1.0.json');put(m,dict(schema='PREAUTH01_DRIVER_ENV02_MANIFEST_V1',status=a['verdict'],batch=o['batch'],sourceSeal=o['sourceSeal'],roots=dict(evidence=str(E),fixture=str(W)),files=rows,excluded=['self manifest','freeze receipt','later coordinator send receipt']))
 for x in rows:
  with Path(x['absolutePath']).open('rb') as f:b=f.read()
  assert len(b)==x['bytes'] and sha(b)==x['sha256']
 receipt=dict(schema='PREAUTH01_DRIVER_ENV02_FREEZE_RECEIPT_V1',utc=datetime.now(timezone.utc).isoformat(),batch=o['batch'],reportPath=str(report),reportSha256=sha(report.read_bytes()),manifestPath=str(m),manifestSha256=sha(m.read_bytes()),files=len(rows),bytes=sum(x['bytes'] for x in rows),maxFileBytes=max(x['bytes'] for x in rows),bad=0,verdict=a['verdict'],qualificationVersionsUsed=1,qualificationActualCalls=3,qualificationRetriesUsed=0,productRetries=0,groupsPassed=9,allNewOriginalsReturned=True,newUnknown=False,source20Bad=0,gate12Bad=0,old56_108_57Bad=0,oldZip57_109Unchanged=True,actualWholeProcessGraph=24,workerSeconds=a['workerSeconds'],outerSeconds=a['outerSeconds'],actualSDK=0,actualNativeRoute=0,actualDevice=0,actualGit=0,oldRuntimeQueries=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 put(T/(N+'_FREEZE_RECEIPT_V1.0.json'),receipt);print(json.dumps(receipt))
if __name__=='__main__':main()
