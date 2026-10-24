from pathlib import Path,PurePosixPath
import hashlib,json,zipfile,ast
R=Path(__file__).resolve().parent;zpath=R.parents[1]/'coder/d1android02-facts-v2-qualification06/QUALIFICATION06-frozen.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(zpath.read_bytes())=='250c98231da3df0ae87e9f99f733e030a15de6d25c0ec8adf4a3531e3e4e4fd5'
with zipfile.ZipFile(zpath) as z:
 names=z.namelist();assert len(names)==len(set(names))==133
 mb=z.read('reference/full-manifest.json');assert sha(mb)=='68dd9820be6eeaf585cbe22793f8a4bc4a1b279acc6356ced0d6dcaa4b8d2e1d'
 m=json.loads(mb);rows=m['files'];assert len(rows)==132 and sum(x['bytes'] for x in rows)==4654998
 for x in rows:
  b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 extracted=[]
 for n in names:
  p=PurePosixPath(n);assert not p.is_absolute() and '..' not in p.parts
  if 'work' in p.parts or p.parts[0]=='evidence' or n=='reference/plan06.json':continue
  if p.suffix not in ('.py','.ps1','.txt','.json','.patch','.md'):continue
  b=z.read(n);f=R/'sealed-code'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
  extracted.append({'path':n,'bytes':len(b),'sha256':sha(b)})
 for n,h in [('reference/runner-source-seal.json','0651323122601622751a4958ae132cc33a6f8f3f5413bcacb69dd38ff4a524aa'),('reference/gate-sources.json','fcc9c66d6be539cbcc936da51178426c9b993d24017d9fdf840f8b12268fbf45'),('DELIVERY.md','d7773dd5c2747bd77a720de4849c302ab0ccdb47a840a820056b54aa010aab82')]:assert sha(z.read(n))==h
 out={'archiveSha256':sha(zpath.read_bytes()),'manifestSha256':sha(mb),'zipMembers':133,'snapshotFiles':132,'snapshotBytes':4654998,'bad':0,'extracted':extracted,'inventory':rows,'productCalls':0,'scope':'ZIP-only; no work outputs materialized or active objects queried'}
 (R/'extraction-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'members':133,'files':132,'bytes':4654998,'extracted':len(extracted),'bad':0}))
