from pathlib import Path
import os,sys,json,time,subprocess,threading,hashlib
H=Path(__file__).resolve().parents[1];sys.path.insert(0,str(H/'selfchecks'))
from call_plan07 import facts_argv,review_argv,aux_argv
PLAN=json.loads((H/'reference/plan07.json').read_bytes());PROFILE=json.loads((H/'reference/profile07.json').read_bytes());W=Path(PLAN['work']);START=PLAN['batchStart'];ORIGINAL=subprocess.Popen
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class Guard:
 def __init__(self):self.calls=[];self.events=[];self.used=set();self.local=threading.local();self.stop=False
 def check(self,a,k):
  if time.monotonic()-START>=320 or self.stop or len(self.calls)>=96:raise ValueError('BATCH_STOP_NEW')
  if str(Path.cwd())!=PLAN['cwd'] or dict(os.environ)!=PLAN['expectedEnvironment']:raise ValueError('HOST_CONTEXT_CHANGED')
  if type(a) is not list or not a or any(type(x) is not str for x in a) or a[0] not in (PY,PS):raise ValueError('FIXED_PROGRAM')
  if set(k)-{'stdin','stdout','stderr','executable','cwd','env','shell','close_fds'} or k.get('shell',False) is not False or k.get('close_fds',True) is not True or k.get('stdin')!=-3 or k.get('stdout')!=-1 or k.get('stderr')!=-1 or k.get('executable') not in (None,a[0]) or k.get('cwd') is not None or k.get('env') is not None:raise ValueError('FIXED_POPEN_OPTIONS')
  prefix=['-I','-X','utf8','-B'] if a[0]==PY else ['-NoProfile','-NonInteractive','-File'];i=1+len(prefix)
  if a[1:i]!=prefix or len(a)<=i:raise ValueError('FIXED_PREFIX')
  source=Path(a[i]);key=None
  f=PLAN['facts'];root=Path(f['root'])
  exact=facts_argv(PLAN)
  if a==exact:key='facts'
  for mode in ('ok','fail'):
   if a==[PY,'-I','-X','utf8','-B',str(H/'driver/context_child.py'),mode]:key='qual-'+mode
  if a==[PS,'-NoProfile','-NonInteractive','-File',str(H/'driver/owned_child.ps1')]:key='qual-PS'
  for label,t in PLAN['targets'].items():
   if a==review_argv(PLAN,label):key='review-'+label
   home=Path(t['home'])
   if a==[PY,'-I','-X','utf8','-B',str(H/'selfchecks/route_fixture.py'),str(home/'outputs/gate-context.json')]:key='gate-'+label
   for role in (['identity','global_idle'] if label=='positive' else ['identity','global_idle'] if label=='receipt-replace' else ['identity']):
    rp=home/('request-'+role+'.json');ap=home/'outputs'/(role+'-owner-admission.json')
    if len(a)==11 and a[:5]==[PS,'-NoProfile','-NonInteractive','-File',str(home/'tools/capture_android02.ps1')] and a[5:8]==['-RequestPath',str(rp),'-PredecessorProofSha'] and a[9]=='-OwnerAdmissionSha':
     ad=load(ap);rq=load(rp)
     if a[10]!=digest(ap) or a[8]!=ad['predecessorProofSha256'] or ad['requestSha256']!=digest(rp) or ad['scope']!=t['target']['scope'] or rq['id']!=role or ad['ownerPid']!=os.getpid():raise ValueError('DERIVED_ORIGINAL_REQUEST_BINDING')
     if digest(source)!=digest(H/'tools/capture_android02.ps1'):raise ValueError('COPIED_ENTRY_SOURCE')
     key='capture-'+label+'-'+role
  for label,script in [('budget','budget_models.ps1'),('v1','review_semantics.ps1')]:
   if a==aux_argv(PLAN,label):key=label
  if key is None:raise ValueError('EXACT_FROZEN_GRAPH_ONLY')
  if source.is_relative_to(H) and not source.is_relative_to(W):
   rel=source.relative_to(H).as_posix();pin=next(x['sha256'] for x in PROFILE if x['path']==rel)
   if digest(source)!=pin:raise ValueError('FIXED_SOURCE')
  return key
 def construct(self,a,*args,**k):
  if args:raise ValueError('NO_POSITIONAL_OPTIONS')
  key=self.check(a,k)
  if key in self.used:raise ValueError('ORIGINAL_TUPLE_ONCE')
  self.used.add(key);row=dict(key=key,argv=a,kwargs=k);self.calls.append(row);self.local.expected=(k.get('executable'),subprocess.list2cmdline(a),k.get('cwd'),k.get('env'))
  try:p=ORIGINAL(a,**k);row['constructorReturned']=True;return p
  finally:self.local.expected=None
 def observe(self,e,a):
  if e!='subprocess.Popen':return
  ok=getattr(self.local,'expected',None)==a;self.events.append(dict(matches=ok))
  if not ok:self.stop=True