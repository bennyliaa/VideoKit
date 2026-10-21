"""Verify frozen C01 evidence/copies, and recompute every read-only sample hash."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();out=root/'docs/coder/d1c02/evidence'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
c01=json.loads((root/'docs/coder/d1/evidence/freeze-summary.json').read_text(encoding='utf-8'));frozen=[]
for row in c01['artifacts']+c01['evidence']:
    frozen.append({'path':row['path'],'expected':row['sha256'],'actual':sha(root/row['path'])})
original_sources=json.loads((root/'docs/coder/d1/evidence/source-manifest.json').read_text(encoding='utf-8'))
for row in original_sources['source_files']:
    if row['path'].startswith('docs/coder/d1/') or row['path']=='docs/coder/D1_DELIVERY_D1-20261005-C01.md':
        frozen.append({'path':row['path'],'expected':row['sha256'],'actual':sha(root/row['path'])})
# Mutable workspace sources cannot be compared to the old manifest during C02.
inventory=json.loads((root/'docs/coder/d1/evidence/media-inventory.json').read_text(encoding='utf-8'));samples=[]
for row in inventory['files']:
    path='test_media/'+row['relative_path'];samples.append({'path':path,'expected':row['sha256'],'actual':sha(root/path)})
result={'c01_frozen_files':frozen,'samples':samples,'scope':'C01 artifact/evidence checks and 45 original media files; excludes mutable app/build config from old source manifest comparison','status':'PASS' if all(x['expected']==x['actual'] for x in frozen+samples) else 'FAIL'}
(out/'integrity-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(result['status'],'C01 frozen files',len(frozen),'media',len(samples))
if result['status']!='PASS':raise SystemExit(1)
