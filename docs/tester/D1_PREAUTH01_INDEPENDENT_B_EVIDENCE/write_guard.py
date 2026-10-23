"""Pre-operation write roots, separate from observation-only process audit."""
from pathlib import Path
import builtins,io,json,os,re
R=Path(__file__).resolve().parent;B=R.parents[1]/'coder/d1android02-readonly-facts-preauth01';EVENTS=[];ORIGINALS=None
def allowed(path):
 if isinstance(path,int):raise ValueError('UNBOUND_WRITE_DESCRIPTOR')
 p=Path(path).absolute().resolve();roots=[R]
 order=R/'order.json'
 if order.exists():
  o=json.loads(order.read_bytes());w=Path(o['work']).resolve()
  if w.parent!=B/'selfchecks/work' or not w.name.startswith('indb-'):raise ValueError('WRITE_SCOPE_ORDER_ROOT')
  roots.append(w)
 if not any(p==r or p.is_relative_to(r) for r in roots):raise ValueError('WRITE_OUTSIDE_NEW_BATCH_ROOTS')
 if re.search(r'(?:^|/)(?:aux|con|prn|nul|com[1-9]|lpt[1-9])(?:\.[^/]*)?(?:/|$)',p.as_posix(),re.I):raise ValueError('WINDOWS_RESERVED_NEW_ARTIFACT')
 return str(p)
def install(registry):
 global ORIGINALS
 assert ORIGINALS is None
 ORIGINALS=(builtins.open,io.open,os.open,os.mkdir)
 def checked_open(fn):
  def op(path,mode='r',*a,**k):
   if any(c in mode for c in 'wax+'):
    p=allowed(path);EVENTS.append(dict(operation='open',path=p,mode=mode))
   return fn(path,mode,*a,**k)
  return op
 def osopen(path,flags,*a,**k):
  if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
   if str(path).casefold()==os.devnull.casefold() and flags==os.O_RDWR and getattr(registry.local,'expected',None) is not None:EVENTS.append(dict(operation='os.open',special='FIXED_PROFILE_SUBPROCESS_DEVNULL'))
   else:EVENTS.append(dict(operation='os.open',path=allowed(path),flags=flags))
  return ORIGINALS[2](path,flags,*a,**k)
 def mkdir(path,*a,**k):EVENTS.append(dict(operation='mkdir',path=allowed(path)));return ORIGINALS[3](path,*a,**k)
 builtins.open=checked_open(ORIGINALS[0]);io.open=checked_open(ORIGINALS[1]);os.open=osopen;os.mkdir=mkdir
