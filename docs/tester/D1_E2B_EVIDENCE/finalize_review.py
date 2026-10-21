"""Finalize E2B static review; no candidate imports, sampling or execution."""
from pathlib import Path
import ast,hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2b';OLD=ROOT/'docs/coder/d1e2a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E2B_ADMISSION_REVIEW_REPORT_V1.0.md'
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',report.read_text(encoding='utf-8')):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines())
archive=read(OUT/'archive-and-manifest-audit.json');assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
for folder in ['upstream-e2a','upstream-e2','upstream-e1e']:
 f=read(BASE/folder/'freeze-summary.json');s=read(BASE/folder/'source-manifest.json')
 for r in f['files']+f['selfcheckFiles']+s['files']:assert sha(ROOT/r['path'])==r['sha256']
for r in read(BASE/'upstream-e1e/preserved-baselines.json')['files']:assert sha(ROOT/r['path'])==r['sha256']
preserved=[]
for rel in ['src/authority.py','src/recovery.py','src/recovery_checks.py','src/runtime_wiring.py','src/Native.cs','src/Core.cs']:
 assert (BASE/rel).read_text(encoding='utf-8')==(OLD/rel).read_text(encoding='utf-8'),rel
 preserved.append(dict(path=rel,sha256=sha(BASE/rel),normalizedTextUnchanged=True))
def node(rel,cls):return next(n for n in ast.parse((BASE/rel).read_text(encoding='utf-8')).body if isinstance(n,ast.ClassDef) and n.name==cls)
for rel,cls in [('src/gcore.py','Store'),('src/gcore.py','Native')]:
 oldnode=next(n for n in ast.parse((OLD/rel).read_text(encoding='utf-8')).body if isinstance(n,ast.ClassDef) and n.name==cls)
 assert ast.dump(node(rel,cls),include_attributes=False)==ast.dump(oldnode,include_attributes=False)
 preserved.append(dict(path=rel,symbol=cls,astUnchanged=True))
fields=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
c=read(BASE/'profiles/cases.json');old=read(OLD/'profiles/cases.json');assert len(c['cases'])==len(old['cases'])==61 and c['limits']==old['limits']
for a,b in zip(c['cases'],old['cases']):assert a['id']==b['id'] and all(a[k]==b[k] for k in fields)
save('preserved-fix-and-budget-audit.json',dict(scope='Static byte-normalized/AST/config identity, not regression rerun',preserved=preserved,all61AllocationsAndOperationsPreserved=True))
anchors={}
for rel in ['src/authority.py','src/gengine.py','src/runtime_wiring.py','src/runtime_metrics.py','src/gcore.py']:
 anchors[rel]=[dict(line=i,text=s) for i,s in enumerate((BASE/rel).read_text(encoding='utf-8').splitlines(),1) if re.search(r'self.cells|PendingCell|threading\.(Event|RLock|Condition)|WinDLL|def (_release_ready|io_call|capture_identity|_close|observe)|self.on_drain|self.release|self.response',s)]
save('g-lifecycle-static-anchors.json',dict(scope='Static retention and native ownership paths; not handle-type attribution',anchors=anchors,priorityHypothesis='Engine.cells retains completed cells/Futures/lock/Event objects; actual Python build/backend and kernel count contribution unproven',nextExperimentAuthorized=False,prohibitedShortcuts=['forced GC to obtain low counter','close arbitrary runtime handles','move original baseline','reuse consumed actual reservation','raise256/+64']))
save('external-primary-reference-notes.json',dict(scope='Upstream Python3.12.14 implementation only; deployed build flags unverified',sources=['https://github.com/python/cpython/blob/v3.12.14/Python/thread_nt.h','https://github.com/python/cpython/blob/v3.12.14/Python/condvar.h','https://github.com/python/cpython/blob/v3.12.14/Include/internal/pycore_condvar.h'],supports='Windows lock/condition emulation may own semaphores and has release paths; native-CV alternative exists',doesNotProve='No measured leak class, exact per-cell handle count, or deployed runtime compile settings'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2B independent whole-package review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='E2A_A01_CLOSED; TWO_ORIGINAL_R_EIGHT_STAGE_DIAGNOSTIC_SUPPORTED; UNIQUE_ACTUAL_FULL_FAILED_G_HANDLES',findings=[],originalClosure={'E2A-A01':'STATICALLY_CLOSED_WITH_EXISTING_ACTIVE_CHAIN_OWNED_FILE_EVIDENCE'},runtimeBlocker='BLOCKED_G_HANDLES_369_GT_256_AND_DELTA_209_GT_64',gRootCauseConfirmed=False,candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(targeted=955,actualFullPassed=0,partialActualAssertionsExcluded=77,diagnosticOSInstances=2,diagnosticSamples=8,scope='Existing evidence only'),ownFunctionalTests=0,newSampling=False,diagnosticRerun=False,selfcheckRerun=False,PFStarted=False,mediaIO=False,mediaStat=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],thresholdsChanged=False,actualReservationConsumed=True,realExperimentAuthorized=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending direct authorized coordinator notification'))
print(json.dumps(dict(reportSha256=sha(report),newFunctionalFindings=0,actualFullPass=0,GResourceBlocked=True,candidateUnchanged=True,inFlight=[])))
