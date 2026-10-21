from pathlib import Path
import hashlib,json,sys,zipfile,re
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c12';e=base/'evidence'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
summary=json.loads((e/'freeze-summary.json').read_text(encoding='utf-8'));manifest=json.loads((e/'source-manifest.json').read_text(encoding='utf-8'))
assert sha(e/'source-manifest.json')==summary['source_manifest_sha256']
for r in summary['artifacts']+summary['evidence']:
 p=root/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
expected={r['path']:r for r in manifest['source_files']};archive=base/'artifacts/D1-20261016-C12/D1-20261016-C12-source.zip'
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for name,r in expected.items():
  data=z.read(name);assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],name
  if '--working-tree' in sys.argv or name.startswith('docs/coder/d1c12/') or (name.startswith('docs/coder/') and 'C12' in Path(name).name):assert sha(root/name)==r['sha256'],name
assert {r['path'] for r in summary['evidence']}=={p.relative_to(root).as_posix() for p in e.rglob('*') if p.is_file() and p.name!='freeze-summary.json'}
review=json.loads((e/'candidate-self-review.json').read_text(encoding='utf-8'));assert all(review[k]==summary[k] for k in ['pure_assertions','script_assertions','total_local_assertions','cpu_device_methods']);assert review['total_local_assertions']==review['pure_assertions']+review['script_assertions']
def count(output):
 match=re.search(r'^PASS (\d+) |assertions=(\d+)',output,re.M);assert match
 return int(next(value for value in match.groups() if value is not None))
results=json.loads((e/'local-check-results.json').read_text(encoding='utf-8'));assert all(r['exit']==0 for r in results)
assert sum(count(r['output']) for r in results)==review['pure_assertions']
assert sum(count((e/name).read_text(encoding='utf-8-sig')) for name in ['device-guard-selfcheck.log','device-runner-selfcheck.log'])==review['script_assertions']
plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'))
for group in ['cpu','host','legacy']:assert len(plan['groups'][group])==summary[group+'_device_methods']
assert plan['total_per_eligible_device']==sum(len(v) for v in plan['groups'].values())
print(json.dumps({'candidateId':summary['candidateId'],'integrity':'PASS','working_tree_checked':'--working-tree' in sys.argv,'frozen_at':summary['frozen_at'],'source_files':len(expected),'evidence_files':len(summary['evidence']),'artifacts':len(summary['artifacts']),'source_zip_sha256':sha(archive),'freeze_summary_sha256':sha(e/'freeze-summary.json'),'state':summary['state'],'android_execution':'NOT_RUN'},indent=2))
