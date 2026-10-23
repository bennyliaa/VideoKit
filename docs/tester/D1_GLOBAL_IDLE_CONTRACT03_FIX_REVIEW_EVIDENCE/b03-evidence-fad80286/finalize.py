from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parent;T=R.parents[1];REPORT=T/'D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_REPORT_V1.0.md'
MAN=T/'D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_MANIFEST_V1.0.json';RECEIPT=T/'D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_FREEZE_RECEIPT_V1.0.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def rd(p):
 with Path(p).open('rb') as f:b=f.read(1048577)
 assert len(b)<=1048576;return b
def load(p):return json.loads(rd(p))
def save(p,d):
 b=(json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode();assert len(b)<=1048576
 with p.open('xb') as f:assert f.write(b)==len(b);f.flush()
def main():
 assert not MAN.exists() and not RECEIPT.exists();o=load(R/'order.json');W=Path(o['work']);s=load(R/'worker-final.json');post=load(R/'post-audit.json')
 assert s['allOwnOriginalsReturned'] and not s['newUnknown'] and all(x==0 for x in s['custody'].values())
 proofs=[]
 for p in sorted(W.rglob('*-completion-proof.json')):
  d=load(p);proofs.append(dict(path=str(p),id=d.get('id'),nextId=d.get('nextId'),batchAmountUnknown=d.get('batchAmountUnknown'),approvedForNext=d.get('approvedForNext'),batchGroups=d.get('batchGroups')))
 save(R/'ledger-summary.json',dict(schema='CONTRACT03_B_KNOWN_LOGICAL_AND_ARTIFACT_LEDGER_V1',runnerKnownSourceBytes=s['runnerSourceBytesKnown'],runnerKnownSourceReads=s['runnerSourceReadsKnown'],driverKnownSourceBytes=s['ownReadBytes'],driverKnownSourceReads=s['ownReadCalls'],postReadBytes=post['postReadBytes'],proofs=proofs,allOriginalAmountUnknownFieldsPreserved=True,physicalIO='UNPROVEN',wholeChildSourceReadTotal='NOT_GLOBALLY_MEASURED',partialRejectedConstructorsNotInvented=True,resourceUnknown=False,actualSDK=0,oldRuntimeQueries=0,secondCloseACKRefund=False))
 rows=[]
 for label,base in [('evidence',R),('new-fixtures',W)]:
  for p in sorted(base.rglob('*')):
   if not p.is_file():continue
   assert not p.stat().st_file_attributes&1024;b=rd(p);rows.append(dict(root=label,path=p.relative_to(base).as_posix(),absolutePath=str(p),bytes=len(b),sha256=sha(b)))
 report=rd(REPORT);rows.append(dict(root='report',path=REPORT.name,absolutePath=str(REPORT),bytes=len(report),sha256=sha(report)))
 assert len(rows)<=4096 and sum(x['bytes'] for x in rows)<=134217728
 save(MAN,dict(schema='CONTRACT03_INDEPENDENT_B_MANIFEST_V1',batch=o['batch'],roots={'evidence':str(R),'new-fixtures':str(W),'report':str(T)},sourceSeal=o['sourceSeal'],files=rows,excluded=['self manifest','freeze receipt','coordinator send receipt after frozen complete report']))
 bad=[]
 for x in rows:
  b=rd(x['absolutePath'])
  if len(b)!=x['bytes'] or sha(b)!=x['sha256']:bad.append(x['absolutePath'])
 assert not bad
 rec=dict(schema='CONTRACT03_INDEPENDENT_B_FREEZE_RECEIPT_V1',batch=o['batch'],reportPath=str(REPORT),reportSHA256=sha(report),manifestPath=str(MAN),manifestSHA256=sha(rd(MAN)),files=len(rows),bytes=sum(x['bytes'] for x in rows),bad=bad,verdict='FAIL_TARGET_COVERAGE_GAPS_NO_NEW_CONFIRMED_PRODUCT_SOURCE_DEFECT',groups=11,passGroups=10,failedGroups=1,exactFaultTargets=9,uncovered=['WRONG_OUTPUT_SOURCE','EXPIRE_DURING_MATERIALIZE'],accurateSourceGuard='PASS_OWNER_SOURCE_PIN_ENTRY',semanticAReused='ACCEPTED_400_SOURCE_UNCHANGED',allNewOriginalsReturned=True,newUnknown=False,originalCandidate98Bad=0,originalDev484Bad=0,originalA408Bad=0,originalProductZIP99Bad=0,originalDevZIP485Bad=0,realSDK=0,realNativeRoute=0,oldQueries=0,automaticNextTest=False,utc=datetime.now(timezone.utc).isoformat())
 save(RECEIPT,rec);print(json.dumps(rec))
if __name__=='__main__':main()
