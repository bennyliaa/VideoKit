from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];old=R/'docs/coder/d1e13';new=R/'docs/coder/d1e13a';new.mkdir(exist_ok=False)
roots=['src','android','upstream-c14','gradle','app/src','fixture/src','checks','tools'];rows=[]
for folder in roots:
 for p in (old/folder).rglob('*'):
  if p.is_file():
   q=new/p.relative_to(old);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);b=p.read_bytes();rows.append({'source':p.relative_to(R).as_posix(),'target':q.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
for parent in [old,old/'app',old/'fixture']:
 for p in parent.iterdir():
  if p.is_file() and (p.suffix in {'.kts','.properties','.lockfile','.p12'} or p.name in {'gradlew','gradlew.bat'}):
   q=new/p.relative_to(old);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);b=p.read_bytes();rows.append({'source':p.relative_to(R).as_posix(),'target':q.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(new/'evidence').mkdir();(new/'evidence/inherited-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
print('E13A inherited',len(rows))
