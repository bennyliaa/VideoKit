"""Finalize static E1C review; no candidate import, tests, builds or helpers."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e1c'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E1C_REVIEW_REPORT_V1.0.md';txt=report.read_text(encoding='utf-8')
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
 target=m.group(1);lm=re.search(r':(\d+)$',target);line=int(lm.group(1)) if lm else None
 if lm:target=target[:lm.start()]
 p=Path(target);assert p.exists(),target
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
archive=json.loads((OUT/'archive-and-manifest-audit.json').read_bytes())
assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
runtime=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/concurrent/futures/_base.py')
lines=runtime.read_text(encoding='utf-8').splitlines()
save('future-runtime-source-review.json',dict(scope='Read-only standard-library source inspection; no callbacks or counterexamples executed',path=str(runtime),sha256=sha(runtime),excerpts=[dict(start=337,end=342,text='\n'.join(lines[336:342])),dict(start=537,end=565,text='\n'.join(lines[536:565]))],conclusion='set_result/set_exception invoke registered done callbacks synchronously in the completing thread; releasing Future condition does not release SourceAuthority/PendingCell locks held by caller'))
save('static-completion-counterexamples.json',dict(scope='Static source reasoning only, not executed tests',cases=[dict(id='E1C-C01',severity='P1',paths=['ordinary open completion','held open gate'],sequence=['source open admitted','seal wins source lock before delivery','consumer finished and cancelled remain false','completion checks only those consumer flags','gate may set successful result despite seal'],originalRule='R2 Source contract open/S03: late post-seal H enters cleanup, not consumer delivery',existingCoverageGap='Targeted lifecycle loops cover end/cancel; P08 uses both seal and cancel'),dict(id='E1C-C02',severity='P1',sequence=['Future done callback registered','ordinary completion holds source lock and cell lock','Future.set_result invokes callback synchronously','callback waits for another thread that needs same source authority','completer waits callback while other thread waits authority lock'],observedDeadlock=False)]))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E1C independent frozen whole-package re-review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),conclusion='NOT_READY_FOR_REAL_LOCAL_EXPERIMENT',originalDefectClosure={'T01':'PARTIALLY_FIXED; completion-boundary residual P1 issues','T02':'STATICALLY_CLOSED','T03':'STATICALLY_CLOSED','T04':'STATICALLY_CLOSED_FOR_ORIGINAL_COUNTEREXAMPLES','T05':'STATICALLY_CLOSED'},findings=[dict(id='E1C-C01',severity='P1',topic='Seal/fence not rechecked before late open consumer delivery'),dict(id='E1C-C02',severity='P1',topic='Future completion executes consumer callbacks under authority/cell locks')],candidateIntegrity='PASS',candidateUnchanged=True,producerSelectedChecks=dict(integration=158,targeted=260,total=418,scope='Existing synthetic evidence only'),independentActions=['Provided read-only verify after source inspection','Independent hashes/ZIP/AST','Read-only decoding of existing schema3 journals/inventory/query events','Local Future source inspection'],ownFunctionalTests=0,targetedRerun=False,PFStarted=False,mediaIO=False,build=False,adb=False,newHelperProcesses=0,inFlight=[],D1Passed=False,M0Started=False,C14Resumed=False,notification='Pending authorized direct report to coordinator after final verification'))
print(json.dumps(dict(reportSha256=sha(report),originalIssuesClosed=4,partiallyClosed=1,residualP1=2,candidateUnchanged=True,inFlight=[]),ensure_ascii=False))
