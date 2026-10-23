from pathlib import Path
from datetime import datetime,timezone
import sys,time,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from self_io import read,load,save,sha,known,READS
from profile import PY,plan,checks
from capture_policy import audit_decision
def order(h):
 assert sha(read(R/'order.json'))==h;o=load(R/'order.json')
 for x in o['sources']:
  b=read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 return o
def main(h):
 o=order(h);now=datetime.now(timezone.utc);assert datetime.fromisoformat(o['notBeforeUtc'])<=now<datetime.fromisoformat(o['expiresUtc']);assert not (R/'once.json').exists()
 save(R/'once.json',dict(orderSha256=h,once=1,utc=now.isoformat()));start=time.monotonic()
 from self_observer import Observer
 from native_identity import own_identity
 save(R/'outer-self.json',own_identity())
 def stop(reason):
  if not (R/'stop.json').exists():save(R/'stop.json',dict(reason=reason,action='STOP_NEW_ADMISSION',noKillSecondClose=True))
 a=[PY,'-I','-X','utf8','-B',str(R/'worker.py'),h];p=plan(a,R);save(R/'outer-constructor-plan.json',dict(plan=p,pureChecks=checks(p)));events=[]
 def audit(event,args):
  if event!='subprocess.Popen':return
  try:d=audit_decision(event,args,p,p,active=True,same_owner=True,event_unused=not events)
  except BaseException:d=dict(allowed=False,rawPayloadComplete=False,reason='OBSERVATION_INTERNAL_ERROR_RETAINED_AS_FACT')
  events.append(d) # observation only: no IO or exception from audit
 sys.addaudithook(audit)
 c=Observer(a,p['executable'],p['cwd'],p['env'],R,stop,window=360);until=time.monotonic()+8
 for i,d in enumerate(events):save(R/('outer-audit-'+str(i)+'.json'),d)
 if any(not d['allowed'] for d in events):stop('OBSERVED_OUTER_PROFILE_MISMATCH_NO_EXCEPTION_IN_AUDIT')
 while not (R/'worker-self.json').exists() and not c.wait['returned'] and time.monotonic()<until:time.sleep(.025)
 if not (R/'stop.json').exists() and (R/'worker-self.json').exists() and c.identity:
  d=load(R/'worker-self.json');assert d['nonce']==o['nonce'] and all(d[k]==c.identity[k] for k in ('pid','creationFileTime','image','argv'));save(R/'worker-admit.json',dict(orderSha256=h,selfSha256=sha(read(R/'worker-self.json'))))
 else:stop('NO_ORIGINAL_WORKER_ADMISSION')
 receipt=c.collect()
 if not known():
  while True:time.sleep(.1)
 save(R/'outer-final.json',dict(receipt=receipt,seconds=time.monotonic()-start,allOwnEvidenceFilesClosed=True,sourceReadBytes=sum(x['bytes'] for x in READS),sourceReads=len(READS),auditObserved=len(events),auditMismatch=sum(not x['allowed'] for x in events),auditRaised=False,newUnknown=False));print(json.dumps(dict(workerExitCode=receipt['exitCode'],outerReturned=True)));return receipt['exitCode']
if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
