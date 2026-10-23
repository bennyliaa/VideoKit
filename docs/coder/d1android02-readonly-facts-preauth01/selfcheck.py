"""One fixed 360s offline batch; freeze every source/profile before invoking."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,os,json,time,copy,uuid,threading,subprocess,hashlib
B=Path(__file__).resolve().parent;sys.path[:0]=[str(B),str(B/'tools'),str(B/'selfchecks'),str(B/'driver'),str(B/'driver/reuse')]
from driver_guard import Registry,PY,PS,ORIGINAL,sha
from owned_capture import Capture,CUSTODY as AUX
from evidence_io import Journal
from fact_preauth import PreparedFacts,validate,load_pins,encode,decode,LIMITS,binding_bytes
from entry_gates import GateSession,CUSTODY as GATES
from fact_collector import OwnedFactCapture,CUSTODY as FACTS,validate_fixture_argv,ENV
START=time.monotonic();P=json.loads((B/'reference/profile.json').read_bytes());PLAN=json.loads((B/'reference/batch-plan.json').read_bytes());W=B/'selfchecks/work';W.mkdir(exist_ok=True)
registry=Registry(P,START);results=[];captures=[];stopped=False
class Control:
 def __init__(self):self.stop=False;self.reasons=[]
 def request(self,r):self.stop=True;self.reasons.append(r)
 def poll(self):return self.stop
 def returned(self):return True
control=Control()
def save(path,d):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encode(d))
def reject(fn,expected=None):
 try:fn()
 except (ValueError,TypeError,KeyError) as e:
  if expected is not None:assert str(e)==expected,(expected,str(e))
  return str(e)
 raise AssertionError('EXPECTED_REJECTION')
def child(argv,qual=False):
 root=W/('aux-'+str(len(captures)));root.mkdir();env=P['qualificationEnv'] if qual else None;cwd=P['qualificationCwd'] if qual else None
 plan=dict(argv=list(argv),cwd=cwd,env=env,profile='python_ok' if argv[0]==PY else 'powershell_ok')
 registry.check(argv,dict(executable=argv[0],cwd=cwd,env=env,shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE))
 j=Journal(root);c=Capture(plan,copy.deepcopy(plan),j,control,registry);captures.append(c);c.launch(registry,5 if qual else 80);disposition=c.collect()
 save(root/'observation.json',dict(disposition=disposition,returned=c.returned,facts=c.facts,failure=c.failure,elapsed=time.monotonic()-c.start,exitCode=getattr(c,'exit_code',None),identity=getattr(c,'identity',None),journal=j.facts()))
 if not c.returned or disposition.startswith('RETAIN'):
  control.request('NEW_ORIGINAL_UNKNOWN');save(B/'evidence/PENDING_UNKNOWN.json',dict(disposition=disposition))
  while True:time.sleep(.1)
 return c.exit_code,bytes(c.buffers[0]),bytes(c.buffers[1])
def qualify():
 negatives=[];a=[PY,'-I','-X','utf8','-B',str(B/'driver/reuse/owned_child.py'),'ok'];k=dict(executable=PY,cwd=P['qualificationCwd'],env=P['qualificationEnv'],shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 registry.check(a,k)
 for bad in [[PS,*a[1:]],['D:/Android/SDK/platform-tools/adb.exe',*a[1:]],a+['extra']]:negatives.append(reject(lambda bad=bad:registry.check(bad,k)))
 facts=[]
 for argv,code in [(a,0),([*a[:-1],'fail'],7),([PS,'-NoProfile','-NonInteractive','-File',str(B/'driver/reuse/owned_child.ps1')],0)]:
  c,b,e=child(argv,True);assert c==code and not e and captures[-1].failure is None and time.monotonic()-captures[-1].start<5;facts.append(dict(exitCode=c,originalReturned=True,semantic='PASS' if c==0 else 'KNOWN_NONZERO_FAIL'))
 return dict(actual=facts,pureWrongPrograms=negatives)
def inputs(name):
 p=json.loads((B/'release/capture-policy.json').read_bytes());s=json.loads((B/'reference/runner-source-seal.json').read_bytes())['sources'];home=W/name/'home';root=home/'outputs';plan=str(uuid.uuid4());run='D1MA02-FACTS_'+uuid.uuid4().hex[:8].upper()
 scope=sha('|'.join((plan,s['tools/capture_android02.ps1'],p['productSealSha256'],p['planSha256'],run)).encode())
 p.update(mode='OFFLINE_FIXTURE',scope=scope,planId=plan,runId=run,evidenceRoot=str(root))
 pins=load_pins(lambda x:Path(x).read_bytes());now=datetime.now(timezone.utc)
 t=dict(schema='GLOBAL_IDLE_FACT_PREAUTH_V1',mode='OFFLINE_FIXTURE',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=80)).isoformat(),scope=scope,planId=plan,runId=run,nonce=str(uuid.uuid4()),home=str(home),evidenceRoot=str(root),policySha256=sha(encode(p)),**{k:pins[k] for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256')},sdk=pins['sdk'],device=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0),queries=pins['queries'],limits=dict(LIMITS))
 return p,t,pins
def pure_templates():
 p,t,pins=inputs('pure');raw=encode(t);approved=sha(raw);assert validate(raw,approved,p,pins)==t;cases=[]
 def check(label,d,expected=None,external=None):
  b=encode(d) if type(d) is dict else d
  cases.append(dict(case=label,reason=reject(lambda:validate(b,sha(b) if external is None else external,p,pins),expected)))
 for k in t:
  d=copy.deepcopy(t);d.pop(k);check('delete:'+k,d,'PREAUTH_SCHEMA')
  d=copy.deepcopy(t);d[k]=None;check('null:'+k,d)
 d=copy.deepcopy(t);d['extra']=True;check('extra',d,'PREAUTH_SCHEMA')
 check('case-duplicate',raw.replace(b'"schema":',b'"Schema":"x","schema":',1),'PREAUTH_DUPLICATE_FIELD')
 check('default-external',t,'PREAUTH_EXTERNAL_HASH',external='')
 check('wrong-external',t,'PREAUTH_EXTERNAL_HASH',external='a'*64)
 d=copy.deepcopy(t);d['sourceTurnId']=str(uuid.uuid4());check('caller-generated-not-external-approved',d,'PREAUTH_EXTERNAL_HASH',external=approved)
 for k in ('scope','sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256','policySha256'):
  d=copy.deepcopy(t);d[k]='1'*64;check('changed:'+k,d)
 for k in LIMITS:
  for v in (True,float(LIMITS[k]),LIMITS[k]+1):
   d=copy.deepcopy(t);d['limits'][k]=v;check('budget:'+k+':'+repr(v),d,'PREAUTH_LIMITS')
 for k in ('sdk','device'):
  for field in t[k]:
   d=copy.deepcopy(t);d[k].pop(field);check('nested-delete:'+k+':'+field,d)
   d=copy.deepcopy(t);d[k][field]=True;check('nested-change:'+k+':'+field,d)
 for i in range(7):
  for field in ('id','command'):
   d=copy.deepcopy(t);d['queries'][i][field]='UNAPPROVED';check('query:'+str(i)+':'+field,d,'PREAUTH_QUERIES')
 d=copy.deepcopy(t);d['queries'].reverse();check('query-order',d,'PREAUTH_QUERIES')
 for label,lo,hi in [('expired',-100,-10),('future',10,80),('too-long',-1,91),('reversed',2,1)]:
  d=copy.deepcopy(t);now=datetime.now(timezone.utc);d.update(notBeforeUtc=(now+timedelta(seconds=lo)).isoformat(),expiresUtc=(now+timedelta(seconds=hi)).isoformat());check(label,d,'PREAUTH_WINDOW')
 for k,v in [('schema','GLOBAL_IDLE_FACT_AUTHORITY_V1'),('mode','LIVE'),('mode','live'),('sourceThreadId',str(uuid.uuid4())),('nonce','OLD'),('planId','OLD'),('home',str(B/'elsewhere')),('runId','OLD')]:
  d=copy.deepcopy(t);d[k]=v;check('identity:'+k+':'+v,d)
 # No constructor or existing claim is involved in these gate identity models.
 ticket=object.__new__(PreparedFacts);ticket.owner=(os.getpid(),threading.get_ident());ticket.gate=object();ticket.template=t;ticket.policy=p
 cases.append(dict(case='wrong-original-gate-model',reason=reject(lambda:ticket.current(object()),'PREAUTH_ORIGINAL_PREPARED_GATE')))
 ticket.owner=(os.getpid(),-1);cases.append(dict(case='wrong-owner-model',reason=reject(lambda:ticket.current(object()),'PREAUTH_ORIGINAL_OWNER')))
 # Registry model covers exact scope/plan/run/nonce already consumed.
 ticket2=PreparedFacts(raw,approved,p);cases.append(dict(case='preauth-replay-before-gate',reason=reject(lambda:PreparedFacts(raw,approved,p),'PREAUTH_REPLAY')));assert ticket2.gate is None
 argv=[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'];assert validate_fixture_argv(argv)==argv
 bad=argv.copy();bad[0]='D:/Android/SDK/platform-tools/adb.exe';cases.append(dict(case='wrong-fact-program-pure',reason=reject(lambda:validate_fixture_argv(bad),'FACT_FIXTURE_ARGV')))
 save(W/'template-cases.json',cases);return dict(negative=len(cases),positive=1,allConstructorsForNegatives=0,externalFixtureIsSynthetic=True)
def semantic():
 from contract_cases import make
 from independent_cases_original import cases as independent
 from contract03_cases import cases as extra
 rows=make()+independent(B)+extra();save(W/'semantics-input.json',rows)
 code,b,e=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/review_semantics.ps1'),'-InputFile',str(W/'semantics-input.json'),'-OutputFile',str(W/'semantics-results.json')]);d=json.loads((W/'semantics-results.json').read_text(encoding='utf-8-sig'));bad=[x for x in d if not x['pass']];assert code==0 and not e and not bad,(code,bad[:3],e[:1000]);assert len(independent(B))==175 and sum(x['expected']=='PASS' for x in independent(B))==17
 return dict(total=len(d),original45=True,independentPositive17=True,positive=sum(x['qualified'] for x in d),bad=0)
def prestart():
 c,b,e=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')]);d=json.loads((W/'prestart.json').read_text(encoding='utf-8-sig'));assert c==0 and not e and d['allPassed'];return d
def preauth_owned():
 p,t,pins=inputs('new-original');raw=encode(t);ticket=PreparedFacts(raw,sha(raw),p);assert ticket.gate is None;g=ticket.prepare();bound=ticket.bind(g);d=decode(bound);neg=[]
 for k in d:
  v=copy.deepcopy(d);v.pop(k);neg.append(dict(case='binding-delete:'+k,reason=reject(lambda v=v:binding_bytes(encode(v),bound),'PREAUTH_BINDING_ONCE_BYTES')))
  v=copy.deepcopy(d);v[k]=None;neg.append(dict(case='binding-change:'+k,reason=reject(lambda v=v:binding_bytes(encode(v),bound),'PREAUTH_BINDING_ONCE_BYTES')))
 neg.append(dict(case='binding-repeat',reason=reject(lambda:ticket.bind(g),'PREAUTH_BIND_ONCE')))
 c=OwnedFactCapture();rec=None
 try:rec=ticket.receive(g,bound,c,[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'])
 finally:
  if getattr(c,'bodyReturned',False) and not c.unknown:release=c.finish_after_original_collect_return(g)
  elif not c.entered and not g.released:release=g.release()
 assert rec['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V2' and rec['authorizationKind']=='GLOBAL_IDLE_FACT_PREAUTH_V1' and 'authoritySha256' not in rec and 'approvalSha256' not in rec and rec['externalPreauthSha256']==sha(raw) and rec['runtimeBindingSha256']==sha(bound)
 assert release['originalUnlockCloseReturned'] and release['factProofTimely'] and release['factCaptureQualified'] and release['sdkChildrenEntered']==1
 neg.append(dict(case='consumed-gate',reason=reject(lambda:ticket.receive(g,bound,OwnedFactCapture()),'PREAUTH_ORIGINAL_PREPARED_GATE')))
 neg.append(dict(case='release-once',reason=reject(g.release,'RELEASE_ONCE')))
 save(W/'new-original-result.json',dict(receipt=rec,release=release,binding=d,negative=neg,sourceBytes=g.source_bytes,sourceReads=g.source_reads,controlBytes=sum(x['bytes'] for x in g.events)+g.carry,exactSourceEvents=g.events))
 return dict(receipt=rec,release=release,binding=d,negative=len(neg),sourceBytes=g.source_bytes,sourceReads=g.source_reads,fixtureExternalApproval=True)
def legacy():
 p,t,pins=inputs('legacy-original');root=Path(p['evidenceRoot']);root.mkdir(parents=True);g=GateSession(root.parent,policy=p);g.prepare();now=datetime.now(timezone.utc)
 a=dict(schema='GLOBAL_IDLE_FACT_AUTHORITY_V1',approvedForExecution=True,scope=g.scope,planId=p['planId'],mode='OFFLINE_FIXTURE',notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=80)).isoformat(),collectorSha256=pins['collectorSha256'],planSha256=pins['factPlanSha256'],routeProofSha256=decode(g.receipt_bytes)['routeSha256'],sourceThreadId=t['sourceThreadId'],sourceTurnId=str(uuid.uuid4()));h=sha(encode(a));instruction='EXECUTE_READONLY_FACTS '+h
 ap=dict(schema='GLOBAL_IDLE_FACT_APPROVAL_V1',mode='OFFLINE_FIXTURE',sourceThreadId=t['sourceThreadId'],sourceTurnId=str(uuid.uuid4()),approvedAuthoritySha256=h,instructionText=instruction,instructionSha256=sha(instruction.encode()));ah=sha(encode(ap));neg=[]
 neg.append(reject(lambda:OwnedFactCapture().collect(a,g,'0'*64,approval=ap,approved_approval_sha256=ah),'FACT_PRIOR_APPROVAL_HASH'))
 neg.append(reject(lambda:OwnedFactCapture().collect(a,g,h,approval=ap,approved_approval_sha256='0'*64),'FACT_EXTERNAL_APPROVAL_CHAIN'))
 c=OwnedFactCapture();rec=None
 try:rec=c.collect(a,g,h,[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'],approval=ap,approved_approval_sha256=ah)
 finally:
  if getattr(c,'bodyReturned',False) and not c.unknown:release=c.finish_after_original_collect_return(g)
  elif not c.entered and not g.released:release=g.release()
 assert rec['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V1' and rec['authoritySha256']==h and rec['approvalSha256']==ah and 'externalPreauthSha256' not in rec and release['factCaptureQualified'];neg.append(reject(lambda:c.collect(a,g,h),'FACT_ONCE'))
 save(W/'legacy-result.json',dict(receipt=rec,release=release,negative=neg,sourceBytes=g.source_bytes,sourceReads=g.source_reads));return dict(receipt=rec,release=release,negative=neg,sourceBytes=g.source_bytes)
def cli():
 p,t,pins=inputs('explicit-cli');folder=W/'explicit-inputs';folder.mkdir();save(folder/'template.json',t);save(folder/'policy.json',p)
 c,b,e=child([PY,'-I','-X','utf8','-B',str(B/'tools/facts_entry.py'),'--template',str(folder/'template.json'),'--approved-template-sha256',sha(encode(t)),'--policy',str(folder/'policy.json')]);assert c==0 and not e,(c,b,e);d=decode(b);assert d['receipt']['schema']=='GLOBAL_IDLE_FACT_CAPTURE_V2' and d['release']['factCaptureQualified'] and d['outerProcessReturnStillRequired'] and d['qualificationIssued'] is False;save(W/'explicit-cli-observed-return.json',dict(originalWaitReadersStreamsHandleReturned=True,result=d));return d
def group(name,fn):
 global stopped
 if stopped or registry.stop or control.stop or time.monotonic()-START>=320:results.append(dict(name=name,status='NOT_RUN'));return
 before=time.monotonic()
 try:detail=fn();results.append(dict(name=name,status='PASS',seconds=time.monotonic()-before,detail=detail))
 except BaseException as e:results.append(dict(name=name,status='FAIL',seconds=time.monotonic()-before,error=repr(e)));stopped=True
 if GATES or FACTS or AUX:stopped=True
 save(B/'evidence'/('group-'+str(len(results))+'.json'),results[-1])
for rel,h in P['scriptPins'].items():assert sha((B/rel).read_bytes())==h,rel
assert not any(k in os.environ for k in ENV)
sys.addaudithook(registry.observe);subprocess.Popen=registry.construct
try:
 for name,fn in [('driver-qualification',qualify),('strict-template-models',pure_templates),('original-346-semantic-regression',semantic),('original-preStart13',prestart),('original-new-preauth-capture-release',preauth_owned),('legacy-V1-exact-path',legacy),('explicit-V2-facts-entry-original-return',cli)]:group(name,fn)
finally:
 subprocess.Popen=ORIGINAL
 post=[r for r,h in P['scriptPins'].items() if sha((B/r).read_bytes())!=h]
 result=dict(schema='PREAUTH01_BATCH_RESULT_V1',results=results,seconds=time.monotonic()-START,allPassed=bool(results) and all(x['status']=='PASS' for x in results),calls=registry.calls,audit=registry.events,auxOriginalsReturned=all(c.returned for c in captures),auxCustody=len(AUX),gateCustody=len(GATES),factCustody=len(FACTS),stopNew=stopped or control.stop or registry.stop,sourcePinsChanged=post,ioReservation=PLAN['ioReservation'],actualSDK=0,actualNativeRoute=0,actualTCP=0,actualDevice=0,actualGit=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN_NO_ADAPTER',D1='NOT_PASSED',M0='NOT_STARTED')
 save(B/'evidence/result.json',result);print(json.dumps(dict(groups=len(results),allPassed=result['allPassed'],seconds=result['seconds'],gateCustody=len(GATES),factCustody=len(FACTS),auxReturned=result['auxOriginalsReturned'])))
if not result['allPassed']:raise SystemExit(2)
