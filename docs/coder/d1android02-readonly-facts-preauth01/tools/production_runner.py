"""One candidate, one permit, one original process; no interactive signing step.

The authoritative execution order supplies BOTH externally fixed input hashes.
This module never writes its permit or approval evidence. Offline test evidence
cannot be consumed by live mode. No network or server lifecycle API lives here.
"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,hashlib,json,os,sys,threading,time,uuid
# -I deliberately omits script/CWD imports. Add only this exact source directory.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from entry_gates import fixture_root_allowed,GateSession,encode,decode,sha,tick,no_links,integer,stable
from win32_route import BACKEND
BASE=Path(__file__).resolve().parents[1]
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
ROLES=['identity','global_idle','app_absence','test_absence','install_app','install_test','scope_all']
OPS=['local_gate','hold_claim','materialize_activation','materialize_policy','run_seven','release_claim']
LIMITS={'wholeSeconds':600,'gateSeconds':30,'checkerSeconds':20,'proofSeconds':10,'outerSeconds':120,'sdkChildren':7,'concurrency':1,'retry':0,'metadataQueries':4,'controlBytes':1048576,'textBytes':3276800,'payloadBytes':7629605,'commandBytes':28672,'localControlBytes':262144,'minimumHandoffMs':1000}
PERMIT_KEYS=set('schema authorizationId mode approvedForExecution notBeforeUtc expiresUtc planId runId scope home evidenceRoot sources sourceSeal review product tools roles operations limits fixtureScenario routeBackend globalIdleQualification'.split())
APPROVAL_KEYS=set('schema mode evidenceKind sourceThreadId sourceTurnId instructionText instructionSha256 approvedPermitSha256'.split())
SOURCE_FILES=('tools/production_runner.py','tools/entry_gates.py','tools/outer_owner.py','tools/capture_android02.ps1','tools/win32_route.py','tools/runtime_binding.py','reference/current-runtime-identity.json','reference/exact-seven-role-plan.json','reference/gate-sources.json','selfchecks/route_fixture.py','selfchecks/capture_fixture.py','reference/route-backend-contract.json','selfchecks/route_model.py','tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py','tools/fact_preauth.py','tools/facts_entry.py','reference/fact-preauth-schema.json')
RUNNER_CUSTODY=[]
def exact(d,keys,code):
 if type(d) is not dict or set(d)!=set(keys):raise ValueError(code)
def same_typed(a,b):
 if type(a) is not type(b):return False
 if type(a) is dict:return set(a)==set(b) and all(same_typed(a[k],b[k]) for k in a)
 if type(a) is list:return len(a)==len(b) and all(same_typed(x,y) for x,y in zip(a,b))
 return a==b
def utc(s):
 if type(s) is not str:raise ValueError('UTC_TYPE')
 t=datetime.fromisoformat(s.replace('Z','+00:00'))
 if t.tzinfo is None:raise ValueError('UTC_ZONE')
 return t.astimezone(timezone.utc)
def uuid_string(s):return type(s) is str and str(uuid.UUID(s))==s
def reference(d):
 exact(d,{'path','sha256'},'REFERENCE_SCHEMA')
 if type(d['path']) is not str or type(d['sha256']) is not str or len(d['sha256'])!=64 or any(c not in '0123456789abcdef' for c in d['sha256']):raise ValueError('REFERENCE_TYPE')
 return Path(d['path'])

class ProductionRunner:
 def __init__(self,mode=None,permit_path=None,permit_sha=None,approval_path=None,approval_sha=None):
  self.start_tick=tick();self.start=self.start_tick/1000;self.pid=os.getpid();self.thread=threading.get_ident()
  self.held=[];self.pending=[];self.pre=[];self.post=[];self.receiver=[];self.final=[];self.failure=None;self.gate=None;self.owner=None
  self.source_bytes=0;self.source_reads=0;self.consumed=False;self.terminal=None;self.received=False;self.seeded=False;self.creation_attempted=False
  self.mode=mode;self.proof_start=None;self.finished=False
  if mode not in ('live','fixture') or not all(type(x) is str and x for x in (permit_path,permit_sha,approval_path,approval_sha)):raise ValueError('EXPLICIT_MODE_AND_PREAUTH_REQUIRED')
  self.fixture=mode=='fixture';self.kind='OFFLINE_FIXTURE' if self.fixture else 'LIVE'
  RUNNER_CUSTODY.append(self)
  try:
   self.permit_path=Path(permit_path).absolute();self.approval_path=Path(approval_path).absolute()
   self.permit_bytes=self.read_file(self.permit_path,'permit-read','pre');self.approval_bytes=self.read_file(self.approval_path,'approval-read','pre')
   if len(self.permit_bytes)>32768 or len(self.approval_bytes)>8192:raise ValueError('PREAUTH_JSON_BYTE_BOUND')
   if sha(self.permit_bytes)!=permit_sha or sha(self.approval_bytes)!=approval_sha:raise ValueError('EXTERNAL_APPROVAL_INPUT_HASH')
   self.permit_sha=permit_sha;self.approval_sha=approval_sha;self.permit=decode(self.permit_bytes);self.approval=decode(self.approval_bytes)
   self.validate()
  except (ValueError,TypeError,KeyError) as e:
   self.fail(str(e));RUNNER_CUSTODY.remove(self);raise
 def fail(self,code):
  if self.failure is None:self.failure=code
 def unknown(self,code):
  self.fail(code)
  while True:time.sleep(.05) # strong refs; no exit/kill/retry/second close
 def observe(self,initial=True):
  now=tick()/1000
  if now-self.start>=600:self.fail('RUNNER_WHOLE_STICKY')
  if initial and now-self.start>=30:self.fail('RUNNER_GATE_STICKY')
  if initial and self.proof_start is not None and now-self.proof_start>=10:self.fail('RUNNER_PROOF_STICKY')
  if hasattr(self,'expires') and not self.not_before<=datetime.now(timezone.utc)<self.expires:self.fail('PERMIT_EXPIRED_OR_FUTURE')
 def require(self,initial=True):
  self.observe(initial)
  if self.failure:raise ValueError(self.failure)
 def event(self,lane,event,n):
  rows=getattr(self,lane)
  if not integer(n,0,131072) or any(x['event']==event for x in rows):raise ValueError('RUNNER_ONCE_AMOUNT')
  rows.append({'event':event,'bytes':n})
  if sum(x['bytes'] for seq in (self.pre,self.post,self.receiver,self.final) for x in seq)>262144:self.fail('RUNNER_CONTROL_CAP')
 def operation(self,name,fn,initial=True):
  self.require(initial);r={'name':name,'returned':False,'error':None,'startTick':tick()};self.held.append(r)
  def body():
   try:r['value']=fn();r['returned']=True
   except BaseException as e:r['error']=repr(e)
   r['endTick']=tick()
  t=threading.Thread(target=body,name='production-runner-'+name);self.held.append(t);self.pending.append(t);t.start()
  while t.is_alive():self.observe(initial);t.join(.005)
  self.observe(initial)
  if not r['returned']:self.unknown('RUNNER_ORIGINAL_IO_UNKNOWN:'+name)
  return r
 def read_file(self,path,name,lane=None,initial=True):
  path=Path(path);no_links(path)
  if not path.is_file():raise ValueError('REQUIRED_FILE_MISSING:'+name)
  def work():
   f=path.open('rb');self.held.append(f);cap=536870912 if lane is None else 131072;b=f.read(cap+1)
   if len(b)>cap:raise IOError('ORIGINAL_READ_BOUND')
   f.close();return b
  r=self.operation(name,work,initial);b=r['value']
  if lane is not None:self.event(lane,name,len(b))
  else:
   self.source_bytes+=len(b);self.source_reads+=1
   if self.source_bytes>536870912 or self.source_reads>256:raise ValueError('RUNNER_SOURCE_BUDGET')
  return b
 def write_file(self,path,data,name,lane,delay=0,initial=True):
  path=Path(path);no_links(path)
  if len(data)>131072 or path.exists():raise ValueError('FIXED_NEW_OUTPUT_REQUIRED:'+name)
  def work():
   f=path.open('xb');self.held.append(f);n=f.write(data)
   if n!=len(data):raise IOError('ORIGINAL_SHORT_WRITE')
   f.flush()
   if delay:time.sleep(delay)
   f.close();return n
  r=self.operation(name,work,initial);self.event(lane,name,len(data));self.require(initial);return r
 def validate(self):
  p=self.permit;a=self.approval;exact(p,PERMIT_KEYS,'PERMIT_EXACT_SCHEMA');exact(a,APPROVAL_KEYS,'APPROVAL_EXACT_SCHEMA')
  if p['schema']!='VIDEOKIT_PRODUCTION_RUNNER_PERMIT_V2' or p['routeBackend']!=BACKEND or p['mode']!=self.kind or p['approvedForExecution'] is not True or not uuid_string(p['authorizationId']) or not uuid_string(p['planId']):raise ValueError('PERMIT_KIND_APPROVAL')
  evidence='OFFLINE_TEST_ONLY' if self.fixture else 'COORDINATOR_EXECUTION_ORDER'
  instruction=('EXECUTE_OFFLINE_PERMIT ' if self.fixture else 'EXECUTE_LIVE_PERMIT ')+self.permit_sha
  if a['schema']!='VIDEOKIT_RUNNER_APPROVAL_EVIDENCE_V1' or a['mode']!=self.kind or a['evidenceKind']!=evidence or a['approvedPermitSha256']!=self.permit_sha or a['instructionText']!=instruction or a['instructionSha256']!=sha(instruction.encode()) or a['sourceThreadId']!='01a107c3-2bf9-7fa0-94a0-234258ca6774' or not uuid_string(a['sourceTurnId']):raise ValueError('PRIOR_APPROVAL_RELATION')
  self.not_before=utc(p['notBeforeUtc']);self.expires=utc(p['expiresUtc'])
  if not 0<(self.expires-self.not_before).total_seconds()<=900:raise ValueError('PERMIT_VALIDITY_BOUND')
  self.require()
  if type(p['runId']) is not str or not p['runId'].startswith('D1MA02-') or not 1<=len(p['runId'][7:])<=32 or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in p['runId'][7:]):raise ValueError('RUN_ID')
  exact(p['limits'],LIMITS,'LIMIT_SCHEMA')
  if any(type(p['limits'][k]) is not int or p['limits'][k]!=v for k,v in LIMITS.items()) or p['operations']!=OPS:raise ValueError('EXACT_OPERATIONS_OR_LIMITS')
  no_links(p['home']);no_links(p['evidenceRoot']);self.home=Path(p['home']).resolve();self.root=Path(p['evidenceRoot']).resolve()
  if str(self.home)!=p['home'] or str(self.root)!=p['evidenceRoot']:raise ValueError('CANONICAL_OUTPUT_PATH_REQUIRED')
  if len(str(self.home))>210:raise ValueError('FIXED_OUTPUT_PATH_BOUND')
  if self.root!=self.home/'outputs' or self.home.exists():raise ValueError('FRESH_ONCE_EXACT_HOME')
  if self.fixture:
   allowed=fixture_root_allowed(p['home'])
   if not allowed:raise ValueError('FIXTURE_HOME')
  elif self.home!=Path('D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION')/p['planId']:raise ValueError('LIVE_EXACT_HOME')
  if self.permit_path.is_relative_to(self.home) or self.approval_path.is_relative_to(self.home):raise ValueError('AUTH_INPUT_NOT_OUTPUT')
  if not self.fixture and p['fixtureScenario']!='NONE':raise ValueError('NO_LIVE_FAULTS')
  if p['fixtureScenario'] not in ('NONE','MATERIALIZE_LATE','RECEIVER_LATE','MATERIALIZE_KNOWN_REJECT','TAIL_LATE','EXPIRE_DURING_MATERIALIZE','WRONG_HOLDER','WRONG_OUTPUT_SOURCE','BUSY','OWNER_END_TAIL','NO_SDK_ABORT','PRESTART_KNOWN_REJECT'):raise ValueError('FIXED_FIXTURE_SCENARIO')
  exact(p['sources'],SOURCE_FILES,'EXACT_SOURCE_SET')
  for rel in SOURCE_FILES:
   b=self.read_file(BASE/rel,'source:'+rel)
   if sha(b)!=p['sources'][rel]:raise ValueError('PREAUTHORIZED_SOURCE_MISMATCH:'+rel)
  seal_path=reference(p['sourceSeal']);sb=self.read_file(seal_path,'source-seal-read','pre');seal=decode(sb)
  if sha(sb)!=p['sourceSeal']['sha256'] or seal!={'schema':'PRODUCTION_RUNNER_SOURCE_SEAL_V1','sources':p['sources']}:raise ValueError('SOURCE_SEAL_RELATION')
  review_path=reference(p['review']);review=self.read_file(review_path,'review-read','pre')
  if sha(review)!=p['review']['sha256']:raise ValueError('REVIEW_PIN')
  self.plan=decode(self.read_file(BASE/'reference/exact-seven-role-plan.json','plan-source'))
  q=p['globalIdleQualification']
  if type(q) is not dict or len(encode(q))>16384 or q.get('targetScope')!=p['scope'] or q.get('targetRunId')!=p['runId'] or q.get('mode')!=self.kind or q.get('fixtureOnly') is not self.fixture or q.get('targetSourceSealSha256')!=p['sourceSeal']['sha256'] or q.get('targetPlanSha256')!=p['sources']['reference/exact-seven-role-plan.json'] or q.get('reviewEvidenceSha256')!=p['review']['sha256']:raise ValueError('GLOBAL_IDLE_PRIOR_QUALIFICATION_BINDING')
  if p['planId'] in self.plan['forbiddenOldPlanIds']:raise ValueError('OLD_PLAN_ID')
  expected_scope=sha('|'.join((p['planId'],p['sources']['tools/capture_android02.ps1'],self.plan['product']['sealSha256'],p['sources']['reference/exact-seven-role-plan.json'],p['runId'])).encode())
  if p['scope']!=expected_scope or not same_typed(p['product'],self.plan['product']):raise ValueError('PREAUTHORIZED_SCOPE_PRODUCT')
  if not self.fixture:
   if not same_typed(p['tools'],self.plan['sdkFiles']):raise ValueError('LIVE_TOOL_SET')
   roles=[dict(s,argv=[p['runId'] if v=='@RUN_ID@' else v for v in s['argv']]) for s in self.plan['steps']]
   if not same_typed(p['roles'],roles):raise ValueError('LIVE_EXACT_SEVEN_ROLES')
  else:
   if not same_typed(p['tools'],[{'path':PY,'bytes':Path(PY).stat().st_size,'sha256':sha(self.read_file(PY,'fixture-tool-source'))}]):raise ValueError('FIXTURE_TOOL_ONLY')
   if type(p['roles']) is not list or len(p['roles'])!=7 or [s.get('id') for s in p['roles']]!=ROLES:raise ValueError('FIXTURE_SEVEN_ORDER')
   modes=['identity','global_busy' if p['fixtureScenario']=='BUSY' else 'global_idle','app_absence','test_absence','payload_app','payload_test','instrument']
   for i,s in enumerate(p['roles']):
    expected=self.fixture_slot(i,modes[i])
    if not same_typed(s,expected):raise ValueError('EXACT_FIXED_FIXTURE_ROLE')
  for i,pin in enumerate(p['tools']):
   b=self.read_file(pin['path'],'tool-pin:'+str(i))
   if len(b)!=pin['bytes'] or sha(b)!=pin['sha256']:raise ValueError('PREAUTHORIZED_TOOL_BYTES')
  # Only opaque integrity hashes; no APK/media parser or actual SDK execution.
  for name in ('app','test'):
   pin=p['product'][name];b=self.read_file(pin['path'],'product-pin:'+name)
   if len(b)!=pin['bytes'] or sha(b)!=pin['sha256']:raise ValueError('PRODUCT_BYTES')
  sealbytes=self.read_file(p['product']['sealPath'],'product-seal-source')
  if sha(sealbytes)!=p['product']['sealSha256']:raise ValueError('PRODUCT_SEAL')
  self.require()
 def fixture_slot(self,i,mode):
  s=dict(self.plan['steps'][i]);s.update(argv=[PY,'-I','-X','utf8','-B',(BASE/'selfchecks/capture_fixture.py').as_posix(),mode,str(self.root/'fixture-gate')],maxTextBytes=min(s['maxTextBytes'],8192),qualificationSeconds=2)
  if i in (4,5):
   n=4096 if i==4 else 2048;b=bytes(range(256))*(n//256);s['payloadPin']={'path':str(self.root/(s['id']+'-fixture-input.bin')),'bytes':n,'sha256':sha(b)}
  return s
 def remaining(self):
  self.require()
  remaining=min(600-(tick()/1000-self.start),30-(tick()/1000-self.start),10-(tick()/1000-self.proof_start))
  if remaining<1:raise ValueError('INSUFFICIENT_SHARED_HANDOFF_REMAINING')
  return remaining
 def verify_inputs(self,lane):
  b=self.read_file(self.permit_path,'permit-recheck',lane);a=self.read_file(self.approval_path,'approval-recheck',lane)
  if b!=self.permit_bytes or a!=self.approval_bytes:raise ValueError('PRIOR_APPROVAL_CHANGED')
  self.require()
 def prepare_home(self):
  self.require();self.creation_attempted=True;self.home.mkdir(parents=True,exist_ok=False)
  for rel in ('tools','reference','release','outputs'):(self.home/rel).mkdir()
  for rel in ('tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/route-backend-contract.json'):
   b=self.read_file(BASE/rel,'copy-read:'+rel,'pre');self.write_file(self.home/rel,b,'copy-write:'+rel,'pre')
  if self.fixture:
   for i in (4,5):
    pin=self.permit['roles'][i]['payloadPin'];b=bytes(range(256))*(pin['bytes']//256);self.write_file(pin['path'],b,'fixture-payload:'+str(i),'pre')
  p=decode(self.read_file(BASE/'release/capture-policy.json','policy-template-read','pre'))
  src=self.permit['sources'];p.update(mode='OFFLINE_FIXTURE' if self.fixture else 'PRODUCTION',scope=self.permit['scope'],planId=self.permit['planId'],runId=self.permit['runId'],evidenceRoot=str(self.root),entrySha256=src['tools/capture_android02.ps1'],outerOwnerSha256=src['tools/outer_owner.py'],gateSourcesSha256=src['reference/gate-sources.json'],runnerSourceSha256=src['tools/production_runner.py'],runnerSources=self.permit['sourceSeal'],runnerPermit={'path':str(self.permit_path),'sha256':self.permit_sha},runnerApproval={'path':str(self.approval_path),'sha256':self.approval_sha},toolCandidateSeal=self.permit['sourceSeal'],independentReview=self.permit['review'],toolSha256=self.permit['tools'][0]['sha256'])
  if self.fixture:p.update(slots=self.permit['roles'],fixtureScriptSha256=src['selfchecks/capture_fixture.py'],fixtureFault='NONE',fixtureGatePath=str(self.root/'fixture-gate'),fixtureOuterSeconds=120,fixtureProofSeconds=10)
  if self.fixture and self.permit['fixtureScenario']=='PRESTART_KNOWN_REJECT':p.update(fixtureFault='PRESTART_KNOWN_REJECT')
  if self.fixture and self.permit['fixtureScenario']=='OWNER_END_TAIL':p.update(fixtureProofTailGate='CROSS_SAME_DEADLINE_AFTER_TIMELY_WRITER',fixtureProofSeconds=2)
  p['routeBackend']=BACKEND
  p['globalIdleQualification']=self.permit['globalIdleQualification']
  local={'schema':'ENTRY_GATES_LOCAL_AUTH_V2','scope':p['scope'],'planId':p['planId'],'entrySha256':p['entrySha256'],'gateSourcesSha256':p['gateSourcesSha256'],'approvedForLocalMetadata':True,'routeBackend':BACKEND}
  lp=self.home/'release/gate-local-authorization.json';lb=encode(local);self.write_file(lp,lb,'local-authorization-write','pre');p['gateAuthorization']={'path':str(lp),'sha256':sha(lb)}
  self.policy=p
  # Original pre-gate IO has all actually returned; seed, do not replay its cost.
  self.gate=GateSession(self.home,policy=p,scope_start_tick=self.start_tick,pre_events=self.pre)
  self.seeded=True;self.gate.prepare();self.proof_start=self.gate.proof_start
  self.initial_proof=self.gate.proof_bytes;self.initial_hash=self.gate.proof_hash
 def materialize(self):
  self.remaining();self.verify_inputs('post');p=self.policy;g=self.gate
  route=self.read_file(self.root/'fresh-route.json','materializer-route-read','post')
  proof=self.read_file(self.root/'pre_sdk_local_gate-completion-proof.json','materializer-proof-read','post')
  if sha(proof)!=g.proof_hash or proof!=self.initial_proof:raise ValueError('INITIAL_PROOF_CHANGED')
  scenario=self.permit['fixtureScenario']
  if scenario=='MATERIALIZE_KNOWN_REJECT':raise ValueError('CONTROLLED_MATERIALIZATION_REJECT_BEFORE_OPEN')
  if scenario=='EXPIRE_DURING_MATERIALIZE':
   while datetime.now(timezone.utc)<self.expires+timedelta(milliseconds=20):time.sleep(.01)
   self.require()
  activation={'schema':'ANDROID02_CAPTURE_ACTIVATION_V1','scope':p['scope'],'planId':p['planId'],'runId':p['runId'],'entrySha256':p['entrySha256'],'planSha256':p['planSha256'],'toolCandidateSealSha256':p['toolCandidateSeal']['sha256'],'productSealSha256':p['productSealSha256'],'reviewSha256':p['independentReview']['sha256'],'toolSha256':p['toolSha256'],'evidenceRoot':str(self.root),'wholeWallSeconds':600,'localProofSeconds':10,'outerSeconds':120,'freshRouteProofSha256':sha(route),'initialPredecessorProofSha256':g.proof_hash,'outerOwnerSha256':p['outerOwnerSha256'],'outerPythonSha256':p['outerPythonSha256'],'runtimeIdentitySha256':p['runtimeIdentitySha256'],'runtimeBindingSourceSha256':p['runtimeBindingSourceSha256'],'approvedForExecution':True,'runnerPermitSha256':self.permit_sha,'runnerSourceSha256':p['runnerSourceSha256'],'runnerApprovalSha256':self.approval_sha}
  activation['routeBackend']=BACKEND
  ap=self.home/'release/activation.json';ab=encode(activation);delay=10.25 if scenario=='MATERIALIZE_LATE' else 0
  self.activation_writer=self.write_file(ap,ab,'activation-write','post',delay);self.activation_bytes=ab
  p['authorization']={'path':str(ap),'sha256':sha(ab)};p['freshRouteProof']={'path':str(self.root/'fresh-route.json'),'sha256':sha(route)}
  pb=encode(p);pp=self.home/'release/capture-policy.json';self.policy_writer=self.write_file(pp,pb,'policy-write','post');self.policy_bytes=pb
  for path,b,name in ((ap,ab,'activation-readback'),(pp,pb,'policy-readback')):
   if self.read_file(path,name,'post')!=b:raise ValueError('MATERIALIZATION_ORIGINAL_READBACK')
  receipt={'schema':'RUNNER_MATERIALIZATION_RETURN_V1','scope':p['scope'],'planId':p['planId'],'kind':self.kind,'generation':g.generation,'ownerPid':self.pid,'scopeStartTick':self.start_tick,'initialProofStartTick':g.proof_start_tick,'permitSha256':self.permit_sha,'approvalSha256':self.approval_sha,'runnerSourceSha256':p['runnerSourceSha256'],'initialProofSha256':g.proof_hash,'activationSha256':sha(ab),'policySha256':sha(pb),'preGateControlBytes':sum(x['bytes'] for x in self.pre),'events':list(self.post),'controlBeforeReceipt':sum(x['bytes'] for x in self.post),'receiptWriteBytes':0,'candidateOnlyWriterCloseNotProven':True}
  rb=stable(receipt,'receiptWriteBytes');self.receipt_writer=self.write_file(self.root/'runner-materialization.json',rb,'materialization-receipt-write','post');self.receipt_bytes=rb
  if scenario=='TAIL_LATE':time.sleep(10.25)
  if scenario=='WRONG_OUTPUT_SOURCE':
   # Only own newly-created source copy, never the frozen candidate/runtime.
   fp=self.home/'tools/capture_android02.ps1';old=self.read_file(fp,'fixture-copy-read','post');self.original_entry_before_fault=old
   f=fp.open('ab');self.held.append(f);n=f.write(b'\n# FIXTURE_SOURCE_CHANGED\n');f.flush();f.close();self.event('post','fixture-copy-append',n)
  self.remaining()
 def read_policy_for_owner(self,home):
  if Path(home).resolve()!=self.home.resolve() or self.received:raise ValueError('SAME_RUNNER_POLICY_ONCE')
  self.remaining();b=self.read_file(self.home/'release/capture-policy.json','owner-policy-read','receiver')
  if b!=self.policy_bytes:raise ValueError('OWNER_POLICY_ORIGINAL_BYTES')
  return decode(b)
 def read_activation_for_owner(self):
  self.require();b=self.read_file(self.home/'release/activation.json','owner-activation-read','receiver',True)
  if b!=self.activation_bytes:raise ValueError('OWNER_ACTIVATION_ORIGINAL_BYTES')
  return decode(b)
 def consume(self,owner):
  if self.received or owner.home!=self.home.resolve() or os.getpid()!=self.pid or threading.get_ident()!=self.thread:raise ValueError('SAME_ORIGINAL_RUNNER_REQUIRED')
  self.remaining();g=self.gate;g.assert_held()
  if self.permit['fixtureScenario']=='RECEIVER_LATE':
   # Same original file read/close worker, finite delay in addition to actual read.
   def delayed():
    f=(self.root/'runner-materialization.json').open('rb');self.held.append(f);b=f.read(32769);time.sleep(10.25);f.close();return b
   r=self.operation('materialization-delayed-receiver',delayed);b=r['value'];self.event('receiver','owner-materialization-read',len(b))
  else:b=self.read_file(self.root/'runner-materialization.json','owner-materialization-read','receiver')
  if b!=self.receipt_bytes or any(t.is_alive() for t in self.pending):raise ValueError('MATERIALIZATION_ORIGINAL_PENDING_OR_BYTES')
  self.remaining();self.received=True
  return {'schema':'RUNNER_HANDOFF_V1','ownerPid':self.pid,'scopeStartTick':self.start_tick,'initialProofStartTick':g.proof_start_tick,'permitExpiresUtc':self.permit['expiresUtc'],'generation':g.generation,'permitSha256':self.permit_sha,'approvalSha256':self.approval_sha,'runnerSourceSha256':self.policy['runnerSourceSha256'],'materializationSha256':sha(b),'initialProofSha256':g.proof_hash,'postControlBytes':sum(x['bytes'] for x in self.post),'receiverControlBytes':sum(x['bytes'] for x in self.receiver),'kind':self.kind,'eventId':sha((self.policy['scope']+'|runner-materialization|'+g.proof_hash+'|'+sha(b)+'|'+sha(self.policy_bytes)).encode())}
 def before_role(self,owner):
  if not self.received or owner is not self.owner:raise ValueError('SAME_ORIGINAL_RUNNER_OWNER')
  self.require(owner.next==0);self.gate.assert_held()
  # Content hash checks, not extra functional approval reads or fresh signing.
  for path,expected,name in ((self.permit_path,self.permit_sha,'permit-integrity'),(self.approval_path,self.approval_sha,'approval-integrity'),(self.home/'tools/capture_android02.ps1',self.policy['entrySha256'],'entry-integrity')):
   if sha(self.read_file(path,name,None,owner.next==0))!=expected:raise ValueError('RUNNER_SOURCE_OR_APPROVAL_CHANGED')
  self.require(owner.next==0)
 def run(self):
  try:
   if self.consumed:raise ValueError('RUNNER_ONCE')
   self.consumed=True;self.prepare_home();self.materialize();scenario=self.permit['fixtureScenario']
   if scenario=='NO_SDK_ABORT':raise ValueError('CONTROLLED_NO_SDK_ABORT')
   if scenario=='WRONG_HOLDER':
    def wrong_holder():
     try:self.gate.assert_held()
     except ValueError as e:return str(e)
     return 'UNEXPECTED_ACCEPT'
    r=self.operation('wrong-holder-check',wrong_holder)
    if r['value']!='SAME_ORIGINAL_HOLDER_REQUIRED':raise ValueError('WRONG_HOLDER_GUARD_FAILED')
    raise ValueError('WRONG_HOLDER_REJECTED')
   from outer_owner import Owner
   self.owner=Owner(self.home,self.gate,self);rows=self.owner.run_seven();self.require(False)
   result={'schema':'RUNNER_TERMINAL_V1','scope':self.policy['scope'],'mode':self.kind,'initialProofSha256':self.initial_hash,'gateGeneration':self.gate.generation,'scopeStartTick':self.start_tick,'rolesCompleted':len(rows),'scopeClaimIntentionallyRetained':True,'postControlBytes':sum(x['bytes'] for x in self.post),'receiverControlBytes':sum(x['bytes'] for x in self.receiver),'initialProofUnchanged':sha(self.read_file(self.root/'pre_sdk_local_gate-completion-proof.json','terminal-proof-integrity',None,False))==self.initial_hash,'candidateOnlyTerminalWriterCloseNotProven':True,'terminalWriteBytes':0,'batchControlBytesKnown':0,'totalLogicalInboundBytesKnown':0}
   for _ in range(12):
    n=len(encode(result));result['terminalWriteBytes']=n;result['batchControlBytesKnown']=rows[-1]['proof']['batchGroups']['control']+n;result['totalLogicalInboundBytesKnown']=rows[-1]['proof']['batchTextChargedBytesKnown']+n
    if n==len(encode(result)):break
   else:raise ValueError('TERMINAL_FIXED_LENGTH')
   data=encode(result);end_start=rows[-1]['sharedProofWindowStart']
   self.terminal_writer=self.write_file(self.root/'runner-terminal.json',data,'terminal-write','final',initial=False)
   if time.monotonic()-end_start>=self.owner.proof:self.fail('RUNNER_END_SAME_PROOF_WINDOW_STICKY')
   self.require(False)
   if any(t.is_alive() for t in self.pending):self.unknown('TERMINAL_PENDING_BEFORE_RELEASE')
   release=self.gate.release();self.owner.claim_release=release;self.require(False)
   self.terminal=dict(result,scopeClaimIntentionallyRetained=False,claimRelease=release,terminalWriterReturned=True)
   self.finished=True;return self.terminal
  except (ValueError,TypeError,KeyError) as e:self.fail(str(e));raise
  finally:
   if self.gate is not None and self.gate.lease is not None and not self.gate.released:
    if any(t.is_alive() for t in self.pending):self.unknown('RUNNER_PENDING_AT_RELEASE')
    self.gate.fail(self.failure or 'RUNNER_NO_SUCCESS');self.abort_release=self.gate.release()
   if self in RUNNER_CUSTODY:RUNNER_CUSTODY.remove(self)

def main(argv=None):
 parser=argparse.ArgumentParser(description='Exact preauthorized VideoKit production runner. Default denies.')
 parser.add_argument('--mode',choices=('live','fixture'));parser.add_argument('--permit');parser.add_argument('--permit-sha256');parser.add_argument('--approval');parser.add_argument('--approval-sha256');a=parser.parse_args(argv)
 r=None
 try:
  r=ProductionRunner(a.mode,a.permit,a.permit_sha256,a.approval,a.approval_sha256);result=r.run();print(json.dumps(result,separators=(',',':')));return 0
 except (ValueError,TypeError,KeyError) as e:
  metadata={'started':r is not None and r.gate is not None and r.gate.attempted,'metadataAmountUnknown':None,'metadataBytesKnown':None}
  if metadata['started']:
   metadata.update(metadataAmountUnknown=r.gate.metadata_amount_unknown,metadataBytesKnown=sum(x['bytes'] for x in r.gate.events if x['event']=='checker-native-metadata-known'))
   if r.gate.checker_stats is not None:metadata.update(imageHashBytesKnown=r.gate.checker_stats['imageHashBytes'],imageHashBytesReservedUnknown=r.gate.checker_stats['imageHashBytesReservedUnknown'],imageHashAmountUnknown=r.gate.checker_stats['imageHashAmountUnknown'])
  print(json.dumps({'status':'REJECTED','reason':str(e),'mode':a.mode,'source':'LOCAL_ROUTE_COMPAT01','liveCallsNotImplied':True,'metadata':metadata},separators=(',',':')));return 2
if __name__=='__main__':
 sys.modules['production_runner']=sys.modules[__name__]
 raise SystemExit(main())
