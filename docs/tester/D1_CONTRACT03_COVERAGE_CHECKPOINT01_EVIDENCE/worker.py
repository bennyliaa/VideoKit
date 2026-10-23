from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,time,threading,json,uuid,copy,subprocess,io
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from self_io import read,load,save,sha,known
from controller import order
from native_identity import own_identity
from profile import PY,checks,plan as own_plan
from capture_policy import snapshot,same
def main(h):
 o=order(h);B=Path(o['candidate']);W=Path(o['work']);ident=own_identity();ident['nonce']=o['nonce'];save(R/'worker-self.json',ident);begin=time.monotonic()
 while not (R/'worker-admit.json').exists():
  if (R/'stop.json').exists() or time.monotonic()-begin>8:return 2
  time.sleep(.025)
 assert load(R/'worker-admit.json')==dict(orderSha256=h,selfSha256=sha(read(R/'worker-self.json')))
 W.mkdir(parents=True);sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
 import production_runner as pr,entry_gates as eg,win32_route as wr
 ns=dict(Path=Path,datetime=datetime,timezone=timezone,timedelta=timedelta,time=time,uuid=uuid,copy=copy,json=json,sha=eg.sha,encode=eg.encode,ProductionRunner=pr.ProductionRunner,START=begin,B=B,W=W,PY=PY,PS='UNUSED_NO_PS_ALLOWED',OPS=pr.OPS,LIMITS=pr.LIMITS,sources=load(B/'reference/runner-source-seal.json')['sources'],plan=load(B/'reference/exact-seven-role-plan.json'),cases=[],save=save)
 exec(compile(read(R/'input_definitions.py').decode(),'<frozen-permit-input-definitions-only>','exec'),ns)
 f,p=ns['permit']('one','EXPIRE_DURING_MATERIALIZE');root=Path(p['evidenceRoot']);argv=[PY,'-I','-X','utf8','-B',str(B/'selfchecks/route_fixture.py'),str(root/'gate-context.json')]
 expected=(None,subprocess.list2cmdline(argv),None,None);observed=[];active=False;constructorReturned=False;originalPopen=subprocess.Popen
 # Pure exact callback shape and wrong program tests, before constructor.
 checkRows=[]
 for name,a,want in [('exact',expected,True),('wrong-program',('D:/Android/SDK/platform-tools/adb.exe',*expected[1:]),False),('extra',(None,expected[1]+' X',None,None),False),('cwd',(None,expected[1],str(R),None),False)]:
  ok=same(a,expected);assert ok is want;checkRows.append(dict(name=name,accepted=ok,pureOnly=True))
 save(R/'checker-profile-before-constructor.json',dict(argv=argv,raw=expected,cases=checkRows,sourceSha256=sha(read(B/'selfchecks/route_fixture.py'))))
 def audit(event,args):
  if event!='subprocess.Popen':return
  observed.append(dict(raw=snapshot(args),matched=active and same(args,expected)))
 def prechecked(a,*pos,**kw):
  nonlocal active,constructorReturned
  if pos or a!=argv or set(kw)!=set(('stdin','stdout','stderr')) or kw['stdin']!=subprocess.DEVNULL or kw['stdout']!=subprocess.PIPE or kw['stderr']!=subprocess.PIPE or observed:raise ValueError('PRECONSTRUCTOR_EXACT_ONE_CHECKER')
  active=True
  try:q=originalPopen(a,**kw);constructorReturned=True;return q
  finally:active=False
 sys.addaudithook(audit);subprocess.Popen=prechecked
 # All templates/profiles fixed; actual wall-clock permit and hashes materialize
 # immediately before the original constructor. No clock or guard mutation.
 anchor=datetime.now(timezone.utc);anchorTick=eg.tick();p['notBeforeUtc']=(anchor-timedelta(seconds=1)).isoformat();p['expiresUtc']=(anchor+timedelta(seconds=o['ttlSeconds'])).isoformat()
 args=ns['inputs'](f,p);save(R/'actual-input-binding.json',dict(anchorUtc=anchor.isoformat(),anchorTick=anchorTick,expiresUtc=p['expiresUtc'],ttlSeconds=o['ttlSeconds'],permitSHA256=args[2],approvalSHA256=args[4],scope=p['scope'],scenario=p['fixtureScenario']))
 # Preserve the original instance even if its unchanged __init__ rejects.
 r=pr.ProductionRunner.__new__(pr.ProductionRunner);snapshots={};done=threading.Event();reason=None;initReturned=False
 def watch():
  while not done.wait(.001):
   now=datetime.now(timezone.utc);tick=eg.tick();g=getattr(r,'gate',None)
   if g is not None and g.prepared and 'gatePrepared' not in snapshots:snapshots['gatePrepared']=dict(utc=now.isoformat(),tick=tick,permitValid=now<datetime.fromisoformat(p['expiresUtc']),leaseHeld=g.lease is not None and not g.lease.closed)
   for record in getattr(r,'held',[]):
    if type(record) is dict and record.get('name')=='materializer-proof-read' and record.get('returned') and 'endTick' in record and 'materializerProofRead' not in snapshots:
     snapshots['materializerProofRead']=dict(utc=now.isoformat(),tick=tick,originalStartTick=record['startTick'],originalEndTick=record['endTick'],originalReadReturned=True,bytes=len(record['value']),sha256=sha(record['value']),permitValid=now<datetime.fromisoformat(p['expiresUtc']),failureAtObservation=getattr(r,'failure',None))
  return
 observer=threading.Thread(target=watch);observer.start()
 try:
  r.__init__(*args);initReturned=True;snapshots['constructorReturn']=dict(utc=datetime.now(timezone.utc).isoformat(),tick=eg.tick(),permitValid=datetime.now(timezone.utc)<r.expires)
  try:r.run();reason='UNEXPECTED_SUCCESS'
  except (ValueError,TypeError,KeyError) as e:reason=str(e)
 except (ValueError,TypeError,KeyError) as e:reason=str(e)
 finally:done.set();observer.join()
 finishUTC=datetime.now(timezone.utc);finishTick=eg.tick();g=getattr(r,'gate',None)
 files=[x for x in getattr(r,'held',[]) if isinstance(x,io.IOBase)]
 pending=any(t.is_alive() for t in getattr(r,'pending',[])) or g is not None and any(t.is_alive() for t in g.pending)
 resources=not pending and all(x.closed for x in files) and (g is None or g.released and g.lease.closed) and not pr.RUNNER_CUSTODY and not eg.CUSTODY and not wr.CUSTODY and known()
 readSnap=snapshots.get('materializerProofRead');target=initReturned and snapshots.get('constructorReturn',{}).get('permitValid') is True and snapshots.get('gatePrepared',{}).get('permitValid') is True and readSnap is not None and readSnap['permitValid'] and readSnap['failureAtObservation'] is None and reason=='PERMIT_EXPIRED_OR_FUTURE' and finishUTC>=r.expires and g is not None and g.released and resources
 if g is not None and hasattr(r,'proof_start'):
  expiryTick=anchorTick+o['ttlSeconds']*1000;target=target and expiryTick<g.proof_start_tick+10000 and expiryTick<r.start_tick+30000
 else:expiryTick=None;target=False
 result=dict(schema='CONTRACT03_COVERAGE_CHECKPOINT01_RESULT_V1',batch=o['batch'],scope=p['scope'],work=str(W),exactTargetPassed=bool(target),reason=reason,initReturned=initReturned,snapshots=snapshots,anchorUtc=anchor.isoformat(),anchorTick=anchorTick,expiryUtc=p['expiresUtc'],estimatedExpiryTick=expiryTick,finalUtc=finishUTC.isoformat(),finalTick=finishTick,scopeStartTick=getattr(r,'start_tick',None),proofStartTick=getattr(g,'proof_start_tick',None),activationCreated=(root/'../release/activation.json').exists(),controllersEntered=len(list(root.glob('*-entered.json'))) if root.exists() else 0,release=getattr(r,'abort_release',None),allOriginalResourcesReturned=resources,pending=pending,newUnknown=not resources,gateSourceBytes=getattr(g,'source_bytes',None),gateSourceReads=getattr(g,'source_reads',None),runnerSourceBytes=getattr(r,'source_bytes',None),runnerSourceReads=getattr(r,'source_reads',None),audit=observed,constructorReturned=constructorReturned,actualSDK=0,actualNativeRoute=0,attempts=1,seconds=time.monotonic()-begin,gitAllowedAfterFreeze=resources)
 save(R/'worker-final.json',result);print(json.dumps(dict(exactTargetPassed=bool(target),reason=reason,allOriginalsReturned=resources,seconds=result['seconds'])))
 if not resources:
  while True:time.sleep(.1)
 return 0 if target else 2
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))

