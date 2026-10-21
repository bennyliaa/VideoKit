"""Read-only frozen artifact/evidence/source ZIP verification; prints result, writes nothing."""
from pathlib import Path
import json,hashlib,zipfile,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c07';e=base/'evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
summary=json.loads((e/'freeze-summary.json').read_text(encoding='utf-8'));manifest=json.loads((e/'source-manifest.json').read_text(encoding='utf-8'))
assert sha(e/'source-manifest.json')==summary['source_manifest_sha256']
for r in summary['artifacts']+summary['evidence']:
 p=root/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
expected={r['path']:r for r in manifest['source_files']};archive=base/'artifacts/D1-20261005-C07/D1-20261005-C07-source.zip'
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for n,r in expected.items():
  data=z.read(n);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],n
  assert sha(root/n)==r['sha256'],n
assert {r['path'] for r in summary['evidence']}=={p.relative_to(root).as_posix() for p in e.rglob('*') if p.is_file() and p.name!='freeze-summary.json'}
assert json.loads((e/'candidate-self-review.json').read_text())['status']=='PASS'
print(json.dumps({'candidateId':summary['candidateId'],'status':'PASS','frozen_at':summary['frozen_at'],'artifacts':len(summary['artifacts']),'evidence_files':len(summary['evidence']),'zip_sources':len(expected),'source_zip_sha256':sha(archive),'freeze_summary_sha256':sha(e/'freeze-summary.json'),'device_execution':'NOT_RUN','acceptance':'BLOCKED / NOT_READY'},indent=2))
