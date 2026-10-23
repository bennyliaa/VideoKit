"""File-only empirical timing envelope and one frozen checkpoint scope."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,hashlib,ast,uuid,math
R=Path(__file__).resolve().parent;T=R.parent;B=T.parent/'coder/d1android02-global-idle-contract03-fix'
A=T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE';V=T/'D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE';P=T/'D1_DRIVER_CAPTURE_FIX01_PACKAGE'
OLD=T/'D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures/b03-fad80286'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def put(p,b):
 with p.open('xb') as f:f.write(b);f.flush()
def main():
 assert not (R/'order.json').exists()
 timings=[];proofs=[]
 for p in sorted(OLD.rglob('runner-materialization.json')):
  d=json.loads(p.read_bytes());proofs.append(dict(path=str(p),sha256=sha(p.read_bytes()),scopeStart=d['scopeStartTick'],proofStart=d['initialProofStartTick'],delta=(d['initialProofStartTick']-d['scopeStartTick'])/1000))
 for p in sorted(OLD.rglob('identity-outer-return.json')):
  d=json.loads(p.read_bytes());a=json.loads((p.parent/'identity-owner-admission.json').read_bytes());origin=a['runnerHandoff']['scopeStartTick']/1000;pr=a['runnerHandoff']['initialProofStartTick']/1000
  timings.append(dict(path=str(p),sha256=sha(p.read_bytes()),readUpper=d['outerStart']-origin,postProofUpper=d['outerStart']-pr,proofDelta=pr-origin))
 pmax=max(x['delta'] for x in proofs);pmin=min(x['delta'] for x in proofs);post=max(x['postProofUpper'] for x in timings)
 inputAllowance=.5;margin=.25;lower=pmax+post+inputAllowance+margin;upper=min(pmin+10,30)-margin
 feasible=lower<upper;ttl=math.floor((lower+upper)/2*1000)/1000 if feasible else None
 save(R/'timing-envelope.json',dict(proofSamples=proofs,completedAdmissionSamples=timings,maxProofStart=pmax,minProofStart=pmin,maxPostProofReadUpper=post,inputPreparationAllowance=inputAllowance,eachSideReserve=margin,lower=lower,upper=upper,ttlSeconds=ttl,feasible=feasible,old9s='Truncated before home; lower-bound evidence only, not an upper bound or a calibration attempt',meaning='Empirical conservative plan from frozen completed phases, not a guarantee about all future scheduler delays. Actual phase/time/return predicates must hold; no retry.',sourceOrder='operation end after original file close -> scenario wait expiry+20ms -> require: whole/gate/proof then permit'))
 if not feasible:print(json.dumps(dict(status='STATIC_BLOCKED_NO_MARGIN')));return
 # Direct own-profile code from accepted A; Observer lifecycle from accepted B.
 for name,src in [('self_io.py',V/'self_io.py'),('self_observer.py',V/'self_observer.py'),('native_identity.py',P/'native_identity.py'),('capture_policy.py',P/'capture_policy.py'),('profile.py',A/'profile.py')]:
  text=src.read_bytes()
  if name=='self_io.py':text=text.decode().replace('4294967296','268435456').replace('8192','2048').encode()
  put(R/name,text)
 ctl=(A/'controller.py').read_text().replace('window=300','window=180');put(R/'controller.py',ctl.encode())
 sys.path.insert(0,str(R));from profile import preflight
 save(R/'profile-preflight.json',preflight(R))
 full=json.loads((B/'reference/freeze-manifest.json').read_bytes());assert len(full['files'])==98
 for x in full['files']:
  b=(B/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 for x in json.loads((P/'source-manifest.json').read_bytes())['files']:assert sha((P/x['path']).read_bytes())==x['sha256']
 for x in json.loads((P/'runtime-pins.json').read_bytes())['files']:
  b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 # Only fixture input generation and exact original construction definitions.
 src=(B/'selfchecks/run_affected.py').read_text();names={'permit','inputs'};defs=[ast.get_source_segment(src,n) for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in names]
 put(R/'input_definitions.py',('\n\n'.join(defs)+'\n').encode())
 W=(T/'D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures'/('cc01-'+uuid.uuid4().hex[:8])).resolve();assert not W.exists()
 save(R/'budget.json',dict(wholeSeconds=180,stopNewSeconds=150,processes=4,readBytes=268435456,reads=2048,artifactBytes=16777216,files=512,stdoutBytes=1048576,stderrBytes=1048576,concurrency=1,retry=0,scopeAttempts=1,observerSeconds=150,originalProductLimits='UNCHANGED',ttlSeconds=ttl,estimatedSeconds=20))
 sources=[]
 for p in sorted(R.glob('*.py')):
  b=p.read_bytes();ast.parse(b.decode('utf-8-sig'));sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 for p in [R/'budget.json',R/'timing-envelope.json',R/'profile-preflight.json']:
  b=p.read_bytes();sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 now=datetime.now(timezone.utc);o=dict(schema='CONTRACT03_COVERAGE_CHECKPOINT01_ORDER_V1',batch=str(uuid.uuid4()),nonce=str(uuid.uuid4()),candidate=str(B),work=str(W),sources=sources,ttlSeconds=ttl,allowedStarts=1,notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=900)).isoformat(),sourceSeal='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774')
 save(R/'order.json',o);print(json.dumps(dict(orderSha256=sha((R/'order.json').read_bytes()),ttl=ttl,lower=lower,upper=upper,scope=str(W))))
if __name__=='__main__':main()

