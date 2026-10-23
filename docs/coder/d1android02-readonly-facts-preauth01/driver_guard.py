"""Finite exact profiles; audit has no rejection or IO."""
from pathlib import Path
import hashlib,json,subprocess,os,threading,time
B=Path(__file__).resolve().parent
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
ORIGINAL=subprocess.Popen
def sha(b):return hashlib.sha256(b).hexdigest()
def env_hash(e):return None if e is None else sha(json.dumps(e,sort_keys=True,separators=(',',':')).encode())
class Registry:
 def __init__(self,p,start):self.p=p;self.start=start;self.calls=[];self.events=[];self.stop=False;self.local=threading.local()
 def check(self,a,k):
  if type(a) is not list or any(type(x) is not str for x in a) or not a or a[0] not in (PY,PS):raise ValueError('PROFILE_PROGRAM_ARGV')
  if set(k)-{'stdin','stdout','stderr','executable','cwd','env','shell','close_fds'} or k.get('shell',False) is not False or k.get('close_fds',True) is not True or k.get('executable') not in (None,a[0]):raise ValueError('PROFILE_KWARGS')
  if k.get('stdin')!=subprocess.DEVNULL or k.get('stdout')!=subprocess.PIPE or k.get('stderr')!=subprocess.PIPE:raise ValueError('PROFILE_STREAMS')
  if str(Path.cwd())!=self.p['hostCwd']:raise ValueError('PROFILE_HOST_CWD')
  if k.get('cwd') is None:
   if k.get('env') is not None or env_hash(dict(os.environ))!=self.p['inheritedEnvSha256']:raise ValueError('PROFILE_INHERITED_ENV')
  elif k.get('cwd')!=self.p['qualificationCwd'] or k.get('env')!=self.p['qualificationEnv']:raise ValueError('PROFILE_CWD_ENV')
  prefix=['-I','-X','utf8','-B'] if a[0]==PY else ['-NoProfile','-NonInteractive','-File']
  i=1+len(prefix)
  if a[1:i]!=prefix or len(a)<=i:raise ValueError('PROFILE_PREFIX')
  script=Path(a[i]);tail=a[i+1:];rel=script.relative_to(B).as_posix() if script.is_relative_to(B) else None
  if rel not in self.p['scriptPins'] or sha(script.read_bytes())!=self.p['scriptPins'][rel]:raise ValueError('PROFILE_SOURCE')
  good=False
  if rel=='driver/reuse/owned_child.py':good=tail in (['ok'],['fail'])
  elif rel=='driver/reuse/owned_child.ps1':good=tail==[]
  elif rel=='selfchecks/fact_fixture.py':good=tail==['COMPLETE']
  elif rel=='selfchecks/route_fixture.py' and len(tail)==1:
   ctx=Path(tail[0]);good=ctx.is_relative_to(B/'selfchecks/work') and json.loads(ctx.read_bytes()).get('kind')=='OFFLINE_FIXTURE'
  elif rel=='selfchecks/review_semantics.ps1':good=len(tail)==4 and tail[::2]==['-InputFile','-OutputFile'] and all(Path(x).is_relative_to(B/'selfchecks/work') for x in tail[1::2])
  elif rel=='selfchecks/prestart_lifetimes.ps1':good=len(tail)==2 and tail[0]=='-OutputFile' and Path(tail[1]).is_relative_to(B/'selfchecks/work')
  elif rel=='tools/facts_entry.py':
   good=not tail or len(tail)==6 and tail[::2]==['--template','--approved-template-sha256','--policy'] and all(Path(x).is_relative_to(B/'selfchecks/work') for x in (tail[1],tail[5])) and sha(Path(tail[1]).read_bytes())==tail[3] and json.loads(Path(tail[1]).read_bytes())['mode']=='OFFLINE_FIXTURE'
  if not good:raise ValueError('PROFILE_EXACT_TAIL')
  return dict(argv=list(a),applicationName=k.get('executable'),commandLine=subprocess.list2cmdline(a),cwd=k.get('cwd'),envSha256=env_hash(k.get('env')))
 def construct(self,a,*pos,**k):
  if pos or self.stop or len(self.calls)>=96 or time.monotonic()-self.start>=320:raise ValueError('PROFILE_STOP_NEW')
  row=self.check(a,k);self.calls.append(row);self.local.expected=row
  try:p=ORIGINAL(a,**k);row['constructorReturned']=True;return p
  finally:self.local.expected=None
 def observe(self,event,args):
  if event!='subprocess.Popen':return
  try:
   r=getattr(self.local,'expected',None);ok=r is not None and len(args)==4 and args[0]==r['applicationName'] and args[1]==r['commandLine'] and args[2]==r['cwd'] and env_hash(args[3])==r['envSha256'];self.events.append(dict(matches=ok,applicationName=args[0],commandLine=args[1]))
   if not ok:self.stop=True
  except BaseException:self.stop=True;self.events.append(dict(matches=False,observerError=True))
