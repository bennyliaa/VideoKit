"""Finalize E1D static review only; no candidate or threading operations run."""
from pathlib import Path
import ast,hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e1d';OLD=ROOT/'docs/coder/d1e1c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E1D_REVIEW_REPORT_V1.0.md';txt=report.read_text(encoding='utf-8')
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
archive=json.loads((OUT/'archive-and-manifest-audit.json').read_bytes());assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
preserved=[]
for rel in ['src/recovery.py','src/recovery_checks.py','src/metadata_checks.py','src/Native.cs','src/Core.cs']:
 same=(OLD/rel).read_bytes()==(BASE/rel).read_bytes();preserved.append(dict(path=rel,sha256=sha(BASE/rel),unchangedFromE1C=same));assert same,rel
def function(p,cls,name):
 tree=ast.parse(p.read_text(encoding='utf-8'));container=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls)
 node=next(n for n in container.body if isinstance(n,ast.FunctionDef) and n.name==name);return ast.dump(node,include_attributes=False)
for rel,cls,names in [('src/gcore.py','Store',['exact_write','save','write_receipt','event']),('src/gengine.py','Ops',['ready','ready_request','takeover'])]:
 for name in names:
  same=function(OLD/rel,cls,name)==function(BASE/rel,cls,name);preserved.append(dict(path=rel,symbol=cls+'.'+name,astUnchangedFromE1C=same));assert same,(rel,cls,name)
save('preserved-fix-audit.json',dict(scope='Static byte/AST comparison only, not regression execution',selectedPreservedT02T05Paths=preserved))
runtime=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/threading.py');lines=runtime.read_text(encoding='utf-8').splitlines()
save('startup-counterexample-review.json',dict(scope='Static source path and local runtime source inspection only; no Thread.start/join or failure injection executed',runtime=dict(path=str(runtime),sha256=sha(runtime),joinPreconditionExcerpt=dict(start=1138,end=1145,text='\n'.join(lines[1137:1145]))),sequence=['Hub.started set true and two worker credits reserved','notifier.start succeeds','monitor.start raises RuntimeError','closing/closed/blocked remain false/false/null; ensure_accepting can pass','PF exception stops normal 61-row loop','normal GC may encounter absent J/R; fallback checks cells/queued/active, not partial-worker startup','close joins notifier then attempts join of unstarted monitor, raising RuntimeError again','worker-credit release and closed flag skipped; no bounded structured startup-failure ownership receipt from Hub'],observedFailure=False,doesNotClaim='No claim of actual continued media, guaranteed leaked thread, or false PASS',requestedFix='Per-worker start state, fail-closed admission, bounded partial-start cleanup/idempotent close and honest pending facts'))
w=json.loads((BASE/'evidence/selfcheck-1792162234030690200.json').read_bytes())['witness']
save('callback-hub-archived-state.json',dict(scope='Existing producer normal-run witness, not re-run',callbackHub=w['callbackHub'],privateCells=w['privateCells'],managedResourcePeaks=w['ledgerPeaks'],outerCloseProof=w['logClose']))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E1D independent completion whole-package review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='C01_C02_MAIN_COMPLETION_PATHS_STATICALLY_CLOSED; PARTIAL_WORKER_START_FAILURE_BLOCKS_DIRECT_REAL_EXPERIMENT_ADMISSION',originalClosure={'C01':'STATICALLY_CLOSED','C02':'MAIN_DELIVERY_CALLBACK_AND_DRAIN_PATHS_STATICALLY_CLOSED; new startup exception gap D01','T02_T05':'PRIOR_STATIC_ACCEPTANCE_PRESERVED'},findings=[dict(id='E1D-D01',severity='P1',topic='Hub partial startup not fenced and close blindly joins unstarted workers')],futureCompatibility='Pre-decision max4 callback contract is compatible with current bounded tool callers, not general Future substitutability',candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(integration=159,targeted=414,total=573,scope='Existing synthetic evidence only'),ownFunctionalTests=0,targetedRerun=False,PFStarted=False,mediaIO=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),newP1=1,candidateUnchanged=True,inFlight=[]),ensure_ascii=False))
