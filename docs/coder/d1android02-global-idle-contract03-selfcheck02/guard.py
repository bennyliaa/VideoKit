"""Fixed SELFCHECK02 pre-constructor profiles; audit observes only."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,threading
H=Path(__file__).resolve().parent
B=Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract03-fix')
PROJECT=Path('D:/CodexProjects/VideoKit')
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
ORIGINAL_POPEN=subprocess.Popen
def digest(v):return hashlib.sha256(v).hexdigest()
def env_digest(e):return None if e is None else digest(json.dumps(e,sort_keys=True,separators=(',',':')).encode())
class Registry:
 def __init__(self,profile):
  self.profile=profile;self.calls=[];self.events=[];self.stop=False;self.local=threading.local()
 def check(self,argv,kw):
  if type(argv) is not list or not argv or any(type(x) is not str for x in argv):raise ValueError('PRE_ARGV_TYPE')
  if argv[0] not in (PY,PS):raise ValueError('PRE_PROGRAM')
  if kw.get('shell',False) is not False or kw.get('close_fds',True) is not True:raise ValueError('PRE_SHELL_OR_INHERITANCE')
  if set(kw)-{'stdin','stdout','stderr','executable','cwd','env','shell','close_fds'}:raise ValueError('PRE_UNDECLARED_KWARG')
  if kw.get('executable') not in (None,argv[0]):raise ValueError('PRE_EXPLICIT_EXE')
  if kw.get('stdin')!=subprocess.DEVNULL or kw.get('stdout')!=subprocess.PIPE or kw.get('stderr')!=subprocess.PIPE:raise ValueError('PRE_STREAMS')
  cwd=kw.get('cwd');env=kw.get('env')
  if str(Path.cwd())!=self.profile['hostCwd']:raise ValueError('PRE_HOST_CWD_CHANGED')
  if cwd is not None and cwd!=self.profile['qualificationCwd']:raise ValueError('PRE_CWD')
  if cwd is None:
   if env is not None or env_digest(dict(os.environ))!=self.profile['inheritedEnvSha256']:raise ValueError('PRE_INHERITED_ENV_CHANGED')
  elif env!=self.profile['qualificationEnv']:raise ValueError('PRE_EXACT_ENV')
  if argv[0]==PY:
   if argv[1:5]!=['-I','-X','utf8','-B'] or len(argv)<6:raise ValueError('PRE_PY_PREFIX')
   script=Path(argv[5]);tail=argv[6:]
  else:
   if argv[1:4]!=['-NoProfile','-NonInteractive','-File'] or len(argv)<5:raise ValueError('PRE_PS_PREFIX')
   script=Path(argv[4]);tail=argv[5:]
  family=None
  if script==H/'reuse/owned_child.py' and tail in (['ok'],['fail']):family='qualification-python'
  elif script==H/'reuse/owned_child.ps1' and tail==[]:family='qualification-PS'
  elif script==B/'tools/production_runner.py':
   if tail in ([],['--mode','live']):family='default-deny-CLI'
   elif len(tail)==10 and tail[::2]==['--mode','--permit','--permit-sha256','--approval','--approval-sha256']:
    permit=json.loads(Path(tail[3]).read_bytes());approval=Path(tail[7]).read_bytes()
    if tail[1] not in ('fixture','live') or permit.get('mode')!='OFFLINE_FIXTURE' or digest(Path(tail[3]).read_bytes())!=tail[5] or digest(approval)!=tail[9]:raise ValueError('PRE_OFFLINE_CLI_BINDING')
    family='exact-offline-CLI'
  elif script==B/'selfchecks/route_fixture.py' and len(tail)==1:
   ctx=json.loads(Path(tail[0]).read_bytes())
   if ctx.get('kind')!='OFFLINE_FIXTURE':raise ValueError('PRE_NO_NATIVE_ROUTE')
   family='fixed-route-fixture'
  elif script==B/'selfchecks/fact_fixture.py' and tail==['COMPLETE']:family='fixed-fact-fixture'
  elif script in (H/'helpers/prestart_lifetimes.ps1',H/'helpers/review_semantics.ps1'):
   expected=['-OutputFile'] if script.name=='prestart_lifetimes.ps1' else ['-InputFile','-OutputFile']
   if tail[::2]!=expected or len(tail)!=2*len(expected):raise ValueError('PRE_FUNCTION_HELPER_ARGS')
   if not all(Path(x).is_relative_to(H) for x in tail[1::2]):raise ValueError('PRE_FUNCTION_OUTPUT_ROOT')
   family='fixed-function-helper'
  elif script.name=='capture_android02.ps1' and len(tail)==6 and tail[::2]==['-RequestPath','-PredecessorProofSha','-OwnerAdmissionSha']:
   from entry_gates import fixture_root_allowed
   home=script.parent.parent
   if not fixture_root_allowed(str(home/'outputs')) or not Path(tail[1]).is_relative_to(home):raise ValueError('PRE_FRESH_CONTROLLER_ROOT')
   policy=json.loads((home/'release/capture-policy.json').read_bytes());request=json.loads(Path(tail[1]).read_bytes())
   if policy['mode']!='OFFLINE_FIXTURE' or request['argv'][0]!=PY:raise ValueError('PRE_LOCAL_CONTROLLER_ONLY')
   if digest(script.read_bytes())!=self.profile['candidateSources']['tools/capture_android02.ps1']:raise ValueError('PRE_CONTROLLER_SOURCE')
   family='original-owned-PS-controller'
  elif script.name=='post-guard-host.ps1' and script.is_relative_to(Path(self.profile['candidateOutput'])) and not tail:family='fixed-post-guard-producer'
  if family is None:raise ValueError('PRE_UNDECLARED_FULL_ARGV')
  key=str(script)
  if key in self.profile['scriptPins'] and digest(script.read_bytes())!=self.profile['scriptPins'][key]:raise ValueError('PRE_HELPER_SOURCE')
  return dict(argv=list(argv),family=family,applicationName=kw.get('executable'),commandLine=subprocess.list2cmdline(argv),cwd=cwd,envSha256=env_digest(env),scriptSha256=digest(script.read_bytes()))
 def construct(self,argv,*pos,**kw):
  if pos:raise ValueError('PRE_POSITIONAL_OPTIONS')
  if self.stop or len(self.calls)>=96:raise ValueError('PRE_NO_NEW_ADMISSION')
  row=self.check(argv,kw);row.update(constructorEntered=False,constructorReturned=False);self.calls.append(row)
  self.local.expected=row
  try:
   row['constructorEntered']=True;p=ORIGINAL_POPEN(argv,**kw);row['constructorReturned']=True;return p
  finally:self.local.expected=None
 def observe(self,event,args):
  if event!='subprocess.Popen':return
  # Never throw or do IO here: Windows already may own temporary handles.
  try:
   expected=getattr(self.local,'expected',None)
   match=expected is not None and type(args) is tuple and len(args)==4 and args[0]==expected['applicationName'] and type(args[1]) is str and args[1]==expected['commandLine'] and args[2]==expected['cwd'] and env_digest(args[3])==expected['envSha256']
   self.events.append(dict(applicationName=args[0],commandLine=args[1],cwd=args[2],envSha256=env_digest(args[3]),matches=match))
   if not match:self.stop=True
  except BaseException as e:self.events.append(dict(observerError=type(e).__name__,matches=False));self.stop=True
