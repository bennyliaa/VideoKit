from pathlib import Path
from datetime import datetime,timezone,timedelta
import time,threading
def run(ns,R,save,stopped,custody):
 specs=__import__('json').loads((R/'scenarios.json').read_bytes());out=[]
 for spec in specs:
  name=spec['name'];started=time.monotonic()
  if stopped():out.append(dict(scenario=name,status='NOT_RUN_BUDGET',target=spec));continue
  f,p=ns['permit']('f-'+str(len(out)),name)
  if name=='EXPIRE_DURING_MATERIALIZE':p['expiresUtc']=(datetime.now(timezone.utc)+timedelta(seconds=9)).isoformat()
  args=ns['inputs'](f,p);save(f/'target-before-constructor.json',spec);r=None;reason=None;witness=[];watch=None
  try:
   r=ns['construct'](args)
   def witness_failure():
    end=time.monotonic()+45
    while time.monotonic()<end:
     if r.failure:
      witness.append(dict(reason=r.failure,pending=sum(t.is_alive() for t in r.pending),leaseHeld=r.gate is not None and r.gate.lease is not None and not r.gate.lease.closed));return
     if r.finished:return
     time.sleep(.01)
   watch=threading.Thread(target=witness_failure);watch.start()
   try:r.run();reason='UNEXPECTED_SUCCESS'
   except (ValueError,TypeError,KeyError) as e:reason=str(e)
  except (ValueError,TypeError,KeyError) as e:reason=str(e)
  finally:
   if watch is not None:watch.join()
  entered=[] if r is None else list(r.root.glob('*-entered.json'))
  ops=[] if r is None else [x for x in r.held if type(x) is dict and x.get('returned')]
  done={x.get('name') for x in ops};g=None if r is None else r.gate
  phase=False;extra={}
  if r is not None:
   if name=='MATERIALIZE_KNOWN_REJECT':phase=g is not None and g.prepared and 'materializer-proof-read' in done
   elif name in ('NO_SDK_ABORT','TAIL_LATE','WRONG_HOLDER','WRONG_OUTPUT_SOURCE'):phase=hasattr(r,'receipt_writer') and r.receipt_writer['returned']
   elif name=='MATERIALIZE_LATE':phase='activation-write' in done
   elif name=='RECEIVER_LATE':phase='materialization-delayed-receiver' in done
   elif name=='EXPIRE_DURING_MATERIALIZE':phase='materializer-proof-read' in done
   elif name=='BUSY':
    phase=len(entered)==2 and (r.root/'global_idle-stdout.bin').exists() and b'ActiveInstrumentation{' in (r.root/'global_idle-stdout.bin').read_bytes()
   elif name=='PRESTART_KNOWN_REJECT':
    fp=r.root/'identity-console.bin'
    if fp.exists():
     co=ns['decode'](fp.read_bytes());extra=dict(noStartResourcesReturned=co.get('noStartResourcesReturned'),startEntered=co.get('startEntered'),disposeCalls=co.get('processDisposeCalls'),initializationFailure=co.get('initializationFailure'),readers=co.get('readers'))
     phase=co.get('noStartResourcesReturned') is True and co.get('startEntered') is False and co.get('processDisposeCalls')==1 and co.get('initializationFailure')=='CONTROLLED_PRESTART_AFTER_TWO_FILES' and all(x['fileCloseCalls']==1 and x['fileCloseReturned'] and x['pipeNeverCreated'] and not x['pipeCloseReturned'] and not x['eof'] for x in co['readers'])
   elif name=='OWNER_END_TAIL':
    phase=r.owner is not None and len(r.owner.records)==7 and r.owner.records[-1]['proof']['nextId']=='END' and r.owner.records[-1]['proofWriter']['closeReturned'] and r.owner.records[-1]['tailGate'] is not None
    if r.owner is not None and r.owner.records:extra=dict(lastRecord=r.owner.records[-1])
  returned=r is None or not any(t.is_alive() for t in r.pending)
  released=g is not None and g.released and getattr(r,'abort_release',{}).get('originalUnlockCloseReturned') is True
  target=reason==spec['expectedReason'] and phase and len(entered)==spec['controllers'] and returned and released
  if name in ('MATERIALIZE_LATE','RECEIVER_LATE'):target=target and bool(witness) and witness[0]['pending']>0 and witness[0]['leaseHeld']
  row=dict(scenario=name,status='PASS_EXACT_TARGET' if target else 'FAIL_TARGET_NOT_COVERED',actualReason=reason,expected=spec,targetStageReached=bool(phase),controllers=len(entered),originalRunnerThreadsReturned=returned,originalClaimReleased=released,release=getattr(r,'abort_release',None),witness=witness,extra=extra,seconds=time.monotonic()-started,normalInitialProofUnchanged=None if r is None or not hasattr(r,'initial_hash') else ns['sha']((r.root/'pre_sdk_local_gate-completion-proof.json').read_bytes())==r.initial_hash)
  save(f/'target-adjudication.json',row);save(R/('fault-'+name+'.json'),row);out.append(row);custody()
 return out
