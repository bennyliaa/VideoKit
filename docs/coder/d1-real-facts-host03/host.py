"""One original facts-entry Capture, archive only. Default and drafts deny.

Uses exact Q07 REV2 Capture/origin/Journal/FactsBundle; no replacement wait,
close, qualification issuer, route probe, or service is implemented here.
"""
from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,hashlib,threading,subprocess,time,copy,uuid,re
H=Path(__file__).resolve().parent
S=Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-facts-v2-qualification07/rev2')
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
SEAL='0db36468464dcfb92c2da87de8d6bff678b09af173bb21b41ed9e3d4d58157de'
GATE='ba8fbd645e4c8403525c111ba2943cb81f3fbf6fbfc11a9f6d7c7c5a49026f81'
SDK_SHA='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f'
PROBE_SHA='d49ee2f675263186de11a3825b530a5612ed2f3cc09cd3969b765da7647efb7a'
TESTER_ROOT=Path('D:/CodexProjects/VideoKit/docs/tester/D1_REAL_FACTS_HOST03_INDEPENDENT_B_EVIDENCE')
OVERRIDES=('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL','ADB_SERVER_ADDRESS')
ORIGINAL=subprocess.Popen;PENDING=[];BATCH_CONTROL=None
def enc(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()

def require_pin(value,label):
 if type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None or value=='0'*64:raise ValueError('REQUIRED_PIN:'+label)
 return value
def exact(d,keys,reason):
 if type(d) is not dict or set(d)!=set(keys):raise ValueError(reason)
def no_links(path):
 p=Path(path)
 if not p.is_absolute() or str(p)!=str(p.resolve()):raise ValueError('CANONICAL_PATH')
 for q in [p,*p.parents]:
  if q.exists() and q.stat().st_file_attributes&1024:raise ValueError('REPARSE_PATH')
def env_hash():return sha(enc(dict(os.environ)))
class Budget:
 def __init__(self):self.readReserved=0;self.savedReserved=0;self.reads=[];self.writes=[]
 def reserve_read(self,n,label):
  if type(n) is not int or n<0 or self.readReserved+n>268435456:raise ValueError('HOST_READ_BUDGET_BEFORE_OPEN')
  self.readReserved+=n;row=dict(label=label,reserved=n,kind='FINITE_RESERVATION',actual=None,originalCloseReturned=None);self.reads.append(row);return row
 def reserve_write(self,n,label):
  if type(n) is not int or n<0 or self.savedReserved+n>4194304:raise ValueError('HOST_WRITE_BUDGET_BEFORE_OPEN')
  self.savedReserved+=n;row=dict(label=label,reserved=n,kind='FINITE_RESERVATION',originalCloseReturned=None);self.writes.append(row);return row
 def read(self,path,cap,digest=None):
  p=Path(path);no_links(p);n=p.stat().st_size
  if n>cap:raise ValueError('INPUT_FILE_CAP_BEFORE_OPEN')
  row=self.reserve_read(n+1,str(p));row.update(kind='ORIGINAL_FILE_READ',originalCloseReturned=False);f=None
  try:
   f=p.open('rb');before=os.fstat(f.fileno())
   try:b=f.read(n+1)
   except OSError:PENDING.append((f,row));row['readAmountUnknown']=True;retain('ORIGINAL_INPUT_READ_UNKNOWN')
   after=os.fstat(f.fileno());row['actual']=len(b)
   if (before.st_dev,before.st_ino,before.st_size)!=(after.st_dev,after.st_ino,after.st_size) or after.st_ino!=p.stat().st_ino or len(b)!=n:raise ValueError('ORIGINAL_INPUT_IDENTITY_OR_SIZE')
   row.update(identity=dict(kind='ORIGINAL_HANDLE_FSTAT',device=before.st_dev,fileId=before.st_ino,bytes=before.st_size),sha256=sha(b))
  finally:
   if f is not None:
    try:f.close();row['originalCloseReturned']=True
    except BaseException:
     PENDING.append((f,row));retain('ORIGINAL_INPUT_CLOSE_UNKNOWN')
  if digest is not None and sha(b)!=digest:raise ValueError('ORIGINAL_INPUT_HASH')
  return b
 def read_pinned(self,path,cap,digest):
  # Mandatory expectations never inherit read()'s optional None semantics.
  return self.read(path,cap,require_pin(digest,'expectedSha256'))
 def read_ref(self,ref,core):
  require_pin(ref['sha256'],'approvedRefSha256')
  p=Path(ref['path']);no_links(p);row=self.reserve_read(ref['bytes']+1,str(p));row.update(kind='ORIGINAL_APPROVED_FILE_READ',originalCloseReturned=False);event=None
  try:
   with core['file'].original_file(p,'rb') as f:
    event=core['file'].ORIGINAL_FILE_EVENTS[-1];before=core['file'].identity(f,p)
    if any(str(before[k])!=str(ref[k]) for k in ('bytes','volumeId','fileId')):raise ValueError('APPROVED_INPUT_FILE_IDENTITY')
    try:b=f.read(ref['bytes']+1)
    except OSError:PENDING.append((f,row));row['readAmountUnknown']=True;retain('ORIGINAL_APPROVED_INPUT_READ_UNKNOWN')
    after=core['file'].identity(f,p);row.update(actual=len(b),identity=before,identityAfter=after,sha256=sha(b))
    if before!=after or len(b)!=ref['bytes'] or sha(b)!=ref['sha256']:raise ValueError('ORIGINAL_APPROVED_INPUT_BYTES')
  finally:
   row['originalCloseReturned']=event is not None and event['closeReturned']
  return b
 def write(self,path,b):
  p=Path(path);no_links(p);row=self.reserve_write(len(b),str(p));row.update(kind='ORIGINAL_ARCHIVE_WRITE',originalCloseReturned=False);f=None
  try:
   f=p.open('xb');n=f.write(b);row['actual']=n
   if n!=len(b):retain('ORIGINAL_ARCHIVE_SHORT_WRITE')
   f.flush()
  except OSError:
   if f is not None:retain('ORIGINAL_ARCHIVE_WRITE_UNKNOWN')
   raise
  finally:
   if f is not None:
    try:f.close();row['originalCloseReturned']=True
    except BaseException:PENDING.append((f,row));retain('ORIGINAL_ARCHIVE_CLOSE_UNKNOWN')
def retain(reason):
 PENDING.append(reason)
 if BATCH_CONTROL is not None:BATCH_CONTROL.request(reason)
 while True:time.sleep(.1)
def decode(b,cap=65536):
 if not 1<=len(b)<=cap:raise ValueError('CONFIG_BYTES')
 def pairs(rows):
  d={}
  for k,v in rows:
   if k.casefold() in {s.casefold() for s in d}:raise ValueError('DUPLICATE_JSON')
   d[k]=v
  return d
 return json.loads(b.decode('utf-8','strict'),object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
def utc(s):
 if type(s) is not str:raise ValueError('TIME_REQUIRED')
 t=datetime.fromisoformat(s.replace('Z','+00:00'))
 if t.tzinfo is None:raise ValueError('TIME_ZONE')
 return t.astimezone(timezone.utc)
COMMON=set('schema mode approvedForExecution sourceRoot sourceSealSha256 hostSourceSha256 cwd envSha256 outputRoot'.split())
LIVE_KEYS=COMMON|set('authorizationSource scope planId notBeforeUtc expiresUtc nativeRouteApproved sdkChildren templateRef policyRef localAuthorizationRef'.split())
PROBE_KEYS=COMMON|{'probeMode','probeSha256'}

def offline_output_allowed(value):
 # Exactly two namespaces and one declared scope + fixed mode leaf. A tester
 # can freeze its own scope without modifying H/S or the original fixture gate.
 if type(value) is not str or any(s in ('.','..') for s in value.replace('/','\\').split('\\')):return False
 p=Path(value)
 if str(p)!=value:return False # reject mixed slashes and normalization aliases
 try:no_links(value)
 except (ValueError,OSError):return False
 for base in (H/'selfchecks/work',TESTER_ROOT/'fixtures'):
  if not p.is_relative_to(base):continue
  parts=p.relative_to(base).parts
  if len(parts)!=2 or re.fullmatch(r'(?:[0-9a-f]{10}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})',parts[0]) is None:return False
  return parts[1] in ('ok','fail','empty','bad','over')
 return False

def validate_scope(config,template,policy,local_auth):
 # Pure pre-resource obligation. Uses policy.entry (capture_android02), never
 # template.entry (facts_entry). Does not repair any approved field or scope.
 if any(type(x) is not dict for x in (config,template,policy,local_auth)):raise ValueError('HOST_SCOPE_OBJECT_TYPES')
 for k in ('planId','entrySha256','productSealSha256','planSha256','runId'):
  if type(policy.get(k)) is not str:raise ValueError('HOST_SCOPE_FIELD_TYPE:'+k)
 pid=policy['planId']
 try:valid=str(uuid.UUID(pid))==pid
 except (ValueError,AttributeError):valid=False
 if not valid:raise ValueError('HOST_SCOPE_PLAN_ID')
 if re.fullmatch(r'D1MA02-[A-Z0-9_-]{1,32}',policy['runId']) is None:raise ValueError('HOST_SCOPE_RUN_ID')
 for k in ('entrySha256','productSealSha256','planSha256'):
  if re.fullmatch('[0-9a-f]{64}',policy[k]) is None or policy[k]=='0'*64:raise ValueError('HOST_SCOPE_FIELD_HASH:'+k)
 if type(template.get('entrySha256')) is not str or re.fullmatch('[0-9a-f]{64}',template['entrySha256']) is None or template['entrySha256']=='0'*64:raise ValueError('HOST_SCOPE_PREAUTH_ENTRY')
 for label,d in (('config',config),('template',template),('policy',policy),('localAuth',local_auth)):
  if type(d.get('scope')) is not str or re.fullmatch('[0-9a-f]{64}',d['scope']) is None or d['scope']=='0'*64:raise ValueError('HOST_SCOPE_VALUE:'+label)
  if d.get('planId')!=pid or type(d.get('planId')) is not str:raise ValueError('HOST_SCOPE_PLAN_BINDING:'+label)
 if template.get('runId')!=policy['runId'] or local_auth.get('entrySha256')!=policy['entrySha256']:raise ValueError('HOST_SCOPE_ORIGINAL_FIELD_BINDING')
 expected=sha('|'.join(policy[k] for k in ('planId','entrySha256','productSealSha256','planSha256','runId')).encode('utf-8'))
 if any(d['scope']!=expected for d in (config,template,policy,local_auth)):raise ValueError('HOST_SCOPE_FORMULA')
 return expected
def static_config(c):
 if c.get('schema')=='REAL_FACTS_HOST01_DRAFT_V1' or c.get('approvedForExecution') is not True:raise ValueError('CONFIG_NOT_APPROVED')
 mode=c.get('mode');exact(c,LIVE_KEYS if mode=='LIVE' else PROBE_KEYS if mode=='OFFLINE_HOST_PROBE' else set(),'CONFIG_EXACT_SCHEMA')
 if mode not in ('LIVE','OFFLINE_HOST_PROBE'):raise ValueError('MODE_DENIED')
 if c['schema']!=('REAL_FACTS_HOST01_LIVE_CONFIG_V1' if mode=='LIVE' else 'REAL_FACTS_HOST01_OFFLINE_PROBE_V1'):raise ValueError('CONFIG_SCHEMA_VALUE')
 require_pin(c['hostSourceSha256'],'hostSourceSha256')
 if c['sourceRoot']!=str(S) or c['sourceSealSha256']!=SEAL:raise ValueError('EXACT_Q07_SOURCE_REQUIRED')
 if c['cwd']!=str(Path('D:/CodexProjects/VideoKit')) or c['envSha256']!=env_hash():raise ValueError('HOST_CONTEXT')
 if str(Path(sys.executable).resolve())!=str(Path(PY).resolve()):raise ValueError('FIXED_PYTHON')
 if any(k in os.environ for k in OVERRIDES):raise ValueError('INHERITED_ROUTING_OVERRIDE')
 no_links(c['outputRoot'])
 if mode=='LIVE':
  if c['nativeRouteApproved'] is not True or type(c['sdkChildren']) is not int or c['sdkChildren']!=1:raise ValueError('EXPLICIT_NATIVE_AND_ONE_SDK_REQUIRED')
  exact(c['authorizationSource'],{'threadId','turnId'},'AUTH_SOURCE_SCHEMA')
  if c['authorizationSource']['threadId']!='01a107c3-2bf9-7fa0-94a0-234258ca6774' or str(uuid.UUID(c['authorizationSource']['turnId']))!=c['authorizationSource']['turnId']:raise ValueError('AUTH_SOURCE')
  if str(uuid.UUID(c['planId']))!=c['planId'] or type(c['scope']) is not str or len(c['scope'])!=64 or any(x not in '0123456789abcdef' for x in c['scope']):raise ValueError('LIVE_SCOPE')
  lo=utc(c['notBeforeUtc']);hi=utc(c['expiresUtc']);now=datetime.now(timezone.utc)
  if not 0<(hi-lo).total_seconds()<=90 or not lo<=now<hi:raise ValueError('CONFIG_TIME_WINDOW')
  base=Path('D:/CodexProjects/VideoKit/docs/tester/D1_REAL_FACTS_HOST01_EXECUTION')/c['planId']
  if Path(c['outputRoot'])!=base/'outer':raise ValueError('LIVE_OUTER_NEW_ROOT')
  for field,name in (('templateRef','facts-preauth.json'),('policyRef','facts-policy.json'),('localAuthorizationRef','gate-local-authorization.json')):
   ref=c[field];exact(ref,{'path','bytes','sha256','volumeId','fileId'},'ORIGINAL_INPUT_REFERENCE_SCHEMA')
   if ref['path']!=str(base/'inputs'/name) or type(ref['bytes']) is not int or not 1<=ref['bytes']<=16384 or type(ref['sha256']) is not str or len(ref['sha256'])!=64 or any(x not in '0123456789abcdef' for x in ref['sha256']):raise ValueError('LIVE_INPUT_REFERENCE')
   require_pin(ref['sha256'],'approvedRefSha256')
   for k,maximum,minimum in (('volumeId',4294967295,0),('fileId',18446744073709551615,1)):
    v=ref[k]
    if type(v) is not str or not v.isascii() or not v.isdigit() or str(int(v))!=v or not minimum<=int(v)<=maximum:raise ValueError('LIVE_INPUT_REFERENCE_ID_TYPE')
 else:
  if c['probeMode'] not in ('ok','fail','empty','bad','over') or not offline_output_allowed(c['outputRoot']) or Path(c['outputRoot']).name!=c['probeMode']:raise ValueError('OFFLINE_PROBE_ONLY')
  if c['probeSha256']!=PROBE_SHA:raise ValueError('FIXED_PROBE_HASH')
 return c
def load_core(budget):
 manifest=budget.read_pinned(S/'reference/runner-source-seal.json',16384,SEAL);sources=decode(manifest)['sources']
 if len(sources)!=30:raise ValueError('SOURCE_SET30')
 content={}
 for rel,pin in sources.items():content[rel]=budget.read_pinned(S/rel,1048576,pin)
 if sha(content['reference/gate-sources.json'])!=GATE:raise ValueError('GATE_PIN')
 sys.path.insert(0,str(S/'tools'))
 import outer_capture,capture_origin,evidence_io,facts_qualification,immutable_evidence,runtime_binding
 for m in (outer_capture,capture_origin,evidence_io,facts_qualification,immutable_evidence,runtime_binding):
  if Path(m.__file__).resolve().parent!=S/'tools':raise ValueError('IMPORTED_MODULE_SOURCE')
 return dict(Capture=outer_capture.Capture,origin=capture_origin,Journal=evidence_io.Journal,FactsBundle=facts_qualification.FactsBundle,file=immutable_evidence,runtime=runtime_binding,custody=outer_capture.CUSTODY,contents=content,sealBytes=manifest)
class Control:
 def __init__(self):self.stop=False;self.reasons=[]
 def request(self,reason):self.stop=True;self.reasons.append(str(reason))
 def poll(self):return self.stop
 def returned(self):return True # no control IO/RPC exists; actual memory-only object
class Registry:
 def __init__(self,spec,check_inputs,control):
  self.spec=copy.deepcopy(spec);self.owner=(os.getpid(),threading.get_ident());self.check_inputs=check_inputs;self.control=control;self.events=[];self.entered=False;self.returned=False;self.active=False;self.expected=None;self.granted=False
 def check(self,a,k):
  if (os.getpid(),threading.get_ident())!=self.owner or self.entered or self.control.stop:raise ValueError('HOST_OWNER_ONCE_OR_STOP')
  if a!=self.spec['argv'] or k!=self.spec['kwargs']:raise ValueError('EXACT_ACTUAL_CALL_SPEC')
  self.check_inputs();self.granted=True;return True
 def construct(self,a,*pos,**k):
  # Capture.launch already performed the original recheck. Execute only the
  # frozen admitted tuple; no source IO or approval decision inside Popen.
  if not self.granted or self.entered or pos or a!=self.spec['argv'] or k!=self.spec['kwargs']:raise ValueError('UNADMITTED_OR_CHANGED_CONSTRUCTOR_CALL')
  self.entered=True;self.active=True;self.expected=(self.spec['kwargs']['executable'],subprocess.list2cmdline(self.spec['argv']),self.spec['kwargs']['cwd'],None)
  try:p=ORIGINAL(self.spec['argv'],**self.spec['kwargs']);self.returned=True;return p
  finally:self.active=False
 def observe(self,event,args):
  if event!='subprocess.Popen' or not self.active:return
  # Observation never throws into the original constructor.
  try:ok=self.active and type(args) is tuple and args==self.expected
  except BaseException:ok=False
  self.events.append(dict(matches=ok,originalConstructorEntered=self.entered))
  if not ok:self.control.request('UNEXPECTED_ORIGINAL_POPEN_AUDIT')
def spec_for(c):
 if c['mode']=='LIVE':argv=[PY,'-I','-X','utf8','-B',str(S/'tools/facts_entry.py'),'--template',c['templateRef']['path'],'--approved-template-sha256',c['templateRef']['sha256'],'--policy',c['policyRef']['path']]
 else:argv=[PY,'-I','-X','utf8','-B',str(H/'selfchecks/probe.py'),c['probeMode']]
 if len(enc(argv))>4096:raise ValueError('HOST_ARGV_BUDGET')
 return dict(argv=argv,kwargs=dict(executable=PY,cwd=c['cwd'],env=None,shell=False,close_fds=True,stdin=-3,stdout=-1,stderr=-1))
def verify_inputs(c,budget,core):
 if env_hash()!=c['envSha256']:raise ValueError('HOST_ENV_CHANGED')
 budget.read_pinned(Path(__file__),262144,c['hostSourceSha256'])
 if c['mode']=='OFFLINE_HOST_PROBE':budget.read_pinned(H/'selfchecks/probe.py',16384,PROBE_SHA);return None
 static_config(c)
 values={}
 for k in ('templateRef','policyRef','localAuthorizationRef'):
  ref=c[k];values[k]=budget.read_ref(ref,core)
 from fact_preauth import validate,load_pins
 p=decode(values['policyRef'],16384);t=decode(values['templateRef'],16384)
 if values['policyRef']!=enc(p) or t['mode']!='LIVE' or p['mode']!='PRODUCTION' or t['scope']!=c['scope'] or t['planId']!=c['planId'] or t['sourceTurnId']!=c['authorizationSource']['turnId'] or t['notBeforeUtc']!=c['notBeforeUtc'] or t['expiresUtc']!=c['expiresUtc']:raise ValueError('ORIGINAL_LIVE_INPUT_BINDING')
 if p['gateAuthorization']!={'path':c['localAuthorizationRef']['path'],'sha256':c['localAuthorizationRef']['sha256']}:raise ValueError('LOCAL_AUTH_REFERENCE')
 auth=decode(values['localAuthorizationRef'],16384)
 validate_scope(c,t,p,auth) # before SDK file IO, runtime, Journal/Capture/Gate/Native
 expected=dict(schema='ENTRY_GATES_LOCAL_AUTH_V2',scope=t['scope'],planId=t['planId'],entrySha256=p['entrySha256'],gateSourcesSha256=p['gateSourcesSha256'],approvedForLocalMetadata=True,routeBackend='WIN32_OWNER_PID_V1')
 if auth!=expected or auth.get('approvedForLocalMetadata') is not True:raise ValueError('LOCAL_AUTH_EXACT_APPROVAL')
 pins=load_pins(lambda path:pinned_seal_read(path,budget));validate(values['templateRef'],c['templateRef']['sha256'],p,pins)
 if p['evidenceRoot']!=str(Path('D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION')/c['planId']/'outputs'):raise ValueError('ORIGINAL_LIVE_FACT_ROOT')
 budget.read_pinned('D:/Android/SDK/platform-tools/adb.exe',8273560,SDK_SHA)
 from fact_preauth import complete_source_plan,FACT_RUNTIME_FILES06
 sizes={str(S/rel):len(b) for rel,b in core['contents'].items()};sizes[str(S/'reference/runner-source-seal.json')]=len(core['sealBytes']);sizes.update({str(Path(x['path'])):x['bytes'] for x in FACT_RUNTIME_FILES06});sizes[c['localAuthorizationRef']['path']]=len(values['localAuthorizationRef']);sizes[str(Path('D:/Android/SDK/platform-tools/adb.exe'))]=8273560
 source_plan=complete_source_plan(p,decode(core['contents']['reference/gate-sources.json'])['files'],FACT_RUNTIME_FILES06,sizes)
 if source_plan['sourceReads']!=58:raise ValueError('EXACT_LIVE_SOURCE_PLAN58')
 values['sourcePlan']=source_plan
 return values

def pinned_seal_read(path,budget):
 expected=S/'reference/runner-source-seal.json'
 if Path(path)!=expected:raise ValueError('PINNED_SEAL_READER_PATH')
 return budget.read_pinned(expected,16384,SEAL)
def run(c,budget):
 global BATCH_CONTROL
 static_config(c);core=load_core(budget);inputs=verify_inputs(c,budget,core);spec=spec_for(c);control=Control();BATCH_CONTROL=control
 registry=Registry(spec,lambda:verify_inputs(c,budget,core),control)
 budget.registry=registry
 registry.check(spec['argv'],spec['kwargs']) # before Journal/Capture factories
 root=Path(c['outputRoot'])
 if root.exists():raise ValueError('FRESH_OUTER_OUTPUT_REQUIRED')
 budget.reserve_write(600000,'original-Journal-finite-capture-reservation')
 root.mkdir(parents=True,exist_ok=False);journal=core['Journal'](root)
 runtime_meta=decode(core['contents']['reference/current-runtime-identity.json']);n=2*len(core['contents']['reference/current-runtime-identity.json'])+sum(x['bytes'] for x in runtime_meta['files'])
 runtime_fee=budget.reserve_read(n,'fixed-original-runtime-helper-16-reservation')
 policy={'runtimeIdentitySha256':'2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48','outerPythonSha256':next(x['sha256'] for x in runtime_meta['files'] if x['kind']=='interpreter-executable')}
 runtime_fact=core['runtime'].require_runtime(policy,'real-facts-host01-before-Capture');runtime_fee['fixedHelperReturned']=True
 plan=dict(argv=spec['argv'],cwd=spec['kwargs']['cwd'],env=None,profile='live-facts-archive-only' if c['mode']=='LIVE' else 'offline-host-probe')
 capture=core['Capture'](plan,copy.deepcopy(plan),journal,control,registry)
 budget.capture=capture
 sys.addaudithook(registry.observe)
 try:
  try:capture.launch(registry,30)
  except BaseException:
   if capture.facts['phase']=='PREFLIGHT' and not registry.entered:
    capture.facts['preflightRejected']=True;capture.facts['otherEvidenceReturned']=journal.returned() and control.returned()
   else:raise
  disposition=capture.collect()
  if not registry.entered and disposition=='FAIL_CLEAN_NO_CONSTRUCTOR':
   result=dict(status='KNOWN_PRECONSTRUCTOR_REJECTED',approved=False,qualificationIssued=False,originalPopenEntered=False,disposition=disposition,facts=capture.facts,journal=journal.facts(),custody=len(core['custody']))
   budget.write(root/'known-preconstructor-return.json',enc(result));return result
  if disposition.startswith('RETAIN') or not capture.returned:retain('ORIGINAL_CAPTURE_RETAINED:'+disposition)
  identity=getattr(capture,'identity',None)
  returned=dict(schema='REAL_FACTS_HOST01_ORIGINAL_RETURN_V1',mode=c['mode'],scope=c.get('scope'),exitCode=capture.exit_code,returned=capture.returned,facts=capture.facts,identity=identity,pipeCounts=capture.counts,capturedCounts=[len(b) for b in capture.buffers],pipeAmountUnknown=capture.pipe_amount_unknown,truncated=capture.counts!=[len(b) for b in capture.buffers],disposition=disposition,failure=capture.failure,audit=list(registry.events),originalPopenEntered=registry.entered,originalPopenReturned=registry.returned,journal=journal.facts(),runtime=runtime_fact,selfOwnedHandleMetadata=dict(GetProcessTimes=1 if identity else None,QueryFullProcessImageNameW=1 if identity else None,GetProcessId=1 if identity else None,GetCurrentProcess=0,accounting='Frozen from_original_handle completed once if identity exists; incomplete call counts UNKNOWN, not zero; derived counts, not an API interceptor'))
  # Save all original return/streams before inspecting expected result content.
  budget.write(root/'original-return.json',enc(returned));budget.write(root/'original-stdout.bin',bytes(capture.buffers[0]));budget.write(root/'original-stderr.bin',bytes(capture.buffers[1]))
  result=dict(status='ARCHIVE_ONLY',approved=False,qualificationIssued=False,mode=c['mode'],originalReturn=returned)
  if capture.failure is not None:result['status']='CAPTURE_FAILED_RETURNED'
  elif capture.exit_code!=0:result['status']='CHILD_EXIT_FAILED_RETURNED'
  elif c['mode']=='LIVE':
   require_success(capture,registry,core);result['originCompleted']=True
   bundle_fee=budget.reserve_read(len(core['sealBytes'])+len(core['contents']['tools/outer_capture.py'])+len(core['contents']['tools/capture_origin.py']),'original-FactsBundle-3-host-source-reads')
   budget.reserve_write(262144,'original-FactsBundle-packet-outside-outer-archive')
   bundle=core['FactsBundle'](capture,inputs['templateRef'],inputs['policyRef'])
   bundle_fee.update(fixedHelperReturned=True,readsInHelper=3)
   for name,b in [('facts-entry-packet.json',bundle.outer),('facts.raw',bundle.raw),('receipt.json',enc(bundle.receipt)),('binding.json',enc(bundle.binding)),('observed-outer.json',enc(bundle.outer_return)),('bundle-evidence.json',enc(bundle.evidence))]:budget.write(root/name,b)
   budget.write(root/'planned-live-source.json',enc(inputs['sourcePlan']))
   result.update(status='FACTS_ARCHIVED_NOT_AUTHORIZED',rawSha256=sha(bundle.raw),rawBytes=len(bundle.raw),home=dict(package=bundle.parsed['homeRolePackage'],component=bundle.parsed['homeComponent'],uid=bundle.parsed['homeUid']),packetRef=bundle.packetRef,historicalOnlyAfterHostExit=True,candidateCreated=False,reviewCreated=False,qualificationIssued=False)
  else:
   raw=bytes(capture.buffers[0])
   if not raw:result['status']='EXPECTED_OUTPUT_MISSING_RETURNED'
   else:
    try:
     out=decode(raw,16384)
     if out!={'schema':'HOST01_PROBE_RETURN_V1','value':'ok'}:raise ValueError('PROBE_OUTPUT_SCHEMA')
     require_success(capture,registry,core);result.update(status='OFFLINE_ORIGINAL_CAPTURE_PASS',originCompleted=True)
    except ValueError:result['status']='EXPECTED_OUTPUT_BAD_RETURNED'
  result['custody']=len(core['custody']);result['filePending']=len(core['file'].FILE_PENDING);result['readReserved']=budget.readReserved;result['savedReserved']=budget.savedReserved
  budget.write(root/'result.json',enc(result));return result
 finally:BATCH_CONTROL=None

def require_success(capture,registry,core):
 record=core['origin'].require(capture)
 keys=('auditObserved','popenObjectReturned','identityBound','constructorTempsReturned','originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned','otherEvidenceReturned')
 if record['phase']!='COMPLETED' or capture.failure is not None or capture.exit_code!=0 or capture.pipe_amount_unknown or capture.counts!=[len(b) for b in capture.buffers] or not all(capture.facts[k] for k in keys) or len(registry.events)!=1 or registry.events[0]['matches'] is not True:raise ValueError('HOST_ORIGINAL_SUCCESS_REQUIRED')
 return record
def admit_config_file(path,approved_hash,budget):
 if type(approved_hash) is not str or len(approved_hash)!=64 or any(x not in '0123456789abcdef' for x in approved_hash) or approved_hash=='0'*64:raise ValueError('EXTERNAL_CONFIG_HASH_REQUIRED')
 cfg=decode(budget.read_pinned(path,65536,approved_hash));static_config(cfg);return cfg
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--approved-config-sha256',required=True);a=parser.parse_args();budget=Budget()
 try:
  cfg=admit_config_file(a.config,a.approved_config_sha256,budget);result=run(cfg,budget);print(json.dumps(dict(status=result['status'],approved=False,qualificationIssued=False)));return 0 if result['status'] in ('FACTS_ARCHIVED_NOT_AUTHORIZED','OFFLINE_ORIGINAL_CAPTURE_PASS') else 2
 except (ValueError,KeyError,TypeError,OSError) as e:
  registry=getattr(budget,'registry',None);capture=getattr(budget,'capture',None)
  entered=registry is not None and registry.entered
  if entered and (capture is None or not capture.returned or not capture.journal.returned() or not capture.control.returned()):retain('HOST_EXCEPTION_WITH_UNRETURNED_ORIGINAL')
  print(json.dumps(dict(status='REJECTED',reason=str(e),phase='KNOWN_RETURNED' if entered else 'PRECONSTRUCTOR',originalPopenEntered=entered,sourceReadReserved=budget.readReserved,sourceEvents=budget.reads,deviceReadOnlyPermissionIssued=False)));return 2
if __name__=='__main__':raise SystemExit(main())
