from pathlib import Path
import sys,time,json,threading
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from self_io import read,load,save,sha,known,READS
from controller import order
from profile import plan,checks,PS
from capture_policy import audit_decision
from self_observer import Observer,CUSTODY
from native_identity import own_identity
def main(h):
 o=order(h);B=Path(o['candidate']);ident=own_identity();ident['nonce']=o['nonce'];save(R/'worker-self.json',ident);start=time.monotonic()
 while not (R/'worker-admit.json').exists():
  if (R/'stop.json').exists() or time.monotonic()-start>8:save(R/'worker-not-admitted.json',dict(knownNoChild=True));return 2
  time.sleep(.025)
 assert load(R/'worker-admit.json')==dict(orderSha256=h,selfSha256=sha(read(R/'worker-self.json')));start=time.monotonic();events=[];armed=None
 def stop(why):
  if not (R/'stop.json').exists():save(R/'stop.json',dict(reason=why,action='STOP_NEW_ADMISSION'))
 def hook(event,args):
  if event!='subprocess.Popen':return
  try:d=audit_decision(event,args,armed,armed,active=True,same_owner=True,event_unused=not events)
  except BaseException:d=dict(allowed=False,rawPayloadComplete=False,reason='OBSERVATION_INTERNAL_ERROR_RETAINED_AS_FACT')
  events.append(d) # no IO, rejection or exception after temporary creation
 sys.addaudithook(hook)
 from pure_checks import run
 pure=run(B,R,read,save)
 a=[PS,'-NoProfile','-NonInteractive','-File',str(R/'host.ps1'),'-InputFile',str(R/'input-index.json'),'-OutputFile',str(R/'semantic-results.json')];p=plan(a,R);save(R/'PS-constructor-plan.json',dict(plan=p,pureChecks=checks(p)))
 assert time.monotonic()-start<240 and not (R/'stop.json').exists();armed=p
 c=Observer(a,p['executable'],p['cwd'],p['env'],R/'PS-original',stop,window=90)
 for i,d in enumerate(events):save(R/('worker-audit-'+str(i)+'.json'),d)
 if any(not d['allowed'] for d in events):stop('OBSERVED_PROFILE_MISMATCH_AUDIT_NEVER_RAISED')
 receipt=c.collect();assert c.returned and not receipt['errors'] and not receipt['expired'] and not CUSTODY and known()
 rows=load(R/'semantic-results.json');assert len(rows)==366
 result=dict(schema='CONTRACT03_SEMANTICS_A_RESULT_V1',batch=o['batch'],semanticCases=len(rows),semanticPassed=sum(x['pass'] for x in rows),unsafePass=[x['logicalIndex'] for x in rows if x['qualified'] and x['expected']!='PASS'],groups=[dict(origin=n,count=sum(x['origin']==n for x in rows),passed=sum(x['origin']==n and x['pass'] for x in rows),positive=sum(x['origin']==n and x['expected']=='PASS' for x in rows),positivePassed=sum(x['origin']==n and x['expected']=='PASS' and x['pass'] for x in rows)) for n in ('independent175','developer98-replay','developer73-map','independent-adjacent20')],pureStaticCases=len(pure),pureStaticPassed=sum(x['passed'] for x in pure),totalLogicalCases=400,PSHosts=1,PSExitCode=receipt['exitCode'],allPSOriginalsReturned=True,sourceReadBytes=sum(x['bytes'] for x in READS),sourceReads=len(READS),auditObserved=len(events),auditMismatch=sum(not x['allowed'] for x in events),auditRaised=False,newUnknown=False,seconds=time.monotonic()-start,allPassed=all(x['pass'] for x in rows) and all(x['passed'] for x in pure) and not (R/'stop.json').exists(),wholePackageB='NOT_RUN',realSDK=0,realNativeRoute=0,oldRuntimeQueries=0)
 save(R/'worker-final.json',result);print(json.dumps(dict(semanticPassed=result['semanticPassed'],semanticCases=366,pureStaticPassed=result['pureStaticPassed'],PSOriginalReturned=True,seconds=result['seconds'])));return 0 if result['allPassed'] else 2
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
