"""Raw process parameters remain exact; child environment gets Windows keys."""
from pathlib import Path
import os,hashlib,json
def sha(b):return hashlib.sha256(b).hexdigest()
def normalize(pairs):
 values=pairs.items() if isinstance(pairs,dict) else pairs;out={}
 for key,value in values:
  if type(key) is not str or type(value) is not str:raise ValueError('HOST_ENV_TYPE')
  name=key.upper()
  if name in out:raise ValueError('HOST_ENV_CASE_COLLISION')
  out[name]=value
 return out
def digest(d):return sha(json.dumps(d,sort_keys=True,separators=(',',':')).encode())
def child_env(raw,parent):return normalize(parent if raw is None else raw)
def child_cwd(raw,parent):return str(Path(parent if raw is None else raw).resolve())
def snapshot():
 env=normalize(dict(os.environ));controlled=['SYSTEMROOT','WINDIR','TEMP','TMP']
 return dict(actualCwd=str(Path.cwd()),environmentKeys=sorted(env),canonicalEnvironmentSha256=digest(env),controlledValueHashes={k:sha(env[k].encode()) for k in controlled if k in env},valuesDisclosed=False)
def pure_models(root):
 raw={'SystemRoot':'C:\\Windows','TEMP':str(root)};parent={'SYSTEMROOT':'C:\\Windows','TEMP':str(root)};rows=[]
 assert digest(raw)!=digest(normalize(raw));assert child_env(raw,parent)==parent;assert child_env(None,parent)==parent
 rows.extend([dict(case='raw-vs-child-key-case',pass_=True),dict(case='explicit-env-child',pass_=True),dict(case='None-inherits-parent',pass_=True),dict(case='None-cwd-inherits',pass_=child_cwd(None,root)==str(Path(root).resolve())),dict(case='explicit-cwd',pass_=child_cwd(root,Path(root).parent)==str(Path(root).resolve()))])
 for name,pairs in [('duplicate',[('TEMP','x'),('TEMP','x')]),('case-collision',[('SystemRoot','x'),('SYSTEMROOT','x')])]:
  try:normalize(pairs)
  except ValueError as e:assert str(e)=='HOST_ENV_CASE_COLLISION';rows.append(dict(case=name,reason=str(e),pass_=True))
  else:raise AssertionError('COLLISION_NOT_REJECTED')
 return rows
