"""Closed pre-constructor tuples and one shared POSIX source-key contract."""
from pathlib import Path
import json,hashlib,os,subprocess,threading,time,re
H=Path(__file__).resolve().parent
C=H.parents[1]/'coder/d1android02-readonly-facts-preauth01'
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
ORIGINAL=subprocess.Popen
def sha(b):return hashlib.sha256(b).hexdigest()
def env_hash(e):return None if e is None else sha(json.dumps(e,sort_keys=True,separators=(',',':')).encode())
def relative_key(k):
 if type(k) is not str or not k or '\\' in k or k.startswith('/') or ':' in k or any(x in ('','.','..') for x in k.split('/')):raise ValueError('PIN_NONCANONICAL_RELATIVE_POSIX')
 if k.split('/')[0] not in ('candidate','driver'):raise ValueError('PIN_NAMESPACE')
 return k
def source_key(path):
 p=Path(path)
 if not p.is_absolute() or any(x in ('.','..') for x in str(path).replace('\\','/').split('/')) or p.absolute()!=p.resolve():raise ValueError('PIN_NONCANONICAL_PATH')
 for prefix,root in [('candidate',C),('driver',H)]:
  if p!=root and p.is_relative_to(root):return relative_key(prefix+'/'+p.relative_to(root).as_posix())
 raise ValueError('PIN_OUTSIDE_ROOT')
def resolve_key(key):
 key=relative_key(key);prefix,rel=key.split('/',1);root=C if prefix=='candidate' else H;p=root/rel
 if source_key(p)!=key:raise ValueError('PIN_ROUNDTRIP')
 return p
def pin_map(rows):
 out={};seen=set()
 for row in rows:
  key=relative_key(row['key'])
  if key.casefold() in seen:raise ValueError('PIN_DUPLICATE_OR_COLLISION')
  if type(row['sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row['sha256']) is None:raise ValueError('PIN_HASH_TYPE')
  seen.add(key.casefold());out[key]=row['sha256']
 return out
def options(k):
 if set(k)-{'stdin','stdout','stderr','executable','cwd','env','shell','close_fds'}:raise ValueError('PROFILE_KWARGS')
 return dict(stdin=k.get('stdin'),stdout=k.get('stdout'),stderr=k.get('stderr'),executable=k.get('executable'),cwd=k.get('cwd'),envSha256=env_hash(k.get('env')),shell=k.get('shell',False),close_fds=k.get('close_fds',True))
def tuple_key(argv,k):return sha(json.dumps(dict(argv=argv,options=options(k)),sort_keys=True,separators=(',',':')).encode())
class Registry:
 def __init__(self,p,start):
  self.p=p;self.start=start;self.calls=[];self.events=[];self.stop=False;self.local=threading.local();self.pins=pin_map(p['pinRows']);self.tuples={x['id']:x for x in p['tuples']}
  if len(self.tuples)!=len(p['tuples']):raise ValueError('PROFILE_DUPLICATE_TUPLE')
 def check(self,a,k,check_host=True):
  if type(a) is not list or not a or any(type(x) is not str for x in a) or a[0] not in (PY,PS):raise ValueError('PROFILE_PROGRAM_ARGV')
  if check_host and (str(Path.cwd())!=self.p['hostCwd'] or env_hash(dict(os.environ))!=self.p['inheritedEnvSha256']):raise ValueError('PROFILE_HOST_ENV_CWD')
  o=options(k)
  if o['shell'] is not False or o['close_fds'] is not True or o['stdin']!=subprocess.DEVNULL or o['stdout']!=subprocess.PIPE or o['stderr']!=subprocess.PIPE or o['executable'] not in (None,a[0]):raise ValueError('PROFILE_STREAMS_OPTIONS')
  prefix=['-I','-X','utf8','-B'] if a[0]==PY else ['-NoProfile','-NonInteractive','-File'];i=1+len(prefix)
  if a[1:i]!=prefix or len(a)<=i:raise ValueError('PROFILE_PREFIX')
  key=source_key(a[i])
  if key not in self.pins or sha(resolve_key(key).read_bytes())!=self.pins[key]:raise ValueError('PROFILE_SOURCE')
  tid=tuple_key(a,k)
  if tid not in self.tuples or self.tuples[tid]['sourceKey']!=key:raise ValueError('PROFILE_EXACT_TUPLE')
  return dict(argv=list(a),sourceKey=key,tupleId=tid,applicationName=k.get('executable'),commandLine=subprocess.list2cmdline(a),cwd=k.get('cwd'),envSha256=env_hash(k.get('env')))
 def construct(self,a,*pos,**k):
  if pos or self.stop or len(self.calls)>=64 or time.monotonic()-self.start>=240:raise ValueError('PROFILE_STOP_NEW')
  row=self.check(a,k);self.calls.append(row);self.local.expected=row
  try:p=ORIGINAL(a,**k);row['constructorReturned']=True;return p
  finally:self.local.expected=None
 def observe(self,event,args):
  if event!='subprocess.Popen':return
  try:
   row=getattr(self.local,'expected',None);ok=row is not None and len(args)==4 and args[0]==row['applicationName'] and args[1]==row['commandLine'] and args[2]==row['cwd'] and env_hash(args[3])==row['envSha256'];self.events.append(dict(matches=ok,applicationName=args[0],commandLine=args[1]))
   if not ok:self.stop=True
  except BaseException:self.stop=True;self.events.append(dict(matches=False,observerError=True))
