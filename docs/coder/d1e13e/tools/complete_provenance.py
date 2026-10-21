from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for row in json.loads((E/'tested-final-class-equivalence.json').read_text())['members']:
 p=B/'.checks'/row['attempt']/row['entry'];assert sha(p)==row['sha256'];q=E/'tested-class-bytes'/row['attempt']/row['entry'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
for attempt in ['host-006','android-005']:
 for row in json.loads((E/attempt/'inputs.json').read_text()):
  p=R/row['path'];assert sha(p)==row['sha256'],row['path'];q=E/attempt/'final-source-snapshots'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
print('PASS exact tested classes and final input snapshots retained')
