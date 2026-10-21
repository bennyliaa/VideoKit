"""Verify immutable C01/C02 deliveries and 45 read-only media."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();out=root/'docs/coder/d1c03/evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
frozen=[]
for folder,candidate in [('d1','C01'),('d1c02','C02')]:
 e=root/'docs/coder'/folder/'evidence';summary=json.loads((e/'freeze-summary.json').read_text(encoding='utf-8'));source=json.loads((e/'source-manifest.json').read_text(encoding='utf-8'))
 selected=summary['artifacts']+summary['evidence']+[r for r in source['source_files'] if r['path'].startswith('docs/coder/'+folder+'/') or r['path']=='docs/coder/D1_DELIVERY_D1-20261005-'+candidate+'.md' or (candidate=='C02' and r['path']=='docs/coder/D1_DEVICE_TEST_REQUEST_V1.0.md')]
 for r in selected:frozen.append({'candidate':candidate,'path':r['path'],'expected':r['sha256'],'actual':sha(root/r['path'])})
inventory=json.loads((root/'docs/coder/d1c02/evidence/media-inventory.json').read_text(encoding='utf-8'));samples=[]
for r in inventory['files']:
 p='test_media/'+r['relative_path'];samples.append({'path':p,'expected':r['sha256'],'actual':sha(root/p)})
result={'frozen_files':frozen,'samples':samples,'scope':'immutable artifacts/evidence/source snapshots/reports/C02 request; mutable root app config excluded','status':'PASS' if all(r['expected']==r['actual'] for r in frozen+samples) else 'FAIL'}
(out/'integrity-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result['status'],len(frozen),'immutable entries',len(samples),'media');assert result['status']=='PASS'
