"""Exact seven-role original outer owner, adapted from READY01's Popen owner.
No general command dispatch. PREPARATION returns before creating a Popen.
Wait/readers/files/handle and each proof writer remain strongly held until their
own return. Timers close admission only, never cancel, terminate or close twice.
"""
from pathlib import Path
import hashlib,json,subprocess,threading,time,sys,os
BASE=Path(__file__).resolve().parents[1]
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
GROUPS=('preflight','install','instrument','control','payload','command')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pairs(xs):
 d={}
 for k,v in xs:
  if k.casefold() in {s.casefold() for s in d}:raise ValueError('DUPLICATE_JSON')
  d[k]=v
 return d
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=pairs)
def encode(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def bounded_int(v,maxv):return type(v) is int and 0<=v<=maxv
def fix_size(d,field):
 for _ in range(12):
  n=len(encode(d))
  if d[field]==n:return encode(d)
  d[field]=n
 raise ValueError('NO_FIXED_SIZE')
class Owner:
 def __init__(self,home=BASE):
  self.home=Path(home).resolve();self.policy=read(self.home/'release/capture-policy.json');self.failure=None;self.held=[];self.events=set();self.next=0;self.text=0;self.records=[];self.timeout_observations=[]
  p=self.policy
  if p['mode']=='PREPARATION_ONLY':raise ValueError('PREPARATION_ONLY_NO_OUTER_CHILD')
  if p['mode'] not in ('PRODUCTION','OFFLINE_FIXTURE'):raise ValueError('EXACT_MODE')
  if digest(__file__)!=p['outerOwnerSha256'] or digest(PY)!=p['outerPythonSha256'] or digest(self.home/'tools/capture_android02.ps1')!=p['entrySha256']:raise ValueError('OWNER_SOURCE_PIN')
  self.plan=read(self.home/'reference/exact-seven-role-plan.json')
  if digest(self.home/'reference/exact-seven-role-plan.json')!=p['planSha256']:raise ValueError('PLAN_PIN')
  self.root=Path(p['evidenceRoot']);self.fixture=p['mode']=='OFFLINE_FIXTURE'
  if self.fixture:
   if not (str(self.root).startswith(str(BASE/'selfchecks/work')+os.sep) or str(self.root).startswith('D:\\CodexProjects\\VideoKit\\docs\\tester\\D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE\\fixtures\\')):raise ValueError('EXACT_FIXTURE_ROOT')
   self.slots=p['slots'];self.outer=p.get('fixtureOuterSeconds',15);self.proof=p.get('fixtureProofSeconds',2);self.whole=30
  else:
   # Controller independently verifies the complete activation again before SDK.
   a=read(p['authorization']['path'])
   if digest(p['authorization']['path'])!=p['authorization']['sha256'] or a['approvedForExecution'] is not True or a['outerOwnerSha256']!=digest(__file__) or a['outerPythonSha256']!=digest(PY) or a['scope']!=p['scope'] or a['entrySha256']!=p['entrySha256'] or a['planSha256']!=p['planSha256']:raise ValueError('OWNER_ACTIVATION_PIN')
   self.outer=a['outerSeconds'];self.proof=a['localProofSeconds'];self.whole=a['wholeWallSeconds']
   self.slots=[dict(s,argv=[p['runId'] if v=='@RUN_ID@' else v for v in s['argv']]) for s in self.plan['steps']]
  if any(type(v) not in (int,float) or not 0<v<=cap for v,cap in [(self.outer,600),(self.proof,30),(self.whole,600)]):raise ValueError('OWNER_WALL_BOUNDS')
  if not self.fixture and any(type(v) is not int for v in (self.outer,self.proof,self.whole)):raise ValueError('OWNER_WALL_INTEGER_TYPES')
  if not 1<=len(self.slots)<=7 or [s['id'] for s in self.slots]!=[s['id'] for s in self.plan['steps'][:len(self.slots)]]:raise ValueError('EXACT_ORDER')
  self.scope_start=time.monotonic();self.last_proof='ABSENT' if self.fixture else a['initialPredecessorProofSha256'];self.last_writer=None
 def fail(self,code):
  if self.failure is None:self.failure=code
 def retain_unknown(self,code):
  self.fail(code)
  # No new work/close attempt. This original owner remains alive with all refs.
  while True:time.sleep(.05)
 def observe(self,start,seconds,code):
  if time.monotonic()-start>=seconds:
   self.fail(code)
   if not any(r['code']==code for r in self.timeout_observations):self.timeout_observations.append({'code':code,'observedAt':time.monotonic(),'start':start,'limit':seconds,'pendingOriginalThreads':sum(isinstance(t,threading.Thread) and t.is_alive() for t in self.held)})
  if time.monotonic()-self.scope_start>=self.whole:self.fail('WHOLE_OUTER_SCOPE_TIMEOUT_STICKY')
 def wait_original(self,thread,start,limit,code):
  while thread.is_alive():self.observe(start,limit,code);thread.join(.005)
  self.observe(start,limit,code)
 def write_original(self,path,data,proof_start,delay=0):
  facts={'path':str(path),'bytes':len(data),'writeReturned':False,'flushReturned':False,'closeReturned':False,'error':None,'start':time.monotonic()}
  def write():
   f=None
   try:
    f=path.open('xb');self.held.append(f)
    n=f.write(data);facts['writeReturnedBytes']=n
    if n!=len(data):raise IOError('ORIGINAL_SHORT_WRITE_UNKNOWN_REMAINDER')
    facts['writeReturned']=True;f.flush();facts['flushReturned']=True
    if delay:time.sleep(delay) # finite, OFFLINE_FIXTURE-only controlled return gate
    f.close();facts['closeReturned']=True
   except BaseException as e:facts['error']=repr(e)
   facts['end']=time.monotonic()
  t=threading.Thread(target=write);self.held.extend([facts,t]);t.start();self.wait_original(t,proof_start,self.proof,'PROOF_WALL_TIMEOUT_STICKY')
  if facts['error'] or not facts['closeReturned']:self.retain_unknown('ORIGINAL_WRITER_UNKNOWN')
  self.text+=len(data);return facts
 def run_one(self):
  if self.failure:raise ValueError('STICKY_HALT_NO_NEW_ADMISSION')
  if self.next>=len(self.slots):raise ValueError('NO_EIGHTH_OR_REPLAY')
  if self.last_writer is not None and not self.last_writer['closeReturned']:raise ValueError('PREVIOUS_PROOF_WRITER_PENDING')
  p=self.policy;s=self.slots[self.next];id=s['id'];root=self.root;proof_start=time.monotonic()
  req={'schema':'ANDROID02_CAPTURE_REQUEST_V1','id':id,'policySha256':digest(self.home/'release/capture-policy.json'),'scope':p['scope'],'evidenceRoot':str(root),'argv':s['argv'],'maxTextBytes':s['maxTextBytes'],'maxBinaryBytes':0,'qualificationSeconds':s['qualificationSeconds']}
  rp=self.home/('request-'+id+'.json');rb=encode(req);self.write_original(rp,rb,proof_start)
  adm={'schema':'ANDROID02_OWNER_ADMISSION_V1','id':id,'scope':p['scope'],'entrySha256':p['entrySha256'],'ownerSha256':digest(__file__),'requestSha256':digest(rp),'predecessorProofSha256':self.last_proof,'previousProofWriterReturned':True,'previousProofWriterTimely':self.failure is None,'requestWriteBytes':len(rb),'admissionWriteBytes':0,'ownerPid':os.getpid(),'proofSeconds':self.proof,'outerSeconds':self.outer}
  ab=fix_size(adm,'admissionWriteBytes');ap=root/(id+'-owner-admission.json');self.write_original(ap,ab,proof_start)
  # Admission writer is actually closed here, before this only Popen is created.
  if self.failure:raise ValueError('PROOF_TIMEOUT_BEFORE_CHILD')
  argv=[PS,'-NoProfile','-NonInteractive','-File',str(self.home/'tools/capture_android02.ps1'),'-RequestPath',str(rp),'-PredecessorProofSha',self.last_proof,'-OwnerAdmissionSha',digest(ap)]
  local_used=time.monotonic()-proof_start
  start=time.monotonic();launch={'argv':argv,'startEntered':True,'process':None,'error':None}
  self.held.append(launch)
  def launch_original():
   try:launch['process']=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   except BaseException as e:launch['error']=repr(e)
  starter=threading.Thread(target=launch_original);self.held.append(starter);starter.start();self.wait_original(starter,start,self.outer,'OUTER_WALL_TIMEOUT_STICKY')
  if launch['error'] or launch['process'] is None:self.retain_unknown('ORIGINAL_OUTER_START_UNKNOWN')
  proc=launch['process'];self.held.append(proc)
  chunks=[bytearray(),bytearray()];reader_errors=[];raw_counts=[0,0]
  def drain(stream,buf):
   try:
    while True:
     b=stream.read(4096)
     if not b:break
     raw_counts[0 if buf is chunks[0] else 1]+=len(b)
     if sum(raw_counts)>65536:self.fail('OUTER_TEXT_BOUND_STICKY')
     else:buf.extend(b)
   except BaseException as e:reader_errors.append(repr(e));self.fail('OUTER_READ_UNKNOWN')
  threads=[threading.Thread(target=drain,args=(stream,buf)) for stream,buf in zip((proc.stdout,proc.stderr),chunks)]
  self.held.extend(threads+chunks)
  for t in threads:t.start()
  returned={'wait':False,'stdoutClose':False,'stderrClose':False,'handleClose':False,'error':None}
  def original_wait():
   try:returned['exitCode']=proc.wait();returned['wait']=True
   except BaseException as e:returned['error']=repr(e)
  waiter=threading.Thread(target=original_wait);self.held.extend([waiter,returned]);waiter.start();self.wait_original(waiter,start,self.outer,'OUTER_WALL_TIMEOUT_STICKY')
  if not returned['wait']:self.retain_unknown('ORIGINAL_OUTER_WAIT_UNKNOWN')
  code=returned['exitCode']
  for t in threads:self.wait_original(t,start,self.outer,'OUTER_WALL_TIMEOUT_STICKY')
  def original_closes():
   try:
    proc.stdout.close();returned['stdoutClose']=True
    proc.stderr.close();returned['stderrClose']=True
    proc._handle.Close();returned['handleClose']=True
   except BaseException as e:returned['error']=repr(e)
  closer=threading.Thread(target=original_closes);self.held.append(closer);closer.start();self.wait_original(closer,start,self.outer,'OUTER_WALL_TIMEOUT_STICKY')
  if returned['error'] or not returned['handleClose']:self.retain_unknown('ORIGINAL_OUTER_CLOSE_UNKNOWN')
  outer_end=time.monotonic()
  out,err=map(bytes,chunks);self.text+=len(out)+len(err);proof_start=time.monotonic()-local_used
  # Same original outer writer, captured bytes are not re-encoded/truncated.
  self.write_original(root/(id+'-console.bin'),out,proof_start);self.write_original(root/(id+'-controller-stderr.bin'),err,proof_start)
  try:co=json.loads(out)
  except (ValueError,UnicodeError):self.fail('NO_ORIGINAL_CONSOLE');raise ValueError(err.decode(errors='replace'))
  if code or err or not co['captureQualified']:self.fail('CAPTURE_FAILED_STICKY')
  native={'schema':'ANDROID02_OUTER_RETURN_V2','argv':argv,'controllerPid':proc.pid,'exitCode':code,'originalControllerWaitReturned':True,'sameOriginalPipeReadersJoined':all(not t.is_alive() for t in threads),'outerStreamsClosed':proc.stdout.closed and proc.stderr.closed,'originalWindowsProcessHandleCloseReturned':True,'amountUnknown':bool(reader_errors) or sum(raw_counts)!=len(out)+len(err),'stdoutSha256':hashlib.sha256(out).hexdigest(),'stderrSha256':hashlib.sha256(err).hexdigest(),'sourceEntrySha256':p['entrySha256'],'sourceOwnerSha256':digest(__file__),'requestSha256':digest(rp),'scope':p['scope'],'id':id,'outerStart':start,'outerEnd':outer_end,'outerSeconds':self.outer,'outerTimely':self.failure is None,'ownerPid':os.getpid(),'ownerAdmissionSha256':digest(ap),'rawOuterBytes':raw_counts}
  np=root/(id+'-outer-return.json');self.write_original(np,encode(native),proof_start)
  event=hashlib.sha256((p['scope']+'|'+id+'|'+digest(rp)+'|'+co['captureReceiptSha256']+'|'+digest(np)).encode()).hexdigest()
  if event in self.events:self.fail('DUPLICATE_DELTA');raise ValueError('DUPLICATE_DELTA')
  proof={'schema':'ANDROID02_CAPTURE_COMPLETION_PROOF_V1','id':id,'nextId':self.slots[self.next+1]['id'] if self.next+1<len(self.slots) else 'END','scope':p['scope'],'controllerPid':proc.pid,'controllerExited':True,'toolStreamsReturned':True,'originalResourcesReturnedAtConsole':co['allOriginalResourcesReturnedAtConsole'],'captureQualifiedAtConsole':co['captureQualified'],'approvedForNext':self.failure is None,'captureReceiptSha256':co['captureReceiptSha256'],'semanticDependency':id+'_ACTUAL_RETURN_AND_SEMANTIC_PASS','dependencyAccepted':co['semantic'] in ('PASS','PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN'),'batchSdkChildrenEntered':co['batchSdkChildrenEntered'],'batchTextChargedBytesKnown':0,'batchBinaryArchiveBytesKnown':0,'batchAmountUnknown':bool(self.failure),'batchGroups':dict(co['batchGroups']),'outerReturnSha256':digest(np),'scopeStartTick':co['scopeStartTick'],'outerDelta':{'eventId':event,'nativeWriteBytes':np.stat().st_size,'proofWriteBytes':0,'additionalForwardBytes':0,'baseConsoleSha256':digest(root/(id+'-console.bin')),'sourceOwnerSha256':digest(__file__)},'proofWriteBytes':0,'candidateOnlyWriterCloseNotProven':True}
  # Only self LENGTH is solved; no circular claim of this writer's own close.
  for _ in range(12):
   n=len(encode(proof));proof['proofWriteBytes']=n;proof['outerDelta']['proofWriteBytes']=n;delta=np.stat().st_size+n;proof['batchGroups']['control']=co['batchGroups']['control']+delta;proof['batchTextChargedBytesKnown']=co['batchTextChargedBytesKnown']+delta
   if len(encode(proof))==n:break
  else:raise ValueError('PROOF_SIZE_UNSTABLE')
  if proof['batchGroups']['control']>1048576 or proof['batchTextChargedBytesKnown']>3276800:self.fail('OUTER_DELTA_BUDGET_STICKY');proof['approvedForNext']=False;proof['batchAmountUnknown']=True
  pp=root/(id+'-completion-proof.json');delay=p.get('fixtureProofCloseDelay',0) if self.fixture else 0
  self.last_writer=self.write_original(pp,encode(proof),proof_start,delay)
  # Failure after the write is NOT retrospectively changed to approved.
  self.events.add(event);self.last_proof=digest(pp);self.next+=1
  self.records.append({'id':id,'console':co,'outer':native,'proof':proof,'proofWriter':dict(self.last_writer),'stickyFailureAfterWriterReturn':self.failure})
  if self.failure:raise ValueError('OWNER_STICKY_NO_SUCCESSOR:'+self.failure)
  return self.records[-1]
 def run_seven(self):
  while self.next<len(self.slots):self.run_one()
  return self.records
if __name__=='__main__':
 # No arbitrary home/argv CLI. Exact production home and fixed ordered scope only.
 try:Owner().run_seven()
 except BaseException:sys.exit(2)
