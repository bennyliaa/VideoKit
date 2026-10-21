"""Read-only seal verification, no subprocesses."""
from pathlib import Path
import hashlib,json,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];p=B/'evidence/ready03-fix-freeze.json';d=json.loads(p.read_text(encoding='utf-8'));bad=[]
for row in d['files']:
 q=R/row['path']
 if not q.is_file() or q.stat().st_size!=row['bytes'] or hashlib.sha256(q.read_bytes()).hexdigest()!=row['sha256']:bad.append(row['path'])
print(json.dumps({'sealSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(d['files']),'bad':bad,'sdkActions':0}));sys.exit(bool(bad))
