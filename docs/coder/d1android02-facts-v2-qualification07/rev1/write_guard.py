"""Only new batch work/evidence writes. Source/config/finally paths are guarded."""
from pathlib import Path
import builtins,io,os
H=Path(__file__).resolve().parent;EVENTS=[]
def allowed(p):
 if isinstance(p,int):raise ValueError('UNBOUND_WRITE_FD')
 q=Path(p).absolute().resolve()
 if not any(q==r or q.is_relative_to(r) for r in (H/'selfchecks/work',H/'evidence')):raise ValueError('WRITE_OUTSIDE_NEW_OUTPUT_ROOTS')
 return str(q)
def install(reg):
 bo,ioo,oo,md=builtins.open,io.open,os.open,os.mkdir
 def wrap(fn):
  def op(p,mode='r',*a,**k):
   if any(c in mode for c in 'wax+'):EVENTS.append(dict(op='open',path=allowed(p)))
   return fn(p,mode,*a,**k)
  return op
 def op(p,flags,*a,**k):
  if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
   if str(p).casefold()==os.devnull.casefold() and flags==os.O_RDWR and getattr(reg.local,'expected',None) is not None:pass
   else:EVENTS.append(dict(op='os.open',path=allowed(p)))
  return oo(p,flags,*a,**k)
 def mkdir(p,*a,**k):EVENTS.append(dict(op='mkdir',path=allowed(p)));return md(p,*a,**k)
 builtins.open=wrap(bo);io.open=wrap(ioo);os.open=op;os.mkdir=mkdir
