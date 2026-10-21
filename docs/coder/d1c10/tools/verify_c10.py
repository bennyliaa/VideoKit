from pathlib import Path
import hashlib,json,sys,zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c10';e=base/'evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
summary=json.loads((e/'freeze-summary.json').read_text(encoding='utf-8'));manifest=json.loads((e/'source-manifest.json').read_text(encoding='utf-8'))
assert sha(e/'source-manifest.json')==summary['source_manifest_sha256']
for r in summary['artifacts']+summary['evidence']:
 p=root/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
expected={r['path']:r for r in manifest['source_files']};archive=base/'artifacts/D1-20261016-C10/D1-20261016-C10-source.zip'
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for name,r in expected.items():
  data=z.read(name);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],name
  if '--working-tree' in sys.argv or name.startswith('docs/coder/d1c10/') or (name.startswith('docs/coder/') and 'C10' in Path(name).name):assert sha(root/name)==r['sha256'],name
assert {r['path'] for r in summary['evidence']}=={p.relative_to(root).as_posix() for p in e.rglob('*') if p.is_file() and p.name!='freeze-summary.json'}
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));assert review['pure_assertions']==293 and review['total_local_assertions']==321 and review['cpu_device_methods']==25
print(json.dumps({'candidateId':summary['candidateId'],'integrity':'PASS','working_tree_checked':'--working-tree' in sys.argv,'frozen_at':summary['frozen_at'],'source_files':len(expected),'evidence_files':len(summary['evidence']),'artifacts':len(summary['artifacts']),'source_zip_sha256':sha(archive),'freeze_summary_sha256':sha(e/'freeze-summary.json'),'state':summary['state'],'android_execution':'NOT_RUN'},indent=2))
