"""Single exact read-only ADB-shell collector. Import/default CLI cannot launch.

LIVE requires an already admitted original GateSession in this process, exact
prior coordinator authority and pins. It never discovers routes, retries,
falls back, releases an unknown original, or changes the seven-role run.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,os,threading,subprocess,time,sys,struct
B=Path(__file__).resolve().parents[1]
ENV=('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL','ADB_SERVER_ADDRESS')
SDK='D:/Android/SDK/platform-tools/adb.exe'
SDK_SHA='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f'
FIXTURE_PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def validate_fixture_argv(argv):
 expected=[FIXTURE_PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE']
 if type(argv) is not list or len(argv)!=7 or any(type(x) is not str for x in argv) or argv!=expected:raise ValueError('FACT_FIXTURE_ARGV')
 return list(expected)
def verify_fixture_runtime(gate):
 # Reuse the frozen 14-file runtime identity already verified by the original
 # gate; recheck the exact program+metadata before Popen, charging source reads.
 from runtime_binding import IDENTITY_SHA256
 meta=gate.source_read(B/'reference/current-runtime-identity.json')
 if sha(meta)!=IDENTITY_SHA256 or gate.policy.get('runtimeIdentitySha256')!=IDENTITY_SHA256 or gate.runtime.get('identitySha256')!=IDENTITY_SHA256:raise ValueError('FACT_FIXTURE_RUNTIME_METADATA')
 m=unique_json(meta);exe=[p for p in m['files'] if p['kind']=='interpreter-executable']
 if len(exe)!=1 or Path(m['executable']).resolve()!=Path(FIXTURE_PY).resolve() or Path(exe[0]['path']).resolve()!=Path(FIXTURE_PY).resolve() or Path(sys.executable).resolve()!=Path(FIXTURE_PY).resolve() or list(sys.version_info[:3])!=m['version'] or struct.calcsize('P')*8!=m['pointerBits'] or sys.platform!=m['platform'] or sys.implementation.name!=m['implementation'] or sys.implementation.cache_tag!=m['cacheTag']:raise ValueError('FACT_FIXTURE_RUNTIME_IDENTITY')
 raw=gate.source_read(FIXTURE_PY)
 if len(raw)!=exe[0]['bytes'] or sha(raw)!=exe[0]['sha256'] or gate.policy.get('outerPythonSha256')!=exe[0]['sha256']:raise ValueError('FACT_FIXTURE_EXECUTABLE_IDENTITY')
 return dict(identitySha256=IDENTITY_SHA256,programSha256=exe[0]['sha256'],sourceReadBytes=len(meta)+len(raw),sourceReads=2)
QUERIES=(('model','getprop ro.product.model'),('api','getprop ro.build.version.sdk'),('firmware','getprop ro.build.fingerprint'),('user','am get-current-user'),('system','cmd package list packages -s -U --user 0'),('role','dumpsys role'),('home','cmd package resolve-activity --brief --components --user 0 -a android.intent.action.MAIN -c android.intent.category.HOME'))
CUSTODY=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def script():
 # The trailing RS/status sentinel retains the query's trailing newlines in
 # shell substitution. Byte counts use LC_ALL=C, no shell evaluation of output.
 s="LC_ALL=C; export LC_ALL; sep=$(printf '\\036'); printf 'GI_FACTS_V1\\n'; "
 for ident,cmd in QUERIES:
  s+=f"a=$(date +%s); r=$({cmd} 2>&1; z=$?; printf '\\036%s' \"$z\"); b=$(date +%s); z=${{r##*\"$sep\"}}; o=${{r%\"$sep\"*}}; printf 'GI_ITEM|{ident}|%s|%s|%s|%s\\n' \"$z\" \"$a\" \"$b\" \"${{#o}}\"; printf '%s\\n' \"$o\"; "
 return s+"printf 'GI_FACTS_END\\n'"
def plan():return dict(schema='GLOBAL_IDLE_FACT_PLAN_V1',argv=[SDK,'-s','HA1Q6WXR','shell',script()],queries=[dict(id=i,command=c) for i,c in QUERIES],stdoutBytes=139264,stderrBytes=8192,combinedBytes=147456,qualificationSeconds=15,outerSeconds=30,proofSeconds=10,wholeSeconds=90,sdkChildren=1,concurrency=1,retry=0,itemClock='device date +%s; seconds; host monotonic also required',perQueryStderr='merged into that item output; global transport stderr must be empty',fallback=False)
def unique_json(raw):
 def pairs(p):
  d={}
  for k,v in p:
   if k.casefold() in {x.casefold() for x in d}:raise ValueError('DUPLICATE_JSON_FIELD')
   d[k]=v
  return d
 return json.loads(raw.decode('utf-8','strict'),object_pairs_hook=pairs)
def decode_wire(raw):
 if type(raw) is not bytes or not 1<=len(raw)<=139264:raise ValueError('FACT_RAW_BOUND')
 if not raw.startswith(b'GI_FACTS_V1\n'):raise ValueError('FACT_BEGIN')
 p=len(b'GI_FACTS_V1\n');items=[]
 for ident,_ in QUERIES:
  end=raw.find(b'\n',p,p+130)
  if end<0:raise ValueError('FACT_ITEM_HEADER')
  m=re.fullmatch(rb'GI_ITEM\|([a-z]+)\|([0-9]{1,3})\|([0-9]{1,12})\|([0-9]{1,12})\|([0-9]{1,6})',raw[p:end])
  if not m or m[1].decode()!=ident:raise ValueError('FACT_ORDER_OR_FRAME')
  status,a,b,n=map(int,m.groups()[1:]);p=end+1
  if status!=0 or not 0<=b-a<=15 or n>131072 or p+n>=len(raw) or raw[p+n:p+n+1]!=b'\n':raise ValueError('FACT_ITEM_STATUS_TIME_OR_BYTES')
  out=raw[p:p+n];text=out.decode('utf-8','strict')
  if re.search(r'[\x00-\x08\x0b-\x1f]',text):raise ValueError('FACT_CONTROL')
  if items and a<items[-1]['endEpochSeconds']:raise ValueError('FACT_CLOCK_REORDER')
  items.append(dict(id=ident,status=status,startEpochSeconds=a,endEpochSeconds=b,bytes=n,sha256=sha(out),output=text));p+=n+1
 if raw[p:]!=b'GI_FACTS_END\n' or items[-1]['endEpochSeconds']-items[0]['startEpochSeconds']>15:raise ValueError('FACT_END_OR_DURATION')
 return items
def role_tree(text):
 lines=text.splitlines()
 if not lines or lines.pop(0)!='ROLE STATE (dumpsys role):':raise ValueError('ROLE_DUMP_HEADER')
 lines=[x.strip() for x in lines if x.strip()];pos=0
 def node(kind,depth=0):
  nonlocal pos
  if depth>8:raise ValueError('ROLE_DEPTH')
  out={} if kind=='{' else [];close='}' if kind=='{' else ']'
  while pos<len(lines):
   line=lines[pos];pos+=1
   if line==close:return out
   if line in ('}',']'):raise ValueError('ROLE_BRACKET')
   if kind=='{':
    m=re.fullmatch(r'([a-z_]+)=(.*)',line)
    if not m or m[1] in out:raise ValueError('ROLE_FIELD')
    out[m[1]]=node(m[2],depth+1) if m[2] in ('{','[') else m[2]
   else:out.append(node(line,depth+1) if line in ('{','[') else line)
  raise ValueError('ROLE_INCOMPLETE')
 if not lines or lines[0]!='{':raise ValueError('ROLE_ROOT')
 pos=1;root=node('{')
 if pos!=len(lines) or set(root)!={'user_states'}:raise ValueError('ROLE_ROOT_SCHEMA')
 users=root['user_states'];users=users if type(users) is list else [users];found=[];seen=set()
 for u in users:
  if type(u) is not dict or set(u)!={'user_id','version','packages_hash','roles'} or not re.fullmatch(r'[0-9]+',u['user_id']) or u['user_id'] in seen:raise ValueError('ROLE_USER_SCHEMA')
  seen.add(u['user_id']);roles=u['roles'];roles=roles if type(roles) is list else [roles];names=set()
  for r in roles:
   if type(r) is not dict or not {'name'}<=set(r)<= {'name','holders'} or r['name'] in names:raise ValueError('ROLE_SCHEMA')
   names.add(r['name']);holders=r.get('holders',[]);holders=holders if type(holders) is list else [holders]
   if u['user_id']=='0' and r['name']=='android.app.role.HOME':found.append(holders)
 if len(found)!=1 or len(found[0])!=1 or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+',found[0][0]):raise ValueError('ROLE_HOME_NOT_UNIQUE')
 return found[0][0]
def facts(raw):
 items=decode_wire(raw);d={v['id']:v['output'].strip() for v in items}
 if d['model']!='TB138FC' or d['api']!='31' or d['user']!='0' or not 8<=len(d['firmware'])<=256 or '\n' in d['firmware']:raise ValueError('FACT_DEVICE')
 packages=[];seen=set()
 for line in d['system'].splitlines():
  m=re.fullmatch(r'package:([A-Za-z_][A-Za-z0-9_.]*) uid:([0-9]+)',line)
  if not m or m[1] in seen or int(m[2])>2147483647:raise ValueError('SYSTEM_UID_SCHEMA')
  seen.add(m[1]);packages.append(dict(package=m[1],uid=int(m[2]),systemFlag=True))
 home=role_tree(d['role']);component=d['home']
 if not re.fullmatch(re.escape(home)+r'/\.?[A-Za-z_][A-Za-z0-9_.]*',component):raise ValueError('HOME_RESOLVER_DISAGREES')
 uid=[p['uid'] for p in packages if p['package']==home]
 if len(uid)!=1 or not 10000<=uid[0]<100000:raise ValueError('HOME_SYSTEM_UID_UNPROVEN')
 activity=component.split('/')[1];activity=home+activity if activity.startswith('.') else activity
 return dict(items=items,model=d['model'],api=31,fingerprint=d['firmware'],user=0,systemPackages=packages,homeRolePackage=home,homeComponent=activity,homeUid=uid[0])
class OwnedFactCapture:
 def __init__(self):
  self.held=[];self.failure=None;self.next=0;self.entered=False;self.returned=False;self.unknown=False
 def collect(self,authority,gate,approved_authority_sha256,fixture_argv=None,approval=None,approved_approval_sha256=None):
  """Caller is the original outer owner. Return is not its own return proof.

  gate is the original prepared local route/claim object, never a file stand-in.
  Fixture override is confined to OFFLINE_FIXTURE and cannot select ADB.
  """
  if self.entered:raise ValueError('FACT_ONCE')
  from entry_gates import GateSession,encode
  if type(gate) is not GateSession or not gate.prepared or gate.accepted or gate.sdk_owner is not None:raise ValueError('FACT_ORIGINAL_GATE_REQUIRED')
  if sha(encode(authority))!=approved_authority_sha256:raise ValueError('FACT_PRIOR_APPROVAL_HASH')
  ak={'schema','mode','sourceThreadId','sourceTurnId','approvedAuthoritySha256','instructionText','instructionSha256'}
  instruction='EXECUTE_READONLY_FACTS '+approved_authority_sha256
  if type(approval) is not dict or set(approval)!=ak or sha(encode(approval))!=approved_approval_sha256 or approval['schema']!='GLOBAL_IDLE_FACT_APPROVAL_V1' or approval['mode']!=authority.get('mode') or approval['sourceThreadId']!='01a107c3-2bf9-7fa0-94a0-234258ca6774' or approval['approvedAuthoritySha256']!=approved_authority_sha256 or approval['instructionText']!=instruction or approval['instructionSha256']!=sha(instruction.encode()):raise ValueError('FACT_EXTERNAL_APPROVAL_CHAIN')
  keys={'schema','approvedForExecution','scope','planId','mode','notBeforeUtc','expiresUtc','collectorSha256','planSha256','routeProofSha256','sourceThreadId','sourceTurnId'}
  if type(authority) is not dict or set(authority)!=keys or authority['schema']!='GLOBAL_IDLE_FACT_AUTHORITY_V1' or authority['approvedForExecution'] is not True or authority['sourceThreadId']!='01a107c3-2bf9-7fa0-94a0-234258ca6774':raise ValueError('FACT_AUTHORITY')
  if authority['scope']!=gate.scope or authority['planId']!=gate.policy['planId'] or authority['mode']!=('OFFLINE_FIXTURE' if gate.fixture else 'LIVE') or authority['collectorSha256']!=sha(gate.source_read(Path(__file__))) or authority['planSha256']!=sha(gate.source_read(B/'reference/fact-plan.json')):raise ValueError('FACT_SCOPE_SOURCE_MODE')
  if authority['routeProofSha256']!=unique_json(gate.receipt_bytes)['routeSha256']:raise ValueError('FACT_ROUTE_HASH')
  lo=datetime.fromisoformat(authority['notBeforeUtc']);hi=datetime.fromisoformat(authority['expiresUtc']);now=datetime.now(timezone.utc)
  if not lo<=now<hi or not 0<(hi-lo).total_seconds()<=90:raise ValueError('FACT_AUTHORITY_STALE')
  return self._capture_authorized(gate,fixture_argv,authority['mode'],hi,authority['collectorSha256'],authority['planSha256'],authority['routeProofSha256'],dict(authoritySha256=approved_authority_sha256,approvalSha256=approved_approval_sha256))
 def _capture_authorized(self,gate,fixture_argv,mode,hi,source_sha,plan_sha,route_sha,authorization):
  # Shared original capture, never manufacture legacy authority/approval.
  if self.entered:raise ValueError('FACT_ONCE')
  if any(k in os.environ for k in ENV):raise ValueError('FACT_INHERITED_ENV_OVERRIDE')
  argv=plan()['argv']
  if fixture_argv is not None:
   if not gate.fixture:raise ValueError('FACT_FIXTURE_ARGV')
   argv=validate_fixture_argv(fixture_argv)
   self.fixtureRuntime=verify_fixture_runtime(gate)
  elif gate.fixture:raise ValueError('FACT_FIXTURE_REQUIRED_NO_ADB')
  else:
   if sha(gate.source_read(SDK))!=SDK_SHA:raise ValueError('FACT_SDK_PIN')
  gate.receive(gate.policy,gate.manifest_hash);gate.sdk_owner=self;gate.before_role(self)
  self.gate=gate;self.entered=True;CUSTODY.append(self);start=time.monotonic();self.captureStart=start;self.startedUtc=datetime.now(timezone.utc).isoformat();self.buf=[bytearray(),bytearray()];self.counts=[0,0];self.eof=[False,False];self.closed=[False,False]
  try:p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
  except BaseException:
   self.unknown=True;self.failure='FACT_START_UNKNOWN';raise
  self.process=p;self.next=1;self.held.append(p)
  def read(i,stream,cap):
   try:
    while True:
     b=stream.read(4096)
     if not b:self.eof[i]=True;break
     self.counts[i]+=len(b)
     if self.counts[i]<=cap:self.buf[i].extend(b)
     else:self.failure='FACT_OUTPUT_BOUND'
    stream.close();self.closed[i]=True
   except BaseException:self.unknown=True;self.failure='FACT_ORIGINAL_PIPE_UNKNOWN'
  threads=[threading.Thread(target=read,args=(i,s,cap)) for i,s,cap in ((0,p.stdout,139264),(1,p.stderr,8192))];self.held.extend(threads)
  for t in threads:t.start()
  while p.poll() is None or any(t.is_alive() for t in threads):
   if time.monotonic()-start>=15:self.failure=self.failure or 'FACT_QUALIFICATION_EXPIRED'
   # No termination/second close. Original objects remain in CUSTODY.
   time.sleep(.005)
  for t in threads:t.join()
  code=p.wait();self.waitReturned=True
  try:p._handle.Close() if os.name=='nt' else None;self.handleClosed=True
  except BaseException:self.unknown=True;self.failure='FACT_ORIGINAL_HANDLE_UNKNOWN';raise
  self.elapsed=time.monotonic()-start
  self.bodyReturned=not self.unknown and all(self.eof+self.closed) and self.handleClosed
  self.bodyReturnTick=time.monotonic()
  if code or self.counts[1] or self.elapsed>=15 or not self.bodyReturned or datetime.now(timezone.utc)>=hi or time.monotonic()-gate.start>=90:self.failure=self.failure or 'FACT_CAPTURE_UNQUALIFIED'
  if self.failure:raise ValueError(self.failure)
  raw=bytes(self.buf[0]);parsed=facts(raw);self.returned=True
  receipt=dict(schema='GLOBAL_IDLE_FACT_CAPTURE_V1',scope=gate.scope,mode=mode,sourceSha256=source_sha,planSha256=plan_sha,routeProofSha256=route_sha,initialProofSha256=gate.proof_hash,hostEnvironment='INHERITED_SEVEN_OVERRIDES_ABSENT',rawSha256=sha(raw),rawBytes=len(raw),stdoutBytes=self.counts[0],stderrBytes=self.counts[1],hostElapsedSeconds=self.elapsed,collectedAtUtc=self.startedUtc,originalBodyReturned=True,outerControllerReturnStillRequired=True,facts=parsed)
  receipt.update(authorization);return receipt
 def finish_after_original_collect_return(self,gate):
  if gate is not getattr(self,'gate',None) or not getattr(self,'bodyReturned',False) or self.unknown or any(isinstance(x,threading.Thread) and x.is_alive() for x in self.held):raise ValueError('FACT_NO_RELEASE_WITH_UNKNOWN')
  # Known original resources are released even after a deadline; expiry never
  # licenses a second close or converts a late result to qualified success.
  r=gate.release();now=time.monotonic();timely=now-self.bodyReturnTick<10 and now-self.captureStart<30 and now-gate.start<90
  r.update(factProofTimely=timely,factCaptureQualified=self.failure is None and timely,outerControllerReturnStillRequired=True)
  CUSTODY.remove(self);return r
if __name__=='__main__':raise SystemExit('NO_IMPLICIT_FACT_EXECUTION: prior scope, authority, original gate and owner required')
