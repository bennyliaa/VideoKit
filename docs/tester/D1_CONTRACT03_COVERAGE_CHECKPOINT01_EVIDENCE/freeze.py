"""CreateNew file-only test freeze; git and later delivery are separate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parent;T=R.parent;N='D1_CONTRACT03_COVERAGE_CHECKPOINT01'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def main():
 report=T/(N+'_REPORT_V1.0.md');a=json.loads((R/'post-audit.json').read_bytes());assert a['allOwnStartedOriginalsReturned'] and not a['newResourceUnknown']
 order=json.loads((R/'order.json').read_bytes());W=Path(order['work']);assert not list(W.rglob('*.*'))
 paths=[report,*[p for p in R.rglob('*') if p.is_file() and 'git' not in p.relative_to(R).parts]]
 rows=[]
 for p in sorted(paths):
  with p.open('rb') as f:b=f.read()
  rows.append(dict(absolutePath=str(p),bytes=len(b),sha256=sha(b)))
 manifest=T/(N+'_MANIFEST_V1.0.json');put(manifest,dict(schema='CONTRACT03_COVERAGE_CHECKPOINT01_MANIFEST_V1',batch=order['batch'],status=a['status'],files=rows,emptyScopeDirectories=[str(W),str(W/'one')],excluded=['self manifest','freeze receipt','Git inventory and operations','later combined delivery and coordinator send receipt']))
 for x in rows:
  with Path(x['absolutePath']).open('rb') as f:b=f.read()
  assert len(b)==x['bytes'] and sha(b)==x['sha256']
 receipt=dict(schema='CONTRACT03_COVERAGE_CHECKPOINT01_FREEZE_RECEIPT_V1',batch=order['batch'],utc=datetime.now(timezone.utc).isoformat(),reportPath=str(report),reportSha256=sha(report.read_bytes()),manifestPath=str(manifest),manifestSha256=sha(manifest.read_bytes()),files=len(rows),bytes=sum(x['bytes'] for x in rows),bad=0,verdict=a['status'],allOwnStartedOriginalsReturned=True,newResourceUnknown=False,dynamicAttempts=1,retries=0,original98_484_408_744Unchanged=True,actualSDK=0,actualNativeRoute=0,devices=0,gitPhase='AUTHORIZED_NOT_STARTED',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 put(T/(N+'_FREEZE_RECEIPT_V1.0.json'),receipt)
 print(json.dumps(receipt))
if __name__=='__main__':main()
