"""Pure reservation arithmetic; synthetic objects, no Capture/Gate/claim/once."""
from pathlib import Path
from types import SimpleNamespace as N
import sys,copy,os,threading,json,uuid
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'tools'))
from source_budget import SourceBudget
from production_runner import ProductionRunner
from entry_gates import GateSession
rows=[]
def model(gb=0,gr=0,rb=0,rr=0):
 g=GateSession.__new__(GateSession);r=ProductionRunner.__new__(ProductionRunner);o=N(gate=g,runner=r,slots=[dict(id='identity'),dict(id='global_idle')],next=0,policy={'globalIdleQualification':{'evidenceRef':{'bytes':1}}})
 g.pid=os.getpid();g.thread=threading.get_ident();g.scope='a'*64;g.generation=str(uuid.uuid4());g.sdk_owner=o;g.source_bytes=gb;g.source_reads=gr;g.source_reserved_unknown=0;g.assert_held=lambda:None;r.owner=o;r.source_bytes=rb;r.source_reads=rr
 return SourceBudget(o)
def reject(label,fn,expected):
 try:fn();reason='ACCEPTED'
 except ValueError as e:reason=str(e)
 assert reason==expected,(label,reason);rows.append(dict(id=label,reason=reason,phase='PURE_SYNTHETIC_BUDGET_NOT_ORIGINAL_OBJECT_PROOF'))
for k,args in [('Gate-bytes',(268435456,0,0,0)),('Gate-reads',(0,64,0,0)),('Runner-bytes',(0,0,536870912,0)),('Runner-reads',(0,0,0,256))]:
 b=model(*args);reject(k,lambda:b.reserve('identity'),'SOURCE_OWNER_BUDGET_BEFORE_LAUNCH');assert b.gate.source_bytes==args[0] and b.runner.source_bytes==args[2]
b=model();reject('wrong-role',lambda:b.reserve('global_idle'),'SOURCE_ROLE_ORDER');t=b.reserve('identity');reject('pending-next',lambda:b.reserve('identity'),'SOURCE_ORIGINAL_AUTHORITY_PENDING')
def delta(ticket):return dict(schema='QUALIFICATION_SOURCE_DELTA_V1',**{k:ticket[k] for k in ('ticketId','scope','generation','ownerPid','requestId','version')},reservedUsedBytes=1,sourceReads=1,actualBytes=0,events=[dict(pathSha256='a'*64,reservedBytes=1,actualBytes=0,closeReturned=True,opened=True,unknown=False)],finished=True)
d=delta(t)
for k in ('scope','ticketId','generation','version'):
 wrong=copy.deepcopy(d);wrong[k]=d[k]+1 if k=='version' else 'WRONG';reject('stale-or-scope:'+k,lambda:b.merge(wrong),'SOURCE_DELTA_STALE_OR_SCOPE')
u=copy.deepcopy(d);u['events'][0]['unknown']=True;reject('unknown-reservation-retained',lambda:b.merge(u),'SOURCE_DELTA_RETURN_UNKNOWN');assert b.pending==t
u=copy.deepcopy(d);u['events'][0]['closeReturned']=False;reject('close-unknown-retained',lambda:b.merge(u),'SOURCE_DELTA_RETURN_UNKNOWN')
b.merge(d);assert b.pending is None and b.gate.source_bytes==262145 and b.gate.source_reads==2 and b.runner.source_bytes==262145
reject('duplicate-delta',lambda:b.merge(d),'SOURCE_DELTA_AUTHORITY_REQUIRED')
reject('same-owner-reinitialize',lambda:SourceBudget(b.owner),'SOURCE_AUTHORITY_ALREADY_BOUND')
b.owner.next=1;t2=b.reserve('global_idle');assert t2['version']==1 and t2['baseGateBytes']==262145 and t2['baseGateReads']==2
reject('old-delta-next-call',lambda:b.merge(d),'SOURCE_DELTA_STALE_OR_SCOPE')
b=model();t=b.reserve('identity');d=delta(t)
for value in (None,[],1,'bad',{}):
 bad=copy.deepcopy(d);bad['events']=[value];reject('event-shape:'+repr(value),lambda:b.merge(bad),'SOURCE_DELTA_EVENT_SCHEMA');assert b.pending==t
for key,value in [('pathSha256',None),('pathSha256','z'*64),('opened',1),('opened',None),('closeReturned',1),('unknown','false'),('reservedBytes',True)]:
 bad=copy.deepcopy(d);bad['events'][0][key]=value;reject('event-type:'+key+':'+repr(value),lambda:b.merge(bad),'SOURCE_DELTA_EVENT_TYPE');assert b.pending==t
old=b.gate.thread;b.gate.thread=old+1
try:reject('merge-original-thread',lambda:b.merge(d),'SOURCE_DELTA_ORIGINAL_AUTHORITY')
finally:b.gate.thread=old
old=b.runner.owner;b.runner.owner=None
try:reject('merge-original-Runner-owner',lambda:b.merge(d),'SOURCE_DELTA_ORIGINAL_AUTHORITY')
finally:b.runner.owner=old
old=b.runner.source_bytes;b.runner.source_bytes=0
try:reject('merge-Runner-charge-reset',lambda:b.merge(d),'SOURCE_DELTA_RUNNER_RESET')
finally:b.runner.source_bytes=old
b.runner.source_bytes+=100;b.runner.source_reads+=3;b.merge(d);assert b.pending is None and b.runner.source_bytes==t['reservedBytes']+100
b=model();t=b.reserve('identity');d=delta(t);d['events'][0]['opened']=False;d['events'][0]['closeReturned']=False;b.merge(d);assert b.pending is None
rows.append(dict(id='not-opened-no-close-claim-and-no-refund',reason='ACCEPTED_CORRECT_VACUOUS_RETURN',phase='PURE_SYNTHETIC_MODEL'))
for name,gb,gr,rb,rr in [('Runner-read-before-open',0,0,0,256),('Runner-byte-before-open',0,0,536870912,0),('Runner-post-reserve-three-reads',0,0,0,254)]:
 b=model(gb,gr,rb,rr)
 if rr==254:b.reserve('identity')
 b.runner.operation=lambda *a,**k:(_ for _ in ()).throw(AssertionError('MODEL_MUST_REJECT_BEFORE_ORIGINAL_IO'))
 reject(name,lambda:b.runner.read_file(H/'tools/runtime_binding.py','PURE_BOUNDARY',None),'RUNNER_SOURCE_BUDGET')
out=dict(allPassed=True,actualPopen=0,actualCapture=0,actualGateConstruction=0,actualClaim=0,actualOnce=0,syntheticUnknownOnly=True,results=rows,shortReadModel='returned zero bytes retains full pre-reservation; original close returned model only',actualParentReservationNoRefund=True)
(H/'evidence').mkdir(exist_ok=True);(H/'evidence/pure-budget-arithmetic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(purePassed=True,cases=len(rows),originalResources=0)))
