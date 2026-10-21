"""Finalize static E1B review evidence, without importing candidate code."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e1b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_E1B_REVIEW_REPORT_V1.0.md';txt=report.read_text(encoding='utf-8')
rows=re.findall(r'^\| R\d{2} \|.*?\| (SUPPORTED|CONTRADICTED|MISSING) \|',txt,re.M)
counts={s:rows.count(s) for s in ['SUPPORTED','CONTRADICTED','MISSING']};assert counts==dict(SUPPORTED=13,CONTRADICTED=4,MISSING=1),counts
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
 t=m.group(1);lm=re.search(r':(\d+)$',t);ln=int(lm.group(1)) if lm else None
 if lm:t=t[:lm.start()]
 p=Path(t);assert p.exists(),t
 if ln:assert 1<=ln<=len(p.read_text(encoding='utf-8-sig').splitlines()),t
archive=json.loads((OUT/'archive-and-manifest-audit.json').read_bytes())
assert sha(BASE/'evidence/freeze-summary.json')==archive['freezeSha256']
for r in archive['allCheckedEntries']:assert sha(ROOT/r['path'])==r['sha256']
findings=[dict(id='E1B-T01',severity='P1',classification='CONTRADICTED',topic='Delayed completion/cancel/timeout are post-return flags; ZERO is tautological'),dict(id='E1B-T02',severity='P1',classification='CONTRADICTED',topic='Consumer finished state and handle-consumer binding absent from open/read admission'),dict(id='E1B-T03',severity='P1',classification='CONTRADICTED',topic='Old ready rejected by boolean rather than original owner/epoch comparison'),dict(id='E1B-T04',severity='P1',classification='CONTRADICTED',topic='Recovery may lower query reservations and omit lost task shards without unknown inventory'),dict(id='E1B-T05',severity='P2',classification='MISSING',topic='Metadata short-write completeness is unchecked before admission proof')]
save('static-counterexample-review.json',dict(scope='Reasoned source paths only; no negative test, no candidate execution, no disk fault injection',cases=[dict(id='T01',path='P09-TIMEOUT',trace=['read_j hold=True completes RPC and returns value','transaction records DONE; private buffer context ended','scenario sleeps 1 second','query sees artificial op marker; no SOURCE_TIMEOUT response observed']),dict(id='T02',path='P11-FUTURE',trace=['end(A) sets finished=True while B keeps version ACTIVE','next h+ label with consumer A/new object name passes prefix order','open predicate checks sealed/cancelled/recovered, not finished','factory is reachable despite ended reservation']),dict(id='T03',path='Q07-TAKEFIRST',trace=['ready(old=True) rejects immediately','same rejection would occur without takeover','no caller ownerEpoch argument is compared by ready']),dict(id='T04',path='recovery.py',snapshotQueryReservation=2,visibleNewQueryEvents=1,recoveredAssignment=1,observedInRuntime=False,missingShardRule='Nonexistent task directory is skipped; admitted inventory unavailable'),dict(id='T05',path='Store.save',trace=['single raw write return value ignored','written += requested8192','sync and save completion treated as full admission proof'],actualShortWriteObserved=False)]))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E1B independent frozen implementation review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),counts=counts,findings=findings,conclusion='NOT_READY_FOR_SEPARATELY_DISPATCHED_REAL_LOCAL_EXPERIMENT',candidateIntegrity='PASS',candidateUnchanged=True,producerSyntheticChecks=dict(integration=148,negative=20,total=168,scope='Existing producer evidence only'),independentActions=['Read-only provided verify.py after source inspection','Independent SHA/ZIP/AST audit','Independent decoding of frozen journals and query events'],ownFunctionalTests=0,selfcheckRerun=False,negativeChecksRerun=False,PFStarted=False,mediaIO=False,build=False,adb=False,newHelperProcesses=0,inFlight=[],C14Resumed=False,D1Passed=False,M0Started=False,notification='Prior cross-thread automatic approval rejection retained; no retry, final result available for coordinator scheduled collection'))
print(json.dumps(dict(reportSha256=sha(report),counts=counts,findings=len(findings),candidateUnchanged=True,inFlight=[]),ensure_ascii=False))
