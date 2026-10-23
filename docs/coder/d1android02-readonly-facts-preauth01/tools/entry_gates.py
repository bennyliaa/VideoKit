"""Candidate-specific pre-SDK gate. Same Python process retains the original lock.

Not a server manager, network probe or portable lock framework. A completion
file is only a candidate; Owner must receive this exact live object after joins.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,sys,time,threading,subprocess,msvcrt,uuid
from win32_route import BACKEND,validate_stats

BASE=Path(__file__).resolve().parents[1]
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
GROUPS=('preflight','install','instrument','control','payload','command')
CUSTODY=[]
ROUTE_KEYS=set('schema kind scope planId generation checkedAtUtc endpoint serverPid serverCreationUtc serverImage serverFileSha256 identityStable routingOverrides contextReadBytes queryCount sourceSha256 routeBackend queryStats'.split())
def tick():return time.monotonic_ns()//1_000_000 # bound CPython Windows GetTickCount64, ~15.625ms
def encode(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(xs):
 d={};seen=set()
 for k,v in xs:
  if k.casefold() in seen:raise ValueError('DUPLICATE_JSON')
  seen.add(k.casefold());d[k]=v
 return d
def decode(b):return json.loads(b.decode('utf-8-sig'),object_pairs_hook=pairs)
def no_links(path):
 p=Path(path).absolute()
 for x in [p,*p.parents]:
  if x.exists() and x.stat().st_file_attributes&1024:raise ValueError('GATE_REPARSE')
def integer(v,lo,hi):return type(v) is int and lo<=v<=hi
def fixture_root_allowed(path):
 try:
  if not isinstance(path,(str,Path)):return False
  raw=str(path)
  if any(x in ('.','..') for x in raw.replace('\\','/').split('/')):return False
  p=Path(path)
  if not p.is_absolute() or p.drive.casefold()!=BASE.drive.casefold() or p.absolute()!=p.resolve():return False
  no_links(p)
  roots=(BASE/'selfchecks/work',Path('D:/CodexProjects/VideoKit/docs/tester/D1_READONLY_FACTS_PREAUTH01_REVIEW_EVIDENCE/fixtures'))
  return any(p!=root and p.is_relative_to(root) for root in roots)
 except (ValueError,OSError):return False

def stable(d,field):
 for _ in range(12):
  n=len(encode(d))
  if d[field]==n:return encode(d)
  d[field]=n
 raise ValueError('FIXED_SIZE')
def sticky(fn):
 def invoke(self,*args,**kwargs):
  try:return fn(self,*args,**kwargs)
  except (ValueError,TypeError,KeyError) as e:self.fail('REJECTED:'+str(e));raise
 return invoke

class GateSession:
 def __init__(self,home,options=None,policy=None,scope_start_tick=None,pre_events=None):
  self.start_tick=tick();self.start=self.start_tick/1000
  if scope_start_tick is not None:
   if not integer(scope_start_tick,1,self.start_tick) or self.start_tick-scope_start_tick>=30000:raise ValueError('ORIGINAL_RUNNER_START_TICK')
   self.start_tick=scope_start_tick;self.start=scope_start_tick/1000
  self.home=Path(home).resolve();self.pid=os.getpid();self.thread=threading.get_ident()
  self.generation=str(uuid.uuid4());self.failure=None;self.held=[];self.events=[];self.pending=[]
  self.released=False;self.release_attempted=False;self.accepted=False;self.prepared=False
  self.metadata_amount_unknown=True
  self.source_reserved_unknown=0;self.checker_stats=None
  self.lease=None;self.proof_hash=None;self.source_bytes=0;self.source_reads=0;self.carry=0;self.sdk_owner=None
  if pre_events is not None:
   for e in pre_events:self.charge('runner-pre:'+e['event'],e['bytes'])
  if policy is None:
   policy_bytes=(self.home/'release/capture-policy.json').read_bytes();self.policy=decode(policy_bytes);self.charge('gate-policy-read',len(policy_bytes))
  else:self.policy=decode(encode(policy)) # immutable initial copy, no policy-file overwrite
  p=self.policy;self.attempted=False
  if p.get('routeBackend')!=BACKEND:raise ValueError('FIXED_ROUTE_BACKEND_REQUIRED')
  if p['mode'] not in ('PRODUCTION','OFFLINE_FIXTURE'):raise ValueError('NO_GATE_IN_PREPARATION')
  self.fixture=p['mode']=='OFFLINE_FIXTURE';self.kind='OFFLINE_FIXTURE' if self.fixture else 'LIVE_LOCAL_METADATA'
  self.scope=p['scope'];self.root=Path(p['evidenceRoot']).resolve();no_links(self.root);no_links(self.home)
  expected_scope=sha('|'.join(p[k] for k in ('planId','entrySha256','productSealSha256','planSha256','runId')).encode())
  if self.scope!=expected_scope:raise ValueError('GATE_SCOPE_FORMULA')
  if self.fixture and not fixture_root_allowed(p['evidenceRoot']):raise ValueError('GATE_FIXTURE_ROOT')
  if not self.fixture and str(self.root)!=str(Path('D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION')/p['planId']/'outputs'):raise ValueError('GATE_PRODUCTION_ROOT')
  self.options=options or {};allowed={'checkerDelay','writerDelay','tailDelay','receiverDelay','checkerSeconds','proofSeconds','gateSeconds','wholeSeconds','fault'}
  if set(self.options)-allowed or (self.options and not self.fixture):raise ValueError('NO_LIVE_FAULT_OPTIONS')
  for k,v in self.options.items():
   if k!='fault' and (type(v) not in (int,float) or not 0<=v<=2):raise ValueError('FINITE_FIXTURE_OPTIONS')
  self.checker_seconds=self.options.get('checkerSeconds',20);self.proof_seconds=self.options.get('proofSeconds',10)
  self.gate_seconds=self.options.get('gateSeconds',30);self.whole=self.options.get('wholeSeconds',600)
  self.source_manifest=self.source_read(BASE/'reference/gate-sources.json')
  self.manifest_hash=sha(self.source_manifest);manifest=decode(self.source_manifest)
  if self.manifest_hash!=p['gateSourcesSha256']:raise ValueError('GATE_SOURCE_MANIFEST_POLICY')
  for row in manifest['files']:
   if sha(self.source_read(BASE/row['path']))!=row['sha256']:raise ValueError('GATE_SOURCE_CHANGED')
  if sha(self.source_read(BASE/'tools/runtime_binding.py'))!='47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982':raise ValueError('GATE_RUNTIME_HELPER')
  from runtime_binding import require_runtime
  self.runtime=require_runtime(p,'gate-before-claim')
  meta=decode((BASE/'reference/current-runtime-identity.json').read_bytes())
  self.source_reads+=len(meta['files'])+2;self.source_bytes+=2*(BASE/'reference/current-runtime-identity.json').stat().st_size+sum(x['bytes'] for x in meta['files'])
  if self.source_reads>64 or self.source_bytes>268435456:raise ValueError('SOURCE_READ_BUDGET')
  if not self.fixture:
   permit=p['gateAuthorization'];raw=self.source_read(permit['path']);a=decode(raw)
   self.charge('gate-local-authorization-read',len(raw))
   if sha(raw)!=permit['sha256'] or a.get('approvedForLocalMetadata') is not True or a!={'schema':'ENTRY_GATES_LOCAL_AUTH_V2','scope':self.scope,'planId':p['planId'],'entrySha256':p['entrySha256'],'gateSourcesSha256':p['gateSourcesSha256'],'approvedForLocalMetadata':True,'routeBackend':BACKEND}:raise ValueError('LOCAL_METADATA_NOT_AUTHORIZED')
  self.claim_path=(self.root.parent/'cooperative-default-route.lock') if self.fixture else Path('D:/CodexProjects/VideoKit/docs/coder/d1android02-production-runner01/release/cooperative-default-route.lock')
  no_links(self.claim_path)
  CUSTODY.append(self) # intentionally strong even when caller raises
 def source_read(self,path):
  no_links(path);b=Path(path).read_bytes();self.source_bytes+=len(b);self.source_reads+=1
  if self.source_bytes>268435456 or self.source_reads>64:raise ValueError('SOURCE_READ_BUDGET')
  return b
 def fail(self,code):
  if self.failure is None:self.failure=code
 def observe(self,start=None,seconds=None):
  now=tick()/1000
  if now-self.start>=self.whole:self.fail('WHOLE_STICKY')
  if now-self.start>=self.gate_seconds and not self.accepted:self.fail('GATE_STICKY')
  if start is not None and now-start>=seconds:self.fail('LOCAL_WINDOW_STICKY')
 def require(self):
  self.observe()
  if self.failure:raise ValueError(self.failure)
 def retain_unknown(self,code):
  self.fail(code)
  while True:time.sleep(.05) # no new attempt, no kill/close/release/retry
 def original(self,name,fn,start=None,seconds=None):
  record={'name':name,'returned':False,'error':None};self.held.append(record)
  def body():
   try:record['value']=fn();record['returned']=True
   except BaseException as e:record['error']=repr(e)
   record['endTick']=tick()
  t=threading.Thread(target=body,name='entry-gate-'+name);self.held.append(t);self.pending.append(t);t.start()
  while t.is_alive():self.observe(start,seconds);t.join(.005)
  self.observe(start,seconds)
  return record
 def charge(self,event,n):
  if not integer(n,0,131072) or any(e['event']==event for e in self.events):raise ValueError('GATE_DELTA_DUPLICATE_OR_TYPE')
  self.events.append({'event':event,'bytes':n})
  if sum(e['bytes'] for e in self.events)>262144:self.fail('GATE_CONTROL_BOUND')
 def write(self,name,data,proof_start=None,delay=0):
  if len(data)>16384:raise ValueError('GATE_FILE_BOUND')
  p=self.root/name;no_links(p)
  def work():
   f=p.open('xb');self.held.append(f);n=f.write(data)
   if n!=len(data):raise IOError('SHORT_WRITE')
   f.flush()
   if delay:time.sleep(delay)
   f.close();return n
  r=self.original('write-'+name,work,proof_start,self.proof_seconds if proof_start is not None else None)
  if not r['returned']:self.retain_unknown('ORIGINAL_WRITE_UNKNOWN')
  r.update(writeReturned=True,flushReturned=True,closeReturned=True,end=r['endTick']/1000)
  self.charge('write:'+name,len(data));return r
 def read_receiver(self,name):
  p=self.root/name;no_links(p)
  def work():
   f=p.open('rb');self.held.append(f);b=f.read(16385)
   if len(b)>16384:raise IOError('RECEIVER_READ_BOUND')
   if self.options.get('receiverDelay',0):time.sleep(self.options['receiverDelay'])
   f.close();return b
  r=self.original('receiver-read-'+name,work,self.proof_start,self.proof_seconds)
  if not r['returned']:self.retain_unknown('ORIGINAL_RECEIVER_READ_CLOSE_UNKNOWN')
  return r['value']
 def acquire(self):
  self.require()
  def work():
   self.lease=open(self.claim_path,'a+b',buffering=0);self.held.append(self.lease);self.lease.seek(0)
   try:msvcrt.locking(self.lease.fileno(),msvcrt.LK_NBLCK,1)
   except OSError as e:
    self.lease.close();self.lease=None
    if e.errno in (13,36):return False
    raise
   self.file_id=os.fstat(self.lease.fileno()).st_ino;return True
  r=self.original('claim-acquire',work)
  if not r['returned']:self.retain_unknown('CLAIM_ACQUIRE_UNKNOWN')
  if not r['value']:
   self.fail('COOPERATIVE_CLAIM_CONFLICT');CUSTODY.remove(self);raise ValueError(self.failure)
  self.assert_held()
 def assert_held(self):
  if self.pid!=os.getpid() or self.thread!=threading.get_ident() or self.released or self.lease is None or self.lease.closed or self.file_id!=os.fstat(self.lease.fileno()).st_ino or self.file_id!=self.claim_path.stat().st_ino:raise ValueError('SAME_ORIGINAL_HOLDER_REQUIRED')
  no_links(self.claim_path)
 def validate_route(self,d,context_size):
  p=self.policy;src='selfchecks/route_fixture.py' if self.fixture else 'tools/win32_route.py'
  if type(d) is not dict or set(d)!=ROUTE_KEYS:raise ValueError('ROUTE_SCHEMA')
  for k in ROUTE_KEYS-{'serverPid','identityStable','routingOverrides','contextReadBytes','queryCount','queryStats'}:
   if type(d[k]) is not str:raise ValueError('ROUTE_TYPE')
  if d['schema']!='ENTRY_LOCAL_ROUTE_V2' or d['routeBackend']!=BACKEND or d['kind']!=self.kind or d['scope']!=self.scope or d['planId']!=p['planId'] or d['generation']!=self.generation or d['endpoint']!='127.0.0.1:5037' or d['serverImage'].replace('\\','/').casefold()!='d:/android/sdk/platform-tools/adb.exe' or d['serverFileSha256']!=p['toolSha256'] or d['sourceSha256']!=sha(self.source_read(BASE/src)):raise ValueError('ROUTE_SOURCE_IDENTITY')
  validate_stats(d['queryStats'],self.fixture)
  if not integer(d['serverPid'],1,2147483647) or d['identityStable'] is not True or type(d['routingOverrides']) is not dict or d['routingOverrides'] or not integer(d['contextReadBytes'],context_size,context_size) or not integer(d['queryCount'],0 if self.fixture else 4,0 if self.fixture else 4):raise ValueError('ROUTE_FACTS')
  checked=datetime.fromisoformat(d['checkedAtUtc'].replace('Z','+00:00'));created=datetime.fromisoformat(d['serverCreationUtc'].replace('Z','+00:00'));now=datetime.now(timezone.utc)
  if checked.tzinfo is None or created.tzinfo is None or not 0<=(now-checked).total_seconds()<30 or created>checked:raise ValueError('ROUTE_NOT_FRESH')
 @sticky
 def prepare(self):
  if self.attempted:raise ValueError('NO_GATE_REPLAY')
  self.attempted=True
  self.acquire();self.require();p=self.policy
  c={'kind':self.kind,'scope':self.scope,'planId':p['planId'],'generation':self.generation,'toolPath':'D:/Android/SDK/platform-tools/adb.exe','toolSha256':p['toolSha256'],'toolBytes':8273560,'routeBackend':BACKEND}
  if self.fixture:c.update(fixtureDelay=self.options.get('checkerDelay',0),fixtureFault=self.options.get('fault','NONE'))
  cb=encode(c);self.write('gate-context.json',cb)
  if len(cb)>8192:raise ValueError('GATE_CONTEXT_BOUND')
  script=BASE/('selfchecks/route_fixture.py' if self.fixture else 'tools/win32_route.py')
  argv=[PY,'-I','-X','utf8','-B',str(script),str(self.root/'gate-context.json')]
  argv_bytes=len(encode(argv))
  if argv_bytes>4096:raise ValueError('GATE_ARGV_BOUND')
  self.charge('checker-command',argv_bytes);start=tick()/1000
  r=self.original('checker-start',lambda:subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE),start,self.checker_seconds)
  if not r['returned']:self.retain_unknown('CHECKER_START_UNKNOWN')
  proc=r['value'];self.proc=proc;self.held.append(proc);chunks=[bytearray(),bytearray()];counts=[0,0];errors=[]
  def drain(i,stream):
   try:
    while True:
     b=stream.read(4096)
     if not b:break
     counts[i]+=len(b)
     if sum(counts)>16384:self.fail('CHECKER_TEXT_BOUND')
     else:chunks[i].extend(b)
   except BaseException as e:errors.append(repr(e))
  readers=[threading.Thread(target=drain,args=(i,s)) for i,s in enumerate((proc.stdout,proc.stderr))];self.held.extend(readers);self.pending.extend(readers)
  for t in readers:t.start()
  wait=self.original('checker-wait',proc.wait,start,self.checker_seconds)
  if not wait['returned']:self.retain_unknown('CHECKER_WAIT_UNKNOWN')
  for t in readers:
   while t.is_alive():self.observe(start,self.checker_seconds);t.join(.005)
  def close():proc.stdout.close();proc.stderr.close();proc._handle.Close();return True
  closed=self.original('checker-stream-handle-close',close,start,self.checker_seconds)
  if errors or not closed['returned']:self.retain_unknown('CHECKER_STREAM_HANDLE_UNKNOWN')
  self.observe(start,self.checker_seconds)
  self.charge('checker-context-read',len(cb));self.charge('checker-stream-read',sum(counts))
  for name,b in zip(('gate-stdout.bin','gate-stderr.bin'),chunks):self.write(name,bytes(b))
  d=decode(bytes(chunks[0]))
  self.metadata_amount_unknown=True
  if type(d) is dict and d.get('routeBackend')==BACKEND and 'queryStats' in d:
   validate_stats(d['queryStats'],self.fixture,success=False)
   s=d['queryStats'];self.checker_stats=s;self.charge('checker-native-metadata-known',s['metadataBytesKnown']);self.metadata_amount_unknown=s['metadataAmountUnknown'] or s['imageHashAmountUnknown']
   if not self.fixture:
    self.source_bytes+=s['imageHashBytes'];self.source_reserved_unknown+=s['imageHashBytesReservedUnknown'];self.source_reads+=int(s['imageHashBytes']+s['imageHashBytesReservedUnknown']>0)
    if self.source_bytes+self.source_reserved_unknown>268435456 or self.source_reads>64:raise ValueError('SOURCE_READ_BUDGET')
  if wait['value'] or chunks[1]:self.fail('CHECKER_REJECTED')
  self.require();self.validate_route(d,len(cb));self.route=d;self.assert_held()
  route={k:d[k] for k in ('scope','planId','checkedAtUtc','serverPid','serverCreationUtc','serverImage','serverFileSha256','routingOverrides')}
  route.update(toolSha256=p['toolSha256'],sourceContractSha256=sha(self.source_read(BASE/'reference/route-backend-contract.json')),claimHeldExclusive=True,claimScope=self.scope,originalCheckerReturned=True,gateGeneration=self.generation,kind=self.kind,sourceSha256=d['sourceSha256'],routeBackend=BACKEND,queryStats=d['queryStats'])
  self.write('fresh-route.json',encode(route));self.proof_start_tick=tick();proof_start=self.proof_start_tick/1000
  receipt={'schema':'ENTRY_GATE_RETURN_V1','scope':self.scope,'planId':p['planId'],'kind':self.kind,'generation':self.generation,'ownerPid':self.pid,'checkerPid':proc.pid,'temporaryResourcesReturned':all(not t.is_alive() for t in self.pending),'scopeClaimIntentionallyRetained':True,'claimFileId':self.file_id,'claimPath':str(self.claim_path),'scopeStartTick':self.start_tick,'checkerSourceSha256':d['sourceSha256'],'gateSourcesSha256':self.manifest_hash,'entrySha256':p['entrySha256'],'ownerSha256':p['outerOwnerSha256'],'routeSha256':sha(encode(route)),'events':list(self.events),'controlBeforeReceipt':sum(e['bytes'] for e in self.events),'receiptWriteBytes':0,'physicalIO':'UNPROVEN','sourceHashBytes':self.source_bytes,'sourceHashReads':self.source_reads}
  rb=stable(receipt,'receiptWriteBytes');self.write('gate-original-return.json',rb,proof_start);self.receipt_bytes=rb
  proof={'schema':'ANDROID02_CAPTURE_COMPLETION_PROOF_V1','id':'pre_sdk_local_gate','nextId':'identity','scope':self.scope,'controllerPid':proc.pid,'controllerExited':True,'toolStreamsReturned':True,'originalResourcesReturnedAtConsole':True,'captureQualifiedAtConsole':True,'approvedForNext':True,'captureReceiptSha256':sha(rb),'semanticDependency':'pre_sdk_local_gate_ACTUAL_RETURN_AND_SEMANTIC_PASS','dependencyAccepted':True,'batchSdkChildrenEntered':0,'batchTextChargedBytesKnown':0,'batchBinaryArchiveBytesKnown':0,'batchAmountUnknown':False,'batchGroups':dict.fromkeys(GROUPS,0),'outerReturnSha256':sha(rb),'scopeStartTick':self.start_tick,'outerDelta':{'eventId':sha((self.scope+'|pre_sdk_local_gate|'+self.generation+'|'+sha(rb)).encode()),'nativeWriteBytes':len(rb),'proofWriteBytes':0,'additionalForwardBytes':0,'sourceOwnerSha256':p['outerOwnerSha256'],'gateSourcesSha256':self.manifest_hash,'generation':self.generation,'kind':self.kind},'proofWriteBytes':0,'candidateOnlyWriterCloseNotProven':True}
  base=sum(e['bytes'] for e in self.events)
  for _ in range(12):
   n=len(encode(proof));proof['proofWriteBytes']=n;proof['outerDelta']['proofWriteBytes']=n;proof['batchGroups']['control']=base+n;proof['batchTextChargedBytesKnown']=base+n
   if n==len(encode(proof)):break
  else:raise ValueError('GATE_PROOF_FIXED_SIZE')
  pb=encode(proof)
  if len(pb)>4096:raise ValueError('INITIAL_PROOF_BOUND')
  self.writer=self.write('pre_sdk_local_gate-completion-proof.json',pb,proof_start,self.options.get('writerDelay',0))
  # This receiver runs AFTER original writer thread join, not inside its file.
  self.proof_hash=sha(pb);self.proof_bytes=pb;self.proof_start=proof_start
  if self.options.get('tailDelay',0):time.sleep(self.options['tailDelay'])
  self.observe(proof_start,self.proof_seconds);self.require();self.assert_held();self.prepared=True
  return self
 @sticky
 def receive(self,policy,expected_manifest):
  if not self.prepared or self.accepted or expected_manifest!=self.manifest_hash:raise ValueError('ORIGINAL_GATE_RECEIVER_ONCE')
  for k in ('scope','planId','runId','entrySha256','outerOwnerSha256','gateSourcesSha256'):
   if policy[k]!=self.policy[k]:raise ValueError('GATE_RECEIVER_SCOPE_SOURCE')
  self.assert_held();self.observe(self.proof_start,self.proof_seconds);self.require()
  # Actual receiver reads both immutable candidate files once; account after base.
  for name,expected in [('pre_sdk_local_gate-completion-proof.json',self.proof_bytes),('gate-original-return.json',self.receipt_bytes)]:
   b=self.read_receiver(name);self.carry+=len(b)
   if b!=expected:raise ValueError('GATE_RECEIVER_ORIGINAL_BYTES')
  if any(t.is_alive() for t in self.pending) or not self.writer['returned']:raise ValueError('GATE_ORIGINAL_PENDING')
  self.observe(self.proof_start,self.proof_seconds);self.require();self.accepted=True
  return {'schema':'ENTRY_GATE_HANDOFF_V1','generation':self.generation,'scopeStartTick':self.start_tick,'ownerPid':self.pid,'initialProofSha256':self.proof_hash,'receiverControlBytes':self.carry,'gateSourcesSha256':self.manifest_hash,'claimFileId':self.file_id,'kind':self.kind}
 @sticky
 def before_role(self,owner):
  if not self.accepted or owner is not self.sdk_owner:raise ValueError('SAME_RECEIVING_OWNER')
  self.assert_held();self.observe()
  if owner.failure:self.fail('SDK_OWNER_STICKY')
  self.require()
 def release(self):
  if self.release_attempted or self.released:raise ValueError('RELEASE_ONCE')
  if any(t.is_alive() for t in self.pending):raise ValueError('NO_RELEASE_WITH_PENDING')
  if self.sdk_owner is not None and any(isinstance(t,threading.Thread) and t.is_alive() for t in self.sdk_owner.held):raise ValueError('NO_RELEASE_WITH_SDK_PENDING')
  self.assert_held();self.release_attempted=True
  def close():self.lease.seek(0);msvcrt.locking(self.lease.fileno(),msvcrt.LK_UNLCK,1);self.lease.close();return True
  r=self.original('claim-original-unlock-close',close)
  if not r['returned']:self.retain_unknown('CLAIM_RELEASE_UNKNOWN')
  self.released=True;CUSTODY.remove(self);return {'originalUnlockCloseReturned':True,'generation':self.generation,'failure':self.failure,'sdkChildrenEntered':0 if self.sdk_owner is None else self.sdk_owner.next,'endTick':tick(),'allTemporaryThreadsJoined':all(not t.is_alive() for t in self.pending)}
