"""Read-only whole-candidate verification. No subprocess or SDK calls."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[4]
B=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 seal=B/'evidence/capture-ready01-freeze.json';d=json.loads(seal.read_text(encoding='utf-8'));bad=[]
 for row in d['files']:
  p=R/row['path']
  if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:bad.append(row['path'])
 print(json.dumps({'sealSha256':sha(seal),'rows':len(d['files']),'bad':bad,'sdkChildren':0,'mode':'READ_ONLY'},ensure_ascii=False))
 return bool(bad)
if __name__=='__main__':sys.exit(main())
