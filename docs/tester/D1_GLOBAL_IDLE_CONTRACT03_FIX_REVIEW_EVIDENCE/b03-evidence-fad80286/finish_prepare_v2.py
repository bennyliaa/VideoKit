"""Continue the file-only preflight after -I omitted the script import path.
No preceding copy, test, scope or candidate execution is repeated."""
from pathlib import Path
import sys,json,ast,uuid
from datetime import datetime,timezone,timedelta
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from prepare import sha,save,B,T
assert not (R/'order.json').exists()
save(R/'preparation-v1-failure.json',dict(status='TESTER_FILE_ONLY_PREPARATION_FAIL',toolChunk='1ee01d',exitCode=1,reason="ModuleNotFoundError: No module named 'profiles'; -I omitted script directory",reached='After source/material/A checks, helper copies, budget and A reference; before pure preflight and order',originalSourceSha256=sha((R/'prepare.py').read_bytes()),candidateCalls=0,Popen=0,allFileOperationsContextManaged=True,noDynamicRetry=True))
W=(R.parent/'fixtures'/('b03-'+R.name.rsplit('-',1)[1])).resolve();assert not W.exists()
from profiles import pure_review
checks=pure_review(R,B,W);save(R/'profile-preflight.json',dict(checks=checks,actualConstructors=0,auditRejectInjected=False))
save(R/'source-isolation.json',dict(candidate=str(B),work=str(W),evidence=str(R),oldDev03AndC45And001a='NO_RUNTIME_QUERIES_OR_REUSE',productFrozen98Bad=0,devMaterial484Bad=0,semanticA408Bad=0,driverDelta='Original Observer retained; outer window720; argv32 profile retained; exact finite preconstructor grammar; audit memory-only; helper admission260->600. File-only preparation import fix is separate, no candidate source changes.',originalRuntime='14 files pinned in original preparation'))
sources=[]
for p in sorted(R.glob('*.py')):
 b=p.read_bytes();ast.parse(b.decode('utf-8-sig'));sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
for p in [R/'budget.json',R/'profile-preflight.json',R/'scenarios.json']:
 b=p.read_bytes();sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
now=datetime.now(timezone.utc);o=dict(schema='CONTRACT03_INDEPENDENT_B_ORDER_V1',batch=str(uuid.uuid4()),nonce=str(uuid.uuid4()),candidate=str(B),work=str(W),sources=sources,sourceSeal='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=1200)).isoformat(),allowedStarts=1)
save(R/'order.json',o);print(json.dumps(dict(orderSha256=sha((R/'order.json').read_bytes()),work=str(W),sources=len(sources),pureChecks=len(checks))))
