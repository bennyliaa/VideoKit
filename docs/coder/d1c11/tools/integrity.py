"""Verify immutable C01/C02 deliveries and 45 read-only media."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();out=root/'docs/coder/d1c11/evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
frozen=[]
assert sha(root/'docs/coder/d1c10/evidence/freeze-summary.json')=='4b728a9b5694e096e0374cd8d2e5bb77ce53afb173e512d0308d8f9ca4e0deec'
assert sha(root/'docs/coder/d1c03/evidence/freeze-summary.json')=='c5f6e23156f2c100079b8e3c04070afd9004c9123865558e64bb5f32058ec707'
assert sha(root/'docs/coder/d1c04/evidence/freeze-summary.json')=='3085520db7458d3bf2da45df0361b2ede350b3b9b02ab1be84cc63a93bf9a472'
assert sha(root/'docs/coder/d1c05/evidence/freeze-summary.json')=='811ca000436ac10fa16d0d88fb0996122e68a8fe984756a9bdd8336c7ff89d29'
assert sha(root/'docs/coder/d1c06/evidence/freeze-summary.json')=='1fc7ef1b294c8e2dd11d3b547385bcec2875540bbc1428f939bfdbd198ae6f0d'
assert sha(root/'docs/coder/d1c07/evidence/freeze-summary.json')=='b6bc17f919adba3bb2d837fb456382ec02650229d6ce352607136dea3d557572'
assert sha(root/'docs/coder/d1c08/evidence/freeze-summary.json')=='c086f5a21a6fcfa616d244c4762e6d1c7bd8abcf336079879de02d9e038ba520'
assert sha(root/'docs/coder/d1c09/evidence/freeze-summary.json')=='cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa'
for folder,candidate in [('d1','C01'),('d1c02','C02'),('d1c03','C03'),('d1c04','C04'),('d1c05','C05'),('d1c06','C06'),('d1c07','C07'),('d1c08','C08'),('d1c09','C09'),('d1c10','C10')]:
 e=root/'docs/coder'/folder/'evidence';summary=json.loads((e/'freeze-summary.json').read_text(encoding='utf-8'));source=json.loads((e/'source-manifest.json').read_text(encoding='utf-8'))
 selected=summary['artifacts']+summary['evidence']+[r for r in source['source_files'] if r['path'].startswith('docs/coder/'+folder+'/') or r['path']=='docs/coder/D1_DELIVERY_D1-20261005-'+candidate+'.md' or (candidate in ('C03','C04','C05','C06','C07','C08','C09','C10') and r['path'].startswith('docs/coder/') and candidate in Path(r['path']).name) or (candidate=='C02' and r['path']=='docs/coder/D1_DEVICE_TEST_REQUEST_V1.0.md') or (candidate=='C07' and r['path']=='docs/coder/D1_SINGLE_APP_ISOLATION_OPTIONS_V1.0.md')]
 for r in selected:frozen.append({'candidate':candidate,'path':r['path'],'expected':r['sha256'],'actual':sha(root/r['path'])})
inventory=json.loads((root/'docs/coder/d1c02/evidence/media-inventory.json').read_text(encoding='utf-8'));samples=[]
for r in inventory['files']:
 p='test_media/'+r['relative_path'];samples.append({'path':p,'expected':r['sha256'],'actual':sha(root/p)})
result={'frozen_files':frozen,'samples':samples,'scope':'immutable artifacts/evidence/source snapshots/reports/C02 request; mutable root app config excluded','status':'PASS' if all(r['expected']==r['actual'] for r in frozen+samples) else 'FAIL'}
(out/'integrity-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result['status'],len(frozen),'immutable entries',len(samples),'media');assert result['status']=='PASS'
