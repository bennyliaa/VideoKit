"""Fixed facts preauthorization. External CLI digest is a trust input, not an issuer.

No legacy-authority synthesis; no signing/IPC or qualification issuance.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,os,threading,uuid,time
B=Path(__file__).resolve().parents[1]
COORDINATOR='01a107c3-2bf9-7fa0-94a0-234258ca6774'
KEYS=set('schema mode sourceThreadId sourceTurnId notBeforeUtc expiresUtc scope planId runId nonce home evidenceRoot policySha256 sourceSealSha256 gateSourcesSha256 collectorSha256 binderSha256 entrySha256 runtimeIdentitySha256 sdk factPlanSha256 device queries limits'.split())
LIMITS=dict(wholeSeconds=90,gateSeconds=30,qualificationSeconds=15,outerSeconds=30,proofSeconds=10,sdkChildren=1,stdoutBytes=139264,stderrBytes=8192,combinedBytes=147456,concurrency=1,retry=0)
USED=set()
def fail(code):raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def decode(raw):
 if type(raw) is not bytes or not 1<=len(raw)<=16384:fail('PREAUTH_BYTES')
 def pairs(xs):
  d={};seen=set()
  for k,v in xs:
   if k.casefold() in seen:fail('PREAUTH_DUPLICATE_FIELD')
   seen.add(k.casefold());d[k]=v
  return d
 return json.loads(raw.decode('utf-8','strict'),object_pairs_hook=pairs,parse_constant=lambda _:fail('PREAUTH_NONFINITE'))
def same(a,b):
 if type(a) is not type(b):return False
 if type(a) is dict:return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if type(a) is list:return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b
def digest(v):return type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None and v!='0'*64
def utc(v):
 if type(v) is not str or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?\+00:00',v):fail('PREAUTH_UTC')
 return datetime.fromisoformat(v)
def uuid_text(v):
 try:return type(v) is str and str(uuid.UUID(v))==v
 except ValueError:return False
def validate(raw,approved_template_sha256,policy,pins,now=None):
 # The trusted invocation supplies this digest, never default to sha(raw).
 if type(raw) is not bytes or not digest(approved_template_sha256) or sha(raw)!=approved_template_sha256:fail('PREAUTH_EXTERNAL_HASH')
 t=decode(raw)
 if type(t) is not dict or set(t)!=KEYS:fail('PREAUTH_SCHEMA')
 if t['schema']!='GLOBAL_IDLE_FACT_PREAUTH_V1' or t['mode'] not in ('LIVE','OFFLINE_FIXTURE'):fail('PREAUTH_KIND_MODE')
 if t['sourceThreadId']!=COORDINATOR or not uuid_text(t['sourceTurnId']):fail('PREAUTH_SOURCE')
 if not uuid_text(t['nonce']) or not uuid_text(t['planId']):fail('PREAUTH_NONCE_PLAN')
 if type(t['runId']) is not str or not re.fullmatch('D1MA02-[A-Z0-9_-]{1,32}',t['runId']):fail('PREAUTH_RUN')
 for k in ('scope','policySha256','sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256'):
  if not digest(t[k]):fail('PREAUTH_HASH_TYPE:'+k)
 if not same(t['limits'],LIMITS):fail('PREAUTH_LIMITS')
 if not same(t['sdk'],pins['sdk']) or not same(t['device'],dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0)):fail('PREAUTH_SDK_DEVICE')
 if not same(t['queries'],pins['queries']):fail('PREAUTH_QUERIES')
 for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256'):
  if t[k]!=pins[k]:fail('PREAUTH_PIN:'+k)
 if type(policy) is not dict or sha(encode(policy))!=t['policySha256']:fail('PREAUTH_POLICY')
 mode='OFFLINE_FIXTURE' if policy.get('mode')=='OFFLINE_FIXTURE' else 'LIVE' if policy.get('mode')=='PRODUCTION' else None
 if t['mode']!=mode:fail('PREAUTH_POLICY_MODE')
 for k in ('scope','planId','runId','evidenceRoot'):
  if type(t[k]) is not str or t[k]!=policy.get(k):fail('PREAUTH_POLICY_ID:'+k)
 if t['home']!=str(Path(t['evidenceRoot']).parent) or Path(t['evidenceRoot']).name!='outputs':fail('PREAUTH_HOME')
 for k in ('home','evidenceRoot'):
  if type(t[k]) is not str or not Path(t[k]).is_absolute() or str(Path(t[k]).resolve())!=t[k]:fail('PREAUTH_CANONICAL_PATH')
 for k in ('gateSourcesSha256','runtimeIdentitySha256'):
  if policy.get(k)!=t[k]:fail('PREAUTH_POLICY_PIN:'+k)
 if policy.get('entrySha256')!=pins['captureSha256'] or policy.get('outerOwnerSha256')!=pins['ownerSha256'] or policy.get('planSha256')!=pins['rolePlanSha256']:fail('PREAUTH_POLICY_SOURCES')
 lo=utc(t['notBeforeUtc']);hi=utc(t['expiresUtc']);now=now or datetime.now(timezone.utc)
 if not 0<(hi-lo).total_seconds()<=90 or not lo<=now<hi:fail('PREAUTH_WINDOW')
 return t
def load_pins(read):
 from fact_collector import QUERIES,SDK,SDK_SHA
 raw=read(B/'reference/runner-source-seal.json');seal=json.loads(raw);sources=seal['sources']
 # Gate independently hashes its fixed sources (including this binder+schema+CLI).
 return dict(sourceSealSha256=sha(raw),gateSourcesSha256=sources['reference/gate-sources.json'],collectorSha256=sources['tools/fact_collector.py'],binderSha256=sources['tools/fact_preauth.py'],entrySha256=sources['tools/facts_entry.py'],runtimeIdentitySha256=sources['reference/current-runtime-identity.json'],factPlanSha256=sources['reference/fact-plan.json'],captureSha256=sources['tools/capture_android02.ps1'],ownerSha256=sources['tools/outer_owner.py'],rolePlanSha256=sources['reference/exact-seven-role-plan.json'],sdk=dict(path=SDK,sha256=SDK_SHA),queries=[dict(id=i,command=c) for i,c in QUERIES])
def binding_bytes(actual,expected):
 decode(actual)
 if type(expected) is not bytes or actual!=expected:fail('PREAUTH_BINDING_ONCE_BYTES')
 return True
class PreparedFacts:
 def __init__(self,raw,approved_template_sha256,policy):
  self.owner=(os.getpid(),threading.get_ident());self.bytes=raw;self.approved=approved_template_sha256
  self.policy=decode(encode(policy));self.sourceBytes=0;self.sourceReads=0;self.controlBytes=len(raw)+len(encode(policy));self.gate=None;self.used=False;self.prepareEntered=False;self.binding=None
  def read(p):
   from entry_gates import no_links
   no_links(p);b=Path(p).read_bytes();self.sourceBytes+=len(b);self.sourceReads+=1
   if self.sourceBytes>268435456 or self.sourceReads>64:fail('PREAUTH_SOURCE_BOUND')
   return b
  self.pins=load_pins(read);self.template=validate(raw,approved_template_sha256,self.policy,self.pins)
  # The actual fixed gate/collector/binder/entry pins are verified before Gate.
  for rel,k in [('reference/gate-sources.json','gateSourcesSha256'),('tools/fact_collector.py','collectorSha256'),('tools/fact_preauth.py','binderSha256'),('tools/facts_entry.py','entrySha256'),('reference/fact-plan.json','factPlanSha256')]:
   if sha(read(B/rel))!=self.pins[k]:fail('PREAUTH_CURRENT_SOURCE:'+rel)
  key=(self.template['scope'],self.template['planId'],self.template['runId'],self.template['nonce'])
  if key in USED:fail('PREAUTH_REPLAY')
  USED.add(key) # no refund/rearm, including later known rejection
 def holder(self):
  if self.owner!=(os.getpid(),threading.get_ident()):fail('PREAUTH_ORIGINAL_OWNER')
 def prepare(self):
  self.holder()
  if self.prepareEntered or self.used:fail('PREAUTH_PREPARE_ONCE')
  self.prepareEntered=True
  validate(self.bytes,self.approved,self.policy,self.pins)
  from entry_gates import GateSession,no_links
  home=Path(self.template['home']);no_links(home)
  if (home/'outputs').exists():fail('PREAUTH_FRESH_OUTPUT_REQUIRED')
  (home/'outputs').mkdir(parents=True,exist_ok=False)
  self.gate=GateSession(home,policy=self.policy,pre_events=[dict(event='preauth-template-policy-read',bytes=self.controlBytes)])
  self.gate.source_bytes+=self.sourceBytes;self.gate.source_reads+=self.sourceReads
  if self.gate.source_bytes>268435456 or self.gate.source_reads>64:fail('SOURCE_READ_BUDGET')
  self.gate.whole=90 # narrower facts whole window, no expansion of original gates
  self.gate.prepare();return self.gate
 def current(self,gate):
  from entry_gates import GateSession
  self.holder()
  if type(gate) is not GateSession or gate is not self.gate or not gate.prepared or gate.accepted or gate.sdk_owner is not None or gate.released or gate.failure:fail('PREAUTH_ORIGINAL_PREPARED_GATE')
  if gate.scope!=self.template['scope'] or not same(gate.policy,self.policy):fail('PREAUTH_GATE_IDENTITY')
  gate.assert_held();gate.observe(gate.proof_start,10);gate.require()
  validate(self.bytes,self.approved,self.policy,self.pins)
 def bind(self,gate):
  self.current(gate)
  if self.used or self.binding is not None:fail('PREAUTH_BIND_ONCE')
  self.used=True
  from entry_gates import decode as gate_decode
  binding=dict(schema='GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1',mode=self.template['mode'],preauthSha256=self.approved,scope=gate.scope,planId=gate.policy['planId'],runId=gate.policy['runId'],nonce=self.template['nonce'],generation=gate.generation,ownerPid=gate.pid,ownerThread=gate.thread,claimFileId=gate.file_id,scopeStartTick=gate.start_tick,proofStartTick=gate.proof_start_tick,routeProofSha256=gate_decode(gate.receipt_bytes)['routeSha256'],initialProofSha256=gate.proof_hash,gateReceiptSha256=sha(gate.receipt_bytes),sourceSealSha256=self.pins['sourceSealSha256'],gateSourcesSha256=gate.manifest_hash,binderSha256=self.pins['binderSha256'],boundAtUtc=datetime.now(timezone.utc).isoformat())
  self.binding=encode(binding)
  gate.charge('preauth-binding-create',len(self.binding));return self.binding
 def receive(self,gate,binding,capture,fixture_argv=None):
  self.current(gate)
  if not self.used or getattr(self,'receiveEntered',False):fail('PREAUTH_BINDING_ONCE_BYTES')
  binding_bytes(binding,self.binding)
  self.receiveEntered=True # never refund or rearm
  d=decode(binding)
  from entry_gates import decode as gate_decode
  if d['generation']!=gate.generation or d['ownerPid']!=gate.pid or d['ownerThread']!=gate.thread or d['claimFileId']!=gate.file_id or d['initialProofSha256']!=gate.proof_hash or d['gateReceiptSha256']!=sha(gate.receipt_bytes) or d['routeProofSha256']!=gate_decode(gate.receipt_bytes)['routeSha256'] or d['scopeStartTick']!=gate.start_tick or d['proofStartTick']!=gate.proof_start_tick:fail('PREAUTH_BINDING_ORIGINAL_CHANGED')
  gate.charge('preauth-template-receiver',len(self.bytes));gate.charge('preauth-binding-receiver',len(binding))
  # Re-read current source pins using original gate source accounting.
  for rel,k in [('reference/runner-source-seal.json','sourceSealSha256'),('tools/fact_preauth.py','binderSha256'),('tools/fact_collector.py','collectorSha256'),('tools/facts_entry.py','entrySha256'),('reference/fact-plan.json','factPlanSha256')]:
   if sha(gate.source_read(B/rel))!=self.pins[k]:fail('PREAUTH_RECEIVER_SOURCE:'+rel)
  from fact_collector import OwnedFactCapture
  if type(capture) is not OwnedFactCapture or capture.entered:fail('PREAUTH_ORIGINAL_CAPTURE')
  result=capture._capture_authorized(gate,fixture_argv,self.template['mode'],utc(self.template['expiresUtc']),self.pins['collectorSha256'],self.pins['factPlanSha256'],d['routeProofSha256'],dict(schema='GLOBAL_IDLE_FACT_CAPTURE_V2',authorizationKind='GLOBAL_IDLE_FACT_PREAUTH_V1',externalPreauthSha256=self.approved,runtimeBindingSha256=sha(binding)))
  return result
