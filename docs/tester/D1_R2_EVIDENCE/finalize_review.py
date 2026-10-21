"""Finalize offline review records; no harness or media access."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def save(n,x): (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
report=ROOT/'docs/tester/D1_R2_REVIEW_REPORT_V1.0.md'
t=report.read_text(encoding='utf-8')
rows=re.findall(r'^\| R\d{2} \|.*?\| (SUPPORTED|MISSING|CONTRADICTED) \|',t,re.M)
counts={s:rows.count(s) for s in ('SUPPORTED','CONTRADICTED','MISSING')}
assert counts==dict(SUPPORTED=17,CONTRADICTED=0,MISSING=3),counts
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',t):
    target=m.group(1);lm=re.search(r':(\d+)$',target)
    line=int(lm.group(1)) if lm else None
    if lm: target=target[:lm.start()]
    p=Path(target)
    assert p.exists(),target
    if line: assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
audit=json.loads((OUT/'input-and-link-audit.json').read_text(encoding='utf-8'))
unchanged=[dict(path=r['path'],before=r['sha256'],after=digest(ROOT/r['path'])) for r in audit['inputs']]
assert all(r['before']==r['after'] for r in unchanged)
expanded={f'P{i:02}':1 for i in range(1,14)}
expanded['P09']=2
expanded.update(dict(Q01=1,Q02=1,Q03=2,Q04=1,Q05=2,Q06=1,Q07=2,Q08=2,Q09=3))
save('budget-review.json',dict(scope='Static arithmetic and conservative review interpretation; not an approved execution manifest',families=22,minimallySeparatedScenarios=expanded,scenarioCount=sum(expanded.values()),remainingAmbiguity=['Q08 writer/validation and READY/ABORT order combinations','Q09 intent field variants','Q05 positive bounded streaming versus injected-space-error terminal'],familyTimeoutSumSeconds=22*10,scenarioTimeoutSumSeconds=sum(expanded.values())*10,globalSeconds=180,p01FullReadRequests=4*2*65536,p01LegalOneByteShortReadRequestUpperExample=4*2*sum(65536-i for i in range(16)),inputBudgetBytes=4*1024*1024,conclusion='Global stopping rules are safe in principle, but complete branch execution and cumulative feasible allocations remain MISSING. Arithmetic is not evidence of an observed runtime failure.'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-R2 independent whole-package offline design review',report=report.relative_to(ROOT).as_posix(),reportSha256=digest(report),counts=counts,conclusion='NEEDS_REVISION_BEFORE_IMPLEMENTATION_AND_FULL_EXPERIMENT_DISPATCH',findings=[dict(id='R2-R01',severity='P1',classification='MISSING',topic='Safe close retry disposition and actual release proof'),dict(id='R2-R02',severity='P1',classification='MISSING',topic='Writer grant delivery/claim versus command replay'),dict(id='R2-R03',severity='P1',classification='MISSING',topic='Expanded branch manifest and cumulative budgets')],inputsUnchanged=unchanged,functionalTestsRun=0,deviceTestsRun=0,adbInvoked=False,gradleInvoked=False,mediaWindowRead=False,productOrFrozenInputModified=False,inFlight=[],D1Passed=False,M0Started=False,notification='Final completion event; no new send_message attempt under prior approval rejection'))
print(json.dumps(dict(reportSha256=digest(report),counts=counts,inputsUnchanged=True,budgetScenariosMinimum=sum(expanded.values()),inFlight=[]),ensure_ascii=False))
