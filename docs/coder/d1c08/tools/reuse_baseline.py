"""Reuse exact C02 reviewed versions; no repeat scan or weight downloads."""
from pathlib import Path
import json,hashlib,sys,shutil
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c02/evidence';out=root/'docs/coder/d1c08/evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
names={'supply-inventory.json','osv-results.json','media-inventory.json','traditional-tracking.log'}
for p in old.iterdir():
 if p.is_file() and (p.name in names or 'NOTICE' in p.name or 'model' in p.name.lower() or 'license' in p.name.lower()):
  shutil.copy2(p,out/p.name);rows.append({'file':p.name,'origin':p.relative_to(root).as_posix(),'sha256':sha(p)})
def coords(p):return {line.split('=')[0] for line in p.read_text().splitlines() if '=' in line and not line.startswith('#') and ':' in line.split('=')[0]}
inventory=json.loads((old/'supply-inventory.json').read_text());reviewed={r['coordinate'] for r in inventory['components']};worker=coords(root/'docs/coder/d1c08/worker_app/gradle.lockfile');app=coords(root/'app/gradle.lockfile');new=sorted((worker|app)-reviewed);assert not new,new
result={'candidateId':'D1-20261005-C08','status':'PASS_EXACT_COORDINATES_REUSED','baseline_files':rows,'worker_locked_coordinates':sorted(worker),'app_locked_coordinates':sorted(app),'new_maven_coordinates':new,'scope':'Exact reviewed versions reused; no new ecosystem scan. Companion notices reuse corresponding exact coordinates. Own JNI/NDK evidence separate. Metadata is not legal clearance.'}
(out/'baseline-reuse.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(result['status'],'worker',len(worker),'app',len(app))

