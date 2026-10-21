"""Static comparison and archived-witness review only; no candidate imports."""
from pathlib import Path
import ast,hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
BASE=ROOT/'docs/coder/d1e1e';OLD=ROOT/'docs/coder/d1e1d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E1E_REVIEW_REPORT_V1.0.md'
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',report.read_text(encoding='utf-8')):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines())
archive=json.loads((OUT/'archive-and-manifest-audit.json').read_bytes())
assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
preserved=[]
for rel in ['src/authority.py','src/recovery.py','src/recovery_checks.py','src/metadata_checks.py','src/Native.cs','src/Core.cs']:
 same=(OLD/rel).read_bytes()==(BASE/rel).read_bytes();assert same,rel
 preserved.append(dict(path=rel,sha256=sha(BASE/rel),unchangedFromE1D=same))
def function(p,cls,name):
 tree=ast.parse(p.read_text(encoding='utf-8'));container=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
 return ast.dump(next(n for n in container.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
for rel,cls,names in [('src/gcore.py','Store',['exact_write','save','write_receipt','event']),('src/gengine.py','Ops',['ready','ready_request','takeover']),('src/notifications.py','DeliveryFuture',['add_done_callback','cancel','set_result','set_exception'])]:
 for name in names:
  same=function(OLD/rel,cls,name)==function(BASE/rel,cls,name);assert same,(rel,cls,name)
  preserved.append(dict(path=rel,symbol=cls+'.'+name,astUnchangedFromE1D=same))
save('preserved-fix-audit.json',dict(scope='Static byte/AST comparison only',preserved=preserved))
t=json.loads((BASE/'evidence/targeted-1792163909644634300.json').read_bytes())
g=next(g for g in t['groups'] if g['assertions']==205)
assert len(g['checks'])==205 and g['status']=='PASS'
assert g['newHelpers']==g['nativeCalls']==g['unresolvedControlledThreads']==0
returns=g['originalReturnChannels'];assert len(returns)==10
assert [r['status'] for r in returns]==['FAIL']*6+['PENDING']*4
for case in ['generic-before-start','join-timeout']:
 o=next(o for o in g['startupObservations'] if o['case']==case)
 assert o['originalFailure']['ownershipPending'] and o['originalFailure']['remainingCredits']==['completion-worker/notify']
 assert o['originalReturn']['status']=='PENDING' and o['originalReturn']['remainingResources']==1
 assert o['controlledCleanup']
save('startup-original-evidence-review.json',dict(scope='Existing evidence only; no candidate execution',assertions=205,observations=g['startupObservations'],originalReturnChannels=returns,controlledThreadsFinallyUnresolved=0,doesNotProve='OS thread exhaustion or independent tester runtime verification'))
w=json.loads((BASE/'evidence/selfcheck-1792163660432915800.json').read_bytes())['witness']
h=w['callbackHub'];assert h['lifecycle']=='CLOSED' and not h['remainingCredits'] and not h['ownershipPending'] and h['workersAlive']==0
for worker in h['workers'].values():assert worker['entered'] and worker['exited'] and worker['joined'] and worker['creditReleased'] and not worker['alive'] and not worker['unknown']
save('callback-hub-archived-state.json',dict(scope='Existing normal synthetic witness, not rerun',callbackHub=h,privateCells=w['privateCells'],managedResourcePeaks=w['ledgerPeaks'],outerCloseProof=w['logClose']))
anchors={}
for rel in ['src/notifications.py','src/controller.py','src/gengine.py','src/phases.py','src/startup_checks.py']:
 anchors[rel]=[dict(line=i,text=s) for i,s in enumerate((BASE/rel).read_text(encoding='utf-8').splitlines(),1) if re.search(r'neverStartedProven|startInProgress|startupError|ownershipPending|helper_attempts|initial_setup|THREAD_JOIN_PROVEN|def (start|close|stop_failure|emit_failure|failure_receipt)|originalReturn|controlledCleanup',s)]
save('startup-source-anchors.json',anchors)
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E1E independent whole-package review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='E1D_D01_STATICALLY_CLOSED_WITHIN_DECLARED_TOOL_CONTRACT; NO_NEW_BLOCKER; RECOMMEND_SEPARATE_REAL_CONFIGURATION_AND_ADMISSION_REVIEW',originalClosure={'E1D-D01':'STATICALLY_CLOSED','C01_C02_T02_T05':'PRIOR_STATIC_ACCEPTANCE_PRESERVED'},findings=[],candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(integration=159,targeted=619,total=778,startup=205,scope='Existing synthetic evidence only'),ownFunctionalTests=0,targetedRerun=False,PFStarted=False,mediaIO=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],realExperimentAuthorized=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),findings=0,candidateUnchanged=True,inFlight=[])))
