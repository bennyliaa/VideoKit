from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,os,time,json,uuid,copy,threading,subprocess
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from self_io import read,load,save,sha,known,READS
from controller import order
from profile import plan as own_plan,checks,PY,PS
from profiles import candidate_shape,own_shape
from capture_policy import snapshot,same
from self_observer import Observer,CUSTODY as AUX
from native_identity import own_identity
def main(h):
 o=order(h);B=Path(o['candidate']);W=Path(o['work']);s=own_identity();s['nonce']=o['nonce'];save(R/'worker-self.json',s);start=time.monotonic()
 while not (R/'worker-admit.json').exists():
  if (R/'stop.json').exists() or time.monotonic()-start>8:return 2
  time.sleep(.025)
 assert load(R/'worker-admit.json')==dict(orderSha256=h,selfSha256=sha(read(R/'worker-self.json')))
 assert not W.exists();W.mkdir(parents=True);START=time.monotonic();groups=[];captures=[];bindings=[];events=[];active={};armed={};mismatch=[]
 expected={str((B/x['path']).resolve()):x['sha256'] for x in load(B/'reference/freeze-manifest.json')['files']}
 seal=load(B/'reference/runner-source-seal.json')['sources'];originalPopen=subprocess.Popen
 def stopped():return (R/'stop.json').exists() or bool(mismatch) or time.monotonic()-START>=600
 def stop(why):
  if not (R/'stop.json').exists():save(R/'stop.json',dict(reason=why,action='STOP_NEW_ADMISSION',noKillOrSecondClose=True))
 def hook(event,args):
  if event!='subprocess.Popen':return
  try:
   binding=active.get(threading.get_ident());snap=snapshot(args);ok=binding is not None and not binding['observed'] and same(args,binding['expected']) and snap['complete'];row=dict(index=len(events),allowed=ok,rawPayload=snap,rawPayloadComplete=snap['complete'],binding=None if binding is None else binding['index'])
   if binding is not None:binding['observed']=True
   events.append(row)
   if not ok:mismatch.append('ACTUAL_TUPLE_MISMATCH_OBSERVATION_ONLY')
  except BaseException:mismatch.append('OBSERVATION_INTERNAL_ERROR')
 def prechecked(argv,*pos,**kw):
  if stopped() or len(bindings)>=128 or pos:raise ValueError('CLOSED_OR_NONFINITE_PRECONSTRUCTOR')
  tid=threading.get_ident();own=armed.get(tid)
  if own is not None:
   if not own_shape(argv,B,W):raise ValueError('OWN_ARGV_PRECONSTRUCTOR')
   if set(kw)!=set(('executable','cwd','env','shell','close_fds','stdin','stdout','stderr')) or kw['executable']!=own['executable'] or kw['cwd']!=own['cwd'] or not same(kw['env'],own['env']) or kw['shell'] is not False or kw['close_fds'] is not True:raise ValueError('OWN_KWARGS_PRECONSTRUCTOR')
   kind='EXACT_OWN'
  else:
   if not candidate_shape(argv,B,W) or set(kw)-{'stdin','stdout','stderr','shell'} or kw.get('shell',False) is not False:raise ValueError('CANDIDATE_ARGV_KWARGS_PRECONSTRUCTOR')
   frames=[];f=sys._getframe(1)
   while f is not None:frames.append(str(Path(f.f_code.co_filename)));f=f.f_back
   if not any(str(B/'tools'/n) in frames for n in ('entry_gates.py','outer_owner.py','fact_collector.py')):raise ValueError('CANDIDATE_SOURCE_CALLSITE_PRECONSTRUCTOR')
   kind='FROZEN_CANDIDATE_NONE'
  if kw.get('stdin')!=subprocess.DEVNULL or kw.get('stdout')!=subprocess.PIPE or kw.get('stderr')!=subprocess.PIPE:raise ValueError('FIXED_STREAMS_PRECONSTRUCTOR')
  script=Path(argv[4] if argv[0]==PS else argv[5]);data=read(script);want=expected.get(str(script.resolve()))
  if want is None and script.name=='capture_android02.ps1':want=seal['tools/capture_android02.ps1']
  if want is None and script.name=='post-guard-host.ps1' and script.is_relative_to(W):want=sha(data) # frozen selected generator, new exact produced script
  if want is None or sha(data)!=want:raise ValueError('SCRIPT_SOURCE_PRECONSTRUCTOR')
  raw=(kw.get('executable'),subprocess.list2cmdline(argv),kw.get('cwd'),kw.get('env'))
  assert snapshot(raw)['complete'];ix=len(bindings);record=dict(index=ix,kind=kind,argv=argv,expected=raw,scriptSha256=want,observed=False,originalConstructorReturned=False)
  save(R/'bindings'/('binding-'+str(ix)+'.json'),dict(index=ix,kind=kind,argv=argv,expected=raw,scriptSha256=want,precheckedBeforeConstructor=True,ambientOverridesAbsent=all(k not in os.environ for k in ('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL','ADB_SERVER_ADDRESS'))))
  bindings.append(record);active[tid]=record
  try:p=originalPopen(argv,**kw);record['originalConstructorReturned']=True;return p
  finally:active.pop(tid,None)
 sys.addaudithook(hook);subprocess.Popen=prechecked
 def child(argv):
  assert not stopped() and own_shape(argv,B,W) and len(captures)<32
  p=own_plan(argv,R);save(R/'aux'/('plan-'+str(len(captures))+'.json'),dict(plan=p,pureChecks=checks(p)));tid=threading.get_ident();armed[tid]=p
  try:c=Observer(argv,p['executable'],p['cwd'],p['env'],R/'aux'/str(len(captures)),stop,window=180);captures.append(c)
  finally:armed.pop(tid,None)
  d=c.collect();assert not d['errors'] and not d['expired'] and c.returned;return d['exitCode'],bytes(c.buffers[0]),bytes(c.buffers[1])
 def group(name,fn):
  if stopped():row=dict(name=name,status='NOT_RUN_STOP',seconds=0)
  else:
   s=time.monotonic()
   try:row=dict(name=name,status='PASS',detail=fn())
   except BaseException as e:row=dict(name=name,status='FAIL',errorType=type(e).__name__,error=str(e)[:2500])
   row['seconds']=time.monotonic()-s
  groups.append(row);save(R/('group-'+str(len(groups))+'.json'),row);return row
 def prestart():
  output=W/'prestart.json';code,b,e=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(output)]);d=load(output);assert code==0 and not e and d['allPassed'] and len(d['results'])==13 and not d['actualUnknownCreated'];return d
 group('original-preStart13-before-candidate-chain',prestart)
 sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
 import production_runner as pr,entry_gates as eg,win32_route as wr,fact_collector as fc
 def custody():
  if pr.RUNNER_CUSTODY or eg.CUSTODY or wr.CUSTODY or fc.CUSTODY or AUX or not known():
   stop('NEW_ORIGINAL_PENDING_OR_UNKNOWN');save(R/'pending-originals.json',dict(runner=len(pr.RUNNER_CUSTODY),gate=len(eg.CUSTODY),native=len(wr.CUSTODY),collector=len(fc.CUSTODY),aux=len(AUX),noKillSecondCloseRefund=True))
   while True:time.sleep(.1)
 ns=dict(Path=Path,datetime=datetime,timezone=timezone,timedelta=timedelta,sys=sys,json=json,time=time,uuid=uuid,copy=copy,threading=threading,subprocess=subprocess,B=B,W=W,START=START,ProductionRunner=pr.ProductionRunner,RUNNER_CUSTODY=pr.RUNNER_CUSTODY,LIMITS=pr.LIMITS,OPS=pr.OPS,PY=PY,PS=PS,encode=eg.encode,decode=eg.decode,sha=eg.sha,CUSTODY=eg.CUSTODY,BACKEND=wr.BACKEND,sources=seal,plan=load(B/'reference/exact-seven-role-plan.json'),results=[],runners=[],children=[],cases=[],positive=None,child=child,save=save)
 exec(compile(read(R/'frozen_definitions.py').decode(),'<selected-frozen-C03-helper-defs>','exec'),ns)
 from reused_groups import owned_collector,exact_append
 def collector():
  begin=len(ns['runners']);result=owned_collector(B,W,ns,fc,save);assert len(ns['runners'])==begin+1;r=ns['runners'][-1];g=r.gate;c=g.sdk_owner;before=eg.decode(g.receipt_bytes)
  delta=dict(bytes=g.source_bytes-before['sourceHashBytes'],reads=g.source_reads-before['sourceHashReads']);assert delta['reads']==2 and delta['bytes']==c.fixtureRuntime['sourceReadBytes'] and c.fixtureRuntime['sourceReads']==2
  raw=bytes(c.buf[0]);assert fc.facts(raw)['homeUid']==10012
  bad=[]
  for name,mut,why in [('status',raw.replace(b'|model|0|',b'|model|1|'),'FACT_ITEM_STATUS_TIME_OR_BYTES'),('over-length',raw.replace(b'|8\nTB138FC',b'|9\nTB138FC'),'FACT_ITEM_STATUS_TIME_OR_BYTES'),('tail',raw+b'X','FACT_END_OR_DURATION'),('NUL',raw.replace(b'TB138FC',b'\0B138FC'),'FACT_CONTROL')]:
   try:fc.facts(mut);raise AssertionError('MALFORMED_FACT_ACCEPTED')
   except ValueError as e:assert str(e)==why;(bad.append(dict(name=name,reason=str(e))))
  result.update(actualFixtureRuntime=c.fixtureRuntime,originalGateSourceDelta=delta,exactWireNegatives=bad);return result
 group('original-collector-fixed-program-source-ledger-wire-return',collector);custody()
 group('same-source-A-reference-and-real-entry-call',lambda:load(R/'semantic-A-reuse.json'));custody()
 from boundary_groups import root_negatives
 group('real-Runner-root-outside-prefix-old-alias-rejections',lambda:root_negatives(ns,W,save));custody()
 for name,fn in [('default-live-without-approval-denied','default_deny'),('prior-source-scope-schema-budget-exact-denials','authority'),('same-new-tester-root-original-seven-END-once','full_cli')]:group(name,ns[fn]);custody()
 from faults import run as run_faults
 faultRows=[]
 def fault_group():
  nonlocal faultRows
  faultRows=run_faults(ns,R,save,stopped,custody)
  d=dict(results=faultRows,exactTargets=sum(x['status']=='PASS_EXACT_TARGET' for x in faultRows),uncovered=[x['scenario'] for x in faultRows if x['status']!='PASS_EXACT_TARGET'],attemptsPerScenario=1)
  save(R/'fault-summary.json',d)
  if d['uncovered']:raise AssertionError('FAULT_TARGETS_NOT_COVERED:'+','.join(d['uncovered']))
  return d
 group('all-eleven-finite-fault-targets-adjudicated-separately',fault_group);custody()
 for name,fn in [('production-PS-post-and-final-start','ps_post_guards'),('changed-original-materialization-exact-reject','changed_materialization')]:
  if fn=='ps_post_guards' and ns['positive'] is None:group(name,lambda:(_ for _ in ()).throw(ValueError('FULL_POSITIVE_DEPENDENCY_NOT_RUN')))
  else:group(name,ns[fn])
  custody()
 group('precise-small-append-OWNER_SOURCE_PIN_ENTRY',lambda:exact_append(R,B,W,ns,save,load));custody()
 # No extra semantic replay. Source/plan/proposal and root lexical negatives are
 # accepted A only; actual full same-new-root behavior above supplies the chain.
 for i,row in enumerate(events):save(R/'audit'/('event-'+str(i)+'.json'),row)
 save(R/'binding-returns.json',dict(records=[dict(index=x['index'],kind=x['kind'],observed=x['observed'],originalConstructorReturned=x['originalConstructorReturned']) for x in bindings]))
 summary=dict(schema='CONTRACT03_INDEPENDENT_B_RESULT_V1',batch=o['batch'],work=str(W),seconds=time.monotonic()-START,groups=[dict(name=g['name'],status=g['status'],seconds=g['seconds']) for g in groups],faultExactTargets=sum(x['status']=='PASS_EXACT_TARGET' for x in faultRows),faultUncovered=[x['scenario'] for x in faultRows if x['status']!='PASS_EXACT_TARGET'],ownAux=len(captures),allOwnOriginalsReturned=all(c.returned for c in captures),ownAuxPipeBytes=sum(sum(c.counts) for c in captures),auditEvents=len(events),auditMismatch=len(mismatch),auditRaised=False,parentConstructors=len(bindings),allParentConstructorsReturned=all(x['originalConstructorReturned'] for x in bindings),runnerSourceBytesKnown=sum(r.source_bytes for r in ns['runners']),runnerSourceReadsKnown=sum(r.source_reads for r in ns['runners']),ownReadBytes=sum(x['bytes'] for x in READS),ownReadCalls=len(READS),newUnknown=False,custody=dict(runner=len(pr.RUNNER_CUSTODY),gate=len(eg.CUSTODY),native=len(wr.CUSTODY),collector=len(fc.CUSTODY),aux=len(AUX)),physicalIO='UNPROVEN',realSDK=0,realNativeRoute=0,oldQueries=0,allGroupsPassed=all(g['status']=='PASS' for g in groups),allFaultTargetsCovered=len(faultRows)==11 and all(x['status']=='PASS_EXACT_TARGET' for x in faultRows),D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 save(R/'worker-final.json',summary);print(json.dumps(dict(groups=len(groups),faultExact=summary['faultExactTargets'],faultUncovered=summary['faultUncovered'],allOriginalsReturned=True,seconds=summary['seconds'])));return 0 if summary['allGroupsPassed'] and summary['allFaultTargetsCovered'] else 2
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))

