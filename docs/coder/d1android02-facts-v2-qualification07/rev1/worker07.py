"""One serial batch. Original product functions and full PS entry, no extraction."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import os,sys,json,uuid,time,copy,subprocess,threading,hashlib
H=Path(__file__).resolve().parent;sys.path[:0]=[str(H),str(H/'tools'),str(H/'selfchecks')]
from facts_contract import enc,sha,dec
from call_plan07 import facts_argv,review_argv,aux_argv,BUDGET_CASES
from production_runner import ProductionRunner,RUNNER_CUSTODY,LIMITS,OPS
from outer_capture import Capture,CUSTODY
from evidence_io import Journal
from facts_qualification import FactsBundle,candidate,qualify
from immutable_evidence import create,FILE_PENDING,ORIGINAL_FILE_EVENTS
from entry_gates import CUSTODY as GATE_CUSTODY
from fact_collector import CUSTODY as FACT_CUSTODY
from capture_origin import require as require_origin
from write_guard import install as install_writes,allowed,EVENTS
PLAN=json.loads((H/'reference/plan07.json').read_bytes());PROFILE=json.loads((H/'reference/profile07.json').read_bytes());W=Path(PLAN['work']);START=PLAN['batchStart'];ORIGINAL=subprocess.Popen;PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe';results=[];caps=[];runners=[];stop=False;bundle=None;wires={}
def save(p,d):allowed(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(enc(d))
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def digest(p):return sha(Path(p).read_bytes())
sys.path.insert(0,str(H/'driver'))
from driver_guard07 import Guard

guard=Guard()
class Control:
 def __init__(self):self.stop=False
 def request(self,r):self.stop=True
 def poll(self):return self.stop
 def returned(self):return True
control=Control()
def child(a,label,seconds=90):
 guard.check(a,dict(executable=a[0],cwd=None,env=None,shell=False,close_fds=True,stdin=-3,stdout=-1,stderr=-1))
 root=W/'children'/label;root.mkdir(parents=True);p=dict(argv=a,cwd=None,env=None,profile=label);c=Capture(p,copy.deepcopy(p),Journal(root),control,guard);caps.append(c);c.launch(guard,seconds);ans=c.collect();save(root/'return.json',dict(returned=c.returned,exitCode=c.exit_code,counts=c.counts,facts=c.facts,disposition=ans,failure=c.failure))
 if not c.returned or ans.startswith('RETAIN'):
  while True:time.sleep(.1)
 return c
def qualification():
 rows=[]
 for mode,code in [('ok',0),('fail',7),('PS',0)]:
  a=[PY,'-I','-X','utf8','-B',str(H/'driver/context_child.py'),mode] if mode!='PS' else [PS,'-NoProfile','-NonInteractive','-File',str(H/'driver/owned_child.ps1')]
  c=child(a,'qual-'+mode,5);assert c.exit_code==code and not c.buffers[1] and c.failure is None and time.monotonic()-c.start<5
  rows.append(dict(mode=mode,exitCode=code,originalReturned=c.returned))
 return rows
def facts():
 f=PLAN['facts'];root=Path(f['root']);c=child(facts_argv(PLAN),'facts')
 assert c.exit_code==0 and not c.buffers[1],bytes(c.buffers[0])[:2000]
 summary=load(Path(f['home'])/'outputs/fact-source-summary.json');assert summary['sourceReads']==summary['plannedReads']==64 and summary['sourceBytes']==summary['plannedBytes'] and summary['admittedBeforeUsed'] and summary['originalFactsBodyReturned']
 rows=[]
 for e in summary['chunks']:
  assert digest(e['path'])==e['sha256'] and Path(e['path']).stat().st_size==e['bytes'];rows+=load(e['path'])['rows']
 planned=load(H/'reference/fact-source-plan07.json')['rows'];assert len(rows)==len(planned)==64
 assert all(all(a[k]==b[k] for k in ('index','path','kind','chargedBytes','scope')) for a,b in zip(rows,planned))
 assert all(x['originalCloseReturned'] for x in rows if x['kind'] in ('read','preauth-read','adopted-read')) and all(x.get('fixedHelperReturned') for x in rows if x['kind']=='runtime-reservation')
 save(W/'actual-facts-complete-source-audit.json',dict(summary=summary,rows=rows,planned=planned,allMatched=True))
 global bundle;bundle=FactsBundle(c,(root/'template.json').read_bytes(),(root/'policy.json').read_bytes());assert len(bundle.raw)==139264 and len(bundle.parsed['systemPackages'])==128;save(W/'facts-bundle.json',dict(evidence=bundle.evidence,outer=bundle.outer_return,packetRef=bundle.packetRef));return dict(rawBytes=len(bundle.raw),packetBytes=len(bundle.outer),originalReturned=True)
def reviews():
 if bundle is None:return dict(status='NOT_RUN_DEPENDENCY')
 out=[]
 for label,d in PLAN['targets'].items():
  require_origin(bundle.actual);c=candidate(bundle,d['target']);request=dict(schema='OFFLINE_REVIEW_REQUEST_V1',fixtureOnly=True,candidateUtf8=enc(c).decode(),bundle=bundle.evidence,outerReturn=bundle.outer_return,preauthUtf8=bundle.preauth.decode(),policyUtf8=bundle.policy.decode(),packetRef=bundle.packetRef,target=d['target'],serviceCount=0,reviewTurnId=str(uuid.uuid4()),processChars=0);save(Path(d['request']),request)
  c=child(review_argv(PLAN,label),'review-'+label);assert c.exit_code==0 and not c.buffers[1],bytes(c.buffers[1])[:1500];reply=load(Path(d['reply'])/'reply.json') if (Path(d['reply'])/'reply.json').exists() else json.loads(c.buffers[0]);raw=Path(reply['reviewPath']).read_bytes();ev={k:v.encode() for k,v in load(reply['evidencePath']).items()};wires[label]=qualify(bundle,d['target'],raw,reply['approvedReviewSha256'],ev);save(W/('wire-'+label+'.json'),wires[label]);out.append(dict(label=label,reviewerPid=c.original.pid,originalReturned=True,wireBytes=len(enc(wires[label])),factAge=(datetime.now(timezone.utc)-datetime.fromisoformat(bundle.receipt['collectedAtUtc'])).total_seconds(),realHumanApproval=False))
 return out
def production(label):
 if label not in wires:return dict(status='NOT_RUN_DEPENDENCY')
 d=PLAN['targets'][label];folder=Path(d['folder']);home=Path(d['home']);plan=load(H/'reference/exact-seven-role-plan.json');sources=load(H/'reference/runner-source-seal.json')['sources'];now=datetime.now(timezone.utc);proto=ProductionRunner.__new__(ProductionRunner);proto.plan=plan;proto.root=home/'outputs';modes=['identity_wrong' if label=='wrong-firmware' else 'identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'];rpath=Path(d['reply'])/'review.json'
 p=dict(schema='VIDEOKIT_PRODUCTION_RUNNER_PERMIT_V2',authorizationId=str(uuid.uuid4()),mode='OFFLINE_FIXTURE',approvedForExecution=True,notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=299)).isoformat(),planId=d['target']['planId'],runId=d['target']['runId'],scope=d['target']['scope'],home=str(home),evidenceRoot=str(home/'outputs'),sources=sources,sourceSeal=dict(path=str(H/'reference/runner-source-seal.json'),sha256=digest(H/'reference/runner-source-seal.json')),review=dict(path=str(rpath),sha256=digest(rpath)),product=plan['product'],tools=[dict(path=PY,bytes=Path(PY).stat().st_size,sha256=digest(PY))],roles=[proto.fixture_slot(i,m) for i,m in enumerate(modes)],operations=list(OPS),limits=dict(LIMITS),fixtureScenario='WRONG_FACT_FIRMWARE' if label=='wrong-firmware' else 'NONE',routeBackend='WIN32_OWNER_PID_V1',globalIdleQualification=wires[label]);save(folder/'permit.json',p);ph=digest(folder/'permit.json');instruction='EXECUTE_OFFLINE_PERMIT '+ph;a=dict(schema='VIDEOKIT_RUNNER_APPROVAL_EVIDENCE_V1',mode='OFFLINE_FIXTURE',evidenceKind='OFFLINE_TEST_ONLY',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),instructionText=instruction,instructionSha256=sha(instruction.encode()),approvedPermitSha256=ph);save(folder/'approval.json',a)
 r=ProductionRunner('fixture',str(folder/'permit.json'),ph,str(folder/'approval.json'),digest(folder/'approval.json'));runners.append(r);error=None;terminal=None;replacement=None
 if label=='receipt-replace':
  original_reader=r.read_receipt
  def replace_then_read(ref,owner,role):
   nonlocal replacement
   from immutable_evidence import original_file,identity
   path=Path(ref['path']);retained=path.with_name('identity-original-receipt-retained.json');allowed(path);allowed(retained)
   with original_file(path,'rb') as f:before=identity(f,path);raw=f.read(8193)
   assert before['fileId']==ref['fileId'] and sha(raw)==ref['sha256']
   path.rename(retained);created=create(raw,str(path.parent),path.name)
   replacement=dict(originalRef=ref,retained=str(retained),replacementRef=created,sameBytes=created['sha256']==ref['sha256'],differentId=created['fileId']!=ref['fileId'])
   save(W/'receipt-replacement-before-original-reader.json',replacement)
   return original_reader(ref,owner,role)
  r.read_receipt=replace_then_read
 if label=='positive':
  original_reader=r.read_receipt;negative_receiver_rows=[]
  def validate_receiver_then_read(ref,owner,role):
   if role=='identity':
    for key,value,want in [('path',ref['path']+'.wrong','ORIGINAL_RECEIPT_FIXED_PATH'),('volumeId',str((int(ref['volumeId'])+1)%4294967296),'ORIGINAL_RECEIPT_FILE_IDENTITY'),('fileId',str(int(ref['fileId'])+1),'ORIGINAL_RECEIPT_FILE_IDENTITY'),('sha256','0'*64,'ORIGINAL_RECEIPT_ORIGINAL_BYTES')]:
     bad=dict(ref);bad[key]=value
     try:original_reader(bad,owner,role);why='ACCEPT'
     except ValueError as e:why=str(e)
     negative_receiver_rows.append(dict(field=key,reason=why,expected=want));save(W/'receipt-reader-negative-originals.json',negative_receiver_rows);assert why==want
   return original_reader(ref,owner,role)
  r.read_receipt=validate_receiver_then_read

 try:terminal=r.run(fixture_prefix=2)
 except (ValueError,TypeError,KeyError) as e:error=str(e)
 detail=dict(label=label,error=error,replacement=replacement,receiptReads=r.receipt_reads,controlAdmission=r.control_admission,runnerSourceFeeEvents=r.source_fee_events,terminal=terminal,runnerFailure=r.failure,gateReleased=r.gate.released,gateSourcesBytes=r.gate.source_bytes,gateSourcesReads=r.gate.source_reads,runnerSourceBytes=r.source_bytes,runnerSourceReads=r.source_reads,sourceEvents=r.owner.source_budget.events if r.owner and hasattr(r.owner,'source_budget') else [],records=r.owner.records if r.owner else [],pending=r.owner.source_budget.pending if r.owner and hasattr(r.owner,'source_budget') else None)
 save(W/('production-'+label+'.json'),detail)
 if label=='positive':
  assert error is None and terminal['rolesCompleted']==2 and [x['console']['semantic'] for x in r.owner.records]==['PASS','PASS'],error
  for rec in r.owner.records:
   bound=next(x for x in r.control_admission['roles'] if x['role']==rec['id']);co=rec['console'];assert co['proofReadBytes']<=bound['functionalReadBytes'] and co['recordWriteBytesKnown']+2*co['consoleBytes']+co['proofReadBytes']<=bound['localControlBytes']
  assert terminal['sourceBudgetProbe']['finalGateReads']==64 and terminal['sourceBudgetProbe']['reject65']=='SOURCE_READ_BUDGET' and terminal['sourceBudgetProbe']['ownerNextRoleReject']=='SOURCE_OWNER_BUDGET_BEFORE_LAUNCH'
 elif label=='wrong-firmware':assert error and r.owner and r.owner.records[0]['console']['semantic']=='FACT_IDENTITY_FIRMWARE_DISAGREEMENT',error
 else:
  assert error=='ORIGINAL_RECEIPT_FILE_IDENTITY' and replacement['sameBytes'] and replacement['differentId'] and r.receipt_reads[-1]['readBytes']==0 and r.receipt_reads[-1]['originalCloseReturned'],error
  assert detail['pending'] is not None and (r.root/'identity-outer-return.json').is_file() and len(r.owner.records)==0
  assert r.gate.released
  return dict(label=label,reason=error,pendingReservationRetained=True,originalControllerReturned=True,originalReaderClosed=True,contentReadBytes=0)
 assert r.gate.released and detail['pending'] is None and all(x['merged'] for x in detail['sourceEvents'])
 return dict(label=label,roles=len(detail['records']),sourceEvents=len(detail['sourceEvents']),gateSourceBytes=detail['gateSourcesBytes'],gateSourceReads=detail['gateSourcesReads'],runnerSourceBytes=detail['runnerSourceBytes'],runnerSourceReads=detail['runnerSourceReads'],gateOriginalRelease=True,expectedReject=label=='wrong-firmware')
def budget_models():
 if not wires:return dict(status='NOT_RUN_DEPENDENCY')
 from fixture_inputs import text
 d=PLAN['targets']['positive']['target'];txt=text();wire=wires['positive'];ctx=dict(scope=d['scope'],runId=d['runId'],mode='OFFLINE_FIXTURE',rawSha256=sha(txt.encode()),rawBytes=len(txt.encode()),captureBodyReturned=True,sourceSealSha256=d['sourceSealSha256'],planSha256=d['planSha256'],reviewEvidenceSha256=wire['reviewEvidenceSha256'],nowUtc=datetime.now(timezone.utc).isoformat(),targetPlanId=d['planId'],evidenceRoot=d['evidenceRoot']);root=W/'models/outputs/v2-authority';ref=create(b'x',str(root),'budget-one-byte.json');save(W/'budget-input.json',dict(schema='INDEPENDENT_BUDGET_INPUT_V1',artifactRoot=str(H/'selfchecks'),candidateRoot=str(H),admissionPath=str(H/'tools/admission_checks.ps1'),admissionSha256=digest(H/'tools/admission_checks.ps1'),ref=ref,root=str(root),name='budget-one-byte.json',wire=wire,context=ctx,expectedFingerprint=bundle.parsed['fingerprint'],expectedCaseIds=BUDGET_CASES));c=child(aux_argv(PLAN,'budget'),'budget');assert (W/'budget-result.json').is_file(),dict(reason='HELPER_RESULT_MISSING',originalExit=c.exit_code,stdout=bytes(c.buffers[0])[:1000].decode(errors='replace'),stderr=bytes(c.buffers[1])[:1000].decode(errors='replace'));out=load(W/'budget-result.json');assert out['complete'] and out['observedCaseIds']==BUDGET_CASES and out['realAuthority'] is False and all(x['pass'] and x['reason']==x['want'] for x in out['results']);assert c.exit_code==0 and not c.buffers[1] and out['allPassed'],dict(out=out,stderr=bytes(c.buffers[1])[:1000]);return out
def regression():
 from contract_cases import make
 from independent_cases_original import cases
 from contract03_cases import cases as additional
 save(W/'v1-input.json',make()+cases(H)+additional());c=child(aux_argv(PLAN,'v1'),'v1');out=load(W/'v1-result.json');assert c.exit_code==0 and not c.buffers[1] and len(out)==346 and all(x['pass'] for x in out);return dict(cases=346,passed=346)
def revision_return_proof():
 owners=[]
 for r in runners:
  g=r.gate;o=r.owner
  waits=[dict(x) for x in (o.held if o else []) if type(x) is dict and 'handleClose' in x]
  writers=[dict(x) for x in (o.held if o else []) if type(x) is dict and 'closeReturned' in x and 'writeReturned' in x]
  alive=any(isinstance(t,threading.Thread) and t.is_alive() for t in r.pending+(g.pending if g else [])+(o.held if o else []))
  gates=[dict(name=x['name'],returned=x['returned'],error=x['error']) for x in (g.held if g else []) if type(x) is dict and 'name' in x and 'returned' in x and 'error' in x]
  good=not alive and all(x['returned'] and x['error'] is None for x in gates) and all(x['wait'] and x['stdoutClose'] and x['stderrClose'] and x['handleClose'] and x['error'] is None for x in waits) and all(x['closeReturned'] and x['writeReturned'] and x['error'] is None for x in writers) and all(x['originalReturned'] for x in r.source_fee_events) and (g is None or g.lease is None or g.released and g.lease.closed)
  owners.append(dict(scope=r.permit['scope'],allProven=good,liveThreads=alive,gateOriginals=gates,outerOriginalReturns=waits,originalWriters=writers,sourceFeeEvents=r.source_fee_events,claimReleasedOrNeverHeld=(g is None or g.lease is None or g.released and g.lease.closed)))
 aux=all(c.returned and all(c.facts.get(k) for k in ('originalWaitReturned','readersJoined','streamsClosed','handleCloseReturned')) for c in caps)
 return dict(allOriginalsProven=aux and all(x['allProven'] for x in owners) and not CUSTODY and not GATE_CUSTODY and not FACT_CUSTODY and not FILE_PENDING and not RUNNER_CUSTODY,auxOriginalsProven=aux,owners=owners)

for x in PROFILE:assert digest(H/x['path'])==x['sha256'],x['path']
for p,h in PLAN['inputPins'].items():assert digest(p)==h
install_writes(guard);sys.addaudithook(guard.observe);subprocess.Popen=guard.construct
try:
 for name,fn in [('qualification',qualification),('actual-max-facts',facts),('independent-review',reviews),('production-prefix-positive',lambda:production('positive')),('production-wrong-firmware',lambda:production('wrong-firmware')),('production-receipt-replacement',lambda:production('receipt-replace')),('source-budget-and-reload-models',budget_models),('V1-regression',regression)]:
  began=time.monotonic()
  if stop or control.stop or guard.stop or time.monotonic()-START>=320:results.append(dict(name=name,status='NOT_RUN_STOP_NEW'));continue
  try:detail=fn();results.append(dict(name=name,status='NOT_RUN_DEPENDENCY' if type(detail) is dict and detail.get('status','').startswith('NOT_RUN') else 'PASS',seconds=time.monotonic()-began,detail=detail))
  except BaseException as e:results.append(dict(name=name,status='FAIL',seconds=time.monotonic()-began,error=repr(e)))
  save(H/'evidence'/('group-'+str(len(results))+'.json'),results[-1])
  if CUSTODY or GATE_CUSTODY or FACT_CUSTODY or FILE_PENDING or (name=='qualification' and results[-1]['status']!='PASS'):stop=True
finally:
 subprocess.Popen=ORIGINAL
 out=dict(schema='QUALIFICATION07_RESULT_V1',revision=PLAN['revision'],revisionReturnProof=revision_return_proof(),batchElapsed=time.monotonic()-START,groups=results,allPassed=len(results)==8 and all(x['status']=='PASS' for x in results),seconds=time.monotonic()-START,hostPopen=guard.calls,audit=guard.events,auxOriginalsReturned=all(c.returned for c in caps),custody=dict(capture=len(CUSTODY),gate=len(GATE_CUSTODY),fact=len(FACT_CUSTODY),file=len(FILE_PENDING),runner=len(RUNNER_CUSTODY)),fileEvents=[{k:v for k,v in x.items() if k!='original'} for x in ORIGINAL_FILE_EVENTS],sourceChanged=[x['path'] for x in PROFILE if digest(H/x['path'])!=x['sha256']],writeEvents=EVENTS,SDK=0,Git=0,realHumanApproval=False,D1='NOT_PASSED',M0='NOT_STARTED');save(H/'evidence/result.json',out);print(json.dumps(dict(allPassed=out['allPassed'],seconds=out['seconds'],groups=[(x['name'],x['status']) for x in results],custody=out['custody'])))
if not out['allPassed']:raise SystemExit(2)
