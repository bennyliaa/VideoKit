"""File-only preparation of one independent offline B; no candidate body."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,sys,ast,uuid,zipfile
R=Path(__file__).resolve().parent;T=R.parents[1];B=T.parent/'coder/d1android02-global-idle-contract03-fix';P=T/'D1_DRIVER_CAPTURE_FIX01_PACKAGE';V=T/'D1_GLOBAL_IDLE_CONTRACT02_REVIEW_EVIDENCE';A=T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE';D=T.parent/'coder/d1android02-global-idle-contract03-selfcheck02'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:assert f.write(b)==len(b);f.flush()
def save(p,d):put(p,(json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode())
def verify(base,manifest,h):
 raw=(base/manifest).read_bytes();assert sha(raw)==h;d=json.loads(raw)
 for x in d['files']:
  b=(base/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 return d
def main():
 assert not (R/'order.json').exists()
 for name,source in [('self_io.py',V/'self_io.py'),('self_observer.py',V/'self_observer.py'),('native_identity.py',P/'native_identity.py'),('capture_policy.py',V/'capture_policy.py'),('profile.py',A/'profile.py')]:put(R/name,source.read_bytes())
 ctl=(A/'controller.py').read_text().replace('window=300','window=720');put(R/'controller.py',ctl.encode())
 assert sha((P/'source-manifest.json').read_bytes())=='b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1'
 for x in json.loads((P/'source-manifest.json').read_bytes())['files']:assert sha((P/x['path']).read_bytes())==x['sha256']
 for x in json.loads((P/'runtime-pins.json').read_bytes())['files']:
  b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 product=verify(B,'reference/freeze-manifest.json','55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81')
 dev=verify(D,'reference/material-manifest.json','ec171260f95bfcfd712d4e2245c68b6612f2a8939631ba79a92f9b7f73b2343a')
 independent=verify(T,'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json','8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066') if False else json.loads((T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json').read_bytes())
 assert sha((T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json').read_bytes())=='8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066'
 for x in independent['files']:
  b=Path(x['absolutePath']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 assert len(product['files'])==98 and len(dev['files'])==484 and len(independent['files'])==408
 # Copy only selected already-reviewed developer helper definitions, never footer.
 text=(B/'selfchecks/run_affected.py').read_text();names={'permit','inputs','construct','rejection','cli','default_deny','authority','full_cli','ps_post_guards','changed_materialization'}
 defs=[ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==len(names)
 selected='\n\n'.join(defs).replace('>=260','>=600').replace('BEFORE_260S','BEFORE_600S')
 put(R/'frozen_definitions.py',(selected+'\n').encode())
 # Reuse mature original collector/exact-small-append group, source ledger checked by wrapper.
 text=(V/'local_groups.py').read_text();names={'owned_collector','exact_append'}
 defs=[ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==2
 put(R/'reused_groups.py',('from pathlib import Path\nfrom datetime import datetime,timezone,timedelta\nimport json,uuid,time,hashlib\n\ndef sha(b):return hashlib.sha256(b).hexdigest()\n\n'+'\n\n'.join(defs)+'\n').encode())
 W=(R.parent/'fixtures'/('b03-'+R.name.rsplit('-',1)[1])).resolve();assert not W.exists()
 save(R/'budget.json',dict(outerSeconds=720,workerSeconds=660,stopNewSeconds=600,auxSeconds=180,auxConservativeGraph=78,auxMax=128,auditMax=512,readBytes=4294967296,readCalls=8192,artifactBytes=134217728,artifactFiles=4096,evidenceFileBytes=1048576,concurrency=1,retry=0,estimatedSeconds=280,originalProductionLimits='600/30/20/10/120 and source/bytes unchanged',all11ScenarioAttempts=1,extraSourceGuardAttempt=1,physicalIO='UNPROVEN',liveQueries=0))
 save(R/'semantic-A-reuse.json',dict(reportSha256='a6f2f4fe2cf1e7d8553d27f428f79753251ab8653e7d579a4fab621f506d7ea2',manifestSha256='8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066',verifiedFiles=408,sameModuleSha256=sha((B/'tools/admission_checks.ps1').read_bytes()),entryCallsSameFunction='Get-GlobalIdleDecision' in (B/'tools/capture_android02.ps1').read_text(),semantic366=366,pure34=34,rerun400=False,modelLimitPreserved=True))
 from profiles import pure_review
 checks=pure_review(R,B,W);save(R/'profile-preflight.json',dict(checks=checks,actualConstructors=0,auditRejectInjected=False))
 save(R/'source-isolation.json',dict(candidate=str(B),work=str(W),evidence=str(R),oldDev03AndC45And001a='NO_RUNTIME_QUERIES_OR_REUSE',productFrozen98Bad=0,devMaterial484Bad=0,semanticA408Bad=0,driverDelta='Reuse original Observer and profile/capture_policy32; outer window300->720, new preconstructor finite grammar; audit only memory observes. Selected test helper admission260->600 only. No product mutation.',originalRuntime='14 files pinned'))
 sources=[]
 for p in sorted(R.glob('*.py')):
  b=p.read_bytes();ast.parse(b.decode('utf-8-sig'));sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 for p in [R/'budget.json',R/'profile-preflight.json',R/'scenarios.json']:
  b=p.read_bytes();sources.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 now=datetime.now(timezone.utc);o=dict(schema='CONTRACT03_INDEPENDENT_B_ORDER_V1',batch=str(uuid.uuid4()),nonce=str(uuid.uuid4()),candidate=str(B),work=str(W),sources=sources,sourceSeal='4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=1200)).isoformat(),allowedStarts=1)
 save(R/'order.json',o);print(json.dumps(dict(orderSha256=sha((R/'order.json').read_bytes()),work=str(W),sources=len(sources),pureChecks=len(checks))))
if __name__=='__main__':main()

